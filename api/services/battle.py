import random
from typing import Literal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import services.encounter as encounter_service
import services.move as move_service
import services.party as party_service
from crud import battle_crud, encounter_crud, monster_crud, move_crud, player_crud
from models.battle import BattleTurn
from models.encounter import (
    Encounter,
    EncounterPerspective,
    EncounterState,
    EncounterType,
)
from models.monster import MonsterInstance
from models.move import Move
from models.player import PlayerInstance
from schemas.battle import (
    BattleResponse,
    CatchResponse,
    FillResponse,
    RoundDetails,
    StatusEffect,
    TurnAction,
)
from schemas.event import EventType
from schemas.move import MonsterMoveResponse


async def attempt_fill(
    db: AsyncSession, player: PlayerInstance, slot: int
) -> FillResponse:
    """Attempt to fill empty active after monster death."""
    current_monster = await monster_crud.get_party_slot(
        db, player.id, player.active_slot
    )
    if not current_monster:
        raise HTTPException(
            status_code=500,
            detail="Active slot is not set as expected in attempted fill.",
        )
    if current_monster.current_hp > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot fill with healthy monster.",
        )
    slot_mon = await monster_crud.get_party_slot(db, player.id, slot)
    if slot_mon is None or slot_mon.current_hp <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid slot to set as active.",
        )
    await party_service.set_active(db, player, slot)
    await encounter_service.set_player_monster(db, player, slot_mon)
    # Notify the opponent of the swap
    encounter = await encounter_service.fetch_player_encounter(db, player)
    await encounter_service.notify_opponent(
        encounter, player.id, EventType.OPPONENT_MONSTER_FILLED
    )
    return FillResponse(success=True, message="Swapped...")


async def attempt_catch(db: AsyncSession, player: PlayerInstance) -> CatchResponse:
    """Attempt to catch a wild monster."""
    encounter = await encounter_service.fetch_player_encounter(db, player)

    if encounter.encounter_type is not EncounterType.WILD:
        return CatchResponse(
            success=False, message="Can only catch wild monsters!", monster_id=None
        )

    monster = await monster_crud.get_full_by_instance_id(
        db, encounter.challenged_mon_id
    )

    # TODO: Resource removal here
    # TODO: Randomizer here to determine if caught

    monster.owner_id = player.id
    monster = await monster_crud.update_instance(db, monster)

    await encounter_service.resolve_encounter(db, encounter)
    await party_service.auto_assign(db, player, monster)

    return CatchResponse(
        success=True,
        message=f"You have caught a {monster.species.name}!",
        monster_id=monster.id,
    )


async def fetch_turn_context(
    db: AsyncSession, player: PlayerInstance
) -> tuple[Encounter, BattleTurn, EncounterPerspective]:
    """Fetch context for current turn."""
    encounter = await encounter_service.fetch_player_encounter(db, player)
    if encounter.active is not EncounterState.ACTIVE:
        # TODO: Alternative handling when not active
        raise HTTPException(
            status_code=400,
            detail="Encounter is no longer active, update code for handle.",
        )
    perspective = encounter_service.get_encounter_perspective(encounter, player.id)
    if perspective is None:
        raise HTTPException(
            status_code=403,
            detail="User missing from encounter.",
        )
    turn = await fetch_active_turn(db, encounter)
    return encounter, turn, perspective


async def advance_turn(
    db: AsyncSession,
    player: PlayerInstance,
    encounter: Encounter,
    turn: BattleTurn,
    perspective: EncounterPerspective,
) -> BattleResponse:
    """Progress the current turn based on the current turn information."""
    is_challenger = perspective is EncounterPerspective.CHALLENGER
    match encounter.encounter_type:
        case EncounterType.WILD:
            ai_move = await select_ai_move(db, encounter.challenged_mon_id)
            turn = set_turn_move(turn, EncounterPerspective.CHALLENGED, ai_move.move_id)
            return await resolve_turn(db, turn, is_challenger)
        case EncounterType.PVP:
            await battle_crud.update_instance(db, turn)

            if False in (
                turn.challenger_submitted,
                turn.challenged_submitted,
            ):
                await encounter_service.notify_opponent(
                    encounter, player.id, EventType.ROUND_PENDING_YOUR_MOVE
                )
                return BattleResponse(
                    active=False,
                    pending=True,
                    round_details=None,
                )

            result = await resolve_turn(db, turn, is_challenger)
            if result.active:
                round_details = await format_battle_turn(
                    db, player, encounter, turn, is_opponent=True
                )
                await encounter_service.notify_opponent(
                    encounter,
                    player.id,
                    EventType.ROUND_RESOLVED,
                    round_details=round_details.model_dump(mode="json"),
                )
            return result
        case _:
            raise HTTPException(
                status_code=500,
                detail="Invalid encounter type when attacking.",
            )


