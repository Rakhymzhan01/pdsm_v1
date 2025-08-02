from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class PVT(Base):
    __tablename__ = "pvt"
    
    id = Column(Integer, primary_key=True, index=True)
    pressure = Column(Float)
    rs = Column(Float)
    bo = Column(Float)
    mu_o = Column(Float)
    rho_o = Column(Float)

class Tops(Base):
    __tablename__ = "tops"
    
    id = Column(Integer, primary_key=True, index=True)
    well_name = Column(String)
    formation = Column(String)
    top_depth = Column(Float)
    bottom_depth = Column(Float)