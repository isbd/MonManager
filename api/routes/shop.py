from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_player
from models.shop import ShopInstance
from schemas.shop import (
    HealRequest,
    HealResponse,
    NearestShopResponse,
)
from services import shop_service

router = APIRouter()


@router.post("/heal", response_model=HealResponse)
async def heal_party(
    body: HealRequest,
    db: AsyncSession = Depends(get_db),
    player: ShopInstance = Depends(get_current_player),
):
    """Heal party at shop."""
    return await shop_service.heal_party(db, player, body.x, body.z)


@router.get("/nearest_shop", response_model=NearestShopResponse)
async def get_nearest_shop(
    x: int = Query(..., description="Overworld X coordinate"),
    z: int = Query(..., description="Overworld Z coordinate"),
    db: AsyncSession = Depends(get_db),
    _: ShopInstance = Depends(get_current_player),
):
    """Fetch coords of nearest shop."""
    return await shop_service.get_nearest_shop(db, x, z)
