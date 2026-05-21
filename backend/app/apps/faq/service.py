from sqlalchemy import select
from app.core.database import async_session
from app.apps.faq.models import FAQ


async def create_faq(**kwargs) -> FAQ:
    async with async_session() as db:
        faq = FAQ(**kwargs)
        db.add(faq)
        await db.commit()
        await db.refresh(faq)
        return faq


async def list_published_faqs() -> list[FAQ]:
    async with async_session() as db:
        result = await db.execute(
            select(FAQ)
            .where(FAQ.is_published == True)
            .order_by(FAQ.order, FAQ.id)
        )
        return result.scalars().all()


async def list_all_faqs() -> list[FAQ]:
    async with async_session() as db:
        result = await db.execute(select(FAQ).order_by(FAQ.order, FAQ.id))
        return result.scalars().all()


async def get_faq_by_id(faq_id: int) -> FAQ | None:
    async with async_session() as db:
        return await db.get(FAQ, faq_id)


async def update_faq(faq_id: int, **kwargs) -> FAQ | None:
    async with async_session() as db:
        faq = await db.get(FAQ, faq_id)
        if faq:
            for k, v in kwargs.items():
                if v is not None:
                    setattr(faq, k, v)
            await db.commit()
            await db.refresh(faq)
        return faq


async def delete_faq(faq_id: int) -> bool:
    async with async_session() as db:
        faq = await db.get(FAQ, faq_id)
        if faq:
            await db.delete(faq)
            await db.commit()
            return True
        return False
