import io

from PIL import Image
from sqlalchemy import select, func

from app.apps.cms.models import Media, MediaType
from app.core.database import async_session
from app.core.storage import storage
from app.shared.pagination import PaginatedResponse, PaginationParams


async def upload_media(file_data: bytes, filename: str, content_type: str) -> Media:
    mt = content_type.split("/")[0]
    media_type = (
        MediaType(mt) if mt in ("image", "video") else MediaType.document
    )

    object_path = storage.upload(file_data, filename, content_type)
    thumbnail_path = None
    width, height = None, None

    if media_type == MediaType.image:
        try:
            img = Image.open(io.BytesIO(file_data))
            width, height = img.size
            thumb = img.copy()
            thumb.thumbnail((400, 300))
            thumb_buf = io.BytesIO()
            thumb.save(thumb_buf, format="WEBP", quality=80)
            thumbnail_path = storage.upload(
                thumb_buf.getvalue(), f"thumb_{filename}", "image/webp"
            )
        except Exception:
            pass  # Non-image data, skip thumbnail

    async with async_session() as db:
        media = Media(
            filename=filename,
            original_name=filename,
            mime_type=content_type,
            size=len(file_data),
            type=media_type,
            path=object_path,
            thumbnail_path=thumbnail_path,
            width=width,
            height=height,
        )
        db.add(media)
        await db.commit()
        await db.refresh(media)
        return media


async def list_media(page: int = 1, size: int = 20) -> dict:
    p = PaginationParams(page, size)
    async with async_session() as db:
        total_result = await db.execute(select(func.count(Media.id)))
        total = total_result.scalar()
        result = await db.execute(
            select(Media).order_by(Media.id.desc()).offset(p.offset).limit(p.size)
        )
        items = result.scalars().all()
        return PaginatedResponse(
            items=[
                {
                    "id": m.id,
                    "filename": m.original_name,
                    "mime_type": m.mime_type,
                    "url": storage.get_url(m.path),
                    "size": m.size,
                    "thumbnail_url": (
                        storage.get_url(m.thumbnail_path)
                        if m.thumbnail_path
                        else None
                    ),
                }
                for m in items
            ],
            total=total,
            page=p.page,
            size=p.size,
            pages=max(1, (total + p.size - 1) // p.size),
        ).model_dump()


async def delete_media(media_id: int) -> bool:
    async with async_session() as db:
        media = await db.get(Media, media_id)
        if media:
            storage.delete(media.path)
            if media.thumbnail_path:
                storage.delete(media.thumbnail_path)
            await db.delete(media)
            await db.commit()
            return True
        return False
