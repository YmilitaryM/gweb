<template>
  <section class="py-16 px-4">
    <div class="max-w-6xl mx-auto">
      <h2
        v-if="content.title_zh"
        class="text-3xl font-light text-center mb-10 text-slate-800 tracking-tight"
      >
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="(card, i) in content.cards"
          :key="i"
          class="bg-white border rounded-xl p-6 transition-shadow hover:shadow-md"
          style="border-color: #e8f5e9"
        >
          <img
            v-if="card.image"
            :src="card.image"
            alt=""
            class="w-full h-48 object-cover rounded-lg mb-4"
          />
          <h3 class="text-lg font-medium text-slate-800 mb-2">
            {{ locale === 'zh' ? card.title_zh : card.title_en }}
          </h3>
          <p class="text-sm text-slate-500 leading-relaxed mb-4">
            {{ locale === 'zh' ? card.desc_zh : card.desc_en }}
          </p>
          <NuxtLink
            v-if="card.link"
            :to="card.link"
            class="text-sm font-medium text-emerald-600 hover:text-emerald-700 no-underline"
          >
            {{ locale === 'zh' ? '了解更多 →' : 'Learn more →' }}
          </NuxtLink>
        </div>
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
