export default defineNuxtConfig({
  compatibilityDate: '2026-05-21',
  devtools: { enabled: true },
  ssr: true,
  css: ['~/assets/css/main.css'],
  modules: ['@nuxtjs/i18n', '@nuxt/image', '@nuxt/ui'],
  i18n: {
    locales: ['zh', 'en'],
    defaultLocale: 'zh',
    strategy: 'prefix_except_default',
    bundle: {
      optimizeTranslationDirective: false,
    },
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
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '/api/v1',
      mediaBase: process.env.NUXT_PUBLIC_MEDIA_BASE || '',
    },
  },
});
