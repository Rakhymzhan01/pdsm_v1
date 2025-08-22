from pydantic import BaseModel
from typing import Optional
from datetime import date

class WellBase(BaseModel):
    Well: Optional[str] = None
    X: Optional[str] = None
    Y: Optional[str] = None
    Lat: Optional[str] = None
    Lon: Optional[str] = None
    Object: Optional[str] = None
    Year: Optional[str] = None

class WellCreate(WellBase):
    pass

class Well(WellBase):
    class Config:
        from_attributes = True