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


class StatusEffect(BaseModel):
    """Details about a monsters status effect in a turn."""

    effect_message: str = ""
    damage_taken: int = 0
    health_gained: int = 0


class TurnAttackDetails(BaseModel):
    """Details about a monsters attack in a turn."""

    move_name: str
    missed: bool
    damage_dealt: int
    target_max_health: int
    target_pre_damage_health: int


class TurnDetails(BaseModel):
    """Battle turn information."""

    turn_number: int
    self_mon_attack: TurnAttackDetails
    opponent_mon_attack: TurnAttackDetails
    self_mon_status: StatusEffect
    opponent_mon_status: StatusEffect
    self_first: bool


class AttackDetails(BaseModel):
    """Details about attack attempt."""

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
    pending: bool
    challenger_attack: Optional[AttackDetails]
    challenged_attack: Optional[AttackDetails]


# TODO: Change these to sub classes
