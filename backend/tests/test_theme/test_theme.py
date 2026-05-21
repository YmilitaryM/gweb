import pytest


@pytest.mark.asyncio
async def test_get_active_theme_public(client):
    from app.apps.theme.service import create_theme

    await create_theme(
        name="默认主题",
        slug="default",
        variables={"primary_color": "#1890ff"},
        tech_effects={},
        is_active=True,
    )
    await create_theme(
        name="备用主题",
        slug="alt",
        variables={"primary_color": "#52c41a"},
        tech_effects={},
        is_active=False,
    )

    resp = await client.get("/api/v1/themes/active")
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == "default"
    assert data["variables"]["primary_color"] == "#1890ff"


@pytest.mark.asyncio
async def test_get_active_theme_none(client):
    resp = await client.get("/api/v1/themes/active")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_activate_theme(client, auth_headers):
    from app.apps.theme.service import create_theme

    theme_a = await create_theme(
        name="主题A",
        slug="theme-a",
        variables={},
        tech_effects={},
        is_active=True,
    )
    theme_b = await create_theme(
        name="主题B",
        slug="theme-b",
        variables={},
        tech_effects={},
        is_active=False,
    )

    # Activate theme B
    resp = await client.put(
        f"/api/v1/admin/themes/{theme_b.id}/activate", headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["slug"] == "theme-b"
    assert resp.json()["is_active"] is True

    # Verify theme A is now inactive
    resp = await client.get("/api/v1/themes/active")
    assert resp.status_code == 200
    assert resp.json()["slug"] == "theme-b"
