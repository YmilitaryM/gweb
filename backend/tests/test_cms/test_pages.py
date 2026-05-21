import pytest


@pytest.mark.asyncio
async def test_create_page(client, auth_headers):
    resp = await client.post("/api/v1/admin/pages", json={
        "name_zh": "首页", "name_en": "Home", "slug": "home"
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["slug"] == "home"


@pytest.mark.asyncio
async def test_get_page_by_slug_public(client):
    from app.apps.cms.service_page import create_page
    await create_page(name_zh="首页", name_en="Home", slug="home", is_published=True)

    resp = await client.get("/api/v1/pages/home")
    assert resp.status_code == 200
    assert resp.json()["slug"] == "home"


@pytest.mark.asyncio
async def test_create_page_duplicate_slug(client, auth_headers):
    from app.apps.cms.service_page import create_page
    await create_page(name_zh="首页", name_en="Home", slug="home")

    resp = await client.post("/api/v1/admin/pages", json={
        "name_zh": "重复", "name_en": "Dup", "slug": "home"
    }, headers=auth_headers)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_nonexistent_page(client):
    resp = await client.get("/api/v1/pages/nonexistent")
    assert resp.status_code == 404
