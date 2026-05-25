# Products Admin Management — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add first-class product and product-category management with admin CRUD, public list/detail pages, and audit logging.

**Architecture:** Backend follows the existing pattern (models → schemas → service → router) used by news/faq apps. Frontend admin pages follow the Vue template pattern from news.vue. Public pages use Nuxt file-based routing.

**Tech Stack:** Python/FastAPI/SQLAlchemy (backend), Vue 3/Nuxt 3 (frontend), PostgreSQL (DB)

---

### Task 1: Create product models

**Files:**
- Create: `backend/app/apps/products/__init__.py`
- Create: `backend/app/apps/products/models.py`

- [ ] **Step 1: Create package init**

```python
```

(`backend/app/apps/products/__init__.py` — empty file)

- [ ] **Step 2: Create models**

```python
from sqlalchemy import String, Text, ForeignKey, Boolean, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.models import Base, TimestampMixin


class ProductCategory(Base, TimestampMixin):
    __tablename__ = "product_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_zh: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("product_categories.id"), nullable=False)
    name_zh: Mapped[str] = mapped_column(String(300), nullable=False)
    name_en: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    cover_image_id: Mapped[int | None] = mapped_column(ForeignKey("media.id"), nullable=True)
    summary_zh: Mapped[str] = mapped_column(Text, default="")
    summary_en: Mapped[str] = mapped_column(Text, default="")
    description_zh: Mapped[str] = mapped_column(Text, default="")
    description_en: Mapped[str] = mapped_column(Text, default="")
    specs: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    images: Mapped[list | None] = mapped_column(JSON, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)

    category: Mapped["ProductCategory"] = relationship("ProductCategory", back_populates="products")
    cover_image: Mapped["Media | None"] = relationship("Media", foreign_keys=[cover_image_id])
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/apps/products/
git commit -m "feat: add Product and ProductCategory models"
```

---

### Task 2: Generate DB migration

**Files:**
- Create: `backend/alembic/versions/XXXX_add_products_tables.py`

- [ ] **Step 1: Generate migration**

```bash
cd backend && alembic revision --autogenerate -m "add_products_tables"
```

- [ ] **Step 2: Verify migration file**

Check the generated migration in `backend/alembic/versions/` — ensure it creates both `product_categories` and `products` tables with proper columns, foreign keys, and indexes.

- [ ] **Step 3: Run migration**

```bash
cd backend && alembic upgrade head
```

- [ ] **Step 4: Commit**

```bash
git add backend/alembic/versions/
git commit -m "feat: add products and product_categories migration"
```

---

### Task 3: Create Pydantic schemas

**Files:**
- Create: `backend/app/apps/products/schemas.py`

- [ ] **Step 1: Write schemas**

```python
from datetime import datetime
from pydantic import BaseModel


# --- ProductCategory ---

class ProductCategoryCreate(BaseModel):
    name_zh: str
    name_en: str
    slug: str
    sort_order: int = 0
    is_published: bool = True


class ProductCategoryUpdate(BaseModel):
    name_zh: str | None = None
    name_en: str | None = None
    slug: str | None = None
    sort_order: int | None = None
    is_published: bool | None = None


class ProductCategoryResponse(BaseModel):
    id: int
    name_zh: str
    name_en: str
    slug: str
    sort_order: int
    is_published: bool
    created_at: datetime
    updated_at: datetime
    product_count: int = 0

    model_config = {"from_attributes": True}


# --- Product ---

class ProductCreate(BaseModel):
    category_id: int
    name_zh: str
    name_en: str
    slug: str
    cover_image_id: int | None = None
    summary_zh: str = ""
    summary_en: str = ""
    description_zh: str = ""
    description_en: str = ""
    specs: list[dict] | None = None
    images: list[int] | None = None
    sort_order: int = 0
    is_published: bool = True


class ProductUpdate(BaseModel):
    category_id: int | None = None
    name_zh: str | None = None
    name_en: str | None = None
    slug: str | None = None
    cover_image_id: int | None = None
    summary_zh: str | None = None
    summary_en: str | None = None
    description_zh: str | None = None
    description_en: str | None = None
    specs: list[dict] | None = None
    images: list[int] | None = None
    sort_order: int | None = None
    is_published: bool | None = None


class ProductResponse(BaseModel):
    id: int
    category_id: int
    name_zh: str
    name_en: str
    slug: str
    cover_image_id: int | None
    summary_zh: str
    summary_en: str
    description_zh: str
    description_en: str
    specs: list[dict] | None
    images: list[int] | None
    sort_order: int
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductDetailResponse(ProductResponse):
    category: ProductCategoryResponse | None = None
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/apps/products/schemas.py
git commit -m "feat: add product and category Pydantic schemas"
```

---

### Task 4: Create service layer

**Files:**
- Create: `backend/app/apps/products/service.py`

- [ ] **Step 1: Write service**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/apps/products/service.py
git commit -m "feat: add product and category service layer"
```

---

### Task 5: Create API routers

**Files:**
- Create: `backend/app/apps/products/router.py`

- [ ] **Step 1: Write router with admin and public routes**

```python
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.apps.audit.service import create_audit_log
from app.apps.auth.router import get_current_user
from app.apps.products.schemas import (
    ProductCategoryCreate,
    ProductCategoryResponse,
    ProductCategoryUpdate,
    ProductCreate,
    ProductDetailResponse,
    ProductResponse,
    ProductUpdate,
)
from app.apps.products.service import (
    count_categories,
    count_products,
    create_category,
    create_product,
    delete_category,
    delete_product,
    get_category_by_id,
    get_category_product_count,
    get_product_by_id,
    get_product_by_slug,
    list_all_products,
    list_categories,
    list_published_products,
    update_category,
    update_product,
)

public_router = APIRouter(prefix="/api/v1", tags=["products"])

admin_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin-products"],
    dependencies=[Depends(get_current_user)],
)


