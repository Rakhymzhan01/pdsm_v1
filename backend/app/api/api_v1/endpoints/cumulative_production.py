from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.core.database import get_db
from app.crud.cumulative_production import get_cumulative_production_by_well

router = APIRouter()

@router.get("/cumulative-production", response_model=List[Dict[str, Any]])
async def read_cumulative_production_data(
    db: AsyncSession = Depends(get_db)
):
    """Get cumulative production data by well with geographic coordinates"""
    try:
        cumulative_data = await get_cumulative_production_by_well(db)
        
        if not cumulative_data:
            return []
        
        return cumulative_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching cumulative production data: {str(e)}"
        )