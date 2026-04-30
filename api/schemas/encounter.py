from pydantic import BaseModel


class WildEncounterCreate(BaseModel):
    """Wild encounter creation."""

    name: str


class WildEncounterResponse(BaseModel):
    """Display the species."""

    id: int
    name: str
    description: str

    class Config:
        from_attributes = True
