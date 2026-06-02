# Audit Log Design

## Overview

Admin operation audit log — records create/update/delete actions performed by admin/editor users in the management backend. Read-only log viewer with filtering and CSV export.

## Backend

### New `audit` app

**Model `AuditLog`** (audit/models.py):
- `id` int PK
- `user_id` int FK → users
- `username` str — denormalized for display after user deletion
- `action` str — create / update / delete
- `resource_type` str — news / page / user / media / menu / setting / inquiry
- `resource_id` int — nullable (resource may be deleted)
- `resource_name` str — human-readable label (e.g. article title)
- `detail` JSON — optional, stores before/after snapshots or change summary
- `ip_address` str — nullable
- `created_at` datetime (TimestampMixin)

**Service** (audit/service.py):
- `create_audit_log(...)` — called by other services
- `list_audit_logs(page, size, user_id, action, resource_type, start_date, end_date)` → (items, total)
- `export_csv(user_id, action, resource_type, start_date, end_date)` → CSV string

**Router** (audit/router.py):
- `GET /api/v1/admin/audit-logs` — paginated list with filters (requires auth)
- `GET /api/v1/admin/audit-logs/export` — CSV download (requires auth)

### Integration points

Add `await create_audit_log(...)` calls in service-layer methods after successful operations:

| Module | Service file | Operations |
|--------|-------------|------------|
| news | news/service.py | create, update, delete |
| pages | cms/service_page.py | create, update, delete |
| media | cms/service_media.py | upload, delete |
| menus | cms/service_menu.py | create, update, delete |
| users | users/service.py | create, update, delete |
| settings | settings/service.py | set (update) |
| inquiry | inquiry/service.py | mark_read |

### Database migration

New table `audit_logs` — auto-created via SQLAlchemy on startup (consistent with existing pattern).

## Frontend

**New page `admin/audit-logs.vue`**:

- Layout: `admin` + middleware `admin-auth`
- Header: back link → dashboard, title "审计日志", subtitle
- Filter bar: user select, action select, resource type select, date range (start/end date inputs), export CSV button
- Table columns: timestamp, user, action (color-coded badge), resource type, resource name, detail (click to expand modal)
- Pagination at bottom
- Export: calls `/admin/audit-logs/export` and triggers browser download

**Dashboard link**: Add "审计日志" entry to `/admin/index.vue` links array.

## Styling

Follows existing admin dark-theme conventions: `background: #090d12`, green accent `#059669`, white text with opacity layers, rounded-xl cards, consistent 12px/13px/14px typography.
