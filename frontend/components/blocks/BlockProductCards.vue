<template>
  <section class="relative h-[864px] flex flex-col justify-center" style="background: #f1f5f9;">
    <div class="absolute top-0 left-0 right-0 h-24 pointer-events-none" style="background: linear-gradient(to top, transparent, rgba(250,251,252,0.9));"></div>
    <div class="absolute bottom-0 left-0 right-0 h-24 pointer-events-none" style="background: linear-gradient(to bottom, transparent, rgba(239,246,255,0.85));"></div>
    <div class="w-full max-w-7xl mx-auto px-6">
      <h2
        v-if="content.title_zh"
        class="text-3xl md:text-4xl font-extrabold text-center mb-5 text-slate-900 tracking-tight"
      >
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <p
        v-if="content.subtitle_zh"
        class="text-lg text-slate-500 text-center max-w-2xl mx-auto mb-14"
      >
        {{ locale === 'zh' ? content.subtitle_zh : content.subtitle_en }}
      </p>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div
          v-for="(card, i) in content.cards"
          :key="i"
          class="group bg-white rounded-2xl border border-slate-100 p-6 transition-all duration-300 ease-out cursor-pointer
                 hover:shadow-xl hover:shadow-slate-200/60 hover:border-brand-200 hover:-translate-y-1"
        >
          <!-- Image -->
          <div class="overflow-hidden rounded-xl mb-5">
            <img
              v-if="card.image"
              :src="card.image"
              alt=""
              class="w-full h-52 object-cover rounded-xl transition-transform duration-500 ease-out group-hover:scale-105"
            />
            <div v-else class="w-full h-52 rounded-xl bg-slate-100 flex items-center justify-center text-slate-300">
              <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
          <!-- Title -->
          <h3 class="text-xl font-bold text-slate-900 mb-3 group-hover:text-brand-700 transition-colors duration-300">
            {{ locale === 'zh' ? card.title_zh : card.title_en }}
          </h3>
          <!-- Description -->
          <p class="text-sm text-slate-500 leading-relaxed mb-5">
            {{ locale === 'zh' ? card.desc_zh : card.desc_en }}
          </p>
          <!-- Link -->
          <NuxtLink
            v-if="card.link"
            :to="card.link"
            class="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 no-underline
                   group-hover:text-brand-700 transition-colors duration-300"
          >
            <span>{{ locale === 'zh' ? '了解更多' : 'Learn more' }}</span>
            <span class="transition-transform duration-300 group-hover:translate-x-1">&rarr;</span>
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
