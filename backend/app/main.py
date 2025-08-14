from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.exceptions import (
    PDMSException,
    pdms_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from app.core.logging import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## Petroleum Data Management System API
    
    Comprehensive API for managing petroleum data from the Karatobe oil field.
    
    ### Features:
    * **Authentication**: JWT-based authentication system
    * **Wells Management**: CRUD operations for well data
    * **Production Data**: Oil and gas production analytics
    * **Geological Data**: PVT, tops, faults, and boundaries
    * **Well Logs**: LAS file processing and well log data
    * **File Management**: Upload/download LAS files and CSV data
    * **Data Export**: Export well data in various formats
    
    ### Authentication:
    Use the `/auth/login_nextjs` endpoint to obtain a JWT token.
    Include the token in the Authorization header: `Bearer <token>`
    
    ### Data Types:
    * Wells: Well locations, completion data, status
    * Production: Daily oil/water production, water cut
    * Geological: PVT properties, formation tops, structural data
    * Well Logs: Depth-based log curves from LAS files
    
    ### File Formats Supported:
    * LAS: Well log data (Log ASCII Standard)
    * CSV: Production, geological, and other tabular data
    * ZIP: Bulk data export
    """,
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add exception handlers
app.add_exception_handler(PDMSException, pdms_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Petroleum Data Management System API",
        "version": "1.0.0",
        "docs_url": f"{settings.API_V1_STR}/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pdms-api"}