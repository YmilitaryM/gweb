from sqlalchemy import select, func
from app.apps.cases.models import Case
from app.core.database import async_session


async def list_published_cases(page: int = 1, size: int = 12, category: str | None = None) -> tuple[list["Case"], int]:
    async with async_session() as db:
        q = select(Case).where(Case.is_published == True)
        if category:
            q = q.where(Case.category == category)
        q = q.order_by(Case.sort_order, Case.created_at.desc())

        total_q = select(func.count()).select_from(Case).where(Case.is_published == True)
        if category:
            total_q = total_q.where(Case.category == category)
        total = (await db.execute(total_q)).scalar() or 0

        offset = (page - 1) * size
        result = await db.execute(q.offset(offset).limit(size))
        return result.scalars().all(), total


async def list_all_cases(page: int = 1, size: int = 20, category: str | None = None) -> tuple[list["Case"], int]:
    async with async_session() as db:
        q = select(Case).order_by(Case.sort_order, Case.created_at.desc())
        if category:
            q = q.where(Case.category == category)
        total_q = select(func.count()).select_from(Case)
        if category:
            total_q = total_q.where(Case.category == category)
        total = (await db.execute(total_q)).scalar() or 0
        offset = (page - 1) * size
        result = await db.execute(q.offset(offset).limit(size))
        return result.scalars().all(), total


async def get_case_by_id(case_id: int) -> Case | None:
    async with async_session() as db:
        return await db.get(Case, case_id)


async def get_case_by_slug(slug: str) -> Case | None:
    async with async_session() as db:
        result = await db.execute(select(Case).where(Case.slug == slug))
        return result.scalar_one_or_none()


async def create_case(**kwargs) -> Case:
    async with async_session() as db:
        case = Case(**kwargs)
        db.add(case)
        await db.commit()
        await db.refresh(case)
        return case


async def update_case(case_id: int, **kwargs) -> Case | None:
    async with async_session() as db:
        case = await db.get(Case, case_id)
        if not case:
            return None
        for k, v in kwargs.items():
            if v is not None:
                setattr(case, k, v)
        await db.commit()
        await db.refresh(case)
        return case


async def delete_case(case_id: int) -> bool:
    async with async_session() as db:
        case = await db.get(Case, case_id)
        if not case:
            return False
        await db.delete(case)
        await db.commit()
        return True
