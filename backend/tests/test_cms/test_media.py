import pytest
from io import BytesIO


@pytest.mark.asyncio
async def test_upload_image(client, auth_headers):
    resp = await client.post(
        "/api/v1/admin/media/upload",
        files={"file": ("test.png", BytesIO(b"fake-png-data"), "image/png")},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["filename"] == "test.png"
    assert data["mime_type"] == "image/png"
    assert "id" in data
    assert "url" in data


@pytest.mark.asyncio
async def test_upload_requires_auth(client):
    resp = await client.post(
        "/api/v1/admin/media/upload",
        files={"file": ("test.png", BytesIO(b"fake"), "image/png")},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_media(client, auth_headers):
    # Upload one first
    await client.post(
        "/api/v1/admin/media/upload",
        files={"file": ("test.png", BytesIO(b"data"), "image/png")},
        headers=auth_headers,
    )
    resp = await client.get("/api/v1/admin/media", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_delete_media(client, auth_headers):
    upload_resp = await client.post(
        "/api/v1/admin/media/upload",
        files={"file": ("test.png", BytesIO(b"data"), "image/png")},
        headers=auth_headers,
    )
    media_id = upload_resp.json()["id"]

    resp = await client.delete(
        f"/api/v1/admin/media/{media_id}", headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True
