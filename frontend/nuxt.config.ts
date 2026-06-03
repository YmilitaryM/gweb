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
    '/chat': { ssr: false },
    '/admin/**': { ssr: false },
  },
  devServer: { port: 5177 },
  nitro: {
    devProxy: {
      '/api': { target: 'http://localhost:8002/api', changeOrigin: true },
      '/media': { target: 'http://localhost:8002/media', changeOrigin: true },
    },
  },
  runtimeConfig: {
    public: {
      apiBase: '/api/v1',
      mediaBase: '',
    },
  },
});
