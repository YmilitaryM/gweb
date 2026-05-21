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
