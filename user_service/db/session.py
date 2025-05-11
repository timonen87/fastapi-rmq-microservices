from uuid import UUID

from core.config import settings
from sqlalchemy import create_engine, func, select
from sqlalchemy.ext import declarative
from sqlalchemy.orm import sessionmaker

engine = create_engine(str(settings.DATABASE_URI))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative.declarative_base()

def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

