<template>
  <button
    @click="$emit('toggle')"
    class="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-2xl flex items-center justify-center cursor-pointer border-none transition-all duration-300 hover:scale-105 hover:shadow-xl group"
    style="background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 4px 20px rgba(5,150,105,0.3);"
    :aria-label="locale === 'zh' ? 'AI 助手' : 'AI Assistant'"
  >
    <svg class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
    </svg>
    <span class="absolute top-1.5 right-1.5 w-2.5 h-2.5 rounded-full bg-white opacity-80 animate-pulse"></span>
  </button>
</template>

<script setup lang="ts">
const { locale } = useI18n();
defineEmits(['toggle']);
</script>
