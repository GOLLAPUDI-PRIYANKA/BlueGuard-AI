from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from geoalchemy2 import Geography
from app.core.config import get_settings


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


settings = get_settings()

engine = create_engine(settings.DATABASE_URL, echo=settings.APP_DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
