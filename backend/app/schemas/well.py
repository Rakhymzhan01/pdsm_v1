from pydantic import BaseModel
from typing import Optional
from datetime import date

class WellBase(BaseModel):
    well_name: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    kb: Optional[float] = None
    td: Optional[float] = None
    completion_date: Optional[date] = None
    status: Optional[str] = None

class WellCreate(WellBase):
    pass

class Well(WellBase):
    id: int
    
    class Config:
        from_attributes = True