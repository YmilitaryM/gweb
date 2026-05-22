from pydantic import BaseModel
from datetime import datetime


class AuditLogOut(BaseModel):
    id: int
    user_id: int
    username: str
    action: str
    resource_type: str
    resource_id: int | None
    resource_name: str | None
    detail: dict | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
