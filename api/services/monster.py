import datetime
import random

from sqlalchemy.ext.asyncio import AsyncSession

from crud import monster_crud
from models.monster import MonsterInstance, MonsterSpecies


def get_current_spawn_time() -> str:
    hour = datetime.datetime.now().hour
    return "day" if hour % 2 else "night"


async def roll_species(db: AsyncSession, by_time: bool = True) -> MonsterSpecies:
    """Roll for wild species."""
    if by_time:
        spawn_time = get_current_spawn_time()
    else:
        spawn_time = "any"
    options = await monster_crud.get_spawnable_species(db, spawn_time)

    if not options:
        return None

    return random.choices(
        options,
        weights=[species_instance.spawn_weight for species_instance in options],
        k=1,
    )[0]


async def create_monster_instance(
    db: AsyncSession, species: MonsterSpecies
) -> MonsterInstance:
    """Create an instance of a monster."""
    # TODO: Randomize the stats. Optionally set owner_id
    monster = MonsterInstance(
        species_id=species.id,
        max_hp=4,
        current_hp=4,
        level=1,
        in_party=False,
        owner_id=None,
    )
    return await monster_crud.create_instance(db, monster)
