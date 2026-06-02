from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from app.apps.audit.service import create_audit_log
from app.apps.auth.router import get_current_user
from app.apps.cms.schemas import BlockCreate, BlockUpdate, MenuCreate, MenuUpdate, PageCreate, PageUpdate, PageOut, PageSlugOut, ReorderRequest
from app.apps.cms.service_block import create_block, delete_block, reorder_blocks, update_block
from app.apps.cms.service_media import (
    delete_media, list_media, list_media_categories,
    create_media_category, rename_media_category, delete_media_category, upload_media,
)
from app.apps.cms.service_menu import create_menu_item, delete_menu_item, get_menu_tree, update_menu_item
from app.apps.cms.service_page import create_page, get_page_by_id, get_page_by_slug, list_pages, list_published_page_slugs, update_page, delete_page as svc_delete_page
from app.core.database import async_session
from app.apps.cms.models import Page as PageModel, Media
from app.core.storage import storage
from sqlalchemy import select

# ---------------------------------------------------------------------------
# Media routes (unchanged)
# ---------------------------------------------------------------------------

admin_router = APIRouter(
    prefix="/api/v1/admin/media",
    tags=["admin-media"],
    dependencies=[Depends(get_current_user)],
)


@admin_router.post("/upload", status_code=201)
async def upload(
    file: UploadFile = File(...),
    category: str | None = Form(None),
    name_zh: str | None = Form(None),
    name_en: str | None = Form(None),
    description: str | None = Form(None),
    request: Request = None,
    current_user=Depends(get_current_user),
):
    data = await file.read()
    media = await upload_media(
        data,
        file.filename,
        file.content_type or "application/octet-stream",
        category=category,
        name_zh=name_zh,
        name_en=name_en,
        description=description,
    )
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="create",
        resource_type="media",
        resource_id=media.id,
        resource_name=media.original_name,
        ip_address=request.client.host if request.client else None,
    )
    return {
        "id": media.id,
        "filename": media.original_name,
        "mime_type": media.mime_type,
        "url": storage.get_url(media.path),
        "thumbnail_url": (
            storage.get_url(media.thumbnail_path) if media.thumbnail_path else None
        ),
        "width": media.width,
        "height": media.height,
    }


@admin_router.get("")
async def list_media_endpoint(
    page: int = 1,
    size: int = 20,
    category: str | None = None,
    q: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
):
    return await list_media(page, size, category=category, q=q, date_from=date_from, date_to=date_to)


@admin_router.get("/categories")
async def list_categories():
    return await list_media_categories()


@admin_router.post("/categories", status_code=201)
async def create_category(
    data: dict,
    request: Request,
    current_user=Depends(get_current_user),
):
    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Category name is required")
    ok = await create_media_category(name)
    if not ok:
        raise HTTPException(status_code=409, detail="Category already exists")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="create",
        resource_type="media_category",
        resource_id=0,
        resource_name=name,
        ip_address=request.client.host if request.client else None,
    )
    return {"ok": True, "name": name}


@admin_router.put("/categories/rename")
async def rename_category(
    old_name: str,
    new_name: str,
    request: Request,
    current_user=Depends(get_current_user),
):
    ok = await rename_media_category(old_name, new_name)
    if not ok:
        raise HTTPException(status_code=404, detail="Category not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="media_category",
        resource_id=0,
        resource_name=f"{old_name} -> {new_name}",
        ip_address=request.client.host if request.client else None,
    )
    return {"ok": True}


@admin_router.delete("/categories/{name}")
async def delete_category(
    name: str,
    request: Request,
    current_user=Depends(get_current_user),
):
    ok = await delete_media_category(name)
    if not ok:
        raise HTTPException(status_code=404, detail="Category not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="delete",
        resource_type="media_category",
        resource_id=0,
        resource_name=name,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True}


@admin_router.delete("/{media_id}")
async def delete_media_endpoint(
    media_id: int,
    request: Request,
    current_user=Depends(get_current_user),
):
    deleted = await delete_media(media_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Media not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="delete",
        resource_type="media",
        resource_id=media_id,
        resource_name=None,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True}


# ---------------------------------------------------------------------------
# Public page endpoint
# ---------------------------------------------------------------------------

public_router = APIRouter(prefix="/api/v1", tags=["public"])


@public_router.get("/pages/slugs", response_model=list[PageSlugOut])
async def get_page_slugs():
    return await list_published_page_slugs()


@public_router.get("/pages/{slug}", response_model=PageOut)
async def get_page(slug: str):
    page = await get_page_by_slug(slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@public_router.get("/menus")
async def get_menus(location: str | None = None):
    return await get_menu_tree(location)


# ---------------------------------------------------------------------------
# Admin page & block CRUD
# ---------------------------------------------------------------------------

page_admin_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin-cms"],
    dependencies=[Depends(get_current_user)],
)