async def attempt_swap(
    db: AsyncSession, player: PlayerInstance, slot: int
) -> BattleResponse:
    encounter, active_turn, perspective = await fetch_turn_context(db, player)

    is_challenger = perspective is EncounterPerspective.CHALLENGER

    is_already_submitted = (
        active_turn.challenger_submitted
        if is_challenger
        else active_turn.challenged_submitted
    )
    if is_already_submitted:
        raise HTTPException(
            status_code=400,
            detail="You already have a move selected.",
        )
    # TODO: finish this logic

    swap_monster = await party_service.fetch_swappable(db, player, slot)
    if is_challenger:
        active_turn.challenger_swap = swap_monster.id
        active_turn.challenger_submitted = True
    else:
        active_turn.challenged_swap = swap_monster.id
        active_turn.challenged_submitted = True

    return await advance_turn(db, player, encounter, active_turn, perspective)


async def attempt_attack(
    db: AsyncSession, player: PlayerInstance, attack_id: int
) -> BattleResponse:
    """Attempt to attack."""
    encounter, active_turn, perspective = await fetch_turn_context(db, player)
    is_challenger = perspective is EncounterPerspective.CHALLENGER

    self_mon_id = (
        encounter.challenger_mon_id if is_challenger else encounter.challenged_mon_id
    )

    move = await move_crud.get_monster_move_by_slot(db, self_mon_id, attack_id)
    if not move:
        raise HTTPException(
            status_code=400,
            detail="Invalid move type while attacking.",
        )

    is_already_submitted = (
        active_turn.challenger_submitted
        if is_challenger
        else active_turn.challenged_submitted
    )
    if is_already_submitted:
        raise HTTPException(
            status_code=400,
            detail="You already have a move selected.",
        )

    active_turn = set_turn_move(active_turn, perspective, move.move_id)

    if is_challenger:
        active_turn.challenger_submitted = True
    else:
        active_turn.challenged_submitted = True

    return await advance_turn(db, player, encounter, active_turn, perspective)


async def select_ai_move(db: AsyncSession, monster_id: int) -> Move:
    """Select ai monster move."""
    # TODO: Improve on this with context of current mon
    move_list = await move_crud.get_monster_moves(db, monster_id)
    return random.choice(move_list)


