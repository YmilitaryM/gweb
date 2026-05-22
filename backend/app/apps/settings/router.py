from fastapi import APIRouter, Depends, HTTPException, Request
from app.apps.auth.router import get_current_user
from app.apps.audit.service import create_audit_log
from app.apps.settings.service import get_setting, set_setting, get_public_settings, list_all_settings
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


@router_admin.get("")
async def admin_list_settings():
    return await list_all_settings()


@router_admin.put("/{key}")
async def update_setting(key: str, body: SetSettingRequest, request: Request, current_user=Depends(get_current_user)):
    await set_setting(key, body.value)
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="setting",
        resource_id=None,
        resource_name=key,
        ip_address=request.client.host if request.client else None,
    )
    return {"key": key, "updated": True}
