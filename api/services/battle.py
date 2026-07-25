import random

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import services.encounter as encounter_service
import services.move as move_service
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
from schemas.battle import AttackDetails, BattleResponse, CatchResponse
from schemas.move import MonsterMoveResponse


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

    return CatchResponse(
        success=True,
        message=f"You have caught a {monster.species.name}!",
        monster_id=monster.id,
    )


async def attempt_attack(
    db: AsyncSession, player: PlayerInstance, attack_id: int
) -> BattleResponse:
    """Attempt to attack."""
    encounter = await encounter_service.fetch_player_encounter(db, player)

    if encounter.active is not EncounterState.ACTIVE:
        # TODO: Alternative handling when not active
        raise HTTPException(
            status_code=400,
            detail="Encounter is not longer active, update code for handle.",
        )

    move = await move_crud.get_monster_move_by_slot(
        db, encounter.challenger_mon_id, attack_id
    )
    if not move:
        raise HTTPException(
            status_code=400,
            detail="Invalid move type while attacking.",
        )
    active_turn = await fetch_active_turn(db, encounter)

    active_perspective = encounter_service.get_encounter_perspective(
        encounter, player.id
    )
    active_turn = await set_turn_move(db, active_turn, active_perspective, move.move_id)

    # TODO: Update dummy attack handling
    match encounter.encounter_type:
        case EncounterType.WILD:
            ai_move = await select_ai_move(db, encounter.challenged_mon_id)
            active_turn = await set_turn_move(
                db, active_turn, EncounterPerspective.CHALLENGED, ai_move.move_id
            )
            # RETURN Resolve turn
            return await resolve_turn(db, active_turn)
        case EncounterType.PVP:
            pass
        case _:
            raise HTTPException(
                status_code=500,
                detail="Invalid encounter type when attacking.",
            )
    return BattleResponse(
        success=False,
        active=False,
        challenger_attack=None,
        challenged_attack=None,
    )


async def select_ai_move(db: AsyncSession, monster_id: int) -> Move:
    """Select ai monster move."""
    # TODO: Improve on this with context of current mon
    move_list = await move_crud.get_monster_moves(db, monster_id)
    return random.choice(move_list)


async def resolve_turn(db: AsyncSession, turn: BattleTurn) -> BattleTurn:
    """Resolve the current turn."""
    challenger_mon = await monster_crud.get_by_instance_id(db, turn.challenger_mon_id)
    challenged_mon = await monster_crud.get_by_instance_id(db, turn.challenged_mon_id)
    challenged_move = await move_crud.get_by_id(db, turn.challenged_move_id)
    challenger_move = await move_crud.get_by_id(db, turn.challenger_move_id)

    # TODO: Determine speed

    challenged_attack = await resolve_attack(
        db, challenged_mon, challenger_mon, challenged_move
    )
    if challenged_attack == -1:
        turn.challenged_move_missed = challenged_attack.missed
    else:
        turn.challenged_damage_dealt = challenged_attack.damage_dealt

    # Check if the mon is dead
    if challenger_mon.current_hp <= 1:
        await resolve_battle(db, turn)
        return BattleResponse(
            success=True,
            active=False,
            challenger_attack=None,
            challenged_attack=challenged_attack,
        )

    challenger_attack = await resolve_attack(
        db, challenger_mon, challenged_mon, challenger_move
    )
    if challenger_attack.missed:
        turn.challenger_move_missed = challenger_attack.missed
    else:
        turn.challenger_damage_dealt = challenger_attack.damage_dealt

    if challenged_mon.current_hp <= 1:
        await resolve_battle(db, turn)
        return BattleResponse(
            success=True,
            active=False,
            challenger_attack=challenger_attack,
            challenged_attack=challenged_attack,
        )

    turn.resolved = True

    await battle_crud.update_instance(db, turn)
    return BattleResponse(
        success=True,
        active=True,
        challenger_attack=challenger_attack,
        challenged_attack=challenged_attack,
    )


async def resolve_battle(db: AsyncSession, turn: BattleTurn):
    """Conclude the battle."""
    # TODO: Better handling for battles
    encounter = await encounter_crud.get_by_id(db, turn.encounter_id)
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
    db: AsyncSession, _attacker: MonsterInstance, defender: MonsterInstance, move: Move
) -> AttackDetails:
    """Resolve current attack."""
    # TODO: Improve accuracy check and damage calculation check
    # Accuracy check
    if not random.random() * 100 < move.accuracy:
        return AttackDetails(
            first=False,
            missed=True,
            damage_dealt=0,
            move_name=move.name,
            targets_current_health=defender.current_hp,
            targets_total_health=defender.max_hp,
            targets_pre_reduced_health=defender.current_hp,
        )
    # Calculate damage
    damage = move.power
    pre_reduced = defender.current_hp
    # Apply damage
    defender.current_hp = max(0, defender.current_hp - damage)
    await monster_crud.update_instance(db, defender)

    return AttackDetails(
        first=False,
        missed=False,
        damage_dealt=damage,
        move_name=move.name,
        targets_current_health=defender.current_hp,
        targets_total_health=defender.max_hp,
        targets_pre_reduced_health=pre_reduced,
    )


# async def determine_action_order(db: AsyncSession, turn: BattleTurn):


async def set_turn_move(
    db: AsyncSession, turn: BattleTurn, perspective: EncounterPerspective, move_id: int
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
