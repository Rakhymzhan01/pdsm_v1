from sqlalchemy import Column, Integer, String, Float, Date
from app.core.database import Base

class Well(Base):
    __tablename__ = "wells"
    
    Well = Column("Well", String, primary_key=True, index=True)
    X = Column("X", String)
    Y = Column("Y", String) 
    Lat = Column("Lat", String)
    Lon = Column("Lon", String)
    Object = Column("Object", String)
    Year = Column("Year", String)