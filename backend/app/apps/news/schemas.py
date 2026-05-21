from datetime import datetime
from pydantic import BaseModel


class NewsCreate(BaseModel):
    title_zh: str
    title_en: str
    summary_zh: str = ""
    summary_en: str = ""
    content_zh: str = ""
    content_en: str = ""
    cover_image_id: int | None = None
    category: str = "company_news"
    published_at: datetime | None = None
    is_published: bool = False


class NewsUpdate(BaseModel):
    title_zh: str | None = None
    title_en: str | None = None
    summary_zh: str | None = None
    summary_en: str | None = None
    content_zh: str | None = None
    content_en: str | None = None
    cover_image_id: int | None = None
    category: str | None = None
    published_at: datetime | None = None
    is_published: bool | None = None


class NewsResponse(BaseModel):
    id: int
    title_zh: str
    title_en: str
    summary_zh: str
    summary_en: str
    content_zh: str
    content_en: str
    cover_image_id: int | None
    category: str
    published_at: datetime
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