async def resolve_turn(
    db: AsyncSession, turn: BattleTurn, is_challenger: bool
) -> BattleResponse:
    """Resolve the current turn."""
    challenged_mon = await monster_crud.get_by_instance_id(db, turn.challenged_mon_id)

    if turn.challenger_swap is not None:
        challenger_mon = await monster_crud.get_by_instance_id(db, turn.challenger_swap)
        challenger_move = None
        challenger_speed = 0
    else:
        challenger_mon = await monster_crud.get_by_instance_id(
            db, turn.challenger_mon_id
        )
        challenger_move = await move_crud.get_by_id(db, turn.challenger_move_id)
        challenger_speed = determine_speed(challenger_mon, challenger_move)

    if turn.challenged_swap is not None:
        challenged_mon = await monster_crud.get_by_instance_id(db, turn.challenged_swap)
        challenged_move = None
        challenged_speed = 0
    else:
        challenged_mon = await monster_crud.get_by_instance_id(
            db, turn.challenged_mon_id
        )
        challenged_move = await move_crud.get_by_id(db, turn.challenged_move_id)
        challenged_speed = determine_speed(challenged_mon, challenged_move)

    # Required for snapshot of battle
    turn.challenged_pre_damage_health = challenged_mon.current_hp
    turn.challenger_pre_damage_health = challenger_mon.current_hp
    turn.challenger_max_hp = challenger_mon.max_hp
    turn.challenged_max_hp = challenged_mon.max_hp

    actions: list[TurnAction] = []
    move_order = [EncounterPerspective.CHALLENGER, EncounterPerspective.CHALLENGED]

    encounter = await encounter_crud.get_by_id(db, turn.encounter_id)

    if turn.challenger_swap is not None:
        await apply_swap(db, encounter, EncounterPerspective.CHALLENGER, challenger_mon)
        actions.append(
            TurnAction(
                actor="self" if is_challenger else "opponent",
                actor_perspective="challenger",
                message="Swapped monster",
                move_name="swap",
                missed=False,
                damage_dealt=0,
                target_max_health=challenged_mon.max_hp,
                target_pre_damage_health=challenged_mon.current_hp,
            )
        )
        move_order.remove(EncounterPerspective.CHALLENGER)

    if turn.challenged_swap is not None:
        await apply_swap(db, encounter, EncounterPerspective.CHALLENGED, challenged_mon)
        actions.append(
            TurnAction(
                actor="self" if not is_challenger else "opponent",
                actor_perspective="challenged",
                message="Swapped monster",
                move_name="swap",
                missed=False,
                damage_dealt=0,
                target_max_health=challenger_mon.max_hp,
                target_pre_damage_health=challenger_mon.current_hp,
            )
        )
        move_order.remove(EncounterPerspective.CHALLENGED)

    if challenger_speed == challenged_speed:
        random.shuffle(move_order)
    elif challenged_speed < challenger_speed:
        move_order.reverse()

    turn.first_actor = move_order[0] if move_order else None

    for move in move_order:
        if move is EncounterPerspective.CHALLENGED:
            mon = challenged_mon
            target_mon = challenger_mon
            mon_move = challenged_move
            title = "challenged"
            is_self = not is_challenger
        else:
            mon = challenger_mon
            target_mon = challenged_mon
            mon_move = challenger_move
            title = "challenger"
            is_self = is_challenger

        attack_result = await resolve_attack(
            db, mon, target_mon, mon_move, title, is_self
        )
        actions.append(attack_result)

        if move is EncounterPerspective.CHALLENGED:
            turn.challenged_damage_dealt = 0
            turn.challenged_move_missed = attack_result.missed
            if not attack_result.missed:
                turn.challenged_damage_dealt = attack_result.damage_dealt
        else:
            turn.challenger_damage_dealt = 0
            turn.challenger_move_missed = attack_result.missed
            if not attack_result.missed:
                turn.challenger_damage_dealt = attack_result.damage_dealt

        if target_mon.current_hp < 1:
            round_details = RoundDetails(
                turn_number=turn.turn_number,
                actions=actions,
                self_mon_status=None,
                opponent_mon_status=None,
            )
            battle_response = BattleResponse(
                active=False, pending=False, round_details=round_details
            )
            await resolve_battle(db, turn, is_challenger)
            return battle_response

    turn.resolved = True

    await battle_crud.update_instance(db, turn)
    return BattleResponse(
        active=True,
        pending=False,
        round_details=RoundDetails(
            turn_number=turn.turn_number,
            actions=actions,
            self_mon_status=None,
            opponent_mon_status=None,
        ),
    )


def determine_speed(monster: MonsterInstance, move: Move) -> int:
    """Determine the speed of selected move."""
    # Move speed + monster speed + modifier?
    return move.speed + monster.speed


async def resolve_battle(db: AsyncSession, turn: BattleTurn, is_challenger: bool):
    """Conclude the battle."""

    encounter = await encounter_crud.get_by_id(db, turn.encounter_id)
    actor_id = encounter.challenger_id if is_challenger else encounter.challenged_id
    opponent = await player_crud.get_by_id(db, actor_id)
    opponent_details = await format_battle_turn(
        db, opponent, encounter, turn, is_opponent=True
    )
    await encounter_service.notify_opponent(
        encounter,
        actor_id,
        EventType.ENCOUNTER_OVER,
        round_details=opponent_details.model_dump(mode="json"),
    )

    encounter.active = EncounterState.COMPLETED
    turn.resolved = True
    await battle_crud.update_instance(db, turn)
    await player_crud.set_player_id_active_encounter_id(
        db, encounter.challenger_id, None
    )
    if encounter.encounter_type is EncounterType.WILD:
        await encounter_service.resolve_encounter(db, encounter)
    else:
        await player_crud.set_player_id_active_encounter_id(
            db, encounter.challenged_id, None
        )


