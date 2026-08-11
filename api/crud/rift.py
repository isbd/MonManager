from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.rift import RiftInstance


async def get_by_id(db: AsyncSession, rift_id: int) -> Optional[RiftInstance]:
    """Get rift instance by id."""
    result = await db.execute(
        select(RiftInstance).where(RiftInstance.id == rift_id)
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, rift: RiftInstance) -> RiftInstance:
    """Create a rift."""
    db.add(rift)
    await db.commit()
    await db.refresh(rift)
    return rift


async def get_all(db: AsyncSession) -> list[RiftInstance]:
    """Fetch all rifts."""
    result = await db.execute(select(RiftInstance))
    return result.scalars().all()
