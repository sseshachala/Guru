from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os


# "postgresql://user:password@localhost/" + os.environ["PG_DBNAME"]
DATABASE_URL = (
    "postgresql://"
    + os.environ["PG_USER"]
    + ":"
    + os.environ["PG_PASSWORD"]
    + "@"
    + os.environ["PG_HOST"]
    + ":"
    + os.environ["PG_PORT"]
    + "/"
    + os.environ["PG_DBNAME"]
)

from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,       # The size of the pool to be maintained
    max_overflow=20,    # The maximum overflow size of the pool
    pool_timeout=30,    # The number of seconds to wait before giving up on getting a connection from the pool
    pool_recycle=1800   # The number of seconds a connection can persist
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()