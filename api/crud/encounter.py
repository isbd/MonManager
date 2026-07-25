from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.encounter import Encounter, EncounterState


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


async def create(db: AsyncSession, encounter: Encounter) -> Optional[Encounter]:
    """Create encounter."""
    if encounter is None:
        return None
    db.add(encounter)
    await db.commit()
    await db.refresh(encounter)
    return encounter


async def get_pending_by_challenger(db: AsyncSession, challenger_id: int):
    """Fetch encounter that are pending by specified challenger_id"""
    result = await db.execute(
        select(Encounter).where(
            Encounter.active == EncounterState.PENDING,
            Encounter.challenger_id == challenger_id,
        )
    )
    return result.scalars().all()


async def get_pending_by_challenged(db: AsyncSession, challenged_id: int):
    """Fetch encounter that are pending by specified challenged_id"""
    result = await db.execute(
        select(Encounter).where(
            Encounter.active == EncounterState.PENDING,
            Encounter.challenged_id == challenged_id,
        )
    )
    return result.scalars().all()


async def update_instance(db: AsyncSession, encounter: Encounter) -> Encounter:
    """Update encounter instance."""
    await db.commit()
    await db.refresh(encounter)
    return encounter
