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
