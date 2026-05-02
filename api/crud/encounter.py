from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.encounter import Encounter


async def get_by_id(db: AsyncSession, encounter_id: int) -> Optional[Encounter]:
    """Fetch encounter by id."""
    result = await db.execute(select(Encounter).where(Encounter.id == encounter_id))
    return result.scalar_one_or_none()


async def delete(db: AsyncSession, encounter: Encounter) -> bool:
    """Delete encounter."""
    if encounter is None:
        return False
    await db.delete(encounter)
    await db.commit()
    return True


async def delete_by_id(db: AsyncSession, encounter_id: int) -> bool:
    """Delete encounter by id."""
    encounter = await get_by_id(db, encounter_id)
    return await delete(db, encounter)
