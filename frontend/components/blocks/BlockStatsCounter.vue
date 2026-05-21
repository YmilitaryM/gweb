<template>
  <section class="py-16 px-4">
    <div class="max-w-4xl mx-auto">
      <h2
        v-if="content.title_zh"
        class="text-3xl font-light text-center mb-10 text-slate-800 tracking-tight"
      >
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="flex justify-center gap-5 flex-wrap">
        <div
          v-for="(item, i) in content.items"
          :key="i"
          class="flex-1 min-w-[140px] max-w-[180px] text-center py-5 px-4 rounded-2xl border"
          style="background: rgba(255,255,255,0.65); backdrop-filter: blur(12px); border-color: rgba(5,150,105,0.06); box-shadow: 0 4px 16px rgba(0,0,0,0.015)"
        >
          <div
            class="text-[30px] font-light tracking-tight"
            :class="i >= 2 ? 'text-sky-600' : 'text-emerald-600'"
            style="font-variant-numeric: tabular-nums"
          >
            {{ item.value }}
          </div>
          <div class="text-xs text-slate-400 mt-1">
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
