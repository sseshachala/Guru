from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from models import Base
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
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()