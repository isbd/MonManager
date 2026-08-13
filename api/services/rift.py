import time

from sqlalchemy.ext.asyncio import AsyncSession

from crud import rift_crud
from models.rift import RiftInstance, RiftState, RiftType
from schemas.rift import RiftCreateResponse


async def create_rift(
    db: AsyncSession, x_coord: int, z_coord: int
) -> RiftCreateResponse:
    current_time = time.time_ns() // 1_000_000
    # 5 minutes
    duration = 300000

    """Create a rift."""
    rift_instance = RiftInstance(
        x_coord=x_coord,
        z_coord=z_coord,
        radius=20,
        state=RiftState.OPEN,
        opened_at=current_time,
        expires_at=current_time + duration,
        rift_type=RiftType.NORMAL,
    )
    rift = await rift_crud.create(db, rift_instance)

    return rift


async def fetch_nearest_rift(
    db: AsyncSession, x_coord: int, z_coord: int
) -> RiftInstance:
    # Get a list of all active rifts
    rift_list = await rift_crud.get_all(db)

    closest = None
    closest_sum = None
    for rift in rift_list:

        if time.time_ns() // 1_000_000 > rift.expires_at:
            # Remove rift?
            continue

        temp_sum = abs(rift.x_coord - x_coord) + abs(rift.z_coord - z_coord)
        if closest_sum is None or closest_sum > temp_sum:
            closest_sum = temp_sum
            closest = rift

    return closest


# Function for creating encounter points, maybe owned by the rift itself?

# Function for fetching an encounter point?

# Function for closing a rift?
