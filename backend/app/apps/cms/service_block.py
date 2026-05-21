from sqlalchemy import select, update
from app.core.database import async_session
from app.apps.cms.models import Block
from app.apps.cms.block_validators import validate_block_content


async def create_block(page_id: int, block_type: str, config: dict, content: dict) -> Block:
    validate_block_content(block_type, content)
    async with async_session() as db:
        result = await db.execute(
            select(Block).where(Block.page_id == page_id).order_by(Block.order.desc()).limit(1)
        )
        last = result.scalar_one_or_none()
        order = (last.order + 1) if last else 0

        block = Block(page_id=page_id, type=block_type, order=order, config=config, content=content)
        db.add(block)
        await db.commit()
        await db.refresh(block)
        return block


async def update_block(block_id: int, **kwargs) -> Block | None:
    async with async_session() as db:
        block = await db.get(Block, block_id)
        if block:
            if "content" in kwargs and kwargs["content"] is not None:
                validate_block_content(block.type, kwargs["content"])
            for k, v in kwargs.items():
                if v is not None:
                    setattr(block, k, v)
            await db.commit()
            await db.refresh(block)
        return block


async def delete_block(block_id: int) -> bool:
    async with async_session() as db:
        block = await db.get(Block, block_id)
        if block:
            await db.delete(block)
            await db.commit()
            return True
        return False


async def reorder_blocks(page_id: int, block_ids: list[int]):
    async with async_session() as db:
        for i, bid in enumerate(block_ids):
            await db.execute(update(Block).where(Block.id == bid).values(order=i))
        await db.commit()
