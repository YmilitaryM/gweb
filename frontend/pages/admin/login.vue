<template>
  <div class="flex h-full min-h-[calc(100vh-57px)]">
    <!-- Left: Branding & visual -->
    <div class="hidden lg:flex flex-1 flex-col justify-center items-center relative overflow-hidden">
      <div class="absolute inset-0 opacity-[0.04]"
        style="background-image: radial-gradient(circle, #2563eb 1px, transparent 1px); background-size: 24px 24px;">
      </div>

      <div class="relative">
        <div class="absolute -top-32 -left-32 w-64 h-64 rounded-full"
          style="border: 1px solid rgba(37,99,235,0.08);"></div>
        <div class="absolute -top-24 -left-24 w-48 h-48 rounded-full"
          style="border: 1px solid rgba(2,132,199,0.06);"></div>
        <div class="relative w-32 h-32 flex items-center justify-center">
          <div class="w-16 h-16 rotate-45"
            style="border: 1px solid rgba(37,99,235,0.15);"></div>
          <div class="absolute w-2 h-2 rounded-full" style="background: #2563eb; box-shadow: 0 0 12px rgba(37,99,235,0.5);"></div>
        </div>
      </div>

      <div class="relative mt-16 text-center">
        <p class="text-[11px] tracking-[0.2em] uppercase" style="color: #94a3b8;">
          Smart Building Platform
        </p>
      </div>
    </div>

    <!-- Right: Login form -->
    <div class="flex-1 flex items-center justify-center px-8">
      <div class="w-full max-w-[360px]">
        <div class="mb-10">
          <h1 class="text-2xl font-light tracking-tight mb-2" style="color: #1e293b">登录管理后台</h1>
          <p class="text-[13px]" style="color: #94a3b8;">请输入管理员账号</p>
        </div>

        <div
          v-if="error"
          class="mb-6 px-4 py-3 rounded-lg text-[13px] flex items-center gap-2"
          style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;"
        >
          {{ error }}
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div class="space-y-1.5">
            <label class="text-[11px] tracking-wider uppercase" style="color: #94a3b8;">账号</label>
            <input
              v-model="username"
              type="text"
              autocomplete="username"
              class="w-full py-2.5 text-[15px] outline-none transition-colors duration-200"
              style="color: #1e293b; background: transparent; border: none; border-bottom: 1px solid #d1d5db;"
              :style="{ borderBottomColor: focused === 'username' ? '#2563eb' : '#d1d5db' }"
              @focus="focused = 'username'"
              @blur="focused = null"
              placeholder="admin"
            />
          </div>

          <div class="space-y-1.5">
            <label class="text-[11px] tracking-wider uppercase" style="color: #94a3b8;">密码</label>
            <input
              v-model="password"
              type="password"
              autocomplete="current-password"
              class="w-full py-2.5 text-[15px] outline-none transition-colors duration-200"
              style="color: #1e293b; background: transparent; border: none; border-bottom: 1px solid #d1d5db;"
              :style="{ borderBottomColor: focused === 'password' ? '#2563eb' : '#d1d5db' }"
              @focus="focused = 'password'"
              @blur="focused = null"
            />
          </div>

          <div class="pt-4">
            <button
              type="submit"
              :disabled="loading"
              class="w-full py-2.5 rounded-lg text-[14px] font-medium text-white border-none cursor-pointer transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed"
              style="background: linear-gradient(135deg, #2563eb, #1d4ed8);"
            >
              <span v-if="!loading">登 录</span>
              <span v-else class="flex items-center justify-center gap-2">
                <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                验证中
              </span>
            </button>
          </div>
        </form>

        <p class="mt-8 text-[11px] text-center" style="color: #cbd5e1;">GWEB CMS v1.0</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin' });

const config = useRuntimeConfig();
const router = useRouter();

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');
const focused = ref<string | null>(null);

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入账号和密码';
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    const data = await $fetch<{ access_token: string }>(
      `${config.public.apiBase}/admin/auth/login`,
      { method: 'POST', body: { username: username.value, password: password.value } }
    );
    localStorage.setItem('admin_token', data.access_token);
    router.push('/admin');
  } catch (e: any) {
    error.value = e?.data?.detail || '登录失败，请检查账号密码';
  } finally {
    loading.value = false;
  }
};
</script>
