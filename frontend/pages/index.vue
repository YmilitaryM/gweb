<template>
  <div class="page-home">
    <BlockRenderer v-for="block in page?.blocks" :key="block.id" :block="block" />
    <p v-if="!page" class="loading">Loading...</p>
  </div>
</template>

<script setup lang="ts">
import BlockRenderer from '~/components/blocks/BlockRenderer.vue';
const { page } = await usePage('home');
</script>
