from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from database import get_db
from models.player import PlayerInstance
from models.monster import MonsterInstance
from schemas.player import PlayerCreate, PlayerResponse, PlayerCreateResponse
from schemas.monster import MonstersResponse
from dependencies import get_current_player
import secrets

router = APIRouter()


@router.get("/", response_model=list[PlayerResponse])
async def get_players(
    db: AsyncSession = Depends(get_db), _: PlayerInstance = Depends(get_current_player)
):
    """Get all players."""
    result = await db.execute(select(PlayerInstance))
    players = result.scalars().all()
    return players


@router.post("/", response_model=PlayerCreateResponse)
async def create_player(body: PlayerCreate, db: AsyncSession = Depends(get_db)):
    """Create player that doesn't already exist."""
    result = await db.execute(
        select(PlayerInstance).where(PlayerInstance.name == body.name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Player already exists")

    player = PlayerInstance(name=body.name, api_key=secrets.token_hex(32))
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: int,
    db: AsyncSession = Depends(get_db),
    _: PlayerInstance = Depends(get_current_player),
):
    """Get a specific player by id."""
    result = await db.execute(
        select(PlayerInstance).where(PlayerInstance.id == player_id)
    )
    player = result.scalar_one_or_none()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player


@router.get("/{player_id}/monsters", response_model=list[MonstersResponse])
async def get_monsters(
    player_id: int,
    db: AsyncSession = Depends(get_db),
    _: PlayerInstance = Depends(get_current_player),
):
    """Get a specific players monsters."""
    result = await db.execute(
        select(PlayerInstance)
        .where(PlayerInstance.id == player_id)
        .options(
            selectinload(PlayerInstance.monsters).joinedload(MonsterInstance.species)
        )
    )
    player = result.scalar_one_or_none()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player.monsters
