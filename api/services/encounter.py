from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import services.monster as monster_service
from crud import encounter_crud, monster_crud, player_crud
from models.encounter import (
    Encounter,
    EncounterPerspective,
    EncounterState,
    EncounterType,
)
from models.player import PlayerInstance
from notifier import notifier
from schemas.encounter import (
    ChallengeCancelResponse,
    ChallengeDetails,
    ChallengeEncounterResponse,
    ChallengeList,
    ChallengeResponse,
    EncounterDetails,
    EncounterMonsterDetails,
    SurrenderResponse,
    WildEncounterResponse,
)
from schemas.event import EventType


async def fetch_player_encounter(db: AsyncSession, player: PlayerInstance) -> Encounter:
    """Safely fetch player encounter, used often for different moves."""
    if not player.active_encounter_id:
        raise HTTPException(status_code=404, detail="No active encounter")
    encounter = await encounter_crud.get_by_id(db, player.active_encounter_id)
    if encounter is None:
        # Cleanup on desync
        await player_crud.set_active_encounter_id(db, player, None)
        raise HTTPException(
            status_code=404,
            detail="Encounter does not exist, removed from false encounter.",
        )
    return encounter


async def resolve_encounter(db, encounter):
    """Remove encounter."""
    await encounter_crud.delete(db, encounter)


async def surrender(db: AsyncSession, player: PlayerInstance) -> SurrenderResponse:
    """Surrender from current encounter."""
    encounter = await fetch_player_encounter(db, player)

    match encounter.encounter_type:
        case EncounterType.WILD:
            monster_id = encounter.challenged_mon_id
            await resolve_encounter(db, encounter)
            await monster_crud.delete_by_id(db, monster_id)
            return SurrenderResponse(
                success=True, message="Successfully escaped wild encounter!"
            )
        case EncounterType.PVP:
            # TODO: Flush this out more
            # TODO: May need to update notifier to include rewards gained
            await notify_opponent(encounter, player.id, EventType.BATTLE_FORFEITED)
            await player_crud.set_player_id_active_encounter_id(
                db, encounter.challenger_id, None
            )
            await player_crud.set_player_id_active_encounter_id(
                db, encounter.challenged_id, None
            )
            await resolve_encounter(db, encounter)

            return SurrenderResponse(success=True, message="Surrendered pvp encounter!")
        case _:
            raise HTTPException(status_code=500, detail="Invalid encounter")


async def get_current_encounter_details(
    db: AsyncSession, player: PlayerInstance
) -> EncounterDetails:
    encounter = await fetch_player_encounter(db, player)
    challenger_mon = await monster_crud.get_full_by_instance_id(
        db, encounter.challenger_mon_id
    )
    challenged_mon = await monster_crud.get_full_by_instance_id(
        db, encounter.challenged_mon_id
    )

    challenger_mon_details = EncounterMonsterDetails(
        id=encounter.challenger_mon_id,
        current_health=challenger_mon.current_hp,
        max_health=challenger_mon.max_hp,
        texture=challenger_mon.species.texture,
    )
    challenged_mon_details = EncounterMonsterDetails(
        id=encounter.challenged_mon_id,
        current_health=challenged_mon.current_hp,
        max_health=challenged_mon.max_hp,
        texture=challenged_mon.species.texture,
    )

    if encounter.challenger_id == player.id:
        challenged_mon_details.texture = monster_service.reverse_monster_image(
            challenged_mon_details.texture
        )
        return EncounterDetails(
            id=encounter.id,
            encounter_type=encounter.encounter_type,
            self_id=encounter.challenger_id,
            self_mon=challenger_mon_details,
            opponent_id=encounter.challenged_id,
            opponent_mon=challenged_mon_details,
        )
    else:
        challenger_mon_details.texture = monster_service.reverse_monster_image(
            challenger_mon_details.texture
        )
        return EncounterDetails(
            id=encounter.id,
            encounter_type=encounter.encounter_type,
            self_id=encounter.challenged_id,
            self_mon=challenged_mon_details,
            opponent_id=encounter.challenger_id,
            opponent_mon=challenger_mon_details,
        )


