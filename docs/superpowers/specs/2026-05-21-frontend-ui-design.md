# Frontend UI Design — 水流玻璃风格

## Context

Frontend has working pages and block components but no visual design. AppHeader/AppFooter have zero CSS. Pages render raw HTML with no layout styling. Need to implement a cohesive visual design system across all layout components.

**Approved direction:** R3 Water Flow + Glass Morphism — light green gradient background, SVG flow curves, glass-morphism cards, circular language toggle.

## Design Tokens

```
Primary:    #059669 (green-600)  — actions, active states, data highlights
Secondary:  #0284c7 (sky-600)   — secondary data, energy stats
Gradient:   linear-gradient(135deg, #059669, #10b981) — buttons
            linear-gradient(135deg, #059669, #0284c7) — hero keyword
Background: linear-gradient(170deg, #fff 0%, #f0fdf6 35%, #fafeff 65%, #fff 100%)
Text:       #0f172a (headings), #64748b (body), #94a3b8 (muted)
Border:     rgba(5,150,105,0.06) — subtle green borders
Shadow:     0 4px 16px rgba(0,0,0,0.015) — glass cards
            0 6px 20px rgba(5,150,105,0.12) — primary button glow
```

## Components

### AppHeader.vue

- White glass background: `rgba(255,255,255,0.75)` + `backdrop-filter: blur(18px)`
- Bottom border: `1px solid rgba(5,150,105,0.05)`
- Logo: plain text "GWEB", weight 650, color #064e3b, 16-17px
- Nav items: horizontal flex, gap 28px, 14px font, color #64748b
- Active nav item: color #059669, weight 550
- Language toggle: 44×24px pill with white circle slider containing "中"/"EN"
  - Track: `linear-gradient(135deg, #d1fae5, #a7f3d0)`, border-radius 12px
  - Slider: 20×20px white circle, `box-shadow: 0 1px 3px rgba(0,0,0,0.1)`
  - Text inside slider: 10px font, weight 600, color #059669
  - On toggle: slider slides left/right, text changes between 中/EN
- Nav items fetched from `/api/v1/menus?location=header`
- Icons: only from `menu.icon` field, no hardcoded decorative icons

### AppFooter.vue

- Top border: `1px solid rgba(5,150,105,0.04)`
- Background: transparent (inherits page gradient)
- Layout: flex row, menu links left, copyright right
- Menu links: 13px, color #64748b, gap 24px
- Copyright: 12px, color #94a3b8
- Menu items fetched from `/api/v1/menus?location=footer`

### Global Page Background

- Applied in layout or global CSS
- `background: linear-gradient(170deg, #ffffff 0%, #f0fdf6 35%, #fafeff 65%, #ffffff 100%)`
- SVG flow curves: 3 decorative paths with stroke opacity 0.03–0.07
- Curves placed as absolute positioned background element, `pointer-events: none`

### Block Components

All 15 block components already exist with Tailwind utility classes. Minor refinements:

- **BlockHero**: Already styled with `bg-gray-900 text-white` — keep as-is, serves as dark contrast to light page
- **BlockStatsCounter**: Stat cards get glass effect: `background: rgba(255,255,255,0.65)`, `backdrop-filter: blur(12px)`, subtle border + shadow
- **BlockProductCards**: Cards get white background with subtle border, matching the clean card style
- **Other blocks**: Maintain existing Tailwind classes, ensure green accent color consistency

## Layout

### layouts/default.vue

```vue
<template>
  <div class="site" style="background: linear-gradient(170deg, #ffffff 0%, #f0fdf6 35%, #fafeff 65%, #ffffff 100%)">
    <!-- SVG flow curves as background decoration -->
    <svg class="flow-curves" aria-hidden="true">...</svg>
    <AppHeader />
    <main>
      <slot />
    </main>
    <AppFooter />
  </div>
</template>
```

The SVG curves go directly in the layout template as a decorative background element.

## Language Toggle Behavior

- Client-side only (wrapped in `<ClientOnly>` or driven by `useI18n()`)
- Click toggles `locale.value` between 'zh' and 'en'
- Slider animates with CSS `transition: transform 0.2s ease`
- Track color stays green regardless of state
- Text inside slider: "中" when locale is zh, "EN" when locale is en

## Typography

- System font stack (no external font loading for v1)
- Headings: weight 300–650, letter-spacing -1px to -1.5px
- Numbers: `font-variant-numeric: tabular-nums` for stat values
- Body: 14-15px, line-height 1.7-1.8, color #64748b
- Muted/small: 11-12px, color #94a3b8

## What NOT to Add

- No emoji or decorative Unicode icons
- No icon libraries (FontAwesome, Heroicons, etc.) unless from menu.icon
- No stock photos or placeholder images beyond what seed data provides
- No background video or particle effects
- No scroll-jacking or excessive animations

## Implementation Scope

1. **AppHeader.vue** — full Tailwind restyle + language toggle
2. **AppFooter.vue** — full Tailwind restyle
3. **layouts/default.vue** — background gradient + SVG curves
4. **BlockStatsCounter.vue** — glass card refinement
5. **BlockProductCards.vue** — card style consistency
6. **Global CSS** — base typography defaults

## Testing

- Manual: start dev servers, verify all 5 pages render with correct styling
- Check zh/en language toggle works across pages
- Verify header/footer menu items load from API
- Check mobile responsiveness (header should wrap or collapse)
