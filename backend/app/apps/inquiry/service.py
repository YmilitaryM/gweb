from sqlalchemy import select, func
from app.core.database import async_session
from app.apps.inquiry.models import Inquiry


async def create_inquiry(**kwargs) -> Inquiry:
    async with async_session() as db:
        inquiry = Inquiry(**kwargs)
        db.add(inquiry)
        await db.commit()
        await db.refresh(inquiry)
        return inquiry


async def list_inquiries(page: int = 1, size: int = 20) -> tuple[list[Inquiry], int]:
    async with async_session() as db:
        count_query = select(func.count(Inquiry.id))
        result_total = await db.execute(count_query)
        total = result_total.scalar() or 0
        query = (
            select(Inquiry)
            .order_by(Inquiry.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await db.execute(query)
        return result.scalars().all(), total


async def get_inquiry_by_id(inquiry_id: int) -> Inquiry | None:
    async with async_session() as db:
        return await db.get(Inquiry, inquiry_id)


async def mark_inquiry_read(inquiry_id: int) -> Inquiry | None:
    async with async_session() as db:
        inquiry = await db.get(Inquiry, inquiry_id)
        if inquiry:
            inquiry.is_read = True
            await db.commit()
            await db.refresh(inquiry)
        return inquiry
