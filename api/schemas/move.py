from pydantic import BaseModel


class MoveInformation(BaseModel):
    """Move information."""

    name: str
    power: int
    accuracy: int
    description: str
    slot: int


class MonsterMoveResponse(BaseModel):
    """List of moves response."""

    moves: list[MoveInformation]
