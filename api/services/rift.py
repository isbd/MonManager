from sqlalchemy.ext.asyncio import AsyncSession

import time
from crud import rift_crud
from models.rift import RiftInstance, RiftState, RiftType
from schemas.rift import RiftCreateResponse


async def create_rift(db: AsyncSession, x_coord: int, z_coord: int) -> RiftCreateResponse:
    current_time = time.time_ns() // 1_000_000
    # 5 minutes
    duration = 300000

    """Create a rift."""
    rift_instance = RiftInstance(
        x_coord = x_coord,
        z_coord = z_coord,
        radius = 20,
        state = RiftState.OPEN,
        opened_at = current_time,
        expires_at = current_time + duration,
        rift_type = RiftType.NORMAL,
    )
    rift = await rift_crud.create(db, rift_instance)

    return rift
