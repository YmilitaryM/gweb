# Frontend Pages & Block Renderer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire up Nuxt 3 frontend with 7 core block renderers, 4 composables, and 5 new pages consuming the backend REST API.

**Architecture:** BlockRenderer dispatches by block.type to block-specific Vue components. Pages and blocks fetch via composables wrapping `useFetch`. Nuxt UI v3 provides UI primitives, Tailwind handles custom styling.

**Tech Stack:** Nuxt 3, Vue 3, Nuxt UI v3, Tailwind CSS, @nuxtjs/i18n

---

### Task 1: Install Nuxt UI v3

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/nuxt.config.ts`

- [ ] **Step 1: Add @nuxt/ui dependency**

```bash
cd frontend && pnpm add @nuxt/ui
```

- [ ] **Step 2: Register Nuxt UI module in config**

In `frontend/nuxt.config.ts`, add `@nuxt/ui` to modules array:

```typescript
export default defineNuxtConfig({
  compatibilityDate: '2026-05-21',
  devtools: { enabled: true },
  ssr: true,
  modules: ['@nuxtjs/i18n', '@nuxt/image', '@nuxt/ui'],
  i18n: {
    locales: ['zh', 'en'],
    defaultLocale: 'zh',
    strategy: 'prefix_except_default',
  },
  image: { domains: ['localhost'] },
  routeRules: {
    '/': { prerender: true },
    '/about': { prerender: true },
    '/products': { prerender: true },
    '/solutions': { prerender: true },
    '/contact': { prerender: true },
    '/news': { isr: 300 },
    '/news/**': { isr: 300 },
    '/chat': { ssr: false },
  },
  runtimeConfig: {
    public: { apiBase: 'http://localhost:8000/api/v1' },
  },
});
```

- [ ] **Step 3: Verify dev server starts**

```bash
cd frontend && pnpm dev
```

Check `http://localhost:3000` loads without errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/package.json frontend/pnpm-lock.yaml frontend/nuxt.config.ts
git commit -m "feat: add Nuxt UI v3 to frontend"
```

---

### Task 2: Create useNews composable

**Files:**
- Create: `frontend/composables/useNews.ts`

- [ ] **Step 1: Create the composable**

```typescript
export const useNewsList = async (page = 1, size = 10, category?: string) => {
  const config = useRuntimeConfig();
  const params = new URLSearchParams({ page: String(page), size: String(size) });
  if (category) params.set('category', category);

  const { data, error, refresh } = await useFetch(
    `${config.public.apiBase}/news?${params}`
  );
  return { data, error, refresh };
};

export const useNewsArticle = async (id: number) => {
  const config = useRuntimeConfig();
  const { data, error } = await useFetch(`${config.public.apiBase}/news/${id}`);
  return { article: data, error };
};
```

- [ ] **Step 2: Commit**

```bash
git add frontend/composables/useNews.ts
git commit -m "feat: add useNews composable"
```

---

### Task 3: Create useFaq composable

**Files:**
- Create: `frontend/composables/useFaq.ts`

- [ ] **Step 1: Create the composable**

```typescript
export const useFaqs = async () => {
  const config = useRuntimeConfig();
  const { data, error, refresh } = await useFetch(`${config.public.apiBase}/faqs`);
  return { data, error, refresh };
};
```

- [ ] **Step 2: Commit**

```bash
git add frontend/composables/useFaq.ts
git commit -m "feat: add useFaq composable"
```

---

### Task 4: Create useInquiry composable

**Files:**
- Create: `frontend/composables/useInquiry.ts`

- [ ] **Step 1: Create the composable**

```typescript
export const useInquiry = () => {
  const config = useRuntimeConfig();
  const loading = ref(false);
  const error = ref<string | null>(null);
  const success = ref(false);

  const submit = async (form: {
    company_name: string;
    contact_name: string;
    phone: string;
    message: string;
  }) => {
    loading.value = true;
    error.value = null;
    success.value = false;
    try {
      await $fetch(`${config.public.apiBase}/inquiries`, {
        method: 'POST',
        body: form,
      });
      success.value = true;
    } catch (e: any) {
      error.value = e.data?.detail || 'Submission failed';
    } finally {
      loading.value = false;
    }
  };

  return { submit, loading, error, success };
};
```

- [ ] **Step 2: Commit**

```bash
git add frontend/composables/useInquiry.ts
git commit -m "feat: add useInquiry composable"
```

---

### Task 5: Create useChat composable

**Files:**
- Create: `frontend/composables/useChat.ts`

- [ ] **Step 1: Create the composable**

```typescript
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/composables/useChat.ts
git commit -m "feat: add useChat composable with SSE streaming"
```

---

### Task 6: Create BlockRenderer component

**Files:**
- Create: `frontend/components/blocks/BlockRenderer.vue`

- [ ] **Step 1: Create BlockRenderer**

```vue
<template>
  <component
    v-if="component"
    :is="component"
    :config="block.config"
    :content="block.content"
  />
