from sqlalchemy import Column, Integer

from .base import Base


class ShopInstance(Base):
    __tablename__ = "shop_instances"

    id = Column(Integer, primary_key=True)
    x_coord = Column(Integer, nullable=False)
    z_coord = Column(Integer, nullable=False)
    radius = Column(Integer, nullable=False)
    # Add different types of shops?
    # Add restock interval?
    # Add items?
