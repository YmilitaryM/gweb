# Audit Log Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add admin operation audit logging — record create/update/delete actions, viewable as a filterable table with CSV export in the admin panel.

**Architecture:** New `audit` backend app with model + service + router. Audit log calls are made from existing admin routers after successful operations (router layer has access to Request for IP and current user). One new frontend admin page + dashboard link.

**Tech Stack:** FastAPI, SQLAlchemy async, Nuxt 3 (Vue), PostgreSQL

---

### Task 1: Create audit backend app (model + service + router)

**Files:**
- Create: `backend/app/apps/audit/__init__.py`
- Create: `backend/app/apps/audit/models.py`
- Create: `backend/app/apps/audit/service.py`
- Create: `backend/app/apps/audit/schemas.py`
- Create: `backend/app/apps/audit/router.py`

- [ ] **Step 1: Create `__init__.py`**

```bash
touch backend/app/apps/audit/__init__.py
```

- [ ] **Step 2: Write AuditLog model**

```python
# backend/app/apps/audit/models.py
from sqlalchemy import String, Integer, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.models import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resource_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **Step 3: Write audit service**

```python
# backend/app/apps/audit/service.py
import csv
import io
from datetime import datetime, timezone

from sqlalchemy import select, func
from app.core.database import async_session
from app.apps.audit.models import AuditLog


async def create_audit_log(
    user_id: int,
    username: str,
    action: str,
    resource_type: str,
    resource_id: int | None = None,
    resource_name: str | None = None,
    detail: dict | None = None,
    ip_address: str | None = None,
):
    async with async_session() as db:
        log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            detail=detail,
            ip_address=ip_address,
        )
        db.add(log)
        await db.commit()


