from typing import Optional

from pydantic import BaseModel


class WildEncounterResponse(BaseModel):
    """Display the species."""

    success: bool
    message: str
    encounter_id: Optional[int] = None
    name: Optional[str] = None
