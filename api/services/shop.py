from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException

from services import monster_service
from models.player import PlayerInstance
from models.shop import ShopInstance
from crud import shop_crud
from schemas.shop import HealResponse
from typing import Optional
import math


async def get_current_shop(
    db: AsyncSession, x_coord: int, z_coord: int
) -> Optional[ShopInstance]:
    """Get the current shop intersecting coords."""

    shop_list = await shop_crud.get_all(db)
    for shop in shop_list:
        distance = int(math.hypot(shop.x_coord - x_coord, shop.z_coord - z_coord))
        if distance - shop.radius < 1:
            return shop
    return None


async def heal_party(
    db: AsyncSession, player: PlayerInstance, x_coord: int, z_coord: int
) -> HealResponse:
    """Health characters party."""
    current_shop = await get_current_shop(db, x_coord, z_coord)
    if current_shop is None:
        raise HTTPException(
            status_code=400,
            detail=f"Outside shop radius",
        )
    return HealResponse(success=await monster_service.heal_players_monster(db, player.id))
