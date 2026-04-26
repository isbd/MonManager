from .base import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

class MonsterType(Base):
    __tablename__ = "monster_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class TypeEffectiveness(Base):
    __tablename__ = "type_effectiveness"

    attacking_type_id = Column(Integer, ForeignKey("monster_types.id"), primary_key=True)
    defending_type_id = Column(Integer, ForeignKey("monster_types.id"), primary_key=True)
    multiplier = Column(Float, nullable=False)

class Move(Base):
    __tablename__ = 'moves'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    # Stats
    type_id = Column(Integer, ForeignKey("monster_types.id"))
    move_type = relationship("MonsterType")
