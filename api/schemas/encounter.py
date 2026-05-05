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


class EncounterDetails(BaseModel):
    """Details about an encounter."""

    id: int
    encounter_type: str
    challenger_id: int
    challenger_mon_id: int
    wild_monster_id: Optional[int]
    challenged_id: Optional[int]
    challenged_mon_id: Optional[int]

    class Config:
        from_attributes = True
