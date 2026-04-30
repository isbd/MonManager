from pydantic import BaseModel


class MonsterListFetch(BaseModel):
    name: str


class MonstersResponse(BaseModel):
    id: int
    nickname: str

    class Config:
        from_attributes = True
