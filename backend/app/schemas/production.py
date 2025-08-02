from pydantic import BaseModel
from typing import Optional
from datetime import date

class ProductionBase(BaseModel):
    Date: Optional[date] = None
    well: Optional[str] = None
    Qo_ton: Optional[float] = None
    Qw_m3: Optional[float] = None
    Ql_m3: Optional[float] = None
    Obv_percent: Optional[float] = None

class ProductionCreate(ProductionBase):
    pass

class Production(ProductionBase):
    id: int
    
    class Config:
        from_attributes = True