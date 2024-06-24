# add_sample_users.py
import os, json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.database.models import Base, User, UserType
from app.database.services import get_password_hash

with open(os.path.join(os.path.dirname(__file__), '..', '.env.json')) as f:
    env = json.load(f)

DATABASE_URL = (
    "postgresql://"
    + env["PG_USER"]
    + ":"
    + env["PG_PASSWORD"]
    + "@"
    + env["PG_HOST"]
    + ":"
    + str(env["PG_PORT"])  # or env["PG_PORT"]
    + "/"
    + env["PG_DBNAME"]
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def add_sample_users():
    db = SessionLocal()
    try:
        sample_users = [
            {
                "email": "admin@example.com",
                "password": get_password_hash("adminpass"),
                "user_type": UserType.admin,
            },
            {
                "email": "regular@example.com",
                "password": get_password_hash("regularpass"),
                "user_type": UserType.regular,
            },
        ]

        for user_data in sample_users:
            user = User(
                email=user_data["email"],
                password=user_data["password"],
                user_type=user_data["user_type"],
                keep_logged_in=False,  # or True, depending on your preference
            )
            db.add(user)
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_users()
    print("Sample users added successfully.")
