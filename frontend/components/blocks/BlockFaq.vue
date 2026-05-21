<template>
  <section class="py-16 px-4">
    <div class="max-w-3xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-10">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <UAccordion :items="accordionItems" />
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();
const { locale } = useI18n();

const { data } = await useFaqs();

const accordionItems = computed(() =>
  (data.value || []).map((faq: any) => ({
    label: locale.value === 'zh' ? faq.question_zh : faq.question_en,
    content: locale.value === 'zh' ? faq.answer_zh : faq.answer_en,
  }))
);
</script>
