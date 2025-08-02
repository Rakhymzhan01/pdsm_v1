from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    wells, production, geological, well_logs, auth
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(wells.router, prefix="/karatobe", tags=["wells"])
api_router.include_router(production.router, prefix="/karatobe", tags=["production"])
api_router.include_router(geological.router, prefix="/karatobe", tags=["geological"])
api_router.include_router(well_logs.router, prefix="/karatobe", tags=["well-logs"])