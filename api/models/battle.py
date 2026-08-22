from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import Base


class BattleTurn(Base):
    __tablename__ = "battle_turns"

    id = Column(Integer, primary_key=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False)
    turn_number = Column(Integer, nullable=False)
    resolved = Column(Boolean, nullable=False, default=False)

    challenger_mon_id = Column(
        Integer, ForeignKey("monster_instances.id"), nullable=True
    )
    challenged_mon_id = Column(
        Integer, ForeignKey("monster_instances.id"), nullable=True
    )

    challenger_move_id = Column(Integer, ForeignKey("moves.id"), nullable=True)
    challenged_move_id = Column(Integer, ForeignKey("moves.id"), nullable=True)

    challenger_max_hp = Column(Integer, nullable=True)
    challenged_max_hp = Column(Integer, nullable=True)

    challenger_pre_damage_health = Column(Integer, nullable=True)
    challenged_pre_damage_health = Column(Integer, nullable=True)

    challenger_damage_dealt = Column(Integer, nullable=True)
    challenged_damage_dealt = Column(Integer, nullable=True)
    challenger_move_missed = Column(Boolean, nullable=True)
    challenged_move_missed = Column(Boolean, nullable=True)

    challenger_move = relationship("Move", foreign_keys=[challenger_move_id])
    challenged_move = relationship("Move", foreign_keys=[challenged_move_id])
