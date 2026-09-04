from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

from schemas.event import EventType


class Notifier:
    def __init__(self):
        # player.id -> socket
        self._connections: dict[int, WebSocket] = {}

    async def connect(self, player_id: int, ws: WebSocket):
        # Boot old connections
        old = self._connections.get(player_id)
        if old is not None:
            try:
                await old.close(code=1008)
            except RuntimeError:
                # Already closed
                pass
        self._connections[player_id] = ws

    def disconnect(self, player_id: int, ws: Optional[WebSocket] = None):
        if ws is None or self._connections.get(player_id) is ws:
            self._connections.pop(player_id, None)

    async def poke(self, player_id: int, event_type: EventType, **fields) -> bool:
        ws = self._connections.get(player_id)
        if ws is None:
            return False
        try:
            await ws.send_json(jsonable_encoder({"type": event_type, **fields}))
            return True
        except (RuntimeError, WebSocketDisconnect):
            self.disconnect(player_id, ws)
            return False


notifier = Notifier()
