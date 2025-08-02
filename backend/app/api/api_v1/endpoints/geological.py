from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import pandas as pd
import os

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.geological import PVT, Tops, FaultData, BoundaryData, GanttData
from app.schemas.user import UserInToken

router = APIRouter()

@router.get("/pvt", response_model=List[PVT])
async def read_pvt_data(
    db: AsyncSession = Depends(get_db),
    current_user: UserInToken = Depends(get_current_user)
):
    """Get PVT data"""
    try:
        from sqlalchemy import text
        result = await db.execute(text("SELECT * FROM pvt"))
        pvt_data = result.fetchall()
        
        return [
            {
                "id": row.id,
                "pressure": row.pressure,
                "rs": row.rs,
                "bo": row.bo,
                "mu_o": row.mu_o,
                "rho_o": row.rho_o
            }
            for row in pvt_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tops", response_model=List[Tops])
async def read_tops_data(
    db: AsyncSession = Depends(get_db),
    current_user: UserInToken = Depends(get_current_user)
):
    """Get tops data"""
    try:
        from sqlalchemy import text
        result = await db.execute(text("SELECT * FROM tops"))
        tops_data = result.fetchall()
        
        return [
            {
                "id": row.id,
                "well_name": row.well_name,
                "formation": row.formation,
                "top_depth": row.top_depth,
                "bottom_depth": row.bottom_depth
            }
            for row in tops_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/faults", response_model=List[Dict[str, Any]])
async def read_faults_data(
    current_user: UserInToken = Depends(get_current_user)
):
    """Get faults data from CSV"""
    try:
        # Get the path relative to the project root
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        filepath = os.path.join(current_dir, 'assets', 'karatobe', 'Faults.csv')
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Faults data file not found")
        
        df_faults = pd.read_csv(filepath)
        return df_faults.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/boundaries", response_model=List[Dict[str, Any]])
async def read_boundaries_data(
    current_user: UserInToken = Depends(get_current_user)
):
    """Get boundaries data from CSV"""
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        filepath = os.path.join(current_dir, 'assets', 'karatobe', 'Gornyi_Otvod.csv')
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Boundaries data file not found")
        
        df_boundaries = pd.read_csv(filepath, skiprows=[1])
        return df_boundaries.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gantt", response_model=List[Dict[str, Any]])
async def read_gantt_data(
    current_user: UserInToken = Depends(get_current_user)
):
    """Get Gantt chart data from CSV"""
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        filepath = os.path.join(current_dir, 'assets', 'karatobe', 'gantt.csv')
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Gantt data file not found")
        
        df_gantt = pd.read_csv(filepath)
        return df_gantt.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relative_permeability_table", response_model=List[Dict[str, Any]])
async def read_relative_permeability_table(
    current_user: UserInToken = Depends(get_current_user)
):
    """Get relative permeability table data"""
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        filepath = os.path.join(current_dir, 'assets', 'karatobe', 'relative_permeability_table.csv')
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Relative permeability table not found")
        
        df_rp_table = pd.read_csv(filepath)
        return df_rp_table.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relative_permeability_summary", response_model=List[Dict[str, Any]])
async def read_relative_permeability_summary(
    current_user: UserInToken = Depends(get_current_user)
):
    """Get relative permeability summary data"""
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        filepath = os.path.join(current_dir, 'assets', 'karatobe', 'relative_permeability_summary.csv')
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Relative permeability summary not found")
        
        df_rp_summary = pd.read_csv(filepath)
        return df_rp_summary.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))