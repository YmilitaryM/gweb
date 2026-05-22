import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_users_admin(client: AsyncClient, admin_auth_headers):
    resp = await client.get("/api/v1/admin/users", headers=admin_auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["username"] == "admin"


@pytest.mark.asyncio
async def test_list_users_editor_forbidden(client: AsyncClient, auth_headers):
    resp = await client.get("/api/v1/admin/users", headers=auth_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_users_unauthorized(client: AsyncClient):
    resp = await client.get("/api/v1/admin/users")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, admin_auth_headers):
    resp = await client.post(
        "/api/v1/admin/users",
        json={
            "username": "editor1",
            "password": "pass123",
            "role": "editor",
            "display_name": "Editor One",
            "email": "editor1@example.com",
        },
        headers=admin_auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "editor1"
    assert data["role"] == "editor"
    assert data["display_name"] == "Editor One"
    assert data["email"] == "editor1@example.com"
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_create_user_duplicate_username(client: AsyncClient, admin_auth_headers):
    await client.post(
        "/api/v1/admin/users",
        json={"username": "dup", "password": "pass123", "role": "editor"},
        headers=admin_auth_headers,
    )
    resp = await client.post(
        "/api/v1/admin/users",
        json={"username": "dup", "password": "pass456", "role": "editor"},
        headers=admin_auth_headers,
    )
    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, admin_auth_headers):
    from app.apps.auth.service import create_user

    user = await create_user("editme", "pass123", "editor")

    resp = await client.put(
        f"/api/v1/admin/users/{user.id}",
        json={"display_name": "Updated Name", "phone": "13800000000"},
        headers=admin_auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "Updated Name"
    assert data["phone"] == "13800000000"


@pytest.mark.asyncio
async def test_update_user_password(client: AsyncClient, admin_auth_headers):
    from app.apps.auth.service import create_user, authenticate

    user = await create_user("pwtest", "oldpass", "editor")

    resp = await client.put(
        f"/api/v1/admin/users/{user.id}",
        json={"password": "newpass"},
        headers=admin_auth_headers,
    )
    assert resp.status_code == 200

    token = await authenticate("pwtest", "newpass")
    assert token is not None
    token_old = await authenticate("pwtest", "oldpass")
    assert token_old is None


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, admin_auth_headers):
    from app.apps.auth.service import create_user

    user = await create_user("todelete", "pass123", "editor")

    resp = await client.delete(
        f"/api/v1/admin/users/{user.id}", headers=admin_auth_headers
    )
    assert resp.status_code == 200
    assert resp.json() == {"deleted": True}

    # Verify gone
    resp2 = await client.get("/api/v1/admin/users", headers=admin_auth_headers)
    ids = [u["id"] for u in resp2.json()]
    assert user.id not in ids


@pytest.mark.asyncio
async def test_cannot_delete_self(client: AsyncClient, admin_auth_headers):
    resp = await client.get("/api/v1/admin/auth/me", headers=admin_auth_headers)
    my_id = resp.json()["id"]

    resp = await client.delete(
        f"/api/v1/admin/users/{my_id}", headers=admin_auth_headers
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_delete_nonexistent_user(client: AsyncClient, admin_auth_headers):
    resp = await client.delete(
        "/api/v1/admin/users/99999", headers=admin_auth_headers
    )
    assert resp.status_code == 404
