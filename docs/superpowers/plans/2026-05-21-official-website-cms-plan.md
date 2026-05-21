# 智慧建筑运维官网 + CMS + 聊天智能体 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a full-stack official website with CMS admin panel and RAG-powered chatbot for a smart building operations company.

**Architecture:** FastAPI monolith backend with clean module separation (core/cms/news/chat/theme/faq/settings), Nuxt 3 SSG/ISR public frontend, Vue3+Vite admin SPA, PostgreSQL+Qdrant+MinIO+Redis data layer, all orchestrated via Docker Compose.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, Nuxt 3, Vue 3 + TypeScript, PostgreSQL 17, Qdrant, MinIO, Redis 7, Docker

---

## File Structure

```
gweb/
├── docker-compose.yml
├── nginx/
│   └── nginx.conf
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── storage.py          # MinIO adapter
│   │   ├── shared/
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # BaseModel, TimestampMixin
│   │   │   └── pagination.py
│   │   └── apps/
│   │       ├── auth/
│   │       │   ├── __init__.py
│   │       │   ├── models.py
│   │       │   ├── schemas.py
│   │       │   ├── service.py
│   │       │   └── router.py
│   │       ├── cms/
│   │       │   ├── __init__.py
│   │       │   ├── models.py        # Page, Block, Menu, Media
│   │       │   ├── schemas.py
│   │       │   ├── service_page.py
│   │       │   ├── service_block.py
│   │       │   ├── service_menu.py
│   │       │   ├── service_media.py
│   │       │   ├── block_validators.py  # JSON Schema per block type
│   │       │   └── router.py
│   │       ├── news/
│   │       │   ├── __init__.py
│   │       │   ├── models.py
│   │       │   ├── schemas.py
│   │       │   ├── service.py
│   │       │   └── router.py
│   │       ├── inquiry/
│   │       │   ├── __init__.py
│   │       │   ├── models.py
│   │       │   ├── schemas.py
│   │       │   ├── service.py
│   │       │   └── router.py
│   │       ├── theme/
│   │       │   ├── __init__.py
│   │       │   ├── models.py
│   │       │   ├── schemas.py
│   │       │   ├── service.py
│   │       │   └── router.py
│   │       ├── faq/
│   │       │   ├── __init__.py
│   │       │   ├── models.py
│   │       │   ├── schemas.py
│   │       │   ├── service.py
│   │       │   └── router.py
│   │       ├── settings/
│   │       │   ├── __init__.py
│   │       │   ├── service.py
│   │       │   └── router.py
│   │       └── chat/
│   │           ├── __init__.py
│   │           ├── models.py
│   │           ├── schemas.py
│   │           ├── router_public.py
│   │           ├── router_admin.py
│   │           ├── engine.py
│   │           ├── retriever.py
│   │           ├── chunker.py
│   │           ├── indexer.py
│   │           └── llm/
│   │               ├── __init__.py
│   │               ├── base.py
│   │               ├── deepseek.py
│   │               ├── openai.py
│   │               └── anthropic.py
│   └── tests/
│       ├── conftest.py
│       ├── test_auth/
│       ├── test_cms/
│       ├── test_news/
│       ├── test_inquiry/
│       ├── test_theme/
│       ├── test_faq/
│       ├── test_settings/
│       └── test_chat/
├── frontend/                   # Nuxt 3 public site
│   ├── nuxt.config.ts
│   ├── package.json
│   ├── pages/
│   │   ├── index.vue
│   │   ├── about.vue
│   │   ├── products.vue
│   │   ├── solutions.vue
│   │   ├── contact.vue
│   │   ├── news/
│   │   │   ├── index.vue
│   │   │   └── [id].vue
│   │   └── chat.vue
│   ├── components/
│   │   ├── blocks/              # 1 per block type
│   │   ├── layout/
│   │   └── tech/                # ParticleNetwork, GlowCursor, etc.
│   ├── composables/
│   │   ├── usePage.ts
│   │   ├── useTheme.ts
│   │   └── useI18n.ts
│   └── assets/
│       └── styles/themes/
└── admin/                      # Vue3 + Vite admin
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── pages/
        │   ├── login/
        │   ├── dashboard/
        │   ├── pages/
        │   ├── media/
        │   ├── news/
        │   ├── themes/
        │   ├── settings/
        │   └── chat/
        ├── components/
        │   └── block-editor/
        ├── composables/
        └── stores/
```

---

## Phase 1: Project Infrastructure

### Task 1.1: Backend project scaffolding

**Files:**
- Modify: `backend/pyproject.toml` (create from existing root)
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`

- [ ] **Step 1: Set up backend pyproject.toml with dependencies**

Move existing `pyproject.toml` content into `backend/`:

```toml
[project]
name = "gweb-backend"
version = "0.1.0"
description = "Smart Building Ops Website Backend"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy[asyncio]>=2.0.36",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.12",
    "httpx>=0.28.0",
    "minio>=7.2.0",
    "qdrant-client>=1.12.0",
    "redis[hiredis]>=5.2.0",
    "openai>=1.58.0",
    "anthropic>=0.42.0",
    "Pillow>=11.0.0",
    "sse-starlette>=2.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.0",
    "factory-boy>=3.3.0",
    "alembic>=1.14.0",
]
```

- [ ] **Step 2: Create config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "GWEB_", "env_file": ".env"}

    # App
    debug: bool = False
    secret_key: str = "change-me-in-production"

    # Database
    database_url: str = "postgresql+asyncpg://gweb:gweb@localhost:5432/gweb"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "gweb-media"
    minio_secure: bool = False

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "gweb_knowledge"

    # LLM defaults
    llm_provider: str = "deepseek"
    llm_api_key: str = ""
    llm_model: str = "deepseek-chat"
    embedding_provider: str = "openai"
    embedding_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"


settings = Settings()
```

- [ ] **Step 3: Create minimal main.py**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="GWeb API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Create shared base model**

Create `backend/app/shared/models.py`:

```python
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

- [ ] **Step 5: Create shared pagination**

Create `backend/app/shared/pagination.py`:

```python
from pydantic import BaseModel


