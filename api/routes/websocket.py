from models.player import PlayerInstance
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from dependencies import get_current_player_ws
from notifier import notifier

active: dict[str, WebSocket] = {} # player_id -> socket

router = APIRouter()

@router.websocket("/ws")
async def ws_endpoint(
    websocket: WebSocket,
    player: PlayerInstance = Depends(get_current_player_ws),
):
    await websocket.accept()
    await notifier.connect(player.id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        # Only evicts if still current
        notifier.disconnect(player.id, websocket)