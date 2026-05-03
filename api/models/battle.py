from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from .base import Base


class BattleTurn(Base):
    __tablename__ = "battle_turns"

    id = Column(Integer, primary_key=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False)
    turn_number = Column(Integer, nullable=False)

    challenger_action = Column(String, nullable=True)
    challenged_action = Column(String, nullable=True)

    resolved = Column(Boolean, nullable=False, default=False)
