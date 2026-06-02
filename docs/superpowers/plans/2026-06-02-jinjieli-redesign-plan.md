# 金捷利官网前端重设计 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 GWeb 前端 100% 还原为金捷利官网设计风格，所有动态数据来源于后端 API，新增 Case 模型和管理页面。

**Architecture:** 后端新增 cases 模块（FastAPI + SQLAlchemy），Settings 系统扩展公司信息字段；前端 Tailwind 主题覆写（emerald→blue），Header/Footer/Hero/AI Chat 四大组件重写，新增 /cases 前端页面。所有页面内容通过 CMS Page API + 各业务 API 动态渲染。

**Tech Stack:** FastAPI + SQLAlchemy + Alembic (后端), Nuxt 3 + Tailwind CSS v4 + Vue 3 (前端)

---

## 文件结构

```
新建:
  backend/app/apps/cases/__init__.py
  backend/app/apps/cases/models.py
  backend/app/apps/cases/schemas.py
  backend/app/apps/cases/service.py
  backend/app/apps/cases/router.py
  backend/alembic/versions/xxxx_add_cases_table.py
  frontend/pages/cases/index.vue
  frontend/pages/cases/[slug].vue
  frontend/pages/admin/cases.vue

修改:
  backend/app/main.py                              — 注册 cases router
  backend/seed.py                                   — 预置金捷利数据
  frontend/assets/css/main.css                      — 全局主题覆写
  frontend/components/layout/AppHeader.vue          — 重写
  frontend/components/layout/AppFooter.vue          — 重写
  frontend/components/blocks/BlockHero.vue          — 轮播升级
  frontend/components/blocks/BlockSolutionCards.vue — Tab组件新增
  frontend/components/blocks/BlockProductCards.vue  — 样式对齐
  frontend/components/blocks/BlockNewsList.vue      — 样式对齐
  frontend/components/blocks/BlockFaq.vue           — 样式对齐
  frontend/components/blocks/BlockContactForm.vue   — 样式对齐
  frontend/components/blocks/BlockCtaBanner.vue     — 样式对齐
  frontend/components/blocks/BlockRichtext.vue      — 样式对齐
  frontend/components/blocks/BlockStatsCounter.vue  — 样式对齐
  frontend/components/chat/ChatFloatingButton.vue   — 重写
  frontend/components/chat/ChatPanel.vue            — 样式对齐
  frontend/pages/admin/settings.vue                 — 扩展字段
```

---

### Task 1: Backend — Case 模型与迁移

**Files:**
- Create: `backend/app/apps/cases/__init__.py`
- Create: `backend/app/apps/cases/models.py`

- [ ] **Step 1: 创建 cases 模块目录和模型**

```bash
mkdir -p backend/app/apps/cases
```

Write `backend/app/apps/cases/__init__.py`:
```python
```

Write `backend/app/apps/cases/models.py`:
```python
from sqlalchemy import String, Text, ForeignKey, Boolean, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.models import Base, TimestampMixin


class Case(Base, TimestampMixin):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_zh: Mapped[str] = mapped_column(String(300), nullable=False)
    name_en: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    cover_image_id: Mapped[int | None] = mapped_column(ForeignKey("media.id"), nullable=True)
    summary_zh: Mapped[str] = mapped_column(Text, default="")
    summary_en: Mapped[str] = mapped_column(Text, default="")
    content_zh: Mapped[str] = mapped_column(Text, default="")
    content_en: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(50), default="park")
    stats: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    cover_image: Mapped["Media | None"] = relationship("Media")
```

- [ ] **Step 2: 注册模型到 shared models 或 main.py**

确认 `app.shared.models.Base` 会自动发现 model。在 `backend/app/apps/cases/models.py` 中 import Media:
```python
from app.apps.cms.models import Media
```

- [ ] **Step 3: 生成并运行 migration**

```bash
cd backend && source .venv/bin/activate && alembic revision --autogenerate -m "add_cases_table"
alembic upgrade head
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/apps/cases/ backend/alembic/versions/
git commit -m "feat: add Case model and migration"
```

---

### Task 2: Backend — Cases API (schemas + service + router)

**Files:**
- Create: `backend/app/apps/cases/schemas.py`
- Create: `backend/app/apps/cases/service.py`
- Create: `backend/app/apps/cases/router.py`

- [ ] **Step 1: 编写 schemas**

Write `backend/app/apps/cases/schemas.py`:
```python
from datetime import datetime
from pydantic import BaseModel


class CaseStat(BaseModel):
    label: str
    value: str


class CaseCreate(BaseModel):
    name_zh: str
    name_en: str
    slug: str
    cover_image_id: int | None = None
    summary_zh: str = ""
    summary_en: str = ""
    content_zh: str = ""
    content_en: str = ""
    category: str = "park"
    stats: list[CaseStat] | None = None
    sort_order: int = 0
    is_published: bool = False


class CaseUpdate(BaseModel):
    name_zh: str | None = None
    name_en: str | None = None
    slug: str | None = None
    cover_image_id: int | None = None
    summary_zh: str | None = None
    summary_en: str | None = None
    content_zh: str | None = None
    content_en: str | None = None
    category: str | None = None
    stats: list[CaseStat] | None = None
    sort_order: int | None = None
    is_published: bool | None = None


class CaseResponse(BaseModel):
    id: int
    name_zh: str
    name_en: str
    slug: str
    cover_image_id: int | None
    summary_zh: str
    summary_en: str
    content_zh: str
    content_en: str
    category: str
    stats: list[CaseStat] | None
    sort_order: int
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: 编写 service**

Write `backend/app/apps/cases/service.py`:
```python
from sqlalchemy import select, func
from app.apps.cases.models import Case
from app.core.database import async_session


