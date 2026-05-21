<template>
  <div class="py-16 px-4 max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-10 text-center">
      {{ locale === 'zh' ? '新闻中心' : 'News' }}
    </h1>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
      <UCard v-for="article in items" :key="article.id" class="cursor-pointer" @click="navigateTo(`/news/${article.id}`)">
        <img
          v-if="article.cover_image_id"
          :src="`${apiBase}/../media/${article.cover_image_id}`"
          class="w-full h-48 object-cover rounded-t"
        />
        <template #header>
          <h3 class="text-lg font-semibold">
            {{ locale === 'zh' ? article.title_zh : article.title_en }}
          </h3>
        </template>
        <p class="text-gray-600 dark:text-gray-400 line-clamp-3">
          {{ locale === 'zh' ? article.summary_zh : article.summary_en }}
        </p>
        <template #footer>
          <span class="text-sm text-gray-500">
            {{ new Date(article.published_at).toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US') }}
          </span>
        </template>
      </UCard>
    </div>

    <div v-if="!items.length" class="text-center text-gray-500 py-20">
      {{ locale === 'zh' ? '暂无新闻' : 'No news yet' }}
    </div>

    <div v-if="total > size" class="flex justify-center gap-2">
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
const { locale } = useI18n();
const apiBase = useRuntimeConfig().public.apiBase;
const route = useRoute();
const currentPage = ref(Number(route.query.page) || 1);
const size = 9;

const { data, refresh } = await useNewsList(currentPage.value, size);
const items = computed(() => data.value?.items || []);
const total = computed(() => data.value?.total || 0);
const totalPages = computed(() => Math.ceil(total.value / size));

const goToPage = (p: number) => {
  currentPage.value = p;
  refresh();
};
</script>
