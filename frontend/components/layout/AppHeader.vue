<template>
  <header
    class="fixed top-0 left-0 right-0 z-50 transition-transform duration-500 ease-in-out border-b border-white/20"
    style="background: rgba(255,255,255,0.5); backdrop-filter: blur(20px) saturate(180%); -webkit-backdrop-filter: blur(20px) saturate(180%);"
    :class="hidden ? '-translate-y-full' : 'translate-y-0'"
  >
    <div class="container mx-auto px-6 flex items-center justify-between h-16">
      <!-- Logo -->
      <NuxtLink :to="localePath('/')" class="flex items-center group">
        <img
          v-if="logoUrl"
          :src="logoUrl"
          alt="金捷利"
          class="h-10 md:h-11 w-auto object-contain transition-transform duration-300 group-hover:scale-[1.02]"
        />
        <span v-else class="text-lg font-bold text-brand-600 tracking-tight">
          {{ settings?.company_name_zh || '金捷利' }}
        </span>
      </NuxtLink>

      <!-- Desktop Nav -->
      <nav class="hidden lg:flex items-center gap-1">
        <NuxtLink
          v-for="item in headerMenu"
          :key="item.id"
          :to="menuLink(item)"
          class="nav-underline text-sm font-semibold px-3 py-2.5 text-slate-800 hover:text-brand-600 transition-colors"
          :class="{ active: $route.path === menuLink(item) }"
        >
          {{ locale === 'zh' ? item.name_zh : item.name_en }}
        </NuxtLink>
      </nav>

      <!-- Right side: Language Toggle + Mobile Hamburger -->
      <div class="flex items-center gap-3">
        <button
          class="relative w-11 h-6 rounded-full cursor-pointer border-none outline-none bg-slate-200 transition-colors"
          :class="{ 'bg-brand-100': locale === 'en' }"
          @click="toggleLang"
          :aria-label="locale === 'zh' ? 'Switch to English' : '切换到中文'"
        >
          <span
            class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm flex items-center justify-center text-[10px] font-semibold transition-transform duration-200"
            :class="locale === 'zh' ? 'left-0.5 text-brand-600' : 'translate-x-[22px] text-slate-400'"
          >
            {{ locale === 'zh' ? '中' : 'EN' }}
          </span>
        </button>

        <!-- Mobile Hamburger -->
        <button class="lg:hidden text-slate-800 p-1" @click="mobileOpen = !mobileOpen">
          <span v-if="mobileOpen" class="text-xl">✕</span>
          <span v-else class="text-xl">☰</span>
        </button>
      </div>
    </div>

    <!-- Mobile Menu -->
    <div
      v-if="mobileOpen"
      style="background: rgba(255,255,255,0.95); backdrop-filter: blur(20px) saturate(180%); -webkit-backdrop-filter: blur(20px) saturate(180%);"
      class="lg:hidden absolute top-full left-0 right-0 border-b border-white/20 p-6 flex flex-col gap-3 shadow-xl"
    >
      <NuxtLink
        v-for="item in headerMenu"
        :key="'m-' + item.id"
        :to="menuLink(item)"
        class="text-lg text-left py-1 text-slate-800 hover:text-brand-600 transition-colors font-semibold"
        :class="{ 'text-brand-600': $route.path === menuLink(item) }"
        @click="mobileOpen = false"
      >
        {{ locale === 'zh' ? item.name_zh : item.name_en }}
      </NuxtLink>
    </div>
  </header>
</template>

<script setup lang="ts">
interface MenuItem {
  id: number
  name_zh: string
  name_en: string
  link: string
  page_slug: string | null
  children: MenuItem[]
}

const { locale } = useI18n()
const localePath = useLocalePath()
const config = useRuntimeConfig()

const { data: headerMenu } = await useFetch<MenuItem[]>(
  `${config.public.apiBase}/menus?location=header`,
  { default: () => [] }
)
const { data: settings } = await useFetch<Record<string, string>>(
  `${config.public.apiBase}/settings/public`,
  { default: () => ({}) }
)

const logoUrl = computed(() => {
  const logoId = settings.value?.logo_id
  return logoId ? `${config.public.apiBase}/../../media/id/${logoId}` : null
})

function menuLink(item: MenuItem): string {
  let path = item.link || '#'
  if (item.page_slug) {
    path = item.page_slug === 'home' ? '/' : '/' + item.page_slug
  }
  return localePath(path)
}

// Scroll hide/show animation
const hidden = ref(false)
let lastScrollY = 0

function onScroll() {
  const currentY = window.scrollY
  hidden.value = currentY > lastScrollY && currentY > 80
  lastScrollY = currentY
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

// Mobile menu
const mobileOpen = ref(false)

const switchLocalePath = useSwitchLocalePath()
const route = useRoute()

function toggleLang() {
  const newLocale = locale.value === 'zh' ? 'en' : 'zh'
  navigateTo(switchLocalePath(newLocale) || route.fullPath)
}
</script>
