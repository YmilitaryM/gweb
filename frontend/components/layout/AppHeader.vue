<template>
  <header
    class="sticky top-0 z-50 flex items-center justify-between px-8 py-4"
    style="background: rgba(255,255,255,0.75); backdrop-filter: blur(18px); border-bottom: 1px solid rgba(5,150,105,0.05)"
  >
    <NuxtLink to="/" class="text-[17px] font-[650] tracking-tight text-emerald-900 no-underline">
      GWEB
    </NuxtLink>

    <nav class="flex gap-7">
      <template v-for="item in menu" :key="item.id">
        <!-- Items with children: dropdown menus -->
        <div
          v-if="item.children && item.children.length > 0"
          class="relative group"
        >
        <NuxtLink
          :to="menuLink(item)"
          class="text-sm transition-colors cursor-pointer"
          :class="$route.path === menuLink(item) ? 'text-emerald-600 font-[550]' : 'text-slate-500 hover:text-slate-700'"
        >
          {{ locale === 'zh' ? item.name_zh : item.name_en }}
          <span class="ml-0.5 text-[10px] opacity-60">&#9660;</span>
        </NuxtLink>

        <!-- Dropdown -->
        <div
          class="absolute left-0 top-full mt-2 min-w-[160px] rounded-lg bg-white shadow-lg border border-emerald-100 py-1.5 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-150 z-50"
        >
          <NuxtLink
            v-for="child in item.children"
            :key="child.id"
            :to="menuLink(child)"
            class="block px-4 py-2 text-sm transition-colors whitespace-nowrap"
            :class="$route.path === menuLink(child) ? 'text-emerald-600 font-[550] bg-emerald-50' : 'text-slate-500 hover:text-emerald-600 hover:bg-emerald-50/50'"
          >
            {{ locale === 'zh' ? child.name_zh : child.name_en }}
          </NuxtLink>
        </div>
        </div>
      </template>

      <!-- Items without children: direct links -->
      <template v-for="item in menu" :key="'link-' + item.id">
        <NuxtLink
          v-if="!item.children || item.children.length === 0"
          :to="menuLink(item)"
          class="text-sm transition-colors"
          :class="$route.path === menuLink(item) ? 'text-emerald-600 font-[550]' : 'text-slate-500 hover:text-slate-700'"
        >
          {{ locale === 'zh' ? item.name_zh : item.name_en }}
        </NuxtLink>
      </template>
    </nav>

    <button
      class="relative w-11 h-6 rounded-full cursor-pointer border-none outline-none"
      style="background: linear-gradient(135deg, #d1fae5, #a7f3d0)"
      @click="toggleLang"
      :aria-label="locale === 'zh' ? 'Switch to English' : '切换到中文'"
    >
      <span
        class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm flex items-center justify-center text-[10px] font-semibold transition-transform duration-200"
        :class="locale === 'zh' ? 'left-0.5 text-emerald-600' : 'translate-x-[22px] text-slate-400'"
      >
        {{ locale === 'zh' ? '中' : 'EN' }}
      </span>
    </button>
  </header>
</template>

<script setup lang="ts">
interface MenuItem {
  id: number;
  name_zh: string;
  name_en: string;
  link: string;
  page_slug: string | null;
  children: MenuItem[];
}

function menuLink(item: MenuItem): string {
  if (item.page_slug) {
    if (item.page_slug === 'home') return '/';
    return '/' + item.page_slug;
  }
  return item.link;
}

const { locale } = useI18n();
const config = useRuntimeConfig();
const { data: menu } = await useFetch<MenuItem[]>(`${config.public.apiBase}/menus?location=header`, { default: () => [] });

function toggleLang() {
  locale.value = locale.value === 'zh' ? 'en' : 'zh';
}
</script>
