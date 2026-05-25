# Page-Menu Refactor: CMS Pages as Canonical Route Registry

> **Goal:** Make CMS pages the single source of truth for all frontend routes. Every public route must correspond to a CMS page. Menus reference pages by ID, not free-text URLs. All hardcoded Vue pages are replaced by CMS page types + blocks rendered through a catch-all `[...slug].vue`.

**Architecture:** Pages gain a `type` field (`content`/`news`/`products`/`faq`/`contact`) that determines rendering mode. A single `[...slug].vue` catch-all route handles all CMS pages and their dynamic children (e.g., `/news/123`, `/products/some-slug`). Menus link to pages via `page_id` FK instead of free-text `link`. Dedicated Vue pages for news, FAQ, contact, and products are deleted.

**Tech Stack:** Nuxt 3 (catch-all route, `[...slug].vue`), FastAPI + SQLAlchemy async (PostgreSQL), Vue 3 Composition API

---

## 1. Page Type System

### 1.1 Types

| Type | Render Mode | Dynamic Child Routes |
|------|-------------|---------------------|
| `content` | Blocks only (BlockRenderer) | None |
| `news` | Blocks + article list | `/news/:id` (article detail) |
| `products` | Blocks + product catalog (category tabs, pagination) | `/products/:slug` (product detail) |
| `faq` | Blocks + FAQ accordion panel | None |
| `contact` | Blocks + inquiry form | None |

### 1.2 Database Migration

**`pages` table:**
- Add `type` VARCHAR(20), NOT NULL, default `'content'`
- Existing 5 pages mapped:
  - home → `content`
  - about → `content`
  - products → `products` (changed from `content`)
  - solutions → `content`
  - contact → `contact` (changed from `content`)

**New pages to create after migration:**
  - `news` slug=news, type=`news`
  - `faq` slug=faq, type=`faq`
  - `products` → update type from `content` to `products`
  - `contact` → update type from `content` to `contact`

**`menus` table:**
- Add `page_id` INTEGER (FK → pages.id, nullable)
- Migrate existing data: resolve `menu.link` → matching `pages.slug`, set `page_id`
- Keep `link` column temporarily during migration, drop after frontend is updated

### 1.3 API Changes

**Page schemas (`schemas.py`):**
- `PageCreate`: add `type` field (optional, default `"content"`)
- `PageUpdate`: add `type` field (optional)
- `PageOut`: add `type` field
- `PageListResponse`: add `type` field

**Menu schemas:**
- `MenuCreate`: add `page_id` (optional, int FK), deprecate `link`
- `MenuUpdate`: add `page_id` (optional)
- `MenuResponse`: add `page_id` and `page_slug` (populated from join)

**Public endpoint:**
- `GET /api/v1/pages/slugs` — return list of `{ slug, type }` for all published pages, used by frontend to resolve which CMS page to load

**Admin endpoints:**
- `GET /api/v1/admin/pages` — return `type` in response
- `POST /api/v1/admin/pages` — accept `type`
- `PUT /api/v1/admin/pages/{id}` — accept `type`

---

## 2. Frontend Routing

### 2.1 Route Structure

Use Nuxt catch-all route `[...slug].vue` which captures all path segments as an array:

| URL | `route.params.slug` |
|-----|---------------------|
| `/` | `['home']` (via index.vue redirect) |
| `/about` | `['about']` |
| `/news` | `['news']` |
| `/news/123` | `['news', '123']` |
| `/products` | `['products']` |
| `/products/some-item` | `['products', 'some-item']` |
| `/faq` | `['faq']` |
| `/contact` | `['contact']` |

Nuxt route priority: explicit files > dynamic routes > catch-all. Admin routes (`/admin/**`) and `/chat` remain as explicit files and are not intercepted.

### 2.2 File Changes

**New:**
- `frontend/pages/[...slug].vue` — catch-all CMS page handler

**Modified:**
- `frontend/pages/index.vue` — redirect to CMS page with slug=home (or load it directly)
- `frontend/components/layout/AppHeader.vue` — adapt to menu response with `page_slug`

**Deleted:**
- `frontend/pages/[slug].vue`
- `frontend/pages/news/index.vue`
- `frontend/pages/news/[id].vue`
- `frontend/pages/faq.vue`
- `frontend/pages/contact.vue`
- `frontend/pages/products/index.vue`
- `frontend/pages/products/[slug].vue`

