<template>
  <section class="py-16 px-4 max-w-3xl mx-auto">
    <h1 class="text-3xl font-bold text-center mb-10">
      {{ locale === 'zh' ? '常见问题' : 'FAQ' }}
    </h1>

    <UAccordion v-if="faqs.length" :items="accordionItems" />

    <p v-else class="text-center text-gray-500 py-20">
      {{ locale === 'zh' ? '暂无常见问题' : 'No FAQs yet' }}
    </p>
  </section>
</template>

<script setup lang="ts">
const { locale } = useI18n();
const { data } = await useFaqs();
const faqs = computed(() => data.value || []);

const accordionItems = computed(() =>
  faqs.value.map((faq: any) => ({
    label: locale.value === 'zh' ? faq.question_zh : faq.question_en,
    content: locale.value === 'zh' ? faq.answer_zh : faq.answer_en,
  }))
);
</script>
