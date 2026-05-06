from pydantic import BaseModel


class MoveInformation(BaseModel):
    name: str
    power: int
    accuracy: int
    description: str
    slot: int


class MonsterMoveResponse(BaseModel):
    moves: list[MoveInformation]
