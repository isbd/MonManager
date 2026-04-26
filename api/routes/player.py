from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.player import PlayerInstance
from schemas.player import PlayerCreate, PlayerResponse, MonstersResponse, MonsterListFetch

router = APIRouter()

# GET all players
@router.get("/", response_model=list[PlayerResponse])
async def get_players(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlayerInstance))
    players = result.scalars().all()
    return players

# POST create player if they don't exist
@router.post("/", response_model=PlayerResponse)
async def create_player(body: PlayerCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PlayerInstance).where(PlayerInstance.name == body.name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Player already exists")

    player = PlayerInstance(name=body.name)
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player
