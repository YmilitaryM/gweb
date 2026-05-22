# 用户管理系统 — 设计文档

**日期:** 2026-05-22
**状态:** 待实现

## 概述

为后台管理系统添加完整的用户管理功能。现有 `users` 表只有基本认证字段，需扩展个人信息字段，并添加后端 CRUD API 和前端管理页面。

## 数据库变更

在 `users` 表新增 4 个可空字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `avatar` | `String(500)` | 头像 URL，来自 media upload |
| `display_name` | `String(100)` | 显示名称 |
| `phone` | `String(30)` | 手机号 |
| `email` | `String(200)` | 邮箱 |

现有字段不变（`id`, `username`, `password_hash`, `role`, `created_at`, `updated_at`）。

## 后端设计

### 新增 `require_admin` 依赖 (`apps/auth/router.py`)

在 `get_current_user` 基础上检查 `role == UserRole.admin`，否则返回 403。

### 新建 `apps/users/` 模块

遵循项目现有分层：

```
apps/users/
├── __init__.py
├── schemas.py    # UserCreate, UserUpdate, UserOut
├── service.py    # list_users, create_user, update_user, delete_user
└── router.py     # CRUD endpoints (admin-only)
```

### API 端点

所有端点前缀 `/api/v1/admin/users`，依赖 `require_admin`。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/users` | 用户列表 |
| `POST` | `/users` | 创建用户 |
| `PUT` | `/users/{user_id}` | 编辑用户（部分更新） |
| `DELETE` | `/users/{user_id}` | 删除用户（不能删除自己） |

### Schemas

**UserCreate:** `username` (必填), `password` (必填), `role` (必填), `display_name`, `phone`, `email`, `avatar`  
**UserUpdate:** 所有字段可选，只更新传入的字段  
**UserOut:** `id`, `username`, `role`, `display_name`, `phone`, `email`, `avatar`, `created_at`

### Service

- `list_users()` — 查询全部用户
- `create_user(...)` — 复用 `auth/service.py` 的 `create_user` 并扩展
- `update_user(user_id, **kwargs)` — 部分更新
- `delete_user(user_id)` — 删除用户

### 注册路由 (`main.py`)

```python
from app.apps.users.router import router as users_router
app.include_router(users_router)
```

## 前端设计

### 新页面 `pages/admin/users.vue`

- 表格展示：头像、用户名、显示名、角色 badge、操作按钮
- 新建/编辑模态框：头像上传（复用 media upload API）、用户名、显示名、密码（编辑时选填）、手机号、邮箱、角色下拉选择
- 删除：二次确认弹窗，当前登录用户不能删除自己
- 风格与现有 admin 页面一致（深色 glass-morphism）

### 修改 `pages/admin/index.vue`

Dashboard 快捷链接新增一行：`{ to: '/admin/users', label: '用户管理', desc: '管理后台管理员和编辑者账号' }`

## 边界情况

- 不能删除当前登录用户自己
- 用户名唯一性校验
- 编辑用户时密码字段为空则不更新密码
- 删除用户前确认，防止误操作
- 只有 admin 角色可以访问用户管理
