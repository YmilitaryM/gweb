from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.apps.auth.router import get_current_user
from app.apps.cms.service_media import delete_media, list_media, upload_media
from app.core.storage import storage

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
