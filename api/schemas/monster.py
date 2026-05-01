from typing import Optional

from pydantic import BaseModel


class MonsterSpeciesInfo(BaseModel):
    name: str

    class Config:
        from_attributes = True


class MonstersResponse(BaseModel):
    id: int
    nickname: Optional[str] = None
    current_hp: int
    max_hp: int
    level: int
    species: MonsterSpeciesInfo

    class Config:
        from_attributes = True
