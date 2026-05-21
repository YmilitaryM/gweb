<template>
  <section class="py-16 px-4">
    <div class="max-w-4xl mx-auto prose dark:prose-invert max-w-none" v-html="html" />
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();
const { locale } = useI18n();

const html = computed(() =>
  locale.value === 'zh'
    ? props.content.html_content_zh || ''
    : props.content.html_content_en || ''
);
</script>
