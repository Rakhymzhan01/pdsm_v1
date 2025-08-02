from sqlalchemy import Column, Integer, String, Float, Date
from app.core.database import Base

class Well(Base):
    __tablename__ = "wells"
    
    id = Column(Integer, primary_key=True, index=True)
    well_name = Column(String, index=True)
    x = Column(Float)
    y = Column(Float)
    lat = Column(Float)
    lon = Column(Float)
    kb = Column(Float)
    td = Column(Float)
    completion_date = Column(Date)
    status = Column(String)