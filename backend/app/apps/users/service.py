from fastapi import HTTPException
from sqlalchemy import select, delete as sql_delete
from sqlalchemy.exc import IntegrityError
from app.core.database import async_session
from app.core.security import hash_password
from app.apps.auth.models import User
from app.apps.auth.service import create_user as auth_create_user, get_user_by_id


async def list_users() -> list[User]:
    async with async_session() as db:
        result = await db.execute(select(User).order_by(User.id))
        return list(result.scalars().all())


async def create_user(**kwargs) -> User:
    try:
        return await auth_create_user(**kwargs)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Username already exists")


async def update_user(user_id: int, **kwargs) -> User | None:
    user = await get_user_by_id(user_id)
    if user is None:
        return None
    async with async_session() as db:
        merged = await db.merge(user)
        if "password" in kwargs:
            pwd = kwargs.pop("password")
            if pwd:
                merged.password_hash = hash_password(pwd)
        for key, value in kwargs.items():
            if value is not None:
                setattr(merged, key, value)
        await db.commit()
        await db.refresh(merged)
        return merged


async def delete_user(user_id: int) -> bool:
    async with async_session() as db:
        result = await db.execute(sql_delete(User).where(User.id == user_id))
        await db.commit()
        return result.rowcount > 0
