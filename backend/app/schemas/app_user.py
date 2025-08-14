from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class Project(ProjectBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# User schemas
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    project_id: int

class UserLogin(BaseModel):
    username: str
    password: str

class AppUserBase(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = 'user'
    status: str = 'pending'

class AppUser(AppUserBase):
    id: int
    project_id: Optional[int] = None
    created_at: datetime
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AppUserWithProject(AppUser):
    project: Optional[Project] = None

class UserApproval(BaseModel):
    user_id: int
    action: str  # 'approve' or 'reject'

class LoginResponse(BaseModel):
    message: str
    user: dict
    access_token: str
    token_type: str