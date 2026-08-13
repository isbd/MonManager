from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from crud import rift_crud
from database import get_db
from dependencies import get_current_player
from models.rift import RiftInstance
from schemas.rift import RiftCreate, RiftCreateResponse, RiftResponse
from services import rift_service

router = APIRouter()


@router.get("/", response_model=list[RiftResponse])
async def get_rifts(
    db: AsyncSession = Depends(get_db), _: RiftInstance = Depends(get_current_player)
):
    """Get all players."""
    return await rift_crud.get_all(db)


@router.get("/closest", response_model=RiftResponse)
async def get_closest_rift(
    x: int = Query(..., description="World X coordinate"),
    z: int = Query(..., description="World Z coordinate"),
    db: AsyncSession = Depends(get_db),
    _: RiftInstance = Depends(get_current_player),
):
    """Get closest rift."""
    return await rift_service.fetch_nearest_rift(db, x, z)


# Create rift (admin locked)
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