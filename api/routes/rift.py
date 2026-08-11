from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud import rift_crud
from database import get_db
from dependencies import get_current_player
from models.rift import RiftInstance
from schemas.rift import RiftResponse

router = APIRouter()


@router.get("/", response_model=list[RiftResponse])
async def get_rifts(
    db: AsyncSession = Depends(get_db), _: RiftInstance = Depends(get_current_player)
):
    """Get all players."""
    return await rift_crud.get_all(db)


# @router.post("/", response_model=PlayerCreateResponse)
# async def create_player(body: PlayerCreate, db: AsyncSession = Depends(get_db)):
#     """Create player that doesn't already exist."""
#     existing = await player_crud.get_by_name(db, body.name)

#     if existing:
#         raise HTTPException(status_code=400, detail="Player already exists")

#     return await player_service.create_player(db, body.name)


# @router.get("/{player_id}", response_model=PlayerResponse)
# async def get_player(
#     player_id: int,
#     db: AsyncSession = Depends(get_db),
#     _: PlayerInstance = Depends(get_current_player),
# ):
#     """Get a specific player by id."""
#     player = await player_crud.get_by_id(db, player_id)

#     if not player:
#         raise HTTPException(status_code=404, detail="Player not found")

#     return player
