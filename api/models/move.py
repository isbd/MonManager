from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


# class MonsterType(Base):
#     __tablename__ = "monster_types"

#     id = Column(Integer, primary_key=True)
#     name = Column(String, unique=True, nullable=False)


# class TypeEffectiveness(Base):
#     __tablename__ = "type_effectiveness"

#     attacking_type_id = Column(
#         Integer, ForeignKey("monster_types.id"), primary_key=True
#     )
#     defending_type_id = Column(
#         Integer, ForeignKey("monster_types.id"), primary_key=True
#     )
#     multiplier = Column(Float, nullable=False)

# TODO: Add typing

class Move(Base):
    __tablename__ = "moves"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    power = Column(Integer, nullable=False)
    accuracy = Column(Integer, nullable=False)

    # Stats
    # type_id = Column(Integer, ForeignKey("monster_types.id"))
    # move_type = relationship("MonsterType")

class MoveInstance(Base):
    __tablename__ = "move_instances"

    monster_id = Column(Integer, ForeignKey("monster_instances.id", ondelete="CASCADE"), primary_key=True)
    slot = Column(Integer, primary_key=True)
    move_id = Column(Integer, ForeignKey("moves.id"))
    move = relationship("Move")