class PaginationParams:
    def __init__(self, page: int = 1, size: int = 20):
        self.page = max(1, page)
        self.size = min(100, max(1, size))
        self.offset = (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int
```

- [ ] **Step 6: Install dependencies**

```bash
cd backend && uv sync
```

- [ ] **Step 7: Verify app starts**

```bash
cd backend && uv run uvicorn app.main:app --port 8000 &
sleep 2 && curl http://localhost:8000/health
# Expected: {"status":"ok"}
kill %1
```

- [ ] **Step 8: Commit**

```bash
git add backend/
git commit -m "feat: backend project scaffolding with FastAPI and shared models"
```

### Task 1.2: Docker Compose infrastructure

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/Dockerfile`

- [ ] **Step 1: Create docker-compose.yml**

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_USER: gweb
      POSTGRES_PASSWORD: gweb
      POSTGRES_DB: gweb
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333", "6334:6334"]
    volumes:
      - qdrant_data:/qdrant/storage

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports: ["9000:9000", "9001:9001"]
    volumes:
      - minio_data:/data

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports: ["8000:8000"]
    environment:
      GWEB_DATABASE_URL: postgresql+asyncpg://gweb:gweb@postgres:5432/gweb
      GWEB_REDIS_URL: redis://redis:6379/0
      GWEB_MINIO_ENDPOINT: minio:9000
      GWEB_QDRANT_URL: http://qdrant:6333
      GWEB_DEBUG: "true"
    volumes:
      - ./backend:/app
    depends_on: [postgres, redis, qdrant, minio]

volumes:
  pgdata:
  qdrant_data:
  minio_data:
```

- [ ] **Step 2: Create backend/Dockerfile**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Start services and verify**

```bash
docker compose up -d postgres redis qdrant minio
docker compose ps
# Expected: all 4 services "healthy" or "running"
```

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml backend/Dockerfile
git commit -m "feat: add Docker Compose infrastructure with PG17/Qdrant/MinIO/Redis"
```

---

## Phase 2: Database Setup & Core Backend

### Task 2.1: Database connection and Alembic setup

**Files:**
- Create: `backend/app/core/database.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/script.py.mako`

- [ ] **Step 1: Create database.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
```

- [ ] **Step 2: Initialize Alembic**

```bash
cd backend && uv run alembic init alembic
```

- [ ] **Step 3: Configure alembic/env.py**

```python
from app.config import settings
from app.shared.models import Base

# Import all models so Base.metadata knows about them
from app.apps.auth.models import User
from app.apps.cms.models import Page, Block, Menu, Media
from app.apps.news.models import NewsArticle
from app.apps.inquiry.models import Inquiry
from app.apps.theme.models import Theme
from app.apps.faq.models import FAQ
from app.apps.chat.models import ChatSession, ChatMessage

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.database_url.replace("+asyncpg", ""))
```

Configure `alembic.ini` to point at the env.py and remove the hardcoded sqlalchemy.url.

- [ ] **Step 4: Create all models in one migration**

Write all model files (see Phase 3-4 model definitions), then:

```bash
cd backend && uv run alembic revision --autogenerate -m "init_all_tables"
uv run alembic upgrade head
```

Verify: `docker compose exec postgres psql -U gweb -d gweb -c "\dt"`
Expected: list of all tables.

- [ ] **Step 5: Commit**

```bash
git add backend/alembic/ backend/app/core/database.py backend/app/apps/*/models.py
git commit -m "feat: add database layer with all models and Alembic migration"
```

### Task 2.2: Auth module (JWT + User)

**Files:**
- Create: `backend/app/core/security.py`
- Create: `backend/app/apps/auth/__init__.py`
- Create: `backend/app/apps/auth/models.py`
- Create: `backend/app/apps/auth/schemas.py`
- Create: `backend/app/apps/auth/service.py`
- Create: `backend/app/apps/auth/router.py`
- Create: `backend/tests/test_auth/__init__.py`
- Create: `backend/tests/test_auth/test_auth.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Write failing tests for auth**

Create `backend/tests/conftest.py`:

```python
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.database import engine, Base


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
```

Create `backend/tests/test_auth/test_auth.py`:

```python
import pytest


@pytest.mark.asyncio
async def test_login_success(client):
    # Seed a user first
    from app.apps.auth.service import create_user
    await create_user("admin", "password123")

    resp = await client.post("/api/v1/admin/auth/login", json={
        "username": "admin", "password": "password123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    from app.apps.auth.service import create_user
    await create_user("admin", "password123")

    resp = await client.post("/api/v1/admin/auth/login", json={
        "username": "admin", "password": "wrong"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_token(client):
    resp = await client.get("/api/v1/admin/pages")
    assert resp.status_code == 401
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && uv run pytest tests/test_auth/ -v
# Expected: all 3 fail (auth endpoints not implemented)
```

- [ ] **Step 3: Create security.py**

```python
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=24))
    return jwt.encode({"sub": str(user_id), "exp": expire}, settings.secret_key, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
```

- [ ] **Step 4: Create auth/models.py**

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
```

- [ ] **Step 5: Create auth/schemas.py**

```python
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

    model_config = {"from_attributes": True}
```

- [ ] **Step 6: Create auth/service.py**

```python
from sqlalchemy import select
from app.core.database import async_session
from app.core.security import hash_password, verify_password, create_access_token
from app.apps.auth.models import User


async def create_user(username: str, password: str) -> User:
    async with async_session() as db:
        user = User(username=username, password_hash=hash_password(password))
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

- [ ] **Step 7: Create auth/router.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.apps.auth.schemas import LoginRequest, TokenResponse
from app.apps.auth.service import authenticate, get_user_by_id
from app.core.security import decode_token

router = APIRouter(prefix="/api/v1/admin/auth", tags=["auth"])
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = decode_token(credentials.credentials)
        user_id = int(payload["sub"])
        user = await get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    token = await authenticate(data.username, data.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=token)
```

- [ ] **Step 8: Register auth router in main.py**

Add to `backend/app/main.py`:

```python
from app.apps.auth.router import router as auth_router
app.include_router(auth_router)
```

- [ ] **Step 9: Run tests to verify they pass**

```bash
cd backend && uv run pytest tests/test_auth/ -v
# Expected: all 3 pass
```

- [ ] **Step 10: Commit**

```bash
git add backend/app/core/security.py backend/app/apps/auth/ backend/tests/
git commit -m "feat: add JWT auth module with login endpoint"
```

### Task 2.3: Settings module

**Files:**
- Create: `backend/app/apps/settings/__init__.py`
- Create: `backend/app/apps/settings/service.py`
- Create: `backend/app/apps/settings/router.py`

- [ ] **Step 1: Create settings service (KV store in PG)**

```python
from sqlalchemy import text
from app.core.database import async_session

ENCRYPTED_KEYS = {"llm_api_key", "embedding_api_key", "secret_key"}

async def get_setting(key: str) -> str | None:
    async with async_session() as db:
        result = await db.execute(
            text("SELECT value FROM settings WHERE key = :key"), {"key": key}
        )
        row = result.fetchone()
        return row[0] if row else None


async def set_setting(key: str, value: str):
    async with async_session() as db:
        await db.execute(
            text("""
                INSERT INTO settings (key, value, is_encrypted, updated_at)
                VALUES (:key, :value, :enc, NOW())
                ON CONFLICT (key) DO UPDATE SET value = :value, updated_at = NOW()
            """),
            {"key": key, "value": value, "enc": key in ENCRYPTED_KEYS},
        )
        await db.commit()


async def get_public_settings() -> dict:
    async with async_session() as db:
        result = await db.execute(
            text("SELECT key, value FROM settings WHERE is_encrypted = false")
        )
        return {row[0]: row[1] for row in result.fetchall()}
```

- [ ] **Step 2: Create settings router**

```python
from fastapi import APIRouter, Depends
from app.apps.settings.service import get_setting, set_setting, get_public_settings
from app.apps.auth.router import get_current_user
from pydantic import BaseModel

router_public = APIRouter(prefix="/api/v1/settings", tags=["settings"])
router_admin = APIRouter(prefix="/api/v1/admin/settings", tags=["admin-settings"], dependencies=[Depends(get_current_user)])


class SetSettingRequest(BaseModel):
    value: str


@router_public.get("/public")
async def public_settings():
    return await get_public_settings()


@router_admin.get("")
async def list_settings():
    # Return all non-encrypted settings
    from app.core.database import async_session
    from sqlalchemy import text
    async with async_session() as db:
        result = await db.execute(text("SELECT key, value, is_encrypted FROM settings"))
        return [{"key": r[0], "value": "***" if r[2] else r[1]} for r in result.fetchall()]


@router_admin.put("/{key}")
async def update_setting(key: str, body: SetSettingRequest):
    await set_setting(key, body.value)
    return {"key": key, "updated": True}
```

- [ ] **Step 3: Register routers in main.py**

```python
from app.apps.settings.router import router_public as settings_public_router
from app.apps.settings.router import router_admin as settings_admin_router
app.include_router(settings_public_router)
app.include_router(settings_admin_router)
```

- [ ] **Step 4: Verify with curl**

```bash
# Set a setting
curl -X PUT http://localhost:8000/api/v1/admin/settings/site_name \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value": "测试网站"}'

# Get public settings
curl http://localhost:8000/api/v1/settings/public
# Expected: {"site_name": "测试网站"}
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/apps/settings/
git commit -m "feat: add settings module (KV store with encrypted key support)"
```

---

## Phase 3: CMS Backend

### Task 3.1: Media module (MinIO upload)

**Files:**
- Create: `backend/app/core/storage.py`
- Create: `backend/app/apps/cms/models.py` (Media model)
- Create: `backend/app/apps/cms/service_media.py`
- Create: `backend/tests/test_cms/test_media.py`

- [ ] **Step 1: Write failing test for media upload**

```python
import pytest
from io import BytesIO


@pytest.mark.asyncio
async def test_upload_image(client, auth_headers):
    resp = await client.post(
        "/api/v1/admin/media/upload",
        files={"file": ("test.png", BytesIO(b"fake-png-data"), "image/png")},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["filename"] == "test.png"
    assert data["mime_type"] == "image/png"
    assert "id" in data
    assert "url" in data
    assert "thumbnail_url" in data


@pytest.mark.asyncio
async def test_upload_requires_auth(client):
    resp = await client.post(
        "/api/v1/admin/media/upload",
        files={"file": ("test.png", BytesIO(b"fake"), "image/png")},
    )
    assert resp.status_code == 401
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && uv run pytest tests/test_cms/test_media.py -v
# Expected: FAIL
```

- [ ] **Step 3: Create storage.py (MinIO adapter)**

```python
from minio import Minio
from minio.error import S3Error
from app.config import settings
import uuid


class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(settings.minio_bucket):
            self.client.make_bucket(settings.minio_bucket)

    def upload(self, data: bytes, filename: str, content_type: str) -> str:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
        object_name = f"{uuid.uuid4().hex}.{ext}"
        self.client.put_object(
            settings.minio_bucket, object_name, data, len(data),
            content_type=content_type,
        )
        return object_name

    def get_url(self, object_name: str) -> str:
        return self.client.presigned_get_object(settings.minio_bucket, object_name)

    def delete(self, object_name: str):
        try:
            self.client.remove_object(settings.minio_bucket, object_name)
        except S3Error:
            pass


storage = StorageService()
```

- [ ] **Step 4: Create Media model in cms/models.py**

```python
from sqlalchemy import String, Integer, BigInteger, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.models import Base, TimestampMixin
import enum


class MediaType(str, enum.Enum):
    image = "image"
    video = "video"
    document = "document"


class Media(Base, TimestampMixin):
    __tablename__ = "media"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type: Mapped[MediaType] = mapped_column(SAEnum(MediaType), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    alt_text_zh: Mapped[str | None] = mapped_column(String(500), nullable=True)
    alt_text_en: Mapped[str | None] = mapped_column(String(500), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

- [ ] **Step 5: Create cms/service_media.py**

```python
import io
from PIL import Image
from app.core.storage import storage
from app.core.database import async_session
from app.apps.cms.models import Media, MediaType


async def upload_media(file_data: bytes, filename: str, content_type: str) -> Media:
    mt = content_type.split("/")[0]
    media_type = MediaType(mt) if mt in ("image", "video") else MediaType.document

    object_path = storage.upload(file_data, filename, content_type)
    thumbnail_path = None
    width, height = None, None

    if media_type == MediaType.image:
        img = Image.open(io.BytesIO(file_data))
        width, height = img.size
        thumb = img.copy()
        thumb.thumbnail((400, 300))
        thumb_buf = io.BytesIO()
        thumb.save(thumb_buf, format="WEBP", quality=80)
        thumbnail_path = storage.upload(thumb_buf.getvalue(), f"thumb_{filename}", "image/webp")

    async with async_session() as db:
        media = Media(
            filename=filename,
            original_name=filename,
            mime_type=content_type,
            size=len(file_data),
            type=media_type,
            path=object_path,
            thumbnail_path=thumbnail_path,
            width=width,
            height=height,
        )
        db.add(media)
        await db.commit()
        await db.refresh(media)
        return media
```

- [ ] **Step 6: Create media endpoints in cms/router.py**

Add this class to the router file (create router.py skeleton first):

```python
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.apps.auth.router import get_current_user
from app.apps.cms.service_media import upload_media, list_media, delete_media
from app.core.storage import storage

admin_router = APIRouter(prefix="/api/v1/admin/media", tags=["admin-media"], dependencies=[Depends(get_current_user)])


@admin_router.post("/upload", status_code=201)
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    media = await upload_media(data, file.filename, file.content_type or "application/octet-stream")
    return {
        "id": media.id,
        "filename": media.original_name,
        "mime_type": media.mime_type,
        "url": storage.get_url(media.path),
        "thumbnail_url": storage.get_url(media.thumbnail_path) if media.thumbnail_path else None,
        "width": media.width,
        "height": media.height,
    }


@admin_router.get("")
async def list_media_endpoint(page: int = 1, size: int = 20):
    return await list_media(page, size)


@admin_router.delete("/{media_id}")
async def delete_media_endpoint(media_id: int):
    await delete_media(media_id)
    return {"deleted": True}
```

- [ ] **Step 7: Run tests to verify they pass**

```bash
cd backend && uv run pytest tests/test_cms/test_media.py -v
# Expected: PASS
```

- [ ] **Step 8: Commit**

```bash
git add backend/app/core/storage.py backend/app/apps/cms/
git commit -m "feat: add media upload with MinIO storage and auto-thumbnail generation"
```

### Task 3.2: Page & Block CRUD

**Files:**
- Modify: `backend/app/apps/cms/models.py` (add Page, Block)
- Create: `backend/app/apps/cms/schemas.py`
- Create: `backend/app/apps/cms/service_page.py`
- Create: `backend/app/apps/cms/service_block.py`
- Create: `backend/app/apps/cms/block_validators.py`
- Modify: `backend/app/apps/cms/router.py` (add page/block routes)
- Create: `backend/tests/test_cms/test_pages.py`
- Create: `backend/tests/test_cms/test_blocks.py`

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_cms/test_pages.py`:

```python
import pytest


@pytest.mark.asyncio
async def test_create_page(client, auth_headers):
    resp = await client.post("/api/v1/admin/pages", json={
        "name_zh": "首页", "name_en": "Home", "slug": "home"
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "home"
    assert data["name_zh"] == "首页"


@pytest.mark.asyncio
async def test_get_page_by_slug_public(client):
    # Seed a page first
    from app.apps.cms.service_page import create_page
    await create_page(name_zh="首页", name_en="Home", slug="home")

    resp = await client.get("/api/v1/pages/home")
    assert resp.status_code == 200
    assert resp.json()["slug"] == "home"


@pytest.mark.asyncio
async def test_create_page_duplicate_slug(client, auth_headers):
    from app.apps.cms.service_page import create_page
    await create_page(name_zh="首页", name_en="Home", slug="home")

    resp = await client.post("/api/v1/admin/pages", json={
        "name_zh": "重复", "name_en": "Dup", "slug": "home"
    }, headers=auth_headers)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_nonexistent_page(client):
    resp = await client.get("/api/v1/pages/nonexistent")
    assert resp.status_code == 404
```

Create `backend/tests/test_cms/test_blocks.py`:

```python
import pytest


@pytest.mark.asyncio
async def test_add_block_to_page(client, auth_headers):
    from app.apps.cms.service_page import create_page
    page = await create_page(name_zh="首页", name_en="Home", slug="home")

    resp = await client.post(f"/api/v1/admin/pages/{page.id}/blocks", json={
        "type": "hero",
        "config": {"background": "dark", "padding": "lg"},
        "content": {
            "title_zh": "智驭建筑", "title_en": "Smart Building",
            "subtitle_zh": "副标题", "subtitle_en": "Subtitle",
            "buttons": []
        }
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["type"] == "hero"
    assert data["order"] == 0


@pytest.mark.asyncio
async def test_reorder_blocks(client, auth_headers):
    from app.apps.cms.service_page import create_page
    from app.apps.cms.service_block import create_block
    page = await create_page(name_zh="首页", name_en="Home", slug="home")
    b1 = await create_block(page.id, "hero", {"background": "dark"}, {"title_zh": "A"})
    b2 = await create_block(page.id, "richtext", {}, {"html_content_zh": "B"})

    resp = await client.put("/api/v1/admin/blocks/reorder", json={
        "page_id": page.id, "block_ids": [b2.id, b1.id]
    }, headers=auth_headers)
    assert resp.status_code == 200
    # Verify order changed
    page_resp = await client.get("/api/v1/pages/home")
    blocks = page_resp.json()["blocks"]
    assert blocks[0]["id"] == b2.id
    assert blocks[1]["id"] == b1.id


@pytest.mark.asyncio
async def test_block_content_validation(client, auth_headers):
    from app.apps.cms.service_page import create_page
    page = await create_page(name_zh="首页", name_en="Home", slug="home")

    # hero block without required title_zh should fail
    resp = await client.post(f"/api/v1/admin/pages/{page.id}/blocks", json={
        "type": "hero",
        "config": {},
        "content": {"title_en": "Missing zh title"}
    }, headers=auth_headers)
    assert resp.status_code == 422
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && uv run pytest tests/test_cms/test_pages.py tests/test_cms/test_blocks.py -v
# Expected: FAIL
```

- [ ] **Step 3: Add Page and Block models to cms/models.py**

```python
from sqlalchemy import String, Integer, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Page(Base, TimestampMixin):
    __tablename__ = "pages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_zh: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    blocks: Mapped[list["Block"]] = relationship(
        "Block", back_populates="page", order_by="Block.order",
        cascade="all, delete-orphan"
    )


class Block(Base, TimestampMixin):
    __tablename__ = "blocks"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    page: Mapped["Page"] = relationship("Page", back_populates="blocks")
```

- [ ] **Step 4: Create block_validators.py**

```python
from pydantic import BaseModel, Field


class HeroContent(BaseModel):
    title_zh: str
    title_en: str
    subtitle_zh: str = ""
    subtitle_en: str = ""
    bg_image: int | None = None
    bg_video: int | None = None
    buttons: list[dict] = []


class NewsListContent(BaseModel):
    title_zh: str
    title_en: str
    count: int = 3
    show_date: bool = True
    show_image: bool = True
    category_filter: list[str] = []


class ProductCardsContent(BaseModel):
    title_zh: str
    title_en: str
    cards: list[dict] = []


class StatsCounterContent(BaseModel):
    title_zh: str
    title_en: str
    items: list[dict] = []


class ContactFormContent(BaseModel):
    title_zh: str
    title_en: str
    fields: list[str] = ["company_name", "contact_name", "phone", "message"]
    features: list[dict] = []
    submit_button_zh: str = "提交"
    submit_button_en: str = "Submit"


class RichtextContent(BaseModel):
    html_content_zh: str = ""
    html_content_en: str = ""


class SolutionCardsContent(BaseModel):
    title_zh: str
    title_en: str
    description_zh: str = ""
    description_en: str = ""
    cards: list[dict] = []


BLOCK_VALIDATORS = {
    "hero": HeroContent,
    "news_list": NewsListContent,
    "product_cards": ProductCardsContent,
    "solution_cards": SolutionCardsContent,
    "stats_counter": StatsCounterContent,
    "contact_form": ContactFormContent,
    "richtext": RichtextContent,
    "video_banner": RichtextContent,
    "image_gallery": RichtextContent,
    "logo_cloud": RichtextContent,
    "faq": RichtextContent,
    "cta_banner": RichtextContent,
    "digital_twin": RichtextContent,
    "live_dashboard": RichtextContent,
    "tech_icon_grid": RichtextContent,
}


def validate_block_content(block_type: str, content: dict):
    validator = BLOCK_VALIDATORS.get(block_type)
    if validator:
        validator(**content)
    return content
```

- [ ] **Step 5: Create service_page.py**

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import async_session
from app.apps.cms.models import Page


async def create_page(name_zh: str, name_en: str, slug: str) -> Page:
    async with async_session() as db:
        page = Page(name_zh=name_zh, name_en=name_en, slug=slug)
        db.add(page)
        await db.commit()
        await db.refresh(page)
        return page


async def get_page_by_slug(slug: str) -> Page | None:
    async with async_session() as db:
        result = await db.execute(
            select(Page).where(Page.slug == slug, Page.is_published == True)
            .options(selectinload(Page.blocks))
        )
        return result.scalar_one_or_none()


async def list_pages() -> list[Page]:
    async with async_session() as db:
        result = await db.execute(select(Page).order_by(Page.id))
        return result.scalars().all()


async def update_page(page_id: int, **kwargs) -> Page | None:
    async with async_session() as db:
        page = await db.get(Page, page_id)
        if page:
            for k, v in kwargs.items():
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

- [ ] **Step 6: Create service_block.py**

```python
from sqlalchemy import select, update
from app.core.database import async_session
from app.apps.cms.models import Block
from app.apps.cms.block_validators import validate_block_content


async def create_block(page_id: int, block_type: str, config: dict, content: dict) -> Block:
    validate_block_content(block_type, content)
    async with async_session() as db:
        # Determine order
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
            if "content" in kwargs:
                validate_block_content(block.type, kwargs["content"])
            for k, v in kwargs.items():
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
```

- [ ] **Step 7: Add page/block routes to cms/router.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from app.apps.auth.router import get_current_user
from app.apps.cms.service_page import create_page, get_page_by_slug, list_pages, update_page, delete_page
from app.apps.cms.service_block import create_block, update_block, delete_block, reorder_blocks
from app.apps.cms.schemas import PageCreate, PageOut, BlockCreate, BlockOut, ReorderRequest
from app.core.storage import storage

public_router = APIRouter(prefix="/api/v1", tags=["public"])
admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin-cms"], dependencies=[Depends(get_current_user)])


@public_router.get("/pages/{slug}", response_model=PageOut)
async def get_page(slug: str):
    page = await get_page_by_slug(slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@admin_router.get("/pages")
async def admin_list_pages():
    pages = await list_pages()
    return [{"id": p.id, "name_zh": p.name_zh, "name_en": p.name_en, "slug": p.slug, "is_published": p.is_published} for p in pages]


@admin_router.post("/pages", status_code=201)
async def admin_create_page(data: PageCreate):
    try:
        page = await create_page(**data.model_dump())
        return {"id": page.id, "slug": page.slug}
    except Exception:
        raise HTTPException(status_code=409, detail="Slug already exists")


@admin_router.put("/pages/{page_id}")
async def admin_update_page(page_id: int, data: PageCreate):
    page = await update_page(page_id, **data.model_dump())
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"id": page.id, "slug": page.slug}


@admin_router.delete("/pages/{page_id}")
async def admin_delete_page(page_id: int):
    deleted = await delete_page(page_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"deleted": True}


@admin_router.post("/pages/{page_id}/blocks", status_code=201)
async def admin_create_block(page_id: int, data: BlockCreate):
    try:
        block = await create_block(page_id, data.type, data.config, data.content)
        return {"id": block.id, "type": block.type, "order": block.order}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@admin_router.put("/blocks/{block_id}")
async def admin_update_block(block_id: int, data: BlockCreate):
    block = await update_block(block_id, **data.model_dump())
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"id": block.id, "type": block.type}


@admin_router.delete("/blocks/{block_id}")
async def admin_delete_block(block_id: int):
    deleted = await delete_block(block_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"deleted": True}


@admin_router.put("/blocks/reorder")
async def admin_reorder_blocks(data: ReorderRequest):
    await reorder_blocks(data.page_id, data.block_ids)
    return {"ok": True}
```

- [ ] **Step 8: Create schemas.py**

```python
from pydantic import BaseModel


class PageCreate(BaseModel):
    name_zh: str
    name_en: str
    slug: str


class BlockCreate(BaseModel):
    type: str
    config: dict = {}
    content: dict = {}


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
    blocks: list[BlockOut]

    model_config = {"from_attributes": True}
```

- [ ] **Step 9: Run tests to verify they pass**

```bash
cd backend && uv run pytest tests/test_cms/ -v
# Expected: all PASS
```

- [ ] **Step 10: Commit**

```bash
git add backend/app/apps/cms/ backend/tests/test_cms/
git commit -m "feat: add Page & Block CRUD with block type validation"
```

### Task 3.3: Menu CRUD

**Files:**
- Modify: `backend/app/apps/cms/models.py` (add Menu)
- Modify: `backend/app/apps/cms/service_menu.py`
- Modify: `backend/app/apps/cms/router.py` (add menu routes)
- Create: `backend/tests/test_cms/test_menus.py`

- [ ] **Step 1: Write failing test**

```python
@pytest.mark.asyncio
async def test_create_menu_item(client, auth_headers):
    resp = await client.post("/api/v1/admin/menus", json={
        "name_zh": "首页", "name_en": "Home", "link": "/", "location": "header", "order": 0
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["name_zh"] == "首页"


@pytest.mark.asyncio
async def test_get_menu_public(client):
    from app.apps.cms.service_menu import create_menu_item
    await create_menu_item(name_zh="首页", name_en="Home", link="/", location="header", order=0)
    await create_menu_item(name_zh="关于我们", name_en="About", link="/about", location="header", order=1)

    resp = await client.get("/api/v1/menus?location=header")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2
    assert items[0]["name_zh"] == "首页"
```

- [ ] **Step 2: Run to verify fail, then implement models/service/router**

- [ ] **Step 2: Run to verify fail, then create model, service, and router**

Create `backend/tests/test_cms/test_menus.py`:

```python
import pytest


@pytest.mark.asyncio
async def test_create_menu_item(client, auth_headers):
    resp = await client.post("/api/v1/admin/menus", json={
        "name_zh": "首页", "name_en": "Home", "link": "/", "location": "header", "order": 0
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name_zh"] == "首页"
    assert data["location"] == "header"


@pytest.mark.asyncio
async def test_get_menu_public(client):
    from app.apps.cms.service_menu import create_menu_item
    await create_menu_item(name_zh="首页", name_en="Home", link="/", location="header", order=0)
    await create_menu_item(name_zh="关于我们", name_en="About", link="/about", location="header", order=1)

    resp = await client.get("/api/v1/menus?location=header")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2
    assert items[0]["name_zh"] == "首页"


@pytest.mark.asyncio
async def test_menu_tree_structure(client):
    from app.apps.cms.service_menu import create_menu_item
    parent = await create_menu_item(name_zh="关于", name_en="About", link="/about", location="header", order=0)
    await create_menu_item(name_zh="公司简介", name_en="Company", link="/about/company", location="header", order=0, parent_id=parent.id)
    await create_menu_item(name_zh="发展历程", name_en="History", link="/about/history", location="header", order=1, parent_id=parent.id)

    resp = await client.get("/api/v1/menus?location=header")
    items = resp.json()
    parent_node = next((i for i in items if i["name_zh"] == "关于"), None)
    assert parent_node is not None
    assert len(parent_node["children"]) == 2
```

Key model:

```python
class Menu(Base, TimestampMixin):
    __tablename__ = "menus"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("menus.id"), nullable=True)
    name_zh: Mapped[str] = mapped_column(String(100))
    name_en: Mapped[str] = mapped_column(String(100))
    link: Mapped[str] = mapped_column(String(500))
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    location: Mapped[str] = mapped_column(String(20))  # "header" | "footer"
    children: Mapped[list["Menu"]] = relationship("Menu")
```

- [ ] **Step 3: Add tree-building logic in service_menu.py**

```python
async def get_menu_tree(location: str | None = None) -> list[dict]:
    async with async_session() as db:
        q = select(Menu).where(Menu.is_visible == True)
        if location:
            q = q.where(Menu.location == location)
        q = q.order_by(Menu.order)
        result = await db.execute(q)
        items = result.scalars().all()

    # Build tree
    by_id = {m.id: {"id": m.id, "name_zh": m.name_zh, "name_en": m.name_en,
                     "link": m.link, "icon": m.icon, "children": []} for m in items}
    tree = []
    for m in items:
        node = by_id[m.id]
        if m.parent_id and m.parent_id in by_id:
            by_id[m.parent_id]["children"].append(node)
        else:
            tree.append(node)
    return tree
```

- [ ] **Step 4: Run tests, commit**

```bash
cd backend && uv run pytest tests/test_cms/ -v
git add backend/app/apps/cms/
git commit -m "feat: add Menu CRUD with tree structure"
```

---

## Phase 4: Content Modules

### Task 4.1: News module

**Files:**
- Create: `backend/app/apps/news/__init__.py`
- Create: `backend/app/apps/news/models.py`
- Create: `backend/app/apps/news/schemas.py`
- Create: `backend/app/apps/news/service.py`
- Create: `backend/app/apps/news/router.py`
- Create: `backend/tests/test_news/test_news.py`

Follow the same TDD pattern. Key model:

```python
class NewsArticle(Base, TimestampMixin):
    __tablename__ = "news_articles"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title_zh: Mapped[str] = mapped_column(String(500))
    title_en: Mapped[str] = mapped_column(String(500))
    summary_zh: Mapped[str] = mapped_column(String(1000))
    summary_en: Mapped[str] = mapped_column(String(1000))
    content_zh: Mapped[str] = mapped_column(Text)
    content_en: Mapped[str] = mapped_column(Text)
    cover_image_id: Mapped[int | None] = mapped_column(ForeignKey("media.id"))
    category: Mapped[str] = mapped_column(String(50), default="company_news")
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    cover_image: Mapped[Media | None] = relationship("Media")
```

API routes (public):
- `GET /api/v1/news?page=1&size=10&category=company_news`
- `GET /api/v1/news/{id}`

Admin routes: standard CRUD.

### Task 4.2: FAQ module

Same TDD pattern. Key model:

```python
class FAQ(Base, TimestampMixin):
    __tablename__ = "faqs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_zh: Mapped[str] = mapped_column(String(1000))
    question_en: Mapped[str] = mapped_column(String(1000))
    answer_zh: Mapped[str] = mapped_column(Text)
    answer_en: Mapped[str] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
```

### Task 4.3: Inquiry module

```python
class Inquiry(Base, TimestampMixin):
    __tablename__ = "inquiries"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(200))
    contact_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
```

Public: `POST /api/v1/inquiries`
Admin: `GET /api/v1/admin/inquiries`, `PUT .../{id}/read`

### Task 4.4: Theme module

```python
class Theme(Base, TimestampMixin):
    __tablename__ = "themes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    variables: Mapped[dict] = mapped_column(JSON, default=dict)
    tech_effects: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
```

Default theme data — seed with 3 presets:
1. "business-blue" — deep blue primary, professional
2. "tech-dark" — dark mode with neon accents
3. "classic-light" — clean white with subtle shadows

Public: `GET /api/v1/themes/active` — returns the active theme CSS variables
Admin: CRUD + `PUT .../{id}/activate`

### Commit checkpoint

```bash
uv run pytest tests/ -v
# Expected: all tests pass across all modules

git add backend/app/apps/news/ backend/app/apps/faq/ backend/app/apps/inquiry/ backend/app/apps/theme/
git commit -m "feat: add News, FAQ, Inquiry, and Theme modules"
```

---

## Phase 5: Chat Backend (RAG)

### Task 5.1: Qdrant client

**Files:**
- Create: `backend/app/core/qdrant.py`

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings

client = QdrantClient(url=settings.qdrant_url)


def ensure_collection():
    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )


async def upsert_points(points: list[dict]):
    ensure_collection()
    pts = [
        PointStruct(
            id=p["id"],
            vector=p["vector"],
            payload=p["payload"],
        )
        for p in points
    ]
    client.upsert(collection_name=settings.qdrant_collection, points=pts)


async def search_similar(vector: list[float], top_k: int = 5, score_threshold: float = 0.7) -> list[dict]:
    results = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=vector,
        limit=top_k,
        score_threshold=score_threshold,
    )
    return [{"id": r.id, "score": r.score, "payload": r.payload} for r in results]


async def delete_by_content_id(content_id: int, content_type: str):
    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector={"filter": {"must": [
            {"key": "content_id", "match": {"value": content_id}},
            {"key": "content_type", "match": {"value": content_type}},
        ]}},
    )
```

### Task 5.2: LLM provider abstraction

**Files:**
- Create: `backend/app/apps/chat/llm/__init__.py`
- Create: `backend/app/apps/chat/llm/base.py`
- Create: `backend/app/apps/chat/llm/deepseek.py`
- Create: `backend/app/apps/chat/llm/openai.py`
- Create: `backend/app/apps/chat/llm/anthropic.py`

```python
# base.py
from abc import ABC, abstractmethod
from typing import AsyncIterator


class LLMProvider(ABC):
    @abstractmethod
    async def chat_stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        ...

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...


# deepseek.py
import httpx
from app.config import settings

class DeepSeekProvider(LLMProvider):
    BASE = "https://api.deepseek.com/v1"

    async def chat_stream(self, messages, **kwargs):
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST", f"{self.BASE}/chat/completions",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={
                    "model": settings.llm_model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.3),
                    "max_tokens": kwargs.get("max_tokens", 2048),
                    "stream": True,
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        import json
                        chunk = json.loads(line[6:])
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]

    async def embed(self, texts):
        # DeepSeek doesn't have embedding API, delegate to OpenAI-compatible endpoint
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE}/embeddings",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={"model": "text-embedding-3-small", "input": texts},
            )
            data = resp.json()
            return [d["embedding"] for d in data["data"]]
```

Create OpenAI and Anthropic providers following same interface. Create a factory:

```python
# llm/__init__.py
from app.apps.chat.llm.deepseek import DeepSeekProvider
from app.apps.chat.llm.openai import OpenAIProvider
from app.apps.chat.llm.anthropic import AnthropicProvider

PROVIDERS = {
    "deepseek": DeepSeekProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
}

def get_llm_provider() -> LLMProvider:
    from app.config import settings
    cls = PROVIDERS.get(settings.llm_provider, DeepSeekProvider)
    return cls()
```

### Task 5.3: Chunker + Indexer

**Files:**
- Create: `backend/app/apps/chat/chunker.py`
- Create: `backend/app/apps/chat/indexer.py`

```python
# chunker.py
from dataclasses import dataclass


@dataclass
class Chunk:
    id: str
    text: str
    title: str
    content_id: int
    content_type: str
    language: str
    page_url: str = ""


def chunk_news(article: dict) -> list[Chunk]:
    chunks = []
    base_id = f"news_{article['id']}"
    for lang in ["zh", "en"]:
        header = f"{article[f'title_{lang}']} {article.get('published_at', '')} {article[f'summary_{lang}']}"
        chunks.append(Chunk(
            id=f"{base_id}_header_{lang}",
            text=header,
            title=article[f"title_{lang}"],
            content_id=article["id"],
            content_type="news",
            language=lang,
            page_url=f"/news/{article['id']}",
        ))
        body = article.get(f"content_{lang}", "")
        if body:
            for i in range(0, len(body), 500):
                chunks.append(Chunk(
                    id=f"{base_id}_{lang}_{i//500}",
                    text=body[i:i+550],
                    title=article[f"title_{lang}"],
                    content_id=article["id"],
                    content_type="news",
                    language=lang,
                    page_url=f"/news/{article['id']}",
                ))
    return chunks


def chunk_faq(faq: dict) -> list[Chunk]:
    chunks = []
    for lang in ["zh", "en"]:
        chunks.append(Chunk(
            id=f"faq_{faq['id']}_{lang}",
            text=f"Q: {faq[f'question_{lang}']}\nA: {faq[f'answer_{lang}']}",
            title=faq[f"question_{lang}"],
            content_id=faq["id"],
            content_type="faq",
            language=lang,
        ))
    return chunks


def chunk_page_block(block: dict) -> list[Chunk]:
    # Serialize block content to text for embedding
    text_parts = []
    content = block.get("content", {})
    for key, val in content.items():
        if isinstance(val, str):
            text_parts.append(val)
    text = " ".join(text_parts)
    if not text.strip():
        return []
    return [Chunk(
        id=f"block_{block['id']}",
        text=text,
        title=f"Block: {block.get('type', '')}",
        content_id=block["id"],
        content_type="page_block",
        language="zh",
    )]
```

```python
# indexer.py
import hashlib
from app.apps.chat.chunker import chunk_news, chunk_faq, chunk_page_block
from app.apps.chat.llm import get_llm_provider
from app.core.qdrant import upsert_points, delete_by_content_id


async def index_content(content_type: str, data: dict):
    match content_type:
        case "news":
            chunks = chunk_news(data)
        case "faq":
            chunks = chunk_faq(data)
        case "page_block":
            chunks = chunk_page_block(data)
        case _:
            return

    if not chunks:
        return

    provider = get_llm_provider()
    texts = [c.text for c in chunks]
    vectors = await provider.embed(texts)

    points = []
    for chunk, vector in zip(chunks, vectors):
        points.append({
            "id": hashlib.md5(chunk.id.encode()).hexdigest(),
            "vector": vector,
            "payload": {
                "content_id": chunk.content_id,
                "content_type": chunk.content_type,
                "title": chunk.title,
                "text": chunk.text,
                "language": chunk.language,
                "page_url": chunk.page_url,
            },
        })

    # Delete old chunks for this content, then upsert new
    await delete_by_content_id(data["id"], content_type)
    await upsert_points(points)


async def full_reindex():
    """Reindex all content — called from admin panel"""
    from app.apps.news.service import get_all_published
    from app.apps.faq.service import get_all_published
    from app.apps.cms.service_block import get_all_published_blocks

    all_news = await get_all_published()
    for article in all_news:
        await index_content("news", article.__dict__)

    all_faqs = await get_all_published()
    for faq in all_faqs:
        await index_content("faq", faq.__dict__)

    all_blocks = await get_all_published_blocks()
    for block in all_blocks:
        await index_content("page_block", block.__dict__)
```

### Task 5.4: Chat engine + SSE endpoint

**Files:**
- Create: `backend/app/apps/chat/models.py`
- Create: `backend/app/apps/chat/schemas.py`
- Create: `backend/app/apps/chat/engine.py`
- Create: `backend/app/apps/chat/retriever.py`
- Create: `backend/app/apps/chat/router_public.py`

```python
# retriever.py
from app.apps.chat.llm import get_llm_provider
from app.core.qdrant import search_similar


async def retrieve_context(query: str, language: str = "zh", top_k: int = 5) -> list[dict]:
    provider = get_llm_provider()
    query_vector = (await provider.embed([query]))[0]

    # First check FAQ (higher priority)
    faq_results = await search_similar(
        query_vector, top_k=top_k, score_threshold=0.85,
    )
    # FAQ results with score > 0.90 get returned directly without LLM

    general_results = await search_similar(
        query_vector, top_k=top_k, score_threshold=0.65,
    )
    return general_results
```

```python
# engine.py
import json
from sse_starlette.sse import EventSourceResponse
from app.apps.chat.retriever import retrieve_context
from app.apps.chat.llm import get_llm_provider
from app.apps.chat.models import ChatSession, ChatMessage


async def chat_query(session_id: str, question: str, language: str = "zh"):
    # 1. Retrieve
    sources = await retrieve_context(question, language)

    # 2. Check FAQ direct match
    high_score_faqs = [s for s in sources if s["payload"]["content_type"] == "faq" and s["score"] > 0.90]
    if high_score_faqs:
        faq_text = high_score_faqs[0]["payload"]["text"]
        answer = faq_text.split("A: ", 1)[1] if "A: " in faq_text else faq_text
        yield {"event": "sources", "data": json.dumps(high_score_faqs)}
        yield {"event": "token", "data": answer}
        yield {"event": "done", "data": ""}
        return

    # 3. Build prompt
    context_text = "\n\n---\n\n".join([
        f"[来源: {s['payload']['title']}] {s['payload']['text']}"
        for s in sources[:5]
    ])
    system_prompt = f"""You are a helpful assistant for a smart building operations company.
Answer questions based on the following context. If you cannot answer from the context, say so.
Always cite sources when available.

Context:
{context_text}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    # 4. Stream
    yield {"event": "sources", "data": json.dumps(sources[:5])}

    provider = get_llm_provider()
    full_answer = ""
    async for token in provider.chat_stream(messages):
        full_answer += token
        yield {"event": "token", "data": token}

    yield {"event": "done", "data": ""}

    # 5. Save to DB
    await save_message(session_id, "user", question)
    await save_message(session_id, "assistant", full_answer, sources)
```

```python
# router_public.py
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from app.apps.chat.engine import chat_query
from app.apps.chat.schemas import ChatRequest
from app.apps.chat.models import ChatSession, ChatMessage
import uuid

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/sessions")
async def create_session():
    session = await create_chat_session(str(uuid.uuid4()), "zh")
    return {"session_id": session.visitor_id}


@router.post("/message")
async def send_message(data: ChatRequest):
    async def event_stream():
        async for event in chat_query(data.session_id, data.message, data.language or "zh"):
            yield {"event": event["event"], "data": event["data"]}
    return EventSourceResponse(event_stream())


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    return await get_session_messages(session_id)


@router.post("/message/{message_id}/rate")
async def rate_message(message_id: int, rating: int):
    await update_rating(message_id, rating)
    return {"ok": True}
```

### Task 5.5: Wire up indexing signals

Add to each service that creates/updates/deletes content:

```python
# In news/service.py after create/update/delete
import asyncio
@app.apps.news.service.create_article(...)
    article = ...
    asyncio.create_task(index_content("news", article.__dict__))
    return article

@app.apps.news.service.delete_article(id)
    asyncio.create_task(delete_by_content_id(id, "news"))
    ...
```

### Commit checkpoint

```bash
uv run pytest tests/test_chat/ -v
# Expected: all pass

git add backend/app/apps/chat/ backend/app/core/qdrant.py
git commit -m "feat: add RAG chat engine with Qdrant, LLM providers, and SSE streaming"
```

---

## Phase 6: Public Frontend (Nuxt 3)

### Task 6.1: Nuxt 3 project setup

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/nuxt.config.ts`
- Create: `frontend/app.vue`
- Create: `frontend/tsconfig.json`

```bash
cd frontend && pnpm init && pnpm add nuxt @nuxtjs/i18n @nuxt/image vue3
```

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  ssr: true,
  modules: ["@nuxtjs/i18n", "@nuxt/image"],
  i18n: {
    locales: ["zh", "en"],
    defaultLocale: "zh",
    strategy: "prefix_except_default",
  },
  image: { domains: ["localhost"] },
  routeRules: {
    "/": { prerender: true },
    "/about": { prerender: true },
    "/products": { prerender: true },
    "/solutions": { prerender: true },
    "/contact": { prerender: true },
    "/news": { isr: 300 },
    "/news/**": { isr: 300 },
    "/chat": { ssr: false },
  },
  runtimeConfig: {
    public: { apiBase: "http://backend:8000/api/v1" },
  },
});
```

### Task 6.2: Core composables

Create `frontend/composables/usePage.ts`:

```typescript
export const usePage = async (slug: string) => {
  const config = useRuntimeConfig();
  const { data, error } = await useFetch(`${config.public.apiBase}/pages/${slug}`);
  return { page: data.value, error: error.value };
};
```

Create `frontend/composables/useTheme.ts`:

```typescript
export const useTheme = () => {
  const config = useRuntimeConfig();
  const { data: theme } = useFetch(`${config.public.apiBase}/themes/active`);

  watchEffect(() => {
    if (theme.value?.variables) {
      const root = document.documentElement;
      for (const [key, val] of Object.entries(theme.value.variables)) {
        root.style.setProperty(key, String(val));
      }
    }
  });

  return theme;
};
```

### Task 6.3: Layout + Header/Footer

- `frontend/components/layout/AppHeader.vue` — fetch menus from API, render nav tree, language switcher
- `frontend/components/layout/AppFooter.vue` — fetch footer menus + settings
- `frontend/components/layout/ThemeProvider.vue` — apply theme on mount

### Task 6.4: Block renderer components

Create `frontend/components/blocks/BlockRenderer.vue`:

```vue
<template>
  <component :is="blockComponent" :block="block" />
</template>

<script setup lang="ts">
import { computed } from 'vue';
import BlockHero from './BlockHero.vue';
import BlockNewsList from './BlockNewsList.vue';
import BlockProductCards from './BlockProductCards.vue';
// ... import all block types

const components: Record<string, any> = {
  hero: BlockHero,
  news_list: BlockNewsList,
  product_cards: BlockProductCards,
  solution_cards: BlockSolutionCards,
  stats_counter: BlockStatsCounter,
  contact_form: BlockContactForm,
  richtext: BlockRichtext,
  // ... all types
};

const props = defineProps<{ block: any }>();
const blockComponent = computed(() => components[props.block.type] || BlockRichtext);
</script>
```

Create each block component (15 total). Example for hero:

```vue
<!-- BlockHero.vue -->
<template>
  <section class="hero" :class="block.config.background" :style="heroStyle">
    <div class="hero-content">
      <h1>{{ $i18n.locale === 'zh' ? block.content.title_zh : block.content.title_en }}</h1>
      <p>{{ $i18n.locale === 'zh' ? block.content.subtitle_zh : block.content.subtitle_en }}</p>
      <div class="hero-buttons" v-if="block.content.buttons?.length">
        <a v-for="btn in block.content.buttons" :key="btn.link"
           :href="btn.link" :class="`btn-${btn.style}`">
          {{ $i18n.locale === 'zh' ? btn.text_zh : btn.text_en }}
        </a>
      </div>
    </div>
  </section>
</template>
```

### Task 6.5: Page template for dynamic pages

```vue
<!-- pages/[slug].vue -->
<template>
  <div class="page">
    <BlockRenderer v-for="block in page?.blocks" :key="block.id" :block="block" />
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const { page } = await usePage(route.params.slug as string);
</script>
```

### Task 6.6: Tech effects components

- `ParticleNetwork.vue` — Canvas 2D particle network (lightweight, no three.js for simple case)
- `GlowCursor.vue` — Custom cursor with CSS glow ring
- `ScrollReveal.vue` — GSAP ScrollTrigger wrapper
- `DigitalTwin.vue` — Three.js model viewer (dynamic import)

All tech components use `defineAsyncComponent` or dynamic import to not block initial render.

### Task 6.7: Chat widget

Create `frontend/components/chat/ChatWidget.vue` — floating chat button → expands to chat panel. Uses SSE EventSource to consume the streaming endpoint.

### Commit checkpoint

```bash
git add frontend/
git commit -m "feat: add Nuxt 3 public frontend with block rendering, theme, i18n, and chat widget"
```

---

## Phase 7: Admin Frontend (Vue3 + Vite)

### Task 7.1: Admin project setup

```bash
cd admin && pnpm create vite . --template vue-ts && pnpm add vue-router pinia axios @vueuse/core
```

### Task 7.2: Auth + Login page

- Login page with form → store JWT in Pinia + localStorage
- Axios interceptor to attach Bearer token
- Route guard to redirect unauthenticated users

### Task 7.3: Page manager + Block editor

- `admin/src/pages/pages/` — list pages, create/edit page, manage blocks
- Block editor component with dynamic form per block type — renders appropriate fields based on selected block type
- Drag-and-drop block reorder (using @vueuse/core `useSortable`)
- Live preview panel that shows how blocks will render

### Task 7.4: Media manager

- Upload with drag-and-drop, preview thumbnails
- Grid view of all media with delete
- Click to copy S3 URL

### Task 7.5: News, FAQ, Theme, Settings managers

- Each follows standard CRUD table pattern with create/edit modal
- Theme editor: code editor for CSS variables JSON, live preview
- Settings: form for LLM config with "Test Connection" button

### Task 7.6: Chat dashboard

- Conversation list with search
- Message thread view with source references
- Token usage statistics and cost estimates

### Commit checkpoint

```bash
git add admin/
git commit -m "feat: add Vue3 admin panel with block editor, media manager, and chat dashboard"
```

---

## Phase 8: Integration & Deployment

### Task 8.1: Nginx configuration

Create `nginx/nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;

    # Public frontend static files (Nuxt generate output)
    location / {
        proxy_pass http://frontend:3000;
    }

    # Admin SPA
    location /admin {
        alias /usr/share/nginx/html/admin;
        try_files $uri $uri/ /admin/index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;  # Required for SSE
    }

    # MinIO media (direct access)
    location /media/ {
        proxy_pass http://minio:9000/gweb-media/;
        proxy_set_header Host $host;
    }
}
```

### Task 8.2: Final docker-compose.yml

Add nginx, frontend, and admin services:

```yaml
  nginx:
    image: nginx:alpine
    ports: ["80:80"]
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./admin/dist:/usr/share/nginx/html/admin
    depends_on: [backend, frontend]

  frontend:
    build: ./frontend
    depends_on: [backend]

  admin:
    build: ./admin
    # Admin is served by nginx as static files
```

### Task 8.3: Seed data script

Create `backend/scripts/seed.py` that:
1. Creates admin user (admin / admin123)
2. Creates default theme presets (3 themes)
3. Creates home page with default blocks (hero, news_list, product_cards, etc.)
4. Creates header/footer menus
5. Creates sample FAQs

### Task 8.4: End-to-end smoke test

```bash
docker compose up -d
# Wait for all services
curl http://localhost/health           # Backend health
curl http://localhost/                 # Frontend HTML (non-empty)
curl http://localhost/admin/           # Admin HTML
curl http://localhost/api/v1/pages/home  # API response
```

### Commit checkpoint

```bash
git add nginx/ docker-compose.yml backend/scripts/
git commit -m "feat: add nginx config, final docker-compose, and seed data"
```

---

## Test Coverage Checklist

- [ ] Auth: login success, login fail, protected route rejection
- [ ] Settings: get/set public + encrypted
- [ ] Media: upload image (thumbnail generated), upload video, delete, auth required
- [ ] Pages: CRUD, duplicate slug rejection, public get by slug (with blocks), 404
- [ ] Blocks: create per type, content validation, reorder, cascade delete
- [ ] Menus: CRUD, tree structure, filter by location
- [ ] News: CRUD, pagination, category filter
- [ ] FAQ: CRUD, public listing
- [ ] Inquiry: submit form, admin list/read
- [ ] Theme: CRUD, activate (deactivates others)
- [ ] Chat: create session, send message (SSE stream), rate message, session history
- [ ] Chat indexing: news/faq/block indexed after create, deleted after delete
