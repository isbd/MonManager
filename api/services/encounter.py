import random

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud import encounter_crud, monster_crud, player_crud
from models.encounter import Encounter, EncounterType
from models.player import PlayerInstance
from schemas.encounter import SurrenderResponse, WildEncounterResponse
import services.monster as monster_service


async def surrender(db: AsyncSession, player: PlayerInstance) -> SurrenderResponse:
    """Surrender from current encounter."""
    encounter = await encounter_crud.get_by_id(db, player.active_encounter_id)

    match encounter.encounter_type:
        case EncounterType.wild:
            await player_crud.set_active_encounter_id(db, player, None)
            await encounter_crud.delete(db, encounter)
            await monster_crud.delete_by_id(db, encounter.wild_monster_id)
            return SurrenderResponse(
                success=True, message="Successfully escaped wild encounter!"
            )
        case EncounterType.pvp:
            # TODO: Flush this out more
            # PVP
            # Ensure both challenger/challenged have null active encounters
            # Set challenger.active_encounter_id
            # Set challenged.active_encounter_id

            # Once encounter is over, must null the active_encounter!
            raise HTTPException(
                status_code=500, detail="Invalid pvp encounter. Not made yet"
            )
        case _:
            raise HTTPException(status_code=500, detail="Invalid encounter")


async def attempt_wild_encounter(
    db: AsyncSession, player: PlayerInstance
) -> WildEncounterResponse:
    """Attempt to start a wild encounter."""
    a = random.randint(0, 10)
    if a > 5:
        return WildEncounterResponse(success=False, message="No monster appeared...")

    monster_species = await monster_service.roll_species(db)
    wild_monster = await monster_service.create_monster_instance(db, monster_species)

    encounter_details = Encounter(
        active=True,
        encounter_type=EncounterType.wild,
        challenger_id=player.id,
        challenger_mon_id=None,
        wild_monster_id=wild_monster.id,
    )
    encounter = await encounter_crud.create(db, encounter_details)
    await player_crud.set_active_encounter_id(db, player, encounter.id)

    return WildEncounterResponse(
        success=True,
        message=f"A wild {monster_species.name} appeared!",
        encounter_id=encounter.id,
        name=monster_species.name,
    )
