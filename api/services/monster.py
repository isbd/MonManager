import datetime
import random
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from crud import monster_crud, move_crud
from models.monster import MonsterInstance, MonsterSpecies
from models.move import MoveInstance


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
    db: AsyncSession, species: MonsterSpecies, owner_id: int = None
) -> MonsterInstance:
    """Create an instance of a monster."""
    # TODO: Randomize the stats. Optionally set owner_id
    monster = MonsterInstance(
        species_id=species.id,
        max_hp=4,
        current_hp=4,
        level=1,
        in_party=False,
        owner_id=owner_id,
    )

    monster = await monster_crud.create_instance(db, monster)

    for slot, move_id in enumerate(species.starter_moves, start=1):
        move_instance = MoveInstance(monster_id=monster.id, slot=slot, move_id=move_id)
        await move_crud.create_instance(db, move_instance)
    return monster


# TODO: replace this with a party system
async def grab_players_monster(
    db: AsyncSession, player_id: int
) -> Optional[MonsterInstance]:
    """Grab players first monster instance."""
    monsters = await monster_crud.get_instances_by_player(db, player_id)
    if not monsters:
        return None
    return monsters[0]