# --- Helper ---

async def _category_to_response(cat) -> ProductCategoryResponse:
    count = await get_category_product_count(cat.id)
    return ProductCategoryResponse(
        id=cat.id,
        name_zh=cat.name_zh,
        name_en=cat.name_en,
        slug=cat.slug,
        sort_order=cat.sort_order,
        is_published=cat.is_published,
        created_at=cat.created_at,
        updated_at=cat.updated_at,
        product_count=count,
    )


# --- Public routes ---

@public_router.get("/product-categories")
async def public_list_categories():
    cats = await list_categories()
    return [await _category_to_response(c) for c in cats if c.is_published]


@public_router.get("/products", response_model=dict)
async def public_list_products(
    page: int = 1,
    size: int = 20,
    category: str | None = None,
):
    products, total = await list_published_products(page, size, category)
    return {
        "items": [ProductDetailResponse.model_validate(p) for p in products],
        "total": total,
        "page": page,
        "size": size,
    }


@public_router.get("/products/{slug}", response_model=ProductDetailResponse)
async def public_get_product(slug: str):
    product = await get_product_by_slug(slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# --- Admin: Category routes ---

@admin_router.get("/product-categories")
async def admin_list_categories():
    cats = await list_categories()
    return [await _category_to_response(c) for c in cats]


@admin_router.post("/product-categories", response_model=ProductCategoryResponse, status_code=201)
async def admin_create_category(
    data: ProductCategoryCreate,
    request: Request,
    current_user=Depends(get_current_user),
):
    cat = await create_category(**data.model_dump())
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="create",
        resource_type="product_category",
        resource_id=cat.id,
        resource_name=cat.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return await _category_to_response(cat)


@admin_router.put("/product-categories/{cat_id}", response_model=ProductCategoryResponse)
async def admin_update_category(
    cat_id: int,
    data: ProductCategoryUpdate,
    request: Request,
    current_user=Depends(get_current_user),
):
    cat = await update_category(cat_id, **data.model_dump(exclude_none=True))
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="product_category",
        resource_id=cat.id,
        resource_name=cat.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return await _category_to_response(cat)


@admin_router.delete("/product-categories/{cat_id}")
async def admin_delete_category(
    cat_id: int,
    request: Request,
    current_user=Depends(get_current_user),
):
    product_count = await get_category_product_count(cat_id)
    if product_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category with {product_count} existing products",
        )
    cat = await get_category_by_id(cat_id)
    name = cat.name_zh if cat else None
    deleted = await delete_category(cat_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="delete",
        resource_type="product_category",
        resource_id=cat_id,
        resource_name=name,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True}


# --- Admin: Product routes ---

@admin_router.get("/products")
async def admin_list_products(
    page: int = 1,
    size: int = 20,
    category_id: int | None = None,
):
    products, total = await list_all_products(page, size, category_id)
    return {
        "items": [ProductDetailResponse.model_validate(p) for p in products],
        "total": total,
        "page": page,
        "size": size,
    }


@admin_router.post("/products", response_model=ProductDetailResponse, status_code=201)
async def admin_create_product(
    data: ProductCreate,
    request: Request,
    current_user=Depends(get_current_user),
):
    prod = await create_product(**data.model_dump())
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="create",
        resource_type="product",
        resource_id=prod.id,
        resource_name=prod.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return await get_product_by_id(prod.id)


