<template>
  <section class="py-16 px-4">
    <div class="max-w-xl mx-auto">
      <h2 class="text-3xl font-light text-center mb-10 text-slate-800 tracking-tight">
        {{ locale === 'zh' ? content.title_zh : content.title_en }}
      </h2>

      <div
        v-if="success"
        class="mb-4 p-4 rounded-xl text-sm font-medium"
        style="background: rgba(5,150,105,0.06); color: #059669; border: 1px solid rgba(5,150,105,0.12);"
      >
        {{ locale === 'zh' ? '提交成功' : 'Submitted successfully' }}
      </div>
      <div
        v-if="error"
        class="mb-4 p-4 rounded-xl text-sm font-medium"
        style="background: rgba(239,68,68,0.06); color: #ef4444; border: 1px solid rgba(239,68,68,0.12);"
      >
        {{ error }}
      </div>

      <form @submit.prevent="onSubmit" class="space-y-5">
        <div v-if="showField('company_name')" class="flex flex-col gap-1.5">
          <label class="text-sm font-medium text-slate-600">
            {{ locale === 'zh' ? '公司名称' : 'Company Name' }} <span class="text-red-400">*</span>
          </label>
          <input
            v-model="form.company_name"
            required
            class="w-full px-4 py-2.5 rounded-xl border text-sm outline-none transition-all duration-200 focus:shadow-sm"
            style="border-color: rgba(5,150,105,0.15); background: rgba(255,255,255,0.8);"
            :placeholder="locale === 'zh' ? '请输入公司名称' : 'Enter company name'"
          />
        </div>

        <div v-if="showField('contact_name')" class="flex flex-col gap-1.5">
          <label class="text-sm font-medium text-slate-600">
            {{ locale === 'zh' ? '联系人' : 'Contact Name' }} <span class="text-red-400">*</span>
          </label>
          <input
            v-model="form.contact_name"
            required
            class="w-full px-4 py-2.5 rounded-xl border text-sm outline-none transition-all duration-200 focus:shadow-sm"
            style="border-color: rgba(5,150,105,0.15); background: rgba(255,255,255,0.8);"
            :placeholder="locale === 'zh' ? '请输入联系人姓名' : 'Enter contact name'"
          />
        </div>

        <div v-if="showField('phone')" class="flex flex-col gap-1.5">
          <label class="text-sm font-medium text-slate-600">
            {{ locale === 'zh' ? '电话' : 'Phone' }} <span class="text-red-400">*</span>
          </label>
          <input
            v-model="form.phone"
            type="tel"
            required
            class="w-full px-4 py-2.5 rounded-xl border text-sm outline-none transition-all duration-200 focus:shadow-sm"
            style="border-color: rgba(5,150,105,0.15); background: rgba(255,255,255,0.8);"
            :placeholder="locale === 'zh' ? '请输入电话号码' : 'Enter phone number'"
          />
        </div>

        <div v-if="showField('message')" class="flex flex-col gap-1.5">
          <label class="text-sm font-medium text-slate-600">
            {{ locale === 'zh' ? '留言' : 'Message' }} <span class="text-red-400">*</span>
          </label>
          <textarea
            v-model="form.message"
            :rows="4"
            required
            class="w-full px-4 py-2.5 rounded-xl border text-sm outline-none transition-all duration-200 focus:shadow-sm resize-none"
            style="border-color: rgba(5,150,105,0.15); background: rgba(255,255,255,0.8);"
            :placeholder="locale === 'zh' ? '请输入留言内容' : 'Enter your message'"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3 rounded-full text-sm font-medium text-white transition-all duration-200 hover:translate-y-[-1px] hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed border-none cursor-pointer"
          style="background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 2px 12px rgba(5,150,105,0.25);"
        >
          {{ loading
            ? (locale === 'zh' ? '提交中...' : 'Submitting...')
            : (locale === 'zh' ? (content.submit_button_zh || '提交') : (content.submit_button_en || 'Submit'))
          }}
        </button>
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
