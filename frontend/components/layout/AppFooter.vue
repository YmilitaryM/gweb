<template>
  <footer class="flex items-center justify-between px-8 py-5 border-t" style="border-color: rgba(5,150,105,0.04)">
    <nav class="flex gap-6">
      <NuxtLink
        v-for="item in menu"
        :key="item.id"
        :to="item.link"
        class="text-[13px] text-slate-500 hover:text-slate-700 transition-colors no-underline"
      >
        {{ locale === 'zh' ? item.name_zh : item.name_en }}
      </NuxtLink>
    </nav>
    <span class="text-xs text-slate-400">&copy; 2026 GWEB</span>
  </footer>
</template>

<script setup lang="ts">
const { locale } = useI18n();
const config = useRuntimeConfig();
const { data: menu } = await useFetch(`${config.public.apiBase}/menus?location=footer`);
</script>
