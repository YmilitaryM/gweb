<template>
  <div class="page-dynamic">
    <BlockRenderer v-for="block in page?.blocks" :key="block.id" :block="block" />
    <p v-if="!page" class="loading">Loading...</p>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const { page } = await usePage(route.params.slug as string);
</script>
