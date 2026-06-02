<template>
  <div v-if="c">
    <!-- Hero -->
    <section class="relative min-h-[40vh] flex items-center justify-center bg-slate-900 overflow-hidden">
      <img v-if="c.cover_image_id" :src="`${apiBase}/../../media/id/${c.cover_image_id}`"
        class="absolute inset-0 w-full h-full object-cover opacity-30" alt="" />
      <div class="absolute inset-0 bg-gradient-to-t from-slate-950/60 to-slate-950/20" />
      <div class="relative z-10 text-center text-white px-6 max-w-4xl">
        <span class="text-sm font-bold text-brand-300 uppercase tracking-wider">{{ categoryLabel(c.category) }}</span>
        <h1 class="text-3xl md:text-4xl font-extrabold mt-3 mb-4">
          {{ locale === 'zh' ? c.name_zh : c.name_en }}
        </h1>
        <p class="text-lg text-white/70 max-w-2xl mx-auto">
          {{ locale === 'zh' ? c.summary_zh : c.summary_en }}
        </p>
      </div>
    </section>

    <!-- Stats -->
    <section v-if="c.stats?.length" class="py-12 bg-white border-b border-slate-100">
      <div class="container mx-auto px-6">
        <div class="flex flex-wrap justify-center gap-8 md:gap-16">
          <div v-for="s in c.stats" :key="s.label" class="text-center">
            <div class="text-3xl md:text-4xl font-extrabold text-brand-600">{{ s.value }}</div>
            <div class="text-sm text-slate-500 mt-1">{{ s.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Content -->
    <section class="py-16">
      <div class="container mx-auto px-6 max-w-3xl">
        <div class="prose prose-slate max-w-none" v-html="locale === 'zh' ? c.content_zh : c.content_en" />
      </div>
    </section>
  </div>

  <!-- Not found -->
  <div v-else class="text-center py-32 text-slate-400">
    <p class="text-xl mb-4">{{ locale === 'zh' ? '案例未找到' : 'Case not found' }}</p>
    <NuxtLink to="/cases" class="text-brand-600 hover:underline">
      {{ locale === 'zh' ? '返回案例列表' : 'Back to cases' }}
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const route = useRoute()

const { data: c } = await useAsyncData('case-detail', () =>
  $fetch(`${apiBase}/cases/${route.params.slug}`).catch(() => null)
)

const categories = [
  { key: 'park', label_zh: '产业园区', label_en: 'Industrial Park' },
  { key: 'medical', label_zh: '医疗建筑', label_en: 'Medical' },
  { key: 'office', label_zh: '写字楼', label_en: 'Office' },
  { key: 'commercial', label_zh: '商业综合体', label_en: 'Commercial' },
]

function categoryLabel(key: string): string {
  const cat = categories.find(c => c.key === key)
  return cat ? (locale.value === 'zh' ? cat.label_zh : cat.label_en) : key
}
</script>
