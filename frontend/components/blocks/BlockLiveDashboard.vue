<template>
  <section class="py-16 px-4">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-light text-center mb-10 text-slate-800 tracking-tight">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div
          v-for="(metric, i) in content.metrics"
          :key="i"
          class="bg-white border rounded-xl p-5"
          style="border-color: #dbeafe;"
        >
          <div class="text-sm text-slate-400 mb-1">
            {{ locale === 'zh' ? metric.label_zh : metric.label_en }}
          </div>
          <div class="text-2xl font-light tracking-tight text-slate-800" style="font-variant-numeric: tabular-nums;">
            {{ metric.value }}
            <span class="text-sm font-normal text-slate-400">{{ metric.unit }}</span>
          </div>
          <div class="mt-2 flex items-center gap-1 text-xs font-medium"
            :style="{
              color: metric.trend === 'up' ? '#2563eb' : metric.trend === 'down' ? '#ef4444' : '#94a3b8'
            }">
            <span>{{ metric.trend === 'up' ? '↑' : metric.trend === 'down' ? '↓' : '→' }}</span>
            {{ metric.trend === 'up' ? 'Up' : metric.trend === 'down' ? 'Down' : 'Stable' }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ config: Record<string, any>; content: Record<string, any> }>();
const { locale } = useI18n();
</script>
