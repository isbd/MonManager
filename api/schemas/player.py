from pydantic import BaseModel


class PlayerCreate(BaseModel):
    """Player creation."""

    name: str


class PlayerCreateResponse(BaseModel):
    """Player creation success with API key."""

    id: int
    name: str
    api_key: str

    class Config:
        from_attributes = True


class PlayerResponse(BaseModel):
    """Player return."""

    id: int
    name: str

    class Config:
        from_attributes = True
