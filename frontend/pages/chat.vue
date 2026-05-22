<template>
  <div class="max-w-3xl mx-auto py-8 px-4">
    <div class="flex items-center gap-3 mb-6">
      <div class="w-8 h-8 rounded-lg flex items-center justify-center"
        style="background: linear-gradient(135deg, rgba(5,150,105,0.1), rgba(2,132,199,0.1));">
        <svg class="w-4 h-4" style="color: #059669;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
        </svg>
      </div>
      <h1 class="text-xl font-medium text-slate-800 tracking-tight">
        {{ locale === 'zh' ? 'AI 智能助手' : 'AI Assistant' }}
      </h1>
    </div>

    <!-- Messages area -->
    <div
      ref="msgContainer"
      class="rounded-2xl p-4 h-[60vh] overflow-y-auto mb-4 space-y-3"
      style="background: rgba(255,255,255,0.5); border: 1px solid rgba(5,150,105,0.06);"
    >
      <div v-if="!messages.length && !streaming" class="text-center mt-20" style="color: rgba(51,65,85,0.4);">
        <div class="w-12 h-12 mx-auto mb-3 rounded-xl flex items-center justify-center"
          style="background: linear-gradient(135deg, rgba(5,150,105,0.06), rgba(2,132,199,0.06));">
          <span class="text-xl">✦</span>
        </div>
        <p class="text-sm">{{ locale === 'zh' ? '你好！有什么可以帮助你的？' : 'Hello! How can I help you?' }}</p>
      </div>

      <div
        v-for="(msg, i) in messages"
        :key="i"
        :class="msg.role === 'user' ? 'text-right' : 'text-left'"
      >
        <div
          :class="msg.role === 'user'
            ? 'text-white ml-auto'
            : 'text-slate-700'"
          :style="msg.role === 'user'
            ? 'background: linear-gradient(135deg, #059669, #10b981);'
            : 'background: rgba(255,255,255,0.8); border: 1px solid rgba(5,150,105,0.06);'"
          class="inline-block max-w-[80%] rounded-xl px-4 py-2.5 text-sm leading-relaxed"
        >
          {{ msg.content }}
        </div>
      </div>

      <div v-if="streaming" class="text-left">
        <div
          class="inline-block max-w-[80%] rounded-xl px-4 py-2.5 text-sm leading-relaxed text-slate-700"
          style="background: rgba(255,255,255,0.8); border: 1px solid rgba(5,150,105,0.06);"
        >
          {{ currentReply }}<span class="animate-pulse" style="color: #059669;">|</span>
        </div>
      </div>
    </div>

    <!-- Input area -->
    <form @submit.prevent="sendMessage" class="flex gap-3">
      <input
        v-model="input"
        :placeholder="locale === 'zh' ? '输入您的问题...' : 'Type your question...'"
        :disabled="streaming"
        class="flex-1 px-4 py-3 rounded-xl border text-sm outline-none transition-all duration-200 focus:shadow-sm disabled:opacity-50"
        style="border-color: rgba(5,150,105,0.15); background: rgba(255,255,255,0.8); color: #334155;"
        @keydown.enter="sendMessage"
      />
      <button
        type="submit"
        :disabled="streaming"
        class="px-5 py-3 rounded-xl text-sm font-medium text-white transition-all duration-200 hover:translate-y-[-1px] hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed border-none cursor-pointer"
        style="background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 2px 12px rgba(5,150,105,0.25);"
      >
        {{ streaming ? (locale === 'zh' ? '思考中' : 'Thinking') : (locale === 'zh' ? '发送' : 'Send') }}
      </button>
    </form>

    <div class="mt-4 text-center">
      <button
        @click="reset"
        class="text-xs font-medium border-none cursor-pointer transition-colors px-4 py-1.5 rounded-full"
        style="color: #94a3b8; background: transparent;"
      >
        {{ locale === 'zh' ? '重新开始' : 'Start Over' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const { locale } = useI18n();
const { messages, streaming, currentReply, send, reset } = useChat();
const input = ref('');
const msgContainer = ref<HTMLElement | null>(null);

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
</script>
