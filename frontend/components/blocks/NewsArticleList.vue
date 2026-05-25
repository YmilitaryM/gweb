<template>
  <div class="py-16 px-4 max-w-6xl mx-auto">
    <h1
      v-if="sectionTitle"
      class="text-3xl font-bold mb-10 text-center"
    >
      {{ sectionTitle }}
    </h1>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
      <UCard
        v-for="article in items"
        :key="article.id"
        class="cursor-pointer"
        @click="navigateTo(`/news/${article.id}`)"
      >
        <img
          v-if="showImage && article.cover_image_id"
          :src="`${apiBase}/../../media/${article.cover_image_id}`"
          class="w-full h-48 object-cover rounded-t"
        />
        <template #header>
          <h3 class="text-lg font-semibold">
            {{ locale === 'zh' ? article.title_zh : article.title_en }}
          </h3>
        </template>
        <p class="text-gray-600 line-clamp-3">
          {{ locale === 'zh' ? article.summary_zh : article.summary_en }}
        </p>
        <template #footer>
          <span v-if="showDate" class="text-sm text-gray-500">
            {{ new Date(article.published_at).toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US') }}
          </span>
        </template>
      </UCard>
    </div>

    <div v-if="!items.length" class="text-center text-gray-500 py-20">
      {{ locale === 'zh' ? '暂无新闻' : 'No news yet' }}
    </div>

    <div v-if="totalPages > 1" class="flex justify-center gap-2">
      <UButton
        v-for="p in totalPages"
        :key="p"
        :variant="p === currentPage ? 'solid' : 'outline'"
        @click="goToPage(p)"
      >
        {{ p }}
      </UButton>
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
