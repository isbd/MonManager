from sqlalchemy.ext.asyncio import AsyncSession

import services.encounter as encounter_service
from crud import monster_crud
from models.encounter import EncounterType
from models.player import PlayerInstance
from schemas.battle import CatchResponse


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