async def resolve_attack(
    db: AsyncSession,
    _attacker: MonsterInstance,
    defender: MonsterInstance,
    move: Move,
    perspective: Literal["challenged", "challenger"],
    is_self: bool = True,
) -> TurnAction:
    """Resolve current attack."""
    # TODO: Improve accuracy check and damage calculation check
    # Accuracy check
    actor = "self" if is_self else "opponent"

    if not random.random() * 100 < move.accuracy:
        return TurnAction(
            actor=actor,
            actor_perspective=perspective,
            message=format_action_message(is_self, move.name, True),
            move_name=move.name,
            missed=True,
            damage_dealt=0,
            target_max_health=defender.max_hp,
            target_pre_damage_health=defender.current_hp,
        )
    # Calculate damage
    damage = move.power
    pre_reduced = defender.current_hp
    # Apply damage
    defender.current_hp = max(0, defender.current_hp - damage)
    await monster_crud.update_instance(db, defender)

    return TurnAction(
        actor=actor,
        actor_perspective=perspective,
        message=format_action_message(is_self, move.name, False),
        move_name=move.name,
        missed=False,
        damage_dealt=damage,
        target_max_health=defender.max_hp,
        target_pre_damage_health=pre_reduced,
    )


def set_turn_move(
    turn: BattleTurn, perspective: EncounterPerspective, move_id: int
) -> BattleTurn:
    """Assign move for turn."""
    match perspective:
        case EncounterPerspective.CHALLENGED:
            turn.challenged_move_id = move_id
        case EncounterPerspective.CHALLENGER:
            turn.challenger_move_id = move_id
        case _:
            raise HTTPException(
                status_code=500,
                detail="Invalid perspective when setting turn move.",
            )
    return turn


async def fetch_active_turn(db: AsyncSession, encounter: Encounter) -> BattleTurn:
    """Get or create the active turn."""
    turn = await battle_crud.get_current_turn(db, encounter.id)
    if turn is None:
        # First turn
        active_turn = await battle_crud.create(
            db,
            BattleTurn(
                encounter_id=encounter.id,
                turn_number=1,
                challenger_mon_id=encounter.challenger_mon_id,
                challenged_mon_id=encounter.challenged_mon_id,
                challenger_move_id=None,
                challenged_move_id=None,
                challenger_damage_dealt=None,
                challenged_damage_dealt=None,
                challenger_move_missed=None,
                challenged_move_missed=None,
                first_actor=None,
                resolved=False,
            ),
        )
    elif turn.resolved:
        # Create new turn
        active_turn = await battle_crud.create(
            db,
            BattleTurn(
                encounter_id=encounter.id,
                turn_number=turn.turn_number + 1,
                challenger_mon_id=encounter.challenger_mon_id,
                challenged_mon_id=encounter.challenged_mon_id,
                challenger_move_id=None,
                challenged_move_id=None,
                challenger_damage_dealt=None,
                challenged_damage_dealt=None,
                challenger_move_missed=None,
                challenged_move_missed=None,
                first_actor=None,
                resolved=False,
            ),
        )
    else:
        # Last turn is active
        active_turn = turn
    return active_turn


async def get_active_moves(
    db: AsyncSession, player: PlayerInstance
) -> MonsterMoveResponse:
    """Fetch active moves from monster."""
    encounter = await encounter_service.fetch_player_encounter(db, player)
    if encounter.challenger_id == player.id:
        return await move_service.get_monster_moves(db, encounter.challenger_mon_id)
    elif encounter.challenged_id == player.id:
        return await move_service.get_monster_moves(db, encounter.challenged_mon_id)
    else:
        raise HTTPException(
            status_code=500, detail="Missing encounter reference in active moves"
        )


async def get_latest_turn(db: AsyncSession, player: PlayerInstance) -> RoundDetails:
    """Fetch latest turn details."""
    encounter = await encounter_service.fetch_player_encounter(db, player)
    battle = await battle_crud.get_latest_resolved_turn(db, encounter.id)
    if not battle:
        raise HTTPException(status_code=404, detail="Requested turn does not exist")

    return await format_battle_turn(db, player, encounter, battle)


async def get_resolved_turn(
    db: AsyncSession, player: PlayerInstance, turn_number: int
) -> RoundDetails:
    """Fetch specific turn details."""
    encounter = await encounter_service.fetch_player_encounter(db, player)
    battle = await battle_crud.get_turn_by_number(db, encounter.id, turn_number)
    if not battle:
        raise HTTPException(status_code=404, detail="Requested turn does not exist")
    if battle.resolved is False:
        raise HTTPException(status_code=400, detail="Requested turn is not resolved")
    return await format_battle_turn(db, player, encounter, battle)


