<template>
  <section class="py-16 px-4 bg-gray-50 dark:bg-gray-900">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-10">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8 items-center justify-items-center">
        <a v-for="(logo, i) in content.logos" :key="i" :href="logo.link || '#'" target="_blank" class="grayscale hover:grayscale-0 transition opacity-60 hover:opacity-100">
          <img :src="logo.url" :alt="logo.name" class="h-12 object-contain" />
        </a>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ config: Record<string, any>; content: Record<string, any> }>();
</script>
