from pydantic import BaseModel
from typing import Optional


class WildEncounterResponse(BaseModel):
    """Display the species."""

    success: bool
    message: str
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
