# deps.py
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal
from typing import AsyncGenerator

# Dependency to get a DB session (asynchronous)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db
