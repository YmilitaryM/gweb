<template>
  <section :style="sectionStyle" class="relative flex flex-col justify-center" :class="sectionHeight">
    <div v-if="config.gradient_top" class="absolute top-0 left-0 right-0 h-24 pointer-events-none" :style="{ background: `linear-gradient(to top, transparent, ${config.gradient_top})` }"></div>
    <div v-if="config.gradient_bottom" class="absolute bottom-0 left-0 right-0 h-24 pointer-events-none" :style="{ background: `linear-gradient(to bottom, transparent, ${config.gradient_bottom})` }"></div>
    <div class="w-full container mx-auto px-6">
      <!-- Section header -->
      <div class="text-center mb-14" v-if="content.title_zh">
        <h2 class="text-3xl md:text-4xl font-extrabold text-slate-900 mb-4">
          {{ locale === 'zh' ? content.title_zh : content.title_en }}
        </h2>
        <p v-if="content.subtitle_zh" class="text-lg text-slate-500 max-w-2xl mx-auto">
          {{ locale === 'zh' ? content.subtitle_zh : content.subtitle_en }}
        </p>
      </div>

      <!-- Tab buttons with numbering (01-06) -->
      <div class="flex flex-wrap justify-center gap-2 mb-12">
        <button
          v-for="(tab, i) in tabs" :key="tab.key"
          @click="activeTab = tab.key"
          class="px-6 py-3 rounded-full text-sm font-semibold transition-all duration-300 cursor-pointer border flex items-center gap-2"
          :class="activeTab === tab.key
            ? 'bg-brand-600 text-white border-brand-600 shadow-md shadow-brand-600/20'
            : 'bg-white text-slate-600 border-slate-200 hover:border-brand-300 hover:text-brand-600'"
        >
          <span class="text-xs opacity-70 font-mono">{{ String(i + 1).padStart(2, '0') }}</span>
          <span>{{ locale === 'zh' ? tab.title_zh : tab.title_en }}</span>
        </button>
      </div>

      <!-- Active tab content -->
      <Transition name="fade" mode="out-in">
        <div
          :key="activeTab"
          class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center"
          :class="activeTabIndex % 2 === 0 ? '' : 'lg:[direction:rtl]'"
        >
          <!-- Text content -->
          <div :class="activeTabIndex % 2 === 0 ? '' : 'lg:[direction:ltr]'">
            <div class="flex items-baseline gap-3 mb-6">
              <span class="text-5xl font-extrabold text-brand-600/20 font-mono leading-none">
                {{ String(activeTabIndex + 1).padStart(2, '0') }}
              </span>
              <h3 class="text-2xl md:text-3xl font-bold text-slate-900">
                {{ locale === 'zh' ? activeTabData?.title_zh : activeTabData?.title_en }}
              </h3>
            </div>
            <ul class="space-y-4">
              <li v-for="(feat, i) in activeTabData?.features || []" :key="i"
                class="flex items-start gap-3 text-slate-600">
                <span class="text-brand-500 shrink-0 mt-0.5 text-lg">&#10003;</span>
                <span>{{ locale === 'zh' ? feat.text_zh : feat.text_en }}</span>
              </li>
            </ul>
          </div>
          <!-- Image -->
          <div class="relative" :class="activeTabIndex % 2 === 0 ? '' : 'lg:[direction:ltr]'">
            <img
              v-if="activeTabData?.image_url"
              :src="activeTabData.image_url"
              :alt="locale === 'zh' ? activeTabData.title_zh : activeTabData.title_en"
              class="w-full rounded-2xl shadow-lg object-cover aspect-[4/3]"
            />
            <div v-else class="w-full aspect-[4/3] rounded-2xl bg-slate-100 flex items-center justify-center text-slate-400">
              暂无图片
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{ config: Record<string, any>; content: Record<string, any> }>()
const { locale } = useI18n()
const runtimeConfig = useRuntimeConfig()

const sectionHeight = computed(() => `min-h-[${props.config.height || 980}px]`)
const sectionStyle = computed(() => ({ background: props.config.bg || '#eff6ff' }))

interface Tab {
  key: string
  title_zh: string
  title_en: string
  image_id?: number
  image_url?: string
  features: Array<{ text_zh: string; text_en: string }>
}

const tabs = computed<Tab[]>(() => {
  const raw = props.content.tabs
  if (!raw || !Array.isArray(raw)) return []
  return raw.map((t: any) => ({
    ...t,
    image_url: t.image_id ? `${runtimeConfig.public.apiBase}/../../media/id/${t.image_id}` : undefined,
  }))
})

const activeTab = ref(tabs.value[0]?.key || '')
const activeTabIndex = computed(() => tabs.value.findIndex(t => t.key === activeTab.value))
const activeTabData = computed(() => tabs.value.find(t => t.key === activeTab.value))
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
