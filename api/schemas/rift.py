from pydantic import BaseModel


class RiftResponse(BaseModel):
    """Rift return."""

    id: int
    x_coords: int
    y_coords: int

    class Config:
        from_attributes = True