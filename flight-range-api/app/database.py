"""
Database engine and session configuration.

Uses SQLite by default (zero setup, good for a demo/portfolio project),
but the connection string is read from an environment variable so the
same code works against PostgreSQL in a real deployment
(e.g. DATABASE_URL=postgresql://user:pass@host:5432/dbname).
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./flight_range.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