async def list_audit_logs(
    page: int = 1,
    size: int = 20,
    user_id: int | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> tuple[list[AuditLog], int]:
    async with async_session() as db:
        query = select(AuditLog)
        count_query = select(func.count(AuditLog.id))

        if user_id is not None:
            query = query.where(AuditLog.user_id == user_id)
            count_query = count_query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
            count_query = count_query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
            count_query = count_query.where(AuditLog.resource_type == resource_type)
        if start_date:
            start_dt = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
            query = query.where(AuditLog.created_at >= start_dt)
            count_query = count_query.where(AuditLog.created_at >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
            query = query.where(AuditLog.created_at <= end_dt)
            count_query = count_query.where(AuditLog.created_at <= end_dt)

        result_total = await db.execute(count_query)
        total = result_total.scalar() or 0

        query = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * size).limit(size)
        result = await db.execute(query)
        return list(result.scalars().all()), total


async def export_csv_data(
    user_id: int | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    async with async_session() as db:
        query = select(AuditLog)
        if user_id is not None:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if start_date:
            start_dt = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
            query = query.where(AuditLog.created_at >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
            query = query.where(AuditLog.created_at <= end_dt)

        query = query.order_by(AuditLog.created_at.desc())
        result = await db.execute(query)
        logs = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "时间", "用户ID", "用户名", "操作", "资源类型", "资源ID", "资源名称", "详情", "IP地址"])
    for log in logs:
        writer.writerow([
            log.id,
            log.created_at.isoformat() if log.created_at else "",
            log.user_id,
            log.username,
            log.action,
            log.resource_type,
            log.resource_id or "",
            log.resource_name or "",
            str(log.detail) if log.detail else "",
            log.ip_address or "",
        ])
    return output.getvalue()
```

- [ ] **Step 4: Write schemas**

```python
# backend/app/apps/audit/schemas.py
from pydantic import BaseModel
from datetime import datetime


class AuditLogOut(BaseModel):
    id: int
    user_id: int
    username: str
    action: str
    resource_type: str
    resource_id: int | None
    resource_name: str | None
    detail: dict | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 5: Write router**

```python
# backend/app/apps/audit/router.py
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response

from app.apps.audit.schemas import AuditLogOut
from app.apps.audit.service import create_audit_log, list_audit_logs, export_csv_data
from app.apps.auth.router import get_current_user

router = APIRouter(
    prefix="/api/v1/admin/audit-logs",
    tags=["admin-audit"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
async def list_logs(
    page: int = 1,
    size: int = 20,
    user_id: int | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    items, total = await list_audit_logs(
        page=page, size=size, user_id=user_id, action=action,
        resource_type=resource_type, start_date=start_date, end_date=end_date,
    )
    return {
        "items": [AuditLogOut.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "size": size,
    }


@router.get("/export")
async def export_logs(
    user_id: int | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    csv_content = await export_csv_data(
        user_id=user_id, action=action,
        resource_type=resource_type, start_date=start_date, end_date=end_date,
    )
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )
```

- [ ] **Step 6: Register router in main.py**

```python
# backend/app/main.py — add after existing imports:
from app.apps.audit.router import router as audit_router

# Add after existing include_router calls:
app.include_router(audit_router)
```

- [ ] **Step 7: Commit**

```bash
git add backend/app/apps/audit/ backend/app/main.py
git commit -m "feat: add audit log backend (model, service, router)"
```

---

### Task 2: Add audit log calls to news router

**Files:**
- Modify: `backend/app/apps/news/router.py`

- [ ] **Step 1: Add imports and request param, call audit log after mutations**

```python
# backend/app/apps/news/router.py
# Add at top after existing imports:
from fastapi import Request
from app.apps.audit.service import create_audit_log

# Modify admin_create_article to accept request and log:
@admin_router.post("", response_model=NewsResponse, status_code=201)
async def admin_create_article(data: NewsCreate, request: Request, current_user=Depends(get_current_user)):
    article = await create_article(**data.model_dump())
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="create",
        resource_type="news",
        resource_id=article.id,
        resource_name=article.title_zh,
        ip_address=request.client.host if request.client else None,
    )
    return article

# Modify admin_update_article:
@admin_router.put("/{article_id}", response_model=NewsResponse)
async def admin_update_article(article_id: int, data: NewsUpdate, request: Request, current_user=Depends(get_current_user)):
    article = await update_article(article_id, **data.model_dump(exclude_none=True))
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="news",
        resource_id=article.id,
        resource_name=article.title_zh,
        ip_address=request.client.host if request.client else None,
    )
    return article

# Modify admin_delete_article:
@admin_router.delete("/{article_id}")
async def admin_delete_article(article_id: int, request: Request, current_user=Depends(get_current_user)):
    article = await get_article_by_id(article_id)
    name = article.title_zh if article else None
    deleted = await delete_article(article_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Article not found")
    await create_audit_log(
        user_id=current_user.id,
        username=current_user.username,
        action="delete",
        resource_type="news",
        resource_id=article_id,
        resource_name=name,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True}
```

- [ ] **Step 2: Verify existing import of get_article_by_id is present in router**

    The router currently only imports service functions used. Add `get_article_by_id` to the import from news.service.

- [ ] **Step 3: Commit**

```bash
git add backend/app/apps/news/router.py
git commit -m "feat: add audit log calls to news admin operations"
```

---

### Task 3: Add audit log calls to CMS router (pages, media, menus)

**Files:**
- Modify: `backend/app/apps/cms/router.py`

- [ ] **Step 1: Add Request import and audit log to page CRUD endpoints**

In `backend/app/apps/cms/router.py`, add `from fastapi import Request` and `from app.apps.audit.service import create_audit_log`. Then add `request: Request, current_user=Depends(get_current_user)` to each admin endpoint and insert audit log calls after successful operations:

- `admin_create_page` — after create: action="create", resource_type="page"
- `admin_update_page` — after update: action="update", resource_type="page"
- `admin_delete_page` — after delete (fetch page name first): action="delete", resource_type="page"
- `admin_create_block` — after create: action="create", resource_type="block"
- `admin_update_block` — after update: action="update", resource_type="block"
- `admin_delete_block` — after delete: action="delete", resource_type="block"
- `upload` (media) — after upload: action="create", resource_type="media"
- `delete_media_endpoint` — after delete: action="delete", resource_type="media"
- `admin_create_menu` — after create: action="create", resource_type="menu"
- `admin_update_menu` — after update: action="update", resource_type="menu"
- `admin_delete_menu` — after delete: action="delete", resource_type="menu"

- [ ] **Step 2: Commit**

```bash
git add backend/app/apps/cms/router.py
git commit -m "feat: add audit log calls to CMS admin operations"
```

---

### Task 4: Add audit log calls to users, settings, inquiry routers

**Files:**
- Modify: `backend/app/apps/users/router.py`
- Modify: `backend/app/apps/settings/router.py`
- Modify: `backend/app/apps/inquiry/router.py`

- [ ] **Step 1: Users router**

Add `from fastapi import Request` and `from app.apps.audit.service import create_audit_log`. Add `request: Request` to create_user, update_user, delete_user endpoints. Log after each successful operation:

- `create_user` — resource_type="user", resource_name=data.username
- `update_user` — resource_type="user"  
- `delete_user` — resource_type="user"

- [ ] **Step 2: Settings router**

Add `request: Request` to `update_setting`. Log after `set_setting`:
- resource_type="setting", resource_name=key, action="update"

- [ ] **Step 3: Inquiry router — check if inquiry router has admin endpoints**

Read `backend/app/apps/inquiry/router.py` to find admin endpoints. If there's a mark_read endpoint, add audit log there.

- [ ] **Step 4: Commit**

```bash
git add backend/app/apps/users/router.py backend/app/apps/settings/router.py backend/app/apps/inquiry/router.py
git commit -m "feat: add audit log calls to users, settings, inquiry operations"
```

---

### Task 5: Create admin audit-logs frontend page

**Files:**
- Create: `frontend/pages/admin/audit-logs.vue`
- Modify: `frontend/pages/admin/index.vue`

- [ ] **Step 1: Write the audit-logs page**

```vue
<!-- frontend/pages/admin/audit-logs.vue -->
<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: rgba(255,255,255,0.25);">
      &larr; 返回控制台
    </NuxtLink>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light text-white tracking-tight mb-1">审计日志</h2>
        <p class="text-[13px]" style="color: rgba(255,255,255,0.25);">查看管理员和编辑者的操作记录</p>
      </div>
      <button
        @click="exportCsv"
        class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all duration-200 hover:translate-y-[-1px]"
        style="background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 2px 12px rgba(5,150,105,0.2);"
      >
        导出 CSV
      </button>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-3 mb-5">
      <select v-model="filters.action" @change="fetchLogs" class="py-2 px-3 text-[13px] text-white outline-none rounded-lg appearance-none" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);">
        <option value="">全部操作</option>
        <option value="create">创建</option>
        <option value="update">编辑</option>
        <option value="delete">删除</option>
      </select>
      <select v-model="filters.resource_type" @change="fetchLogs" class="py-2 px-3 text-[13px] text-white outline-none rounded-lg appearance-none" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);">
        <option value="">全部资源</option>
        <option value="news">新闻</option>
        <option value="page">页面</option>
        <option value="media">媒体</option>
        <option value="menu">菜单</option>
        <option value="user">用户</option>
        <option value="setting">设置</option>
        <option value="inquiry">咨询</option>
        <option value="block">区块</option>
      </select>
      <input v-model="filters.start_date" type="date" @change="fetchLogs" class="py-2 px-3 text-[13px] text-white outline-none rounded-lg" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);" />
      <span class="text-[12px]" style="color: rgba(255,255,255,0.2);">至</span>
      <input v-model="filters.end_date" type="date" @change="fetchLogs" class="py-2 px-3 text-[13px] text-white outline-none rounded-lg" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);" />
    </div>

    <div v-if="loading" class="text-[13px] py-12 text-center" style="color: rgba(255,255,255,0.25);">加载中...</div>

    <div
      v-else-if="error"
      class="mb-6 px-4 py-3 rounded-lg text-[13px]"
      style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;"
    >
      {{ error }}
    </div>

    <template v-else>
      <div v-if="logs.length === 0" class="text-[13px] py-12 text-center" style="color: rgba(255,255,255,0.25);">
        暂无日志
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="log in logs"
          :key="log.id"
          class="flex items-center justify-between px-5 py-3 rounded-xl cursor-pointer transition-colors"
          style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);"
          @click="detail = log"
        >
          <div class="flex items-center gap-5 flex-1 min-w-0">
            <span class="text-[12px] flex-shrink-0 w-36" style="color: rgba(255,255,255,0.3); font-variant-numeric: tabular-nums;">
              {{ new Date(log.created_at).toLocaleString('zh-CN') }}
            </span>
            <span class="text-[13px] text-white flex-shrink-0 w-20">{{ log.username }}</span>
            <span
              class="text-[11px] px-2 py-0.5 rounded-full flex-shrink-0 w-12 text-center"
              :style="actionStyle(log.action)"
            >
              {{ actionLabel(log.action) }}
            </span>
            <span class="text-[12px] flex-shrink-0 w-16" style="color: rgba(255,255,255,0.25);">{{ resourceLabel(log.resource_type) }}</span>
            <span class="text-[13px] truncate" style="color: rgba(255,255,255,0.6);">{{ log.resource_name || '—' }}</span>
          </div>
          <span class="text-[11px] flex-shrink-0 ml-4" style="color: rgba(255,255,255,0.15);">{{ log.ip_address || '' }}</span>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
        <button
          v-for="p in totalPages"
          :key="p"
          @click="page = p; fetchLogs()"
          class="text-[12px] border-none cursor-pointer w-8 h-8 rounded-lg transition-colors"
          :style="p === page ? 'background: rgba(5,150,105,0.15); color: #34d399;' : 'background: rgba(255,255,255,0.02); color: rgba(255,255,255,0.35);'"
        >
          {{ p }}
        </button>
      </div>
    </template>

    <!-- Detail Modal -->
    <div
      v-if="detail"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
      @click.self="detail = null"
    >
      <div
        class="rounded-2xl p-6 w-full max-w-lg mx-4"
        style="background: #11161e; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 20px 60px rgba(0,0,0,0.5);"
      >
        <h3 class="text-[15px] font-medium text-white mb-5">操作详情</h3>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <div class="text-[11px] tracking-wider uppercase mb-1" style="color: rgba(255,255,255,0.25);">操作用户</div>
              <div class="text-[14px] text-white">{{ detail.username }}</div>
            </div>
            <div>
              <div class="text-[11px] tracking-wider uppercase mb-1" style="color: rgba(255,255,255,0.25);">操作类型</div>
              <div class="text-[14px] text-white">{{ actionLabel(detail.action) }}</div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <div class="text-[11px] tracking-wider uppercase mb-1" style="color: rgba(255,255,255,0.25);">资源类型</div>
              <div class="text-[14px] text-white">{{ resourceLabel(detail.resource_type) }}</div>
            </div>
            <div>
              <div class="text-[11px] tracking-wider uppercase mb-1" style="color: rgba(255,255,255,0.25);">资源名称</div>
              <div class="text-[14px] text-white">{{ detail.resource_name || '—' }}</div>
            </div>
          </div>
          <div>
            <div class="text-[11px] tracking-wider uppercase mb-1" style="color: rgba(255,255,255,0.25);">操作时间</div>
            <div class="text-[14px] text-white">{{ new Date(detail.created_at).toLocaleString('zh-CN') }}</div>
          </div>
          <div v-if="detail.ip_address">
            <div class="text-[11px] tracking-wider uppercase mb-1" style="color: rgba(255,255,255,0.25);">IP 地址</div>
            <div class="text-[14px] text-white">{{ detail.ip_address }}</div>
          </div>
          <div v-if="detail.detail">
            <div class="text-[11px] tracking-wider uppercase mb-1" style="color: rgba(255,255,255,0.25);">变更详情</div>
            <pre class="text-[13px] text-white leading-relaxed whitespace-pre-wrap font-mono p-3 rounded-lg" style="background: rgba(255,255,255,0.04);">{{ JSON.stringify(detail.detail, null, 2) }}</pre>
          </div>
        </div>
        <div class="flex justify-end pt-5 mt-2" style="border-top: 1px solid rgba(255,255,255,0.04);">
          <button
            @click="detail = null"
            class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg"
            style="color: rgba(255,255,255,0.4); background: rgba(255,255,255,0.04);"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['admin-auth'] });

const config = useRuntimeConfig();
const apiBase = config.public.apiBase as string;

const getHeaders = () => {
  const token = import.meta.client ? localStorage.getItem('admin_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

interface AuditLog {
  id: number;
  user_id: number;
  username: string;
  action: string;
  resource_type: string;
  resource_id: number | null;
  resource_name: string | null;
  detail: Record<string, any> | null;
  ip_address: string | null;
  created_at: string;
}

const logs = ref<AuditLog[]>([]);
const loading = ref(true);
const error = ref('');
const page = ref(1);
const totalPages = ref(1);
const detail = ref<AuditLog | null>(null);

const filters = ref({
  action: '',
  resource_type: '',
  start_date: '',
  end_date: '',
});

const actionLabel = (a: string) => {
  const map: Record<string, string> = { create: '创建', update: '编辑', delete: '删除' };
  return map[a] || a;
};

const actionStyle = (a: string) => {
  const colors: Record<string, string> = {
    create: 'background: rgba(5,150,105,0.12); color: #34d399;',
    update: 'background: rgba(2,132,199,0.12); color: #38bdf8;',
    delete: 'background: rgba(239,68,68,0.12); color: #f87171;',
  };
  return colors[a] || colors.create;
};

const resourceLabel = (r: string) => {
  const map: Record<string, string> = {
    news: '新闻', page: '页面', media: '媒体', menu: '菜单',
    user: '用户', setting: '设置', inquiry: '咨询', block: '区块',
  };
  return map[r] || r;
};

const buildParams = () => {
  const params: Record<string, any> = { page: page.value, size: 20 };
  if (filters.value.action) params.action = filters.value.action;
  if (filters.value.resource_type) params.resource_type = filters.value.resource_type;
  if (filters.value.start_date) params.start_date = filters.value.start_date;
  if (filters.value.end_date) params.end_date = filters.value.end_date;
  return params;
};

const fetchLogs = async () => {
  loading.value = true;
  error.value = '';
  try {
    const params = buildParams();
    const qs = new URLSearchParams(params as any).toString();
    const data = await $fetch<{ items: AuditLog[]; total: number; page: number; size: number }>(
      `${apiBase}/admin/audit-logs?${qs}`,
      { headers: getHeaders() }
    );
    logs.value = data.items;
    totalPages.value = Math.ceil(data.total / data.size);
  } catch (e: any) {
    error.value = e?.data?.detail || '加载日志失败';
  } finally {
    loading.value = false;
  }
};

const exportCsv = async () => {
  try {
    const params: Record<string, any> = {};
    if (filters.value.action) params.action = filters.value.action;
    if (filters.value.resource_type) params.resource_type = filters.value.resource_type;
    if (filters.value.start_date) params.start_date = filters.value.start_date;
    if (filters.value.end_date) params.end_date = filters.value.end_date;
    const qs = new URLSearchParams(params as any).toString();
    const blob = await $fetch<Blob>(`${apiBase}/admin/audit-logs/export?${qs}`, {
      headers: { ...getHeaders(), 'Content-Type': 'text/csv' },
    });
    const url = window.URL.createObjectURL(new Blob([blob], { type: 'text/csv' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = 'audit_logs.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  } catch {}
};

onMounted(fetchLogs);
</script>
```

- [ ] **Step 2: Add audit log link to admin dashboard**

In `frontend/pages/admin/index.vue`, add to the `links` array inside `<script setup>`:

```typescript
{ to: '/admin/audit-logs', label: '审计日志', desc: '查看管理员操作记录' },
```

Add it after the inquiries link and before the settings link.

- [ ] **Step 3: Commit**

```bash
git add frontend/pages/admin/audit-logs.vue frontend/pages/admin/index.vue
git commit -m "feat: add audit log admin page with filters and CSV export"
```

---

### Task 6: Verify and test

- [ ] **Step 1: Start backend and verify API**

```bash
cd backend && python -m uvicorn app.main:app --reload --port 8000
```

```bash
# Test list endpoint
curl -s -H "Authorization: Bearer <token>" "http://localhost:8000/api/v1/admin/audit-logs?page=1&size=20" | python -m json.tool
```

- [ ] **Step 2: Start frontend and test UI**

```bash
cd frontend && npm run dev
```

Navigate to `/admin/audit-logs`, verify: page loads, filters work, detail modal opens, export downloads CSV.

- [ ] **Step 3: Perform an admin action and verify log appears**

Create a news article via admin, then check audit-logs page to confirm the action was recorded.

- [ ] **Step 4: Commit any fixes**

```bash
git add -A
git commit -m "fix: audit log verification fixes"
```