async def notify_opponent(
    encounter: Encounter, player_id: int, event: EventType, **fields
) -> bool:
    """Send websocket poke to opponent."""
    if encounter.challenger_id == player_id:
        is_notified = await notifier.poke(encounter.challenged_id, event, **fields)
    elif encounter.challenged_id == player_id:
        is_notified = await notifier.poke(encounter.challenger_id, event, **fields)
    else:
        raise HTTPException(
            status_code=500, detail="Encounter perspective not found to notify opponent"
        )
    return is_notified


def get_encounter_perspective(
    encounter: Encounter, player_id: int
) -> Optional[EncounterPerspective]:
    """Get the players perspective for the encounter."""
    if encounter.challenged_id == player_id:
        return EncounterPerspective.CHALLENGED
    elif encounter.challenger_id == player_id:
        return EncounterPerspective.CHALLENGER
    else:
        return None


async def attempt_wild_encounter(
    db: AsyncSession, player: PlayerInstance
) -> WildEncounterResponse:
    """Attempt to start a wild encounter."""
    # a = random.randint(0, 10)
    # if a > 5:
    #     return WildEncounterResponse(success=False, message="No monster appeared...")

    monster_species = await monster_service.roll_species(db)

    # Fetch players first monster TODO: placeholder right now, should replace with party system
    player_monster = await monster_service.grab_players_monster(db, player.id)

    wild_monster = await monster_service.create_monster_instance(db, monster_species)

    encounter_details = Encounter(
        active=EncounterState.ACTIVE,
        encounter_type=EncounterType.WILD,
        challenger_id=player.id,
        challenger_mon_id=player_monster.id,
        challenged_mon_id=wild_monster.id,
    )
    encounter = await encounter_crud.create(db, encounter_details)
    await player_crud.set_active_encounter_id(db, player, encounter.id)

    return WildEncounterResponse(
        success=True,
        message=f"A wild {monster_species.name} appeared!",
        encounter_id=encounter.id,
        name=monster_species.name,
    )


async def current_challenges(db, player: PlayerInstance) -> ChallengeList:
    """Fetch current challenges relating to player."""
    received = await encounter_crud.get_pending_by_challenged(db, player.id)
    received_challenges = []
    for entry in received:
        challenger = await player_crud.get_by_id(db, entry.challenger_id)
        received_challenges.append(
            ChallengeDetails(
                challenge_id=entry.id,
                challenger=challenger.name,
                challenger_id=challenger.id,
                challenged=player.name,
                challenged_id=player.id,
            )
        )
    sent = await encounter_crud.get_pending_by_challenger(db, player.id)
    # if len(sent) > 1:
    # Issue
    sent_challenges = None
    if len(sent) > 0:
        challenged = await player_crud.get_by_id(db, sent[0].challenged_id)
        sent_challenges = ChallengeDetails(
            challenge_id=sent[0].id,
            challenger=player.name,
            challenger_id=player.id,
            challenged=challenged.name,
            challenged_id=challenged.id,
        )

    return ChallengeList(
        received_challenges=received_challenges, sent_challenge=sent_challenges
    )


async def cancel_challenge(
    db, player: PlayerInstance, challenge_id: int
) -> ChallengeCancelResponse:
    """Attempt to cancel a pvp challenge."""
    encounter = await encounter_crud.get_by_id(db, challenge_id)

    if encounter is None:
        raise HTTPException(
            status_code=404, detail="Attempted response on stale challenge"
        )

    if encounter.challenger_id != player.id:
        raise HTTPException(
            status_code=400, detail="Only the challenger can cancel the challenge"
        )

    if encounter.active is EncounterState.ACTIVE:
        raise HTTPException(
            status_code=400, detail="Cannot cancel challenge for active encounter"
        )

    # Deleting encounter but may require state later
    encounter.active = EncounterState.EXPIRED
    await player_crud.set_player_id_active_encounter_id(
        db, encounter.challenger_id, None
    )
    await encounter_crud.delete(db, encounter)

    is_notified = await notifier.poke(
        encounter.challenged_id, EventType.CHALLENGE_CANCELED, challenge_id=encounter.id
    )

    if not is_notified:
        return ChallengeCancelResponse(
            success=True,
            message="Challenge rejected but failed to notify opponent",
        )
    return ChallengeCancelResponse(success=True, message="Challenge canceled.")


