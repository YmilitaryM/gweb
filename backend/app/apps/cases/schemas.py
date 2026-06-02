from datetime import datetime
from pydantic import BaseModel


class CaseStat(BaseModel):
    label: str
    value: str


class CaseCreate(BaseModel):
    name_zh: str
    name_en: str
    slug: str
    cover_image_id: int | None = None
    summary_zh: str = ""
    summary_en: str = ""
    content_zh: str = ""
    content_en: str = ""
    category: str = "park"
    stats: list[CaseStat] | None = None
    sort_order: int = 0
    is_published: bool = False


class CaseUpdate(BaseModel):
    name_zh: str | None = None
    name_en: str | None = None
    slug: str | None = None
    cover_image_id: int | None = None
    summary_zh: str | None = None
    summary_en: str | None = None
    content_zh: str | None = None
    content_en: str | None = None
    category: str | None = None
    stats: list[CaseStat] | None = None
    sort_order: int | None = None
    is_published: bool | None = None


class CaseResponse(BaseModel):
    id: int
    name_zh: str
    name_en: str
    slug: str
    cover_image_id: int | None
    summary_zh: str
    summary_en: str
    content_zh: str
    content_en: str
    category: str
    stats: list[CaseStat] | None
    sort_order: int
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
