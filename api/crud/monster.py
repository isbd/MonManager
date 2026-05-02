from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.monster import MonsterInstance


async def get_by_id(db: AsyncSession, monster_id: int) -> Optional[MonsterInstance]:
    """Fetch monster by id."""
    result = await db.execute(
        select(MonsterInstance).where(MonsterInstance.id == monster_id)
    )
    return result.scalar_one_or_none()


async def get_full_by_id(
    db: AsyncSession, monster_id: int
) -> Optional[MonsterInstance]:
    """Fetch monster and species by id."""
    result = await db.execute(
        select(MonsterInstance)
        .where(MonsterInstance.id == monster_id)
        .options(joinedload(MonsterInstance.species))
    )
    return result.scalar_one_or_none()


async def delete(db: AsyncSession, monster: MonsterInstance) -> bool:
    """Delete a monster."""
    if monster is None:
        return False
    await db.delete(monster)
    await db.commit()
    return True


async def delete_by_id(db: AsyncSession, monster_id: int) -> bool:
    """Delete a monster by id."""
    monster = await get_by_id(db, monster_id)
    return await delete(db, monster)


# TODO: Update stats
