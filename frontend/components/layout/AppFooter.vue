<template>
  <footer class="bg-[#f5f7fa] border-t border-slate-200/60 pt-12 pb-8">
    <div class="container mx-auto px-6">
      <!-- Main grid -->
      <div class="grid grid-cols-1 md:grid-cols-12 gap-8 lg:gap-12 mb-10">
        <!-- Col 1: Logo + Description + Hotline -->
        <div class="md:col-span-12 lg:col-span-5 flex flex-col gap-5">
          <div class="space-y-3">
            <NuxtLink to="/" class="inline-flex items-center group">
              <img
                v-if="logoUrl"
                :src="logoUrl"
                alt="金捷利"
                class="h-10 md:h-11 w-auto object-contain"
              />
            </NuxtLink>
            <p class="text-slate-500 text-[13px] leading-relaxed max-w-sm">
              {{ settings?.company_description_zh || '' }}
            </p>
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-[10px] text-slate-400 font-semibold tracking-wider uppercase">
              7x24小时全国智能运维热线
            </span>
            <a :href="`tel:${settings?.hotline || ''}`"
              class="text-lg font-black tracking-tight text-slate-800 hover:text-brand-600 transition-colors">
              {{ settings?.hotline || '' }}
            </a>
          </div>
        </div>

        <!-- Cols 2-4: Menu groups -->
        <div class="md:col-span-12 lg:col-span-7 flex flex-col sm:flex-row sm:justify-end gap-8 sm:gap-x-16 lg:gap-x-20">
          <div v-for="group in footerGroups" :key="group.name" class="flex flex-col min-w-[120px] sm:text-right">
            <h4 class="text-slate-900 font-extrabold text-[14px] mb-4 tracking-wide">
              {{ locale === 'zh' ? group.name_zh : group.name_en }}
            </h4>
            <ul class="space-y-2.5 text-[13px] text-slate-500 font-medium">
              <li v-for="item in group.items" :key="item.id">
                <NuxtLink :to="menuLink(item)"
                  class="hover:text-brand-600 transition-colors duration-200 block">
                  {{ locale === 'zh' ? item.name_zh : item.name_en }}
                </NuxtLink>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="pt-6 border-t border-slate-200/70 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 text-xs text-slate-400">
        <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
          <span class="font-semibold text-slate-550">© 2026 {{ settings?.company_name_zh || '' }}</span>
          <span class="hidden sm:inline text-slate-300">|</span>
          <span class="text-slate-400/80 tracking-wider uppercase text-[10px]">All Rights Reserved.</span>
        </div>
        <div class="flex flex-wrap items-center gap-x-5 gap-y-2">
          <NuxtLink to="/privacy" class="hover:text-brand-600 hover:underline transition-colors">隐私政策</NuxtLink>
          <span class="inline-block w-1 h-1 rounded-full bg-slate-300"></span>
          <NuxtLink to="/terms" class="hover:text-brand-600 hover:underline transition-colors">法律声明</NuxtLink>
          <span v-if="settings?.icp_beian" class="inline-block w-1 h-1 rounded-full bg-slate-300"></span>
          <a v-if="settings?.icp_beian" href="https://beian.miit.gov.cn/" target="_blank" rel="noopener"
            class="hover:text-brand-600 hover:underline transition-colors">{{ settings.icp_beian }}</a>
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
const config = useRuntimeConfig()

const { data: footerMenu } = await useFetch<MenuItem[]>(
  `${config.public.apiBase}/menus?location=footer`,
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

const footerGroups = computed(() => {
  const raw = footerMenu.value || []
  return raw.map(g => ({
    name_zh: g.name_zh,
    name_en: g.name_en,
    items: g.children || [],
  }))
})

function menuLink(item: MenuItem): string {
  if (item.page_slug) return item.page_slug === 'home' ? '/' : '/' + item.page_slug
  return item.link || '#'
}
</script>
