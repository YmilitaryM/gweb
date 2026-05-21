import pytest


@pytest.mark.asyncio
async def test_create_article(client, auth_headers):
    resp = await client.post(
        "/api/v1/admin/news",
        json={
            "title_zh": "测试新闻",
            "title_en": "Test News",
            "summary_zh": "摘要",
            "summary_en": "Summary",
            "content_zh": "内容",
            "content_en": "Content",
            "category": "company_news",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title_zh"] == "测试新闻"
    assert data["title_en"] == "Test News"
    assert data["category"] == "company_news"


@pytest.mark.asyncio
async def test_list_news_public(client):
    from app.apps.news.service import create_article

    await create_article(
        title_zh="已发布",
        title_en="Published",
        is_published=True,
    )
    await create_article(
        title_zh="未发布",
        title_en="Unpublished",
        is_published=False,
    )

    resp = await client.get("/api/v1/news")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title_zh"] == "已发布"


@pytest.mark.asyncio
async def test_get_article_by_id(client):
    from app.apps.news.service import create_article

    article = await create_article(
        title_zh="文章",
        title_en="Article",
        is_published=True,
    )

    resp = await client.get(f"/api/v1/news/{article.id}")
    assert resp.status_code == 200
    assert resp.json()["title_zh"] == "文章"


@pytest.mark.asyncio
async def test_get_unpublished_article_returns_404(client):
    from app.apps.news.service import create_article

    article = await create_article(
        title_zh="草稿",
        title_en="Draft",
        is_published=False,
    )

    resp = await client.get(f"/api/v1/news/{article.id}")
    assert resp.status_code == 404
