from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.battle import BattleTurn


async def get_current_turn(db: AsyncSession, encounter_id: int) -> Optional[BattleTurn]:
    """Get current turn of encounter."""
    recent_turn = await db.execute(
        select(BattleTurn)
        .where(BattleTurn.encounter_id == encounter_id)
        .order_by(BattleTurn.turn_number.desc())
    )
    return recent_turn.scalars().first()


async def get_by_id(db: AsyncSession, battle_id: int) -> Optional[BattleTurn]:
    """Get battle turn by id."""
    battle_turn = await db.execute(select(BattleTurn).where(BattleTurn.id == battle_id))
    return battle_turn


async def create(db: AsyncSession, battle_turn: BattleTurn) -> Optional[BattleTurn]:
    """Create a battle turn."""
    db.add(battle_turn)
    await db.commit()
    await db.refresh(battle_turn)
    return battle_turn


async def update_instance(db: AsyncSession, battle_turn: BattleTurn) -> BattleTurn:
    """Update battle turn."""
    await db.commit()
    await db.refresh(battle_turn)
    return battle_turn
