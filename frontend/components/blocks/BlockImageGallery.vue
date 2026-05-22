<template>
  <section class="py-16 px-4">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-light text-center mb-10 text-slate-800 tracking-tight">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <div
          v-for="(img, i) in content.images"
          :key="i"
          class="relative group overflow-hidden rounded-xl"
          style="border: 1px solid rgba(5,150,105,0.06);"
        >
          <img
            :src="img.url"
            :alt="locale === 'zh' ? img.caption_zh : img.caption_en"
            class="w-full h-64 object-cover transition duration-300 group-hover:scale-105"
          />
          <div
            v-if="img.caption_zh"
            class="absolute bottom-0 inset-x-0 p-3 opacity-0 group-hover:opacity-100 transition duration-200"
            style="background: linear-gradient(transparent, rgba(0,0,0,0.5));"
          >
            <p class="text-white text-sm">{{ locale === 'zh' ? img.caption_zh : img.caption_en }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ config: Record<string, any>; content: Record<string, any> }>();
const { locale } = useI18n();
</script>
