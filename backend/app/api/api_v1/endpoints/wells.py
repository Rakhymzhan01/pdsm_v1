from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.crud.well import get_wells
from app.schemas.well import Well
from app.schemas.user import UserInToken

router = APIRouter()

@router.get("/wells", response_model=List[Well])
async def read_wells(
    db: AsyncSession = Depends(get_db)
):
    """Get all wells data"""
    try:
        wells = await get_wells(db)
        return wells
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))