from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/speedometer.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def ensure_schema():
    if not DATABASE_URL.startswith("sqlite"):
        return

    with engine.begin() as connection:
        existing_trip_columns = {
            row[1] for row in connection.exec_driver_sql("PRAGMA table_info(trips)").fetchall()
        }
        if "start_address" not in existing_trip_columns:
            connection.exec_driver_sql("ALTER TABLE trips ADD COLUMN start_address VARCHAR")
        if "end_address" not in existing_trip_columns:
            connection.exec_driver_sql("ALTER TABLE trips ADD COLUMN end_address VARCHAR")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
