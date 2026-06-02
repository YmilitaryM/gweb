<template>
  <section class="relative py-20 px-4 overflow-hidden">
    <!-- Subtle gradient bg -->
    <div class="absolute inset-0" style="background: linear-gradient(135deg, rgba(37,99,235,0.04), rgba(2,132,199,0.04));"></div>

    <div class="relative max-w-3xl mx-auto text-center">
      <h2 class="text-3xl md:text-4xl font-bold mb-4 text-slate-800 tracking-tight">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <p class="text-lg mb-8 max-w-xl mx-auto leading-relaxed" style="color: rgba(51,65,85,0.65);">
        {{ locale === 'zh' ? content.description_zh : content.description_en }}
      </p>
      <a
        v-if="content.button_link"
        :href="content.button_link"
        class="inline-flex items-center px-6 py-2.5 rounded-full text-sm font-medium text-white no-underline transition-all duration-200 hover:translate-y-[-1px] hover:shadow-lg"
        style="background: linear-gradient(135deg, #2563eb, #1d4ed8); box-shadow: 0 2px 12px rgba(37,99,235,0.25);"
      >
        {{ locale === 'zh' ? content.button_text_zh : content.button_text_en }}
      </a>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ config: Record<string, any>; content: Record<string, any> }>();
const { locale } = useI18n();
</script>