@admin_router.get("/products/{prod_id}", response_model=ProductDetailResponse)
async def admin_get_product(prod_id: int):
    prod = await get_product_by_id(prod_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod


@admin_router.put("/products/{prod_id}", response_model=ProductDetailResponse)
async def admin_update_product(
    prod_id: int,
    data: ProductUpdate,
    request: Request,
    current_user=Depends(get_current_user),
):
    prod = await update_product(prod_id, **data.model_dump(exclude_none=True))
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="product",
        resource_id=prod.id,
        resource_name=prod.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return await get_product_by_id(prod_id)


@admin_router.delete("/products/{prod_id}")
async def admin_delete_product(
    prod_id: int,
    request: Request,
    current_user=Depends(get_current_user),
):
    prod = await get_product_by_id(prod_id)
    name = prod.name_zh if prod else None
    deleted = await delete_product(prod_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="delete",
        resource_type="product",
        resource_id=prod_id,
        resource_name=name,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True}


# --- Admin: Stats ---

@admin_router.get("/product-stats")
async def admin_product_stats():
    return {
        "product_count": await count_products(),
        "category_count": await count_categories(),
    }
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/apps/products/router.py
git commit -m "feat: add product and category API routes"
```

---

### Task 6: Register routers in main.py

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: Add imports**

Add after the theme imports (line 23):

```python
from app.apps.products.router import public_router as products_public_router
from app.apps.products.router import admin_router as products_admin_router
```

- [ ] **Step 2: Register routers**

Add before the health endpoint (before line 60):

```python
app.include_router(products_public_router)
app.include_router(products_admin_router)
```

- [ ] **Step 3: Verify the app starts**

```bash
cd backend && python -c "from app.main import app; print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/main.py
git commit -m "feat: register products API routes"
```

---

### Task 7: Admin product categories page

**Files:**
- Create: `frontend/pages/admin/product-categories.vue`

- [ ] **Step 1: Create the page**

```vue
<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: #94a3b8;">
      &larr; 返回控制台
    </NuxtLink>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light tracking-tight mb-1" style="color: #1e293b">产品分类</h2>
        <p class="text-[13px]" style="color: #94a3b8;">管理产品分类</p>
      </div>
      <button
        @click="openCreate"
        class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all duration-200 hover:translate-y-[-1px]"
        style="background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 2px 12px rgba(5,150,105,0.2);"
      >
        新建分类
      </button>
    </div>

    <div v-if="loading" class="text-[13px] py-12 text-center" style="color: #94a3b8;">加载中...</div>

    <div v-else-if="error" class="mb-6 px-4 py-3 rounded-lg text-[13px]" style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;">
      {{ error }}
    </div>

    <template v-else>
      <div v-if="categories.length === 0" class="text-[13px] py-12 text-center" style="color: #94a3b8;">暂无分类</div>
      <div v-else class="space-y-3">
        <div
          v-for="cat in categories"
          :key="cat.id"
          class="flex items-center justify-between px-5 py-4 rounded-xl"
          style="background: #ffffff; border: 1px solid #e8f5e9;"
        >
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-3">
              <span class="text-[14px] font-medium" style="color: #1e293b">{{ cat.name_zh }}</span>
              <span class="text-[12px]" style="color: #94a3b8;">{{ cat.name_en }}</span>
              <span class="text-[11px] px-2 py-0.5 rounded-full" :style="cat.is_published ? 'background: rgba(5,150,105,0.12); color: #34d399;' : 'background: #f1f5f9; color: #94a3b8;'">{{ cat.is_published ? '已发布' : '草稿' }}</span>
            </div>
            <div class="text-[12px] mt-0.5" style="color: #94a3b8;">
              {{ cat.slug }} &middot; 排序: {{ cat.sort_order }} &middot; {{ cat.product_count }} 个产品
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0 ml-4">
            <button @click="openEdit(cat)" class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors" style="color: #34d399; background: rgba(5,150,105,0.08);">编辑</button>
            <button @click="confirmDelete(cat)" class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors" style="color: #f87171; background: rgba(239,68,68,0.08);">删除</button>
          </div>
        </div>
      </div>
    </template>

    <!-- Modal -->
    <div v-if="modalOpen" class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto py-10" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);" @click.self="modalOpen = false">
      <div class="rounded-2xl p-6 w-full max-w-lg mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <h3 class="text-[15px] font-medium mb-5" style="color: #1e293b">{{ editing ? '编辑分类' : '新建分类' }}</h3>
        <form @submit.prevent="save" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">中文名称</label>
              <input v-model="form.name_zh" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文名称</label>
              <input v-model="form.name_en" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">Slug</label>
              <input v-model="form.slug" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">排序</label>
              <input v-model.number="form.sort_order" type="number" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.is_published" type="checkbox" class="accent-emerald-600" />
            <span class="text-[12px]" style="color: #64748b;">发布</span>
          </label>
          <div v-if="formError" class="text-[12px]" style="color: #f87171;">{{ formError }}</div>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="modalOpen = false" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">取消</button>
            <button type="submit" :disabled="saving" class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all disabled:opacity-40" style="background: linear-gradient(135deg, #059669, #10b981);">{{ saving ? '保存中...' : '保存' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);" @click.self="deleteTarget = null">
      <div class="rounded-2xl p-6 w-full max-w-sm mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <p class="text-[14px] mb-1" style="color: #1e293b">确认删除</p>
        <p class="text-[12px] mb-5" style="color: #94a3b8;">确定要删除分类 "{{ deleteTarget.name_zh }}" 吗？</p>
        <div class="flex justify-end gap-3">
          <button @click="deleteTarget = null" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">取消</button>
          <button @click="doDelete" class="text-[13px] font-medium text-white border-none cursor-pointer px-4 py-2 rounded-lg" style="background: #ef4444;">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['admin-auth'] });

const { api } = useAdminApi();

interface Category {
  id: number;
  name_zh: string;
  name_en: string;
  slug: string;
  sort_order: number;
  is_published: boolean;
  product_count: number;
}

const categories = ref<Category[]>([]);
const loading = ref(true);
const error = ref('');

const fetchCategories = async () => {
  loading.value = true;
  error.value = '';
  try {
    categories.value = await api<Category[]>('/admin/product-categories');
  } catch (e: any) {
    error.value = e?.data?.detail || '加载分类列表失败';
  } finally {
    loading.value = false;
  }
};

const modalOpen = ref(false);
const saving = ref(false);
const formError = ref('');
const editing = ref<Category | null>(null);
const form = ref({ name_zh: '', name_en: '', slug: '', sort_order: 0, is_published: true });

const openCreate = () => {
  editing.value = null;
  form.value = { name_zh: '', name_en: '', slug: '', sort_order: 0, is_published: true };
  formError.value = '';
  modalOpen.value = true;
};

const openEdit = (cat: Category) => {
  editing.value = cat;
  form.value = { name_zh: cat.name_zh, name_en: cat.name_en, slug: cat.slug, sort_order: cat.sort_order, is_published: cat.is_published };
  formError.value = '';
  modalOpen.value = true;
};

const save = async () => {
  if (!form.value.name_zh || !form.value.name_en || !form.value.slug) {
    formError.value = '请填写所有必填字段';
    return;
  }
  saving.value = true;
  formError.value = '';
  try {
    if (editing.value) {
      await api(`/admin/product-categories/${editing.value.id}`, { method: 'PUT', body: form.value });
    } else {
      await api('/admin/product-categories', { method: 'POST', body: form.value });
    }
    modalOpen.value = false;
    await fetchCategories();
  } catch (e: any) {
    formError.value = e?.data?.detail || '保存失败';
  } finally {
    saving.value = false;
  }
};

const deleteTarget = ref<Category | null>(null);
const confirmDelete = (cat: Category) => { deleteTarget.value = cat; };
const doDelete = async () => {
  if (!deleteTarget.value) return;
  try {
    await api(`/admin/product-categories/${deleteTarget.value.id}`, { method: 'DELETE' });
    deleteTarget.value = null;
    await fetchCategories();
  } catch (e: any) {
    error.value = e?.data?.detail || '删除失败';
    deleteTarget.value = null;
  }
};

