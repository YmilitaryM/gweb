<template>
  <section class="py-16 px-4">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-10">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <div v-for="(img, i) in content.images" :key="i" class="relative group overflow-hidden rounded-lg">
          <img :src="img.url" :alt="locale === 'zh' ? img.caption_zh : img.caption_en" class="w-full h-64 object-cover transition group-hover:scale-105" />
          <div v-if="img.caption_zh" class="absolute bottom-0 inset-x-0 bg-black/60 p-3 opacity-0 group-hover:opacity-100 transition">
            <p class="text-white text-sm">{{ locale === 'zh' ? img.caption_zh : img.caption_en }}</p>
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
