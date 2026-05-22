# User Management System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add complete user management (CRUD + extended profile fields) to the admin backend.

**Architecture:** New `apps/users/` module (router + service + schemas) for CRUD endpoints, extend existing `User` model with profile fields, add `require_admin` guard, and add a Vue admin page.

**Tech Stack:** FastAPI, SQLAlchemy async, Pydantic v2, Vue 3 + Nuxt 3, TypeScript

---

### Task 1: Extend User model with profile fields

**Files:**
- Modify: `backend/app/apps/auth/models.py`
- Modify: `backend/app/apps/auth/service.py`
- Modify: `backend/app/apps/auth/schemas.py`

- [ ] **Step 1: Add profile columns to User model**

Add four nullable columns to `backend/app/apps/auth/models.py`:

```python
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.models import Base, TimestampMixin
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    editor = "editor"


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.editor)
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
```

- [ ] **Step 2: Update create_user in auth/service.py to accept new fields**

Replace the `create_user` function in `backend/app/apps/auth/service.py`:

```python
from sqlalchemy import select
from app.core.database import async_session
from app.core.security import hash_password, verify_password, create_access_token
from app.apps.auth.models import User, UserRole


async def create_user(
    username: str,
    password: str,
    role: str = "editor",
    display_name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    avatar: str | None = None,
) -> User:
    async with async_session() as db:
        user = User(
            username=username,
            password_hash=hash_password(password),
            role=UserRole(role),
            display_name=display_name,
            phone=phone,
            email=email,
            avatar=avatar,
        )
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
```

- [ ] **Step 3: Update UserOut schema with new fields**

Replace `UserOut` in `backend/app/apps/auth/schemas.py`:

