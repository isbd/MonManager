import enum

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import Base


class EncounterType(enum.Enum):
    wild = "wild"
    pvp = "pvp"


class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(Integer, primary_key=True)
    active = Column(Boolean, nullable=False)
    encounter_type = Column(Enum(EncounterType), nullable=False)

    # Shared
    challenger_id = Column(Integer, ForeignKey("player_instances.id"), nullable=False)
    challenger_mon_id = Column(
        Integer, ForeignKey("monster_instances.id"), nullable=True
    )

    # Wild only
    wild_monster_id = Column(Integer, ForeignKey("monster_instances.id"), nullable=True)

    # PvP only
    challenged_id = Column(Integer, ForeignKey("player_instances.id"), nullable=True)
    challenged_mon_id = Column(
        Integer, ForeignKey("monster_instances.id"), nullable=True
    )

    turns = relationship("BattleTurn", cascade="all, delete-orphan")


# TODO: Explore expanding this into separate tables
