from typing import Literal, Optional

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


class TurnAction(BaseModel):
    """Details about a turn action."""

    actor: Literal["self", "opponent"]
    actor_perspective: Literal["challenger", "challenged"]
    message: str
    move_name: str
    missed: bool
    damage_dealt: int
    target_max_health: int
    target_pre_damage_health: int


class RoundDetails(BaseModel):
    """Battle round information."""

    turn_number: int
    actions: list[TurnAction]
    self_mon_status: Optional[StatusEffect]
    opponent_mon_status: Optional[StatusEffect]


class BattleResponse(BaseModel):
    """Response for attack."""

    active: bool
    pending: bool
    round_details: Optional[RoundDetails]
