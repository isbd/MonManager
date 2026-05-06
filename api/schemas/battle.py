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


# TODO: Modify this, only for testing purposes right now
class AttackResponse(BaseModel):
    """Response for attack."""

    success: bool
    attack_name: Optional[str]
    damage_dealth: Optional[int]
    enemy_health: Optional[int]
