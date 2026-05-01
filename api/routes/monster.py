from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from database import get_db
from models.player import PlayerInstance
from models.monster import MonsterInstance
from schemas.monster import MonstersResponse

router = APIRouter()


@router.get("/{monster_id}", response_model=MonstersResponse)
async def get_monster(monster_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific players monsters."""
    result = await db.execute(
        select(MonsterInstance)
        .where(MonsterInstance.id == monster_id)
        .options(joinedload(MonsterInstance.species))
    )
    monster = result.scalar_one_or_none()

    if not monster:
        raise HTTPException(status_code=404, detail="Monster not found")

    return monster
