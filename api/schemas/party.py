from typing import Union

from pydantic import BaseModel

from schemas.monster import MonstersResponse


class GetPartyReponse(BaseModel):
    """Get party response."""

    monsters: list[Union[MonstersResponse, int]]
    party_size: int
    active_slot: int


class SwapResponse(BaseModel):
    """Swap party spots response."""

    success: bool


class AddResponse(BaseModel):
    """Get monster to party response."""

    success: bool


class RemoveResponse(BaseModel):
    """Remove monster from party response."""

    success: bool


class SwapRequest(BaseModel):
    """Request to swap monster in party."""

    slot_a: int
    slot_b: int


class RemoveRequest(BaseModel):
    """Request to remove monster from party."""

    slot: int


class AddRequest(BaseModel):
    """Request to add monster to party."""

    monster_id: int
    slot: int
