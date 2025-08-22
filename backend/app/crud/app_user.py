from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.app_user import AppUser, Project
from app.schemas.app_user import UserRegister
from passlib.context import CryptContext
from typing import Optional, List
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[AppUser]:
    result = await db.execute(
        select(AppUser)
        .options(selectinload(AppUser.project))
        .where(AppUser.username == username)
    )
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[AppUser]:
    result = await db.execute(select(AppUser).where(AppUser.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserRegister) -> AppUser:
    hashed_password = pwd_context.hash(user.password)
    
    db_user = AppUser(
        username=user.username,
        email=user.email,
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        project_id=user.project_id,
        role='user',
        status='pending'
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[AppUser]:
    user = await get_user_by_username(db, username)
    if not user:
        return None
    
    # Check if user is approved
    if user.status != 'approved':
        return None
    
    # Verify password
    if not pwd_context.verify(password, user.password):
        return None
    
    return user

async def get_projects(db: AsyncSession) -> List[Project]:
    result = await db.execute(select(Project))
    return result.scalars().all()

async def get_pending_users(db: AsyncSession) -> List[AppUser]:
    result = await db.execute(
        select(AppUser)
        .options(selectinload(AppUser.project))
        .where(AppUser.status == 'pending')
        .order_by(AppUser.created_at)
    )
    return result.scalars().all()

async def approve_user(db: AsyncSession, user_id: int, approver_id: int) -> Optional[AppUser]:
    result = await db.execute(select(AppUser).where(AppUser.id == user_id))
    user = result.scalar_one_or_none()
    
    if user and user.status == 'pending':
        user.status = 'approved'
        user.approved_at = datetime.utcnow()
        user.approved_by = approver_id
        await db.commit()
        await db.refresh(user)
        return user
    
    return None

async def reject_user(db: AsyncSession, user_id: int, approver_id: int) -> Optional[AppUser]:
    result = await db.execute(select(AppUser).where(AppUser.id == user_id))
    user = result.scalar_one_or_none()
    
    if user and user.status == 'pending':
        user.status = 'rejected'
        user.approved_by = approver_id
        await db.commit()
        await db.refresh(user)
        return user
    
    return None