</template>

<script setup lang="ts">
interface Block {
  id: number;
  type: string;
  order: number;
  config: Record<string, any>;
  content: Record<string, any>;
}

const props = defineProps<{ block: Block }>();

const componentMap: Record<string, any> = {
  hero: defineAsyncComponent(() => import('./BlockHero.vue')),
  richtext: defineAsyncComponent(() => import('./BlockRichtext.vue')),
  news_list: defineAsyncComponent(() => import('./BlockNewsList.vue')),
  faq: defineAsyncComponent(() => import('./BlockFaq.vue')),
  contact_form: defineAsyncComponent(() => import('./BlockContactForm.vue')),
  product_cards: defineAsyncComponent(() => import('./BlockProductCards.vue')),
  stats_counter: defineAsyncComponent(() => import('./BlockStatsCounter.vue')),
};

const component = computed(() => componentMap[props.block.type] || null);
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/blocks/BlockRenderer.vue
git commit -m "feat: add BlockRenderer dispatch component"
```

---

### Task 7: Create BlockHero component

**Files:**
- Create: `frontend/components/blocks/BlockHero.vue`

- [ ] **Step 1: Create BlockHero**

```vue
<template>
  <section class="relative flex items-center justify-center min-h-[60vh] bg-gray-900 text-white overflow-hidden">
    <img
      v-if="bgUrl"
      :src="bgUrl"
      alt=""
      class="absolute inset-0 w-full h-full object-cover opacity-50"
    />
    <div class="relative z-10 text-center px-4 max-w-4xl">
      <h1 class="text-4xl md:text-5xl font-bold mb-4">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h1>
      <p
        v-if="subtitle"
        class="text-lg md:text-xl text-gray-300 mb-8"
      >
        {{ subtitle }}
      </p>
      <div v-if="content.buttons?.length" class="flex gap-4 justify-center flex-wrap">
        <UButton
          v-for="(btn, i) in content.buttons"
          :key="i"
          :to="btn.link"
          :variant="btn.variant || 'solid'"
          size="lg"
        >
          {{ locale === 'zh' ? btn.label_zh : btn.label_en }}
        </UButton>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();
const { locale } = useI18n();
const config = useRuntimeConfig();

const subtitle = computed(() =>
  locale.value === 'zh'
    ? props.content.subtitle_zh
    : props.content.subtitle_en
);

const bgUrl = computed(() =>
  props.content.bg_image
    ? `${config.public.apiBase}/../media/${props.content.bg_image}`
    : null
);
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/blocks/BlockHero.vue
git commit -m "feat: add BlockHero component"
```

---

### Task 8: Create BlockRichtext component

**Files:**
- Create: `frontend/components/blocks/BlockRichtext.vue`

- [ ] **Step 1: Create BlockRichtext**

```vue
<template>
  <section class="py-16 px-4">
    <div class="max-w-4xl mx-auto prose dark:prose-invert max-w-none" v-html="html" />
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();
const { locale } = useI18n();

