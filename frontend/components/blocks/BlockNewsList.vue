<template>
  <section :style="sectionStyle" class="relative flex flex-col justify-center overflow-hidden">
    <div class="w-full max-w-6xl mx-auto px-6">
      <h2 class="text-3xl font-extrabold text-center mb-10 text-slate-800 tracking-tight">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <!-- Loading -->
      <div v-if="pending" class="text-center text-slate-400 text-sm">加载中...</div>

      <!-- Empty -->
      <div v-else-if="!items.length" class="text-center text-slate-400 text-sm">
        暂无新闻，请在管理端 <a href="/admin/news" class="text-brand-600">新闻管理</a> 中添加
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center text-red-400 text-sm">加载失败，请检查后端服务</div>

      <!-- News grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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

const sectionStyle = computed(() => {
  const bg = (props.config.bg || '').trim() || '#fafbfc'
  const h = props.config.height || 864
  return { minHeight: `${h}px`, background: bg }
})

const count = computed(() => props.config?.count || props.content?.count || 3);

const { data, pending, error } = await useNewsList(1, count);
const items = computed(() => data.value?.items || []);
</script>
