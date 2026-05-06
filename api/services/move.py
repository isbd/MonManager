from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud import move_crud
from schemas.move import MonsterMoveResponse, MoveInformation


async def get_monster_moves(db: AsyncSession, monster_id: int) -> MonsterMoveResponse:
    """Grab a monsters moves."""

    move_instances = await move_crud.get_monster_moves(db, monster_id)
    if not move_instances:
        raise HTTPException(
            status_code=404,
            detail=f"Unable to fetch monster ID:{monster_id} moves.",
        )

    moves = []
    for move_instance in move_instances:
        move_info = MoveInformation(
            name=move_instance.move.name,
            power=move_instance.move.power,
            accuracy=move_instance.move.accuracy,
            description=move_instance.move.description,
            slot=move_instance.slot,
        )
        moves.append(move_info)

    return MonsterMoveResponse(moves=moves)
