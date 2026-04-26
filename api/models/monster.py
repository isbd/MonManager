from .base import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class MonsterSpecies(Base):
    __tablename__ = "species"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)

class MonsterInstance(Base):
    __tablename__ = "monster_instance"

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
