from sqlalchemy import select, func
from app.core.database import async_session
from app.apps.news.models import NewsArticle


async def create_article(**kwargs) -> NewsArticle:
    async with async_session() as db:
        article = NewsArticle(**kwargs)
        db.add(article)
        await db.commit()
        await db.refresh(article)
        return article


async def list_published_articles(
    page: int = 1, size: int = 10, category: str | None = None
) -> tuple[list[NewsArticle], int]:
    async with async_session() as db:
        query = select(NewsArticle).where(NewsArticle.is_published == True)
        count_query = select(func.count(NewsArticle.id)).where(
            NewsArticle.is_published == True
        )
        if category:
            query = query.where(NewsArticle.category == category)
            count_query = count_query.where(NewsArticle.category == category)
        result_total = await db.execute(count_query)
        total = result_total.scalar() or 0
        query = (
            query.order_by(NewsArticle.published_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await db.execute(query)
        return result.scalars().all(), total


async def list_all_articles(
    page: int = 1, size: int = 10, category: str | None = None
) -> tuple[list[NewsArticle], int]:
    async with async_session() as db:
        query = select(NewsArticle)
        count_query = select(func.count(NewsArticle.id))
        if category:
            query = query.where(NewsArticle.category == category)
            count_query = count_query.where(NewsArticle.category == category)
        result_total = await db.execute(count_query)
        total = result_total.scalar() or 0
        query = (
            query.order_by(NewsArticle.published_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await db.execute(query)
        return result.scalars().all(), total


async def get_article_by_id(article_id: int) -> NewsArticle | None:
    async with async_session() as db:
        return await db.get(NewsArticle, article_id)


async def update_article(article_id: int, **kwargs) -> NewsArticle | None:
    async with async_session() as db:
        article = await db.get(NewsArticle, article_id)
        if article:
            for k, v in kwargs.items():
                if v is not None:
                    setattr(article, k, v)
            await db.commit()
            await db.refresh(article)
        return article


async def delete_article(article_id: int) -> bool:
    async with async_session() as db:
        article = await db.get(NewsArticle, article_id)
        if article:
            await db.delete(article)
            await db.commit()
            return True
        return False
