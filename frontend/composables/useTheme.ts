export const useTheme = () => {
  const config = useRuntimeConfig();
  const { data: theme } = useFetch(`${config.public.apiBase}/themes/active`, { lazy: true });

  watchEffect(() => {
    if (theme.value?.variables) {
      const root = document.documentElement;
      for (const [key, val] of Object.entries(theme.value.variables)) {
        root.style.setProperty(key, String(val));
      }
    }
  });

  return theme;
};
