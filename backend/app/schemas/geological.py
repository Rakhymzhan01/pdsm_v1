from pydantic import BaseModel
from typing import Optional

class PVTBase(BaseModel):
    pressure: Optional[float] = None
    rs: Optional[float] = None
    bo: Optional[float] = None
    mu_o: Optional[float] = None
    rho_o: Optional[float] = None

class PVT(PVTBase):
    id: int
    
    class Config:
        from_attributes = True

class TopsBase(BaseModel):
    well_name: Optional[str] = None
    formation: Optional[str] = None
    top_depth: Optional[float] = None
    bottom_depth: Optional[float] = None

class Tops(TopsBase):
    id: int
    
    class Config:
        from_attributes = True

class FaultData(BaseModel):
    x: float
    y: float
    fault_type: Optional[str] = None

class BoundaryData(BaseModel):
    x: float
    y: float
    boundary_type: Optional[str] = None

class GanttData(BaseModel):
    task: str
    start_date: str
    end_date: str
    well: Optional[str] = None