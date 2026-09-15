from typing import List, Union

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import services.monster as monster_service
from crud import monster_crud
from models.monster import PARTY_SIZE, MonsterInstance
from models.player import PlayerInstance
from schemas.party import GetPartyReponse


def validate_slots(slots: List[int]) -> None:
    """Validate list of slots are within expected range."""
    for slot in slots:
        if slot > PARTY_SIZE or slot < 1:
            raise HTTPException(
                status_code=400, detail=f"Slot {slot} is out of range of 1-{PARTY_SIZE}"
            )


def validate_party_management(player: PlayerInstance) -> None:
    """Validate party management is allowed."""
    if player.active_encounter is not None:
        raise HTTPException(
            status_code=400, detail="Unable to manage party while in encounter!"
        )


async def get_formatted_party(
    db: AsyncSession, player: PlayerInstance
) -> GetPartyReponse:
    party_response = await get_party(db, player)
    idx = 0
    formatted_monsters = []
    for slot_num in range(1, PARTY_SIZE + 1):
        if idx + 1 > len(party_response.monsters):
            formatted_monsters.append(slot_num)
        else:
            if party_response.monsters[idx].party_slot == slot_num:
                formatted_monsters.append(party_response.monsters[idx])
                idx += 1
            else:
                formatted_monsters.append(slot_num)

    party_response.monsters = formatted_monsters
    return party_response


async def get_party(db: AsyncSession, player: PlayerInstance) -> GetPartyReponse:
    """Fetch player's current party."""
    monster_list = await monster_crud.get_party(db, player.id)
    return GetPartyReponse(
        monsters=monster_list, party_size=PARTY_SIZE, active_slot=player.active_slot
    )


async def get_empty_slots(db: AsyncSession, player: PlayerInstance) -> List[int]:
    """Fetch list of empty slots."""
    used_slots = await monster_crud.get_used_party_slots(db, player.id)
    return sorted(set(range(1, PARTY_SIZE + 1)) - used_slots)


async def empty_slot(
    db: AsyncSession, player: PlayerInstance, slot_number: int
) -> None:
    """Empty current players selected slot."""
    validate_slots([slot_number])
    validate_party_management(player)
    slot_monster = await monster_crud.get_party_slot(db, player.id, slot_number)
    if slot_monster is None:
        return

    used_slots = await monster_crud.get_used_party_slots(db, player.id)
    if len(used_slots) < 1:
        raise HTTPException(
            status_code=400,
            detail="Removing monster from slot causes invalid party size",
        )

    await monster_crud.set_party_slot(db, slot_monster, None)
    await db.commit()
    return None


async def swap_slots(
    db: AsyncSession, player: PlayerInstance, slot_a: int, slot_b: int
) -> None:
    """Switch monsters in two slots."""
    validate_slots([slot_a, slot_b])
    validate_party_management(player)
    slot_monster_a = await monster_crud.get_party_slot(db, player.id, slot_a)
    slot_monster_b = await monster_crud.get_party_slot(db, player.id, slot_b)

    if slot_monster_a is not None:
        await monster_crud.set_party_slot(db, slot_monster_a, slot_b)
    if slot_monster_b is not None:
        await monster_crud.set_party_slot(db, slot_monster_b, slot_a)

    if player.active_slot == slot_a:
        player.active_slot = slot_b
    elif player.active_slot == slot_b:
        player.active_slot = slot_a
    await db.commit()


async def assign_slot(
    db: AsyncSession,
    player: PlayerInstance,
    monster_ref: Union[int, MonsterInstance],
    slot_num: int,
) -> None:
    """Assign a monster a slot."""
    monster = await monster_service.resolve_monster(db, monster_ref)
    if monster.party_slot is not None:
        await swap_slots(db, player, monster.party_slot, slot_num)
        return

    validate_party_management(player)
    collision_monster = await monster_crud.get_party_slot(db, player.id, slot_num)
    if collision_monster is None:
        await monster_crud.set_party_slot(db, monster, slot_num)
        db.commit()
        return

    empty_slots = await get_empty_slots(db, player)
    # Shift collisions to empty slots if able
    if len(empty_slots) > 0:
        await monster_crud.set_party_slot(db, collision_monster, empty_slots[0])
    else:
        await monster_crud.set_party_slot(db, collision_monster, None)
    await monster_crud.set_party_slot(db, monster, slot_num)
    await db.commit()


async def set_active(db: AsyncSession, player: PlayerInstance, slot_num: int) -> None:
    """Set player's active slot."""
    validate_slots([slot_num])
    player.active_slot = slot_num
    await db.commit()
