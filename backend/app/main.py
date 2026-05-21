from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.apps.auth.router import router as auth_router
from app.apps.cms.router import admin_router as media_admin_router
from app.apps.cms.router import public_router as cms_public_router
from app.apps.cms.router import page_admin_router
from app.apps.settings.router import router_public as settings_public_router
from app.apps.settings.router import router_admin as settings_admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="GWeb API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.include_router(auth_router)
app.include_router(cms_public_router)
app.include_router(settings_public_router)
app.include_router(settings_admin_router)
app.include_router(media_admin_router)
app.include_router(page_admin_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
