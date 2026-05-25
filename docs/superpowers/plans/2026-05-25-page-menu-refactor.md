# Page-Menu Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make CMS pages the canonical registry of all frontend routes. Add `type` to pages, `page_id` FK to menus, replace hardcoded Vue pages with a single `[...slug].vue` catch-all route.

**Architecture:** Pages gain a `type` enum (content/news/products/faq/contact). A `[...slug].vue` catch-all route handles all CMS pages, reading `page.type` to decide rendering mode. Menus link to pages via `page_id` FK. Six page-level components are extracted from the deleted hardcoded pages. All existing public API endpoints (news, products, faqs, inquiries) remain unchanged.

**Tech Stack:** FastAPI + SQLAlchemy async, Nuxt 3 catch-all route, Vue 3 Composition API

---

### Task 1: DB migration — add type to pages, page_id to menus

**Files:**
- Create: `backend/alembic/versions/<auto>_add_page_type_and_menu_page_id.py`
- Modify: `backend/app/apps/cms/models.py`

- [ ] **Step 1: Add `type` field to Page model**

In `backend/app/apps/cms/models.py:30-41`, add the type column to the Page class:

```python
class Page(Base, TimestampMixin):
    __tablename__ = "pages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_zh: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="content")
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    blocks: Mapped[list["Block"]] = relationship(
        "Block", back_populates="page", order_by="Block.order",
        cascade="all, delete-orphan"
    )
```

- [ ] **Step 2: Add `page_id` field to Menu model**

In `backend/app/apps/cms/models.py:55-67`, add page_id FK to the Menu class:

```python
class Menu(Base, TimestampMixin):
    __tablename__ = "menus"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("menus.id", ondelete="SET NULL"), nullable=True)
    name_zh: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    link: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    page_id: Mapped[int | None] = mapped_column(ForeignKey("pages.id"), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    location: Mapped[str] = mapped_column(String(20), nullable=False, default="header")
    parent: Mapped["Menu | None"] = relationship("Menu", remote_side=[id], back_populates="children")
    children: Mapped[list["Menu"]] = relationship("Menu", back_populates="parent")
    page: Mapped["Page | None"] = relationship("Page")
```

- [ ] **Step 3: Generate and run alembic migration**

Run:
```bash
cd backend && source .venv/bin/activate && alembic revision --autogenerate -m "add_page_type_and_menu_page_id"
```

Then:
```bash
cd backend && source .venv/bin/activate && alembic upgrade head
```

Expected: migration created and applied without errors, new columns exist in DB.

- [ ] **Step 4: Commit**

```bash
git add backend/app/apps/cms/models.py backend/alembic/versions/*add_page_type*.py
git commit -m "feat: add type column to pages, page_id FK to menus"
```

---

### Task 2: Backend — page schemas, service, API for type

**Files:**
- Modify: `backend/app/apps/cms/schemas.py`
- Modify: `backend/app/apps/cms/service_page.py`
- Modify: `backend/app/apps/cms/router.py`

- [ ] **Step 1: Update page schemas**

In `backend/app/apps/cms/schemas.py`, update `PageCreate` to accept type, add `PageUpdate`, and add `type` to `PageOut`:

```python
from pydantic import BaseModel

VALID_PAGE_TYPES = {"content", "news", "products", "faq", "contact"}

class PageCreate(BaseModel):
    name_zh: str
    name_en: str
    slug: str
    type: str = "content"


class PageUpdate(BaseModel):
    name_zh: str | None = None
    name_en: str | None = None
    slug: str | None = None
    type: str | None = None


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
    type: str
    blocks: list[BlockOut]

    model_config = {"from_attributes": True}


class PageSlugOut(BaseModel):
    slug: str
    type: str
```

- [ ] **Step 2: Update page service for type**

In `backend/app/apps/cms/service_page.py`, update `create_page` to accept `type`:

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import async_session
from app.apps.cms.models import Page


async def create_page(name_zh: str, name_en: str, slug: str, type: str = "content", is_published: bool = False) -> Page:
    async with async_session() as db:
        page = Page(name_zh=name_zh, name_en=name_en, slug=slug, type=type, is_published=is_published)
        db.add(page)
        await db.commit()
        await db.refresh(page)
        return page


async def get_page_by_slug(slug: str) -> Page | None:
    async with async_session() as db:
        result = await db.execute(
            select(Page)
            .where(Page.slug == slug, Page.is_published == True)
            .options(selectinload(Page.blocks))
        )
        return result.scalar_one_or_none()


async def get_page_by_id(page_id: int) -> Page | None:
    async with async_session() as db:
        return await db.get(Page, page_id)


async def list_pages() -> list[Page]:
    async with async_session() as db:
        result = await db.execute(select(Page).order_by(Page.id))
        return result.scalars().all()


async def list_published_page_slugs() -> list[dict]:
    async with async_session() as db:
        result = await db.execute(
            select(Page.slug, Page.type).where(Page.is_published == True).order_by(Page.id)
        )
        return [{"slug": row[0], "type": row[1]} for row in result.all()]


async def update_page(page_id: int, **kwargs) -> Page | None:
    async with async_session() as db:
        page = await db.get(Page, page_id)
        if page:
            for k, v in kwargs.items():
                if v is not None:
                    setattr(page, k, v)
            await db.commit()
            await db.refresh(page)
        return page


async def delete_page(page_id: int) -> bool:
    async with async_session() as db:
        page = await db.get(Page, page_id)
        if page:
            await db.delete(page)
            await db.commit()
            return True
        return False
