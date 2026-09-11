from pydantic import BaseModel


class HealRequest(BaseModel):
    """Heal request including coords."""

    x: int
    z: int


class HealResponse(BaseModel):
    """Heal response."""

    success: bool


class NearestShopResponse(BaseModel):
    """Coords of nearest shop."""

    x_coord: int
    z_coord: int
    radius: int
