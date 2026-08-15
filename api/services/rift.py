import math
import random
import time

from sqlalchemy.ext.asyncio import AsyncSession

from crud import rift_crud
from models.player import PlayerInstance
from models.rift import RiftInstance, RiftState, RiftType
from schemas.rift import (
    CalibrateResponse,
    RiftCreateResponse,
    RiftFishResponse,
    RiftResponse,
)
from services import encounter_service


async def create_rift(
    db: AsyncSession, x_coord: int, z_coord: int
) -> RiftCreateResponse:
    """Create rift at location."""
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
        charges=5,
    )
    rift = await rift_crud.create(db, rift_instance)

    return rift


def distance_calculation(rift: RiftInstance, x_coord: int, z_coord: int) -> float:
    """Euclidean distance calculation."""
    return int(math.hypot(rift.x_coord - x_coord, rift.z_coord - z_coord))


async def fetch_nearest_rift(
    db: AsyncSession, x_coord: int, z_coord: int
) -> RiftInstance:
    """Fetch nearest rift."""
    # Get a list of all active rifts
    rift_list = await rift_crud.get_all(db)

    closest = None
    closest_sum = None
    for rift in rift_list:
        if time.time_ns() // 1_000_000 > rift.expires_at:
            await rift_crud.stage_delete(db, rift)
            continue

        temp_sum = max(distance_calculation(rift, x_coord, z_coord) - rift.radius, 0)
        if closest_sum is None or closest_sum > temp_sum:
            closest_sum = temp_sum
            closest = rift

    await db.commit()
    return closest


async def get_all_rifts(db: AsyncSession) -> list[RiftResponse]:
    """Fetch all rifts."""
    rift_list = await rift_crud.get_all(db)
    valid_rifts = []
    for rift in rift_list:
        if time.time_ns() // 1_000_000 > rift.expires_at:
            await rift_crud.stage_delete(db, rift)
            continue
        print(f"{time.time_ns() // 1_000_000} vs {rift.expires_at}")
        valid_rifts.append(rift)
    await db.commit()

    return valid_rifts


async def fish_rifts(
    db: AsyncSession, player: PlayerInstance, x_coord: int, z_coord: int
) -> RiftFishResponse:
    """Rift fishing handler."""
    # TODO: player charges to prevent spam
    closest_rift = await fetch_nearest_rift(db, x_coord, z_coord)

    # TODO: replace placeholders with player stat pulls
    max_distance = 500

    if closest_rift is None:
        distance = max_distance + 1
    else:
        distance = max(
            distance_calculation(closest_rift, x_coord, z_coord) - closest_rift.radius,
            0,
        )

    if distance > max_distance:
        # TODO: Check if player can summon a new rift. Determine the type randomization
        theta = random.uniform(0, 2 * math.pi)
        r = max_distance * math.sqrt(random.random())
        x_random = x_coord + round(r * math.cos(theta))
        z_random = z_coord + round(r * math.sin(theta))
        closest_rift = await create_rift(db, x_random, z_random)

    distance = max(
        distance_calculation(closest_rift, x_coord, z_coord) - closest_rift.radius, 0
    )
    return RiftFishResponse(
        success=True,
        distance=round(distance),
        error_message="",
    )


async def calibrate(
    db: AsyncSession, player: PlayerInstance, x_coord: int, z_coord: int
) -> CalibrateResponse:
    """Calibrate in current rift."""
    # TODO: Player cooldown?
    closest_rift = await fetch_nearest_rift(db, x_coord, z_coord)
    distance = max(
        distance_calculation(closest_rift, x_coord, z_coord) - closest_rift.radius, 0
    )
    if distance > 0:
        return CalibrateResponse(
            success=False,
            message="No active rift detected.",
        )
    else:
        # TODO: Micro calibration instead of immediate encounter?
        closest_rift.charges = closest_rift.charges - 1
        encounter = await encounter_service.attempt_wild_encounter(db, player)
        return CalibrateResponse(
            success=encounter.success,
            message=encounter.message,
        )


# Function for creating encounter points, maybe owned by the rift itself?

# Function for fetching an encounter point?

# Function for closing a rift?
