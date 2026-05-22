from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "editor"
    display_name: str | None = None
    phone: str | None = None
    email: str | None = None
    avatar: str | None = None


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    role: str | None = None
    display_name: str | None = None
    phone: str | None = None
    email: str | None = None
    avatar: str | None = None
