<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <div
      v-if="open"
      class="fixed inset-0 z-[60] transition-opacity duration-300"
      style="background: rgba(0,0,0,0.15);"
      @click="close"
    />

    <!-- Panel -->
    <div
      class="fixed top-0 right-0 h-full z-[61] w-[400px] max-w-[calc(100vw-2rem)] flex flex-col transition-transform duration-300 ease-out"
      :style="{
        transform: open ? 'translateX(0)' : 'translateX(100%)',
        background: 'rgba(255,255,255,0.95)',
        backdropFilter: 'blur(24px)',
        borderLeft: '1px solid rgba(37,99,235,0.05)',
        boxShadow: '-8px 0 40px rgba(0,0,0,0.06)',
      }"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-5 py-4" style="border-bottom: 1px solid rgba(37,99,235,0.06);">
        <div class="flex items-center gap-2.5">
          <div class="w-7 h-7 rounded-lg flex items-center justify-center"
            style="background: linear-gradient(135deg, rgba(37,99,235,0.1), rgba(2,132,199,0.1));">
            <svg class="w-3.5 h-3.5" style="color: #2563eb;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
            </svg>
          </div>
          <span class="text-sm font-medium text-slate-700">
            {{ locale === 'zh' ? 'AI 助手' : 'AI Assistant' }}
          </span>
        </div>
        <button
          @click="close"
          class="w-7 h-7 rounded-lg flex items-center justify-center border-none cursor-pointer text-slate-400 hover:text-slate-600 transition-colors"
          style="background: transparent;"
          :aria-label="locale === 'zh' ? '关闭' : 'Close'"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Messages -->
      <div ref="msgContainer" class="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        <div v-if="!messages.length && !streaming" class="text-center mt-20" style="color: rgba(51,65,85,0.35);">
          <div class="w-10 h-10 mx-auto mb-3 rounded-xl flex items-center justify-center"
            style="background: linear-gradient(135deg, rgba(37,99,235,0.06), rgba(2,132,199,0.06));">
            <span class="text-lg">✦</span>
          </div>
          <p class="text-xs">{{ locale === 'zh' ? '有什么可以帮助你的？' : 'How can I help you?' }}</p>
        </div>

        <div v-for="(msg, i) in messages" :key="i" :class="msg.role === 'user' ? 'text-right' : 'text-left'">
          <div
            :style="msg.role === 'user'
              ? 'background: linear-gradient(135deg, #2563eb, #1d4ed8);'
              : 'background: rgba(37,99,235,0.04); border: 1px solid rgba(37,99,235,0.06);'"
            :class="msg.role === 'user' ? 'text-white ml-auto' : 'text-slate-700'"
            class="inline-block max-w-[85%] rounded-xl px-3.5 py-2 text-[13px] leading-relaxed"
          >
            {{ msg.content }}
          </div>
        </div>

        <div v-if="streaming" class="text-left">
          <div class="inline-block max-w-[85%] rounded-xl px-3.5 py-2 text-[13px] leading-relaxed text-slate-700"
            style="background: rgba(37,99,235,0.04); border: 1px solid rgba(37,99,235,0.06);">
            {{ currentReply }}<span class="animate-pulse" style="color: #2563eb;">|</span>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="px-4 py-3" style="border-top: 1px solid rgba(37,99,235,0.06);">
        <form @submit.prevent="sendMessage" class="flex gap-2">
          <input
            v-model="input"
            :placeholder="locale === 'zh' ? '输入问题...' : 'Ask anything...'"
            :disabled="streaming"
            class="flex-1 px-3.5 py-2 rounded-xl border text-[13px] outline-none transition-all duration-200 focus:shadow-sm disabled:opacity-50"
            style="border-color: rgba(37,99,235,0.12); background: rgba(37,99,235,0.02); color: #334155;"
          />
          <button
            type="submit"
            :disabled="streaming || !input.trim()"
            class="w-9 h-9 rounded-xl flex items-center justify-center border-none cursor-pointer transition-all duration-200 hover:scale-105 disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
            style="background: linear-gradient(135deg, #2563eb, #1d4ed8); box-shadow: 0 2px 8px rgba(37,99,235,0.2);"
          >
            <svg class="w-3.5 h-3.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </button>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
const { locale } = useI18n();
const { messages, streaming, currentReply, send, reset } = useChat();
const input = ref('');
const msgContainer = ref<HTMLElement | null>(null);
const open = ref(false);

const close = () => { open.value = false; };
const show = () => {
  open.value = true;
  nextTick(() => {
    if (msgContainer.value) {
      msgContainer.value.scrollTop = msgContainer.value.scrollHeight;
    }
  });
};

const sendMessage = async () => {
  const text = input.value.trim();
  if (!text || streaming.value) return;
  input.value = '';
  await send(text);
  nextTick(() => {
    if (msgContainer.value) {
      msgContainer.value.scrollTop = msgContainer.value.scrollHeight;
    }
  });
};

defineExpose({ show, close });
</script>