```

- [ ] **Step 3: Update page API endpoints and add /pages/slugs**

In `backend/app/apps/cms/router.py`, update the admin page list/create/update endpoints:

Add import for `PageUpdate`:
```python
from app.apps.cms.schemas import BlockCreate, BlockUpdate, PageCreate, PageUpdate, PageOut, PageSlugOut, ReorderRequest
```

Add import for `list_published_page_slugs`:
```python
from app.apps.cms.service_page import create_page, get_page_by_id, get_page_by_slug, list_pages, list_published_page_slugs, update_page, delete_page as svc_delete_page
```

Add `type` to admin_list_pages response (line 119-128):
```python
@page_admin_router.get("/pages")
async def admin_list_pages():
    pages = await list_pages()
    return [
        {
            "id": p.id,
            "name_zh": p.name_zh,
            "name_en": p.name_en,
            "slug": p.slug,
            "type": p.type,
            "is_published": p.is_published,
        }
        for p in pages
    ]
```

Update admin_create_page (line 131-154) — accept `type` from PageCreate which now has field `type`:

Change `data: PageCreate` signature stays same, but `create_page(**data.model_dump())` now includes `type`. No code change needed since PageCreate already has the type field with default.

Update admin_update_page (line 157-176) — use `PageUpdate` instead of `PageCreate`:
```python
@page_admin_router.put("/pages/{page_id}")
async def admin_update_page(
    page_id: int,
    data: PageUpdate,
    request: Request,
    current_user=Depends(get_current_user),
):
    page = await update_page(page_id, **data.model_dump(exclude_none=True))
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="page",
        resource_id=page.id,
        resource_name=data.name_zh or page.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return {"id": page.id, "slug": page.slug}
```

Add `GET /pages/slugs` public endpoint after the existing `get_page` endpoint:
```python
@public_router.get("/pages/slugs", response_model=list[PageSlugOut])
async def get_page_slugs():
    return await list_published_page_slugs()
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/apps/cms/schemas.py backend/app/apps/cms/service_page.py backend/app/apps/cms/router.py
git commit -m "feat: add page type to schemas, service, and admin API; add /pages/slugs endpoint"
```

---

### Task 3: Backend — menu schemas, service, API with page_id

**Files:**
- Modify: `backend/app/apps/cms/schemas.py`
- Modify: `backend/app/apps/cms/service_menu.py`
- Modify: `backend/app/apps/cms/router.py`

- [ ] **Step 1: Update menu service for page_id**

In `backend/app/apps/cms/service_menu.py`, update `create_menu_item` to accept `page_id`, and update `get_menu_tree` to include `page_slug`:

```python
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.apps.cms.models import Menu
from app.core.database import async_session


async def create_menu_item(
    name_zh: str,
    name_en: str,
    link: str = "",
    page_id: int | None = None,
    location: str = "header",
    order: int = 0,
    parent_id: int | None = None,
    icon: str | None = None,
) -> Menu:
    async with async_session() as db:
        menu = Menu(
            name_zh=name_zh,
            name_en=name_en,
            link=link,
            page_id=page_id,
            location=location,
            order=order,
            parent_id=parent_id,
            icon=icon,
        )
        db.add(menu)
        await db.commit()
        await db.refresh(menu)
        return menu


async def get_menu_tree(location: str | None = None) -> list[dict]:
    async with async_session() as db:
        from app.apps.cms.models import Page
        q = select(Menu).where(Menu.is_visible == True)
        if location:
            q = q.where(Menu.location == location)
        q = q.order_by(Menu.order)
        result = await db.execute(q)
        items = result.scalars().all()

    by_id: dict[int, dict] = {}
    for m in items:
        by_id[m.id] = {
            "id": m.id,
            "name_zh": m.name_zh,
            "name_en": m.name_en,
            "link": m.link,
            "page_id": m.page_id,
            "page_slug": None,
            "icon": m.icon,
            "children": [],
        }

    # Resolve page_slug for items with page_id
    if items:
        async with async_session() as db:
            page_ids = [m.page_id for m in items if m.page_id]
            if page_ids:
                page_result = await db.execute(
                    select(Page.id, Page.slug).where(Page.id.in_(page_ids))
                )
                slug_map = {row[0]: row[1] for row in page_result.all()}
                for m in items:
                    if m.page_id and m.page_id in slug_map:
                        by_id[m.id]["page_slug"] = slug_map[m.page_id]

    tree: list[dict] = []
    for m in items:
        node = by_id[m.id]
        if m.parent_id and m.parent_id in by_id:
            by_id[m.parent_id]["children"].append(node)
        else:
            tree.append(node)
    return tree


async def update_menu_item(menu_id: int, **kwargs) -> Menu | None:
    async with async_session() as db:
        menu = await db.get(Menu, menu_id)
        if menu:
            for k, v in kwargs.items():
                if v is not None:
                    setattr(menu, k, v)
            await db.commit()
            await db.refresh(menu)
        return menu


async def delete_menu_item(menu_id: int) -> bool:
    async with async_session() as db:
        menu = await db.get(Menu, menu_id)
        if menu:
            await db.delete(menu)
            await db.commit()
            return True
        return False
