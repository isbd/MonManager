from fastapi import WebSocket
from typing import Optional

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


    async def poke(self, player_id: int, event: dict):
        ws = self._connections.get(player_id)
        if ws:
            await ws.send_json(event)


notifier = Notifier()