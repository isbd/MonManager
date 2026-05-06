from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import services.encounter as encounter_service
import services.move as move_service
from crud import monster_crud, move_crud
from models.encounter import EncounterType
from models.player import PlayerInstance
from schemas.battle import AttackResponse, CatchResponse
from schemas.move import MonsterMoveResponse


async def attempt_catch(db: AsyncSession, player: PlayerInstance) -> CatchResponse:
    """Attempt to catch a wild monster."""
    encounter = await encounter_service.fetch_player_encounter(db, player)

    if encounter.encounter_type is not EncounterType.wild:
        return CatchResponse(
            success=False, message="Can only catch wild monsters!", monster_id=None
        )

    monster = await monster_crud.get_full_by_instance_id(db, encounter.wild_monster_id)

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
) -> AttackResponse:
    """Attempt to attack."""
    encounter = await encounter_service.fetch_player_encounter(db, player)

    # TODO: Update dummy attack handling
    match encounter.encounter_type:
        case EncounterType.wild:
            move = await move_crud.get_monster_move_by_slot(
                db, encounter.challenger_mon_id, attack_id
            )
            if not move:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid move type while attacking.",
                )
            return AttackResponse(
                success=True,
                attack_name=move.move.name,
                damage_dealth=move.move.power,
                enemy_health=0,
            )
        case EncounterType.pvp:
            pass
        case _:
            raise HTTPException(
                status_code=500,
                detail="Invalid encounter type when attacking.",
            )
    return AttackResponse(
        success=False,
        attack_name=None,
        damage_dealth=None,
        enemy_health=None,
    )


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
