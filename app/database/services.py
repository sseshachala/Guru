from sqlalchemy.orm import Session
from .models import User, Session as UserSession,  Embedding, Index
from .schemas import UserCreate, UserLogin, PasswordReset, PasswordResetRequest, EmbeddingCreate, IndexCreate
from passlib.context import CryptContext
from passlib.hash import argon2
import secrets
from fastapi import HTTPException, status


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return argon2.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return argon2.verify(plain_password, hashed_password)

def create_user(db: Session, user: UserCreate) -> User:
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password=hashed_password,
        keep_logged_in=user.keep_logged_in,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, user: UserLogin) -> dict:
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = secrets.token_hex(16)
    session = UserSession(token=token, user_id=db_user.id)
    db.add(session)
    db.commit()
    return {"token": token}

def reset_password_request(db: Session, request: PasswordResetRequest) -> dict:
    db_user = db.query(User).filter(User.email == request.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Email not registered")
    # Here you would send an email with a reset link/token
    return {"message": "Password reset link sent"}

def reset_password(db: Session, reset: PasswordReset) -> dict:
    db_user = db.query(User).filter(User.email == reset.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email")
    db_user.password = get_password_hash(reset.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

def delete_user(db: Session, email: str, token: str) -> dict:
    session = db.query(UserSession).filter(UserSession.token == token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    user = db.query(User).filter(User.id == session.user_id).first()
    
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

def logout_user(db: Session, token: str) -> dict:
    session = db.query(UserSession).filter(UserSession.token == token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    db.delete(session)
    db.commit()
    return {"message": "Logged out successfully"}

def create_embedding(db: Session, embedding: EmbeddingCreate) -> Embedding:
    db_embedding = Embedding(
        user_id=embedding.user_id,
        file_path=embedding.file_path,
        version=embedding.version,
        chunk_index=embedding.chunk_index,
        paragraph=embedding.paragraph,
        embedding=embedding.embedding
    )
    db.add(db_embedding)
    db.commit()
    db.refresh(db_embedding)
    return db_embedding

def create_index(db: Session, index: IndexCreate) -> Index:
    db_index = Index(
        user_id=index.user_id,
        file_path=index.file_path,
        version=index.version,
        chunk_index=index.chunk_index,
        paragraph=index.paragraph,
        text_chunk=index.text_chunk
    )
    db.add(db_index)
    db.commit()
    db.refresh(db_index)
    return db_index
