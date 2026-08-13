import enum

from sqlalchemy import BigInteger, Column, Enum, Integer

from .base import Base


class RiftState(enum.Enum):
    OPEN = "open"
    COLLAPSING = "collapsing"
    CLOSED = "closed"


class RiftType(enum.Enum):
    NORMAL = "normal"


class RiftInstance(Base):
    __tablename__ = "rift_instance"

    id = Column(Integer, primary_key=True)
    x_coord = Column(Integer, nullable=False)
    z_coord = Column(Integer, nullable=False)
    radius = Column(Integer, nullable=False)
    state = Column(Enum(RiftState), nullable=False)
    opened_at = Column(BigInteger, nullable=False)  # EPOCH
    expires_at = Column(BigInteger, nullable=False)  # EPOCH
    rift_type = Column(Enum(RiftType), nullable=False)
    # Spawn reason mechanic? Allows for specific player lure, event
