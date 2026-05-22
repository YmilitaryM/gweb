from datetime import datetime
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    display_name: str | None = None
    phone: str | None = None
    email: str | None = None
    avatar: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
