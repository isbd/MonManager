import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_player
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
    # TODO: Fix return to return success, monster_id, encounter_id and name only. Don't auto catch
    a = random.randint(0, 10)
    if a > 5:
        return WildEncounterResponse(success=False, message="No monster appeared...")

    result = await db.execute(
        select(MonsterSpecies).where(MonsterSpecies.name == "Goblin")
    )
    species = result.scalar_one_or_none()

    if not species:
        raise HTTPException(status_code=400, detail="Failed to find GOBLIN")

    wild_monster = MonsterInstance(
        species_id=species.id,
        max_hp=4,
        current_hp=4,
        level=1,
        in_party=False,
        owner_id=player.id,
    )
    db.add(wild_monster)
    await db.commit()
    await db.refresh(wild_monster)
    # Return an encounter, with the ID
    # Lock player into encounter via status change

    return WildEncounterResponse(
        success=True,
        message=f"A wild {species.name} appeared!",
        id=species.id,
        name=species.name,
        description=species.description,
    )


# PVP
# Ensure both challenger/challenged have null active encounters
# Set challenger.active_encounter_id
# Set challenged.active_encounter_id

# PVE
# Ensure challenger has null active encounter
# Set challenger.active_encounter_id

# Once encounter is over, must null the active_encounter!
