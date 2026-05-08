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


class AttackDetails(BaseModel):
    first: bool
    missed: bool
    damage_dealt: int
    move_name: str
    targets_current_health: int
    targets_total_health: int
    targets_pre_reduced_health: int


# TODO: Modify this, only for testing purposes right now
class BattleResponse(BaseModel):
    """Response for attack."""

    success: bool
    active: bool
    challenger_attack: Optional[AttackDetails]
    challenged_attack: Optional[AttackDetails]


# TODO: Change these to sub classes
