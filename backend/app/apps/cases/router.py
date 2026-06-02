from fastapi import APIRouter, Depends, HTTPException, Request

from app.apps.audit.service import create_audit_log
from app.apps.auth.router import get_current_user
from app.apps.cases.schemas import CaseCreate, CaseResponse, CaseUpdate
from app.apps.cases.service import (
    create_case, delete_case, get_case_by_id, get_case_by_slug,
    list_all_cases, list_published_cases, update_case,
)

public_router = APIRouter(prefix="/api/v1", tags=["cases"])

admin_router = APIRouter(
    prefix="/api/v1/admin/cases",
    tags=["admin-cases"],
    dependencies=[Depends(get_current_user)],
)


@public_router.get("/cases")
async def public_list_cases(page: int = 1, size: int = 12, category: str | None = None):
    cases, total = await list_published_cases(page, size, category)
    return {
        "items": [CaseResponse.model_validate(c) for c in cases],
        "total": total,
        "page": page,
        "size": size,
    }


@public_router.get("/cases/{slug}", response_model=CaseResponse)
async def public_get_case(slug: str):
    case = await get_case_by_slug(slug)
    if not case or not case.is_published:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@admin_router.get("")
async def admin_list_cases(page: int = 1, size: int = 20, category: str | None = None):
    cases, total = await list_all_cases(page, size, category)
    return {
        "items": [CaseResponse.model_validate(c) for c in cases],
        "total": total,
        "page": page,
        "size": size,
    }


@admin_router.post("", response_model=CaseResponse, status_code=201)
async def admin_create_case(data: CaseCreate, request: Request, current_user=Depends(get_current_user)):
    case = await create_case(**data.model_dump())
    await create_audit_log(
        user_id=current_user.id, username=current_user.username,
        action="create", resource_type="case", resource_id=case.id,
        resource_name=case.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return case


@admin_router.put("/{case_id}", response_model=CaseResponse)
async def admin_update_case(case_id: int, data: CaseUpdate, request: Request, current_user=Depends(get_current_user)):
    case = await update_case(case_id, **data.model_dump(exclude_none=True))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    await create_audit_log(
        user_id=current_user.id, username=current_user.username,
        action="update", resource_type="case", resource_id=case.id,
        resource_name=case.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return case


@admin_router.delete("/{case_id}")
async def admin_delete_case(case_id: int, request: Request, current_user=Depends(get_current_user)):
    case = await get_case_by_id(case_id)
    name = case.name_zh if case else None
    deleted = await delete_case(case_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Case not found")
    await create_audit_log(
        user_id=current_user.id, username=current_user.username,
        action="delete", resource_type="case", resource_id=case_id,
        resource_name=name,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True}
