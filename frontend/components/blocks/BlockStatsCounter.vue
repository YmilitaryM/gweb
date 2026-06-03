<template>
  <section :style="sectionStyle" class="relative flex flex-col justify-center overflow-hidden">
    <div class="w-full container mx-auto px-6">
      <!-- Section label -->
      <div class="text-center mb-6" v-if="content.subtitle_zh || content.subtitle_en">
        <span class="text-brand-400 text-sm font-semibold uppercase tracking-widest">
          {{ locale === 'zh' ? (content.subtitle_zh || content.label_zh) : (content.subtitle_en || content.label_en) }}
        </span>
      </div>

      <!-- Title -->
      <h2
        v-if="content.title_zh"
        class="text-3xl md:text-4xl lg:text-5xl font-extrabold text-center mb-16 text-white tracking-tight"
      >
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>

      <!-- Stats grid -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-5xl mx-auto">
        <div
          v-for="(item, i) in content.items"
          :key="i"
          class="text-center"
        >
          <div
            class="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-white mb-3"
            style="font-variant-numeric: tabular-nums"
          >
            {{ item.value }}
          </div>
          <div class="text-slate-400 text-sm md:text-base font-medium tracking-wide">
            {{ locale === 'zh' ? item.label_zh : item.label_en }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();
const { locale } = useI18n();

const sectionStyle = computed(() => {
  const bg = (props.config.bg || '').trim() || '#0f172a'
  const h = props.config.height || 624
  return { minHeight: `${h}px`, background: bg }
})
</script>
