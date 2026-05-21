from datetime import datetime
from pydantic import BaseModel


class ThemeCreate(BaseModel):
    name: str
    slug: str
    variables: dict = {}
    tech_effects: dict = {}
    is_active: bool = False


class ThemeUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    variables: dict | None = None
    tech_effects: dict | None = None
    is_active: bool | None = None


class ThemeResponse(BaseModel):
    id: int
    name: str
    slug: str
    variables: dict
    tech_effects: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
