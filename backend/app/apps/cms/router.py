from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.apps.auth.router import get_current_user
from app.apps.cms.schemas import BlockCreate, BlockUpdate, PageCreate, PageOut, ReorderRequest
from app.apps.cms.service_block import create_block, delete_block, reorder_blocks, update_block
from app.apps.cms.service_media import delete_media, list_media, upload_media
from app.apps.cms.service_page import create_page, get_page_by_id, get_page_by_slug, list_pages, update_page, delete_page as svc_delete_page
from app.core.database import async_session
from app.apps.cms.models import Page as PageModel
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
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    media = await upload_media(
        data, file.filename, file.content_type or "application/octet-stream"
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
async def list_media_endpoint(page: int = 1, size: int = 20):
    return await list_media(page, size)


@admin_router.delete("/{media_id}")
async def delete_media_endpoint(media_id: int):
    deleted = await delete_media(media_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Media not found")
    return {"deleted": True}


# ---------------------------------------------------------------------------
# Public page endpoint
# ---------------------------------------------------------------------------

public_router = APIRouter(prefix="/api/v1", tags=["public"])


@public_router.get("/pages/{slug}", response_model=PageOut)
async def get_page(slug: str):
    page = await get_page_by_slug(slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


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
            "is_published": p.is_published,
        }
        for p in pages
    ]


@page_admin_router.post("/pages", status_code=201)
async def admin_create_page(data: PageCreate):
    # Check for duplicate slug
    async with async_session() as db:
        result = await db.execute(
            select(PageModel).where(PageModel.slug == data.slug)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Slug already exists")
    page = await create_page(**data.model_dump())
    return {"id": page.id, "slug": page.slug}


@page_admin_router.put("/pages/{page_id}")
async def admin_update_page(page_id: int, data: PageCreate):
    page = await update_page(page_id, **data.model_dump())
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"id": page.id, "slug": page.slug}


@page_admin_router.delete("/pages/{page_id}")
async def admin_delete_page(page_id: int):
    deleted = await svc_delete_page(page_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"deleted": True}


@page_admin_router.post("/pages/{page_id}/blocks", status_code=201)
async def admin_create_block(page_id: int, data: BlockCreate):
    pg = await get_page_by_id(page_id)
    if not pg:
        raise HTTPException(status_code=404, detail="Page not found")
    try:
        block = await create_block(page_id, data.type, data.config, data.content)
        return {"id": block.id, "type": block.type, "order": block.order}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@page_admin_router.put("/blocks/reorder")
async def admin_reorder_blocks(data: ReorderRequest):
    await reorder_blocks(data.page_id, data.block_ids)
    return {"ok": True}


@page_admin_router.put("/blocks/{block_id}")
async def admin_update_block(block_id: int, data: BlockUpdate):
    block = await update_block(block_id, **data.model_dump(exclude_none=True))
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"id": block.id, "type": block.type}


@page_admin_router.delete("/blocks/{block_id}")
async def admin_delete_block(block_id: int):
    deleted = await delete_block(block_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"deleted": True}
