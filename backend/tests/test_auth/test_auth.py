import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    from app.apps.auth.service import create_user

    await create_user("admin", "password123")

    resp = await client.post(
        "/api/v1/admin/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    from app.apps.auth.service import create_user

    await create_user("admin", "password123")

    resp = await client.post(
        "/api/v1/admin/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_token(client: AsyncClient):
    resp = await client.get("/api/v1/admin/auth/me")
    assert resp.status_code == 401
