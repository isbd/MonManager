from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.monster import MonsterInstance, MonsterSpecies


async def get_by_instance_id(
    db: AsyncSession, monster_id: int
) -> Optional[MonsterInstance]:
    """Fetch monster by id."""
    result = await db.execute(
        select(MonsterInstance).where(MonsterInstance.id == monster_id)
    )
    return result.scalar_one_or_none()


async def get_full_by_instance_id(
    db: AsyncSession, monster_id: int
) -> Optional[MonsterInstance]:
    """Fetch monster and species by id."""
    result = await db.execute(
        select(MonsterInstance)
        .where(MonsterInstance.id == monster_id)
        .options(joinedload(MonsterInstance.species))
    )
    return result.scalar_one_or_none()


async def delete_instance(db: AsyncSession, monster: MonsterInstance) -> bool:
    """Delete a monster."""
    if monster is None:
        return False
    await db.delete(monster)
    await db.commit()
    return True


async def delete_by_id(db: AsyncSession, monster_id: int) -> bool:
    """Delete a monster by id."""
    monster = await get_by_instance_id(db, monster_id)
    return await delete_instance(db, monster)


async def get_spawnable_species(
    db: AsyncSession, spawn_time: str
) -> list[MonsterSpecies]:
    """Get list of spawnable species."""
    result = await db.execute(
        select(MonsterSpecies).where(MonsterSpecies.spawn_time.in_([spawn_time, "any"]))
    )
    return result.scalars().all()


async def get_instances_by_player(
    db: AsyncSession, player_id: int
) -> list[MonsterInstance]:
    """Get list of monsters player owns."""
    result = await db.execute(
        select(MonsterInstance)
        .where(MonsterInstance.owner_id == player_id)
        .options(joinedload(MonsterInstance.species))
    )
    return result.scalars().all()


async def create_instance(
    db: AsyncSession, monster_instance: MonsterInstance
) -> MonsterInstance:
    """Create a monster."""
    db.add(monster_instance)
    await db.commit()
    await db.refresh(monster_instance)
    return monster_instance


async def update_instance(
    db: AsyncSession, monster_instance: MonsterInstance
) -> MonsterInstance:
    """Update monster instance."""
    await db.commit()
    await db.refresh(monster_instance)
    return monster_instance
