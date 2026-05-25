import { computed, unref, type MaybeRef } from 'vue'

export const useNewsList = (page: MaybeRef<number> = 1, size: MaybeRef<number> = 10, category?: MaybeRef<string | undefined>) => {
  const config = useRuntimeConfig();
  const url = computed(() => {
    const params = new URLSearchParams({ page: String(unref(page)), size: String(unref(size)) });
    const cat = category ? unref(category) : undefined;
    if (cat) params.set('category', cat);
    return `${config.public.apiBase}/news?${params}`;
  });
  const { data, error, refresh } = useFetch(url);
  return { data, error, refresh };
};

export const useNewsArticle = async (id: number) => {
  const config = useRuntimeConfig();
  const { data, error } = await useFetch(`${config.public.apiBase}/news/${id}`);
  return { article: data, error };
};
