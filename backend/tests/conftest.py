import os
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Override database URL to use SQLite for testing before any app imports
os.environ["GWEB_DATABASE_URL"] = "sqlite+aiosqlite:///file::memory:?cache=shared&uri=true"

from app.main import app
from app.core.database import engine
from app.shared.models import Base


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
