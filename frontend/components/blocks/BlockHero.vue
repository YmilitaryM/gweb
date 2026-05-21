<template>
  <section class="relative flex items-center justify-center min-h-[60vh] bg-gray-900 text-white overflow-hidden">
    <img
      v-if="bgUrl"
      :src="bgUrl"
      alt=""
      class="absolute inset-0 w-full h-full object-cover opacity-50"
    />
    <div class="relative z-10 text-center px-4 max-w-4xl">
      <h1 class="text-4xl md:text-5xl font-bold mb-4">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h1>
      <p
        v-if="subtitle"
        class="text-lg md:text-xl text-gray-300 mb-8"
      >
        {{ subtitle }}
      </p>
      <div v-if="content.buttons?.length" class="flex gap-4 justify-center flex-wrap">
        <UButton
          v-for="(btn, i) in content.buttons"
          :key="i"
          :to="btn.link"
          :variant="btn.variant || 'solid'"
          size="lg"
        >
          {{ locale === 'zh' ? btn.label_zh : btn.label_en }}
        </UButton>
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
const config = useRuntimeConfig();

const subtitle = computed(() =>
  locale.value === 'zh'
    ? props.content.subtitle_zh
    : props.content.subtitle_en
);

const bgUrl = computed(() =>
  props.content.bg_image
    ? `${config.public.apiBase}/../media/${props.content.bg_image}`
    : null
);
</script>
