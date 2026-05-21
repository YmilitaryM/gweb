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
