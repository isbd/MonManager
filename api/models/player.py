from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class PlayerInstance(Base):
    __tablename__ = "player_instances"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    monsters = relationship("MonsterInstance", back_populates="owner")
    active_encounter_id = Column(
        Integer, ForeignKey("encounters.id", ondelete="SET NULL"), nullable=True
    )
    active_encounter = relationship("Encounter", foreign_keys=[active_encounter_id])
