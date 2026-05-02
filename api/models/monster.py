from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


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

    def __repr__(self):
        return f"({self.id}) {self.name} {self.description}"


class MonsterInstance(Base):
    __tablename__ = "monster_instances"

    id = Column(Integer, primary_key=True)
    nickname = Column(String)
    in_party = Column(Boolean, default=False, nullable=False)

    current_hp = Column(Integer, nullable=False)
    max_hp = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)

    species_id = Column(Integer, ForeignKey("species.id"))
    owner_id = Column(Integer, ForeignKey("player_instances.id"))

    species = relationship("MonsterSpecies")
    owner = relationship("PlayerInstance", back_populates="monsters")
