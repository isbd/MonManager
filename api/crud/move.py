from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.move import MoveInstance

async def create_instance(db: AsyncSession, move_instance: MoveInstance) -> MoveInstance:
    db.add(move_instance)
    await db.commit()
    return MoveInstance
