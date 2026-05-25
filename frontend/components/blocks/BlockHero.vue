<template>
  <section class="relative flex items-center justify-center min-h-[70vh] overflow-hidden">
    <!-- Background image layer -->
    <img
      v-if="bgUrl"
      :src="bgUrl"
      alt=""
      class="absolute inset-0 w-full h-full object-cover opacity-15"
    />

    <!-- Glass content card -->
    <div class="relative z-10 text-center px-6 py-14 max-w-4xl mx-4 rounded-3xl"
      style="background: rgba(255,255,255,0.72); backdrop-filter: blur(20px); border: 1px solid rgba(5,150,105,0.06); box-shadow: 0 8px 40px rgba(0,0,0,0.04);">

      <!-- Decorative top accent line -->
      <div class="mx-auto mb-8 w-16 h-[2px] rounded-full"
        style="background: linear-gradient(90deg, #059669, #0284c7);"></div>

      <h1 class="text-4xl md:text-5xl font-bold mb-5 text-slate-800 tracking-tight leading-tight">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h1>

      <p
        v-if="subtitle"
        class="text-lg md:text-xl mb-10 max-w-2xl mx-auto leading-relaxed"
        style="color: rgba(51,65,85,0.7);"
      >
        {{ subtitle }}
      </p>

      <div v-if="content.buttons?.length" class="flex gap-4 justify-center flex-wrap">
        <a
          v-for="(btn, i) in content.buttons"
          :key="i"
          :href="btn.link"
          :class="[
            'inline-flex items-center px-6 py-2.5 rounded-full text-sm font-medium no-underline transition-all duration-200',
            i === 0
              ? 'text-white hover:translate-y-[-1px] hover:shadow-lg'
              : 'border hover:translate-y-[-1px]'
          ]"
          :style="i === 0
            ? 'background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 2px 12px rgba(5,150,105,0.25);'
            : 'border-color: rgba(5,150,105,0.2); color: #059669; background: rgba(255,255,255,0.6);'"
        >
          {{ locale === 'zh' ? btn.label_zh : btn.label_en }}
        </a>
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
    ? `${config.public.apiBase}/../../media/${props.content.bg_image}`
    : null
);
</script>
