import math
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud import shop_crud
from models.player import PlayerInstance
from models.shop import ShopInstance
from schemas.shop import HealResponse, NearestShopResponse
from services import monster_service


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


async def get_nearest_shop(
    db: AsyncSession, x_coord: int, z_coord: int
) -> NearestShopResponse:
    """Get the nearest shop."""

    shop_list = await shop_crud.get_all(db)
    closest = None
    closest_distance = None
    for shop in shop_list:
        distance = int(math.hypot(shop.x_coord - x_coord, shop.z_coord - z_coord))
        if closest is None or distance < closest_distance:
            closest_distance = distance
            print(f"{shop.x_coord}")
            closest = NearestShopResponse(
                x_coord=shop.x_coord,
                z_coord=shop.z_coord,
                radius=shop.radius,
            )
    if closest is None:
        raise HTTPException(
            status_code=404,
            detail="No shops available",
        )
    return closest


async def heal_party(
    db: AsyncSession, player: PlayerInstance, x_coord: int, z_coord: int
) -> HealResponse:
    """Heal characters party."""
    current_shop = await get_current_shop(db, x_coord, z_coord)
    if current_shop is None:
        raise HTTPException(
            status_code=400,
            detail="Outside shop radius",
        )
    return HealResponse(
        success=await monster_service.heal_players_monster(db, player.id)
    )
