from pydantic import BaseModel


class PlayerCreate(BaseModel):
    """Player creation."""

    name: str


class PlayerResponse(BaseModel):
    """Player return."""

    id: int
    name: str

    class Config:
        from_attributes = True
