from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import get_db
from dependencies import get_current_player
from models.monster import MonsterInstance
from models.player import PlayerInstance
from schemas.monster import MonstersResponse
from crud import monster_crud

router = APIRouter()


@router.get("/{monster_id}", response_model=MonstersResponse)
async def get_monster(monster_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific players monsters."""
    monster = await monster_crud.get_full_by_instance_id(db, monster_id)

    if not monster:
        raise HTTPException(status_code=404, detail="Monster not found")

    return monster


@router.get("/", response_model=list[MonstersResponse])
async def get_player_monsters(
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Get all monsters belonging to current player."""
    return await monster_crud.get_instances_by_player(db, player.id)
