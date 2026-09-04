from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.battle import BattleTurn


async def get_turn_by_number(
    db: AsyncSession, encounter_id: int, turn_number: int
) -> Optional[BattleTurn]:
    """Get specified turn."""
    selected_turn = await db.execute(
        select(BattleTurn).where(
            BattleTurn.encounter_id == encounter_id,
            BattleTurn.turn_number == turn_number,
        )
    )
    return selected_turn.scalar_one_or_none()


async def get_latest_resolved_turn(
    db: AsyncSession, encounter_id: int
) -> Optional[BattleTurn]:
    """Get latest resolved turn."""
    recent_turns = await db.execute(
        select(BattleTurn)
        .where(BattleTurn.encounter_id == encounter_id)
        .order_by(BattleTurn.turn_number.desc())
    )
    turns = recent_turns.scalars().all()
    if not turns:
        return None

    for turn in turns:
        if turn.resolved:
            return turn
    return None


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
