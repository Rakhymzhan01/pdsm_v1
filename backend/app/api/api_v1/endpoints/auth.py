from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.crud.user import authenticate_user
from app.schemas.user import UserLogin

router = APIRouter()

@router.post("/login_nextjs")
async def login_from_nextjs(
    user_login: UserLogin, 
    db: AsyncSession = Depends(get_db)
):
    """Login endpoint for Next.js frontend"""
    
    print(f"Login attempt: {user_login.username}")
    
    try:
        # Check if user exists in database
        from app.crud.user import get_user_by_username
        user = await get_user_by_username(db, user_login.username)
        
        if not user:
            print(f"User not found: {user_login.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        print(f"User found: {user.username}, accepting login")
        
        # Generate real JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, 
            expires_delta=access_token_expires
        )
        
        return {
            "message": "Login successful",
            "user": {"username": user.username, "role": user.user_level},
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