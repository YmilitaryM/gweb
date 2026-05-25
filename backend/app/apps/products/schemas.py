from datetime import datetime
from pydantic import BaseModel


class ProductSpec(BaseModel):
    key: str
    value: str


# --- ProductCategory ---

class ProductCategoryCreate(BaseModel):
    name_zh: str
    name_en: str
    slug: str
    sort_order: int = 0
    is_published: bool = True


class ProductCategoryUpdate(BaseModel):
    name_zh: str | None = None
    name_en: str | None = None
    slug: str | None = None
    sort_order: int | None = None
    is_published: bool | None = None


class ProductCategoryResponse(BaseModel):
    id: int
    name_zh: str
    name_en: str
    slug: str
    sort_order: int
    is_published: bool
    created_at: datetime
    updated_at: datetime
    product_count: int = 0

    model_config = {"from_attributes": True}


# --- Product ---

class ProductCreate(BaseModel):
    category_id: int
    name_zh: str
    name_en: str
    slug: str
    cover_image_id: int | None = None
    summary_zh: str = ""
    summary_en: str = ""
    description_zh: str = ""
    description_en: str = ""
    specs: list[ProductSpec] | None = None
    images: list[int] | None = None
    sort_order: int = 0
    is_published: bool = True


class ProductUpdate(BaseModel):
    category_id: int | None = None
    name_zh: str | None = None
    name_en: str | None = None
    slug: str | None = None
    cover_image_id: int | None = None
    summary_zh: str | None = None
    summary_en: str | None = None
    description_zh: str | None = None
    description_en: str | None = None
    specs: list[ProductSpec] | None = None
    images: list[int] | None = None
    sort_order: int | None = None
    is_published: bool | None = None


class ProductResponse(BaseModel):
    id: int
    category_id: int
    name_zh: str
    name_en: str
    slug: str
    cover_image_id: int | None
    summary_zh: str
    summary_en: str
    description_zh: str
    description_en: str
    specs: list[ProductSpec] | None
    images: list[int] | None
    sort_order: int
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductDetailResponse(ProductResponse):
    category: ProductCategoryResponse | None = None
