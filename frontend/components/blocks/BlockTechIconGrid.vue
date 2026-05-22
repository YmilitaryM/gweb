<template>
  <section class="py-16 px-4">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-light text-center mb-10 text-slate-800 tracking-tight">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <div
          v-for="(item, i) in content.items"
          :key="i"
          class="text-center p-6 rounded-xl transition-all duration-200 hover:translate-y-[-2px]"
          style="background: rgba(255,255,255,0.6); border: 1px solid rgba(5,150,105,0.06);"
        >
          <div class="w-10 h-10 mx-auto mb-3 rounded-lg flex items-center justify-center"
            style="background: linear-gradient(135deg, rgba(5,150,105,0.08), rgba(2,132,199,0.08));">
            <span class="text-lg">{{ item.icon || '◆' }}</span>
          </div>
          <h3 class="font-medium text-slate-700 mb-1 text-sm">
            {{ locale === 'zh' ? item.label_zh : item.label_en }}
          </h3>
          <p class="text-xs text-slate-400 leading-relaxed">
            {{ locale === 'zh' ? item.desc_zh : item.desc_en }}
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ config: Record<string, any>; content: Record<string, any> }>();
const { locale } = useI18n();
</script>
