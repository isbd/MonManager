import datetime
import random
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud import monster_crud, move_crud
from models.monster import MonsterInstance, MonsterSpecies
from models.move import MoveInstance
from models.player import PlayerInstance


def get_current_spawn_time() -> str:
    hour = datetime.datetime.now().hour
    return "day" if hour % 2 else "night"


def reverse_monster_image(image_text: str) -> str:
    """Reverse text image."""
    new_image_text = ""
    for line in image_text.split("\n"):
        new_image_text += f"{line[::-1]}\n"
    return new_image_text[:-1]


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
        max_hp=30,
        current_hp=30,
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


async def heal_players_monster(db: AsyncSession, player_id: int) -> bool:
    """Heal players first monster instance."""
    monster = await grab_players_monster(db, player_id)
    if monster is None:
        return False
    monster.current_hp = monster.max_hp
    await monster_crud.update_instance(db, monster)
    return True


async def party_fight_validation(db: AsyncSession, player: PlayerInstance):
    """Ensure a player's party is valid for an encounter."""
    mon_instance = await grab_players_monster(db, player.id)
    if mon_instance is None:
        raise HTTPException(
            status_code=400,
            detail=f"User {player.name} is missing a mon to start this battle",
        )
    if mon_instance.current_hp < 1:
        raise HTTPException(
            status_code=400, detail="Party is not suitable for encounter."
        )
