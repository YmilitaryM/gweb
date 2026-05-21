<template>
  <section class="py-16 px-4">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-10">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <UCard v-for="(card, i) in content.cards" :key="i">
          <img
            v-if="card.image"
            :src="card.image"
            class="w-full h-48 object-cover rounded-t"
          />
          <template #header>
            <h3 class="text-lg font-semibold">
              {{ locale === 'zh' ? card.title_zh : card.title_en }}
            </h3>
          </template>
          <p class="text-gray-600 dark:text-gray-400">
            {{ locale === 'zh' ? card.desc_zh : card.desc_en }}
          </p>
          <template v-if="card.link" #footer>
            <UButton :to="card.link" variant="link">
              {{ locale === 'zh' ? '了解更多' : 'Learn more' }}
            </UButton>
          </template>
        </UCard>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();
const { locale } = useI18n();
</script>
