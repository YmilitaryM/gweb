export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export const useChat = () => {
  const config = useRuntimeConfig();
  const { locale } = useI18n();

  const sessionId = ref<string | null>(null);
  const messages = ref<ChatMessage[]>([]);
  const streaming = ref(false);
  const currentReply = ref('');

  const createSession = async () => {
    const data = await $fetch<{ session_id: string }>(
      `${config.public.apiBase}/chat/sessions`,
      { method: 'POST' }
    );
    sessionId.value = data.session_id;
  };

  const send = async (text: string) => {
    if (!sessionId.value) await createSession();
    if (!sessionId.value) return;

    messages.value.push({ role: 'user', content: text });
    streaming.value = true;
    currentReply.value = '';

    const response = await fetch(`${config.public.apiBase}/chat/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId.value,
        message: text,
        language: locale.value,
      }),
    });

    const reader = response.body?.getReader();
    if (!reader) return;
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          currentReply.value += line.slice(6);
        }
      }
    }

    messages.value.push({ role: 'assistant', content: currentReply.value });
    currentReply.value = '';
    streaming.value = false;
  };

  const reset = () => {
    sessionId.value = null;
    messages.value = [];
    currentReply.value = '';
    streaming.value = false;
  };

  return { sessionId, messages, streaming, currentReply, send, reset };
};
