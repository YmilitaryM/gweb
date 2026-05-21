from fastapi import APIRouter, Depends
from app.apps.auth.router import get_current_user
from app.apps.settings.service import get_setting, set_setting, get_public_settings
from pydantic import BaseModel

router_public = APIRouter(prefix="/api/v1/settings", tags=["settings"])
router_admin = APIRouter(
    prefix="/api/v1/admin/settings",
    tags=["admin-settings"],
    dependencies=[Depends(get_current_user)],
)


class SetSettingRequest(BaseModel):
    value: str


@router_public.get("/public")
async def public_settings():
    return await get_public_settings()


@router_admin.put("/{key}")
async def update_setting(key: str, body: SetSettingRequest):
    await set_setting(key, body.value)
    return {"key": key, "updated": True}