onMounted(fetchCategories);
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/pages/admin/product-categories.vue
git commit -m "feat: add admin product categories page"
```

---

### Task 8: Admin products page

**Files:**
- Create: `frontend/pages/admin/products.vue`

- [ ] **Step 1: Create the products management page**

```vue
<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: #94a3b8;">
      &larr; 返回控制台
    </NuxtLink>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light tracking-tight mb-1" style="color: #1e293b">产品管理</h2>
        <p class="text-[13px]" style="color: #94a3b8;">管理产品信息</p>
      </div>
      <button
        @click="openCreate"
        class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all duration-200 hover:translate-y-[-1px]"
        style="background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 2px 12px rgba(5,150,105,0.2);"
      >
        新建产品
      </button>
    </div>

    <!-- Category tabs -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button
        v-for="tab in categoryTabs"
        :key="tab.id"
        @click="selectedCategoryId = tab.id; page = 1; fetchProducts()"
        class="text-[12px] border-none cursor-pointer px-4 py-1.5 rounded-full transition-colors"
        :style="selectedCategoryId === tab.id ? 'background: rgba(5,150,105,0.12); color: #34d399;' : 'background: #f1f5f9; color: #94a3b8;'"
      >
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="text-[13px] py-12 text-center" style="color: #94a3b8;">加载中...</div>

    <div v-else-if="error" class="mb-6 px-4 py-3 rounded-lg text-[13px]" style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;">
      {{ error }}
    </div>

    <template v-else>
      <div v-if="products.length === 0" class="text-[13px] py-12 text-center" style="color: #94a3b8;">暂无产品</div>
      <div v-else class="space-y-3">
        <div
          v-for="prod in products"
          :key="prod.id"
          class="flex items-center justify-between px-5 py-4 rounded-xl"
          style="background: #ffffff; border: 1px solid #e8f5e9;"
        >
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <img
              v-if="prod.cover_image_id"
              :src="`${apiBase}/../../media/id/${prod.cover_image_id}`"
              class="w-14 h-10 rounded-md object-cover flex-shrink-0"
            />
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-3">
                <span class="text-[14px] font-medium truncate" style="color: #1e293b">{{ prod.name_zh }}</span>
                <span class="text-[12px] truncate" style="color: #94a3b8;">{{ prod.name_en }}</span>
                <span class="text-[11px] px-2 py-0.5 rounded-full" :style="prod.is_published ? 'background: rgba(5,150,105,0.12); color: #34d399;' : 'background: #f1f5f9; color: #94a3b8;'">{{ prod.is_published ? '已发布' : '草稿' }}</span>
              </div>
              <div class="text-[12px] mt-0.5" style="color: #94a3b8;">
                {{ prod.category?.name_zh || '-' }} &middot; 排序: {{ prod.sort_order }}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0 ml-4">
            <button @click="openEdit(prod)" class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors" style="color: #34d399; background: rgba(5,150,105,0.08);">编辑</button>
            <button @click="confirmDelete(prod)" class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors" style="color: #f87171; background: rgba(239,68,68,0.08);">删除</button>
          </div>
        </div>
      </div>

      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
        <button
          v-for="p in totalPages"
          :key="p"
          @click="page = p; fetchProducts()"
          class="text-[12px] border-none cursor-pointer w-8 h-8 rounded-lg transition-colors"
          :style="p === page ? 'background: rgba(5,150,105,0.15); color: #34d399;' : 'background: #f1f5f9; color: #94a3b8;'"
        >{{ p }}</button>
      </div>
    </template>

    <!-- Product Modal -->
    <div v-if="modalOpen" class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto py-10" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);" @click.self="modalOpen = false">
      <div class="rounded-2xl p-6 w-full max-w-3xl mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <h3 class="text-[15px] font-medium mb-5" style="color: #1e293b">{{ editing ? '编辑产品' : '新建产品' }}</h3>
        <form @submit.prevent="save" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">中文名称</label>
              <input v-model="form.name_zh" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文名称</label>
              <input v-model="form.name_en" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">分类</label>
              <select v-model="form.category_id" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;">
                <option :value="0" disabled>选择分类</option>
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name_zh }}</option>
              </select>
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">Slug</label>
              <input v-model="form.slug" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">排序</label>
              <input v-model.number="form.sort_order" type="number" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">封面图片</label>
            <div class="flex items-start gap-4">
              <div v-if="coverPreview" class="relative flex-shrink-0">
                <img :src="coverPreview" class="w-32 h-20 rounded-lg object-cover" />
                <button type="button" @click="removeCover" class="absolute -top-2 -right-2 w-5 h-5 rounded-full border-none cursor-pointer flex items-center justify-center text-[11px]" style="background: #ef4444; color: white;">&times;</button>
              </div>
              <label class="flex-shrink-0 w-32 h-20 rounded-lg flex flex-col items-center justify-center gap-1 cursor-pointer transition-colors border border-dashed text-[11px]" style="background: #ffffff; border-color: #d1d5db; color: #94a3b8;" :style="uploadingCover ? 'opacity: 0.5; pointer-events: none;' : ''">
                <span class="text-[16px]">&#8593;</span>
                <span>{{ uploadingCover ? '上传中...' : '点击上传' }}</span>
                <input type="file" accept="image/*" class="hidden" @change="uploadCover" :disabled="uploadingCover" />
              </label>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">中文简介</label>
              <textarea v-model="form.summary_zh" rows="2" class="w-full py-2.5 px-3 text-[13px] outline-none rounded-lg resize-y" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;"></textarea>
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文简介</label>
              <textarea v-model="form.summary_en" rows="2" class="w-full py-2.5 px-3 text-[13px] outline-none rounded-lg resize-y" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;"></textarea>
            </div>
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">中文详情</label>
            <textarea v-model="form.description_zh" rows="4" class="w-full py-2.5 px-3 text-[13px] outline-none rounded-lg resize-y" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;"></textarea>
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文详情</label>
            <textarea v-model="form.description_en" rows="4" class="w-full py-2.5 px-3 text-[13px] outline-none rounded-lg resize-y" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;"></textarea>
          </div>
          <!-- Specs editor -->
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">规格参数</label>
            <div class="space-y-2">
              <div v-for="(spec, i) in form.specs" :key="i" class="flex gap-2 items-center">
                <input v-model="spec.key" placeholder="参数名" class="flex-1 py-2 px-3 text-[13px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
                <input v-model="spec.value" placeholder="参数值" class="flex-1 py-2 px-3 text-[13px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
                <button type="button" @click="form.specs.splice(i, 1)" class="border-none cursor-pointer px-2 py-1 rounded text-[12px]" style="color: #f87171; background: rgba(239,68,68,0.08);">删除</button>
              </div>
              <button type="button" @click="form.specs.push({ key: '', value: '' })" class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg" style="color: #34d399; background: rgba(5,150,105,0.08);">+ 添加参数</button>
            </div>
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.is_published" type="checkbox" class="accent-emerald-600" />
            <span class="text-[12px]" style="color: #64748b;">发布</span>
          </label>
          <div v-if="formError" class="text-[12px]" style="color: #f87171;">{{ formError }}</div>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="modalOpen = false" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">取消</button>
            <button type="submit" :disabled="saving" class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all disabled:opacity-40" style="background: linear-gradient(135deg, #059669, #10b981);">{{ saving ? '保存中...' : '保存' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);" @click.self="deleteTarget = null">
      <div class="rounded-2xl p-6 w-full max-w-sm mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <p class="text-[14px] mb-1" style="color: #1e293b">确认删除</p>
        <p class="text-[12px] mb-5" style="color: #94a3b8;">确定要删除产品 "{{ deleteTarget.name_zh }}" 吗？</p>
        <div class="flex justify-end gap-3">
          <button @click="deleteTarget = null" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">取消</button>
          <button @click="doDelete" class="text-[13px] font-medium text-white border-none cursor-pointer px-4 py-2 rounded-lg" style="background: #ef4444;">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['admin-auth'] });

