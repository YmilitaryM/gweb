<template>
  <div class="max-w-3xl mx-auto py-8 px-4">
    <h1 class="text-2xl font-bold mb-6">
      {{ locale === 'zh' ? '智能客服' : 'AI Assistant' }}
    </h1>

    <div class="bg-gray-100 dark:bg-gray-800 rounded-lg p-4 h-[60vh] overflow-y-auto mb-4 space-y-3">
      <div v-if="!messages.length && !streaming" class="text-center text-gray-500 mt-20">
        {{ locale === 'zh' ? '你好！有什么可以帮助你的？' : 'Hello! How can I help you?' }}
      </div>

      <div
        v-for="(msg, i) in messages"
        :key="i"
        :class="msg.role === 'user' ? 'text-right' : 'text-left'"
      >
        <div
          :class="msg.role === 'user'
            ? 'bg-blue-500 text-white ml-auto'
            : 'bg-white dark:bg-gray-700'"
          class="inline-block max-w-[80%] rounded-lg px-4 py-2"
        >
          {{ msg.content }}
        </div>
      </div>

      <div v-if="streaming" class="text-left">
        <div class="inline-block max-w-[80%] rounded-lg px-4 py-2 bg-white dark:bg-gray-700">
          {{ currentReply }}<span class="animate-pulse">|</span>
        </div>
      </div>
    </div>

    <form @submit.prevent="sendMessage" class="flex gap-2">
      <UInput
        v-model="input"
        :placeholder="locale === 'zh' ? '输入您的问题...' : 'Type your question...'"
        class="flex-1"
        :disabled="streaming"
      />
      <UButton type="submit" :loading="streaming">
        {{ locale === 'zh' ? '发送' : 'Send' }}
      </UButton>
    </form>

    <div class="mt-4 text-center">
      <UButton variant="ghost" size="sm" @click="reset">
        {{ locale === 'zh' ? '重新开始' : 'Start Over' }}
      </UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
const { locale } = useI18n();
const { messages, streaming, currentReply, send, reset } = useChat();
const input = ref('');

const sendMessage = async () => {
  const text = input.value.trim();
  if (!text || streaming.value) return;
  input.value = '';
  await send(text);
};
</script>
