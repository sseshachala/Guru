from pydantic import BaseModel, EmailStr
from typing import Optional
import enum


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    keep_logged_in: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str

class UserBase(BaseModel):
    id: int
    email: EmailStr
    creation_date: Optional[str] = None  # Assuming ISO 8601 format for datetime
    keep_logged_in: bool

    class Config:
        orm_mode = True

class SessionCreate(BaseModel):
    token: str
    user_id: int

class SessionResponse(BaseModel):
    token: str
    user: UserBase
    creation_date: Optional[str] = None  # Assuming ISO 8601 format for datetime

    class Config:
        orm_mode = True

class EmbeddingBase(BaseModel):
    user_id: int
    file_path: str
    version: int
    chunk_index: int
    paragraph: str
    embedding: list[float]  # Assuming embedding is a list of floats

    class Config:
        orm_mode = True

class EmbeddingCreate(EmbeddingBase):
    pass

class EmbeddingResponse(EmbeddingBase):
    id: int

class IndexBase(BaseModel):
    user_id: int
    file_path: str
    version: int
    chunk_index: int
    paragraph: str
    text_chunk: str

    class Config:
        orm_mode = True

class IndexCreate(IndexBase):
    pass

class IndexResponse(IndexBase):
    id: int
