<template>
  <section class="py-16 px-4">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-light text-center mb-4 text-slate-800 tracking-tight">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-10">
        <div
          class="lg:col-span-2 rounded-xl flex items-center justify-center min-h-[400px]"
          style="background: rgba(255,255,255,0.5); border: 1px solid rgba(37,99,235,0.06);"
        >
          <div class="text-center" style="color: rgba(37,99,235,0.4);">
            <div class="w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center"
              style="background: linear-gradient(135deg, rgba(37,99,235,0.06), rgba(2,132,199,0.06));">
              <span class="text-2xl">◈</span>
            </div>
            <p class="text-sm">{{ locale === 'zh' ? '数字孪生模型' : 'Digital Twin Model' }}</p>
          </div>
        </div>
        <div class="space-y-4">
          <div
            v-for="(stat, i) in content.stats"
            :key="i"
            class="bg-white border rounded-xl p-5"
            style="border-color: #dbeafe;"
          >
            <div class="text-2xl font-light tracking-tight"
              :class="i % 2 === 0 ? 'text-brand-600' : 'text-sky-600'"
              style="font-variant-numeric: tabular-nums;">
              {{ stat.value }}
            </div>
            <div class="text-sm text-slate-400 mt-1">
              {{ locale === 'zh' ? stat.label_zh : stat.label_en }}
            </div>
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
