<template>
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-nav">
        <div v-for="item in menu" :key="item.id">
          <a :href="item.link">{{ locale === 'zh' ? item.name_zh : item.name_en }}</a>
        </div>
      </div>
      <p class="copyright">&copy; 2026 GWEB. All rights reserved.</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
const { locale } = useI18n();
const config = useRuntimeConfig();
const { data: menu } = await useFetch(`${config.public.apiBase}/menus?location=footer`);
</script>
