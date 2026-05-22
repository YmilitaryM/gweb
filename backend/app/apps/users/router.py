from fastapi import APIRouter, Depends, HTTPException, Request

from app.apps.audit.service import create_audit_log
from app.apps.auth.router import require_admin, get_current_user
from app.apps.auth.schemas import UserOut
from app.apps.users.schemas import UserCreate, UserUpdate
from app.apps.users import service as users_svc

router = APIRouter(
    prefix="/api/v1/admin/users",
    tags=["admin-users"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=list[UserOut])
async def list_users():
    return await users_svc.list_users()


@router.post("", response_model=UserOut, status_code=201)
async def create_user(data: UserCreate, request: Request, current_user=Depends(get_current_user)):
    user = await users_svc.create_user(**data.model_dump())
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="create",
        resource_type="user",
        resource_id=user.id,
        resource_name=user.username,
        ip_address=request.client.host if request.client else None,
    )
    return user


@router.put("/{user_id}", response_model=UserOut)
async def update_user(user_id: int, data: UserUpdate, request: Request, current_user=Depends(get_current_user)):
    user = await users_svc.update_user(user_id, **data.model_dump(exclude_none=True))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="user",
        resource_id=user.id,
        resource_name=user.username,
        ip_address=request.client.host if request.client else None,
    )
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: int, request: Request, current_user=Depends(get_current_user)):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    deleted = await users_svc.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="delete",
        resource_type="user",
        resource_id=user_id,
        resource_name=None,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True}
