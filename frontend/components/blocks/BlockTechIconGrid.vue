<template>
  <section class="py-16 px-4">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-10">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <div v-for="(item, i) in content.items" :key="i" class="text-center p-6 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition">
          <UIcon :name="item.icon || 'i-heroicons-cpu-chip'" class="w-10 h-10 mx-auto mb-3 text-blue-500" />
          <h3 class="font-semibold mb-1">{{ locale === 'zh' ? item.label_zh : item.label_en }}</h3>
          <p class="text-sm text-gray-500">{{ locale === 'zh' ? item.desc_zh : item.desc_en }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ config: Record<string, any>; content: Record<string, any> }>();
const { locale } = useI18n();
</script>
