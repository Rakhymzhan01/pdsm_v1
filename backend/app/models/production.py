from sqlalchemy import Column, Integer, String, Float, Date
from app.core.database import Base

class Production(Base):
    __tablename__ = "prod"
    
    Date = Column("Date", Date, primary_key=True)
    Well = Column("Well", String, primary_key=True)
    Horizon = Column("Horizon", String)
    Pump = Column("Pump", Float)
    H_m = Column("H_m", Float)
    Ptr_atm = Column("Ptr_atm", Float)
    Pztr_atm = Column("Pztr_atm", Float)
    Time_hr = Column("Time_hr", Float)
    Ql_m3 = Column("Ql_m3", Float)
    Qo_m3 = Column("Qo_m3", Float)
    Qw_m3 = Column("Qw_m3", Float)
    Qo_ton = Column("Qo_ton", Float)
    Qi_m3 = Column("Qi_m3", Float)