const html = computed(() =>
  locale.value === 'zh'
    ? props.content.html_content_zh || ''
    : props.content.html_content_en || ''
);
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/blocks/BlockRichtext.vue
git commit -m "feat: add BlockRichtext component"
```

---

### Task 9: Create BlockNewsList component

**Files:**
- Create: `frontend/components/blocks/BlockNewsList.vue`

- [ ] **Step 1: Create BlockNewsList**

```vue
<template>
  <section class="py-16 px-4 bg-gray-50 dark:bg-gray-900">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-10">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <UCard v-for="article in items" :key="article.id">
          <img
            v-if="content.show_image && article.cover_image_id"
            :src="`${apiBase}/../media/${article.cover_image_id}`"
            class="w-full h-48 object-cover rounded-t"
          />
          <template #header>
            <h3 class="text-lg font-semibold">
              {{ locale === 'zh' ? article.title_zh : article.title_en }}
            </h3>
          </template>
          <p class="text-gray-600 dark:text-gray-400 line-clamp-3">
            {{ locale === 'zh' ? article.summary_zh : article.summary_en }}
          </p>
          <template #footer>
            <div class="flex justify-between items-center">
              <span v-if="content.show_date" class="text-sm text-gray-500">
                {{ new Date(article.published_at).toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US') }}
              </span>
              <UButton :to="`/news/${article.id}`" variant="link" size="sm">
                {{ locale === 'zh' ? '阅读更多' : 'Read more' }}
              </UButton>
            </div>
          </template>
        </UCard>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();
const { locale } = useI18n();
const apiBase = useRuntimeConfig().public.apiBase;

const { data } = await useNewsList(1, props.content.count || 3);
const items = computed(() => data.value?.items || []);
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/blocks/BlockNewsList.vue
git commit -m "feat: add BlockNewsList component"
```

---

### Task 10: Create BlockFaq component

**Files:**
- Create: `frontend/components/blocks/BlockFaq.vue`

- [ ] **Step 1: Create BlockFaq**

```vue
<template>
  <section class="py-16 px-4">
    <div class="max-w-3xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-10">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <UAccordion :items="accordionItems" />
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();
const { locale } = useI18n();

const { data } = await useFaqs();

const accordionItems = computed(() =>
  (data.value || []).map((faq: any) => ({
    label: locale.value === 'zh' ? faq.question_zh : faq.question_en,
    content: locale.value === 'zh' ? faq.answer_zh : faq.answer_en,
  }))
);
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/blocks/BlockFaq.vue
git commit -m "feat: add BlockFaq component with Nuxt UI Accordion"
```

---

### Task 11: Create BlockContactForm component

**Files:**
- Create: `frontend/components/blocks/BlockContactForm.vue`

- [ ] **Step 1: Create BlockContactForm**

```vue
<template>
  <section class="py-16 px-4 bg-gray-50 dark:bg-gray-900">
    <div class="max-w-xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-10">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <UAlert
        v-if="success"
        color="green"
        :title="locale === 'zh' ? '提交成功' : 'Submitted successfully'"
        class="mb-4"
      />
      <UAlert
        v-if="error"
        color="red"
        :title="error"
        class="mb-4"
      />
      <form @submit.prevent="onSubmit" class="space-y-4">
        <UFormGroup
          v-if="showField('company_name')"
          :label="locale === 'zh' ? '公司名称' : 'Company Name'"
          required
        >
          <UInput v-model="form.company_name" />
        </UFormGroup>
        <UFormGroup
          v-if="showField('contact_name')"
          :label="locale === 'zh' ? '联系人' : 'Contact Name'"
          required
        >
          <UInput v-model="form.contact_name" />
        </UFormGroup>
        <UFormGroup
          v-if="showField('phone')"
          :label="locale === 'zh' ? '电话' : 'Phone'"
          required
        >
          <UInput v-model="form.phone" type="tel" />
        </UFormGroup>
        <UFormGroup
          v-if="showField('message')"
          :label="locale === 'zh' ? '留言' : 'Message'"
          required
        >
          <UTextarea v-model="form.message" :rows="4" />
        </UFormGroup>
        <UButton type="submit" :loading="loading" block size="lg">
          {{ locale === 'zh' ? content.submit_button_zh || '提交' : content.submit_button_en || 'Submit' }}
        </UButton>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  config: Record<string, any>;
  content: Record<string, any>;
}>();
const { locale } = useI18n();
const { submit, loading, error, success } = useInquiry();

const form = reactive({
  company_name: '',
  contact_name: '',
  phone: '',
  message: '',
});

const fields = computed(() => props.content.fields || ['company_name', 'contact_name', 'phone', 'message']);

const showField = (name: string) => fields.value.includes(name);

const onSubmit = async () => {
  await submit({ ...form });
};
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/blocks/BlockContactForm.vue
git commit -m "feat: add BlockContactForm component"
```

---

### Task 12: Create BlockProductCards component

**Files:**
- Create: `frontend/components/blocks/BlockProductCards.vue`

- [ ] **Step 1: Create BlockProductCards**

```vue
<template>
  <section class="py-16 px-4">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-10">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <UCard v-for="(card, i) in content.cards" :key="i">
          <img
            v-if="card.image"
            :src="card.image"
            class="w-full h-48 object-cover rounded-t"
          />
          <template #header>
            <h3 class="text-lg font-semibold">
              {{ locale === 'zh' ? card.title_zh : card.title_en }}
            </h3>
          </template>
          <p class="text-gray-600 dark:text-gray-400">
            {{ locale === 'zh' ? card.desc_zh : card.desc_en }}
          </p>
          <template v-if="card.link" #footer>
            <UButton :to="card.link" variant="link">
              {{ locale === 'zh' ? '了解更多' : 'Learn more' }}
            </UButton>
          </template>
        </UCard>
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/blocks/BlockProductCards.vue
git commit -m "feat: add BlockProductCards component"
```

---

### Task 13: Create BlockStatsCounter component

**Files:**
- Create: `frontend/components/blocks/BlockStatsCounter.vue`

- [ ] **Step 1: Create BlockStatsCounter**

```vue
<template>
  <section class="py-16 px-4 bg-gray-900 text-white">
    <div class="max-w-5xl mx-auto">
      <h2 class="text-3xl font-bold text-center mb-10">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
        <div v-for="(item, i) in content.items" :key="i">
          <div class="text-4xl font-bold mb-2">{{ item.value }}</div>
          <div class="text-gray-400 text-sm">
            {{ locale === 'zh' ? item.label_zh : item.label_en }}
          </div>
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/blocks/BlockStatsCounter.vue
git commit -m "feat: add BlockStatsCounter component"
```

---

### Task 14: Create news index page

**Files:**
- Create: `frontend/pages/news/index.vue`
- Create: `frontend/pages/news/[id].vue`

- [ ] **Step 1: Create news list page**

`frontend/pages/news/index.vue`:

```vue
<template>
  <div class="py-16 px-4 max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-10 text-center">
      {{ locale === 'zh' ? '新闻中心' : 'News' }}
    </h1>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
      <UCard v-for="article in items" :key="article.id" class="cursor-pointer" @click="navigateTo(`/news/${article.id}`)">
        <img
          v-if="article.cover_image_id"
          :src="`${apiBase}/../media/${article.cover_image_id}`"
          class="w-full h-48 object-cover rounded-t"
        />
        <template #header>
          <h3 class="text-lg font-semibold">
            {{ locale === 'zh' ? article.title_zh : article.title_en }}
          </h3>
        </template>
        <p class="text-gray-600 dark:text-gray-400 line-clamp-3">
          {{ locale === 'zh' ? article.summary_zh : article.summary_en }}
        </p>
        <template #footer>
          <span class="text-sm text-gray-500">
            {{ new Date(article.published_at).toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US') }}
          </span>
        </template>
      </UCard>
    </div>

    <div v-if="!items.length" class="text-center text-gray-500 py-20">
      {{ locale === 'zh' ? '暂无新闻' : 'No news yet' }}
    </div>

    <div v-if="total > size" class="flex justify-center gap-2">
      <UButton
        v-for="p in totalPages"
        :key="p"
        :variant="p === currentPage ? 'solid' : 'outline'"
        @click="goToPage(p)"
      >
        {{ p }}
      </UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
const { locale } = useI18n();
const apiBase = useRuntimeConfig().public.apiBase;
const route = useRoute();
const currentPage = ref(Number(route.query.page) || 1);
const size = 9;

const { data, refresh } = await useNewsList(currentPage.value, size);
const items = computed(() => data.value?.items || []);
const total = computed(() => data.value?.total || 0);
const totalPages = computed(() => Math.ceil(total.value / size));

const goToPage = (p: number) => {
  currentPage.value = p;
  refresh();
};
</script>
```

- [ ] **Step 2: Create news detail page**

`frontend/pages/news/[id].vue`:

```vue
<template>
  <article v-if="article" class="py-16 px-4 max-w-3xl mx-auto">
    <img
      v-if="article.cover_image_id"
      :src="`${apiBase}/../media/${article.cover_image_id}`"
      class="w-full max-h-96 object-cover rounded-lg mb-8"
    />
    <h1 class="text-3xl font-bold mb-4">
      {{ locale === 'zh' ? article.title_zh : article.title_en }}
    </h1>
    <p class="text-gray-500 mb-8">
      {{ new Date(article.published_at).toLocaleDateString(locale === 'zh' ? 'zh-CN' : 'en-US') }}
    </p>
    <div
      class="prose dark:prose-invert max-w-none"
      v-html="locale === 'zh' ? article.content_zh : article.content_en"
    />
    <div class="mt-10">
      <UButton to="/news" variant="outline">
        {{ locale === 'zh' ? '返回新闻列表' : 'Back to News' }}
      </UButton>
    </div>
  </article>

  <div v-else-if="error" class="py-20 text-center text-gray-500">
    {{ locale === 'zh' ? '文章未找到' : 'Article not found' }}
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const { locale } = useI18n();
const apiBase = useRuntimeConfig().public.apiBase;

const { article, error } = await useNewsArticle(Number(route.params.id));
</script>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/pages/news/
git commit -m "feat: add news list and detail pages"
```

---

### Task 15: Create FAQ page

**Files:**
- Create: `frontend/pages/faq.vue`

- [ ] **Step 1: Create FAQ page**

```vue
<template>
  <section class="py-16 px-4 max-w-3xl mx-auto">
    <h1 class="text-3xl font-bold text-center mb-10">
      {{ locale === 'zh' ? '常见问题' : 'FAQ' }}
    </h1>

    <UAccordion v-if="faqs.length" :items="accordionItems" />

    <p v-else class="text-center text-gray-500 py-20">
      {{ locale === 'zh' ? '暂无常见问题' : 'No FAQs yet' }}
    </p>
  </section>
</template>

<script setup lang="ts">
const { locale } = useI18n();
const { data } = await useFaqs();
const faqs = computed(() => data.value || []);

const accordionItems = computed(() =>
  faqs.value.map((faq: any) => ({
    label: locale.value === 'zh' ? faq.question_zh : faq.question_en,
    content: locale.value === 'zh' ? faq.answer_zh : faq.answer_en,
  }))
);
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/pages/faq.vue
git commit -m "feat: add FAQ page with Nuxt UI Accordion"
```

---

### Task 16: Create contact page

**Files:**
- Create: `frontend/pages/contact.vue`

- [ ] **Step 1: Create contact page**

```vue
<template>
  <section class="py-16 px-4 max-w-xl mx-auto">
    <h1 class="text-3xl font-bold text-center mb-10">
      {{ locale === 'zh' ? '联系我们' : 'Contact Us' }}
    </h1>

    <UAlert
      v-if="success"
      color="green"
      :title="locale === 'zh' ? '提交成功，我们会尽快联系您！' : 'Submitted! We will contact you soon.'"
      class="mb-4"
    />
    <UAlert v-if="error" color="red" :title="error" class="mb-4" />
    <UCard>
      <form @submit.prevent="onSubmit" class="space-y-4">
        <UFormGroup :label="locale === 'zh' ? '公司名称' : 'Company Name'" required>
          <UInput v-model="form.company_name" />
        </UFormGroup>
        <UFormGroup :label="locale === 'zh' ? '联系人' : 'Contact Name'" required>
          <UInput v-model="form.contact_name" />
        </UFormGroup>
        <UFormGroup :label="locale === 'zh' ? '电话' : 'Phone'" required>
          <UInput v-model="form.phone" type="tel" />
        </UFormGroup>
        <UFormGroup :label="locale === 'zh' ? '留言' : 'Message'" required>
          <UTextarea v-model="form.message" :rows="4" />
        </UFormGroup>
        <UButton type="submit" :loading="loading" block size="lg">
          {{ locale === 'zh' ? '提交' : 'Submit' }}
        </UButton>
      </form>
    </UCard>
  </section>
</template>

<script setup lang="ts">
const { locale } = useI18n();
const { submit, loading, error, success } = useInquiry();

const form = reactive({
  company_name: '',
  contact_name: '',
  phone: '',
  message: '',
});

const onSubmit = async () => {
  await submit({ ...form });
};
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/pages/contact.vue
git commit -m "feat: add contact page with inquiry form"
```

---

### Task 17: Create chat page

**Files:**
- Create: `frontend/pages/chat.vue`

- [ ] **Step 1: Create chat page**

```vue
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/pages/chat.vue
git commit -m "feat: add AI chat page with SSE streaming"
```

---

### Task 18: Verify end-to-end

- [ ] **Step 1: Start backend (if not running)**

```bash
cd backend && uv run uvicorn app.main:app --reload --port 8000
```

- [ ] **Step 2: Start frontend dev server**

```bash
cd frontend && pnpm dev
```

- [ ] **Step 3: Smoke test each page**

Visit and verify each loads without JS errors:
- `http://localhost:3000/` — homepage with blocks
- `http://localhost:3000/news` — news listing
- `http://localhost:3000/news/1` — news detail (may 404 if no data, check graceful)
- `http://localhost:3000/faq` — FAQ page
- `http://localhost:3000/contact` — contact form
- `http://localhost:3000/chat` — chat page

- [ ] **Step 4: Commit any fixes if needed**
