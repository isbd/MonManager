from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_player
from models.player import PlayerInstance
from schemas.battle import (
    AttackRequest,
    BattleResponse,
    CatchResponse,
    FillResponse,
    RoundDetails,
    SwapRequest,
)
from schemas.move import MonsterMoveResponse
from services import battle_service

router = APIRouter()


@router.post("/catch", response_model=CatchResponse)
async def attempt_catch(
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Attempt to capture a monster."""
    return await battle_service.attempt_catch(db, player)


@router.post("/swap", response_model=BattleResponse)
async def attempt_swap(
    body: SwapRequest,
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Attempt an swap active monster."""
    return await battle_service.attempt_swap(db, player, body.slot)


@router.post("/fill", response_model=FillResponse)
async def attempt_fill(
    body: SwapRequest,
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Attempt to fill empty spot from monster death."""
    return await battle_service.attempt_fill(db, player, body.slot)


@router.post("/attack", response_model=BattleResponse)
async def attempt_attack(
    body: AttackRequest,
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Attempt an attack."""
    return await battle_service.attempt_attack(db, player, body.attack_id)


@router.get("/moves", response_model=MonsterMoveResponse)
async def get_active_moves(
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Fetch information about the active monsters current moves."""
    return await battle_service.get_active_moves(db, player)


@router.get("/turn", response_model=RoundDetails)
async def get_latest_resolved_turn(
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Fetch the latest resolved turn."""
    return await battle_service.get_latest_turn(db, player)


@router.get("/{turn_number}", response_model=RoundDetails)
async def get_resolved_turn(
    turn_number: int,
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Fetch specific resolved turn."""
    return await battle_service.get_turn(db, player, turn_number)
