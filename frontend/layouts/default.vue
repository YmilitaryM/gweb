<template>
  <div
    class="site min-h-screen"
    style="background: linear-gradient(170deg, #ffffff 0%, #f0fdf6 35%, #fafeff 65%, #ffffff 100%)"
  >
    <!-- Decorative flow curves -->
    <svg
      class="fixed inset-0 w-full h-full pointer-events-none -z-10"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M0,120 C200,90 300,170 500,120 C650,80 700,150 800,130"
        fill="none"
        stroke="rgba(5,150,105,0.07)"
        stroke-width="1.5"
        preserveAspectRatio="none"
      />
      <path
        d="M0,210 C180,240 350,180 500,210 C620,230 720,190 800,220"
        fill="none"
        stroke="rgba(5,150,105,0.04)"
        stroke-width="1"
        preserveAspectRatio="none"
      />
      <path
        d="M0,300 C250,330 400,250 550,300 C650,320 750,280 800,310"
        fill="none"
        stroke="rgba(59,130,246,0.03)"
        stroke-width="1"
        preserveAspectRatio="none"
      />
    </svg>

    <AppHeader />
    <main>
      <slot />
    </main>
    <AppFooter />

    <ChatFloatingButton @toggle="panel?.show()" />
    <ChatPanel ref="panel" />
  </div>
</template>

<script setup lang="ts">
import AppHeader from '~/components/layout/AppHeader.vue';
import AppFooter from '~/components/layout/AppFooter.vue';

const panel = ref<InstanceType<typeof ChatPanel> | null>(null);
</script>
