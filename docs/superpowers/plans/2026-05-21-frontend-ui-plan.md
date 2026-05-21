# Frontend UI — 水流玻璃风格 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement cohesive visual design across all layout components using Tailwind CSS — glass-morphism header, light green gradient background, SVG flow curves, circular language toggle.

**Architecture:** All styling uses Tailwind utility classes directly in Vue SFC `<template>` blocks. No separate CSS files. The layout wraps pages in gradient background + SVG decorations. Header/Footer use `backdrop-filter` for glass effect. Language toggle is a pure CSS animated pill switch driven by `useI18n().locale`.

**Tech Stack:** Nuxt 3, Tailwind CSS v4, Nuxt UI v3, @nuxtjs/i18n

---

### Task 1: AppHeader — Glass Header + Circular Language Toggle

**Files:**
- Modify: `frontend/components/layout/AppHeader.vue` (full rewrite)

- [ ] **Step 1: Replace template with Tailwind-styled glass header**

Replace the entire file content:

```vue
<template>
  <header
    class="sticky top-0 z-50 flex items-center justify-between px-8 py-4"
    style="background: rgba(255,255,255,0.75); backdrop-filter: blur(18px); border-bottom: 1px solid rgba(5,150,105,0.05)"
  >
    <!-- Logo -->
    <NuxtLink to="/" class="text-[17px] font-semibold tracking-tight text-emerald-900 no-underline">
      {{ settings?.site_name_zh || 'GWEB' }}
    </NuxtLink>

    <!-- Nav -->
    <nav class="flex gap-7">
      <NuxtLink
        v-for="item in menu"
        :key="item.id"
        :to="item.link"
        class="text-sm transition-colors"
        :class="$route.path === item.link ? 'text-emerald-600 font-medium' : 'text-slate-500 hover:text-slate-700'"
      >
        {{ locale === 'zh' ? item.name_zh : item.name_en }}
      </NuxtLink>
    </nav>

    <!-- Language Toggle -->
    <button
      class="relative w-11 h-6 rounded-full cursor-pointer border-none transition-colors duration-200"
      :class="locale === 'zh' ? 'bg-emerald-100' : 'bg-slate-100'"
      @click="toggleLang"
      :aria-label="locale === 'zh' ? 'Switch to English' : '切换到中文'"
    >
      <span
        class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm flex items-center justify-center text-[10px] font-semibold transition-transform duration-200"
        :class="locale === 'zh' ? 'left-0.5 text-emerald-600' : 'left-[calc(100%-22px)] text-slate-400'"
      >
        {{ locale === 'zh' ? '中' : 'EN' }}
      </span>
    </button>
  </header>
</template>

<script setup lang="ts">
const { locale } = useI18n();
const config = useRuntimeConfig();
const { data: menu } = await useFetch(`${config.public.apiBase}/menus?location=header`);
const { data: settings } = await useFetch(`${config.public.apiBase}/settings`);

function toggleLang() {
  locale.value = locale.value === 'zh' ? 'en' : 'zh';
}
</script>
```

- [ ] **Step 2: Verify header renders in browser**

Open `http://localhost:3000` — check: glass header visible, nav items link correctly, language toggle shows "中" on left side in green.

- [ ] **Step 3: Test language toggle**

Click the toggle — verify slider slides right, text changes to "EN", page locale switches.

- [ ] **Step 4: Commit**

```bash
git add frontend/components/layout/AppHeader.vue
git commit -m "feat: restyle AppHeader with glass effect and circular language toggle"
```

---

### Task 2: AppFooter — Tailwind Restyle

**Files:**
- Modify: `frontend/components/layout/AppFooter.vue` (full rewrite)

- [ ] **Step 1: Replace template with Tailwind-styled footer**

Replace the entire file content:

```vue
<template>
  <footer class="flex items-center justify-between px-8 py-5 border-t" style="border-color: rgba(5,150,105,0.04)">
    <nav class="flex gap-6">
      <NuxtLink
        v-for="item in menu"
        :key="item.id"
        :to="item.link"
        class="text-[13px] text-slate-500 hover:text-slate-700 transition-colors no-underline"
      >
        {{ locale === 'zh' ? item.name_zh : item.name_en }}
      </NuxtLink>
    </nav>
    <span class="text-xs text-slate-400">© 2026 GWEB</span>
  </footer>
</template>

<script setup lang="ts">
const { locale } = useI18n();
const config = useRuntimeConfig();
const { data: menu } = await useFetch(`${config.public.apiBase}/menus?location=footer`);
</script>
```

- [ ] **Step 2: Verify footer renders**

Open `http://localhost:3000` — check: footer links load from API, copyright visible, layout is horizontal.

- [ ] **Step 3: Commit**

```bash
git add frontend/components/layout/AppFooter.vue
git commit -m "feat: restyle AppFooter with Tailwind"
```

---

### Task 3: Layout — Background Gradient + SVG Flow Curves

**Files:**
- Modify: `frontend/layouts/default.vue` (replace content)

- [ ] **Step 1: Replace layout with gradient background and SVG curves**

Replace the entire file content:

