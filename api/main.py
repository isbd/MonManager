from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import player
from database import engine
from models.base import Base
import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(player.router, prefix="/player", tags=["Player"])