```

Note: The page_slug resolution uses a separate DB session after the first one is closed. This works because `async_session` creates a new session each time.

- [ ] **Step 2: No router changes needed for menus**

The menu admin create/update endpoints already accept `data: dict` and pass kwargs through. Since `page_id` is now a valid keyword arg in `create_menu_item` and `update_menu_item`, no router changes are needed.

- [ ] **Step 3: Commit**

```bash
git add backend/app/apps/cms/service_menu.py
git commit -m "feat: add page_id FK support to menu service; include page_slug in menu tree"
```

---

### Task 4: Backend — seed data and menu data migration

**Files:**
- Modify: `backend/seed.py`

- [ ] **Step 1: Write a data migration script**

Create/update seed logic to:
1. Update existing pages: contact → type=contact, products → type=products
2. Create news page (slug=news, type=news, is_published=True)
3. Create faq page (slug=faq, type=faq, is_published=True)
4. Migrate menu links to page_id

Add to `backend/seed.py` after the existing seed code:

```python
async def migrate_pages_and_menus():
    """One-shot migration: add types, create new pages, link menus to pages."""
    from app.apps.cms.service_page import create_page, update_page, list_pages
    from app.apps.cms.service_menu import update_menu_item, get_menu_tree
    from app.apps.cms.models import Page, Menu

    pages = await list_pages()

    # Update existing pages to correct types
    type_map = {"contact": "contact", "products": "products"}
    for p in pages:
        if p.slug in type_map:
            await update_page(p.id, type=type_map[p.slug])

    # Create news and faq pages if they don't exist
    existing_slugs = {p.slug for p in pages}
    if "news" not in existing_slugs:
        await create_page(name_zh="新闻中心", name_en="News", slug="news", type="news", is_published=True)
    if "faq" not in existing_slugs:
        await create_page(name_zh="常见问题", name_en="FAQ", slug="faq", type="faq", is_published=True)

    # Migrate menu link -> page_id
    # Re-fetch pages after creation
    pages_after = await list_pages()
    slug_to_id = {p.slug: p.id for p in pages_after}
    slug_to_id["home"] = slug_to_id.get("home")  # ensure home is mapped

    async with async_session() as db:
        from sqlalchemy import select
        result = await db.execute(select(Menu))
        menus = result.scalars().all()
        for menu in menus:
            if menu.link and not menu.page_id:
                # Extract slug from link like "/about" -> "about", "/" -> "home"
                if menu.link == "/":
                    slug = "home"
                else:
                    slug = menu.link.lstrip("/")
                if slug in slug_to_id:
                    menu.page_id = slug_to_id[slug]
        await db.commit()

    print("Migration complete: page types updated, news/faq pages created, menu links resolved.")
