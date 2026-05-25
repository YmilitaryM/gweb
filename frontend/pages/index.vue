<template>
  <div>
    <BlockRenderer v-for="block in page?.blocks" :key="block.id" :block="block" />
    <p v-if="!page" class="text-center py-20 text-gray-500">Loading...</p>
  </div>
</template>

<script setup lang="ts">
import BlockRenderer from '~/components/blocks/BlockRenderer.vue';
const { page } = await usePage('home');
</script>
