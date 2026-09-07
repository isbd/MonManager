from pydantic import BaseModel


class HealRequest(BaseModel):
    """Heal request including coords."""

    x: int
    z: int


class HealResponse(BaseModel):
    """Heal response."""

    success: bool
