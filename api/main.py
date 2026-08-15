from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

# Required for the create_all
import models  # noqa: F401
from database import engine
from dependencies import get_current_player
from models.base import Base
from routes import battle, encounter, monster, player, rift, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # May need job handling
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(player.router, prefix="/player", tags=["Player"])
app.include_router(
    encounter.router,
    prefix="/encounter",
    tags=["Encounter"],
    dependencies=[Depends(get_current_player)],
)
app.include_router(
    monster.router,
    prefix="/monster",
    tags=["Monster"],
    dependencies=[Depends(get_current_player)],
)
app.include_router(
    battle.router,
    prefix="/battle",
    tags=["Battle"],
    dependencies=[Depends(get_current_player)],
)
app.include_router(
    rift.router,
    prefix="/rift",
    tags=["Rift"],
    dependencies=[Depends(get_current_player)],
)

# Websocket status notifier
app.include_router(websocket.router, prefix="/websocket", tags=["Websocket"])
