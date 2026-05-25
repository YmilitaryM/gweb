export const useAdminApi = () => {
  const config = useRuntimeConfig();
  const apiBase = config.public.apiBase as string;
  const router = useRouter();

  const getHeaders = (json = true) => {
    const token = import.meta.client ? localStorage.getItem('admin_token') : null;
    const h: Record<string, string> = {};
    if (json) h['Content-Type'] = 'application/json';
    if (token) h['Authorization'] = `Bearer ${token}`;
    return h;
  };

  const api = async (url: string, opts: any = {}) => {
    try {
      const isFormData = opts.body instanceof FormData;
      const useJson = !isFormData;
      const mergedHeaders = { ...getHeaders(useJson), ...(opts.headers || {}) };
      return await $fetch(`${apiBase}${url}`, { ...opts, headers: mergedHeaders });
    } catch (e: any) {
      if (e?.response?.status === 401) {
        localStorage.removeItem('admin_token');
        router.push('/admin/login');
      }
      throw e;
    }
  };

  return { api, apiBase, getHeaders };
};