async def list_published_cases(page: int = 1, size: int = 12, category: str | None = None):
    async with async_session() as db:
        q = select(Case).where(Case.is_published == True)
        if category:
            q = q.where(Case.category == category)
        q = q.order_by(Case.sort_order, Case.created_at.desc())

        total_q = select(func.count()).select_from(Case).where(Case.is_published == True)
        if category:
            total_q = total_q.where(Case.category == category)
        total = (await db.execute(total_q)).scalar() or 0

        offset = (page - 1) * size
        result = await db.execute(q.offset(offset).limit(size))
        return result.scalars().all(), total


async def list_all_cases(page: int = 1, size: int = 20, category: str | None = None):
    async with async_session() as db:
        q = select(Case).order_by(Case.sort_order, Case.created_at.desc())
        if category:
            q = q.where(Case.category == category)
        total_q = select(func.count()).select_from(Case)
        if category:
            total_q = total_q.where(Case.category == category)
        total = (await db.execute(total_q)).scalar() or 0
        offset = (page - 1) * size
        result = await db.execute(q.offset(offset).limit(size))
        return result.scalars().all(), total


async def get_case_by_id(case_id: int) -> Case | None:
    async with async_session() as db:
        return await db.get(Case, case_id)


async def get_case_by_slug(slug: str) -> Case | None:
    async with async_session() as db:
        result = await db.execute(select(Case).where(Case.slug == slug))
        return result.scalar_one_or_none()


async def create_case(**kwargs) -> Case:
    async with async_session() as db:
        case = Case(**kwargs)
        db.add(case)
        await db.commit()
        await db.refresh(case)
        return case


async def update_case(case_id: int, **kwargs) -> Case | None:
    async with async_session() as db:
        case = await db.get(Case, case_id)
        if not case:
            return None
        for k, v in kwargs.items():
            setattr(case, k, v)
        await db.commit()
        await db.refresh(case)
        return case


async def delete_case(case_id: int) -> bool:
    async with async_session() as db:
        case = await db.get(Case, case_id)
        if not case:
            return False
        await db.delete(case)
        await db.commit()
        return True
```

- [ ] **Step 3: 编写 router 并注册到 main.py**

Write `backend/app/apps/cases/router.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, Request

from app.apps.audit.service import create_audit_log
from app.apps.auth.router import get_current_user
from app.apps.cases.schemas import CaseCreate, CaseResponse, CaseUpdate
from app.apps.cases.service import (
    create_case, delete_case, get_case_by_id, get_case_by_slug,
    list_all_cases, list_published_cases, update_case,
)

public_router = APIRouter(prefix="/api/v1", tags=["cases"])

admin_router = APIRouter(
    prefix="/api/v1/admin/cases",
    tags=["admin-cases"],
    dependencies=[Depends(get_current_user)],
)


@public_router.get("/cases")
async def public_list_cases(page: int = 1, size: int = 12, category: str | None = None):
    cases, total = await list_published_cases(page, size, category)
    return {
        "items": [CaseResponse.model_validate(c) for c in cases],
        "total": total,
        "page": page,
        "size": size,
    }


@public_router.get("/cases/{slug}", response_model=CaseResponse)
async def public_get_case(slug: str):
    case = await get_case_by_slug(slug)
    if not case or not case.is_published:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@admin_router.get("")
async def admin_list_cases(page: int = 1, size: int = 20, category: str | None = None):
    cases, total = await list_all_cases(page, size, category)
    return {
        "items": [CaseResponse.model_validate(c) for c in cases],
        "total": total,
        "page": page,
        "size": size,
    }