```

Run:
```bash
cd backend && source .venv/bin/activate && python -c "import asyncio; from seed import migrate_pages_and_menus; asyncio.run(migrate_pages_and_menus())"
```

- [ ] **Step 2: Commit**

```bash
git add backend/seed.py
git commit -m "feat: seed data migration for page types and menu page_id linkage"
```

---

### Task 5: Frontend — NewsArticleList component

**Files:**
- Create: `frontend/components/blocks/NewsArticleList.vue`

This replaces `pages/news/index.vue`. It renders a full-page news list with pagination.

- [ ] **Step 1: Create NewsArticleList.vue**

```vue
<template>
  <div class="py-16 px-4 max-w-6xl mx-auto">
    <h1 v-if="title" class="text-3xl font-bold mb-10 text-center">
      {{ title }}
    </h1>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
      <UCard v-for="article in items" :key="article.id" class="cursor-pointer" @click="navigateTo(`/news/${article.id}`)">
        <img
          v-if="showImage && article.cover_image_id"
          :src="`${apiBase}/../../media/${article.cover_image_id}`"
          class="w-full h-48 object-cover rounded-t"
        />
        <template #header>
          <h3 class="text-lg font-semibold">
            {{ locale === 'zh' ? article.title_zh : article.title_en }}
          </h3>
        </template>
        <p class="text-gray-600 line-clamp-3">
          {{ locale === 'zh' ? article.summary_zh : article.summary_en }}
        </p>
        <template #footer>
          <span v-if="showDate" class="text-sm text-gray-500">
            {{ new Date(article.published_at).toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US') }}
          </span>
        </template>
      </UCard>
    </div>

    <div v-if="!items.length" class="text-center text-gray-500 py-20">
      {{ locale === 'zh' ? '暂无新闻' : 'No news yet' }}
    </div>

    <div v-if="totalPages > 1" class="flex justify-center gap-2">
      <UButton
        v-for="p in totalPages"
        :key="p"
        :variant="p === currentPage ? 'solid' : 'outline'"
        @click="currentPage = p"
      >
        {{ p }}
      </UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();

const { locale } = useI18n();
const apiBase = useRuntimeConfig().public.apiBase;

const title = computed(() => locale.value === 'zh' ? props.content.title_zh : props.content.title_en);
const showImage = computed(() => props.content.show_image !== false);
const showDate = computed(() => props.content.show_date !== false);
const pageSize = computed(() => props.content.count || 9);

const currentPage = ref(1);

const { data } = await useNewsList(currentPage.value, pageSize.value);
const items = computed(() => data.value?.items || []);
const total = computed(() => data.value?.total || 0);
const totalPages = computed(() => Math.ceil(total.value / pageSize.value));
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/blocks/NewsArticleList.vue
git commit -m "feat: add NewsArticleList page-level component"
```

---

### Task 6: Frontend — NewsArticleDetail component

**Files:**
- Create: `frontend/components/blocks/NewsArticleDetail.vue`

Replaces `pages/news/[id].vue`.

- [ ] **Step 1: Create NewsArticleDetail.vue**

```vue
<template>
  <article v-if="article" class="py-16 px-4 max-w-3xl mx-auto">
    <img
      v-if="article.cover_image_id"
      :src="`${apiBase}/../../media/${article.cover_image_id}`"
      class="w-full max-h-96 object-cover rounded-lg mb-8"
    />
    <h1 class="text-3xl font-bold mb-4">
      {{ locale === 'zh' ? article.title_zh : article.title_en }}
    </h1>
    <p class="text-gray-500 mb-8">
      {{ new Date(article.published_at).toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US') }}
    </p>
    <div
      class="prose max-w-none"
      v-html="locale === 'zh' ? article.content_zh : article.content_en"
    />
    <div class="mt-10">
      <UButton to="/news" variant="outline">
        {{ locale === 'zh' ? '返回新闻列表' : 'Back to News' }}
      </UButton>
    </div>
  </article>

  <div v-else-if="error" class="py-20 text-center text-gray-500">
    {{ locale === 'zh' ? '文章未找到' : 'Article not found' }}
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ articleId: string }>();
const { locale } = useI18n();
const apiBase = useRuntimeConfig().public.apiBase;

const { article, error } = await useNewsArticle(Number(props.articleId));
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/blocks/NewsArticleDetail.vue
git commit -m "feat: add NewsArticleDetail page-level component"
```

---

### Task 7: Frontend — ProductCatalog component

**Files:**
- Create: `frontend/components/blocks/ProductCatalog.vue`

Replaces `pages/products/index.vue`.

- [ ] **Step 1: Create ProductCatalog.vue**

```vue
<template>
  <div class="min-h-screen" style="background: #f8fafc;">
    <div class="max-w-7xl mx-auto px-4 py-12">
      <h1 class="text-3xl font-light tracking-tight mb-2" style="color: #1e293b">
        {{ locale === 'zh' ? '产品中心' : 'Products' }}
      </h1>
      <p class="text-[14px] mb-8" style="color: #94a3b8;">
        {{ locale === 'zh' ? '探索我们的产品与解决方案' : 'Explore our products and solutions' }}
      </p>

      <!-- Category tabs -->
      <div class="flex flex-wrap gap-3 mb-8">
        <button
          v-for="tab in tabs"
          :key="tab.slug"
          @click="activeCategory = tab.slug; page = 1; fetchProducts()"
          class="text-[13px] border-none cursor-pointer px-5 py-2 rounded-full transition-colors"
          :style="activeCategory === tab.slug ? 'background: rgba(5,150,105,0.12); color: #34d399;' : 'background: #ffffff; color: #94a3b8; border: 1px solid #e2e8f0;'"
        >
          {{ locale === 'zh' ? tab.name_zh : tab.name_en }}
        </button>
      </div>

      <div v-if="loading" class="text-[14px] py-20 text-center" style="color: #94a3b8;">
        {{ locale === 'zh' ? '加载中...' : 'Loading...' }}
      </div>

      <div v-else-if="products.length === 0" class="text-[14px] py-20 text-center" style="color: #94a3b8;">
        {{ locale === 'zh' ? '暂无产品' : 'No products' }}
      </div>

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
            <div v-else class="w-full h-full flex items-center justify-center text-[12px]" style="color: #94a3b8;">
              {{ locale === 'zh' ? '暂无图片' : 'No image' }}
            </div>
          </div>
          <div class="p-5">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-[11px] px-2 py-0.5 rounded-full" style="background: rgba(5,150,105,0.08); color: #34d399;">
                {{ prod.category ? (locale === 'zh' ? prod.category.name_zh : prod.category.name_en) : '' }}
              </span>
            </div>
            <h3 class="text-[16px] font-medium mb-2" style="color: #1e293b">
              {{ locale === 'zh' ? prod.name_zh : prod.name_en }}
            </h3>
            <p class="text-[13px] leading-relaxed line-clamp-2" style="color: #94a3b8;">
              {{ locale === 'zh' ? prod.summary_zh : prod.summary_en }}
            </p>
          </div>
        </NuxtLink>
      </div>

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
const props = defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();

const { locale } = useI18n();
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
  name_en: string;
  slug: string;
  cover_image_id: number | null;
  summary_zh: string;
  summary_en: string;
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
git add frontend/components/blocks/ProductCatalog.vue
git commit -m "feat: add ProductCatalog page-level component"
```

---

### Task 8: Frontend — ProductDetail component

**Files:**
- Create: `frontend/components/blocks/ProductDetail.vue`

Replaces `pages/products/[slug].vue`.

- [ ] **Step 1: Create ProductDetail.vue**

```vue
<template>
  <div class="min-h-screen" style="background: #f8fafc;">
    <div v-if="loading" class="text-[14px] py-20 text-center" style="color: #94a3b8;">Loading...</div>

    <div v-else-if="error" class="text-[14px] py-20 text-center" style="color: #f87171;">{{ error }}</div>

    <template v-else-if="product">
      <div class="max-w-5xl mx-auto px-4 py-6">
        <div class="flex items-center gap-2 text-[12px]" style="color: #94a3b8;">
          <NuxtLink to="/" class="no-underline hover:opacity-70" style="color: #94a3b8;">{{ locale === 'zh' ? '首页' : 'Home' }}</NuxtLink>
          <span>/</span>
          <NuxtLink to="/products" class="no-underline hover:opacity-70" style="color: #94a3b8;">{{ locale === 'zh' ? '产品中心' : 'Products' }}</NuxtLink>
          <span v-if="product.category">/</span>
          <span v-if="product.category" style="color: #34d399;">{{ locale === 'zh' ? product.category.name_zh : product.category.name_en }}</span>
          <span>/</span>
          <span style="color: #64748b;">{{ locale === 'zh' ? product.name_zh : product.name_en }}</span>
        </div>
      </div>

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
              <span v-if="product.category" class="text-[11px] px-2 py-1 rounded-full mb-3 self-start" style="background: rgba(5,150,105,0.08); color: #34d399;">{{ locale === 'zh' ? product.category.name_zh : product.category.name_en }}</span>
              <h1 class="text-2xl font-light tracking-tight mb-3" style="color: #1e293b">{{ locale === 'zh' ? product.name_zh : product.name_en }}</h1>
              <p class="text-[14px] leading-relaxed" style="color: #64748b;">{{ locale === 'zh' ? product.summary_zh : product.summary_en }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-if="product.specs && product.specs.length > 0" class="max-w-5xl mx-auto px-4 pb-8">
        <h2 class="text-[16px] font-medium mb-4" style="color: #1e293b">{{ locale === 'zh' ? '规格参数' : 'Specifications' }}</h2>
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

      <div v-if="product.description_zh || product.description_en" class="max-w-5xl mx-auto px-4 pb-12">
        <h2 class="text-[16px] font-medium mb-4" style="color: #1e293b">{{ locale === 'zh' ? '产品详情' : 'Product Details' }}</h2>
        <div class="rounded-xl p-6 text-[14px] leading-relaxed" style="background: #ffffff; border: 1px solid #e2e8f0; color: #334155;" v-html="(locale === 'zh' ? product.description_zh : product.description_en)?.replace(/\\n/g, '<br/>')">
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ productSlug: string }>();
const { locale } = useI18n();
const config = useRuntimeConfig();
const apiBase = config.public.apiBase as string;

interface Category {
  id: number;
  name_zh: string;
  name_en: string;
}

interface ProductDetail {
  id: number;
  name_zh: string;
  name_en: string;
  slug: string;
  cover_image_id: number | null;
  summary_zh: string;
  summary_en: string;
  description_zh: string;
  description_en: string;
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
    product.value = await $fetch<ProductDetail>(`${apiBase}/products/${props.productSlug}`);
  } catch (e: any) {
    error.value = e?.data?.detail || (locale.value === 'zh' ? '产品不存在' : 'Product not found');
  } finally {
    loading.value = false;
  }
};

onMounted(fetchProduct);
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/blocks/ProductDetail.vue
git commit -m "feat: add ProductDetail page-level component"
```

---

### Task 9: Frontend — FaqPanel and ContactFormBlock components

**Files:**
- Create: `frontend/components/blocks/FaqPanel.vue`
- Create: `frontend/components/blocks/ContactFormBlock.vue`

- [ ] **Step 1: Create FaqPanel.vue**

```vue
<template>
  <section class="py-16 px-4 max-w-3xl mx-auto">
    <h1 v-if="title" class="text-3xl font-bold text-center mb-10">
      {{ title }}
    </h1>

    <UAccordion v-if="faqs.length" :items="accordionItems" />

    <p v-else class="text-center text-gray-500 py-20">
      {{ locale === 'zh' ? '暂无常见问题' : 'No FAQs yet' }}
    </p>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();

const { locale } = useI18n();
const { data } = await useFaqs();
const faqs = computed(() => data.value || []);

const title = computed(() => locale.value === 'zh' ? props.content.title_zh : props.content.title_en);

const accordionItems = computed(() =>
  faqs.value.map((faq: any) => ({
    label: locale.value === 'zh' ? faq.question_zh : faq.question_en,
    content: locale.value === 'zh' ? faq.answer_zh : faq.answer_en,
  }))
);
</script>
```

- [ ] **Step 2: Create ContactFormBlock.vue**

```vue
<template>
  <section class="py-16 px-4 max-w-xl mx-auto">
    <h1 v-if="title" class="text-3xl font-bold text-center mb-10">
      {{ title }}
    </h1>

    <UAlert
      v-if="success"
      color="green"
      :title="locale === 'zh' ? '提交成功，我们会尽快联系您！' : 'Submitted! We will contact you soon.'"
      class="mb-4"
    />
    <UAlert v-if="errorMsg" color="red" :title="errorMsg" class="mb-4" />
    <UCard>
      <form @submit.prevent="onSubmit" class="space-y-4">
        <UFormGroup v-if="showField('company_name')" :label="locale === 'zh' ? '公司名称' : 'Company Name'" required>
          <UInput v-model="form.company_name" />
        </UFormGroup>
        <UFormGroup v-if="showField('contact_name')" :label="locale === 'zh' ? '联系人' : 'Contact Name'" required>
          <UInput v-model="form.contact_name" />
        </UFormGroup>
        <UFormGroup v-if="showField('phone')" :label="locale === 'zh' ? '电话' : 'Phone'" required>
          <UInput v-model="form.phone" type="tel" />
        </UFormGroup>
        <UFormGroup v-if="showField('message')" :label="locale === 'zh' ? '留言' : 'Message'" required>
          <UTextarea v-model="form.message" :rows="4" />
        </UFormGroup>
        <UButton type="submit" :loading="loading" block size="lg">
          {{ submitLabel }}
        </UButton>
      </form>
    </UCard>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();

const { locale } = useI18n();
const { submit, loading, error: inquiryError, success } = useInquiry();

const errorMsg = computed(() => inquiryError.value);

const title = computed(() => locale.value === 'zh' ? props.content.title_zh : props.content.title_en);
const submitLabel = computed(() => locale.value === 'zh'
  ? (props.content.submit_button_zh || '提交')
  : (props.content.submit_button_en || 'Submit')
);

const fields = computed(() => props.content.fields || ['company_name', 'contact_name', 'phone', 'message']);

const showField = (name: string) => fields.value.includes(name);

const form = reactive({
  company_name: '',
  contact_name: '',
  phone: '',
  message: '',
});

const onSubmit = async () => {
  await submit({ ...form });
};
</script>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/components/blocks/FaqPanel.vue frontend/components/blocks/ContactFormBlock.vue
git commit -m "feat: add FaqPanel and ContactFormBlock page-level components"
```

---

### Task 10: Frontend — [...slug].vue catch-all page and index.vue update

**Files:**
- Create: `frontend/pages/[...slug].vue`
- Modify: `frontend/pages/index.vue`

- [ ] **Step 1: Create [...slug].vue**

This is the core of the refactor — the single dynamic page handler.

```vue
<template>
  <div>
    <!-- Content pages: block rendering -->
    <template v-if="!page">
      <p class="text-center py-20 text-gray-500">Loading...</p>
    </template>

    <!-- type=content: blocks only -->
    <template v-else-if="page.type === 'content'">
      <BlockRenderer v-for="block in page.blocks" :key="block.id" :block="block" />
    </template>

    <!-- type=news -->
    <template v-else-if="page.type === 'news'">
      <template v-if="!detailParam">
        <!-- News list: render blocks above, then news list -->
        <BlockRenderer v-for="block in nonNewsListBlocks" :key="block.id" :block="block" />
        <NewsArticleList :config="{}" :content="newsListConfig" />
      </template>
      <template v-else>
        <NewsArticleDetail :articleId="detailParam" />
      </template>
    </template>

    <!-- type=products -->
    <template v-else-if="page.type === 'products'">
      <template v-if="!detailParam">
        <BlockRenderer v-for="block in page.blocks" :key="block.id" :block="block" />
        <ProductCatalog :config="{}" :content="{}" />
      </template>
      <template v-else>
        <ProductDetail :productSlug="detailParam" />
      </template>
    </template>

    <!-- type=faq -->
    <template v-else-if="page.type === 'faq'">
      <BlockRenderer v-for="block in page.blocks" :key="block.id" :block="block" />
      <FaqPanel :config="{}" :content="faqConfig" />
    </template>

    <!-- type=contact -->
    <template v-else-if="page.type === 'contact'">
      <BlockRenderer v-for="block in page.blocks" :key="block.id" :block="block" />
      <ContactFormBlock :config="{}" :content="contactConfig" />
    </template>
  </div>
</template>

<script setup lang="ts">
import BlockRenderer from '~/components/blocks/BlockRenderer.vue';
import NewsArticleList from '~/components/blocks/NewsArticleList.vue';
import NewsArticleDetail from '~/components/blocks/NewsArticleDetail.vue';
import ProductCatalog from '~/components/blocks/ProductCatalog.vue';
import ProductDetail from '~/components/blocks/ProductDetail.vue';
import FaqPanel from '~/components/blocks/FaqPanel.vue';
import ContactFormBlock from '~/components/blocks/ContactFormBlock.vue';

const route = useRoute();
const slug = route.params.slug as string[];
const pageSlug = slug[0];
const detailParam = slug[1] || null;

const { page } = await usePage(pageSlug);

if (!page) {
  throw createError({ statusCode: 404, message: 'Page not found' });
}

// For news pages, extract config from the first news_list block
const newsListBlock = computed(() =>
  (page.value as any)?.blocks?.find((b: any) => b.type === 'news_list')
);

const nonNewsListBlocks = computed(() =>
  ((page.value as any)?.blocks || []).filter((b: any) => b.type !== 'news_list')
);

const newsListConfig = computed(() => newsListBlock.value?.content || {
  title_zh: '新闻中心',
  title_en: 'News',
  count: 9,
  show_date: true,
  show_image: true,
});

const faqConfig = computed(() => {
  const faqBlock = (page.value as any)?.blocks?.find((b: any) => b.type === 'faq');
  return faqBlock?.content || {
    title_zh: '常见问题',
    title_en: 'FAQ',
  };
});

const contactConfig = computed(() => {
  const contactBlock = (page.value as any)?.blocks?.find((b: any) => b.type === 'contact_form');
  return contactBlock?.content || {
    title_zh: '联系我们',
    title_en: 'Contact Us',
  };
});
</script>
```

- [ ] **Step 2: Update index.vue**

Rewrite to use the same page page but using `usePage('home')`:

```vue
<template>
  <div>
    <BlockRenderer v-for="block in page?.blocks" :key="block.id" :block="block" />
    <p v-if="!page" class="text-center py-20 text-gray-500">Loading...</p>
  </div>
</template>

<script setup lang="ts">
import BlockRenderer from '~/components/blocks/BlockRenderer.vue';
const { page } = await usePage('home');
</script>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/pages/[...slug].vue frontend/pages/index.vue
git commit -m "feat: add catch-all [...slug].vue, update index.vue for home page"
```

---

### Task 11: Frontend — admin pages.vue with type selector

**Files:**
- Modify: `frontend/pages/admin/pages.vue`

- [ ] **Step 1: Add type to Page interface and type field to form**

In the `<script setup>` section, update the `Page` interface to include `type`:

```ts
interface Page {
  id: number;
  name_zh: string;
  name_en: string;
  slug: string;
  type: string;
  is_published: boolean;
  _blocks?: Block[];
}
```

Update the `pageForm` to include `type`:

```ts
const pageForm = ref({ name_zh: '', name_en: '', slug: '', type: 'content' });
```

Update `openCreatePage`:

```ts
const openCreatePage = () => {
  editingPage.value = null;
  pageForm.value = { name_zh: '', name_en: '', slug: '', type: 'content' };
  pageFormError.value = '';
  pageModal.value = true;
};
```

Update `openEditPage`:

```ts
const openEditPage = (page: Page) => {
  editingPage.value = page;
  pageForm.value = { name_zh: page.name_zh, name_en: page.name_en, slug: page.slug, type: page.type || 'content' };
  pageFormError.value = '';
  pageModal.value = true;
};
```

- [ ] **Step 2: Add type selector to page form template**

After the slug input, add:

```html
<div>
  <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">类型</label>
  <select
    v-model="pageForm.type"
    class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg transition-colors appearance-none"
    style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
  >
    <option value="content">内容页</option>
    <option value="news">新闻列表</option>
    <option value="products">产品目录</option>
    <option value="faq">常见问题</option>
    <option value="contact">联系我们</option>
  </select>
</div>
```

- [ ] **Step 3: Show type badge in page list rows**

In the page list row template (after `is_published` badge), add:

```html
<span class="text-[12px] px-2 py-0.5 rounded-full" :style="typeBadgeStyle(page.type)">
  {{ typeLabel(page.type) }}
</span>
```

And add helper functions in script:

```ts
const typeLabels: Record<string, string> = {
  content: '内容页',
  news: '新闻',
  products: '产品',
  faq: 'FAQ',
  contact: '联系',
};

const typeLabel = (t: string) => typeLabels[t] || t;

const typeBadgeStyle = (t: string) =>
  t === 'content'
    ? 'background: #f1f5f9; color: #94a3b8;'
    : 'background: rgba(5,150,105,0.12); color: #34d399;';
```

- [ ] **Step 4: Commit**

```bash
git add frontend/pages/admin/pages.vue
git commit -m "feat: add page type selector to admin pages management"
```

---

### Task 12: Frontend — admin menus.vue with page selector dropdown

**Files:**
- Modify: `frontend/pages/admin/menus.vue`

- [ ] **Step 1: Fetch pages list for dropdown**

Add page fetching in script:

```ts
interface PageOption {
  id: number;
  name_zh: string;
  slug: string;
  type: string;
}

const pageOptions = ref<PageOption[]>([]);

const fetchPages = async () => {
  try {
    pageOptions.value = await api<PageOption[]>('/admin/pages');
  } catch {}
};
```

Call `fetchPages()` in the existing `onMounted(fetchMenus)` → change to:

```ts
onMounted(() => { fetchMenus(); fetchPages(); });
```

Add `page_id` to the form:

```ts
const form = ref({
  name_zh: '', name_en: '', link: '', icon: '',
  order: 0, is_visible: true, location: 'header',
  page_id: null as number | null,
});
```

- [ ] **Step 2: Replace link input with page selector in template**

Replace the existing link input `<div>` with:

```html
<div>
  <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">选择页面</label>
  <select
    v-model="form.page_id"
    class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg appearance-none"
    style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
  >
    <option :value="null">— 无 —</option>
    <option v-for="p in pageOptions" :key="p.id" :value="p.id">
      /{{ p.slug }} — {{ p.name_zh }}
    </option>
  </select>
</div>
```

Remove the link text input. Also remove `link` from the form reset in `openCreate` and `openEdit`.

- [ ] **Step 3: Update save to include page_id**

In the `save` function, the body already spreads `form.value`, so `page_id` is included automatically. No change needed.

- [ ] **Step 4: Commit**

```bash
git add frontend/pages/admin/menus.vue
git commit -m "feat: replace menu link input with page selector dropdown"
```

---

### Task 13: Frontend — AppHeader.vue and nuxt.config.ts

**Files:**
- Modify: `frontend/components/layout/AppHeader.vue`
- Modify: `frontend/nuxt.config.ts`

- [ ] **Step 1: Update AppHeader.vue for page_slug**

Replace the `NuxtLink` `:to` for both dropdown items (with children) and direct links:

For direct links (item without children):
```html
<NuxtLink
  v-if="!item.children || item.children.length === 0"
  :to="item.page_slug === 'home' ? '/' : '/' + item.page_slug"
  class="text-sm transition-colors"
  :class="$route.path === (item.page_slug === 'home' ? '/' : '/' + item.page_slug) ? 'text-emerald-600 font-[550]' : 'text-slate-500 hover:text-slate-700'"
>
  {{ locale === 'zh' ? item.name_zh : item.name_en }}
</NuxtLink>
```

For dropdown parent (item with children):
```html
<NuxtLink
  :to="item.page_slug === 'home' ? '/' : '/' + item.page_slug"
  class="text-sm transition-colors cursor-pointer"
  :class="$route.path === (item.page_slug === 'home' ? '/' : '/' + item.page_slug) ? 'text-emerald-600 font-[550]' : 'text-slate-500 hover:text-slate-700'"
>
  {{ locale === 'zh' ? item.name_zh : item.name_en }}
  <span class="ml-0.5 text-[10px] opacity-60">&#9660;</span>
</NuxtLink>
```

And for child items:
```html
<NuxtLink
  v-for="child in item.children"
  :key="child.id"
  :to="child.page_slug === 'home' ? '/' : '/' + child.page_slug"
  class="block px-4 py-2 text-sm transition-colors whitespace-nowrap"
  :class="$route.path === (child.page_slug === 'home' ? '/' : '/' + child.page_slug) ? 'text-emerald-600 font-[550] bg-emerald-50' : 'text-slate-500 hover:text-emerald-600 hover:bg-emerald-50/50'"
>
  {{ locale === 'zh' ? child.name_zh : child.name_en }}
</NuxtLink>
```

Also update the `MenuItem` interface to include `page_slug`:
```ts
interface MenuItem {
  id: number;
  name_zh: string;
  name_en: string;
  link: string;
  page_id: number | null;
  page_slug: string | null;
  children: MenuItem[];
}
```

- [ ] **Step 2: Update nuxt.config.ts route rules**

```ts
export default defineNuxtConfig({
  compatibilityDate: '2026-05-21',
  devtools: { enabled: true },
  ssr: true,
  css: ['~/assets/css/main.css'],
  modules: ['@nuxtjs/i18n', '@nuxt/image', '@nuxt/ui'],
  i18n: {
    locales: ['zh', 'en'],
    defaultLocale: 'zh',
    strategy: 'prefix_except_default',
  },
  image: { domains: ['localhost'] },
  routeRules: {
    '/': { prerender: true },
    '/about': { prerender: true },
    '/products': { prerender: true },
    '/solutions': { prerender: true },
    '/contact': { prerender: true },
    '/news': { isr: 300 },
    '/news/**': { isr: 300 },
    '/faq': { isr: 300 },
    '/chat': { ssr: false },
    '/admin/**': { ssr: false },
  },
  devServer: { port: 5177 },
  runtimeConfig: {
    public: { apiBase: 'http://localhost:8002/api/v1' },
  },
});
```

- [ ] **Step 3: Commit**

```bash
git add frontend/components/layout/AppHeader.vue frontend/nuxt.config.ts
git commit -m "feat: update AppHeader for page_slug routing; add /faq ISR route rule"
```

---

### Task 14: Frontend — delete hardcoded page files

**Files to delete:**
- `frontend/pages/[slug].vue`
- `frontend/pages/news/index.vue`
- `frontend/pages/news/[id].vue`
- `frontend/pages/faq.vue`
- `frontend/pages/contact.vue`
- `frontend/pages/products/index.vue`
- `frontend/pages/products/[slug].vue`

- [ ] **Step 1: Remove the old files**

```bash
cd /Users/ymilitarym/hp-2026/gweb
rm frontend/pages/\[slug\].vue
rm frontend/pages/news/index.vue
rm frontend/pages/news/\[id\].vue
rm frontend/pages/faq.vue
rm frontend/pages/contact.vue
rm frontend/pages/products/index.vue
rm frontend/pages/products/\[slug\].vue
```

Remove empty directories if any:
```bash
rmdir frontend/pages/news 2>/dev/null || true
rmdir frontend/pages/products 2>/dev/null || true
```

- [ ] **Step 2: Commit**

```bash
git add -A frontend/pages/
git commit -m "refactor: remove hardcoded page files, replaced by [...slug].vue"
```

---

### Task 15: Backend — drop link column from menus

**Files:**
- Create: `backend/alembic/versions/<auto>_drop_menu_link_column.py`
- Modify: `backend/app/apps/cms/models.py`

- [ ] **Step 1: Generate migration to drop link column**

```bash
cd backend && source .venv/bin/activate
```

First, update the Menu model to remove the `link` field:

In `backend/app/apps/cms/models.py:55-67`, remove the `link` line:
```python
class Menu(Base, TimestampMixin):
    __tablename__ = "menus"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("menus.id", ondelete="SET NULL"), nullable=True)
    name_zh: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    page_id: Mapped[int | None] = mapped_column(ForeignKey("pages.id"), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    location: Mapped[str] = mapped_column(String(20), nullable=False, default="header")
    parent: Mapped["Menu | None"] = relationship("Menu", remote_side=[id], back_populates="children")
    children: Mapped[list["Menu"]] = relationship("Menu", back_populates="parent")
    page: Mapped["Page | None"] = relationship("Page")
```

Then run:
```bash
alembic revision --autogenerate -m "drop_menu_link_column"
alembic upgrade head
```

- [ ] **Step 2: Update menu service to remove link references**

In `backend/app/apps/cms/service_menu.py`, update `create_menu_item` — remove `link` parameter:

```python
async def create_menu_item(
    name_zh: str,
    name_en: str,
    page_id: int | None = None,
    location: str = "header",
    order: int = 0,
    parent_id: int | None = None,
    icon: str | None = None,
) -> Menu:
    async with async_session() as db:
        menu = Menu(
            name_zh=name_zh,
            name_en=name_en,
            page_id=page_id,
            location=location,
            order=order,
            parent_id=parent_id,
            icon=icon,
        )
        db.add(menu)
        await db.commit()
        await db.refresh(menu)
        return menu
```

In `get_menu_tree`, remove `link` from the response dict:

```python
by_id[m.id] = {
    "id": m.id,
    "name_zh": m.name_zh,
    "name_en": m.name_en,
    "page_id": m.page_id,
    "page_slug": None,
    "icon": m.icon,
    "children": [],
}
```

- [ ] **Step 3: Update menu admin router to not expect link**

In `backend/app/apps/cms/router.py`, the admin menu endpoints accept `data: dict` and pass through to `create_menu_item` / `update_menu_item`. Since `link` is no longer a valid kwarg, old data with `link` will be silently ignored. No explicit change needed for the router.

- [ ] **Step 4: Commit**

```bash
git add backend/app/apps/cms/models.py backend/app/apps/cms/service_menu.py backend/alembic/versions/*drop_menu_link*.py
git commit -m "feat: drop link column from menus, use page_id exclusively"
```

---

### Task 16: Tests — update and verify

**Files:**
- Modify: `backend/tests/test_cms.py` (if exists) or create new tests
- Check: `backend/tests/conftest.py`

- [ ] **Step 1: Check existing CMS tests**

```bash
cd backend && find tests -name "*.py" | xargs grep -l "pages\|menu\|cms" | head -10
```

- [ ] **Step 2: Run existing tests to see what breaks**

```bash
cd /Users/ymilitarym/hp-2026/gweb/backend && source .venv/bin/activate && python -m pytest tests/ -x --tb=short 2>&1 | head -80
```

- [ ] **Step 3: Update failing tests**

For each failing test, update to include the new `type` field in page creation and `page_id` in menu creation. Key changes:
- Test page creation: include `type: "content"` in request body
- Test menu creation: use `page_id` instead of `link`
- Test public /pages/{slug}: assert response includes `type` field
- Test admin list pages: assert response items include `type`
- Test menu tree: assert response includes `page_id` and `page_slug`

- [ ] **Step 4: Run tests to confirm all pass**

```bash
cd /Users/ymilitarym/hp-2026/gweb/backend && source .venv/bin/activate && python -m pytest tests/ -v --tb=short
```

- [ ] **Step 5: Commit**

```bash
git add backend/tests/
git commit -m "test: update tests for page type and menu page_id"
```

---

### Task 17: Build verification

- [ ] **Step 1: Start backend and verify APIs**

```bash
cd /Users/ymilitarym/hp-2026/gweb/backend && source .venv/bin/activate && uvicorn app.main:app --port 8002 &
```

Test key endpoints:
```bash
# Pages should include type
curl -s http://localhost:8002/api/v1/pages/about | python -m json.tool | grep type

# Menu tree should include page_slug
curl -s "http://localhost:8002/api/v1/menus?location=header" | python -m json.tool | grep page_slug

# Pages slugs endpoint
curl -s http://localhost:8002/api/v1/pages/slugs | python -m json.tool
```

- [ ] **Step 2: Build frontend**

```bash
cd /Users/ymilitarym/hp-2026/gweb/frontend && npm run build 2>&1 | tail -20
```

Expected: build succeeds, prerender errors are gone, no missing route warnings.

- [ ] **Step 3: Start frontend and manual smoke test**

```bash
cd /Users/ymilitarym/hp-2026/gweb/frontend && npm run dev &
```

Verify these pages load:
- `/` — home page with blocks
- `/about` — about page with blocks
- `/news` — news list with pagination
- `/news/1` — first article detail
- `/products` — product catalog with category tabs
- `/products/<some-slug>` — product detail
- `/faq` — FAQ accordion
- `/contact` — contact form
- `/solutions` — solutions page
- `/admin/pages` — admin page list with type badges
- `/admin/menus` — admin menu list with page selector

- [ ] **Step 4: Cleanup**

Stop dev servers and commit any final fixes.

```bash
git add -A
git commit -m "chore: final build verification adjustments"
```
