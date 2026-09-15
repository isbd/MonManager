import secrets

from sqlalchemy.ext.asyncio import AsyncSession

import services.monster as monster_service
from crud import player_crud
from models.player import PlayerInstance
from schemas.player import PlayerCreateResponse


async def create_player(db: AsyncSession, player_username: str) -> PlayerCreateResponse:
    """Create and register player."""
    player_instance = PlayerInstance(
        name=player_username, api_key=secrets.token_hex(32), active_slot=1
    )
    player = await player_crud.create(db, player_instance)

    # TODO: Better starter selection than this random filler
    # Register a starter
    monster_species = await monster_service.roll_species(db)
    await monster_service.create_monster_instance(db, monster_species, owner=player)

    return player
