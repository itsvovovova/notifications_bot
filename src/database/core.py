from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from logging import getLogger
from src.config import get_settings
from src.database.models import Base

logger = getLogger(__name__)
database_url = get_settings().database_url

sync_engine = create_engine(database_url.replace("asyncpg", "psycopg2"), echo=True)

if not database_exists(sync_engine.url):
    create_database(sync_engine.url)
    logger.info("Database did not exist - created new one")
else:
    logger.info("Database already exists")

async_engine = create_async_engine(database_url, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)