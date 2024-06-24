# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
import enum

class UserType(enum.Enum):
    admin = "admin"
    regular = "regular"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    user_type: UserType = UserType.regular
    keep_logged_in: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str
