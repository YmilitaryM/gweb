<template>
  <section class="py-20 px-4" :style="{ backgroundColor: content.bg_color || '#1e40af' }">
    <div class="max-w-3xl mx-auto text-center text-white">
      <h2 class="text-3xl md:text-4xl font-bold mb-4">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <p class="text-lg text-white/80 mb-8">
        {{ locale === 'zh' ? content.description_zh : content.description_en }}
      </p>
      <UButton v-if="content.button_link" :to="content.button_link" size="lg" variant="outline" class="text-white border-white hover:bg-white hover:text-gray-900">
        {{ locale === 'zh' ? content.button_text_zh : content.button_text_en }}
      </UButton>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ config: Record<string, any>; content: Record<string, any> }>();
const { locale } = useI18n();
</script>
