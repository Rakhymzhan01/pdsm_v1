from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    user_level: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInToken(BaseModel):
    username: str
    role: str