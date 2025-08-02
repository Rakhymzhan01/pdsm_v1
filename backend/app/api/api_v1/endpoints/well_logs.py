from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import lasio
import os

from app.core.security import get_current_user
from app.schemas.user import UserInToken

router = APIRouter()

@router.get("/logs/{well_name}", response_model=List[Dict[str, Any]])
async def read_well_log_data(
    well_name: str,
    current_user: UserInToken = Depends(get_current_user)
):
    """Get well log data (LAS files) for a specific well"""
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        log_dir = os.path.join(current_dir, 'assets', 'karatobe', 'LOGs', well_name)
        
        if not os.path.exists(log_dir):
            raise HTTPException(status_code=404, detail=f"Log directory for well {well_name} not found")
        
        # Find the first LAS file in the directory
        log_file = None
        for f in os.listdir(log_dir):
            if f.lower().endswith('.las'):
                log_file = os.path.join(log_dir, f)
                break
        
        if not log_file:
            raise HTTPException(status_code=404, detail=f"No LAS file found for well {well_name}")

        las = lasio.read(log_file)
        df_log = las.df()
        df_log.reset_index(inplace=True)  # Make 'DEPT' a regular column

        # Convert datetime columns to string if any
        for col in df_log.columns:
            if pd.api.types.is_datetime64_any_dtype(df_log[col]):
                df_log[col] = df_log[col].dt.isoformat()

        # Replace NaN with None for JSON serialization
        df_log = df_log.replace({np.nan: None})
        return df_log.to_dict(orient="records")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/xpt_data/{well_name}", response_model=List[Dict[str, Any]])
async def read_xpt_data(
    well_name: str,
    current_user: UserInToken = Depends(get_current_user)
):
    """Get XPT data for a specific well"""
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        filepath = os.path.join(current_dir, 'assets', 'karatobe', 'XPTs', well_name, 'XPT.csv')
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail=f"XPT data for well {well_name} not found")
        
        df_xpt = pd.read_csv(filepath)
        return df_xpt.to_dict(orient="records")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))