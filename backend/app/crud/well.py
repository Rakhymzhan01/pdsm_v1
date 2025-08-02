from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.well import Well
from typing import List

async def get_wells(db: AsyncSession) -> List[Well]:
    result = await db.execute(select(Well))
    return result.scalars().all()