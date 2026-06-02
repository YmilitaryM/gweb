<template>
  <section class="relative min-h-[660px] md:min-h-[720px] lg:h-[86vh] lg:max-h-[800px] w-full overflow-hidden flex flex-col justify-center items-center text-white">
    <!-- Background image slides with crossfade -->
    <div class="absolute inset-0 w-full h-full overflow-hidden bg-slate-900">
      <div
        v-for="(slide, i) in slides"
        :key="i"
        class="absolute inset-0 transition-opacity duration-1000 ease-in-out"
        :class="i === currentIndex ? 'opacity-100' : 'opacity-0'"
      >
        <img
          v-if="slide.image_url"
          :src="slide.image_url"
          alt=""
          class="w-full h-full object-cover"
        />
        <div class="absolute inset-0 bg-black/20"></div>
      </div>
    </div>

    <!-- Content overlay -->
    <div class="relative z-10 text-center px-6 max-w-4xl mx-auto">
      <h1 class="text-4xl md:text-5xl lg:text-6xl font-extrabold mb-5 tracking-tight leading-tight drop-shadow-sm">
        {{ locale === 'zh' ? currentSlide?.title_zh : currentSlide?.title_en }}
      </h1>
      <p v-if="currentSlide?.subtitle_zh || currentSlide?.subtitle_en"
        class="text-lg md:text-xl mb-10 max-w-2xl mx-auto leading-relaxed text-white/85">
        {{ locale === 'zh' ? currentSlide?.subtitle_zh : currentSlide?.subtitle_en }}
      </p>
      <div v-if="currentSlide?.buttons?.length" class="flex gap-4 justify-center flex-wrap">
        <a v-for="(btn, i) in currentSlide.buttons" :key="i" :href="btn.link"
          :class="[
            'inline-flex items-center px-7 py-3 rounded-full text-sm font-semibold transition-all duration-300',
            i === 0
              ? 'bg-brand-600 text-white hover:bg-brand-700 hover:scale-105 shadow-lg shadow-brand-600/30'
              : 'border border-white/30 text-white hover:bg-white/10 hover:scale-105'
          ]">
          {{ locale === 'zh' ? btn.label_zh : btn.label_en }}
        </a>
      </div>
    </div>

    <!-- Navigation arrows (only show if multiple slides) -->
    <button v-if="slides.length > 1" @click="prev"
      class="absolute left-6 top-1/2 -translate-y-1/2 w-14 h-14 rounded-full border border-white/10 bg-black/30 hover:bg-black/60 backdrop-blur-md flex items-center justify-center text-white transition-all z-30 cursor-pointer">
      <span class="text-2xl">‹</span>
    </button>
    <button v-if="slides.length > 1" @click="next"
      class="absolute right-6 top-1/2 -translate-y-1/2 w-14 h-14 rounded-full border border-white/10 bg-black/30 hover:bg-black/60 backdrop-blur-md flex items-center justify-center text-white transition-all z-30 cursor-pointer">
      <span class="text-2xl">›</span>
    </button>

    <!-- Dot indicators (only if multiple slides) -->
    <div v-if="slides.length > 1" class="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-2 z-30">
      <button
        v-for="(_, i) in slides" :key="i"
        @click="goTo(i)"
        class="w-2.5 h-2.5 rounded-full transition-all duration-300 cursor-pointer"
        :class="i === currentIndex ? 'bg-white w-8' : 'bg-white/40 hover:bg-white/70'"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{ config: Record<string, any>; content: Record<string, any> }>()
const { locale } = useI18n()
const runtimeConfig = useRuntimeConfig()

interface Slide {
  image_id?: number
  image_url?: string
  title_zh?: string
  title_en?: string
  subtitle_zh?: string
  subtitle_en?: string
  buttons?: Array<{ label_zh: string; label_en: string; link: string }>
}

const slides = computed<Slide[]>(() => {
  const raw = props.content.slides
  if (!raw || !Array.isArray(raw) || raw.length === 0) {
    // Fallback: single slide from old format
    return [{
      image_id: props.content.bg_image,
      image_url: props.content.bg_image ? `${runtimeConfig.public.apiBase}/../../media/id/${props.content.bg_image}` : undefined,
      title_zh: props.content.title_zh,
      title_en: props.content.title_en,
      subtitle_zh: props.content.subtitle_zh,
      subtitle_en: props.content.subtitle_en,
      buttons: props.content.buttons || [],
    }]
  }
  return raw.map((s: any) => ({
    ...s,
    image_url: s.image_id ? `${runtimeConfig.public.apiBase}/../../media/id/${s.image_id}` : undefined,
  }))
})

const currentIndex = ref(0)
const currentSlide = computed(() => slides.value[currentIndex.value] || slides.value[0])

function next() { currentIndex.value = (currentIndex.value + 1) % slides.value.length }
function prev() { currentIndex.value = (currentIndex.value - 1 + slides.value.length) % slides.value.length }
function goTo(i: number) { currentIndex.value = i }

// Auto-play
let timer: ReturnType<typeof setInterval> | null = null
const interval = computed(() => props.content.auto_play_interval || 5000)

onMounted(() => {
  if (slides.value.length > 1) {
    timer = setInterval(next, interval.value)
  }
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

