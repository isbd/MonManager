from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_player
from models.player import PlayerInstance
from schemas.battle import CatchResponse
from services import battle_service

router = APIRouter()


@router.post("/catch", response_model=CatchResponse)
async def attempt_catch(
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Attempt to capture a monster."""
    if player.active_encounter_id is None:
        raise HTTPException(status_code=400, detail="No active encounter")

    return await battle_service.attempt_catch(db, player)
