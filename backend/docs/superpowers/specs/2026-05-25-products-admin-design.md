# Products Admin Management — Design Spec

## Overview

Add first-class product management to the admin backend. Products currently only exist as a `product_cards` CMS block type; this spec adds dedicated product and product category entities with full CRUD APIs, admin pages, and public-facing list/detail pages.

## Database

### New Table: `product_categories`

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default uuid4 |
| name_zh | VARCHAR(200) | NOT NULL |
| name_en | VARCHAR(200) | NOT NULL |
| slug | VARCHAR(200) | NOT NULL, UNIQUE |
| sort_order | INTEGER | NOT NULL, DEFAULT 0 |
| is_published | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | DATETIME | NOT NULL, DEFAULT now |
| updated_at | DATETIME | NOT NULL, DEFAULT now, ON UPDATE now |

### New Table: `products`

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default uuid4 |
| category_id | UUID | NOT NULL, FK → product_categories.id |
| name_zh | VARCHAR(300) | NOT NULL |
| name_en | VARCHAR(300) | NOT NULL |
| slug | VARCHAR(300) | NOT NULL, UNIQUE |
| cover_image_id | UUID | NULLABLE, FK → media.id |
| summary_zh | TEXT | NULLABLE |
| summary_en | TEXT | NULLABLE |
| description_zh | TEXT | NULLABLE (rich text) |
| description_en | TEXT | NULLABLE (rich text) |
| specs | JSON | NULLABLE (array of {key, value} objects) |
| images | JSON | NULLABLE (array of media UUIDs) |
| sort_order | INTEGER | NOT NULL, DEFAULT 0 |
| is_published | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | DATETIME | NOT NULL, DEFAULT now |
| updated_at | DATETIME | NOT NULL, DEFAULT now, ON UPDATE now |

### Migration

New Alembic migration adding both tables with indexes on `slug`, `category_id`, `is_published`, and `sort_order`.

## Backend

### Models

- `backend/app/apps/products/models.py` — `ProductCategory` and `Product` SQLAlchemy models

### Schemas

- `backend/app/apps/products/schemas.py` — Pydantic request/response schemas (Create/Update/Response for both entities)

### Service

- `backend/app/apps/products/service.py` — CRUD operations for categories and products

### Admin Routes (JWT-protected)

All under `/api/v1/admin/`, authenticated, audit-logged.

| Method | Path | Description |
|--------|------|-------------|
| POST | `/product-categories` | Create category |
| GET | `/product-categories` | List all categories (sorted by sort_order) |
| GET | `/product-categories/{id}` | Get single category |
| PUT | `/product-categories/{id}` | Update category |
| DELETE | `/product-categories/{id}` | Delete category (block if products exist) |
| POST | `/products` | Create product |
| GET | `/products` | List products (?category_id=&page=&page_size=) |
| GET | `/products/{id}` | Get single product |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Delete product |

### Public Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/products` | List published products (?category={slug}&page=&page_size=) |
| GET | `/api/v1/products/{slug}` | Product detail by slug |

### Audit Log Integration

Actions logged: `create`, `update`, `delete` on resource types `product_category` and `product`. Resource name captured for display.

## Frontend — Admin

### Product Categories Page (`/admin/product-categories`)

- Table list: name (zh/en), slug, sort_order, published status badge, actions (edit/delete)
- Create/Edit modal: name fields, slug input, sort order input, publish toggle
- Delete blocked with error message if category has products

### Products Page (`/admin/products`)

- Category filter tabs at top (All + each category), dynamically loaded from categories API
- Paginated table: cover thumbnail, name (zh/en), category name, sort_order, published badge, timestamp, actions
- Create/Edit modal (full-width or large modal):
  - Bilingual name fields
  - Category dropdown
  - Slug input (auto-generated from zh name, editable)
  - Cover image picker (opens media library selector)
  - Bilingual summary textareas
  - Bilingual description rich-text editors (or textareas minimal, reuse existing pattern)
  - Specs editor: dynamic key-value pair list (add row / remove row)
  - Image gallery editor: pick from media library, reorder via drag or simple order
  - Sort order input, publish toggle

### Admin Dashboard Update

Add product count and category count to the stats cards on `/admin`.

### Admin Navigation

Add "Products" and "Product Categories" to the admin dashboard quick-link cards.

## Frontend — Public

### Product List Page (`/products`)

- Category filter tabs
- Product card grid (cover image, name, summary, link to detail)
- Each card links to `/products/{slug}`

### Product Detail Page (`/products/[slug]`)

- Hero section: cover image + product name + category badge
- Specs table (if specs present)
- Rich text description
- Image gallery (if images present)
- Breadcrumb: Home > Products > [Category] > [Product Name]

### Components

- `ProductCard.vue` — card component for listing
- Reuse `BlockProductCards.vue` patterns where applicable

## Testing

- Backend unit tests for product/category CRUD services
- Backend API tests for admin and public routes
- Verify audit log entries are created on mutations

## Files to Create/Modify

### New Files

| File | Purpose |
|------|---------|
| `backend/app/apps/products/__init__.py` | Package init |
| `backend/app/apps/products/models.py` | SQLAlchemy models |
| `backend/app/apps/products/schemas.py` | Pydantic schemas |
| `backend/app/apps/products/service.py` | Business logic |
| `backend/app/apps/products/router.py` | Admin + public API routes |
| `backend/app/alembic/versions/xxxx_add_products_tables.py` | Migration |
| `frontend/pages/admin/products.vue` | Admin product management |
| `frontend/pages/admin/product-categories.vue` | Admin category management |
| `frontend/pages/products/index.vue` | Public product list |
| `frontend/pages/products/[id].vue` | Public product detail |
| `frontend/components/ProductCard.vue` | Product card component |
| `backend/tests/test_products/` | Product tests |

### Modified Files

| File | Change |
|------|--------|
| `backend/app/main.py` | Register products router |
| `frontend/pages/admin/index.vue` | Add product/category stats + quick links |

### Block Component Cleanup

After products are a first-class entity, the `product_cards` CMS block type could eventually be deprecated or updated to reference product entities instead of inline data. This is out of scope for this spec and should be a follow-up decision.
