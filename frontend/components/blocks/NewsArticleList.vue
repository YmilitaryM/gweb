<template>
  <div class="py-16 px-4 max-w-6xl mx-auto">
    <h2
      v-if="sectionTitle"
      class="text-3xl font-extrabold mb-10 text-center text-slate-900"
    >
      {{ sectionTitle }}
    </h2>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
      <div
        v-for="article in items"
        :key="article.id"
        class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden cursor-pointer hover:shadow-lg hover:border-brand-100 transition-all duration-300 group"
        @click="navigateTo(`/news/${article.id}`)"
      >
        <img
          v-if="showImage && article.cover_image_id"
          :src="`${apiBase}/../../media/id/${article.cover_image_id}`"
          class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-500"
        />
        <div class="p-6">
          <div class="flex items-center gap-2 mb-3">
            <span v-if="showDate" class="text-xs text-slate-400">
              {{ new Date(article.published_at).toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US') }}
            </span>
          </div>
          <h3 class="text-lg font-bold text-slate-900 mb-2 group-hover:text-brand-600 transition-colors">
            {{ locale === 'zh' ? article.title_zh : article.title_en }}
          </h3>
          <p class="text-sm text-slate-500 line-clamp-3">
            {{ locale === 'zh' ? article.summary_zh : article.summary_en }}
          </p>
        </div>
      </div>
    </div>

    <div v-if="!items.length" class="text-center text-slate-400 py-20">
      {{ locale === 'zh' ? '暂无新闻' : 'No news yet' }}
    </div>

    <div v-if="totalPages > 1" class="flex justify-center gap-2">
      <button
        v-for="p in totalPages"
        :key="p"
        @click="goToPage(p)"
        class="w-10 h-10 rounded-lg text-sm font-semibold transition-all cursor-pointer border"
        :class="p === currentPage
          ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
          : 'bg-white text-slate-600 border-slate-200 hover:border-brand-300 hover:text-brand-600'"
      >
        {{ p }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  config: Record<string, any>;
}>();

const { locale } = useI18n();
const apiBase = useRuntimeConfig().public.apiBase;

const count = computed(() => props.config.count || 6);
const showImage = computed(() => props.config.show_image !== false);
const showDate = computed(() => props.config.show_date !== false);

const sectionTitle = computed(() => {
  if (locale.value === 'zh') return props.config.title_zh || '';
  return props.config.title_en || '';
});

const categoryFilter = computed(() => props.config.category_filter || undefined);

const currentPage = ref(1);

const { data } = useNewsList(currentPage, count, categoryFilter);

const items = computed(() => data.value?.items || []);
const total = computed(() => data.value?.total || 0);
const totalPages = computed(() => Math.ceil(total.value / count.value));

function goToPage(p: number) {
  currentPage.value = p;
}
</script>
