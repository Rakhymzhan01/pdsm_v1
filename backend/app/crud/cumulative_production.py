from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any

async def get_cumulative_production_by_well(db: AsyncSession) -> List[Dict[str, Any]]:
    """Get cumulative production data by well with coordinates"""
    query = text('''
        SELECT 
            w."Well" as well_name,
            w."Lat" as latitude,
            w."Lon" as longitude,
            w."Object" as object_type,
            w."Year" as year,
            COALESCE(SUM(p."Qo_ton"), 0) as cumulative_oil,
            COALESCE(SUM(p."Qw_m3"), 0) as cumulative_water,
            COALESCE(SUM(p."Ql_m3"), 0) as cumulative_liquid,
            COUNT(p."Date") as production_days,
            COALESCE(AVG(p."Qo_ton"), 0) as avg_daily_oil
        FROM wells w
        LEFT JOIN prod p ON w."Well" = p."Well"
        WHERE w."Lat" IS NOT NULL 
        AND w."Lon" IS NOT NULL 
        AND w."Lat" != '' 
        AND w."Lon" != ''
        GROUP BY w."Well", w."Lat", w."Lon", w."Object", w."Year"
        ORDER BY cumulative_oil DESC
    ''')
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        {
            "well_name": row.well_name,
            "latitude": float(row.latitude) if row.latitude else 0,
            "longitude": float(row.longitude) if row.longitude else 0,
            "object_type": row.object_type or "Unknown",
            "horizon": row.year or "Unknown",  # Using year instead of horizon
            "cumulative_oil": float(row.cumulative_oil) if row.cumulative_oil else 0,
            "cumulative_water": float(row.cumulative_water) if row.cumulative_water else 0,
            "cumulative_liquid": float(row.cumulative_liquid) if row.cumulative_liquid else 0,
            "production_days": int(row.production_days) if row.production_days else 0,
            "avg_daily_oil": float(row.avg_daily_oil) if row.avg_daily_oil else 0
        }
        for row in rows
    ]