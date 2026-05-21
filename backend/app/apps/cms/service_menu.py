from sqlalchemy import select

from app.apps.cms.models import Menu
from app.core.database import async_session


async def create_menu_item(
    name_zh: str,
    name_en: str,
    link: str = "",
    location: str = "header",
    order: int = 0,
    parent_id: int | None = None,
    icon: str | None = None,
) -> Menu:
    async with async_session() as db:
        menu = Menu(
            name_zh=name_zh,
            name_en=name_en,
            link=link,
            location=location,
            order=order,
            parent_id=parent_id,
            icon=icon,
        )
        db.add(menu)
        await db.commit()
        await db.refresh(menu)
        return menu


async def get_menu_tree(location: str | None = None) -> list[dict]:
    async with async_session() as db:
        q = select(Menu).where(Menu.is_visible == True)
        if location:
            q = q.where(Menu.location == location)
        q = q.order_by(Menu.order)
        result = await db.execute(q)
        items = result.scalars().all()

    by_id: dict[int, dict] = {}
    for m in items:
        by_id[m.id] = {
            "id": m.id,
            "name_zh": m.name_zh,
            "name_en": m.name_en,
            "link": m.link,
            "icon": m.icon,
            "children": [],
        }
    tree: list[dict] = []
    for m in items:
        node = by_id[m.id]
        if m.parent_id and m.parent_id in by_id:
            by_id[m.parent_id]["children"].append(node)
        else:
            tree.append(node)
    return tree


async def update_menu_item(menu_id: int, **kwargs) -> Menu | None:
    async with async_session() as db:
        menu = await db.get(Menu, menu_id)
        if menu:
            for k, v in kwargs.items():
                if v is not None:
                    setattr(menu, k, v)
            await db.commit()
            await db.refresh(menu)
        return menu


async def delete_menu_item(menu_id: int) -> bool:
    async with async_session() as db:
        menu = await db.get(Menu, menu_id)
        if menu:
            await db.delete(menu)
            await db.commit()
            return True
        return False
