from pydantic import BaseModel


class PageCreate(BaseModel):
    name_zh: str
    name_en: str
    slug: str
    type: str = "content"


class PageUpdate(BaseModel):
    name_zh: str | None = None
    name_en: str | None = None
    slug: str | None = None
    type: str | None = None


class BlockCreate(BaseModel):
    type: str
    config: dict = {}
    content: dict = {}


class BlockUpdate(BaseModel):
    type: str | None = None
    config: dict | None = None
    content: dict | None = None


class ReorderRequest(BaseModel):
    page_id: int
    block_ids: list[int]


class BlockOut(BaseModel):
    id: int
    type: str
    order: int
    config: dict
    content: dict

    model_config = {"from_attributes": True}


class PageOut(BaseModel):
    id: int
    name_zh: str
    name_en: str
    slug: str
    type: str
    blocks: list[BlockOut]

    model_config = {"from_attributes": True}


class PageSlugOut(BaseModel):
    slug: str
    type: str


class MenuCreate(BaseModel):
    name_zh: str
    name_en: str
    link: str = ""
    page_id: int | None = None
    location: str = "header"
    order: int = 0
    parent_id: int | None = None
    icon: str | None = None


class MenuUpdate(BaseModel):
    name_zh: str | None = None
    name_en: str | None = None
    link: str | None = None
    page_id: int | None = None
    location: str | None = None
    order: int | None = None
    parent_id: int | None = None
    icon: str | None = None


class MenuResponse(BaseModel):
    id: int
    name_zh: str
    name_en: str
    link: str
    page_id: int | None
    page_slug: str | None
    icon: str | None
    children: list["MenuResponse"] = []

    model_config = {"from_attributes": True}
