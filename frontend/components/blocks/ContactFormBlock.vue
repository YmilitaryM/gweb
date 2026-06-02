<template>
  <section class="py-16 px-4 max-w-xl mx-auto">
    <h2 v-if="title" class="text-3xl font-extrabold text-center mb-4 text-slate-900">
      {{ title }}
    </h2>
    <p v-if="subtitle" class="text-center text-slate-500 mb-10">
      {{ subtitle }}
    </p>

    <!-- Success alert -->
    <div
      v-if="success"
      class="mb-6 p-4 rounded-xl bg-green-50 border border-green-200 text-green-700 text-sm"
    >
      {{ locale === 'zh' ? '提交成功，我们会尽快联系您！' : 'Submitted! We will contact you soon.' }}
    </div>

    <!-- Error alert -->
    <div
      v-if="error"
      class="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm"
    >
      {{ error }}
    </div>

    <!-- Form card -->
    <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-8">
      <form @submit.prevent="onSubmit" class="space-y-5">
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">
            {{ locale === 'zh' ? '公司名称' : 'Company Name' }}
            <span class="text-red-400">*</span>
          </label>
          <input
            v-model="form.company_name"
            type="text"
            required
            class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-500 transition"
            :placeholder="locale === 'zh' ? '请输入公司名称' : 'Enter company name'"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">
            {{ locale === 'zh' ? '联系人' : 'Contact Name' }}
            <span class="text-red-400">*</span>
          </label>
          <input
            v-model="form.contact_name"
            type="text"
            required
            class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-500 transition"
            :placeholder="locale === 'zh' ? '请输入联系人姓名' : 'Enter contact name'"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">
            {{ locale === 'zh' ? '电话' : 'Phone' }}
            <span class="text-red-400">*</span>
          </label>
          <input
            v-model="form.phone"
            type="tel"
            required
            class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-500 transition"
            :placeholder="locale === 'zh' ? '请输入电话号码' : 'Enter phone number'"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">
            {{ locale === 'zh' ? '留言' : 'Message' }}
            <span class="text-red-400">*</span>
          </label>
          <textarea
            v-model="form.message"
            :rows="4"
            required
            class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-500 transition resize-none"
            :placeholder="locale === 'zh' ? '请输入您的需求或留言' : 'Enter your message'"
          ></textarea>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3 rounded-xl text-white font-semibold text-sm transition-all duration-200 flex items-center justify-center gap-2"
          :class="loading
            ? 'bg-brand-400 cursor-not-allowed'
            : 'bg-brand-600 hover:bg-brand-700 active:scale-[0.98] shadow-md shadow-brand-600/20'"
        >
          <span v-if="loading" class="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          {{ loading ? (locale === 'zh' ? '提交中...' : 'Submitting...') : (locale === 'zh' ? '提交' : 'Submit') }}
        </button>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{ config: Record<string, any>; content?: Record<string, any> }>();
const { locale } = useI18n();
const { submit, loading, error, success } = useInquiry();

const title = computed(() => {
  if (!props.content) return null;
  return locale.value === 'zh'
    ? (props.content.title_zh || '联系我们')
    : (props.content.title_en || 'Contact Us');
});

const subtitle = computed(() => {
  if (!props.content) return null;
  return locale.value === 'zh'
    ? (props.content.subtitle_zh || '请填写以下表单，我们会尽快与您联系')
    : (props.content.subtitle_en || 'Fill out the form and we will contact you shortly');
});

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
