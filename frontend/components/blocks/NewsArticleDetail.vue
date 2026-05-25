<template>
  <article v-if="article" class="py-16 px-4 max-w-3xl mx-auto">
    <img
      v-if="article.cover_image_id"
      :src="`${apiBase}/../../media/${article.cover_image_id}`"
      class="w-full max-h-96 object-cover rounded-lg mb-8"
    />
    <h1 class="text-3xl font-bold mb-4">
      {{ locale === 'zh' ? article.title_zh : article.title_en }}
    </h1>
    <p class="text-gray-500 mb-8">
      {{ new Date(article.published_at).toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US') }}
    </p>
    <div
      class="prose max-w-none"
      v-html="locale === 'zh' ? article.content_zh : article.content_en"
    />
    <div class="mt-10">
      <UButton to="/news" variant="outline">
        {{ locale === 'zh' ? '返回新闻列表' : 'Back to News' }}
      </UButton>
    </div>
  </article>

  <div v-else-if="error" class="py-20 text-center text-gray-500">
    {{ locale === 'zh' ? '文章未找到' : 'Article not found' }}
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ articleId: string }>();
const { locale } = useI18n();
const apiBase = useRuntimeConfig().public.apiBase;

const { article, error } = await useNewsArticle(Number(props.articleId));
</script>
