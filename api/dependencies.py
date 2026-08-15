import os

from fastapi import Depends, HTTPException, WebSocket, WebSocketException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from crud import player_crud
from database import get_db
from models.player import PlayerInstance

DEV_AUTO_LOGIN = os.getenv("DEV_AUTO_LOGIN") == "1"

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def get_current_player(
    x_api_key: str = Depends(api_key_header), db: AsyncSession = Depends(get_db)
) -> PlayerInstance:
    if not x_api_key:
        if DEV_AUTO_LOGIN:
            result = await player_crud.get_all(db)
            if len(result) == 0:
                raise HTTPException(
                    status_code=401, detail="Running autologin without any players"
                )
            return result[0]
        raise HTTPException(status_code=401, detail="Missing API key")

    player = await player_crud.get_by_api_key(db, x_api_key)

    if not player:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return player


async def get_current_player_ws(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
) -> PlayerInstance:
    api_key = websocket.headers.get("x-api-key")
    if not api_key:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    player = await player_crud.get_by_api_key(db, api_key)
    if not player:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    return player