### 2.3 index.vue

The home page at `/` is a special case. Since `[...slug].vue` only matches paths with at least one segment, the root `/` matches `index.vue`. This page uses `usePage('home')` to fetch the CMS page with slug=home and renders it identically to a `type=content` page.

```vue
<template>
  <div>
    <BlockRenderer v-for="block in page?.blocks" :key="block.id" :block="block" />
    <p v-if="!page">Loading...</p>
  </div>
</template>

<script setup>
import BlockRenderer from '~/components/blocks/BlockRenderer.vue';
const { page } = await usePage('home');
</script>
```

### 2.4 `[...slug].vue`

```vue
<script setup>
import BlockRenderer from '~/components/blocks/BlockRenderer.vue';

const route = useRoute();
const slug = (route.params.slug as string[]);
const pageSlug = slug[0];
const detailParam = slug[1] || null;

const { page } = await usePage(pageSlug);

if (!page) throw createError({ statusCode: 404 });
</script>
```

Rendering logic (pseudocode):

```
type=content:
  → if detailParam → 404
  → render page.blocks via BlockRenderer

type=news:
  → if no detailParam:
      render page.blocks
      render <NewsArticleList :config="newsListBlockContent" />
  → if detailParam:
      render <NewsArticleDetail :articleId="detailParam" />

type=products:
  → if no detailParam:
      render page.blocks
      render <ProductCatalog />
  → if detailParam:
      render <ProductDetail :productSlug="detailParam" />

type=faq:
  → render page.blocks
  → render <FaqPanel />

type=contact:
  → render page.blocks
  → render <ContactFormBlock />
```

Each dynamic section (NewsArticleList, NewsArticleDetail, ProductCatalog, ProductDetail, FaqPanel, ContactFormBlock) is extracted as a component in `components/blocks/` and receives its configuration from the page's blocks or from URL parameters.

### 2.5 Nuxt Route Rules Update

```ts
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
```

---

## 3. Menu → Page Linkage

### 3.1 Backend

`Menu` model: add `page_id` FK, keep `link` as computed fallback.

```python
page_id: Mapped[int | None] = mapped_column(ForeignKey("pages.id"), nullable=True)
page: Mapped["Page | None"] = relationship("Page")
```

Menu API response includes `page_slug` so frontend can construct links without knowing IDs:

```json
{
  "id": 2,
  "name_zh": "产品中心",
  "page_id": 3,
  "page_slug": "products",
  "children": []
}
```

### 3.2 Frontend Admin (menus.vue)

Replace free-text `link` input with a page selector dropdown:

```
[下拉选择: 选择页面 ▼]
  /home — 首页 (content)
  /about — 关于我们 (content)
  /products — 产品中心 (products)
  /solutions — 解决方案 (content)
  /news — 新闻中心 (news)
  /faq — 常见问题 (faq)
  /contact — 联系我们 (contact)
```

Fetch published pages list and render as select options. Menu link is derived from page slug.

### 3.3 AppHeader.vue

When rendering menu items, use `page_slug` to construct `NuxtLink` target:

```vue
<NuxtLink :to="'/' + item.page_slug">
  {{ locale === 'zh' ? item.name_zh : item.name_en }}
</NuxtLink>
```

Home page (slug=home) is a special case: its link is `/` not `/home`. In the AppHeader, check `page_slug === 'home'` and render `to="/"` instead of `to="/home"`. All other pages link as `to="/" + page_slug`.

---

## 4. Component Extraction

Each rendering mode used in `[...slug].vue` is extracted as a clean component:

| Component | Location | Purpose |
|-----------|----------|---------|
| `NewsArticleList.vue` | `components/blocks/` | Fetches and renders paginated news article cards (replaces `pages/news/index.vue`) |
| `NewsArticleDetail.vue` | `components/blocks/` | Fetches and renders single article (replaces `pages/news/[id].vue`) |
| `ProductCatalog.vue` | `components/blocks/` | Category tabs + paginated product grid (replaces `pages/products/index.vue`) |
| `ProductDetail.vue` | `components/blocks/` | Product hero + specs + description (replaces `pages/products/[slug].vue`) |
| `FaqPanel.vue` | `components/blocks/` | Accordion FAQ list (replaces `pages/faq.vue`) |
| `ContactFormBlock.vue` | `components/blocks/` | Inquiry form (replaces `pages/contact.vue`) |

