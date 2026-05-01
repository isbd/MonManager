from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from database import engine
from dependencies import get_current_player
from models import encounter, monster, player
from models.base import Base
from routes import encounter, monster, player


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
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
