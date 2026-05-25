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
defineProps<{ config: Record<string, any> }>();
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