async def challenge_response(
    db, player: PlayerInstance, challenge_id: int, accept: bool
) -> ChallengeResponse:
    """Attempt to accept or reject a challenge."""
    encounter = await encounter_crud.get_by_id(db, challenge_id)

    if encounter is None:
        raise HTTPException(
            status_code=404, detail="Attempted response on stale challenge"
        )

    if encounter.challenged_id != player.id:
        raise HTTPException(status_code=400, detail="Challenge was not issued to you")

    if player.active_encounter_id is not None:
        raise HTTPException(
            status_code=400, detail="Cannot respond to challenge while inside encounter"
        )

    if accept:
        challenger_mon = await monster_service.grab_players_monster(
            db, encounter.challenger_id
        )
        challenged_mon = await monster_service.grab_players_monster(
            db, encounter.challenged_id
        )

        if None in (challenger_mon, challenged_mon):
            raise HTTPException(
                status_code=400, detail="A user is missing a mon to start this battle"
            )

        encounter.active = EncounterState.ACTIVE
        encounter.challenged_id = player.id
        encounter.challenger_mon_id = challenger_mon.id
        encounter.challenged_mon_id = challenged_mon.id
        await encounter_crud.update_instance(db, encounter)
        await player_crud.set_active_encounter_id(db, player, encounter.id)
        is_notified = await notifier.poke(
            encounter.challenger_id,
            EventType.CHALLENGE_RESPONSE,
            challenge_id=encounter.id,
            accepted=True,
        )
        if not is_notified:
            return ChallengeResponse(
                success=True,
                message="Challenge accepted but failed to notify opponent.",
            )
        return ChallengeResponse(success=True, message="Challenge accepted.")
    else:
        # Deleting encounter but may require state later
        encounter.active = EncounterState.DECLINED
        await player_crud.set_player_id_active_encounter_id(
            db, encounter.challenger_id, None
        )
        await encounter_crud.delete(db, encounter)
        is_notified = await notifier.poke(
            encounter.challenger_id,
            EventType.CHALLENGE_RESPONSE,
            challenge_id=encounter.id,
            accepted=False,
        )
        if not is_notified:
            return ChallengeResponse(
                success=True,
                message="Challenge rejected but failed to notify opponent.",
            )
        return ChallengeResponse(success=True, message="Challenge rejected.")


async def attempt_challenge(
    db, player: PlayerInstance, target_id: int
) -> ChallengeEncounterResponse:
    """Attempt to start a pvp encounter."""
    if player.active_encounter_id is not None:
        raise HTTPException(
            status_code=400, detail="Cannot initiate a challenge with an encounter"
        )

    target_player = await player_crud.get_by_id(db, target_id)
    if not target_player:
        raise HTTPException(
            status_code=404, detail="Target player to challenge not found"
        )

    encounter_details = Encounter(
        active=EncounterState.PENDING,
        encounter_type=EncounterType.PVP,
        challenger_id=player.id,
        challenged_id=target_player.id,
        challenger_mon_id=None,
        challenged_mon_id=None,
    )

    encounter = await encounter_crud.create(db, encounter_details)

    is_notified = await notifier.poke(
        target_id, EventType.CHALLENGE_RECEIVED, challenge_id=encounter.id
    )

    await player_crud.set_active_encounter_id(db, player, encounter.id)

    if not is_notified:
        return ChallengeEncounterResponse(
            success=True, message="Opponent is not connected!"
        )

    return ChallengeEncounterResponse(success=True, message="Challenge awaiting")
