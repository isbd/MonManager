from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from routes import player, encounter, monster
from database import engine
from models.base import Base
from fastapi.security import APIKeyHeader
from dependencies import get_current_player
import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

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
