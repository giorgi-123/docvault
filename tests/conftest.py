import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from docvault.main import app
from docvault.database import Base, get_db
from docvault.config import settings


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """
    Creates all tables before each test, drops them after.
    Yields a session for the test to use.
    """
    # Creating engine inside fixture (withing the test's event loop)
    test_engine = create_async_engine(settings.test_database_url, echo=False)
    test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Create session
    async with test_session_factory() as session:
        yield session
        await session.rollback()
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # clean up engine
    await test_engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    """
    HTTP Client that uses test database.
    """
    async def get_test_db():
        yield test_db
    
    app.dependency_overrides[get_db] = get_test_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function")
async def register_user(client):
    """
    Creates a test user and returns their data.
    """
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
    }
    await client.post("/auth/register", json=user_data)
    return user_data


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client, register_user):
    """
    Logs in the test user and returns authorization headers.
    """
    login_request = await client.post("/auth/login", json=register_user)
    response_data = login_request.json()
    token = response_data["access_token"]
    return {"Authorization": f"Bearer {token}"}
