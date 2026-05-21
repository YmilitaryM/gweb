import pytest


@pytest.mark.asyncio
async def test_set_and_get_setting(client, auth_headers):
    await client.put("/api/v1/admin/settings/site_name", json={"value": "测试网站"}, headers=auth_headers)

    resp = await client.get("/api/v1/settings/public")
    assert resp.status_code == 200
    data = resp.json()
    assert data["site_name"] == "测试网站"


@pytest.mark.asyncio
async def test_setting_requires_auth(client):
    resp = await client.put("/api/v1/admin/settings/site_name", json={"value": "x"})
    assert resp.status_code == 401
