<template>
  <section class="py-16 px-4 bg-gray-900 text-white">
    <div class="max-w-5xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-10">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
        <div v-for="(item, i) in content.items" :key="i">
          <div class="text-4xl font-bold mb-2">{{ item.value }}</div>
          <div class="text-gray-400 text-sm">
            {{ locale === 'zh' ? item.label_zh : item.label_en }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();
const { locale } = useI18n();
</script>
