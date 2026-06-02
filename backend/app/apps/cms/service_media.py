import io

from PIL import Image
from sqlalchemy import select, func

from app.apps.cms.models import Media, MediaCategory, MediaType
from app.core.database import async_session
from app.core.storage import storage
from app.shared.pagination import PaginatedResponse, PaginationParams


async def upload_media(
    file_data: bytes,
    filename: str,
    content_type: str,
    category: str | None = None,
    name_zh: str | None = None,
    name_en: str | None = None,
    description: str | None = None,
) -> Media:
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
        try:
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
                category=category,
                name_zh=name_zh,
                name_en=name_en,
                description=description,
            )
            db.add(media)
            await db.commit()
            await db.refresh(media)
            return media
        except Exception:
            # Clean up uploaded files on DB failure
            storage.delete(object_path)
            if thumbnail_path:
                storage.delete(thumbnail_path)
            raise


async def list_media(
    page: int = 1,
    size: int = 20,
    category: str | None = None,
    q: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict:
    p = PaginationParams(page, size)
    async with async_session() as db:
        stmt = select(Media)
        count_stmt = select(func.count(Media.id))

        if category:
            stmt = stmt.where(Media.category == category)
            count_stmt = count_stmt.where(Media.category == category)
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                (Media.filename.ilike(pattern))
                | (Media.name_zh.ilike(pattern))
                | (Media.name_en.ilike(pattern))
            )
            count_stmt = count_stmt.where(
                (Media.filename.ilike(pattern))
                | (Media.name_zh.ilike(pattern))
                | (Media.name_en.ilike(pattern))
            )
        if date_from:
            stmt = stmt.where(Media.created_at >= date_from)
            count_stmt = count_stmt.where(Media.created_at >= date_from)
        if date_to:
            stmt = stmt.where(Media.created_at <= date_to)
            count_stmt = count_stmt.where(Media.created_at <= date_to)

        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        result = await db.execute(
            stmt.order_by(Media.id.desc()).offset(p.offset).limit(p.size)
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
                    "category": m.category,
                    "name_zh": m.name_zh,
                    "name_en": m.name_en,
                    "description": m.description,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in items
            ],
            total=total,
            page=p.page,
            size=p.size,
            pages=max(1, (total + p.size - 1) // p.size),
        ).model_dump()


async def list_media_categories() -> list[dict]:
    async with async_session() as db:
        # Query categories with media counts
        from sqlalchemy.orm import aliased
        result = await db.execute(
            select(
                MediaCategory.name,
                func.count(Media.id).label("count"),
                func.max(Media.id).label("cover_id"),
            )
            .outerjoin(Media, Media.category == MediaCategory.name)
            .group_by(MediaCategory.name, MediaCategory.sort_order)
            .order_by(MediaCategory.sort_order, MediaCategory.name)
        )
        return [
            {
                "name": row.name,
                "count": row.count,
                "cover_image_id": row.cover_id,
            }
            for row in result
        ]


async def create_media_category(name: str) -> bool:
    async with async_session() as db:
        existing = await db.execute(
            select(MediaCategory).where(MediaCategory.name == name)
        )
        if existing.scalar_one_or_none():
            return False
        db.add(MediaCategory(name=name))
        await db.commit()
        return True


async def rename_media_category(old_name: str, new_name: str) -> bool:
    async with async_session() as db:
        cat = await db.execute(
            select(MediaCategory).where(MediaCategory.name == old_name)
        )
        cat = cat.scalar_one_or_none()
        if not cat:
            return False
        # Check new name doesn't exist
        dup = await db.execute(
            select(MediaCategory).where(MediaCategory.name == new_name)
        )
        if dup.scalar_one_or_none():
            return False
        cat.name = new_name
        # Update media referencing this category
        media_result = await db.execute(
            select(Media).where(Media.category == old_name)
        )
        for m in media_result.scalars().all():
            m.category = new_name
        await db.commit()
        return True


async def delete_media_category(name: str) -> bool:
    """Delete category and clear it from all media. Returns True if category existed."""
    async with async_session() as db:
        cat = await db.execute(
            select(MediaCategory).where(MediaCategory.name == name)
        )
        cat = cat.scalar_one_or_none()
        if not cat:
            return False
        await db.delete(cat)
        # Clear media referencing this category
        media_result = await db.execute(
            select(Media).where(Media.category == name)
        )
        for m in media_result.scalars().all():
            m.category = None
        await db.commit()
        return True


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
