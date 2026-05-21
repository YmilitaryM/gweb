from fastapi import APIRouter, Depends, HTTPException, Query

from app.apps.auth.router import get_current_user
from app.apps.inquiry.schemas import InquiryCreate, InquiryResponse
from app.apps.inquiry.service import (
    create_inquiry,
    get_inquiry_by_id,
    list_inquiries,
    mark_inquiry_read,
)

public_router = APIRouter(prefix="/api/v1", tags=["inquiry"])

admin_router = APIRouter(
    prefix="/api/v1/admin/inquiries",
    tags=["admin-inquiry"],
    dependencies=[Depends(get_current_user)],
)


@public_router.post("/inquiries", response_model=dict, status_code=201)
async def submit_inquiry(data: InquiryCreate):
    inquiry = await create_inquiry(**data.model_dump())
    return {"id": inquiry.id, "message": "Inquiry submitted successfully"}


@admin_router.get("", response_model=dict)
async def admin_list_inquiries(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    items, total = await list_inquiries(page, size)
    return {
        "items": [InquiryResponse.model_validate(i) for i in items],
        "total": total,
        "page": page,
        "size": size,
    }


@admin_router.put("/{inquiry_id}/read", response_model=InquiryResponse)
async def admin_mark_read(inquiry_id: int):
    inquiry = await mark_inquiry_read(inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    return inquiry
