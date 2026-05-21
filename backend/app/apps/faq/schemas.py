from datetime import datetime
from pydantic import BaseModel


class FAQCreate(BaseModel):
    question_zh: str
    question_en: str
    answer_zh: str = ""
    answer_en: str = ""
    order: int = 0
    is_published: bool = True


class FAQUpdate(BaseModel):
    question_zh: str | None = None
    question_en: str | None = None
    answer_zh: str | None = None
    answer_en: str | None = None
    order: int | None = None
    is_published: bool | None = None


class FAQResponse(BaseModel):
    id: int
    question_zh: str
    question_en: str
    answer_zh: str
    answer_en: str
    order: int
    is_published: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
