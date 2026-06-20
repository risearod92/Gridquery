from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class DBSubstationAsset(Base):
    __tablename__ = "substations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    capacity_mw = Column(Integer, nullable=False)
    state = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)