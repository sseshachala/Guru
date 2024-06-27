from sqlalchemy import Column, String, Integer, Enum, DateTime, Boolean, Text, ForeignKey, Sequence, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.postgresql import BYTEA

import numpy as np

Base = declarative_base()


class Vector(TypeDecorator):
    impl = BYTEA

    def process_bind_param(self, value, dialect):
        if value is not None:
            return np.array(value, dtype=np.float32).tobytes()
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return np.frombuffer(value, dtype=np.float32).tolist()
        return value

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    keep_logged_in = Column(Boolean, default=False)
    
    # Establish relationships
    sessions = relationship("Session", back_populates="user")
    embeddings = relationship("Embedding", back_populates="user")
    indices = relationship("Index", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"
    
    token = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Establish relationship
    user = relationship("User", back_populates="sessions")

class Embedding(Base):
    __tablename__ = "embeddings"
    
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_path = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    paragraph = Column(Text, nullable=False)
    embedding = Column(Vector, nullable=False)
    
    # Establish relationship
    user = relationship("User", back_populates="embeddings")

class Index(Base):
    __tablename__ = "indices"
    
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_path = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    paragraph = Column(Text, nullable=False)
    text_chunk = Column(Text, nullable=False)
    
    # Establish relationship
    user = relationship("User", back_populates="indices")
