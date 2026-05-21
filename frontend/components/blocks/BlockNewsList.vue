<template>
  <section class="py-16 px-4 bg-gray-50 dark:bg-gray-900">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-10">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <UCard v-for="article in items" :key="article.id">
          <img
            v-if="content.show_image && article.cover_image_id"
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
            <div class="flex justify-between items-center">
              <span v-if="content.show_date" class="text-sm text-gray-500">
                {{ new Date(article.published_at).toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US') }}
              </span>
              <UButton :to="`/news/${article.id}`" variant="link" size="sm">
                {{ locale === 'zh' ? '阅读更多' : 'Read more' }}
              </UButton>
            </div>
          </template>
        </UCard>
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
const apiBase = useRuntimeConfig().public.apiBase;

const { data } = await useNewsList(1, props.content.count || 3);
const items = computed(() => data.value?.items || []);
</script>
