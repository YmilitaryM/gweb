export const usePage = async (slug: string) => {
  const config = useRuntimeConfig();
  const { data, error } = await useFetch(`${config.public.apiBase}/pages/${slug}`);
  return { page: data.value, error: error.value };
};
