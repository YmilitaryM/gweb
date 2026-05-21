from pydantic import BaseModel


class PaginationParams:
    def __init__(self, page: int = 1, size: int = 20):
        self.page = max(1, page)
        self.size = min(100, max(1, size))
        self.offset = (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int
