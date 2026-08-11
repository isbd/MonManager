from pydantic import BaseModel


class RiftCreate(BaseModel):
    """Rift creation."""

    x_coord: int
    z_coord: int


class RiftCreateResponse(BaseModel):
    """Rift creation success"""

    id: int
    x_coord: int
    z_coord: int

    class Config:
        from_attributes = True


class RiftResponse(BaseModel):
    """Rift return."""

    id: int
    x_coord: int
    z_coord: int

    class Config:
        from_attributes = True