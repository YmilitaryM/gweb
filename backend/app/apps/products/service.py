from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from app.core.database import async_session
from app.apps.products.models import Product, ProductCategory


# --- Category CRUD ---

async def create_category(**kwargs) -> ProductCategory:
    async with async_session() as db:
        cat = ProductCategory(**kwargs)
        db.add(cat)
        await db.commit()
        await db.refresh(cat)
        return cat


async def list_categories() -> list[ProductCategory]:
    async with async_session() as db:
        result = await db.execute(
            select(ProductCategory).order_by(ProductCategory.sort_order)
        )
        return list(result.scalars().all())


async def get_category_by_id(cat_id: int) -> ProductCategory | None:
    async with async_session() as db:
        return await db.get(ProductCategory, cat_id)


async def update_category(cat_id: int, **kwargs) -> ProductCategory | None:
    async with async_session() as db:
        cat = await db.get(ProductCategory, cat_id)
        if cat:
            for k, v in kwargs.items():
                if v is not None:
                    setattr(cat, k, v)
            await db.commit()
            await db.refresh(cat)
        return cat


async def delete_category(cat_id: int) -> bool:
    async with async_session() as db:
        cat = await db.get(ProductCategory, cat_id)
        if cat:
            await db.delete(cat)
            await db.commit()
            return True
        return False


async def get_category_product_count(cat_id: int) -> int:
    async with async_session() as db:
        result = await db.execute(
            select(func.count(Product.id)).where(Product.category_id == cat_id)
        )
        return result.scalar() or 0


# --- Product CRUD ---

async def create_product(**kwargs) -> Product:
    async with async_session() as db:
        prod = Product(**kwargs)
        db.add(prod)
        await db.commit()
        await db.refresh(prod)
        return prod


async def list_all_products(
    page: int = 1, size: int = 20, category_id: int | None = None
) -> tuple[list[Product], int]:
    async with async_session() as db:
        query = select(Product).options(joinedload(Product.category))
        count_query = select(func.count(Product.id))
        if category_id is not None:
            query = query.where(Product.category_id == category_id)
            count_query = count_query.where(Product.category_id == category_id)
        result_total = await db.execute(count_query)
        total = result_total.scalar() or 0
        query = (
            query.order_by(Product.sort_order, Product.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await db.execute(query)
        return list(result.unique().scalars().all()), total


async def list_published_products(
    page: int = 1, size: int = 20, category_slug: str | None = None
) -> tuple[list[Product], int]:
    async with async_session() as db:
        query = (
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.is_published == True)
        )
        count_query = select(func.count(Product.id)).where(
            Product.is_published == True
        )
        if category_slug:
            query = query.join(Product.category).where(
                ProductCategory.slug == category_slug
            )
            count_query = count_query.join(Product.category).where(
                ProductCategory.slug == category_slug
            )
        result_total = await db.execute(count_query)
        total = result_total.scalar() or 0
        query = (
            query.order_by(Product.sort_order, Product.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await db.execute(query)
        return list(result.unique().scalars().all()), total


async def get_product_by_id(prod_id: int) -> Product | None:
    async with async_session() as db:
        result = await db.execute(
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.id == prod_id)
        )
        return result.unique().scalar_one_or_none()


async def get_product_by_slug(slug: str) -> Product | None:
    async with async_session() as db:
        result = await db.execute(
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.slug == slug, Product.is_published == True)
        )
        return result.unique().scalar_one_or_none()


async def update_product(prod_id: int, **kwargs) -> Product | None:
    async with async_session() as db:
        prod = await db.get(Product, prod_id)
        if prod:
            for k, v in kwargs.items():
                if v is not None:
                    setattr(prod, k, v)
            await db.commit()
            await db.refresh(prod)
        return prod


async def delete_product(prod_id: int) -> bool:
    async with async_session() as db:
        prod = await db.get(Product, prod_id)
        if prod:
            await db.delete(prod)
            await db.commit()
            return True
        return False


async def count_products() -> int:
    async with async_session() as db:
        result = await db.execute(select(func.count(Product.id)))
        return result.scalar() or 0


async def count_categories() -> int:
    async with async_session() as db:
        result = await db.execute(select(func.count(ProductCategory.id)))
        return result.scalar() or 0
