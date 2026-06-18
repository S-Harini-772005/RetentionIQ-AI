import os
from typing import Generator
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.engine import Engine

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/churn_analytics"
)

# Standard Synchronous Engine
engine: Engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False
)

# Synchronous SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    """Dependency Injection for FastAPI"""
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()