from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_player
from models.player import PlayerInstance
from schemas.encounter import (
    AttemptChallenge,
    ChallengeCancel,
    ChallengeCancelResponse,
    ChallengeEncounterResponse,
    ChallengeList,
    ChallengeResponse,
    EncounterDetails,
    RespondChallenge,
    SurrenderResponse,
    WildEncounterResponse,
)
from services import encounter_service

router = APIRouter()


@router.post("/challenge", response_model=ChallengeEncounterResponse)
async def attempt_challenge(
    body: AttemptChallenge,
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Attempt to create a challenge encounter."""

    return await encounter_service.attempt_challenge(db, player, body.player_id)


@router.post("/challenge/respond", response_model=ChallengeResponse)
async def respond_challenge(
    body: RespondChallenge,
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Respond to a challenge encounter."""

    return await encounter_service.challenge_response(
        db, player, body.challenge_id, body.accept
    )


@router.post("/challenge/cancel", response_model=ChallengeCancelResponse)
async def cancel_challenge(
    body: ChallengeCancel,
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Cancel a challenge request."""

    return await encounter_service.cancel_challenge(db, player, body.challenge_id)


@router.get("/challenges", response_model=ChallengeList)
async def current_challenges(
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Fetch current challenges."""

    return await encounter_service.current_challenges(db, player)


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


@router.get("/", response_model=EncounterDetails)
async def current_encounter(
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Fetch information about the player's current encounter."""

    return await encounter_service.get_current_encounter_details(db, player)
