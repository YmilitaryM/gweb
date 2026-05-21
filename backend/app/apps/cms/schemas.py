from pydantic import BaseModel


class PageCreate(BaseModel):
    name_zh: str
    name_en: str
    slug: str


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
    blocks: list[BlockOut]

    model_config = {"from_attributes": True}
