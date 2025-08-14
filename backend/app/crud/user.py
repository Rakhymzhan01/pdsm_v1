from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from typing import Optional

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    import bcrypt
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db_user = User(
        username=user.username,
        password=hashed_password,
        user_level=user.user_level
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    import bcrypt
    from app.core.logging import logger
    
    try:
        logger.info(f"Authenticating user: {username}")
        
        user = await get_user_by_username(db, username)
        if not user:
            logger.warning(f"User not found: {username}")
            return None
        
        logger.info(f"User found: {username}, checking password")
        
        # Use Flask-Bcrypt verification for existing database users
        try:
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                logger.info(f"Password correct for user: {username}")
                return user
            else:
                logger.warning(f"Password incorrect for user: {username}")
        except Exception as e:
            logger.error(f"Password verification error for {username}: {str(e)}")
        
        return None
    except Exception as e:
        logger.error(f"Authentication error for {username}: {str(e)}", exc_info=True)
        return None