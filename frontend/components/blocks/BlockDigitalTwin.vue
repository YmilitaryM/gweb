<template>
  <section class="py-16 px-4 bg-gray-900 text-white">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-4">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-10">
        <div class="lg:col-span-2 bg-gray-800 rounded-xl flex items-center justify-center min-h-[400px]">
          <div class="text-center text-gray-500">
            <UIcon name="i-heroicons-cube-transparent" class="w-16 h-16 mx-auto mb-4" />
            <p>{{ locale === 'zh' ? '数字孪生模型' : 'Digital Twin Model' }}</p>
          </div>
        </div>
        <div class="space-y-4">
          <UCard v-for="(stat, i) in content.stats" :key="i">
            <div class="text-2xl font-bold text-blue-500">{{ stat.value }}</div>
            <div class="text-sm text-gray-500 dark:text-gray-400">
              {{ locale === 'zh' ? stat.label_zh : stat.label_en }}
            </div>
          </UCard>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ config: Record<string, any>; content: Record<string, any> }>();
const { locale } = useI18n();
</script>
