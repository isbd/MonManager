from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from crud import rift_crud
from database import get_db
from dependencies import get_current_player
from models.rift import RiftInstance
from schemas.rift import (
    CalibrateResponse,
    RiftCreate,
    RiftCreateResponse,
    RiftFishResponse,
    RiftResponse,
)
from services import rift_service

router = APIRouter()


@router.get("/", response_model=list[RiftResponse])
async def get_rifts(
    db: AsyncSession = Depends(get_db), _: RiftInstance = Depends(get_current_player)
):
    """Get all rifts."""
    return await rift_service.get_all_rifts(db)


@router.get("/fish_rifts", response_model=RiftFishResponse)
async def fish_rifts(
    x: int = Query(..., description="Overworld X coordinate"),
    z: int = Query(..., description="Overworld Z coordinate"),
    db: AsyncSession = Depends(get_db),
    player: RiftInstance = Depends(get_current_player),
):
    """Search for the closest rift."""
    return await rift_service.fish_rifts(db, player, x, z)


@router.get("/calibrate", response_model=CalibrateResponse)
async def calibrate(
    x: int = Query(..., description="Overworld X coordinate"),
    z: int = Query(..., description="Overworld Z coordinate"),
    db: AsyncSession = Depends(get_db),
    player: RiftInstance = Depends(get_current_player),
):
    """Calibrate in active rift."""
    return await rift_service.calibrate(db, player, x, z)


# Create rift (TODO admin locked)
@router.post("/", response_model=RiftCreateResponse)
async def create_rift(body: RiftCreate, db: AsyncSession = Depends(get_db)):
    """Create rift at specified coordinates."""
    return await rift_service.create_rift(db, body.x_coord, body.z_coord)


@router.get("/{rift_id}", response_model=RiftResponse)
async def get_rift(
    rift_id: int,
    db: AsyncSession = Depends(get_db),
    _: RiftInstance = Depends(get_current_player),
):
    """Get a specific rift by id."""
    rift = await rift_crud.get_by_id(db, rift_id)

    if not rift:
        raise HTTPException(status_code=404, detail="Rift not found")

    return rift