```vue
<template>
  <div
    class="site min-h-screen"
    style="background: linear-gradient(170deg, #ffffff 0%, #f0fdf6 35%, #fafeff 65%, #ffffff 100%)"
  >
    <!-- Decorative flow curves -->
    <svg
      class="fixed inset-0 w-full h-full pointer-events-none -z-10"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M0,120 C200,90 300,170 500,120 C650,80 700,150 800,130"
        fill="none"
        stroke="rgba(5,150,105,0.07)"
        stroke-width="1.5"
        preserveAspectRatio="none"
      />
      <path
        d="M0,210 C180,240 350,180 500,210 C620,230 720,190 800,220"
        fill="none"
        stroke="rgba(5,150,105,0.04)"
        stroke-width="1"
        preserveAspectRatio="none"
      />
      <path
        d="M0,300 C250,330 400,250 550,300 C650,320 750,280 800,310"
        fill="none"
        stroke="rgba(59,130,246,0.03)"
        stroke-width="1"
        preserveAspectRatio="none"
      />
    </svg>

    <AppHeader />
    <main>
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import AppHeader from '~/components/layout/AppHeader.vue';
import AppFooter from '~/components/layout/AppFooter.vue';
</script>
```

- [ ] **Step 2: Verify layout renders**

Open `http://localhost:3000` — check: page has green gradient background, SVG curves visible as subtle decorative lines.

- [ ] **Step 3: Commit**

```bash
git add frontend/layouts/default.vue
git commit -m "feat: add gradient background and SVG flow curves to layout"
```

---

### Task 4: BlockStatsCounter — Glass Card Refinement

**Files:**
- Modify: `frontend/components/blocks/BlockStatsCounter.vue` (replace content)

- [ ] **Step 1: Change from dark bg to light glass cards**

Replace the entire file content:

```vue
<template>
  <section class="py-16 px-4">
    <div class="max-w-4xl mx-auto">
      <h2
        v-if="content.title_zh"
        class="text-3xl font-light text-center mb-10 text-slate-800 tracking-tight"
      >
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="flex justify-center gap-5 flex-wrap">
        <div
          v-for="(item, i) in content.items"
          :key="i"
          class="flex-1 min-w-[140px] max-w-[180px] text-center py-5 px-4 rounded-2xl border"
          style="background: rgba(255,255,255,0.65); backdrop-filter: blur(12px); border-color: rgba(5,150,105,0.06); box-shadow: 0 4px 16px rgba(0,0,0,0.015)"
        >
          <div
            class="text-[30px] font-light tracking-tight"
            :class="i >= 2 ? 'text-sky-600' : 'text-emerald-600'"
            style="font-variant-numeric: tabular-nums"
          >
            {{ item.value }}
          </div>
          <div class="text-xs text-slate-400 mt-1">
            {{ locale === 'zh' ? item.label_zh : item.label_en }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();
const { locale } = useI18n();
</script>
```

- [ ] **Step 2: Verify stats render correctly**

Open `http://localhost:3000` — check: stats section shows glass cards with green/blue numbers, labels below. First two stats green, last two blue.

- [ ] **Step 3: Commit**

```bash
git add frontend/components/blocks/BlockStatsCounter.vue
git commit -m "feat: refine BlockStatsCounter with glass card style"
```

---

### Task 5: BlockProductCards — Card Style Consistency

**Files:**
- Modify: `frontend/components/blocks/BlockProductCards.vue` (replace content)

- [ ] **Step 1: Refine cards for consistency with design system**

Replace the entire file content:

```vue
<template>
  <section class="py-16 px-4">
    <div class="max-w-6xl mx-auto">
      <h2
        v-if="content.title_zh"
        class="text-3xl font-light text-center mb-10 text-slate-800 tracking-tight"
      >
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="(card, i) in content.cards"
          :key="i"
          class="bg-white border rounded-xl p-6 transition-shadow hover:shadow-md"
          style="border-color: #e8f5e9"
        >
          <img
            v-if="card.image"
            :src="card.image"
            alt=""
            class="w-full h-48 object-cover rounded-lg mb-4"
          />
          <h3 class="text-lg font-medium text-slate-800 mb-2">
            {{ locale === 'zh' ? card.title_zh : card.title_en }}
          </h3>
          <p class="text-sm text-slate-500 leading-relaxed mb-4">
            {{ locale === 'zh' ? card.desc_zh : card.desc_en }}
          </p>
          <NuxtLink
            v-if="card.link"
            :to="card.link"
            class="text-sm font-medium text-emerald-600 hover:text-emerald-700 no-underline"
          >
            {{ locale === 'zh' ? '了解更多 →' : 'Learn more →' }}
          </NuxtLink>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();
const { locale } = useI18n();
</script>
```

- [ ] **Step 2: Verify product cards render**

Open `http://localhost:3000` — check: product cards show white cards with green border, hover shadow effect, "了解更多 →" links.

- [ ] **Step 3: Commit**

```bash
git add frontend/components/blocks/BlockProductCards.vue
git commit -m "feat: refine BlockProductCards with clean card style"
```

---

### Final Verification

- [ ] Open `http://localhost:3000` — verify full page renders with all elements
- [ ] Navigate to `/about`, `/products`, `/solutions`, `/contact` — verify all pages styled consistently
- [ ] Open `/news`, `/faq`, `/chat` — verify standalone pages inherit layout styling
- [ ] Toggle language switch — verify all pages switch zh/en correctly
- [ ] Check no Vue warnings in browser console
