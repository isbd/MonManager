import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud import player_crud
from database import get_db
from dependencies import get_current_player
from models.player import PlayerInstance
from schemas.player import PlayerCreate, PlayerCreateResponse, PlayerResponse

router = APIRouter()


@router.get("/", response_model=list[PlayerResponse])
async def get_players(
    db: AsyncSession = Depends(get_db), _: PlayerInstance = Depends(get_current_player)
):
    """Get all players."""
    return await player_crud.get_all(db)


@router.post("/", response_model=PlayerCreateResponse)
async def create_player(body: PlayerCreate, db: AsyncSession = Depends(get_db)):
    """Create player that doesn't already exist."""
    existing = await player_crud.get_by_name(db, body.name)

    if existing:
        raise HTTPException(status_code=400, detail="Player already exists")

    player = PlayerInstance(name=body.name, api_key=secrets.token_hex(32))
    return await player_crud.create(db, player)


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: int,
    db: AsyncSession = Depends(get_db),
    _: PlayerInstance = Depends(get_current_player),
):
    """Get a specific player by id."""
    player = await player_crud.get_by_id(db, player_id)

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player
