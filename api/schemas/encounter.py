from typing import List, Optional

from pydantic import BaseModel


class WildEncounterResponse(BaseModel):
    """Result for wild encounter attempt."""

    success: bool
    message: str
    encounter_id: Optional[int] = None
    name: Optional[str] = None


class SurrenderResponse(BaseModel):
    """Result for surrender attempt."""

    success: bool
    message: str


class AttemptChallenge(BaseModel):
    """Attempted player id to challenge."""

    player_id: int


class ChallengeEncounterResponse(BaseModel):
    """Result of challenge request."""

    success: bool
    message: str


class ChallengeDetails(BaseModel):
    """Details over specific challenge"""

    challenge_id: int
    challenger: str
    challenger_id: int
    challenged: str
    challenged_id: int


class ChallengeList(BaseModel):
    """Current challenges."""

    received_challenges: List[ChallengeDetails]
    sent_challenge: Optional[ChallengeDetails]


class RespondChallenge(BaseModel):
    """Submitted response to challenge."""

    challenge_id: int
    accept: bool


class ChallengeResponse(BaseModel):
    """Result of challenge response."""

    success: bool
    message: str


class ChallengeCancelResponse(BaseModel):
    """Result of challenge cancel response."""

    success: bool
    message: str


class ChallengeCancel(BaseModel):
    """Attempt to cancel a challenge."""

    challenge_id: int


class EncounterMonsterDetails(BaseModel):
    """Details about a specific monster in an encounter."""

    id: int
    current_health: int
    max_health: int
    texture: str


class EncounterDetails(BaseModel):
    """Details about an encounter."""

    id: int
    encounter_type: str
    self_id: int
    self_mon: EncounterMonsterDetails
    opponent_id: Optional[int]
    opponent_mon: EncounterMonsterDetails

    class Config:
        from_attributes = True
