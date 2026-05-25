<template>
  <div class="admin-shell min-h-screen flex" style="background: linear-gradient(170deg, #ffffff 0%, #f0fdf6 35%, #fafeff 65%, #ffffff 100%); color: #1e293b;">
    <!-- Left accent line -->
    <div class="flex-shrink-0 w-px" style="background: linear-gradient(180deg, #059669, #0284c7);"></div>

    <div class="flex-1 flex flex-col">
      <!-- Top bar -->
      <header class="flex items-center justify-between px-8 py-4" style="border-bottom: 1px solid rgba(5,150,105,0.08);">
        <div class="flex items-center gap-3">
          <div class="w-2 h-2 rounded-full" style="background: #059669; box-shadow: 0 0 6px rgba(5,150,105,0.4);"></div>
          <NuxtLink to="/admin" class="text-[13px] font-medium tracking-wide no-underline" style="color: #64748b;">
            GWEB ADMIN
          </NuxtLink>
        </div>
        <div v-if="token" class="flex items-center gap-4">
          <span class="text-[12px]" style="color: #94a3b8;">admin</span>
          <button
            @click="doLogout"
            class="text-[12px] border-none cursor-pointer transition-colors px-3 py-1.5 rounded"
            style="background: transparent; color: #64748b;"
          >
            退出
          </button>
        </div>
      </header>

      <main class="flex-1">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const token = ref<string | null>(null);
const router = useRouter();

if (import.meta.client) {
  token.value = localStorage.getItem('admin_token');
}

const doLogout = () => {
  localStorage.removeItem('admin_token');
  router.push('/admin/login');
};
</script>
