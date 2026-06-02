<template>
  <div>
    <!-- Hero from CMS (inline, same as BlockHero but works in standalone page) -->
    <section
      v-if="heroSlide"
      class="relative min-h-[350px] md:min-h-[420px] lg:h-[500px] w-full overflow-hidden flex flex-col justify-center items-center text-white bg-slate-900"
    >
      <img
        v-if="heroSlide.image_url"
        :src="heroSlide.image_url"
        class="absolute inset-0 w-full h-full object-cover"
      />
      <div class="absolute inset-0 bg-black/20"></div>
      <div class="relative z-10 text-center px-6 max-w-4xl mx-auto">
        <h1 class="text-4xl md:text-5xl font-extrabold mb-4 tracking-tight">
          {{ locale === 'zh' ? heroSlide.title_zh : heroSlide.title_en }}
        </h1>
        <p v-if="heroSlide.subtitle_zh || heroSlide.subtitle_en"
          class="text-lg md:text-xl max-w-2xl mx-auto leading-relaxed text-white/85">
          {{ locale === 'zh' ? heroSlide.subtitle_zh : heroSlide.subtitle_en }}
        </p>
      </div>
    </section>

    <!-- Category filter -->
    <section class="py-12">
      <div class="container mx-auto px-6">
        <div class="flex flex-wrap justify-center gap-2 mb-10">
          <button
            v-for="cat in categories" :key="cat.key"
            @click="activeCategory = activeCategory === cat.key ? '' : cat.key"
            class="px-5 py-2.5 rounded-full text-sm font-semibold transition-all cursor-pointer border"
            :class="activeCategory === cat.key
              ? 'bg-brand-600 text-white border-brand-600'
              : 'bg-white text-slate-600 border-slate-200 hover:border-brand-300 hover:text-brand-600'"
          >
            {{ locale === 'zh' ? cat.label_zh : cat.label_en }}
          </button>
        </div>

        <!-- Case cards grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <NuxtLink
            v-for="c in cases" :key="c.id"
            :to="`/cases/${c.slug}`"
            class="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 border border-slate-100 hover:border-brand-100"
          >
            <div class="aspect-[16/10] bg-slate-100 overflow-hidden">
              <img
                v-if="c.cover_image_id"
                :src="`${apiBase}/../../media/id/${c.cover_image_id}`"
                :alt="locale === 'zh' ? c.name_zh : c.name_en"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-slate-400">暂无图片</div>
            </div>
            <div class="p-6">
              <span class="text-xs font-bold text-brand-600 uppercase tracking-wider">
                {{ categoryLabel(c.category) }}
              </span>
              <h3 class="text-lg font-bold text-slate-900 mt-2 mb-2 group-hover:text-brand-600 transition-colors">
                {{ locale === 'zh' ? c.name_zh : c.name_en }}
              </h3>
              <p class="text-sm text-slate-500 line-clamp-2">
                {{ locale === 'zh' ? c.summary_zh : c.summary_en }}
              </p>
            </div>
          </NuxtLink>
        </div>

        <!-- Empty state -->
        <div v-if="cases.length === 0 && !pending" class="text-center py-20 text-slate-400">
          {{ locale === 'zh' ? '暂无案例' : 'No cases yet' }}
        </div>

        <!-- Loading -->
        <div v-if="pending" class="text-center py-20 text-slate-400">
          Loading...
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const activeCategory = ref('')

// Fetch CMS page hero
const { data: casesPage } = await useAsyncData('cases-page-hero', () =>
  $fetch(`${apiBase}/pages/cases`).catch(() => null)
)
const heroSlide = computed(() => {
  const blocks = (casesPage.value as any)?.blocks || []
  const hero = blocks.find((b: any) => b.type === 'hero')
  if (!hero) return null
  const slide = hero.content?.slides?.[0] || {}
  return {
    ...slide,
    image_url: slide.image_id ? `${apiBase}/../../media/id/${slide.image_id}` : null,
  }
})

const categories = [
  { key: 'park', label_zh: '产业园区', label_en: 'Industrial Park' },
  { key: 'medical', label_zh: '医疗建筑', label_en: 'Medical' },
  { key: 'office', label_zh: '写字楼', label_en: 'Office' },
  { key: 'commercial', label_zh: '商业综合体', label_en: 'Commercial' },
]

const query = computed(() => ({
  page: 1,
  size: 12,
  category: activeCategory.value || undefined,
}))

const { data: result, pending } = await useAsyncData(
  'cases-list',
  () => $fetch(`${apiBase}/cases`, { query: query.value }),
  { watch: [activeCategory] }
)

const cases = computed(() => (result.value as any)?.items || [])

function categoryLabel(key: string): string {
  const cat = categories.find(c => c.key === key)
  return cat ? (locale.value === 'zh' ? cat.label_zh : cat.label_en) : key
}
</script>
