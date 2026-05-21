<template>
  <section class="py-16 px-4 bg-gray-50 dark:bg-gray-900">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-4">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <p class="text-center text-gray-500 mb-10 max-w-2xl mx-auto">
        {{ locale === 'zh' ? content.description_zh : content.description_en }}
      </p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <UCard v-for="(card, i) in content.cards" :key="i" class="flex flex-col md:flex-row gap-6">
          <img v-if="card.image" :src="card.image" class="w-full md:w-48 h-40 object-cover rounded-lg" />
          <div class="flex-1">
            <h3 class="text-xl font-semibold mb-2">
              {{ locale === 'zh' ? card.title_zh : card.title_en }}
            </h3>
            <p class="text-gray-600 dark:text-gray-400">
              {{ locale === 'zh' ? card.desc_zh : card.desc_en }}
            </p>
            <UButton v-if="card.link" :to="card.link" variant="link" class="mt-2 px-0">
              {{ locale === 'zh' ? '了解更多' : 'Learn more' }} →
            </UButton>
          </div>
        </UCard>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ config: Record<string, any>; content: Record<string, any> }>();
const { locale } = useI18n();
</script>
