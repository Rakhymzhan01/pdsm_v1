from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.production import Production
from typing import List

async def get_production_data(db: AsyncSession, limit: int = 1000) -> List[Production]:
    query = text('''
        SELECT * FROM prod
        ORDER BY "Date" ASC
        LIMIT :limit
    ''')
    result = await db.execute(query, {"limit": limit})
    return result.fetchall()