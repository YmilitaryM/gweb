<template>
  <div class="p-8">
    <div class="mb-8">
      <h2 class="text-xl font-light text-white tracking-tight mb-1">控制台</h2>
      <p class="text-[13px]" style="color: rgba(255,255,255,0.25);">欢迎回来</p>
    </div>

    <!-- Quick stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div
        v-for="card in stats"
        :key="card.label"
        class="rounded-xl p-5"
        style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);"
      >
        <div class="text-[11px] tracking-wider uppercase mb-2" style="color: rgba(255,255,255,0.25);">
          {{ card.label }}
        </div>
        <div class="text-2xl font-light text-white tracking-tight" style="font-variant-numeric: tabular-nums;">
          {{ card.value }}
        </div>
      </div>
    </div>

    <!-- Quick links -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <NuxtLink
        v-for="link in links"
        :key="link.to"
        :to="link.to"
        class="rounded-xl p-5 no-underline transition-all duration-200 hover:translate-y-[-1px]"
        style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);"
      >
        <div class="text-[13px] font-medium text-white mb-1">{{ link.label }}</div>
        <div class="text-[12px]" style="color: rgba(255,255,255,0.25);">{{ link.desc }}</div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['admin-auth'],
});

const config = useRuntimeConfig();
const apiBase = config.public.apiBase as string;

const getHeaders = () => {
  const token = import.meta.client ? localStorage.getItem('admin_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

const pageCount = ref<number | null>(null);
const newsCount = ref<number | null>(null);
const inquiryCount = ref<number | null>(null);

const stats = computed(() => [
  { label: '页面', value: pageCount.value !== null ? String(pageCount.value) : '—' },
  { label: '新闻', value: newsCount.value !== null ? String(newsCount.value) : '—' },
  { label: '咨询', value: inquiryCount.value !== null ? String(inquiryCount.value) : '—' },
]);

onMounted(async () => {
  try {
    const pages = await $fetch<any[]>(`${apiBase}/admin/pages`, { headers: getHeaders() });
    pageCount.value = Array.isArray(pages) ? pages.length : 0;
  } catch {}
  try {
    const newsData = await $fetch<{ total: number }>(`${apiBase}/admin/news?page=1&size=1`, { headers: getHeaders() });
    newsCount.value = newsData.total;
  } catch {}
  try {
    const inquiryData = await $fetch<{ total: number }>(`${apiBase}/admin/inquiries?page=1&size=1`, { headers: getHeaders() });
    inquiryCount.value = inquiryData.total;
  } catch {}
});

const links = [
  { to: '/admin/pages', label: '页面管理', desc: '编辑网站页面和内容区块' },
  { to: '/admin/news', label: '新闻管理', desc: '发布和管理新闻文章' },
  { to: '/admin/media', label: '媒体管理', desc: '上传和管理图片、视频等媒体资源' },
  { to: '/admin/menus', label: '菜单管理', desc: '配置导航菜单结构' },
  { to: '/admin/users', label: '用户管理', desc: '管理后台管理员和编辑者账号' },
  { to: '/admin/inquiries', label: '咨询管理', desc: '查看用户提交的咨询' },
  { to: '/admin/audit-logs', label: '审计日志', desc: '查看管理员操作记录' },
  { to: '/admin/settings', label: '系统设置', desc: '配置 LLM、站点信息等系统参数' },
];
</script>
