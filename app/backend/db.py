import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

username = os.environ.get("DB_USERNAME")
password = os.environ.get("DB_PASSWORD")
db_name = os.environ.get("DB_NAME")
db_url = f"postgresql+asyncpg://{username}:{password}@localhost:5432/{db_name}"


engine = create_async_engine(db_url, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass
