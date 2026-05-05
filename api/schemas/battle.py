from typing import Optional

from pydantic import BaseModel


class CatchResponse(BaseModel):
    """Result from catch attempt."""

    success: bool
    message: str
    monster_id: Optional[int]

class AttackRequest(BaseModel):
    """Request to attack."""

    attack_id: int
    