<template>
  <div class="page-home">
    <BlockRenderer v-for="block in page?.blocks" :key="block.id" :block="block" />
    <p v-if="!page" class="loading">Loading...</p>
  </div>
</template>

<script setup lang="ts">
const { page } = await usePage('home');
</script>
