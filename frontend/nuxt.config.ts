export default defineNuxtConfig({
  compatibilityDate: '2026-05-21',
  devtools: { enabled: true },
  ssr: true,
  css: ['~/assets/css/main.css'],
  modules: ['@nuxtjs/i18n', '@nuxt/image', '@nuxt/ui'],
  app: {
    head: {
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap' },
      ],
    },
  },
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
    '/faq': { isr: 300 },
    '/chat': { ssr: false },
    '/admin/**': { ssr: false },
  },
  devServer: { port: 5177 },
  runtimeConfig: {
    public: { apiBase: 'http://localhost:8002/api/v1' },
  },
});
