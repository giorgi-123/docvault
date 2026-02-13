from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase


from docvault.config import settings

# Create async engine
engine = create_async_engine(settings.database_url, echo=True)

# Create session factory
async_session = async_sessionmaker(engine, expire_on_commit=False)


# Base class for all models
class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency that provides a database session"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise 