async def format_battle_turn(
    db: AsyncSession,
    player: PlayerInstance,
    encounter: Encounter,
    battle: BattleTurn,
    is_opponent: bool = False,
) -> RoundDetails:
    """Format turn details result."""

    player_id = player.id
    if is_opponent:
        player_id = (
            encounter.challenged_id
            if encounter.challenger_id == player.id
            else encounter.challenger_id
        )

    actions: list[TurnAction] = []

    move_order = [EncounterPerspective.CHALLENGER, EncounterPerspective.CHALLENGED]
    if battle.challenger_swap is not None:
        is_self = encounter.challenger_id == player_id
        actions.append(
            TurnAction(
                actor="self" if is_self else "opponent",
                actor_perspective="challenger",
                message="Swapped monster",
                move_name="swap",
                missed=False,
                damage_dealt=0,
                target_max_health=battle.challenged_max_hp,
                target_pre_damage_health=battle.challenged_pre_damage_health,
            )
        )
        move_order.remove(EncounterPerspective.CHALLENGER)
    if battle.challenged_swap is not None:
        is_self = encounter.challenged_id == player_id
        actions.append(
            TurnAction(
                actor="self" if is_self else "opponent",
                actor_perspective="challenged",
                message="Swapped monster",
                move_name="swap",
                missed=False,
                damage_dealt=0,
                target_max_health=battle.challenger_max_hp,
                target_pre_damage_health=battle.challenger_pre_damage_health,
            )
        )
        move_order.remove(EncounterPerspective.CHALLENGED)

    if battle.first_actor is EncounterPerspective.CHALLENGED:
        move_order.reverse()

    for move in move_order:
        if move is EncounterPerspective.CHALLENGED:
            # Fainted
            if battle.challenged_move_missed is None:
                continue
            move_instance = await move_crud.get_by_id(db, battle.challenged_move_id)
            is_self = encounter.challenged_id == player_id
            actions.append(
                TurnAction(
                    actor="self" if is_self else "opponent",
                    actor_perspective="challenged",
                    message=format_action_message(
                        is_self,
                        move_instance.name,
                        battle.challenged_move_missed,
                    ),
                    move_name=move_instance.name,
                    missed=battle.challenged_move_missed,
                    damage_dealt=battle.challenged_damage_dealt,
                    target_max_health=battle.challenger_max_hp,
                    target_pre_damage_health=battle.challenger_pre_damage_health,
                )
            )
        else:
            # Fainted
            if battle.challenger_move_missed is None:
                continue
            move_instance = await move_crud.get_by_id(db, battle.challenger_move_id)
            is_self = encounter.challenger_id == player_id
            actions.append(
                TurnAction(
                    actor="self" if is_self else "opponent",
                    actor_perspective="challenger",
                    message=format_action_message(
                        is_self,
                        move_instance.name,
                        battle.challenger_move_missed,
                    ),
                    move_name=move_instance.name,
                    missed=battle.challenger_move_missed,
                    damage_dealt=battle.challenger_damage_dealt,
                    target_max_health=battle.challenged_max_hp,
                    target_pre_damage_health=battle.challenged_pre_damage_health,
                )
            )

    # TODO: add status effects
    return RoundDetails(
        turn_number=battle.turn_number,
        actions=actions,
        self_mon_status=StatusEffect(),
        opponent_mon_status=StatusEffect(),
    )


async def apply_swap(
    db: AsyncSession,
    encounter: Encounter,
    perspective: EncounterPerspective,
    swap_mon: MonsterInstance,
) -> None:
    """Persist a swap once the turn resolves."""
    player_id = (
        encounter.challenger_id
        if perspective is EncounterPerspective.CHALLENGER
        else encounter.challenged_id
    )
    player = await player_crud.get_by_id(db, player_id)
    await party_service.set_active(db, player, swap_mon.party_slot)
    await encounter_service.set_player_monster(db, player, swap_mon)


def format_action_message(is_self: bool, move_name: str, missed: bool) -> str:
    """Format action display."""
    perspective = "You" if is_self else "Opp"
    missed = ". Missed!" if missed else ""
    return f"{perspective} used {move_name}{missed}"
