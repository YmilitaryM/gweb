from fastapi import APIRouter, Depends, HTTPException

from app.apps.auth.router import get_current_user
from app.apps.theme.schemas import ThemeCreate, ThemeResponse, ThemeUpdate
from app.apps.theme.service import (
    activate_theme,
    create_theme,
    delete_theme,
    get_active_theme,
    list_themes,
    update_theme,
)

public_router = APIRouter(prefix="/api/v1", tags=["theme"])

admin_router = APIRouter(
    prefix="/api/v1/admin/themes",
    tags=["admin-theme"],
    dependencies=[Depends(get_current_user)],
)


@public_router.get("/themes/active", response_model=ThemeResponse)
async def get_active():
    theme = await get_active_theme()
    if not theme:
        raise HTTPException(status_code=404, detail="No active theme")
    return theme


@admin_router.get("", response_model=list[ThemeResponse])
async def admin_list_themes():
    return await list_themes()


@admin_router.post("", response_model=ThemeResponse, status_code=201)
async def admin_create_theme(data: ThemeCreate):
    theme = await create_theme(**data.model_dump())
    return theme


@admin_router.put("/{theme_id}", response_model=ThemeResponse)
async def admin_update_theme(theme_id: int, data: ThemeUpdate):
    theme = await update_theme(theme_id, **data.model_dump(exclude_none=True))
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    return theme


@admin_router.delete("/{theme_id}")
async def admin_delete_theme(theme_id: int):
    deleted = await delete_theme(theme_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Theme not found")
    return {"deleted": True}


@admin_router.put("/{theme_id}/activate", response_model=ThemeResponse)
async def admin_activate_theme(theme_id: int):
    theme = await activate_theme(theme_id)
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    return theme
