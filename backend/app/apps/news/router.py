from fastapi import APIRouter, Depends, HTTPException

from app.apps.auth.router import get_current_user
from app.apps.news.schemas import NewsCreate, NewsResponse, NewsUpdate
from app.apps.news.service import (
    create_article,
    delete_article,
    get_article_by_id,
    list_all_articles,
    list_published_articles,
    update_article,
)

public_router = APIRouter(prefix="/api/v1", tags=["news"])

admin_router = APIRouter(
    prefix="/api/v1/admin/news",
    tags=["admin-news"],
    dependencies=[Depends(get_current_user)],
)


@public_router.get("/news", response_model=dict)
async def get_news(page: int = 1, size: int = 10, category: str | None = None):
    articles, total = await list_published_articles(page, size, category)
    return {
        "items": [NewsResponse.model_validate(a) for a in articles],
        "total": total,
        "page": page,
        "size": size,
    }


@public_router.get("/news/{article_id}", response_model=NewsResponse)
async def get_article(article_id: int):
    article = await get_article_by_id(article_id)
    if not article or not article.is_published:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@admin_router.get("", response_model=dict)
async def admin_list_articles(page: int = 1, size: int = 10, category: str | None = None):
    articles, total = await list_all_articles(page, size, category)
    return {
        "items": [NewsResponse.model_validate(a) for a in articles],
        "total": total,
        "page": page,
        "size": size,
    }


@admin_router.post("", response_model=NewsResponse, status_code=201)
async def admin_create_article(data: NewsCreate):
    article = await create_article(**data.model_dump())
    return article


@admin_router.put("/{article_id}", response_model=NewsResponse)
async def admin_update_article(article_id: int, data: NewsUpdate):
    article = await update_article(article_id, **data.model_dump(exclude_none=True))
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@admin_router.delete("/{article_id}")
async def admin_delete_article(article_id: int):
    deleted = await delete_article(article_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"deleted": True}