```python
from datetime import datetime
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    display_name: str | None = None
    phone: str | None = None
    email: str | None = None
    avatar: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: Update conftest.py to create admin role user for testing**

In `backend/tests/conftest.py`, the `auth_headers` fixture creates user with default "editor" role. Add an `admin_auth_headers` fixture:

```python
@pytest_asyncio.fixture
async def admin_auth_headers(client):
    from app.apps.auth.service import create_user

    await create_user("admin", "password123", "admin")
    resp = await client.post(
        "/api/v1/admin/auth/login", json={"username": "admin", "password": "password123"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

Append this after the existing `auth_headers` fixture (after line 39).

- [ ] **Step 5: Run existing tests to verify no regressions**

```bash
cd backend && python -m pytest tests/ -v
```

Expected: all existing tests pass.

- [ ] **Step 6: Commit**

```bash
git add backend/app/apps/auth/models.py backend/app/apps/auth/service.py backend/app/apps/auth/schemas.py backend/tests/conftest.py
git commit -m "feat: extend User model with avatar, display_name, phone, email fields"
```

---

### Task 2: Add require_admin dependency

**Files:**
- Modify: `backend/app/apps/auth/router.py`

- [ ] **Step 1: Add require_admin dependency**

In `backend/app/apps/auth/router.py`, add `require_admin` after the existing `get_current_user` function (before the route decorators). Also add the `UserRole` import:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.apps.auth.schemas import LoginRequest, TokenResponse, UserOut
from app.apps.auth.service import authenticate, get_user_by_id
from app.apps.auth.models import UserRole
from app.core.security import decode_token

router = APIRouter(prefix="/api/v1/admin/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(credentials.credentials)
        user_id = int(payload["sub"])
        user = await get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


async def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    token = await authenticate(data.username, data.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(current_user=Depends(get_current_user)):
    return current_user
```

- [ ] **Step 2: Run tests to verify**

```bash
cd backend && python -m pytest tests/ -v
```

Expected: all pass.

- [ ] **Step 3: Commit**

```bash
git add backend/app/apps/auth/router.py
git commit -m "feat: add require_admin dependency for role-based access"
```

---

### Task 3: Create users schemas

**Files:**
- Create: `backend/app/apps/users/__init__.py`
- Create: `backend/app/apps/users/schemas.py`

- [ ] **Step 1: Create __init__.py**

Create empty `backend/app/apps/users/__init__.py`:

```python
```

- [ ] **Step 2: Create schemas**

Create `backend/app/apps/users/schemas.py`:

```python
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
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/apps/users/__init__.py backend/app/apps/users/schemas.py
git commit -m "feat: add users schemas — UserCreate, UserUpdate"
```

---

### Task 4: Create users service

**Files:**
- Create: `backend/app/apps/users/service.py`

- [ ] **Step 1: Create service**

Create `backend/app/apps/users/service.py`:

```python
from sqlalchemy import select, delete as sql_delete
from app.core.database import async_session
from app.core.security import hash_password
from app.apps.auth.models import User, UserRole
from app.apps.auth.service import create_user as auth_create_user, get_user_by_id


async def list_users() -> list[User]:
    async with async_session() as db:
        result = await db.execute(select(User).order_by(User.id))
        return list(result.scalars().all())


async def create_user(**kwargs) -> User:
    return await auth_create_user(**kwargs)


async def update_user(user_id: int, **kwargs) -> User | None:
    user = await get_user_by_id(user_id)
    if user is None:
        return None
    async with async_session() as db:
        merged = await db.merge(user)
        if "password" in kwargs and kwargs["password"]:
            merged.password_hash = hash_password(kwargs.pop("password"))
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/apps/users/service.py
git commit -m "feat: add users service — list, create, update, delete"
```

---

### Task 5: Create users router

**Files:**
- Create: `backend/app/apps/users/router.py`

- [ ] **Step 1: Create router**

Create `backend/app/apps/users/router.py`:

```python
from fastapi import APIRouter, Depends, HTTPException

from app.apps.auth.router import require_admin, get_current_user
from app.apps.auth.schemas import UserOut
from app.apps.users.schemas import UserCreate, UserUpdate
from app.apps.users import service as users_svc

router = APIRouter(
    prefix="/api/v1/admin/users",
    tags=["admin-users"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=list[UserOut])
async def list_users():
    return await users_svc.list_users()


@router.post("", response_model=UserOut, status_code=201)
async def create_user(data: UserCreate):
    return await users_svc.create_user(**data.model_dump())


@router.put("/{user_id}", response_model=UserOut)
async def update_user(user_id: int, data: UserUpdate):
    user = await users_svc.update_user(user_id, **data.model_dump(exclude_none=True))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: int, current_user=Depends(get_current_user)):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    deleted = await users_svc.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": True}
```

- [ ] **Step 2: Register router in main.py**

In `backend/app/main.py`, add the import and router registration. Add this import line after the other app imports:

```python
from app.apps.users.router import router as users_router
```

Add this include_router line after the other includes:

```python
app.include_router(users_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/apps/users/router.py backend/app/main.py
git commit -m "feat: add users CRUD API endpoints (admin-only)"
```

---

### Task 6: Write tests for users API

**Files:**
- Create: `backend/tests/test_users/__init__.py`
- Create: `backend/tests/test_users/test_users.py`

- [ ] **Step 1: Create test module**

Create empty `backend/tests/test_users/__init__.py`:

```python
```

- [ ] **Step 2: Write tests**

Create `backend/tests/test_users/test_users.py`:

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_users_admin(client: AsyncClient, admin_auth_headers):
    resp = await client.get("/api/v1/admin/users", headers=admin_auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["username"] == "admin"


@pytest.mark.asyncio
async def test_list_users_editor_forbidden(client: AsyncClient, auth_headers):
    resp = await client.get("/api/v1/admin/users", headers=auth_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_users_unauthorized(client: AsyncClient):
    resp = await client.get("/api/v1/admin/users")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, admin_auth_headers):
    resp = await client.post(
        "/api/v1/admin/users",
        json={
            "username": "editor1",
            "password": "pass123",
            "role": "editor",
            "display_name": "Editor One",
            "email": "editor1@example.com",
        },
        headers=admin_auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "editor1"
    assert data["role"] == "editor"
    assert data["display_name"] == "Editor One"
    assert data["email"] == "editor1@example.com"
    assert "password" not in data  # password_hash never leaked
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_create_user_duplicate_username(client: AsyncClient, admin_auth_headers):
    await client.post(
        "/api/v1/admin/users",
        json={"username": "dup", "password": "pass123", "role": "editor"},
        headers=admin_auth_headers,
    )
    resp = await client.post(
        "/api/v1/admin/users",
        json={"username": "dup", "password": "pass456", "role": "editor"},
        headers=admin_auth_headers,
    )
    assert resp.status_code == 500  # SQLite unique constraint


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, admin_auth_headers):
    from app.apps.auth.service import create_user

    user = await create_user("editme", "pass123", "editor")

    resp = await client.put(
        f"/api/v1/admin/users/{user.id}",
        json={"display_name": "Updated Name", "phone": "13800000000"},
        headers=admin_auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "Updated Name"
    assert data["phone"] == "13800000000"


@pytest.mark.asyncio
async def test_update_user_password(client: AsyncClient, admin_auth_headers):
    from app.apps.auth.service import create_user, authenticate

    user = await create_user("pwtest", "oldpass", "editor")

    resp = await client.put(
        f"/api/v1/admin/users/{user.id}",
        json={"password": "newpass"},
        headers=admin_auth_headers,
    )
    assert resp.status_code == 200

    token = await authenticate("pwtest", "newpass")
    assert token is not None
    token_old = await authenticate("pwtest", "oldpass")
    assert token_old is None


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, admin_auth_headers):
    from app.apps.auth.service import create_user

    user = await create_user("todelete", "pass123", "editor")

    resp = await client.delete(
        f"/api/v1/admin/users/{user.id}", headers=admin_auth_headers
    )
    assert resp.status_code == 200
    assert resp.json() == {"deleted": True}

    # Verify gone
    resp2 = await client.get("/api/v1/admin/users", headers=admin_auth_headers)
    ids = [u["id"] for u in resp2.json()]
    assert user.id not in ids


@pytest.mark.asyncio
async def test_cannot_delete_self(client: AsyncClient, admin_auth_headers):
    resp = await client.get("/api/v1/admin/auth/me", headers=admin_auth_headers)
    my_id = resp.json()["id"]

    resp = await client.delete(
        f"/api/v1/admin/users/{my_id}", headers=admin_auth_headers
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_delete_nonexistent_user(client: AsyncClient, admin_auth_headers):
    resp = await client.delete(
        "/api/v1/admin/users/99999", headers=admin_auth_headers
    )
    assert resp.status_code == 404
```

- [ ] **Step 3: Run tests**

```bash
cd backend && python -m pytest tests/test_users/ -v
```

Expected: all 9 tests pass.

- [ ] **Step 4: Run full test suite to check for regressions**

```bash
cd backend && python -m pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_users/
git commit -m "test: add user management API tests"
```

---

### Task 7: Create frontend user management page

**Files:**
- Create: `frontend/pages/admin/users.vue`

- [ ] **Step 1: Create the users page**

Create `frontend/pages/admin/users.vue`:

```vue
<template>
  <div class="p-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light text-white tracking-tight mb-1">用户管理</h2>
        <p class="text-[13px]" style="color: rgba(255,255,255,0.25);">管理后台管理员和编辑者账号</p>
      </div>
      <button
        @click="openCreate"
        class="px-4 py-2 rounded-lg text-[13px] font-medium text-white border-none cursor-pointer transition-all duration-200 hover:opacity-90"
        style="background: linear-gradient(135deg, #059669, #10b981);"
      >
        新建用户
      </button>
    </div>

    <!-- Users table -->
    <div
      class="rounded-xl overflow-hidden"
      style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);"
    >
      <table class="w-full text-left">
        <thead>
          <tr style="border-bottom: 1px solid rgba(255,255,255,0.04);">
            <th class="py-3 px-5 text-[11px] font-medium tracking-wider uppercase" style="color: rgba(255,255,255,0.2);">用户</th>
            <th class="py-3 px-5 text-[11px] font-medium tracking-wider uppercase" style="color: rgba(255,255,255,0.2);">角色</th>
            <th class="py-3 px-5 text-[11px] font-medium tracking-wider uppercase" style="color: rgba(255,255,255,0.2);">邮箱</th>
            <th class="py-3 px-5 text-[11px] font-medium tracking-wider uppercase" style="color: rgba(255,255,255,0.2);">手机号</th>
            <th class="py-3 px-5 text-[11px] font-medium tracking-wider uppercase" style="color: rgba(255,255,255,0.2);">创建时间</th>
            <th class="py-3 px-5 text-[11px] font-medium tracking-wider uppercase" style="color: rgba(255,255,255,0.2);">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="user in users"
            :key="user.id"
            class="transition-colors duration-150"
            style="border-bottom: 1px solid rgba(255,255,255,0.02);"
            :style="hoverId === user.id ? { background: 'rgba(255,255,255,0.02)' } : {}"
            @mouseenter="hoverId = user.id"
            @mouseleave="hoverId = null"
          >
            <td class="py-3 px-5">
              <div class="flex items-center gap-3">
                <div
                  class="w-8 h-8 rounded-full flex items-center justify-center text-[12px] font-medium flex-shrink-0"
                  :style="avatarStyle(user)"
                >
                  {{ avatarText(user) }}
                </div>
                <div>
                  <div class="text-[13px] text-white font-medium">{{ user.display_name || user.username }}</div>
                  <div class="text-[11px]" style="color: rgba(255,255,255,0.2);">{{ user.username }}</div>
                </div>
              </div>
            </td>
            <td class="py-3 px-5">
              <span
                class="inline-block px-2 py-0.5 rounded text-[11px] font-medium"
                :style="roleBadgeStyle(user.role)"
              >{{ user.role === 'admin' ? '管理员' : '编辑者' }}</span>
            </td>
            <td class="py-3 px-5 text-[13px]" style="color: rgba(255,255,255,0.35);">{{ user.email || '—' }}</td>
            <td class="py-3 px-5 text-[13px]" style="color: rgba(255,255,255,0.35);">{{ user.phone || '—' }}</td>
            <td class="py-3 px-5 text-[13px]" style="color: rgba(255,255,255,0.2);">{{ formatDate(user.created_at) }}</td>
            <td class="py-3 px-5">
              <div class="flex items-center gap-3">
                <button
                  @click="openEdit(user)"
                  class="text-[12px] border-none bg-transparent cursor-pointer transition-colors"
                  style="color: rgba(255,255,255,0.3);"
                >编辑</button>
                <button
                  v-if="user.id !== myId"
                  @click="confirmDelete(user)"
                  class="text-[12px] border-none bg-transparent cursor-pointer transition-colors"
                  style="color: rgba(239,68,68,0.5);"
                >删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="users.length === 0" class="py-16 text-center text-[13px]" style="color: rgba(255,255,255,0.15);">
        暂无用户
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Teleport to="body">
      <div
        v-if="showModal"
        class="fixed inset-0 z-50 flex items-center justify-center"
        style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
        @click.self="closeModal"
      >
        <div
          class="w-full max-w-[480px] rounded-2xl p-8"
          style="background: #111820; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 20px 60px rgba(0,0,0,0.5);"
        >
          <h3 class="text-lg font-light text-white mb-6">
            {{ editingUser ? '编辑用户' : '新建用户' }}
          </h3>

          <div class="space-y-4">
            <!-- Avatar upload -->
            <div class="flex items-center gap-4 mb-2">
              <div
                class="w-16 h-16 rounded-full flex items-center justify-center text-xl font-medium relative overflow-hidden cursor-pointer"
                :style="formAvatarPreview
                  ? { backgroundImage: `url(${formAvatarPreview})`, backgroundSize: 'cover', backgroundPosition: 'center' }
                  : { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }"
                @click="triggerUpload"
                :title="formAvatarPreview ? '点击更换头像' : '点击上传头像'"
              >
                <span v-if="!formAvatarPreview" style="color: rgba(255,255,255,0.15);">+</span>
                <div
                  v-if="uploadingAvatar"
                  class="absolute inset-0 flex items-center justify-center"
                  style="background: rgba(0,0,0,0.5);"
                >
                  <span class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                </div>
              </div>
              <input
                ref="fileInput"
                type="file"
                accept="image/*"
                class="hidden"
                @change="handleAvatarUpload"
              />
              <div>
                <div class="text-[13px] text-white mb-1">头像</div>
                <div class="text-[11px]" style="color: rgba(255,255,255,0.2);">点击上传，支持 JPG/PNG</div>
              </div>
            </div>

            <div>
              <label class="text-[11px] tracking-wider uppercase block mb-1.5" style="color: rgba(255,255,255,0.25);">用户名 *</label>
              <input
                v-model="form.username"
                type="text"
                class="w-full py-2.5 px-3 rounded-lg text-[14px] text-white outline-none border transition-colors"
                style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.06);"
              />
            </div>

            <div>
              <label class="text-[11px] tracking-wider uppercase block mb-1.5" style="color: rgba(255,255,255,0.25);">显示名称</label>
              <input
                v-model="form.display_name"
                type="text"
                class="w-full py-2.5 px-3 rounded-lg text-[14px] text-white outline-none border transition-colors"
                style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.06);"
              />
            </div>

            <div>
              <label class="text-[11px] tracking-wider uppercase block mb-1.5" style="color: rgba(255,255,255,0.25);">
                密码{{ editingUser ? ' (留空则不修改)' : ' *' }}
              </label>
              <input
                v-model="form.password"
                type="password"
                class="w-full py-2.5 px-3 rounded-lg text-[14px] text-white outline-none border transition-colors"
                style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.06);"
              />
            </div>

            <div>
              <label class="text-[11px] tracking-wider uppercase block mb-1.5" style="color: rgba(255,255,255,0.25);">邮箱</label>
              <input
                v-model="form.email"
                type="email"
                class="w-full py-2.5 px-3 rounded-lg text-[14px] text-white outline-none border transition-colors"
                style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.06);"
              />
            </div>

            <div>
              <label class="text-[11px] tracking-wider uppercase block mb-1.5" style="color: rgba(255,255,255,0.25);">手机号</label>
              <input
                v-model="form.phone"
                type="text"
                class="w-full py-2.5 px-3 rounded-lg text-[14px] text-white outline-none border transition-colors"
                style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.06);"
              />
            </div>

            <div>
              <label class="text-[11px] tracking-wider uppercase block mb-1.5" style="color: rgba(255,255,255,0.25);">角色</label>
              <select
                v-model="form.role"
                class="w-full py-2.5 px-3 rounded-lg text-[14px] text-white outline-none border appearance-none cursor-pointer"
                style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.06);"
              >
                <option value="editor" style="background: #111820;">编辑者 (Editor)</option>
                <option value="admin" style="background: #111820;">管理员 (Admin)</option>
              </select>
            </div>
          </div>

          <!-- Error message -->
          <div
            v-if="formError"
            class="mt-4 px-4 py-3 rounded-lg text-[13px]"
            style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;"
          >
            {{ formError }}
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3 mt-8">
            <button
              @click="closeModal"
              class="px-4 py-2 rounded-lg text-[13px] border-none cursor-pointer transition-colors"
              style="background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.4);"
            >
              取消
            </button>
            <button
              @click="submitForm"
              :disabled="formLoading"
              class="px-6 py-2 rounded-lg text-[13px] font-medium text-white border-none cursor-pointer transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              style="background: linear-gradient(135deg, #059669, #10b981);"
            >
              <span v-if="!formLoading">{{ editingUser ? '保存' : '创建' }}</span>
              <span v-else class="flex items-center gap-2">
                <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                处理中
              </span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Delete confirm modal -->
    <Teleport to="body">
      <div
        v-if="deleteTarget"
        class="fixed inset-0 z-50 flex items-center justify-center"
        style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
        @click.self="deleteTarget = null"
      >
        <div
          class="w-full max-w-[380px] rounded-2xl p-8"
          style="background: #111820; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 20px 60px rgba(0,0,0,0.5);"
        >
          <h3 class="text-lg font-light text-white mb-3">确认删除</h3>
          <p class="text-[14px] mb-1" style="color: rgba(255,255,255,0.4);">
            确定要删除用户 <span class="text-white font-medium">{{ deleteTarget.username }}</span> 吗？
          </p>
          <p class="text-[12px] mb-6" style="color: rgba(239,68,68,0.4);">此操作不可撤销</p>
          <div class="flex justify-end gap-3">
            <button
              @click="deleteTarget = null"
              class="px-4 py-2 rounded-lg text-[13px] border-none cursor-pointer transition-colors"
              style="background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.4);"
            >
              取消
            </button>
            <button
              @click="doDelete"
              :disabled="deleting"
              class="px-6 py-2 rounded-lg text-[13px] font-medium text-white border-none cursor-pointer transition-all disabled:opacity-40"
              style="background: #ef4444;"
            >
              {{ deleting ? '删除中...' : '删除' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['admin-auth'],
});

const config = useRuntimeConfig();
const apiBase = config.public.apiBase as string;

const getHeaders = () => {
  const token = import.meta.client ? localStorage.getItem('admin_token') : null;
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

interface User {
  id: number;
  username: string;
  role: string;
  display_name: string | null;
  phone: string | null;
  email: string | null;
  avatar: string | null;
  created_at: string;
}

const users = ref<User[]>([]);
const myId = ref<number | null>(null);
const hoverId = ref<number | null>(null);

// --- Table helpers ---

const avatarText = (user: User) => {
  return ((user.display_name || user.username) as string).charAt(0).toUpperCase();
};

const avatarStyle = (user: User) => {
  if (user.avatar) {
    return {
      backgroundImage: `url(${user.avatar})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
    };
  }
  return {
    background: user.role === 'admin'
      ? 'linear-gradient(135deg, #059669, #0284c7)'
      : 'linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.12))',
  };
};

const roleBadgeStyle = (role: string) => {
  if (role === 'admin') {
    return {
      background: 'rgba(5,150,105,0.12)',
      color: '#34d399',
      border: '1px solid rgba(5,150,105,0.2)',
    };
  }
  return {
    background: 'rgba(255,255,255,0.04)',
    color: 'rgba(255,255,255,0.5)',
    border: '1px solid rgba(255,255,255,0.06)',
  };
};

const formatDate = (s: string) => {
  if (!s) return '—';
  return new Date(s).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
};

// --- Data fetching ---

const fetchUsers = async () => {
  try {
    const data = await $fetch<User[]>(`${apiBase}/admin/users`, { headers: getHeaders() });
    users.value = data;
  } catch (e: any) {
    if (e?.response?.status === 403) {
      // editor role, just show empty
      users.value = [];
    }
  }
};

const fetchMe = async () => {
  try {
    const data = await $fetch<User>(`${apiBase}/admin/auth/me`, { headers: getHeaders() });
    myId.value = data.id;
  } catch {}
};

onMounted(() => {
  fetchMe();
  fetchUsers();
});

// --- Modal logic ---

const showModal = ref(false);
const editingUser = ref<User | null>(null);
const form = ref({ username: '', password: '', role: 'editor', display_name: '', phone: '', email: '', avatar: '' });
const formError = ref('');
const formLoading = ref(false);
const formAvatarPreview = ref('');
const uploadingAvatar = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);

const resetForm = () => {
  form.value = { username: '', password: '', role: 'editor', display_name: '', phone: '', email: '', avatar: '' };
  formError.value = '';
  formAvatarPreview.value = '';
};

const triggerUpload = () => {
  fileInput.value?.click();
};

const handleAvatarUpload = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  uploadingAvatar.value = true;
  try {
    const body = new FormData();
    body.append('file', file);
    const result = await $fetch<{ url: string }>(`${apiBase}/admin/media/upload`, {
      method: 'POST',
      headers: { ...(getHeaders()) },
      body,
    });
    formAvatarPreview.value = result.url;
    form.value.avatar = result.url;
  } catch {
    formError.value = '头像上传失败';
  } finally {
    uploadingAvatar.value = false;
    target.value = '';
  }
};

