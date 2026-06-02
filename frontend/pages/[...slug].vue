<template>
  <div>
    <template v-if="!page">
      <p class="text-center py-20 text-gray-500">Loading...</p>
    </template>

    <!-- type=news -->
    <template v-else-if="page.type === 'news'">
      <template v-if="!detailParam">
        <BlockRenderer v-for="block in nonNewsListBlocks" :key="block.id" :block="block" />
        <NewsArticleList :config="newsListConfig" />
      </template>
      <template v-else>
        <NewsArticleDetail :articleId="detailParam" />
      </template>
    </template>

    <!-- type=products -->
    <template v-else-if="page.type === 'products'">
      <template v-if="!detailParam">
        <BlockRenderer v-for="block in page.blocks" :key="block.id" :block="block" />
        <ProductCatalog :config="{}" />
      </template>
      <template v-else>
        <ProductDetail :productSlug="detailParam" />
      </template>
    </template>

    <!-- type=faq -->
    <template v-else-if="page.type === 'faq'">
      <BlockRenderer v-for="block in page.blocks" :key="block.id" :block="block" />
      <FaqPanel :config="{}" />
    </template>

    <!-- type=page (home, about, solutions, cooperation, contact) and type=content (cases, privacy, terms): blocks only -->
    <template v-else>
      <BlockRenderer v-for="block in page.blocks" :key="block.id" :block="block" />
    </template>
  </div>
</template>

<script setup lang="ts">
import BlockRenderer from '~/components/blocks/BlockRenderer.vue';
import NewsArticleList from '~/components/blocks/NewsArticleList.vue';
import NewsArticleDetail from '~/components/blocks/NewsArticleDetail.vue';
import ProductCatalog from '~/components/blocks/ProductCatalog.vue';
import ProductDetail from '~/components/blocks/ProductDetail.vue';
import FaqPanel from '~/components/blocks/FaqPanel.vue';

const route = useRoute();
const slug = route.params.slug as string[];
const pageSlug = slug[0];
const detailParam = slug[1] || null;

const { page } = await usePage(pageSlug);

if (!page) {
  throw createError({ statusCode: 404, message: 'Page not found' });
}

const newsListBlock = computed(() =>
  (page.value as any)?.blocks?.find((b: any) => b.type === 'news_list')
);

const nonNewsListBlocks = computed(() =>
  ((page.value as any)?.blocks || []).filter((b: any) => b.type !== 'news_list')
);

const newsListConfig = computed(() => newsListBlock.value?.content || {
  title_zh: '新闻中心',
  title_en: 'News',
  count: 9,
  show_date: true,
  show_image: true,
});
</script>
