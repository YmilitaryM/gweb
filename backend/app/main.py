from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import select
from app.apps.auth.router import router as auth_router
from app.apps.cms.router import admin_router as media_admin_router
from app.apps.cms.router import public_router as cms_public_router
from app.apps.cms.router import page_admin_router
from app.apps.cms.models import Media
from app.apps.settings.router import router_public as settings_public_router
from app.apps.settings.router import router_admin as settings_admin_router
from app.apps.news.router import public_router as news_public_router
from app.apps.news.router import admin_router as news_admin_router
from app.apps.faq.router import public_router as faq_public_router
from app.apps.faq.router import admin_router as faq_admin_router
from app.apps.inquiry.router import public_router as inquiry_public_router
from app.apps.inquiry.router import admin_router as inquiry_admin_router
from app.apps.theme.router import public_router as theme_public_router
from app.apps.theme.router import admin_router as theme_admin_router
from app.apps.users.router import router as users_router
from app.apps.chat.router_public import router as chat_public_router
from app.apps.chat.router_admin import router as chat_admin_router
from app.apps.audit.router import router as audit_router
from app.core.database import async_session
from app.core.storage import storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="GWeb API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(cms_public_router)
app.include_router(settings_public_router)
app.include_router(settings_admin_router)
app.include_router(media_admin_router)
app.include_router(page_admin_router)
app.include_router(news_public_router)
app.include_router(news_admin_router)
app.include_router(faq_public_router)
app.include_router(faq_admin_router)
app.include_router(inquiry_public_router)
app.include_router(inquiry_admin_router)
app.include_router(theme_public_router)
app.include_router(theme_admin_router)
app.include_router(chat_public_router)
app.include_router(chat_admin_router)
app.include_router(audit_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/media/id/{media_id}")
async def serve_media_by_id(media_id: int):
    async with async_session() as db:
        result = await db.execute(
            select(Media).where(Media.id == media_id)
        )
        media = result.scalar_one_or_none()
    if media is None:
        raise HTTPException(status_code=404, detail="Media not found")
    filepath = Path(storage._local_storage) / media.path
    resolved = filepath.resolve()
    if not str(resolved).startswith(str(Path(storage._local_storage).resolve())):
        raise HTTPException(status_code=404, detail="Media not found")
    if not resolved.exists():
        raise HTTPException(status_code=404, detail="Media not found")
    return FileResponse(resolved, media_type=media.mime_type)


@app.get("/media/{media_path:path}")
async def serve_media(media_path: str):
    async with async_session() as db:
        result = await db.execute(
            select(Media).where(Media.path == media_path)
        )
        media = result.scalar_one_or_none()
    if media is None:
        raise HTTPException(status_code=404, detail="Media not found")
    filepath = Path(storage._local_storage) / media.path
    resolved = filepath.resolve()
    if not str(resolved).startswith(str(Path(storage._local_storage).resolve())):
        raise HTTPException(status_code=404, detail="Media not found")
    if not resolved.exists():
        raise HTTPException(status_code=404, detail="Media not found")
    return FileResponse(resolved, media_type=media.mime_type)
