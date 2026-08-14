from pydantic import BaseModel


class RiftCreate(BaseModel):
    """Rift creation."""

    x_coord: int
    z_coord: int


class CalibrateResponse(BaseModel):
    """Rift calibration response."""

    success: bool
    message: str


class RiftFishResponse(BaseModel):
    """Rift fishing response."""

    success: bool
    distance: int
    error_message: str


class RiftCreateResponse(BaseModel):
    """Rift creation success."""

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