@admin_router.post("", response_model=CaseResponse, status_code=201)
async def admin_create_case(data: CaseCreate, request: Request, current_user=Depends(get_current_user)):
    case = await create_case(**data.model_dump())
    await create_audit_log(
        user_id=current_user.id, username=current_user.username,
        action="create", resource_type="case", resource_id=case.id,
        resource_name=case.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return case


@admin_router.put("/{case_id}", response_model=CaseResponse)
async def admin_update_case(case_id: int, data: CaseUpdate, request: Request, current_user=Depends(get_current_user)):
    case = await update_case(case_id, **data.model_dump(exclude_none=True))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    await create_audit_log(
        user_id=current_user.id, username=current_user.username,
        action="update", resource_type="case", resource_id=case.id,
        resource_name=case.name_zh,
        ip_address=request.client.host if request.client else None,
    )
    return case


@admin_router.delete("/{case_id}")
async def admin_delete_case(case_id: int, request: Request, current_user=Depends(get_current_user)):
    case = await get_case_by_id(case_id)
    name = case.name_zh if case else None
    deleted = await delete_case(case_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Case not found")
    await create_audit_log(
        user_id=current_user.id, username=current_user.username,
        action="delete", resource_type="case", resource_id=case_id,
        resource_name=name,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True}
```

Edit `backend/app/main.py` — add to imports:
```python
from app.apps.cases.router import public_router as cases_public_router
from app.apps.cases.router import admin_router as cases_admin_router
```

Add to lifespan/router registration (after products routers):
```python
app.include_router(cases_public_router)
app.include_router(cases_admin_router)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/apps/cases/ backend/app/main.py
git commit -m "feat: add Cases CRUD API with public and admin routes"
```

---

### Task 3: Backend — Seed 数据更新

**Files:**
- Modify: `backend/seed.py`

- [ ] **Step 1: 更新 seed.py 预置金捷利数据**

Read current `backend/seed.py` to understand existing seed patterns, then rewrite with Jinjieli data. Core additions to seed function:

```python
# --- Settings ---
company_settings = {
    "company_name_zh": "金捷利科技有限公司",
    "company_name_en": "GOLDGINNY Technology Co., Ltd.",
    "company_description_zh": "专注建筑智能运维领域，以技术赋能建筑全生命周期高效管理，致力于成为中国领先的智慧建筑服务商。",
    "company_description_en": "Focused on intelligent building operations, empowering full-lifecycle building management with technology.",
    "hotline": "400-888-0000",
    "contact_email": "aaqiuaa@gmail.com",
    "icp_beian": "沪ICP备XXXXXXXX号",
    "logo_id": "",  # will set after media upload
    "og_image_id": "",
}
for key, value in company_settings.items():
    existing = await db.execute(select(Setting).where(Setting.key == key))
    if not existing.scalar_one_or_none():
        db.add(Setting(key=key, value=value))

# --- Menus ---
# Header: 首页, 解决方案, 产品服务, 关于我们, 商务合作, 联系我们
# Footer groups: 产品服务(5 items), 解决方案(4 items), 公司(5 items)

# --- Pages ---
# home: hero(carousel) + product_cards + solution_cards + news_list + cta_banner
# solutions: hero + solution_cards
# about: hero + richtext + stats_counter
# cooperation: hero + richtext + contact_form
# privacy, terms: richtext

# --- News Articles ---
# 4 articles: award, project, certification, cooperation

# --- Products ---
# Edge-G100 gateway, environmental sensor, etc.

# --- Cases ---
# 3-4 cases in different categories
```

- [ ] **Step 2: 运行 seed 验证**

```bash
cd backend && source .venv/bin/activate && python seed.py
```

- [ ] **Step 3: Commit**

```bash
git add backend/seed.py
git commit -m "feat: add Jinjieli brand seed data"
```

---

### Task 4: Frontend — 全局 CSS/Tailwind 主题覆写

**Files:**
- Modify: `frontend/assets/css/main.css`

- [ ] **Step 1: 覆写全局主题**

Read current `frontend/assets/css/main.css`, then rewrite with:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

/* Tailwind v4 theme overrides */
@theme {
  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, monospace;
  --color-brand-50: #eff6ff;
  --color-brand-100: #dbeafe;
  --color-brand-500: #2563eb;
  --color-brand-600: #1d4ed8;
  --color-brand-900: #1e3a8a;
  --color-dark-bg: #f8fafc;
  --color-glass: #ffffffbf;
}

body {
  color: #0f172a;
  font-family: var(--font-sans);
  background-color: #f8fafc;
  background-image: radial-gradient(circle at 50% -20%, #eff6ff, #f1f5f9);
  min-height: 100vh;
}

/* Glass utility */
.glass {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.glass-strong {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
}

/* Animated underline */
.nav-underline {
  position: relative;
}
.nav-underline::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--color-brand-600);
  transform: scaleX(0);
  transition: transform 0.3s ease-in-out;
}
.nav-underline:hover::after,
.nav-underline.active::after {
  transform: scaleX(1);
}
```

- [ ] **Step 2: 验证前端编译**

```bash
cd frontend && pnpm dev  # quick check that it compiles
```

- [ ] **Step 3: Commit**

```bash
git add frontend/assets/css/main.css
git commit -m "style: override Tailwind theme to Jinjieli blue brand"
```

---

### Task 5: Frontend — AppHeader 重写

**Files:**
- Modify: `frontend/components/layout/AppHeader.vue`

- [ ] **Step 1: 重写 Header 组件**

Design specs from reference site:
- Sticky top, glass effect (bg-white/80 backdrop-blur-md)
- Scroll hide/show animation (translateY)
- Desktop: nav items with blue underline hover animation
- Mobile: hamburger → full-width slide-down panel
- Logo from Settings API logo_id
- Language toggle (保留)

Write `frontend/components/layout/AppHeader.vue`:
```vue
<template>
  <header
    class="fixed top-0 left-0 right-0 z-50 transition-transform duration-500 ease-in-out bg-white/80 backdrop-blur-md border-b border-slate-200/50"
    :class="hidden ? '-translate-y-full' : 'translate-y-0'"
  >
    <div class="container mx-auto px-6 flex items-center justify-between h-16">
      <!-- Logo -->
      <NuxtLink to="/" class="flex items-center group">
        <img
          v-if="logoUrl"
          :src="logoUrl"
          alt="金捷利"
          class="h-10 md:h-11 w-auto object-contain transition-transform duration-300 group-hover:scale-[1.02]"
        />
        <span v-else class="text-lg font-bold text-brand-600 tracking-tight">
          {{ settings?.company_name_zh || '金捷利' }}
        </span>
      </NuxtLink>

      <!-- Desktop Nav -->
      <nav class="hidden lg:flex items-center gap-1">
        <NuxtLink
          v-for="item in headerMenu"
          :key="item.id"
          :to="menuLink(item)"
          class="nav-underline text-sm font-semibold px-3 py-2.5 text-slate-800 hover:text-brand-600 transition-colors"
          :class="{ active: $route.path === menuLink(item) }"
        >
          {{ locale === 'zh' ? item.name_zh : item.name_en }}
        </NuxtLink>
      </nav>

      <!-- Language Toggle -->
      <div class="flex items-center gap-3">
        <button
          class="relative w-11 h-6 rounded-full cursor-pointer border-none outline-none bg-slate-200 transition-colors"
          :class="{ 'bg-brand-100': locale === 'en' }"
          @click="toggleLang"
          :aria-label="locale === 'zh' ? 'Switch to English' : '切换到中文'"
        >
          <span
            class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm flex items-center justify-center text-[10px] font-semibold transition-transform duration-200"
            :class="locale === 'zh' ? 'left-0.5 text-brand-600' : 'translate-x-[22px] text-slate-400'"
          >
            {{ locale === 'zh' ? '中' : 'EN' }}
          </span>
        </button>

        <!-- Mobile Hamburger -->
        <button class="lg:hidden text-slate-800 p-1" @click="mobileOpen = !mobileOpen">
          <XMarkIcon v-if="mobileOpen" class="w-6 h-6" />
          <Bars3Icon v-else class="w-6 h-6" />
        </button>
      </div>
    </div>

    <!-- Mobile Menu -->
    <div
      v-if="mobileOpen"
      class="lg:hidden absolute top-full left-0 right-0 bg-white/98 backdrop-blur-md border-b border-slate-200/60 p-6 flex flex-col gap-3 shadow-xl"
    >
      <NuxtLink
        v-for="item in headerMenu"
        :key="'m-' + item.id"
        :to="menuLink(item)"
        class="text-lg text-left py-1 text-slate-800 hover:text-brand-600 transition-colors font-semibold"
        :class="{ 'text-brand-600': $route.path === menuLink(item) }"
        @click="mobileOpen = false"
      >
        {{ locale === 'zh' ? item.name_zh : item.name_en }}
      </NuxtLink>
    </div>
  </header>
</template>

<script setup lang="ts">
import { Bars3Icon, XMarkIcon } from '@heroicons/vue/24/outline'

interface MenuItem {
  id: number
  name_zh: string
  name_en: string
  link: string
  page_slug: string | null
  children: MenuItem[]
}

const { locale } = useI18n()
const config = useRuntimeConfig()

// Fetch menu & settings
const { data: headerMenu } = await useFetch<MenuItem[]>(
  `${config.public.apiBase}/menus?location=header`,
  { default: () => [] }
)
const { data: settings } = await useFetch<Record<string, string>>(
  `${config.public.apiBase}/settings/public`,
  { default: () => ({}) }
)

const logoUrl = computed(() => {
  const logoId = settings.value?.logo_id
  return logoId ? `${config.public.apiBase}/../../media/id/${logoId}` : null
})

function menuLink(item: MenuItem): string {
  if (item.page_slug) {
    return item.page_slug === 'home' ? '/' : '/' + item.page_slug
  }
  return item.link || '#'
}

// Scroll hide/show
const hidden = ref(false)
let lastScrollY = 0

function onScroll() {
  const currentY = window.scrollY
  hidden.value = currentY > lastScrollY && currentY > 80
  lastScrollY = currentY
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

// Mobile
const mobileOpen = ref(false)

function toggleLang() {
  locale.value = locale.value === 'zh' ? 'en' : 'zh'
}
</script>
```

- [ ] **Step 2: 验证 Header 渲染**

```bash
cd frontend && pnpm dev  # check header renders correctly
```

- [ ] **Step 3: Commit**

```bash
git add frontend/components/layout/AppHeader.vue
git commit -m "feat: rewrite AppHeader with Jinjieli design — glass, scroll hide, underline nav"
```

---

### Task 6: Frontend — AppFooter 重写

**Files:**
- Modify: `frontend/components/layout/AppFooter.vue`

- [ ] **Step 1: 重写 Footer 为 4 列网格布局**

```vue
<template>
  <footer class="bg-[#f5f7fa] border-t border-slate-200/60 pt-12 pb-8">
    <div class="container mx-auto px-6">
      <!-- Main grid -->
      <div class="grid grid-cols-1 md:grid-cols-12 gap-8 lg:gap-12 mb-10">
        <!-- Col 1: Logo + Description + Hotline -->
        <div class="md:col-span-12 lg:col-span-5 flex flex-col gap-5">
          <div class="space-y-3">
            <NuxtLink to="/" class="inline-flex items-center group">
              <img
                v-if="logoUrl"
                :src="logoUrl"
                alt="金捷利"
                class="h-10 md:h-11 w-auto object-contain"
              />
            </NuxtLink>
            <p class="text-slate-500 text-[13px] leading-relaxed max-w-sm">
              {{ settings?.company_description_zh || '' }}
            </p>
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-[10px] text-slate-400 font-semibold tracking-wider uppercase">
              7x24小时全国智能运维热线
            </span>
            <a :href="`tel:${settings?.hotline || ''}`"
              class="text-lg font-black tracking-tight text-slate-800 hover:text-brand-600 transition-colors">
              {{ settings?.hotline || '' }}
            </a>
          </div>
        </div>

        <!-- Cols 2-4: Menu groups -->
        <div class="md:col-span-12 lg:col-span-7 flex flex-col sm:flex-row sm:justify-end gap-8 sm:gap-x-16 lg:gap-x-20">
          <div v-for="group in footerGroups" :key="group.name" class="flex flex-col min-w-[120px] sm:text-right">
            <h4 class="text-slate-900 font-extrabold text-[14px] mb-4 tracking-wide">
              {{ locale === 'zh' ? group.name_zh : group.name_en }}
            </h4>
            <ul class="space-y-2.5 text-[13px] text-slate-500 font-medium">
              <li v-for="item in group.items" :key="item.id">
                <NuxtLink :to="menuLink(item)"
                  class="hover:text-brand-600 transition-colors duration-200 block">
                  {{ locale === 'zh' ? item.name_zh : item.name_en }}
                </NuxtLink>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="pt-6 border-t border-slate-200/70 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 text-xs text-slate-400">
        <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
          <span class="font-semibold text-slate-550">© 2026 {{ settings?.company_name_zh || '' }}</span>
          <span class="hidden sm:inline text-slate-300">|</span>
          <span class="text-slate-400/80 tracking-wider uppercase text-[10px]">All Rights Reserved.</span>
        </div>
        <div class="flex flex-wrap items-center gap-x-5 gap-y-2">
          <NuxtLink to="/privacy" class="hover:text-brand-600 hover:underline transition-colors">隐私政策</NuxtLink>
          <span class="inline-block w-1 h-1 rounded-full bg-slate-300"></span>
          <NuxtLink to="/terms" class="hover:text-brand-600 hover:underline transition-colors">法律声明</NuxtLink>
          <span v-if="settings?.icp_beian" class="inline-block w-1 h-1 rounded-full bg-slate-300"></span>
          <a v-if="settings?.icp_beian" href="https://beian.miit.gov.cn/" target="_blank" rel="noopener"
            class="hover:text-brand-600 hover:underline transition-colors">{{ settings.icp_beian }}</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
interface MenuItem {
  id: number; name_zh: string; name_en: string; link: string;
  page_slug: string | null; children: MenuItem[]
}

const { locale } = useI18n()
const config = useRuntimeConfig()

const { data: footerMenu } = await useFetch<MenuItem[]>(
  `${config.public.apiBase}/menus?location=footer`,
  { default: () => [] }
)
const { data: settings } = await useFetch<Record<string, string>>(
  `${config.public.apiBase}/settings/public`,
  { default: () => ({}) }
)

const logoUrl = computed(() => {
  const logoId = settings.value?.logo_id
  return logoId ? `${config.public.apiBase}/../../media/id/${logoId}` : null
})

// Group footer menu items: products, solutions, company
const footerGroups = computed(() => {
  const raw = footerMenu.value || []
  // Menu items with children = groups; top-level items without children = direct links
  // The seed creates parent menu items with children for each group
  return raw.map(g => ({
    name_zh: g.name_zh,
    name_en: g.name_en,
    items: g.children || [],
  }))
})

function menuLink(item: MenuItem): string {
  if (item.page_slug) return item.page_slug === 'home' ? '/' : '/' + item.page_slug
  return item.link || '#'
}
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/layout/AppFooter.vue
git commit -m "feat: rewrite AppFooter with 4-column grid, company info from settings"
```

---

### Task 7: Frontend — BlockHero 轮播升级

**Files:**
- Modify: `frontend/components/blocks/BlockHero.vue`

- [ ] **Step 1: 升级为多图轮播**

```vue
<template>
  <section class="relative min-h-[660px] md:min-h-[720px] lg:h-[86vh] lg:max-h-[800px] w-full overflow-hidden flex flex-col justify-center items-center text-white">
    <!-- Background image slides -->
    <div class="absolute inset-0 w-full h-full overflow-hidden bg-slate-900">
      <Transition name="fade" mode="out-in">
        <div :key="currentIndex" class="absolute inset-0">
          <img
            v-if="currentSlide?.image_url"
            :src="currentSlide.image_url"
            alt=""
            class="w-full h-full object-cover"
          />
          <div class="absolute inset-0 bg-black/12"></div>
        </div>
      </Transition>
    </div>

    <!-- Content -->
    <div class="relative z-10 text-center px-6 max-w-4xl mx-auto">
      <h1 class="text-4xl md:text-5xl lg:text-6xl font-extrabold mb-5 tracking-tight leading-tight drop-shadow-sm">
        {{ locale === 'zh' ? currentSlide?.title_zh : currentSlide?.title_en }}
      </h1>
      <p v-if="currentSlide?.subtitle_zh || currentSlide?.subtitle_en"
        class="text-lg md:text-xl mb-10 max-w-2xl mx-auto leading-relaxed text-white/85">
        {{ locale === 'zh' ? currentSlide?.subtitle_zh : currentSlide?.subtitle_en }}
      </p>
      <div v-if="currentSlide?.buttons?.length" class="flex gap-4 justify-center flex-wrap">
        <a v-for="(btn, i) in currentSlide.buttons" :key="i" :href="btn.link"
          :class="[
            'inline-flex items-center px-7 py-3 rounded-full text-sm font-semibold transition-all duration-300',
            i === 0
              ? 'bg-brand-600 text-white hover:bg-brand-700 hover:scale-105 shadow-lg shadow-brand-600/30'
              : 'border border-white/30 text-white hover:bg-white/10 hover:scale-105'
          ]">
          {{ locale === 'zh' ? btn.label_zh : btn.label_en }}
        </a>
      </div>
    </div>

    <!-- Navigation arrows -->
    <button v-if="slides.length > 1" @click="prev"
      class="absolute left-6 top-1/2 -translate-y-1/2 w-14 h-14 rounded-full border border-white/10 bg-black/30 hover:bg-black/60 backdrop-blur-md flex items-center justify-center text-white transition-all z-30 cursor-pointer">
      <ChevronLeftIcon class="w-7 h-7" />
    </button>
    <button v-if="slides.length > 1" @click="next"
      class="absolute right-6 top-1/2 -translate-y-1/2 w-14 h-14 rounded-full border border-white/10 bg-black/30 hover:bg-black/60 backdrop-blur-md flex items-center justify-center text-white transition-all z-30 cursor-pointer">
      <ChevronRightIcon class="w-7 h-7" />
    </button>

    <!-- Dots -->
    <div v-if="slides.length > 1" class="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-2 z-30">
      <button
        v-for="(_, i) in slides" :key="i"
        @click="goTo(i)"
        class="w-2.5 h-2.5 rounded-full transition-all duration-300 cursor-pointer"
        :class="i === currentIndex ? 'bg-white w-8' : 'bg-white/40 hover:bg-white/70'"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{ config: Record<string, any>; content: Record<string, any> }>()
const { locale } = useI18n()
const config = useRuntimeConfig()

interface Slide {
  image_id?: number
  image_url?: string
  title_zh?: string
  title_en?: string
  subtitle_zh?: string
  subtitle_en?: string
  buttons?: Array<{ label_zh: string; label_en: string; link: string }>
}

const slides = computed<Slide[]>(() => {
  const raw = props.content.slides
  if (!raw || !Array.isArray(raw)) {
    // Fallback: single slide from old format
    return [{
      image_id: props.content.bg_image,
      image_url: props.content.bg_image ? `${config.public.apiBase}/../../media/id/${props.content.bg_image}` : undefined,
      title_zh: props.content.title_zh,
      title_en: props.content.title_en,
      subtitle_zh: props.content.subtitle_zh,
      subtitle_en: props.content.subtitle_en,
      buttons: props.content.buttons || [],
    }]
  }
  return raw.map((s: any) => ({
    ...s,
    image_url: s.image_id ? `${config.public.apiBase}/../../media/id/${s.image_id}` : undefined,
  }))
})

const currentIndex = ref(0)
const currentSlide = computed(() => slides.value[currentIndex.value] || slides.value[0])

function next() { currentIndex.value = (currentIndex.value + 1) % slides.value.length }
function prev() { currentIndex.value = (currentIndex.value - 1 + slides.value.length) % slides.value.length }
function goTo(i: number) { currentIndex.value = i }

// Auto-play
let timer: ReturnType<typeof setInterval> | null = null
const interval = computed(() => props.content.auto_play_interval || 5000)

onMounted(() => {
  if (slides.value.length > 1) {
    timer = setInterval(next, interval.value)
  }
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.8s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/blocks/BlockHero.vue
git commit -m "feat: upgrade BlockHero to multi-slide carousel with auto-play"
```

---

### Task 8: Frontend — BlockSolutionCards 新增 + 其他 Block 样式对齐

**Files:**
- Create/Modify: `frontend/components/blocks/BlockSolutionCards.vue`
- Modify: `frontend/components/blocks/BlockProductCards.vue`
- Modify: `frontend/components/blocks/BlockNewsList.vue`
- Modify: `frontend/components/blocks/BlockFaq.vue`
- Modify: `frontend/components/blocks/BlockContactForm.vue`
- Modify: `frontend/components/blocks/BlockCtaBanner.vue`
- Modify: `frontend/components/blocks/BlockRichtext.vue`
- Modify: `frontend/components/blocks/BlockStatsCounter.vue`

- [ ] **Step 1: 新增 BlockSolutionCards Tab 组件**

Read current `frontend/components/blocks/BlockSolutionCards.vue`, then rewrite with Tab switching:

```vue
<template>
  <section class="py-20 md:py-28 bg-white">
    <div class="container mx-auto px-6">
      <!-- Section header -->
      <div class="text-center mb-14" v-if="content.title_zh">
        <h2 class="text-3xl md:text-4xl font-extrabold text-slate-900 mb-4">
          {{ locale === 'zh' ? content.title_zh : content.title_en }}
        </h2>
        <p v-if="content.subtitle_zh" class="text-lg text-slate-500 max-w-2xl mx-auto">
          {{ locale === 'zh' ? content.subtitle_zh : content.subtitle_en }}
        </p>
      </div>

      <!-- Tab buttons -->
      <div class="flex flex-wrap justify-center gap-2 mb-12">
        <button
          v-for="tab in tabs" :key="tab.key"
          @click="activeTab = tab.key"
          class="px-6 py-3 rounded-full text-sm font-semibold transition-all duration-300 cursor-pointer border"
          :class="activeTab === tab.key
            ? 'bg-brand-600 text-white border-brand-600 shadow-md shadow-brand-600/20'
            : 'bg-white text-slate-600 border-slate-200 hover:border-brand-300 hover:text-brand-600'"
        >
          {{ locale === 'zh' ? tab.title_zh : tab.title_en }}
        </button>
      </div>

      <!-- Active tab content -->
      <Transition name="fade" mode="out-in">
        <div :key="activeTab" class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <h3 class="text-2xl md:text-3xl font-bold text-slate-900 mb-6">
              {{ locale === 'zh' ? activeTabData?.title_zh : activeTabData?.title_en }}
            </h3>
            <ul class="space-y-4">
              <li v-for="(feat, i) in activeTabData?.features || []" :key="i"
                class="flex items-start gap-3 text-slate-600">
                <CheckCircleIcon class="w-5 h-5 text-brand-500 shrink-0 mt-0.5" />
                <span>{{ locale === 'zh' ? feat.text_zh : feat.text_en }}</span>
              </li>
            </ul>
          </div>
          <div class="relative">
            <img
              v-if="activeTabData?.image_url"
              :src="activeTabData.image_url"
              :alt="locale === 'zh' ? activeTabData.title_zh : activeTabData.title_en"
              class="w-full rounded-2xl shadow-lg object-cover aspect-[4/3]"
            />
            <div v-else class="w-full aspect-[4/3] rounded-2xl bg-slate-100 flex items-center justify-center text-slate-400">
              暂无图片
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </section>
</template>

<script setup lang="ts">
import { CheckCircleIcon } from '@heroicons/vue/24/outline'
import { ref, computed } from 'vue'

const props = defineProps<{ config: Record<string, any>; content: Record<string, any> }>()
const { locale } = useI18n()
const config = useRuntimeConfig()

interface Tab {
  key: string
  title_zh: string
  title_en: string
  image_id?: number
  image_url?: string
  features: Array<{ text_zh: string; text_en: string }>
}

const tabs = computed<Tab[]>(() => {
  const raw = props.content.tabs
  if (!raw || !Array.isArray(raw)) return []
  return raw.map((t: any) => ({
    ...t,
    image_url: t.image_id ? `${config.public.apiBase}/../../media/id/${t.image_id}` : undefined,
  }))
})

const activeTab = ref(tabs.value[0]?.key || '')
const activeTabData = computed(() => tabs.value.find(t => t.key === activeTab.value))
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
```

- [ ] **Step 2: 对齐其他 Block 组件样式**

For each Block component, replace all emerald/green color classes with brand blue equivalents:

| Old class | New class |
|---|---|
| `text-emerald-600`, `text-emerald-500` | `text-brand-600`, `text-brand-500` |
| `bg-emerald-50`, `bg-emerald-100` | `bg-brand-50`, `bg-brand-100` |
| `border-emerald-100`, `border-emerald-200` | `border-brand-100`, `border-brand-200` |
| `#059669`, `#10b981` | `#2563eb`, `#1d4ed8` |
| `from-emerald-*`, `to-emerald-*` | `from-brand-500`, `to-brand-600` |
| `shadow-emerald-*/10` | `shadow-brand-600/10` |
| `rgba(5,150,105,...)` | `rgba(37,99,235,...)` |

Apply to: BlockProductCards, BlockNewsList, BlockFaq, BlockContactForm, BlockCtaBanner, BlockRichtext, BlockStatsCounter. Also ensure rounded corners match (rounded-2xl, rounded-3xl) and shadows are softer.

- [ ] **Step 3: Commit**

```bash
git add frontend/components/blocks/
git commit -m "feat: add BlockSolutionCards with tabs, align all Blocks to blue brand theme"
```

---

### Task 9: Frontend — AI Chat 浮动按钮改造

**Files:**
- Modify: `frontend/components/chat/ChatFloatingButton.vue`
- Modify: `frontend/components/chat/ChatPanel.vue`

- [ ] **Step 1: 改造 ChatFloatingButton 为金捷利 AI 风格**

Rewrite with:
- Fixed bottom-right "AI" circle button (bg-brand-600, shadow-xl shadow-brand-600/30, hover:scale-110)
- Chat window: glass card, rounded-3xl, 580px height
- Header: "金捷利 AI 智能管家" + "24/7 Energy & IoT Advisor" subtitle
- Back-to-top button (visible after scrolling 300px)
- Preset quick-reply suggestions

```vue
<template>
  <div class="fixed bottom-8 right-8 z-50 flex flex-col items-center gap-3.5 pointer-events-none">
    <!-- Back to top -->
    <Transition name="fade-up">
      <button v-if="showBackToTop" @click="scrollToTop"
        class="w-12 h-12 bg-white/95 backdrop-blur-md text-slate-600 hover:text-brand-600 border border-slate-200/90 hover:border-brand-300 rounded-full flex items-center justify-center hover:scale-110 active:scale-95 transition-all shadow-lg cursor-pointer pointer-events-auto"
        title="返回顶部" aria-label="返回顶部">
        <ChevronUpIcon class="w-6 h-6 stroke-[2.5]" />
      </button>
    </Transition>

    <!-- AI floating button & window -->
    <button v-if="!isOpen" @click="isOpen = true"
      class="w-16 h-16 bg-brand-600 text-white rounded-full flex items-center justify-center hover:scale-110 active:scale-95 transition-all shadow-xl shadow-brand-600/30 cursor-pointer pointer-events-auto font-bold text-xl tracking-wider select-none">
      AI
    </button>

    <Transition name="fade-up">
      <div v-if="isOpen"
        class="w-[360px] md:w-[410px] h-[580px] bg-white/95 backdrop-blur-2xl rounded-3xl flex flex-col overflow-hidden shadow-[0_20px_50px_rgba(0,0,0,0.12)] border border-slate-200/80 pointer-events-auto">
        <!-- Header -->
        <div class="bg-slate-50 border-b border-slate-200/60 p-5 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-brand-50 flex items-center justify-center text-brand-600 border border-brand-100">
              <SparklesIcon class="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div class="font-bold text-sm text-slate-950 flex items-center gap-1.5">
                金捷利 AI 智能管家
              </div>
              <div class="text-[11px] text-slate-500 font-mono tracking-wider uppercase">
                24/7 Energy & IoT Advisor
              </div>
            </div>
          </div>
          <button @click="isOpen = false"
            class="w-8 h-8 rounded-lg border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-200 flex items-center justify-center transition-all cursor-pointer">
            <XMarkIcon class="w-4 h-4" />
          </button>
        </div>
        <!-- Chat content -->
        <div class="flex-1 overflow-hidden">
          <ChatPanel :embedded="true" />
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ChevronUpIcon, SparklesIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { ref, onMounted, onUnmounted } from 'vue'

const isOpen = ref(false)
const showBackToTop = ref(false)

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function onScroll() {
  showBackToTop.value = window.scrollY > 300
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
.fade-up-enter-active, .fade-up-leave-active { transition: all 0.3s ease; }
.fade-up-enter-from, .fade-up-leave-to { opacity: 0; transform: translateY(15px) scale(0.95); }
</style>
```

- [ ] **Step 2: 对齐 ChatPanel 样式**

将 ChatPanel 内的品牌色从 emerald 改为 blue，glass 效果增强。

- [ ] **Step 3: Commit**

```bash
git add frontend/components/chat/
git commit -m "feat: rewrite AI chat with floating button, back-to-top, Jinjieli branding"
```

---

### Task 10: Frontend — /cases 前端页面

**Files:**
- Create: `frontend/pages/cases/index.vue`
- Create: `frontend/pages/cases/[slug].vue`

- [ ] **Step 1: 创建案例列表页**

Write `frontend/pages/cases/index.vue`:
```vue
<template>
  <div>
    <!-- Hero -->
    <section class="relative min-h-[40vh] flex items-center justify-center bg-slate-900 overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-b from-slate-950/30 to-slate-950/50" />
      <div class="relative z-10 text-center text-white px-6">
        <h1 class="text-4xl md:text-5xl font-extrabold mb-4">
          {{ locale === 'zh' ? '服务案例' : 'Case Studies' }}
        </h1>
        <p class="text-lg text-white/70 max-w-xl mx-auto">
          {{ locale === 'zh' ? '以技术赋能建筑全生命周期，见证每一个成功案例' : 'Witness every successful case empowered by technology' }}
        </p>
      </div>
    </section>

    <!-- Category filter -->
    <section class="py-12">
      <div class="container mx-auto px-6">
        <div class="flex flex-wrap justify-center gap-2 mb-10">
          <button
            v-for="cat in categories" :key="cat.key"
            @click="activeCategory = activeCategory === cat.key ? '' : cat.key"
            class="px-5 py-2.5 rounded-full text-sm font-semibold transition-all cursor-pointer border"
            :class="activeCategory === cat.key
              ? 'bg-brand-600 text-white border-brand-600'
              : 'bg-white text-slate-600 border-slate-200 hover:border-brand-300 hover:text-brand-600'"
          >
            {{ locale === 'zh' ? cat.label_zh : cat.label_en }}
          </button>
        </div>

        <!-- Case cards grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <NuxtLink
            v-for="c in cases" :key="c.id"
            :to="`/cases/${c.slug}`"
            class="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 border border-slate-100 hover:border-brand-100"
          >
            <div class="aspect-[16/10] bg-slate-100 overflow-hidden">
              <img
                v-if="c.cover_image_id"
                :src="`${apiBase}/../../media/id/${c.cover_image_id}`"
                :alt="locale === 'zh' ? c.name_zh : c.name_en"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-slate-400">暂无图片</div>
            </div>
            <div class="p-6">
              <span class="text-xs font-bold text-brand-600 uppercase tracking-wider">
                {{ categoryLabel(c.category) }}
              </span>
              <h3 class="text-lg font-bold text-slate-900 mt-2 mb-2 group-hover:text-brand-600 transition-colors">
                {{ locale === 'zh' ? c.name_zh : c.name_en }}
              </h3>
              <p class="text-sm text-slate-500 line-clamp-2">
                {{ locale === 'zh' ? c.summary_zh : c.summary_en }}
              </p>
            </div>
          </NuxtLink>
        </div>

        <!-- Empty -->
        <div v-if="cases.length === 0 && !pending" class="text-center py-20 text-slate-400">
          暂无案例
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const activeCategory = ref('')
const route = useRoute()

const categories = [
  { key: 'park', label_zh: '产业园区', label_en: 'Industrial Park' },
  { key: 'medical', label_zh: '医疗建筑', label_en: 'Medical' },
  { key: 'office', label_zh: '写字楼', label_en: 'Office' },
  { key: 'commercial', label_zh: '商业综合体', label_en: 'Commercial' },
]

const { data: result, pending } = await useAsyncData(
  'cases',
  () => $fetch(`${apiBase}/cases`, {
    query: {
      page: 1,
      size: 12,
      category: activeCategory.value || undefined,
    },
  }),
  { watch: [activeCategory] }
)

const cases = computed(() => (result.value as any)?.items || [])

function categoryLabel(key: string): string {
  const cat = categories.find(c => c.key === key)
  return cat ? (locale.value === 'zh' ? cat.label_zh : cat.label_en) : key
}
</script>
```

- [ ] **Step 2: 创建案例详情页**

Write `frontend/pages/cases/[slug].vue`:
```vue
<template>
  <div v-if="c">
    <!-- Hero -->
    <section class="relative min-h-[40vh] flex items-center justify-center bg-slate-900 overflow-hidden">
      <img v-if="c.cover_image_id" :src="`${apiBase}/../../media/id/${c.cover_image_id}`"
        class="absolute inset-0 w-full h-full object-cover opacity-30" alt="" />
      <div class="absolute inset-0 bg-gradient-to-t from-slate-950/60 to-slate-950/20" />
      <div class="relative z-10 text-center text-white px-6 max-w-4xl">
        <span class="text-sm font-bold text-brand-300 uppercase tracking-wider">{{ categoryLabel(c.category) }}</span>
        <h1 class="text-3xl md:text-4xl font-extrabold mt-3 mb-4">
          {{ locale === 'zh' ? c.name_zh : c.name_en }}
        </h1>
        <p class="text-lg text-white/70 max-w-2xl mx-auto">
          {{ locale === 'zh' ? c.summary_zh : c.summary_en }}
        </p>
      </div>
    </section>

    <!-- Stats -->
    <section v-if="c.stats?.length" class="py-12 bg-white border-b border-slate-100">
      <div class="container mx-auto px-6">
        <div class="flex flex-wrap justify-center gap-8 md:gap-16">
          <div v-for="s in c.stats" :key="s.label" class="text-center">
            <div class="text-3xl md:text-4xl font-extrabold text-brand-600">{{ s.value }}</div>
            <div class="text-sm text-slate-500 mt-1">{{ s.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Content -->
    <section class="py-16">
      <div class="container mx-auto px-6 max-w-3xl">
        <div class="prose prose-slate max-w-none" v-html="locale === 'zh' ? c.content_zh : c.content_en" />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const route = useRoute()

const { data: c } = await useAsyncData('case-detail', () =>
  $fetch(`${apiBase}/cases/${route.params.slug}`)
)

const categories = [
  { key: 'park', label_zh: '产业园区', label_en: 'Industrial Park' },
  { key: 'medical', label_zh: '医疗建筑', label_en: 'Medical' },
  { key: 'office', label_zh: '写字楼', label_en: 'Office' },
  { key: 'commercial', label_zh: '商业综合体', label_en: 'Commercial' },
]

function categoryLabel(key: string): string {
  const cat = categories.find(c => c.key === key)
  return cat ? (locale.value === 'zh' ? cat.label_zh : cat.label_en) : key
}
</script>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/pages/cases/
git commit -m "feat: add /cases list and detail pages"
```

---

### Task 11: Frontend — 管理端 cases.vue

**Files:**
- Create: `frontend/pages/admin/cases.vue`

- [ ] **Step 1: 创建案例管理页面**

参照 `frontend/pages/admin/products.vue` 的模式，实现 Case CRUD:

- 表格列表（名称、分类、排序、发布时间、状态）
- 新建/编辑表单（含中英文名称、slug、分类下拉、封面图选择、摘要、内容富文本、Stats JSON编辑器、排序号、发布开关）
- 删除确认

- [ ] **Step 2: Commit**

```bash
git add frontend/pages/admin/cases.vue
git commit -m "feat: add admin cases CRUD page"
```

---

### Task 12: 验证与设计走查

- [ ] **Step 1: 启动后端**

```bash
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8002
```

- [ ] **Step 2: 启动前端**

```bash
cd frontend && pnpm dev
```

- [ ] **Step 3: 验证关键路由**

访问并检查:
- `/` — 首页: Hero 轮播、服务卡片、方案 Tab、新闻列表、CTA
- `/products` — 产品列表
- `/solutions` — 方案 Tab 切换
- `/cases` — 案例列表 + 详情
- `/news` — 新闻列表
- `/about` — 关于我们
- `/contact` — 联系我们
- `/cooperation` — 商务合作
- Header sticky + scroll 显隐动画
- Footer 4 列网格
- AI 浮动按钮 + 对话窗口
- 中英文切换

- [ ] **Step 4: 验证管理端**

访问 `/admin/`:
- 页面管理 → 编辑各页面 Blocks（确认 Hero slides、Solution tabs 可编辑）
- 案例管理 → CRUD
- 设置 → 公司信息字段
- 菜单管理 → Header/Footer 菜单

- [ ] **Step 5: 修复问题并提交**

```bash
git add -A && git commit -m "fix: design walkthrough fixes"
```
