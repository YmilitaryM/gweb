<template>
  <article v-if="article" class="py-16 px-4 max-w-3xl mx-auto">
    <img
      v-if="article.cover_image_id"
      :src="`${apiBase}/../../media/id/${article.cover_image_id}`"
      class="w-full max-h-96 object-cover rounded-2xl mb-8 shadow-sm"
    />
    <h1 class="text-3xl md:text-4xl font-extrabold mb-4 text-slate-900">
      {{ locale === 'zh' ? article.title_zh : article.title_en }}
    </h1>
    <p class="text-slate-400 text-sm mb-8">
      {{ new Date(article.published_at).toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US') }}
    </p>
    <div
      class="prose prose-slate max-w-none"
      v-html="locale === 'zh' ? article.content_zh : article.content_en"
    />
    <div class="mt-12 pt-8 border-t border-slate-100">
      <NuxtLink
        to="/news"
        class="inline-flex items-center px-5 py-2.5 rounded-full text-sm font-semibold border border-slate-200 text-slate-600 hover:text-brand-600 hover:border-brand-300 transition-all"
      >
        ← {{ locale === 'zh' ? '返回新闻列表' : 'Back to News' }}
      </NuxtLink>
    </div>
  </article>

  <div v-else-if="error" class="py-20 text-center text-slate-400">
    {{ locale === 'zh' ? '文章未找到' : 'Article not found' }}
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ articleId: string }>();
const { locale } = useI18n();
const apiBase = useRuntimeConfig().public.apiBase;

const { article, error } = await useNewsArticle(Number(props.articleId));
</script>
