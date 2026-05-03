from typing import Optional

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


class CatchResponse(BaseModel):
    """Result from catch attempt."""

    success: bool
    message: str
    monster_id: Optional[int]
