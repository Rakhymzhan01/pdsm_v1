from sqlalchemy import Column, Integer, String
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(10), unique=True, nullable=False, index=True)
    password = Column(String(60), nullable=False)
    user_level = Column(String(60), nullable=False)