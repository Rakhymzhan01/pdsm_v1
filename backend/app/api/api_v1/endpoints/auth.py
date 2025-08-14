from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.crud.app_user import (
    authenticate_user, create_user, get_projects, 
    get_pending_users, approve_user, reject_user,
    get_user_by_username, get_user_by_email
)
from app.schemas.app_user import (
    UserLogin, UserRegister, LoginResponse, Project, 
    AppUserWithProject, UserApproval
)

router = APIRouter()

@router.post("/login_nextjs", response_model=LoginResponse)
async def login_from_nextjs(
    user_login: UserLogin, 
    db: AsyncSession = Depends(get_db)
):
    """Login endpoint for Next.js frontend"""
    
    print(f"Login attempt: {user_login.username}")
    
    try:
        user = await authenticate_user(db, user_login.username, user_login.password)
        
        if not user:
            print(f"Login failed: {user_login.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials or account not approved"
            )
        
        print(f"Login successful: {user.username}")
        
        # Generate JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, 
            expires_delta=access_token_expires
        )
        
        return {
            "message": "Login successful",
            "user": {
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "project": user.project.name if user.project else None
            },
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )

@router.post("/register", response_model=dict)
async def register_user(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register new user"""
    
    # Check if username exists
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists
    existing_email = await get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create user
    user = await create_user(db, user_data)
    
    return {
        "message": "Registration successful. Please wait for admin approval.",
        "username": user.username,
        "status": user.status
    }

@router.get("/projects", response_model=List[Project])
async def get_available_projects(db: AsyncSession = Depends(get_db)):
    """Get list of available projects"""
    return await get_projects(db)

@router.get("/pending-users", response_model=List[AppUserWithProject])
async def get_pending_approvals(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get pending user approvals (master users only)"""
    
    # Check if current user is master
    user = await get_user_by_username(db, current_user["username"])
    if not user or user.role != 'master':
        raise HTTPException(status_code=403, detail="Access denied. Master role required.")
    
    return await get_pending_users(db)

@router.post("/approve-user", response_model=dict)
async def approve_user_request(
    approval: UserApproval,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve or reject user registration (master users only)"""
    
    # Check if current user is master
    user = await get_user_by_username(db, current_user["username"])
    if not user or user.role != 'master':
        raise HTTPException(status_code=403, detail="Access denied. Master role required.")
    
    if approval.action == 'approve':
        updated_user = await approve_user(db, approval.user_id, user.id)
        if updated_user:
            return {"message": f"User {updated_user.username} approved successfully"}
    elif approval.action == 'reject':
        updated_user = await reject_user(db, approval.user_id, user.id)
        if updated_user:
            return {"message": f"User {updated_user.username} rejected"}
    
    raise HTTPException(status_code=400, detail="Invalid action or user not found")