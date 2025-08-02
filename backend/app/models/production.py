from sqlalchemy import Column, Integer, String, Float, Date
from app.core.database import Base

class Production(Base):
    __tablename__ = "prod"
    
    id = Column(Integer, primary_key=True, index=True)
    Date = Column(Date)
    well = Column(String)
    Qo_ton = Column(Float)
    Qw_m3 = Column(Float)
    Ql_m3 = Column(Float)
    Obv_percent = Column(Float)