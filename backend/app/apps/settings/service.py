from sqlalchemy import select
from app.apps.settings.models import Setting
from app.core.database import async_session

ENCRYPTED_KEYS = {"llm_api_key", "embedding_api_key", "secret_key"}


async def get_setting(key: str) -> str | None:
    async with async_session() as db:
        setting = await db.get(Setting, key)
        return setting.value if setting else None


async def set_setting(key: str, value: str):
    async with async_session() as db:
        setting = await db.get(Setting, key)
        if setting:
            setting.value = value
            setting.is_encrypted = key in ENCRYPTED_KEYS
        else:
            setting = Setting(key=key, value=value, is_encrypted=key in ENCRYPTED_KEYS)
            db.add(setting)
        await db.commit()


async def get_public_settings() -> dict:
    async with async_session() as db:
        result = await db.execute(
            select(Setting).where(Setting.is_encrypted == False)
        )
        return {s.key: s.value for s in result.scalars()}