const { api, apiBase } = useAdminApi();

interface Category {
  id: number;
  name_zh: string;
  name_en: string;
  slug: string;
  sort_order: number;
  is_published: boolean;
}

interface ProductItem {
  id: number;
  category_id: number;
  name_zh: string;
  name_en: string;
  slug: string;
  cover_image_id: number | null;
  summary_zh: string;
  summary_en: string;
  description_zh: string;
  description_en: string;
  specs: { key: string; value: string }[] | null;
  images: number[] | null;
  sort_order: number;
  is_published: boolean;
  category: Category | null;
}

const products = ref<ProductItem[]>([]);
const categories = ref<Category[]>([]);
const loading = ref(true);
const error = ref('');
const page = ref(1);
const totalPages = ref(1);
const selectedCategoryId = ref<number | null>(null);

const categoryTabs = computed(() => {
  const tabs: { id: number | null; label: string }[] = [{ id: null, label: '全部' }];
  for (const c of categories.value) {
    tabs.push({ id: c.id, label: c.name_zh });
  }
  return tabs;
});

const fetchCategories = async () => {
  try {
    categories.value = await api<Category[]>('/admin/product-categories');
  } catch {}
};

const fetchProducts = async () => {
  loading.value = true;
  error.value = '';
  try {
    const params = new URLSearchParams({ page: String(page.value), size: '20' });
    if (selectedCategoryId.value) params.set('category_id', String(selectedCategoryId.value));
    const data = await api<{ items: ProductItem[]; total: number; page: number; size: number }>(`/admin/products?${params}`);
    products.value = data.items;
    totalPages.value = Math.ceil(data.total / data.size);
  } catch (e: any) {
    error.value = e?.data?.detail || '加载产品列表失败';
  } finally {
    loading.value = false;
  }
};

const modalOpen = ref(false);
const saving = ref(false);
const formError = ref('');
const editing = ref<ProductItem | null>(null);
const form = ref({
  category_id: 0,
  name_zh: '',
  name_en: '',
  slug: '',
  cover_image_id: null as number | null,
  summary_zh: '',
  summary_en: '',
  description_zh: '',
  description_en: '',
  specs: [] as { key: string; value: string }[],
  images: [] as number[],
  sort_order: 0,
  is_published: true,
});

const coverPreview = ref<string | null>(null);
const uploadingCover = ref(false);

const uploadCover = async (e: Event) => {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  uploadingCover.value = true;
  try {
    const fd = new FormData();
    fd.append('file', file);
    const res = await api<{ id: number; url: string }>('/admin/media/upload', { method: 'POST', body: fd });
    form.value.cover_image_id = res.id;
    coverPreview.value = `${apiBase}/../../media/id/${res.id}`;
  } catch {
    formError.value = '封面上传失败';
  } finally {
    uploadingCover.value = false;
    input.value = '';
  }
};

const removeCover = () => {
  form.value.cover_image_id = null;
  coverPreview.value = null;
};

const resetForm = () => {
  form.value = { category_id: 0, name_zh: '', name_en: '', slug: '', cover_image_id: null, summary_zh: '', summary_en: '', description_zh: '', description_en: '', specs: [], images: [], sort_order: 0, is_published: true };
  coverPreview.value = null;
  formError.value = '';
};

const openCreate = () => {
  editing.value = null;
  resetForm();
  modalOpen.value = true;
};

const openEdit = (prod: ProductItem) => {
  editing.value = prod;
  coverPreview.value = prod.cover_image_id ? `${apiBase}/../../media/id/${prod.cover_image_id}` : null;
  form.value = {
    category_id: prod.category_id,
    name_zh: prod.name_zh,
    name_en: prod.name_en,
    slug: prod.slug,
    cover_image_id: prod.cover_image_id,
    summary_zh: prod.summary_zh || '',
    summary_en: prod.summary_en || '',
    description_zh: prod.description_zh || '',
    description_en: prod.description_en || '',
    specs: prod.specs ? [...prod.specs] : [],
    images: prod.images ? [...prod.images] : [],
    sort_order: prod.sort_order,
    is_published: prod.is_published,
  };
  formError.value = '';
  modalOpen.value = true;
};

