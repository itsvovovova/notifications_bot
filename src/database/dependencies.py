from src.database.core import AsyncSessionLocal

async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session