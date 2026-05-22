<template>
  <section class="py-16 px-4">
    <div class="max-w-3xl mx-auto">
      <h2 class="text-3xl font-light text-center mb-10 text-slate-800 tracking-tight">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="space-y-3">
        <div
          v-for="(item, i) in accordionItems"
          :key="i"
          class="bg-white border rounded-xl overflow-hidden"
          style="border-color: #e8f5e9;"
        >
          <button
            class="w-full flex justify-between items-center px-5 py-4 text-left text-sm font-medium text-slate-700 hover:text-slate-900 transition-colors border-none cursor-pointer"
            style="background: transparent;"
            @click="toggle(i)"
          >
            {{ item.label }}
            <span
              class="text-base transition-transform duration-200 flex-shrink-0 ml-4"
              :style="{ transform: openIndex === i ? 'rotate(45deg)' : 'rotate(0deg)', color: openIndex === i ? '#059669' : '#94a3b8' }"
            >+</span>
          </button>
          <div
            v-if="openIndex === i"
            class="px-5 pb-4 text-sm text-slate-500 leading-relaxed"
            style="border-top: 1px solid rgba(5,150,105,0.06); padding-top: 1rem;"
          >
            {{ item.content }}
          </div>
        </div>
      </div>
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

const openIndex = ref<number | null>(null);
const toggle = (i: number) => {
  openIndex.value = openIndex.value === i ? null : i;
};
</script>
