from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from ..config import get_settings

settings = get_settings()

# pool_pre_ping=True protects your app from database connection drops/restarts in Docker
engine = create_engine(
    settings.database_url, 
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modern SQLAlchemy 2.0 style declarative base class
class Base(DeclarativeBase):
    pass

# FastAPI dependency for managing database session lifecycles per request
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()