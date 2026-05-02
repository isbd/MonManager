from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud import encounter_crud, monster_crud, player_crud
from models.encounter import EncounterType
from models.player import PlayerInstance
from schemas.encounter import SurrenderResponse


async def surrender(db: AsyncSession, player: PlayerInstance) -> SurrenderResponse:
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
            return SurrenderResponse(
                success=True, message="Successfully escaped wild encounter!"
            )
        case _:
            raise HTTPException(status_code=500, detail="Invalid encounter")
