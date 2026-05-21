# Frontend Pages & Block Renderer Design

## Context

Backend has 8 complete modules (Auth, CMS, News, FAQ, Inquiry, Theme, Settings, Chat) with 37 passing tests. Frontend has Nuxt 3 scaffold with only skeleton pages and no API integration. Need to wire up frontend to consume backend APIs and render actual content.

## Architecture

```
components/blocks/
  BlockRenderer.vue    — dispatches by block.type to correct component
  BlockHero.vue        — full-width hero with bg image, title, buttons
  BlockRichtext.vue    — raw HTML content block
  BlockNewsList.vue    — fetches /api/v1/news and renders card grid
  BlockFaq.vue         — fetches /api/v1/faqs and renders accordion
  BlockContactForm.vue — inquiry form posting to /api/v1/inquiries
  BlockProductCards.vue— card grid with image/title/desc
  BlockStatsCounter.vue— animated stat counters

composables/
  useNews.ts, useFaq.ts, useInquiry.ts, useChat.ts

pages/
  news/index.vue  — paginated news listing
  news/[id].vue   — single article detail
  faq.vue         — standalone FAQ page (uses Nuxt UI Accordion)
  contact.vue     — standalone contact form
  chat.vue        — SSE streaming chat with Nuxt UI components
```

## Data Flow

- Pages and blocks fetch data via composables wrapping `useFetch` against `runtimeConfig.public.apiBase`
- SSR pre-fetches first render; client handles pagination, form submission, chat
- BlockRenderer uses `<component :is>` dynamic dispatch on block.type
- i18n: each component reads `locale` from `useI18n()` and picks `_zh` / `_en` fields

## Block Types (7 core)

| Type | Component | Content fields |
|------|-----------|---------------|
| hero | BlockHero | title_zh/en, subtitle_zh/en, bg_image, buttons[] |
| richtext | BlockRichtext | html_content_zh/en |
| news_list | BlockNewsList | title_zh/en, count, show_date, show_image |
| faq | BlockFaq | title_zh/en (fetches /faqs) |
| contact_form | BlockContactForm | title_zh/en, fields[], submit_button_zh/en |
| product_cards | BlockProductCards | title_zh/en, cards[{image,title,desc}] |
| stats_counter | BlockStatsCounter | title_zh/en, items[{value,label}] |

## Chat (SSE)

- POST `/api/v1/chat/sessions` creates session
- POST `/api/v1/chat/message` returns SSE stream with `event: token` / `event: done`
- Client renders tokens incrementally via ReadableStream reader
- POST `/api/v1/chat/message/{id}/rate` for thumbs up/down

## Dependencies

- `@nuxt/ui` (Nuxt UI v3) added to nuxt.config.ts modules
- Uses Nuxt UI components: UAccordion, UButton, UInput, UCard, etc.
- Tailwind CSS for custom styling within block components

## Error Handling

- `useFetch` errors surfaced via `error.value` — components show Nuxt UI alert
- Form submissions disable button during loading, show success/error toast
- Chat reconnection on SSE stream break

## Testing

- Manual: start backend + frontend dev server, verify each page renders
- BlockRenderer: test each block type has a corresponding component