const openCreate = () => {
  editingUser.value = null;
  resetForm();
  showModal.value = true;
};

const openEdit = (user: User) => {
  editingUser.value = user;
  form.value = {
    username: user.username,
    password: '',
    role: user.role,
    display_name: user.display_name || '',
    phone: user.phone || '',
    email: user.email || '',
    avatar: user.avatar || '',
  };
  formAvatarPreview.value = user.avatar || '';
  formError.value = '';
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  editingUser.value = null;
};

const submitForm = async () => {
  if (!form.value.username.trim()) {
    formError.value = '用户名不能为空';
    return;
  }
  if (!editingUser.value && !form.value.password) {
    formError.value = '密码不能为空';
    return;
  }

  formLoading.value = true;
  formError.value = '';

  try {
    const body: Record<string, any> = {
      username: form.value.username.trim(),
      role: form.value.role,
    };
    if (form.value.password) body.password = form.value.password;
    if (form.value.display_name) body.display_name = form.value.display_name.trim();
    if (form.value.phone) body.phone = form.value.phone.trim();
    if (form.value.email) body.email = form.value.email.trim();
    if (form.value.avatar) body.avatar = form.value.avatar;

    if (editingUser.value) {
      await $fetch(`${apiBase}/admin/users/${editingUser.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', ...getHeaders() },
        body: JSON.stringify(body),
      });
    } else {
      await $fetch(`${apiBase}/admin/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getHeaders() },
        body: JSON.stringify(body),
      });
    }
    closeModal();
    await fetchUsers();
  } catch (e: any) {
    formError.value = e?.data?.detail || '操作失败';
  } finally {
    formLoading.value = false;
  }
};

