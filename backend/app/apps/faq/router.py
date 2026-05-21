from fastapi import APIRouter, Depends, HTTPException

from app.apps.auth.router import get_current_user
from app.apps.faq.schemas import FAQCreate, FAQResponse, FAQUpdate
from app.apps.faq.service import (
    create_faq,
    delete_faq,
    get_faq_by_id,
    list_all_faqs,
    list_published_faqs,
    update_faq,
)

public_router = APIRouter(prefix="/api/v1", tags=["faq"])

admin_router = APIRouter(
    prefix="/api/v1/admin/faqs",
    tags=["admin-faq"],
    dependencies=[Depends(get_current_user)],
)


@public_router.get("/faqs", response_model=list[FAQResponse])
async def get_faqs():
    return await list_published_faqs()


@admin_router.get("", response_model=list[FAQResponse])
async def admin_list_faqs():
    return await list_all_faqs()


@admin_router.post("", response_model=FAQResponse, status_code=201)
async def admin_create_faq(data: FAQCreate):
    faq = await create_faq(**data.model_dump())
    return faq


@admin_router.put("/{faq_id}", response_model=FAQResponse)
async def admin_update_faq(faq_id: int, data: FAQUpdate):
    faq = await update_faq(faq_id, **data.model_dump(exclude_none=True))
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq


@admin_router.delete("/{faq_id}")
async def admin_delete_faq(faq_id: int):
    deleted = await delete_faq(faq_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return {"deleted": True}
