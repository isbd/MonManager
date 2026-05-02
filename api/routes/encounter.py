import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_player
from models.encounter import Encounter, EncounterType
from models.monster import MonsterInstance, MonsterSpecies
from models.player import PlayerInstance
from schemas.encounter import WildEncounterResponse

router = APIRouter()


@router.post("/wild", response_model=WildEncounterResponse)
async def attempt_encounter(
    db: AsyncSession = Depends(get_db),
    player: PlayerInstance = Depends(get_current_player),
):
    """Attempt to create an encounter."""
    # TODO: Check player cooldown, randomizer, random monster.

    if player.active_encounter_id:
        raise HTTPException(status_code=400, detail="Already in an encounter")

    a = random.randint(0, 10)
    if a > 5:
        return WildEncounterResponse(success=False, message="No monster appeared...")

    result = await db.execute(
        select(MonsterSpecies).where(MonsterSpecies.name == "Goblin")
    )
    species = result.scalar_one_or_none()

    if not species:
        raise HTTPException(status_code=400, detail="Failed to find GOBLIN")

    # Create the creature
    # TODO: Randomize the creature
    wild_monster = MonsterInstance(
        species_id=species.id,
        max_hp=4,
        current_hp=4,
        level=1,
        in_party=False,
        owner_id=None,
    )
    db.add(wild_monster)
    await db.commit()
    await db.refresh(wild_monster)

    # Create the encounter
    encounter = Encounter(
        active=True,
        encounter_type=EncounterType.wild,
        challenger_id=player.id,
        challenger_mon_id=None,
        wild_monster_id=wild_monster.id,
    )
    db.add(encounter)
    await db.commit()
    await db.refresh(encounter)
    player.active_encounter_id = encounter.id
    await db.commit()
    await db.refresh(player)

    return WildEncounterResponse(
        success=True,
        message=f"A wild {species.name} appeared!",
        encounter_id=encounter.id,
        name=species.name,
    )


# PVP
# Ensure both challenger/challenged have null active encounters
# Set challenger.active_encounter_id
# Set challenged.active_encounter_id

# Once encounter is over, must null the active_encounter!
