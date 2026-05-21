from sqlalchemy import select
from app.core.database import async_session
from app.apps.theme.models import Theme


async def create_theme(**kwargs) -> Theme:
    async with async_session() as db:
        theme = Theme(**kwargs)
        db.add(theme)
        await db.commit()
        await db.refresh(theme)
        return theme


async def get_active_theme() -> Theme | None:
    async with async_session() as db:
        result = await db.execute(
            select(Theme).where(Theme.is_active == True).limit(1)
        )
        return result.scalar_one_or_none()


async def list_themes() -> list[Theme]:
    async with async_session() as db:
        result = await db.execute(select(Theme).order_by(Theme.id))
        return result.scalars().all()


async def get_theme_by_id(theme_id: int) -> Theme | None:
    async with async_session() as db:
        return await db.get(Theme, theme_id)


async def update_theme(theme_id: int, **kwargs) -> Theme | None:
    async with async_session() as db:
        theme = await db.get(Theme, theme_id)
        if theme:
            for k, v in kwargs.items():
                if v is not None:
                    setattr(theme, k, v)
            await db.commit()
            await db.refresh(theme)
        return theme


async def delete_theme(theme_id: int) -> bool:
    async with async_session() as db:
        theme = await db.get(Theme, theme_id)
        if theme:
            await db.delete(theme)
            await db.commit()
            return True
        return False


async def activate_theme(theme_id: int) -> Theme | None:
    async with async_session() as db:
        theme = await db.get(Theme, theme_id)
        if not theme:
            return None
        # Deactivate all other themes
        result = await db.execute(select(Theme).where(Theme.is_active == True))
        for t in result.scalars().all():
            t.is_active = False
        # Activate the requested theme
        theme.is_active = True
        await db.commit()
        await db.refresh(theme)
        return theme
