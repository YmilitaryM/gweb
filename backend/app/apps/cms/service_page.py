from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import async_session
from app.apps.cms.models import Page


async def create_page(name_zh: str, name_en: str, slug: str, type: str = "content", sort_order: int = 0, is_published: bool = False) -> Page:
    async with async_session() as db:
        page = Page(name_zh=name_zh, name_en=name_en, slug=slug, type=type, sort_order=sort_order, is_published=is_published)
        db.add(page)
        await db.commit()
        await db.refresh(page)
        return page


async def get_page_by_slug(slug: str) -> Page | None:
    async with async_session() as db:
        result = await db.execute(
            select(Page)
            .where(Page.slug == slug, Page.is_published == True)
            .options(selectinload(Page.blocks))
        )
        return result.scalar_one_or_none()


async def get_page_by_id(page_id: int) -> Page | None:
    async with async_session() as db:
        return await db.get(Page, page_id)


async def list_pages() -> list[Page]:
    async with async_session() as db:
        result = await db.execute(select(Page).order_by(Page.sort_order, Page.id))
        return result.scalars().all()


async def list_published_page_slugs() -> list[dict]:
    async with async_session() as db:
        result = await db.execute(
            select(Page.slug, Page.type, Page.sort_order).where(Page.is_published == True).order_by(Page.sort_order, Page.id)
        )
        return [{"slug": row[0], "type": row[1], "sort_order": row[2]} for row in result.all()]


async def update_page(page_id: int, **kwargs) -> Page | None:
    async with async_session() as db:
        page = await db.get(Page, page_id)
        if page:
            for k, v in kwargs.items():
                if v is not None:
                    setattr(page, k, v)
            await db.commit()
            await db.refresh(page)
        return page


async def delete_page(page_id: int) -> bool:
    async with async_session() as db:
        page = await db.get(Page, page_id)
        if page:
            await db.delete(page)
            await db.commit()
            return True
        return False


async def delete_page_with_name(page_id: int) -> tuple[bool, str | None]:
    """Delete a page and return (success, page_name_for_audit)."""
    async with async_session() as db:
        page = await db.get(Page, page_id)
        if not page:
            return False, None
        name = page.name_zh
        await db.delete(page)
        await db.commit()
        return True, name
