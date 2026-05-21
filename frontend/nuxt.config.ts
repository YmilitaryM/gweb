export default defineNuxtConfig({
  compatibilityDate: '2026-05-21',
  devtools: { enabled: true },
  ssr: true,
  modules: ['@nuxtjs/i18n', '@nuxt/image'],
  i18n: {
    locales: ['zh', 'en'],
    defaultLocale: 'zh',
    strategy: 'prefix_except_default',
  },
  image: { domains: ['localhost'] },
  routeRules: {
    '/': { prerender: true },
    '/about': { prerender: true },
    '/products': { prerender: true },
    '/solutions': { prerender: true },
    '/contact': { prerender: true },
    '/news': { isr: 300 },
    '/news/**': { isr: 300 },
    '/chat': { ssr: false },
  },
  runtimeConfig: {
    public: { apiBase: 'http://localhost:8000/api/v1' },
  },
});
