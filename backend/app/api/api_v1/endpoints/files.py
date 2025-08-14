from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
import shutil
import tempfile
import pandas as pd
import lasio
from typing import List
import zipfile
import io

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserInToken
from app.core.logging import logger
from app.core.exceptions import ValidationError, NotFoundError

router = APIRouter()

# Configure upload settings
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'.las', '.csv', '.xlsx', '.txt'}
UPLOAD_DIR = "uploads"

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

def validate_file_extension(filename: str) -> bool:
    """Validate file extension"""
    extension = os.path.splitext(filename.lower())[1]
    return extension in ALLOWED_EXTENSIONS

def validate_file_size(file_size: int) -> bool:
    """Validate file size"""
    return file_size <= MAX_FILE_SIZE

@router.post("/upload/las")
async def upload_las_file(
    well_name: str,
    file: UploadFile = File(...),
    current_user: UserInToken = Depends(get_current_user)
):
    """Upload a LAS file for a specific well"""
    try:
        # Validate file
        if not validate_file_extension(file.filename):
            raise ValidationError("Invalid file type. Only .las files are allowed.")
        
        if not validate_file_size(len(await file.read())):
            raise ValidationError("File too large. Maximum size is 50MB.")
        
        # Reset file pointer
        await file.seek(0)
        
        # Create well directory
        well_dir = os.path.join(UPLOAD_DIR, "las", well_name)
        os.makedirs(well_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(well_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate LAS file by trying to read it
        try:
            las = lasio.read(file_path)
            logger.info(f"LAS file uploaded successfully: {file_path}")
        except Exception as e:
            # Remove invalid file
            os.remove(file_path)
            raise ValidationError(f"Invalid LAS file format: {str(e)}")
        
        return {
            "message": "LAS file uploaded successfully",
            "filename": file.filename,
            "well_name": well_name,
            "file_path": file_path
        }
        
    except Exception as e:
        logger.error(f"Error uploading LAS file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/csv")
async def upload_csv_file(
    data_type: str,  # production, pvt, tops, etc.
    file: UploadFile = File(...),
    current_user: UserInToken = Depends(get_current_user)
):
    """Upload a CSV file"""
    try:
        # Validate file
        if not file.filename.lower().endswith('.csv'):
            raise ValidationError("Invalid file type. Only .csv files are allowed.")
        
        if not validate_file_size(len(await file.read())):
            raise ValidationError("File too large. Maximum size is 50MB.")
        
        # Reset file pointer
        await file.seek(0)
        
        # Create data type directory
        data_dir = os.path.join(UPLOAD_DIR, "csv", data_type)
        os.makedirs(data_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(data_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate CSV by trying to read it
        try:
            df = pd.read_csv(file_path)
            row_count = len(df)
            col_count = len(df.columns)
            logger.info(f"CSV file uploaded successfully: {file_path} ({row_count} rows, {col_count} columns)")
        except Exception as e:
            # Remove invalid file
            os.remove(file_path)
            raise ValidationError(f"Invalid CSV file format: {str(e)}")
        
        return {
            "message": "CSV file uploaded successfully",
            "filename": file.filename,
            "data_type": data_type,
            "file_path": file_path,
            "rows": row_count,
            "columns": col_count
        }
        
    except Exception as e:
        logger.error(f"Error uploading CSV file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/las/{well_name}/{filename}")
async def download_las_file(
    well_name: str,
    filename: str,
    current_user: UserInToken = Depends(get_current_user)
):
    """Download a LAS file"""
    try:
        file_path = os.path.join(UPLOAD_DIR, "las", well_name, filename)
        
        if not os.path.exists(file_path):
            raise NotFoundError(f"LAS file not found: {filename}")
        
        logger.info(f"LAS file downloaded: {file_path}")
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Error downloading LAS file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/csv/{data_type}/{filename}")
async def download_csv_file(
    data_type: str,
    filename: str,
    current_user: UserInToken = Depends(get_current_user)
):
    """Download a CSV file"""
    try:
        file_path = os.path.join(UPLOAD_DIR, "csv", data_type, filename)
        
        if not os.path.exists(file_path):
            raise NotFoundError(f"CSV file not found: {filename}")
        
        logger.info(f"CSV file downloaded: {file_path}")
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='text/csv'
        )
        
    except Exception as e:
        logger.error(f"Error downloading CSV file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/well_data/{well_name}")
async def export_well_data(
    well_name: str,
    current_user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export all data for a specific well as ZIP archive"""
    try:
        # Create a temporary ZIP file
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add LAS files if they exist
            las_dir = os.path.join(UPLOAD_DIR, "las", well_name)
            if os.path.exists(las_dir):
                for filename in os.listdir(las_dir):
                    file_path = os.path.join(las_dir, filename)
                    zip_file.write(file_path, f"las/{filename}")
            
            # Add well data from database as CSV
            from sqlalchemy import text
            
            # Well information
            well_query = text("SELECT * FROM wells WHERE well_name = :well_name")
            result = await db.execute(well_query, {"well_name": well_name})
            well_data = result.fetchall()
            
            if well_data:
                well_df = pd.DataFrame([dict(row._mapping) for row in well_data])
                csv_buffer = well_df.to_csv(index=False)
                zip_file.writestr(f"{well_name}_well_info.csv", csv_buffer)
            
            # Production data
            prod_query = text('SELECT * FROM prod WHERE well = :well_name')
            result = await db.execute(prod_query, {"well_name": well_name})
            prod_data = result.fetchall()
            
            if prod_data:
                prod_df = pd.DataFrame([dict(row._mapping) for row in prod_data])
                csv_buffer = prod_df.to_csv(index=False)
                zip_file.writestr(f"{well_name}_production.csv", csv_buffer)
            
            # Tops data
            tops_query = text("SELECT * FROM tops WHERE well_name = :well_name")
            result = await db.execute(tops_query, {"well_name": well_name})
            tops_data = result.fetchall()
            
            if tops_data:
                tops_df = pd.DataFrame([dict(row._mapping) for row in tops_data])
                csv_buffer = tops_df.to_csv(index=False)
                zip_file.writestr(f"{well_name}_tops.csv", csv_buffer)
        
        zip_buffer.seek(0)
        
        logger.info(f"Well data exported for: {well_name}")
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={well_name}_data.zip"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting well data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/list")
async def list_uploaded_files(
    current_user: UserInToken = Depends(get_current_user)
):
    """List all uploaded files"""
    try:
        files = {"las": {}, "csv": {}}
        
        # List LAS files
        las_base_dir = os.path.join(UPLOAD_DIR, "las")
        if os.path.exists(las_base_dir):
            for well_name in os.listdir(las_base_dir):
                well_path = os.path.join(las_base_dir, well_name)
                if os.path.isdir(well_path):
                    files["las"][well_name] = os.listdir(well_path)
        
        # List CSV files
        csv_base_dir = os.path.join(UPLOAD_DIR, "csv")
        if os.path.exists(csv_base_dir):
            for data_type in os.listdir(csv_base_dir):
                data_path = os.path.join(csv_base_dir, data_type)
                if os.path.isdir(data_path):
                    files["csv"][data_type] = os.listdir(data_path)
        
        return files
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))