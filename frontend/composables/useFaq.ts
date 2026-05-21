export const useFaqs = async () => {
  const config = useRuntimeConfig();
  const { data, error, refresh } = await useFetch(`${config.public.apiBase}/faqs`);
  return { data, error, refresh };
};