const save = async () => {
  if (!form.value.name_zh || !form.value.name_en || !form.value.slug || !form.value.category_id) {
    formError.value = '请填写所有必填字段';
    return;
  }
  saving.value = true;
  formError.value = '';
  const body: any = { ...form.value, specs: form.value.specs.length > 0 ? form.value.specs : null, images: form.value.images.length > 0 ? form.value.images : null };
  try {
    if (editing.value) {
      await api(`/admin/products/${editing.value.id}`, { method: 'PUT', body });
    } else {
      await api('/admin/products', { method: 'POST', body });
    }
    modalOpen.value = false;
    await fetchProducts();
  } catch (e: any) {
    formError.value = e?.data?.detail || '保存失败';
  } finally {
    saving.value = false;
  }
};

const deleteTarget = ref<ProductItem | null>(null);
const confirmDelete = (prod: ProductItem) => { deleteTarget.value = prod; };
const doDelete = async () => {
  if (!deleteTarget.value) return;
  try {
    await api(`/admin/products/${deleteTarget.value.id}`, { method: 'DELETE' });
    deleteTarget.value = null;
    await fetchProducts();
  } catch {}
};

onMounted(async () => {
  await fetchCategories();
  await fetchProducts();
});
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/pages/admin/products.vue
git commit -m "feat: add admin products management page"
```

---

### Task 9: Update admin dashboard

**Files:**
- Modify: `frontend/pages/admin/index.vue`

- [ ] **Step 1: Add product/category stats and quick links**

Update the stats computed property to add product and category counts:

```typescript
const productCount = ref<number | null>(null);
const categoryCount = ref<number | null>(null);

const stats = computed(() => [
  { label: '页面', value: pageCount.value !== null ? String(pageCount.value) : '—' },
  { label: '新闻', value: newsCount.value !== null ? String(newsCount.value) : '—' },
  { label: '咨询', value: inquiryCount.value !== null ? String(inquiryCount.value) : '—' },
  { label: '产品', value: productCount.value !== null ? String(productCount.value) : '—' },
]);
```

Add product stats fetch in onMounted:

```typescript
try {
  const productStats = await api<{ product_count: number; category_count: number }>('/admin/product-stats');
  productCount.value = productStats.product_count;
  categoryCount.value = productStats.category_count;
} catch {}
```

Update links array to add product management entries:

```typescript
{ to: '/admin/products', label: '产品管理', desc: '管理产品信息和分类' },
{ to: '/admin/product-categories', label: '产品分类', desc: '管理产品分类' },
```

Update the grid to 4 columns (md:grid-cols-4) for stats, and add product links to the quick links grid.

- [ ] **Step 2: Full updated script section reference**

The complete script section becomes:

```typescript
definePageMeta({
  layout: 'admin',
  middleware: ['admin-auth'],
});

const { api, getHeaders } = useAdminApi();

const pageCount = ref<number | null>(null);
const newsCount = ref<number | null>(null);
const inquiryCount = ref<number | null>(null);
const productCount = ref<number | null>(null);

const stats = computed(() => [
  { label: '页面', value: pageCount.value !== null ? String(pageCount.value) : '—' },
  { label: '新闻', value: newsCount.value !== null ? String(newsCount.value) : '—' },
  { label: '咨询', value: inquiryCount.value !== null ? String(inquiryCount.value) : '—' },
  { label: '产品', value: productCount.value !== null ? String(productCount.value) : '—' },
]);

onMounted(async () => {
  try {
    const pages = await api<any[]>('/admin/pages');
    pageCount.value = Array.isArray(pages) ? pages.length : 0;
  } catch {}
  try {
    const newsData = await api<{ total: number }>('/admin/news?page=1&size=1');
    newsCount.value = newsData.total;
  } catch {}
  try {
    const inquiryData = await api<{ total: number }>('/admin/inquiries?page=1&size=1');
    inquiryCount.value = inquiryData.total;
  } catch {}
  try {
    const productStats = await api<{ product_count: number; category_count: number }>('/admin/product-stats');
    productCount.value = productStats.product_count;
  } catch {}
});

