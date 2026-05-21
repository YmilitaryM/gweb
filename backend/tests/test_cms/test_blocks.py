import pytest


@pytest.mark.asyncio
async def test_add_block_to_page(client, auth_headers):
    from app.apps.cms.service_page import create_page
    page = await create_page(name_zh="首页", name_en="Home", slug="home")

    resp = await client.post(f"/api/v1/admin/pages/{page.id}/blocks", json={
        "type": "hero",
        "config": {"background": "dark", "padding": "lg"},
        "content": {
            "title_zh": "智驭建筑", "title_en": "Smart Building",
            "subtitle_zh": "副标题", "subtitle_en": "Subtitle",
            "buttons": []
        }
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["type"] == "hero"
    assert data["order"] == 0


@pytest.mark.asyncio
async def test_reorder_blocks(client, auth_headers):
    from app.apps.cms.service_page import create_page
    from app.apps.cms.service_block import create_block
    page = await create_page(name_zh="首页", name_en="Home", slug="home", is_published=True)
    b1 = await create_block(page.id, "hero", {"background": "dark"}, {"title_zh": "A", "title_en": "B"})
    b2 = await create_block(page.id, "richtext", {}, {"html_content_zh": "B", "html_content_en": "C"})

    resp = await client.put("/api/v1/admin/blocks/reorder", json={
        "page_id": page.id, "block_ids": [b2.id, b1.id]
    }, headers=auth_headers)
    assert resp.status_code == 200
    page_resp = await client.get("/api/v1/pages/home")
    blocks = page_resp.json()["blocks"]
    assert blocks[0]["id"] == b2.id
    assert blocks[1]["id"] == b1.id


@pytest.mark.asyncio
async def test_block_content_validation(client, auth_headers):
    from app.apps.cms.service_page import create_page
    page = await create_page(name_zh="首页", name_en="Home", slug="home")

    # hero block without required title_zh should fail
    resp = await client.post(f"/api/v1/admin/pages/{page.id}/blocks", json={
        "type": "hero",
        "config": {},
        "content": {"title_en": "Missing zh title"}
    }, headers=auth_headers)
    assert resp.status_code == 422
