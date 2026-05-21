<template>
  <component
    v-if="component"
    :is="component"
    :config="block.config"
    :content="block.content"
  />
</template>

<script setup lang="ts">
interface Block {
  id: number;
  type: string;
  order: number;
  config: Record<string, any>;
  content: Record<string, any>;
}

const props = defineProps<{ block: Block }>();

const componentMap: Record<string, any> = {
  hero: defineAsyncComponent(() => import('./BlockHero.vue')),
  richtext: defineAsyncComponent(() => import('./BlockRichtext.vue')),
  news_list: defineAsyncComponent(() => import('./BlockNewsList.vue')),
  faq: defineAsyncComponent(() => import('./BlockFaq.vue')),
  contact_form: defineAsyncComponent(() => import('./BlockContactForm.vue')),
  product_cards: defineAsyncComponent(() => import('./BlockProductCards.vue')),
  stats_counter: defineAsyncComponent(() => import('./BlockStatsCounter.vue')),
  video_banner: defineAsyncComponent(() => import('./BlockVideoBanner.vue')),
  image_gallery: defineAsyncComponent(() => import('./BlockImageGallery.vue')),
  logo_cloud: defineAsyncComponent(() => import('./BlockLogoCloud.vue')),
  cta_banner: defineAsyncComponent(() => import('./BlockCtaBanner.vue')),
  digital_twin: defineAsyncComponent(() => import('./BlockDigitalTwin.vue')),
  live_dashboard: defineAsyncComponent(() => import('./BlockLiveDashboard.vue')),
  tech_icon_grid: defineAsyncComponent(() => import('./BlockTechIconGrid.vue')),
  solution_cards: defineAsyncComponent(() => import('./BlockSolutionCards.vue')),
};

const component = computed(() => componentMap[props.block.type] || null);
</script>
