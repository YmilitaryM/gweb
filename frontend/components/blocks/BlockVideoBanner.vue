<template>
  <section class="relative flex items-center justify-center min-h-[60vh] overflow-hidden">
    <video
      v-if="content.video_url"
      :src="content.video_url"
      :poster="content.poster_image"
      autoplay
      muted
      loop
      playsinline
      class="absolute inset-0 w-full h-full object-cover opacity-15"
    />

    <div class="relative z-10 text-center px-6 py-14 max-w-4xl mx-4 rounded-3xl"
      style="background: rgba(255,255,255,0.72); backdrop-filter: blur(20px); border: 1px solid rgba(5,150,105,0.06); box-shadow: 0 8px 40px rgba(0,0,0,0.04);">

      <div class="mx-auto mb-8 w-16 h-[2px] rounded-full"
        style="background: linear-gradient(90deg, #059669, #0284c7);"></div>

      <h2 class="text-4xl md:text-5xl font-bold mb-4 text-slate-800 tracking-tight">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <p v-if="subtitle" class="text-lg md:text-xl max-w-2xl mx-auto leading-relaxed"
        style="color: rgba(51,65,85,0.7);">
        {{ subtitle }}
      </p>
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{ config: Record<string, any>; content: Record<string, any> }>();
const { locale } = useI18n();

const subtitle = computed(() =>
  locale.value === 'zh' ? props.content.subtitle_zh : props.content.subtitle_en
);
</script>
