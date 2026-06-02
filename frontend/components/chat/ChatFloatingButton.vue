<template>
  <div class="fixed bottom-8 right-8 z-50 flex flex-col items-center gap-3.5 pointer-events-none">
    <!-- Back to top -->
    <Transition name="fade-up">
      <button v-if="showBackToTop" @click="scrollToTop"
        class="w-12 h-12 bg-white/95 backdrop-blur-md text-slate-600 hover:text-brand-600 border border-slate-200/90 hover:border-brand-300 rounded-full flex items-center justify-center hover:scale-110 active:scale-95 transition-all shadow-lg cursor-pointer pointer-events-auto"
        title="返回顶部" aria-label="返回顶部">
        <span class="text-xl font-bold">↑</span>
      </button>
    </Transition>

    <!-- AI floating button & window -->
    <button v-if="!isOpen" @click="isOpen = true"
      class="w-16 h-16 bg-brand-600 text-white rounded-full flex items-center justify-center hover:scale-110 active:scale-95 transition-all shadow-xl shadow-brand-600/30 cursor-pointer pointer-events-auto font-bold text-xl tracking-wider select-none">
      AI
    </button>

    <Transition name="fade-up">
      <div v-if="isOpen"
        class="w-[360px] md:w-[410px] h-[580px] bg-white/95 backdrop-blur-2xl rounded-3xl flex flex-col overflow-hidden shadow-[0_20px_50px_rgba(0,0,0,0.12)] border border-slate-200/80 pointer-events-auto">
        <!-- Header -->
        <div class="bg-slate-50 border-b border-slate-200/60 p-5 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-brand-50 flex items-center justify-center text-brand-600 border border-brand-100">
              <span class="text-lg">✦</span>
            </div>
            <div>
              <div class="font-bold text-sm text-slate-950">金捷利 AI 智能管家</div>
              <div class="text-[11px] text-slate-500 font-mono tracking-wider uppercase">24/7 Energy & IoT Advisor</div>
            </div>
          </div>
          <button @click="isOpen = false"
            class="w-8 h-8 rounded-lg border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-200 flex items-center justify-center transition-all cursor-pointer">
            <span>✕</span>
          </button>
        </div>
        <!-- Chat content -->
        <div class="flex-1 overflow-hidden">
          <ChatPanel :embedded="true" />
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const isOpen = ref(false)
const showBackToTop = ref(false)

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function onScroll() {
  showBackToTop.value = window.scrollY > 300
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
.fade-up-enter-active, .fade-up-leave-active { transition: all 0.3s ease; }
.fade-up-enter-from, .fade-up-leave-to { opacity: 0; transform: translateY(15px) scale(0.95); }
</style>
