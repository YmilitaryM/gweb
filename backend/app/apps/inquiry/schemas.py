from datetime import datetime
from pydantic import BaseModel


class InquiryCreate(BaseModel):
    company_name: str
    contact_name: str
    phone: str
    message: str


class InquiryResponse(BaseModel):
    id: int
    company_name: str
    contact_name: str
    phone: str
    message: str
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
