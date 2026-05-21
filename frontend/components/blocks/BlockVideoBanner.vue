<template>
  <section class="relative flex items-center justify-center min-h-[60vh] bg-gray-900 text-white overflow-hidden">
    <video
      v-if="content.video_url"
      :src="content.video_url"
      :poster="content.poster_image"
      autoplay
      muted
      loop
      playsinline
      class="absolute inset-0 w-full h-full object-cover opacity-50"
    />
    <div class="relative z-10 text-center px-4 max-w-4xl">
      <h2 class="text-4xl md:text-5xl font-bold mb-4">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <p v-if="subtitle" class="text-lg md:text-xl text-gray-300">
        {{ subtitle }}
      </p>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ config: Record<string, any>; content: Record<string, any> }>();
const { locale } = useI18n();

const subtitle = computed(() =>
  locale.value === 'zh' ? content.subtitle_zh : content.subtitle_en
);
</script>
