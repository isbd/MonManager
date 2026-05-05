from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_player
from models.player import PlayerInstance
from schemas.encounter import SurrenderResponse, WildEncounterResponse, EncounterDetails
from services import encounter_service

router = APIRouter()


@router.post("/wild", response_model=WildEncounterResponse)
async def attempt_encounter(
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Attempt to create an encounter."""
    if player.active_encounter_id:
        raise HTTPException(status_code=400, detail="Already in an encounter")

    return await encounter_service.attempt_wild_encounter(db, player)


@router.post("/surrender", response_model=SurrenderResponse)
async def attempt_surrender(
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Attempt to surrender from an encounter."""

    return await encounter_service.surrender(db, player)


@router.post("/", response_model=EncounterDetails)
async def current_encounter(
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Fetch information about the player's current encounter."""

    return await encounter_service.get_current_encounter_details(db, player)
