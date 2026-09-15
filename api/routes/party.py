from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_player
from models.player import PlayerInstance
from schemas.party import (
    AddRequest,
    AddResponse,
    GetPartyReponse,
    RemoveRequest,
    RemoveResponse,
    SwapRequest,
    SwapResponse,
)
from services import party_service

router = APIRouter()


@router.get("/", response_model=GetPartyReponse)
async def get_party(
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Get current user's party."""
    return await party_service.get_formatted_party(db, player)


@router.post("/swap", response_model=SwapResponse)
async def swap_spots(
    body: SwapRequest,
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Swap party spots."""
    return await party_service.swap_slots(db, player, body.slot_a, body.slot_b)


@router.post("/remove", response_model=RemoveResponse)
async def remove(
    body: RemoveRequest,
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Remove from party."""
    return await party_service.empty_slot(db, player, body.slot)


@router.post("/add", response_model=AddResponse)
async def add(
    body: AddRequest,
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Add to party."""
    return await party_service.assign_slot(db, player, body.monster_id, body.slot)
