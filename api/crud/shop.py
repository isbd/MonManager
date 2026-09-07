from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.shop import ShopInstance


async def get_by_id(db: AsyncSession, shop_id: int) -> Optional[ShopInstance]:
    """Get shop instance by id."""
    result = await db.execute(select(ShopInstance).where(ShopInstance.id == shop_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, shop: ShopInstance) -> ShopInstance:
    """Create a shop."""
    db.add(shop)
    await db.commit()
    await db.refresh(shop)
    return shop


async def stage_delete(db: AsyncSession, shop: ShopInstance) -> bool:
    """Stage deleting a shop."""
    if shop is None:
        return False
    await db.delete(shop)
    return True


async def delete_instance(db: AsyncSession, shop: ShopInstance) -> bool:
    """Delete a shop."""
    if await stage_delete(db, shop) is False:
        return False
    await db.commit()
    return True


async def delete_by_id(db: AsyncSession, shop_id: int) -> bool:
    """Delete a shop by id."""
    shop = await get_by_id(db, shop_id)
    return await delete_instance(db, shop)


async def get_all(db: AsyncSession) -> list[ShopInstance]:
    """Fetch all shops."""
    result = await db.execute(select(ShopInstance))
    return result.scalars().all()
