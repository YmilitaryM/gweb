import pytest


@pytest.mark.asyncio
async def test_create_menu_item(client, auth_headers):
    resp = await client.post(
        "/api/v1/admin/menus",
        json={
            "name_zh": "首页",
            "name_en": "Home",
            "link": "/",
            "location": "header",
            "order": 0,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name_zh"] == "首页"


@pytest.mark.asyncio
async def test_get_menu_public(client):
    from app.apps.cms.service_menu import create_menu_item

    await create_menu_item(
        name_zh="首页", name_en="Home", link="/", location="header", order=0
    )
    await create_menu_item(
        name_zh="关于", name_en="About", link="/about", location="header", order=1
    )

    resp = await client.get("/api/v1/menus?location=header")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2


@pytest.mark.asyncio
async def test_menu_tree_structure(client):
    from app.apps.cms.service_menu import create_menu_item

    parent = await create_menu_item(
        name_zh="关于", name_en="About", link="/about", location="header", order=0
    )
    child1 = await create_menu_item(
        name_zh="公司简介",
        name_en="Company",
        link="/about/company",
        location="header",
        order=0,
        parent_id=parent.id,
    )
    child2 = await create_menu_item(
        name_zh="发展历程",
        name_en="History",
        link="/about/history",
        location="header",
        order=1,
        parent_id=parent.id,
    )

    resp = await client.get("/api/v1/menus?location=header")
    items = resp.json()
    parent_node = next((i for i in items if i["name_zh"] == "关于"), None)
    assert parent_node is not None
    assert len(parent_node["children"]) == 2
