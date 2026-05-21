from sqlalchemy import select
from app.core.database import async_session
from app.core.security import hash_password, verify_password, create_access_token
from app.apps.auth.models import User, UserRole


async def create_user(username: str, password: str, role: str = "editor") -> User:
    async with async_session() as db:
        user = User(username=username, password_hash=hash_password(password), role=UserRole(role))
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


async def authenticate(username: str, password: str) -> str | None:
    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user and verify_password(password, user.password_hash):
            return create_access_token(user.id)
        return None


async def get_user_by_id(user_id: int) -> User | None:
    async with async_session() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
