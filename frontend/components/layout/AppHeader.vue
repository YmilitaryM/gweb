<template>
  <header class="site-header">
    <div class="header-inner">
      <a href="/" class="logo">GWEB</a>
      <nav>
        <ul>
          <li v-for="item in menu" :key="item.id">
            <a :href="item.link">{{ locale === 'zh' ? item.name_zh : item.name_en }}</a>
            <ul v-if="item.children?.length">
              <li v-for="child in item.children" :key="child.id">
                <a :href="child.link">{{ locale === 'zh' ? child.name_zh : child.name_en }}</a>
              </li>
            </ul>
          </li>
        </ul>
      </nav>
      <div class="lang-switch">
        <button @click="switchLang('zh')">中</button>
        <button @click="switchLang('en')">EN</button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
const { locale } = useI18n();
const config = useRuntimeConfig();
const { data: menu } = await useFetch(`${config.public.apiBase}/menus?location=header`);

function switchLang(lang: string) {
  locale.value = lang;
}
</script>
