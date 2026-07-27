import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import Base


class EncounterState(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DECLINED = "declined"
    EXPIRED = "expired"
    COMPLETED = "completed"


class EncounterPerspective(enum.Enum):
    CHALLENGED = "challenged"
    CHALLENGER = "challenger"


class EncounterType(enum.Enum):
    WILD = "wild"
    PVP = "pvp"


# TODO: Explore expanding this into separate tables
class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(Integer, primary_key=True)
    active = Column(Enum(EncounterState), nullable=False)
    encounter_type = Column(Enum(EncounterType), nullable=False)

    # Shared
    challenger_id = Column(Integer, ForeignKey("player_instances.id"), nullable=False)
    challenger_mon_id = Column(
        Integer, ForeignKey("monster_instances.id"), nullable=True
    )

    # PvP only
    challenged_id = Column(Integer, ForeignKey("player_instances.id"), nullable=True)
    challenged_mon_id = Column(
        Integer, ForeignKey("monster_instances.id"), nullable=True
    )

    turns = relationship("BattleTurn", cascade="all, delete-orphan")
