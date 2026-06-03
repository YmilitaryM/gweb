<template>
  <section :style="sectionStyle" class="relative flex flex-col justify-center overflow-hidden">
    <div class="w-full max-w-7xl mx-auto px-6">
      <h2 v-if="content.title_zh" class="text-3xl md:text-4xl font-extrabold text-center mb-5 text-slate-900 tracking-tight">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <p v-if="content.subtitle_zh" class="text-lg text-slate-500 text-center max-w-2xl mx-auto mb-14">
        {{ locale === 'zh' ? content.subtitle_zh : content.subtitle_en }}
      </p>

      <div v-if="pending" class="text-center py-12 text-slate-400 text-sm">加载中...</div>

      <div v-else-if="!categories.length" class="text-center py-12 text-slate-400 text-sm">
        暂无产品分类，请在管理端添加
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <NuxtLink
          v-for="cat in categories.slice(0, displayCount)"
          :key="cat.id"
          :to="`/products?category=${cat.slug}`"
          class="group bg-white rounded-2xl border border-slate-100 p-6 transition-all duration-300 ease-out no-underline
                 hover:shadow-xl hover:shadow-slate-200/60 hover:border-brand-200 hover:-translate-y-1"
        >
          <div class="overflow-hidden rounded-xl mb-5 bg-slate-100 h-52 flex items-center justify-center">
            <div class="text-center">
              <div class="text-5xl mb-3">{{ catIcon(cat.slug) }}</div>
              <div class="text-xs text-slate-400 uppercase tracking-wider">{{ cat.product_count || 0 }} 款产品</div>
            </div>
          </div>
          <h3 class="text-xl font-bold text-slate-900 mb-3 group-hover:text-brand-700 transition-colors duration-300">
            {{ locale === 'zh' ? cat.name_zh : cat.name_en }}
          </h3>
          <span class="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 group-hover:text-brand-700 transition-colors duration-300">
            <span>{{ locale === 'zh' ? '了解更多' : 'Learn more' }}</span>
            <span class="transition-transform duration-300 group-hover:translate-x-1">&rarr;</span>
          </span>
        </NuxtLink>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{ config: Record<string, any>; content: Record<string, any> }>()
const { locale } = useI18n()
const apiBase = useRuntimeConfig().public.apiBase

const displayCount = computed(() => props.config?.count || props.content?.count || 6)

const sectionStyle = computed(() => {
  const bg = (props.config.bg || '').trim() || '#f1f5f9'
  const h = props.config.height || 864
  return { minHeight: `${h}px`, background: bg }
})

const { data, pending } = await useFetch<Array<{
  id: number; name_zh: string; name_en: string; slug: string; product_count: number
}>>(`${apiBase}/product-categories`)

const categories = computed(() => data.value || [])

function catIcon(slug: string): string {
  const icons: Record<string, string> = {
    'smart-hardware': '🖥️',
    software: '💻',
    services: '🔧',
  }
  return icons[slug] || '📦'
}
</script>
