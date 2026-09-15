from sqlalchemy import (
    JSON,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base

PARTY_SIZE = 6


class MonsterSpecies(Base):
    __tablename__ = "species"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    spawn_weight = Column(Integer, server_default="100", nullable=False)
    spawn_time = Column(
        Enum("any", "day", "night", name="spawn_time_enum"),
        default="any",
        nullable=False,
    )
    starter_moves = Column(JSON, nullable=False, server_default="[]")
    texture = Column(String)

    def __repr__(self):
        return f"({self.id}) {self.name} {self.description}"


class MonsterInstance(Base):
    __tablename__ = "monster_instances"
    __table_args__ = (
        UniqueConstraint("owner_id", "party_slot", name="uq_owner_party_slot"),
    )

    id = Column(Integer, primary_key=True)
    nickname = Column(String)
    party_slot = Column(
        Integer,
        CheckConstraint(
            f"party_slot BETWEEN 1 AND {PARTY_SIZE}", name="party_slot_range"
        ),
        nullable=True,
    )

    current_hp = Column(Integer, nullable=False)
    max_hp = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)

    moves = relationship("MoveInstance", cascade="all, delete-orphan")

    species_id = Column(Integer, ForeignKey("species.id"))
    owner_id = Column(Integer, ForeignKey("player_instances.id"))

    species = relationship("MonsterSpecies")
    owner = relationship("PlayerInstance", back_populates="monsters")

    @property
    def in_party(self):
        return self.party_slot is not None
