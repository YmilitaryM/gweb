<template>
  <footer
    :class="isHomePage
      ? 'bg-slate-900 text-slate-300 border-slate-800'
      : 'bg-[#f5f7fa] border-slate-200/60'"
    class="border-t pt-12 pb-8"
  >
    <div class="container mx-auto px-6">
      <div class="grid grid-cols-1 md:grid-cols-12 gap-8 lg:gap-12 mb-10">
        <!-- Col 1: Company info from CMS footer page -->
        <div class="md:col-span-12 lg:col-span-5 flex flex-col gap-5">
          <div class="space-y-3">
            <NuxtLink :to="localePath('/')" class="inline-flex items-center group">
              <img v-if="logoUrl" :src="logoUrl" alt="金捷利" class="h-10 md:h-11 w-auto object-contain" />
            </NuxtLink>
            <div :class="isHomePage ? 'text-slate-400' : 'text-slate-500'" class="text-[13px] leading-relaxed max-w-sm" v-html="footerIntro" />
          </div>
          <div class="flex flex-col gap-1" v-if="settings?.hotline">
            <span :class="isHomePage ? 'text-slate-500' : 'text-slate-400'" class="text-[10px] font-semibold tracking-wider uppercase">
              {{ settings?.footer_hotline_label || '7x24小时全国智能运维热线' }}
            </span>
            <a :href="`tel:${settings.hotline}`" :class="isHomePage ? 'text-white hover:text-brand-400' : 'text-slate-800 hover:text-brand-600'" class="text-lg font-black tracking-tight transition-colors">
              {{ settings.hotline }}
            </a>
          </div>
        </div>

        <!-- Cols 2-4: Link groups from Menu API -->
        <div class="md:col-span-12 lg:col-span-7 flex flex-col sm:flex-row sm:justify-end gap-8 sm:gap-x-16 lg:gap-x-20">
          <div v-for="group in footerGroups" :key="group.name" class="flex flex-col min-w-[120px] sm:text-right">
            <h4 :class="isHomePage ? 'text-white' : 'text-slate-900'" class="font-extrabold text-[14px] mb-4 tracking-wide">
              {{ locale === 'zh' ? group.name_zh : group.name_en }}
            </h4>
            <ul :class="isHomePage ? 'text-slate-400' : 'text-slate-500'" class="space-y-2.5 text-[13px] font-medium">
              <li v-for="item in group.items" :key="item.id">
                <NuxtLink :to="menuLink(item)" :class="isHomePage ? 'hover:text-brand-400' : 'hover:text-brand-600'" class="transition-colors duration-200 block">
                  {{ locale === 'zh' ? item.name_zh : item.name_en }}
                </NuxtLink>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Bottom bar from CMS footer page -->
      <div :class="[isHomePage ? 'border-slate-800 text-slate-500' : 'border-slate-200/70 text-slate-400', 'pt-6 border-t flex flex-col md:flex-row justify-between items-start md:items-center gap-4 text-xs']">
        <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
          <span :class="isHomePage ? 'text-slate-300' : 'text-slate-550'" class="font-semibold">
            © {{ new Date().getFullYear() }} {{ settings?.company_name_zh || '' }}
          </span>
          <span :class="isHomePage ? 'text-slate-700' : 'text-slate-300'" class="hidden sm:inline">|</span>
          <span :class="isHomePage ? 'text-slate-500' : 'text-slate-400/80'" class="tracking-wider uppercase text-[10px]">All Rights Reserved.</span>
        </div>
        <div class="flex flex-wrap items-center gap-x-5 gap-y-2">
          <NuxtLink :to="localePath('/privacy')" :class="isHomePage ? 'hover:text-brand-400' : 'hover:text-brand-600'" class="hover:underline transition-colors">
            {{ settings?.footer_privacy_text || '隐私政策' }}
          </NuxtLink>
          <span :class="isHomePage ? 'bg-slate-700' : 'bg-slate-300'" class="inline-block w-1 h-1 rounded-full"></span>
          <NuxtLink :to="localePath('/terms')" :class="isHomePage ? 'hover:text-brand-400' : 'hover:text-brand-600'" class="hover:underline transition-colors">
            {{ settings?.footer_terms_text || '法律声明' }}
          </NuxtLink>
          <span v-if="settings?.icp_beian" :class="isHomePage ? 'bg-slate-700' : 'bg-slate-300'" class="inline-block w-1 h-1 rounded-full"></span>
          <a v-if="settings?.icp_beian" href="https://beian.miit.gov.cn/" target="_blank" rel="noopener"
            :class="isHomePage ? 'hover:text-brand-400' : 'hover:text-brand-600'" class="hover:underline transition-colors">{{ settings.icp_beian }}</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
interface MenuItem {
  id: number; name_zh: string; name_en: string; link: string;
  page_slug: string | null; children: MenuItem[]
}

const { locale } = useI18n()
const localePath = useLocalePath()
const config = useRuntimeConfig()
const route = useRoute()

const isHomePage = computed(() => route.path === '/' || route.path === '/en')

// Fetch CMS footer page
const { data: footerPage } = await useFetch<any>(
  `${config.public.apiBase}/pages/footer`,
  { default: () => null }
)

const footerIntro = computed(() => {
  const blocks = footerPage.value?.blocks || []
  const intro = blocks.find((b: any) => b.type === 'richtext')
  if (!intro) return ''
  return locale.value === 'zh'
    ? (intro.content?.html_content_zh || intro.content?.text_zh || '')
    : (intro.content?.html_content_en || intro.content?.text_en || '')
})

// Footer menu links
const { data: footerMenu } = await useFetch<MenuItem[]>(
  `${config.public.apiBase}/menus?location=footer`,
  { default: () => [] }
)

// Settings
const { data: settings } = await useFetch<Record<string, string>>(
  `${config.public.apiBase}/settings/public`,
  { default: () => ({}) }
)

const logoUrl = computed(() => {
  const logoId = settings.value?.logo_id
  return logoId ? `${config.public.apiBase}/../../media/id/${logoId}` : null
})

const footerGroups = computed(() => {
  const raw = footerMenu.value || []
  return raw.map(g => ({
    name_zh: g.name_zh,
    name_en: g.name_en,
    items: g.children || [],
  }))
})

function menuLink(item: MenuItem): string {
  let path = item.link || '#'
  if (item.page_slug) path = item.page_slug === 'home' ? '/' : '/' + item.page_slug
  return localePath(path)
}
</script>
