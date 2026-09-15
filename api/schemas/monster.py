from typing import Optional

from pydantic import BaseModel


class MonsterSpeciesInfo(BaseModel):
    """Monster species information."""

    name: str
    texture: str

    class Config:
        from_attributes = True


class MonstersResponse(BaseModel):
    """Monsters response."""

    id: int
    nickname: Optional[str] = None
    current_hp: int
    max_hp: int
    level: int
    species: MonsterSpeciesInfo
    party_slot: int

    class Config:
        from_attributes = True