Existing `BlockContactForm.vue` and `BlockFaq.vue` remain as separate blocks for embedding within `type=content` pages. The new components are standalone page-level components, not CMS blocks, but share the same composables (`useFaqs`, `useInquiry`, `useNewsList`, `useNewsArticle`, etc.).

### 4.1 NewsArticleList

Config comes from the page's first `news_list` block. When the page is type=news, `[...slug].vue` looks for a block of type `news_list` in `page.blocks` and extracts `content.count`, `content.show_date`, `content.show_image`, `content.category_filter` to configure the paginated list. If no `news_list` block exists, sensible defaults apply (count=6, show_date=true, show_image=true).

```ts
interface NewsListConfig {
  count: number;      // items per page (default 6)
  show_date: boolean;
  show_image: boolean;
  category_filter: string | null;
}
```

Fetches `GET /api/v1/news?page=&size=&category=`.

### 4.2 ProductCatalog

Fetches `GET /api/v1/product-categories` and `GET /api/v1/products?page=&size=&category=`. No block config needed — the product API handles categorization.

### 4.3 NewsArticleDetail / ProductDetail

Pure API-to-UI rendering. Fetches single entity by ID/slug, renders with breadcrumb + content.

---

## 5. Existing Block Adjustments

### 5.1 BlockNewsList

Current `BlockNewsList.vue` is a section-level block for embedding a few news cards within a `content` page. Keep it as-is but increase configurability: support click navigation to `/news/:id` detail page. The page-level `NewsArticleList.vue` component replaces `pages/news/index.vue` and handles full-page layout with pagination.

### 5.2 BlockProductCards

Current `BlockProductCards.vue` renders static CMS-managed product cards (curated selection). Keep it. The new `ProductCatalog.vue` component is a separate page-level component for the full dynamic catalog.

### 5.3 Block ContactForm and BlockFaq

Keep both as embeddable blocks for `type=content` pages. The `type=contact` and `type=faq` page types render the page-level equivalents (`ContactFormBlock.vue`, `FaqPanel.vue`) which are essentially the same components but with full-page layout.

---

## 6. Admin UI Changes

### 6.1 Pages Admin (pages.vue)

- Add `type` selector in create/edit form: dropdown with radio-like options (content / news / products / faq / contact)
- Show `type` badge in page list rows alongside publish status
- Changing `type` from `content` to something else is allowed (user intent: this page should now function as that type)

### 6.2 Menus Admin (menus.vue)

- Replace `link` text input with `page_id` page selector dropdown
- Dropdown lists all published pages grouped by type
- Selected page's slug is shown as read-only link preview

### 6.3 Dashboard (admin/index.vue)

- Page count now includes all pages regardless of type
- Stats card for "pages" shows total count

---

## 7. Pre/Publish & SSR

### 7.1 Prerender

Static pages (content type) are prerendered. Dynamic pages (news, products) use ISR.

Route rules updated in Section 2.5.

### 7.2 API Deprecation

Old public endpoints remain (no breaking change to backend API):
- `GET /api/v1/products` — still used by ProductCatalog
- `GET /api/v1/products/{slug}` — still used by ProductDetail
- `GET /api/v1/news` — still used by NewsArticleList
- `GET /api/v1/news/{id}` — still used by NewsArticleDetail
- `GET /api/v1/faqs` — still used by FaqPanel
- `POST /api/v1/inquiries` — still used by ContactFormBlock

---

## 8. Migration Steps (Execution Order)

1. Backend: Add `type` column to pages, `page_id` column to menus
2. Backend: Create seed data for news, faq pages; update products/contact types
3. Backend: Migrate existing menu data (resolve `link` → `page_id`)
4. Backend: Update schemas and API to include `type` and `page_id`
5. Frontend: Create `[...slug].vue` catch-all page
6. Frontend: Extract 6 page-level components from deleted pages
7. Frontend: Update `index.vue` to use `usePage('home')`
8. Frontend: Update `menu.vue` admin — page selector dropdown
9. Frontend: Update `pages.vue` admin — type selector
10. Frontend: Update `AppHeader.vue` — use `page_slug` from menu
11. Frontend: Delete 7 hardcoded page files
12. Backend: Drop `link` column from menus
13. Backend: Update prerender / route rules in nuxt.config.ts
14. Tests: Update all affected tests
15. Build: Full build + prerender verification