// --- Delete logic ---

const deleteTarget = ref<User | null>(null);
const deleting = ref(false);

const confirmDelete = (user: User) => {
  deleteTarget.value = user;
};

const doDelete = async () => {
  if (!deleteTarget.value) return;
  deleting.value = true;
  try {
    await $fetch(`${apiBase}/admin/users/${deleteTarget.value.id}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    deleteTarget.value = null;
    await fetchUsers();
  } catch {}
  deleting.value = false;
};
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/pages/admin/users.vue
git commit -m "feat: add user management admin page"
```

---

### Task 8: Add users shortcut to admin dashboard

**Files:**
- Modify: `frontend/pages/admin/index.vue`

- [ ] **Step 1: Add users link to dashboard**

In `frontend/pages/admin/index.vue`, add the users entry to the `links` array (inside `<script setup>`, after the settings entry):

```typescript
const links = [
  { to: '/admin/pages', label: '页面管理', desc: '编辑网站页面和内容区块' },
  { to: '/admin/news', label: '新闻管理', desc: '发布和管理新闻文章' },
  { to: '/admin/media', label: '媒体管理', desc: '上传和管理图片、视频等媒体资源' },
  { to: '/admin/menus', label: '菜单管理', desc: '配置导航菜单结构' },
  { to: '/admin/users', label: '用户管理', desc: '管理后台管理员和编辑者账号' },
  { to: '/admin/inquiries', label: '咨询管理', desc: '查看用户提交的咨询' },
  { to: '/admin/settings', label: '系统设置', desc: '配置 LLM、站点信息等系统参数' },
];
```

(The only change is adding the `users` line between `menus` and `inquiries`.)

- [ ] **Step 2: Commit**

```bash
git add frontend/pages/admin/index.vue
git commit -m "feat: add user management link to admin dashboard"
```

---

### Task 9: End-to-end verification

- [ ] **Step 1: Run backend tests**

```bash
cd backend && python -m pytest tests/ -v
```

Expected: all tests pass (existing + new users tests).

- [ ] **Step 2: Verify database schema update**

If running locally, restart the backend and run seed.py to recreate tables with new columns:

```bash
cd backend && python seed.py
```

- [ ] **Step 3: Manual UI check**

Start the frontend dev server, log in as admin, navigate to `/admin/users`, and verify:
- User list loads
- Create new user works
- Edit user (including password change) works
- Delete user works (and self-delete is blocked)
- Editor role users see 403 when accessing user management API
