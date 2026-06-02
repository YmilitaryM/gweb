<template>
  <div class="p-8">
    <div class="mb-8">
      <h2 class="text-xl font-light tracking-tight mb-1" style="color: #1e293b">控制台</h2>
      <p class="text-[13px]" style="color: #94a3b8;">欢迎回来</p>
    </div>

    <!-- Quick stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div
        v-for="card in stats"
        :key="card.label"
        class="rounded-xl p-5"
        style="background: #ffffff; border: 1px solid #dbeafe;"
      >
        <div class="text-[11px] tracking-wider uppercase mb-2" style="color: #94a3b8;">
          {{ card.label }}
        </div>
        <div class="text-2xl font-light tracking-tight" style="color: #1e293b; font-variant-numeric: tabular-nums;">
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
        style="background: #ffffff; border: 1px solid #dbeafe;"
      >
        <div class="text-[13px] font-medium mb-1" style="color: #1e293b">{{ link.label }}</div>
        <div class="text-[12px]" style="color: #94a3b8;">{{ link.desc }}</div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['admin-auth'],
});

const { api, getHeaders } = useAdminApi();

const pageCount = ref<number | null>(null);
const newsCount = ref<number | null>(null);
const inquiryCount = ref<number | null>(null);
const productCount = ref<number | null>(null);

const stats = computed(() => [
  { label: '页面', value: pageCount.value !== null ? String(pageCount.value) : '—' },
  { label: '新闻', value: newsCount.value !== null ? String(newsCount.value) : '—' },
  { label: '咨询', value: inquiryCount.value !== null ? String(inquiryCount.value) : '—' },
  { label: '产品', value: productCount.value !== null ? String(productCount.value) : '—' },
]);

onMounted(async () => {
  try {
    const pages = await api<any[]>('/admin/pages');
    pageCount.value = Array.isArray(pages) ? pages.length : 0;
  } catch {}
  try {
    const newsData = await api<{ total: number }>('/admin/news?page=1&size=1');
    newsCount.value = newsData.total;
  } catch {}
  try {
    const inquiryData = await api<{ total: number }>('/admin/inquiries?page=1&size=1');
    inquiryCount.value = inquiryData.total;
  } catch {}
  try {
    const productStats = await api<{ product_count: number; category_count: number }>('/admin/product-stats');
    productCount.value = productStats.product_count;
  } catch {}
});

const links = [
  { to: '/admin/pages', label: '页面管理', desc: '编辑网站页面和内容区块' },
  { to: '/admin/news', label: '新闻管理', desc: '发布和管理新闻文章' },
  { to: '/admin/products', label: '产品管理', desc: '管理产品信息和分类' },
  { to: '/admin/product-categories', label: '产品分类', desc: '管理产品分类' },
  { to: '/admin/media', label: '媒体管理', desc: '上传和管理图片、视频等媒体资源' },
  { to: '/admin/menus', label: '菜单管理', desc: '配置导航菜单结构' },
  { to: '/admin/users', label: '用户管理', desc: '管理后台管理员和编辑者账号' },
  { to: '/admin/inquiries', label: '咨询管理', desc: '查看用户提交的咨询' },
  { to: '/admin/audit-logs', label: '审计日志', desc: '查看管理员操作记录' },
  { to: '/admin/settings', label: '系统设置', desc: '配置 LLM、站点信息等系统参数' },
];
</script>
