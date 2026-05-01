from .base import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class PlayerInstance(Base):
    __tablename__ = "player_instances"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    monsters = relationship("MonsterInstance", back_populates="owner")
    active_encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True)
    active_encounter = relationship("Encounter", foreign_keys=[active_encounter_id])
