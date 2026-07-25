from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from dependencies import get_current_player_ws
from models.player import PlayerInstance
from notifier import notifier

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
