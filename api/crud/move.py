from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.move import Move, MoveInstance


async def create_instance(
    db: AsyncSession, move_instance: MoveInstance
) -> MoveInstance:
    """Create monster instance."""
    db.add(move_instance)
    await db.commit()
    return MoveInstance


async def get_monster_moves(db: AsyncSession, monster_id: int) -> list[MoveInstance]:
    """Fetch all of a monsters moves."""
    result = await db.execute(
        select(MoveInstance)
        .where(MoveInstance.monster_id == monster_id)
        .options(joinedload(MoveInstance.move))
        .order_by(MoveInstance.slot)
    )
    return result.scalars().all()


async def get_monster_move_by_slot(
    db: AsyncSession, monster_id: int, slot: int
) -> Optional[MoveInstance]:
    """Grab monster move by slot."""
    result = await db.execute(
        select(MoveInstance)
        .where(MoveInstance.monster_id == monster_id, MoveInstance.slot == slot)
        .options(joinedload(MoveInstance.move))
    )
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, move_id: int) -> Optional[Move]:
    """Get move by move_id"""
    result = await db.execute(select(Move).where(Move.id == move_id))
    return result.scalar_one_or_none()
