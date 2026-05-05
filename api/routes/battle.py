from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_player
from models.player import PlayerInstance
from schemas.battle import CatchResponse, AttackRequest
from services import battle_service

router = APIRouter()


@router.post("/catch", response_model=CatchResponse)
async def attempt_catch(
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Attempt to capture a monster."""
    return await battle_service.attempt_catch(db, player)


@router.post("/attack", response_model=CatchResponse)
async def attempt_attack(
    body: AttackRequest,
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Attempt an attack."""
    return await battle_service.attempt_attack(db, player, body.attack_id)