const links = [
  { to: '/admin/pages', label: '页面管理', desc: '编辑网站页面和内容区块' },
  { to: '/admin/news', label: '新闻管理', desc: '发布和管理新闻文章' },
  { to: '/admin/products', label: '产品管理', desc: '管理产品信息和分类' },
  { to: '/admin/product-categories', label: '产品分类', desc: '管理产品分类' },
  { to: '/admin/media', label: '媒体管理', desc: '上传和管理图片、视频等媒体资源' },
  { to: '/admin/menus', label: '菜单管理', desc: '配置导航菜单结构' },
  { to: '/admin/users', label: '用户管理', desc: '管理后台管理员和编辑者账号' },
  { to: '/admin/inquiries', label: '咨询管理', desc: '查看用户提交的咨询' },
  { to: '/admin/audit-logs', label: '审计日志', desc: '查看管理员操作记录' },
  { to: '/admin/settings', label: '系统设置', desc: '配置 LLM、站点信息等系统参数' },
];
```

Also update the template grid classes: change `md:grid-cols-3` to `md:grid-cols-4` for stats.

- [ ] **Step 3: Commit**

```bash
git add frontend/pages/admin/index.vue
git commit -m "feat: add product stats and links to admin dashboard"
```

---

### Task 10: Public product list page

**Files:**
- Create: `frontend/pages/products/index.vue`

- [ ] **Step 1: Create public product list page**

```vue
<template>
  <div class="min-h-screen" style="background: #f8fafc;">
    <div class="max-w-7xl mx-auto px-4 py-12">
      <h1 class="text-3xl font-light tracking-tight mb-2" style="color: #1e293b">产品中心</h1>
      <p class="text-[14px] mb-8" style="color: #94a3b8;">探索我们的产品与解决方案</p>

      <!-- Category tabs -->
      <div class="flex flex-wrap gap-3 mb-8">
        <button
          v-for="tab in tabs"
          :key="tab.slug"
          @click="activeCategory = tab.slug; page = 1; fetchProducts()"
          class="text-[13px] border-none cursor-pointer px-5 py-2 rounded-full transition-colors"
          :style="activeCategory === tab.slug ? 'background: rgba(5,150,105,0.12); color: #34d399;' : 'background: #ffffff; color: #94a3b8; border: 1px solid #e2e8f0;'"
        >
          {{ tab.name_zh }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-[14px] py-20 text-center" style="color: #94a3b8;">加载中...</div>

      <!-- Empty -->
      <div v-else-if="products.length === 0" class="text-[14px] py-20 text-center" style="color: #94a3b8;">暂无产品</div>

      <!-- Product grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <NuxtLink
          v-for="prod in products"
          :key="prod.id"
          :to="`/products/${prod.slug}`"
          class="rounded-xl overflow-hidden no-underline transition-all duration-200 hover:translate-y-[-2px] block"
          style="background: #ffffff; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.04);"
        >
          <div class="h-48 overflow-hidden" style="background: #f1f5f9;">
            <img
              v-if="prod.cover_image_id"
              :src="`${apiBase}/../../media/id/${prod.cover_image_id}`"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-[12px]" style="color: #94a3b8;">暂无图片</div>
          </div>
          <div class="p-5">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-[11px] px-2 py-0.5 rounded-full" style="background: rgba(5,150,105,0.08); color: #34d399;">{{ prod.category?.name_zh }}</span>
            </div>
            <h3 class="text-[16px] font-medium mb-2" style="color: #1e293b">{{ prod.name_zh }}</h3>
            <p class="text-[13px] leading-relaxed line-clamp-2" style="color: #94a3b8;">{{ prod.summary_zh }}</p>
          </div>
        </NuxtLink>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-10">
        <button
          v-for="p in totalPages"
          :key="p"
          @click="page = p; fetchProducts()"
          class="text-[13px] border-none cursor-pointer w-9 h-9 rounded-lg transition-colors"
          :style="p === page ? 'background: rgba(5,150,105,0.15); color: #34d399;' : 'background: #ffffff; color: #94a3b8; border: 1px solid #e2e8f0;'"
        >{{ p }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const apiBase = config.public.apiBase as string;

interface Category {
  id: number;
  name_zh: string;
  name_en: string;
  slug: string;
}

interface ProductItem {
  id: number;
  name_zh: string;
  slug: string;
  cover_image_id: number | null;
  summary_zh: string;
  category: Category | null;
}

const tabs = ref<(Category & { slug: string })[]>([{ id: 0, name_zh: '全部', name_en: 'All', slug: '' }]);
const activeCategory = ref('');
const products = ref<ProductItem[]>([]);
const loading = ref(true);
const page = ref(1);
const totalPages = ref(1);

const fetchCategories = async () => {
  try {
    const cats = await $fetch<Category[]>(`${apiBase}/product-categories`);
    tabs.value = [{ id: 0, name_zh: '全部', name_en: 'All', slug: '' }, ...cats];
  } catch {}
};

const fetchProducts = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams({ page: String(page.value), size: '12' });
    if (activeCategory.value) params.set('category', activeCategory.value);
    const data = await $fetch<{ items: ProductItem[]; total: number; size: number }>(`${apiBase}/products?${params}`);
    products.value = data.items;
    totalPages.value = Math.ceil(data.total / data.size);
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await fetchCategories();
  await fetchProducts();
});
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/pages/products/
git commit -m "feat: add public products list page"
```

---

### Task 11: Public product detail page

**Files:**
- Create: `frontend/pages/products/[id].vue`

- [ ] **Step 1: Create product detail page**

```vue
<template>
  <div class="min-h-screen" style="background: #f8fafc;">
    <div v-if="loading" class="text-[14px] py-20 text-center" style="color: #94a3b8;">加载中...</div>

    <div v-else-if="error" class="text-[14px] py-20 text-center" style="color: #f87171;">{{ error }}</div>

    <template v-else-if="product">
      <!-- Breadcrumb -->
      <div class="max-w-5xl mx-auto px-4 py-6">
        <div class="flex items-center gap-2 text-[12px]" style="color: #94a3b8;">
          <NuxtLink to="/" class="no-underline hover:opacity-70" style="color: #94a3b8;">首页</NuxtLink>
          <span>/</span>
          <NuxtLink to="/products" class="no-underline hover:opacity-70" style="color: #94a3b8;">产品中心</NuxtLink>
          <span v-if="product.category">/</span>
          <span v-if="product.category" style="color: #34d399;">{{ product.category.name_zh }}</span>
          <span>/</span>
          <span style="color: #64748b;">{{ product.name_zh }}</span>
        </div>
      </div>

      <!-- Hero -->
      <div class="max-w-5xl mx-auto px-4 pb-8">
        <div class="rounded-2xl overflow-hidden" style="background: #ffffff; border: 1px solid #e2e8f0;">
          <div class="grid grid-cols-1 md:grid-cols-2">
            <div class="h-72 md:h-auto overflow-hidden" style="background: #f1f5f9;">
              <img
                v-if="product.cover_image_id"
                :src="`${apiBase}/../../media/id/${product.cover_image_id}`"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-[14px]" style="color: #94a3b8;">暂无图片</div>
            </div>
            <div class="p-8 flex flex-col justify-center">
              <span v-if="product.category" class="text-[11px] px-2 py-1 rounded-full mb-3 self-start" style="background: rgba(5,150,105,0.08); color: #34d399;">{{ product.category.name_zh }}</span>
              <h1 class="text-2xl font-light tracking-tight mb-3" style="color: #1e293b">{{ product.name_zh }}</h1>
              <p class="text-[14px] leading-relaxed" style="color: #64748b;">{{ product.summary_zh }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Specs -->
      <div v-if="product.specs && product.specs.length > 0" class="max-w-5xl mx-auto px-4 pb-8">
        <h2 class="text-[16px] font-medium mb-4" style="color: #1e293b">规格参数</h2>
        <div class="rounded-xl overflow-hidden" style="background: #ffffff; border: 1px solid #e2e8f0;">
          <table class="w-full text-[14px]">
            <tbody>
              <tr v-for="(spec, i) in product.specs" :key="i" :style="i % 2 === 0 ? 'background: #ffffff;' : 'background: #f8fafc;'">
                <td class="px-5 py-3 w-48" style="color: #94a3b8;">{{ spec.key }}</td>
                <td class="px-5 py-3" style="color: #1e293b;">{{ spec.value }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Description -->
      <div v-if="product.description_zh" class="max-w-5xl mx-auto px-4 pb-12">
        <h2 class="text-[16px] font-medium mb-4" style="color: #1e293b">产品详情</h2>
        <div class="rounded-xl p-6 text-[14px] leading-relaxed" style="background: #ffffff; border: 1px solid #e2e8f0; color: #334155;" v-html="product.description_zh.replace(/\n/g, '<br/>')">
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const apiBase = config.public.apiBase as string;
const route = useRoute();

interface Category {
  id: number;
  name_zh: string;
}

interface ProductDetail {
  id: number;
  name_zh: string;
  slug: string;
  cover_image_id: number | null;
  summary_zh: string;
  description_zh: string;
  specs: { key: string; value: string }[] | null;
  category: Category | null;
}

const product = ref<ProductDetail | null>(null);
const loading = ref(true);
const error = ref('');

const fetchProduct = async () => {
  loading.value = true;
  error.value = '';
  try {
    product.value = await $fetch<ProductDetail>(`${apiBase}/products/${route.params.id}`);
  } catch (e: any) {
    error.value = e?.data?.detail || '产品不存在';
  } finally {
    loading.value = false;
  }
};

onMounted(fetchProduct);
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/pages/products/
git commit -m "feat: add public product detail page"
```

---

### Task 12: Backend tests

**Files:**
- Create: `backend/tests/test_products/__init__.py`
- Create: `backend/tests/test_products/test_service.py`

- [ ] **Step 1: Write service tests**

```python
import pytest
from app.apps.products.service import (
    create_category,
    create_product,
    delete_category,
    delete_product,
    get_category_by_id,
    get_product_by_id,
    get_product_by_slug,
    list_all_products,
    list_categories,
    list_published_products,
    update_category,
    update_product,
)


@pytest.mark.asyncio
async def test_create_and_list_categories():
    cat = await create_category(name_zh="软件产品", name_en="Software", slug="software", sort_order=1)
    assert cat.id is not None
    assert cat.name_zh == "软件产品"

    cats = await list_categories()
    assert len(cats) > 0

    found = await get_category_by_id(cat.id)
    assert found is not None
    assert found.slug == "software"


@pytest.mark.asyncio
async def test_update_category():
    cat = await create_category(name_zh="硬件", name_en="Hardware", slug="hardware", sort_order=2)
    updated = await update_category(cat.id, name_zh="硬件产品")
    assert updated.name_zh == "硬件产品"

    await delete_category(cat.id)
    assert await get_category_by_id(cat.id) is None


@pytest.mark.asyncio
async def test_create_and_get_product():
    cat = await create_category(name_zh="软件", name_en="Software", slug="sw", sort_order=1)
    prod = await create_product(
        category_id=cat.id,
        name_zh="智能楼宇系统",
        name_en="Smart Building System",
        slug="smart-building",
        is_published=True,
    )
    assert prod.id is not None

    found = await get_product_by_id(prod.id)
    assert found is not None
    assert found.name_zh == "智能楼宇系统"

    found_slug = await get_product_by_slug("smart-building")
    assert found_slug is not None

    await delete_product(prod.id)
    await delete_category(cat.id)


@pytest.mark.asyncio
async def test_list_published_products():
    cat = await create_category(name_zh="测试", name_en="Test", slug="test", sort_order=1)
    p1 = await create_product(category_id=cat.id, name_zh="已发布", name_en="Pub", slug="pub", is_published=True)
    p2 = await create_product(category_id=cat.id, name_zh="草稿", name_en="Draft", slug="draft", is_published=False)

    products, total = await list_published_products()
    ids = [p.id for p in products]
    assert p1.id in ids
    assert p2.id not in ids

    await delete_product(p1.id)
    await delete_product(p2.id)
    await delete_category(cat.id)


@pytest.mark.asyncio
async def test_delete_category_with_products_blocked():
    cat = await create_category(name_zh="有产品", name_en="Has Products", slug="has", sort_order=1)
    prod = await create_product(category_id=cat.id, name_zh="产品", name_en="P", slug="p1")

    from app.apps.products.service import get_category_product_count
    count = await get_category_product_count(cat.id)
    assert count >= 1

    await delete_product(prod.id)
    await delete_category(cat.id)
```

- [ ] **Step 2: Run tests**

```bash
cd backend && pytest tests/test_products/ -v
```

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_products/
git commit -m "test: add product and category service tests"
```

---

### Task 13: Final verification and cleanup

- [ ] **Step 1: Run all backend tests**

```bash
cd backend && pytest -v
```

Expected: all tests pass.

- [ ] **Step 2: Verify backend starts cleanly**

```bash
cd backend && python -c "from app.main import app; print('Routes:', len(app.routes))"
```

- [ ] **Step 3: Build frontend to check no compile errors**

```bash
cd frontend && npx nuxi build --prerender 2>&1 | tail -20
```

- [ ] **Step 4: Commit any remaining changes**

```bash
git add -A
git commit -m "chore: final verification of products feature"
```
