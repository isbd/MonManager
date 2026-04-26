from .base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class PlayerInstance(Base):
    __tablename__ = "player_instances"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    monsters = relationship("MonsterInstance", back_populates="owner")
