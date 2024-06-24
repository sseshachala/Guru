# models.py
from sqlalchemy import Column, String, DateTime, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class UserType(enum.Enum):
    admin = "admin"
    regular = "regular"

class User(Base):
    __tablename__ = "users"
    
    email = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=False)
    user_type = Column(Enum(UserType), default=UserType.regular)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    keep_logged_in = Column(Boolean, default=False)

class Session(Base):
    __tablename__ = "sessions"
    
    token = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
