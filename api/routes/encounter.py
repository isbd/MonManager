from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.player import PlayerInstance
from models.monster import MonsterSpecies, MonsterInstance
from schemas.encounter import WildEncounterCreate, WildEncounterResponse
import random

router = APIRouter()


@router.post("/wild", response_model=WildEncounterResponse)
async def attempt_encounter(
    body: WildEncounterCreate, db: AsyncSession = Depends(get_db)
):
    """Attempt to create an encounter."""

    result = await db.execute(
        select(PlayerInstance).where(PlayerInstance.name == body.name)
    )
    existing = result.scalar_one_or_none()

    if not existing:
        raise HTTPException(status_code=400, detail="Player not found")

    a = random.randint(0, 10)
    if a > 5:
        raise HTTPException(status_code=401, detail="Number was too high!")

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
        owner_id=existing.id,
    )
    db.add(wild_monster)
    await db.commit()
    await db.refresh(wild_monster)
    # Return an encounter

    return species


# PVP
# Ensure both challenger/challenged have null active encounters
# Set challenger.active_encounter_id
# Set challenged.active_encounter_id

# PVE
# Ensure challenger has null active encounter
# Set challenger.active_encounter_id

# Once encounter is over, must null the active_encounter!
