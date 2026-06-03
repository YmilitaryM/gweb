<template>
  <section :style="sectionStyle" class="relative flex flex-col justify-center" :class="sectionHeight">
    <div v-if="config.gradient_top" class="absolute top-0 left-0 right-0 h-20 pointer-events-none" :style="{ background: `linear-gradient(to top, transparent, ${config.gradient_top})` }"></div>
    <div v-if="config.gradient_bottom" class="absolute bottom-0 left-0 right-0 h-24 pointer-events-none" :style="{ background: `linear-gradient(to bottom, transparent, ${config.gradient_bottom})` }"></div>
    <div class="w-full max-w-6xl mx-auto px-6">
      <h2 class="text-3xl font-extrabold text-center mb-10 text-slate-800 tracking-tight">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="article in items"
          :key="article.id"
          class="bg-white border border-blue-100 rounded-xl overflow-hidden transition-shadow hover:shadow-md"
        >
          <img
            v-if="content.show_image && article.cover_image_id"
            :src="mediaUrl(article.cover_image_id)"
            class="w-full h-48 object-cover"
          />
          <div class="p-5">
            <h3 class="text-lg font-medium text-slate-800 mb-2 line-clamp-2">
              {{ locale === 'zh' ? article.title_zh : article.title_en }}
            </h3>
            <p class="text-sm text-slate-500 leading-relaxed line-clamp-3 mb-4">
              {{ locale === 'zh' ? article.summary_zh : article.summary_en }}
            </p>
            <div class="flex justify-between items-center">
              <span v-if="content.show_date" class="text-xs text-slate-400">
                {{ new Date(article.published_at).toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US') }}
              </span>
              <NuxtLink
                :to="`/news/${article.id}`"
                class="text-sm font-medium text-brand-600 hover:text-brand-700 no-underline"
              >
                {{ locale === 'zh' ? '阅读更多' : 'Read more' }} →
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();
const { locale } = useI18n();
const mediaUrl = useMediaUrl();

const sectionHeight = computed(() => {
  const h = props.config.height || 864
  return `h-[${h}px]`
})
const sectionStyle = computed(() => ({
  background: props.config.bg || '#fafbfc',
}))

const { data } = await useNewsList(1, props.content.count || 3);
const items = computed(() => data.value?.items || []);
</script>
