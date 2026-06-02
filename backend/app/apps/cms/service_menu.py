from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.apps.cms.models import Menu
from app.core.database import async_session


async def create_menu_item(
    name_zh: str,
    name_en: str,
    link: str = "",
    page_id: int | None = None,
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
            page_id=page_id,
            location=location,
            order=order,
            parent_id=parent_id,
            icon=icon,
        )
        db.add(menu)
        await db.commit()
        await db.refresh(menu)
        return menu


async def get_menu_tree(location: str | None = None, admin: bool = False) -> list[dict]:
    async with async_session() as db:
        from app.apps.cms.models import Page
        q = (
            select(Menu)
            .outerjoin(Page, Menu.page_id == Page.id)
        )
        if not admin:
            q = q.where(Menu.is_visible == True)
            q = q.where((Page.is_published == True) | (Menu.page_id == None))
        if location:
            q = q.where(Menu.location == location)
        q = q.order_by(Page.sort_order, Menu.order)
        result = await db.execute(q)
        items = result.scalars().all()

    by_id: dict[int, dict] = {}
    for m in items:
        by_id[m.id] = {
            "id": m.id,
            "name_zh": m.name_zh,
            "name_en": m.name_en,
            "link": m.link,
            "page_id": m.page_id,
            "page_slug": None,
            "icon": m.icon,
            "order": m.order,
            "is_visible": m.is_visible,
            "location": m.location,
            "parent_id": m.parent_id,
            "children": [],
        }

    # Resolve page_slug for items with page_id
    if items:
        async with async_session() as db:
            from app.apps.cms.models import Page
            page_ids = [m.page_id for m in items if m.page_id]
            if page_ids:
                page_result = await db.execute(
                    select(Page.id, Page.slug).where(Page.id.in_(page_ids))
                )
                slug_map = {row[0]: row[1] for row in page_result.all()}
                for m in items:
                    if m.page_id and m.page_id in slug_map:
                        by_id[m.id]["page_slug"] = slug_map[m.page_id]

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
