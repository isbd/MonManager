from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_player
from models.shop import ShopInstance
from schemas.shop import (
    HealRequest,
    HealResponse,
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
