
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from sqlalchemy.ext import declarative
from uuid import UUID
from core.config import settings

engine = create_engine(str(settings.ASYNC_DATABASE_URI))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative.declarative_base()

# engine = create_async_engine(
#     str(settings.ASYNC_DATABASE_URI),
#     echo=False,
# )

# SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()