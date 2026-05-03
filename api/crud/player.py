from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.player import PlayerInstance


async def get_by_id(db: AsyncSession, player_id: int) -> Optional[PlayerInstance]:
    """Get player instance by id."""
    result = await db.execute(
        select(PlayerInstance).where(PlayerInstance.id == player_id)
    )
    return result.scalar_one_or_none()


async def get_by_name(db: AsyncSession, player_name: str) -> Optional[PlayerInstance]:
    """Fetch player by name."""
    result = await db.execute(
        select(PlayerInstance).where(PlayerInstance.name == player_name)
    )
    return result.scalar_one_or_none()


async def get_by_api_key(db: AsyncSession, api_key: str) -> Optional[PlayerInstance]:
    """Fetch player by api key."""
    result = await db.execute(
        select(PlayerInstance).where(PlayerInstance.api_key == api_key)
    )
    return result.scalar_one_or_none()


async def set_active_encounter_id(db: AsyncSession, player: PlayerInstance, encounter_id: Optional[int]):
    """Set a players active encounter id."""
    player.active_encounter_id = encounter_id
    await db.commit()
    await db.refresh(player)


async def create(db: AsyncSession, player: PlayerInstance) -> PlayerInstance:
    """Create a player."""
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player


async def get_all(db: AsyncSession) -> list[PlayerInstance]:
    """Fetch all players."""
    result = await db.execute(select(PlayerInstance))
    return result.scalars().all()
