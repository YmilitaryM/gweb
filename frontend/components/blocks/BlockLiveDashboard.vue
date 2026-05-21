<template>
  <section class="py-16 px-4 bg-gray-50 dark:bg-gray-900">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-10">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <UCard v-for="(metric, i) in content.metrics" :key="i">
          <div class="text-sm text-gray-500 mb-1">
            {{ locale === 'zh' ? metric.label_zh : metric.label_en }}
          </div>
          <div class="text-2xl font-bold">
            {{ metric.value }}
            <span class="text-sm font-normal text-gray-400">{{ metric.unit }}</span>
          </div>
          <div class="mt-2 flex items-center gap-1" :class="{
            'text-green-500': metric.trend === 'up',
            'text-red-500': metric.trend === 'down',
            'text-gray-400': metric.trend === 'stable',
          }">
            <UIcon v-if="metric.trend === 'up'" name="i-heroicons-arrow-trending-up" class="w-4 h-4" />
            <UIcon v-else-if="metric.trend === 'down'" name="i-heroicons-arrow-trending-down" class="w-4 h-4" />
            <UIcon v-else name="i-heroicons-minus" class="w-4 h-4" />
            <span class="text-xs">{{ metric.trend === 'up' ? '↑' : metric.trend === 'down' ? '↓' : '→' }}</span>
          </div>
        </UCard>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ config: Record<string, any>; content: Record<string, any> }>();
const { locale } = useI18n();
</script>
