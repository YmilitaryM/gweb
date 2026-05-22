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


@pytest_asyncio.fixture
async def auth_headers(client):
    from app.apps.auth.service import create_user

    await create_user("admin", "password123")
    resp = await client.post(
        "/api/v1/admin/auth/login", json={"username": "admin", "password": "password123"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_auth_headers(client):
    from app.apps.auth.service import create_user

    await create_user("admin", "password123", "admin")
    resp = await client.post(
        "/api/v1/admin/auth/login", json={"username": "admin", "password": "password123"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