@page_admin_router.get("/pages")
async def admin_list_pages():
    pages = await list_pages()
    return [
        {
            "id": p.id,
            "name_zh": p.name_zh,
            "name_en": p.name_en,
            "slug": p.slug,
            "type": p.type,
            "sort_order": p.sort_order,
            "is_published": p.is_published,
        }
        for p in pages
    ]


@page_admin_router.post("/pages", status_code=201)
async def admin_create_page(
    data: PageCreate,
    request: Request,
    current_user=Depends(get_current_user),
):
    # Check for duplicate slug
    async with async_session() as db:
        result = await db.execute(
            select(PageModel).where(PageModel.slug == data.slug)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Slug already exists")
    page = await create_page(**data.model_dump())
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="create",
        resource_type="page",
        resource_id=page.id,
        resource_name=data.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return {"id": page.id, "slug": page.slug}


@page_admin_router.put("/pages/{page_id}")
async def admin_update_page(
    page_id: int,
    data: PageUpdate,
    request: Request,
    current_user=Depends(get_current_user),
):
    page = await update_page(page_id, **data.model_dump(exclude_none=True))
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="page",
        resource_id=page.id,
        resource_name=data.name_zh or page.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return {"id": page.id, "slug": page.slug}


@page_admin_router.delete("/pages/{page_id}")
async def admin_delete_page(
    page_id: int,
    request: Request,
    current_user=Depends(get_current_user),
):
    page = await get_page_by_id(page_id)
    deleted = await svc_delete_page(page_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Page not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="delete",
        resource_type="page",
        resource_id=page_id,
        resource_name=page.name_zh if page else None,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True}


@page_admin_router.post("/pages/{page_id}/blocks", status_code=201)
async def admin_create_block(
    page_id: int,
    data: BlockCreate,
    request: Request,
    current_user=Depends(get_current_user),
):
    pg = await get_page_by_id(page_id)
    if not pg:
        raise HTTPException(status_code=404, detail="Page not found")
    try:
        block = await create_block(page_id, data.type, data.config, data.content)
        await create_audit_log(
            user_id=current_user.id,
            username=current_user.username,
            action="create",
            resource_type="block",
            resource_id=block.id,
            resource_name=f"block_{data.type}",
            ip_address=request.client.host if request.client else None,
        )
        return {"id": block.id, "type": block.type, "order": block.order}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@page_admin_router.put("/blocks/reorder")
async def admin_reorder_blocks(data: ReorderRequest):
    await reorder_blocks(data.page_id, data.block_ids)
    return {"ok": True}


@page_admin_router.put("/blocks/{block_id}")
async def admin_update_block(
    block_id: int,
    data: BlockUpdate,
    request: Request,
    current_user=Depends(get_current_user),
):
    block = await update_block(block_id, **data.model_dump(exclude_none=True))
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="block",
        resource_id=block.id,
        resource_name=f"block_{block.type}",
        ip_address=request.client.host if request.client else None,
    )
    return {"id": block.id, "type": block.type}


@page_admin_router.delete("/blocks/{block_id}")
async def admin_delete_block(
    block_id: int,
    request: Request,
    current_user=Depends(get_current_user),
):
    deleted = await delete_block(block_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Block not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="delete",
        resource_type="block",
        resource_id=block_id,
        resource_name=None,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True}


# ---------------------------------------------------------------------------
# Admin menu CRUD
# ---------------------------------------------------------------------------


@page_admin_router.get("/menus")
async def admin_list_menus(location: str | None = None):
    return await get_menu_tree(location, admin=True)


@page_admin_router.post("/menus", status_code=201)
async def admin_create_menu(
    data: MenuCreate,
    request: Request,
    current_user=Depends(get_current_user),
):
    menu = await create_menu_item(**data.model_dump())
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="create",
        resource_type="menu",
        resource_id=menu.id,
        resource_name=data.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return {"id": menu.id, "name_zh": menu.name_zh, "name_en": menu.name_en}


@page_admin_router.put("/menus/{menu_id}")
async def admin_update_menu(
    menu_id: int,
    data: MenuUpdate,
    request: Request,
    current_user=Depends(get_current_user),
):
    menu = await update_menu_item(menu_id, **data.model_dump(exclude_none=True))
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="menu",
        resource_id=menu.id,
        resource_name=data.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return {"id": menu.id, "name_zh": menu.name_zh}


@page_admin_router.delete("/menus/{menu_id}")
async def admin_delete_menu(
    menu_id: int,
    request: Request,
    current_user=Depends(get_current_user),
):
    deleted = await delete_menu_item(menu_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Menu not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="delete",
        resource_type="menu",
        resource_id=menu_id,
        resource_name=None,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True}
