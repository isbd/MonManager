from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.player import PlayerInstance

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def get_current_player(
    x_api_key: str = Depends(api_key_header), db: AsyncSession = Depends(get_db)
) -> PlayerInstance:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    result = await db.execute(
        select(PlayerInstance).where(PlayerInstance.api_key == x_api_key)
    )
    player = result.scalar_one_or_none()

    if not player:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return player
