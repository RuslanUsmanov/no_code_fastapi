from os import environ

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DB_USER = environ.get("POSTGRES_USER")
DB_PASSWORD = environ.get("POSTGRES_PASSWORD")
DB_HOST = environ.get("POSTGRES_HOST")
DB_NAME = environ.get("POSTGRES_DB")
DB_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
)

engine = create_engine(DB_URL)
engine_async = create_async_engine(DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SessionLocalAsync = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_async, class_=AsyncSession
)


async def get_db_async():
    async with SessionLocalAsync() as session:
        yield session
