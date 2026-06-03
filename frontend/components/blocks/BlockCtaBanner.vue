<template>
  <section :style="sectionStyle" class="relative flex flex-col justify-center overflow-hidden" :class="sectionHeight">
    <div v-if="config.gradient_top" class="absolute top-0 left-0 right-0 h-20 pointer-events-none" :style="{ background: `linear-gradient(to top, transparent, ${config.gradient_top})` }"></div>
    <div class="absolute inset-0 pointer-events-none" style="background: linear-gradient(135deg, rgba(37,99,235,0.03), rgba(2,132,199,0.03));"></div>
    <div v-if="config.gradient_bottom" class="absolute bottom-0 left-0 right-0 h-32 pointer-events-none" :style="{ background: `linear-gradient(to bottom, transparent, ${config.gradient_bottom})` }"></div>
    <div class="relative w-full max-w-3xl mx-auto px-6 text-center">
      <h2 class="text-3xl md:text-4xl font-extrabold mb-4 text-slate-800 tracking-tight">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <p class="text-lg mb-8 max-w-xl mx-auto leading-relaxed text-slate-700/65">
        {{ locale === 'zh' ? content.description_zh : content.description_en }}
      </p>
      <a
        v-if="content.button_link"
        :href="content.button_link"
        class="inline-flex items-center px-6 py-2.5 rounded-full text-sm font-medium text-white no-underline transition-all duration-200 hover:translate-y-[-1px] bg-gradient-to-br from-blue-600 to-blue-700 shadow-lg shadow-blue-600/25"
      >
        {{ locale === 'zh' ? content.button_text_zh : content.button_text_en }}
      </a>
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{ config: Record<string, any>; content: Record<string, any> }>();
const { locale } = useI18n();

const sectionHeight = computed(() => `h-[${props.config.height || 714}px]`)
const sectionStyle = computed(() => ({ background: props.config.bg || '#f8fafc' }))
</script>
