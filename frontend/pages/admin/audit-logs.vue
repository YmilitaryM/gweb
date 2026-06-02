<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: #94a3b8;">
      &larr; 返回控制台
    </NuxtLink>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light tracking-tight mb-1" style="color: #1e293b;">审计日志</h2>
        <p class="text-[13px]" style="color: #94a3b8;">查看管理员和编辑者的操作记录</p>
      </div>
      <button
        @click="exportCsv"
        class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all duration-200 hover:translate-y-[-1px]"
        style="background: linear-gradient(135deg, #2563eb, #1d4ed8); box-shadow: 0 2px 12px rgba(37,99,235,0.2);"
      >
        导出 CSV
      </button>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-3 mb-5">
      <select v-model="filters.action" @change="page = 1; fetchLogs()" class="py-2 px-3 text-[13px] outline-none rounded-lg appearance-none" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;">
        <option value="">全部操作</option>
        <option value="create">创建</option>
        <option value="update">编辑</option>
        <option value="delete">删除</option>
      </select>
      <select v-model="filters.resource_type" @change="page = 1; fetchLogs()" class="py-2 px-3 text-[13px] outline-none rounded-lg appearance-none" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;">
        <option value="">全部资源</option>
        <option value="news">新闻</option>
        <option value="page">页面</option>
        <option value="media">媒体</option>
        <option value="menu">菜单</option>
        <option value="user">用户</option>
        <option value="setting">设置</option>
        <option value="inquiry">咨询</option>
        <option value="block">区块</option>
      </select>
      <input v-model="filters.start_date" type="date" @change="page = 1; fetchLogs()" class="py-2 px-3 text-[13px] outline-none rounded-lg" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;" />
      <span class="text-[12px]" style="color: #94a3b8;">至</span>
      <input v-model="filters.end_date" type="date" @change="page = 1; fetchLogs()" class="py-2 px-3 text-[13px] outline-none rounded-lg" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;" />
    </div>

    <div v-if="loading" class="text-[13px] py-12 text-center" style="color: #94a3b8;">加载中...</div>

    <div
      v-else-if="error"
      class="mb-6 px-4 py-3 rounded-lg text-[13px]"
      style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;"
    >
      {{ error }}
    </div>

    <template v-else>
      <div v-if="logs.length === 0" class="text-[13px] py-12 text-center" style="color: #94a3b8;">
        暂无日志
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="log in logs"
          :key="log.id"
          class="flex items-center justify-between px-5 py-3 rounded-xl cursor-pointer transition-colors"
          style="background: #ffffff; border: 1px solid #dbeafe;"
          @click="detail = log"
        >
          <div class="flex items-center gap-5 flex-1 min-w-0">
            <span class="text-[12px] flex-shrink-0 w-36" style="color: #64748b; font-variant-numeric: tabular-nums;">
              {{ new Date(log.created_at).toLocaleString('zh-CN') }}
            </span>
            <span class="text-[13px] flex-shrink-0 w-20" style="color: #1e293b;">{{ log.username }}</span>
            <span
              class="text-[11px] px-2 py-0.5 rounded-full flex-shrink-0 w-12 text-center"
              :style="actionStyle(log.action)"
            >
              {{ actionLabel(log.action) }}
            </span>
            <span class="text-[12px] flex-shrink-0 w-16" style="color: #94a3b8;">{{ resourceLabel(log.resource_type) }}</span>
            <span class="text-[13px] truncate" style="color: #475569;">{{ log.resource_name || '—' }}</span>
          </div>
          <span class="text-[11px] flex-shrink-0 ml-4" style="color: #94a3b8;">{{ log.ip_address || '' }}</span>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
        <button
          v-for="p in totalPages"
          :key="p"
          @click="page = p; fetchLogs()"
          class="text-[12px] border-none cursor-pointer w-8 h-8 rounded-lg transition-colors"
          :style="p === page ? 'background: rgba(37,99,235,0.15); color: #60a5fa;' : 'background: #f1f5f9; color: #94a3b8;'"
        >
          {{ p }}
        </button>
      </div>
    </template>

    <!-- Detail Modal -->
    <div
      v-if="detail"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
      @click.self="detail = null"
    >
      <div
        class="rounded-2xl p-6 w-full max-w-lg mx-4"
        style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.15);"
      >
        <h3 class="text-[15px] font-medium mb-5" style="color: #1e293b;">操作详情</h3>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <div class="text-[11px] tracking-wider uppercase mb-1" style="color: #94a3b8;">操作用户</div>
              <div class="text-[14px]" style="color: #1e293b;">{{ detail.username }}</div>
            </div>
            <div>
              <div class="text-[11px] tracking-wider uppercase mb-1" style="color: #94a3b8;">操作类型</div>
              <div class="text-[14px]" style="color: #1e293b;">{{ actionLabel(detail.action) }}</div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <div class="text-[11px] tracking-wider uppercase mb-1" style="color: #94a3b8;">资源类型</div>
              <div class="text-[14px]" style="color: #1e293b;">{{ resourceLabel(detail.resource_type) }}</div>
            </div>
            <div>
              <div class="text-[11px] tracking-wider uppercase mb-1" style="color: #94a3b8;">资源名称</div>
              <div class="text-[14px]" style="color: #1e293b;">{{ detail.resource_name || '—' }}</div>
            </div>
          </div>
          <div>
            <div class="text-[11px] tracking-wider uppercase mb-1" style="color: #94a3b8;">操作时间</div>
            <div class="text-[14px]" style="color: #1e293b;">{{ new Date(detail.created_at).toLocaleString('zh-CN') }}</div>
          </div>
          <div v-if="detail.ip_address">
            <div class="text-[11px] tracking-wider uppercase mb-1" style="color: #94a3b8;">IP 地址</div>
            <div class="text-[14px]" style="color: #1e293b;">{{ detail.ip_address }}</div>
          </div>
          <div v-if="detail.detail">
            <div class="text-[11px] tracking-wider uppercase mb-1" style="color: #94a3b8;">变更详情</div>
            <pre class="text-[13px] leading-relaxed whitespace-pre-wrap font-mono p-3 rounded-lg" style="background: #f8fafc; color: #1e293b;">{{ JSON.stringify(detail.detail, null, 2) }}</pre>
          </div>
        </div>
        <div class="flex justify-end pt-5 mt-2" style="border-top: 1px solid #e5e7eb;">
          <button
            @click="detail = null"
            class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg"
            style="color: #64748b; background: #f1f5f9;"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['admin-auth'] });

const { api, apiBase, getHeaders } = useAdminApi();

interface AuditLog {
  id: number;
  user_id: number;
  username: string;
  action: string;
  resource_type: string;
  resource_id: number | null;
  resource_name: string | null;
  detail: Record<string, any> | null;
  ip_address: string | null;
  created_at: string;
}

const logs = ref<AuditLog[]>([]);
const loading = ref(true);
const error = ref('');
const page = ref(1);
const totalPages = ref(1);
const detail = ref<AuditLog | null>(null);

const filters = ref({
  action: '',
  resource_type: '',
  start_date: '',
  end_date: '',
});

const actionLabel = (a: string) => {
  const map: Record<string, string> = { create: '创建', update: '编辑', delete: '删除' };
  return map[a] || a;
};

const actionStyle = (a: string) => {
  const colors: Record<string, string> = {
    create: 'background: rgba(37,99,235,0.12); color: #60a5fa;',
    update: 'background: rgba(2,132,199,0.12); color: #38bdf8;',
    delete: 'background: rgba(239,68,68,0.12); color: #f87171;',
  };
  return colors[a] || colors.create;
};

const resourceLabel = (r: string) => {
  const map: Record<string, string> = {
    news: '新闻', page: '页面', media: '媒体', menu: '菜单',
    user: '用户', setting: '设置', inquiry: '咨询', block: '区块',
  };
  return map[r] || r;
};

const buildParams = () => {
  const params: Record<string, any> = { page: page.value, size: 20 };
  if (filters.value.action) params.action = filters.value.action;
  if (filters.value.resource_type) params.resource_type = filters.value.resource_type;
  if (filters.value.start_date) params.start_date = filters.value.start_date;
  if (filters.value.end_date) params.end_date = filters.value.end_date;
  return params;
};

const fetchLogs = async () => {
  loading.value = true;
  error.value = '';
  try {
    const params = buildParams();
    const qs = new URLSearchParams(params as any).toString();
    const data = await api<{ items: AuditLog[]; total: number; page: number; size: number }>(`/admin/audit-logs?${qs}`);
    logs.value = data.items;
    totalPages.value = Math.ceil(data.total / data.size);
  } catch (e: any) {
    error.value = e?.data?.detail || '加载日志失败';
  } finally {
    loading.value = false;
  }
};

const exportCsv = async () => {
  try {
    const params: Record<string, any> = {};
    if (filters.value.action) params.action = filters.value.action;
    if (filters.value.resource_type) params.resource_type = filters.value.resource_type;
    if (filters.value.start_date) params.start_date = filters.value.start_date;
    if (filters.value.end_date) params.end_date = filters.value.end_date;
    const qs = new URLSearchParams(params as any).toString();
    const resp = await fetch(`${apiBase}/admin/audit-logs/export?${qs}`, {
      headers: getHeaders(false),
    });
    if (resp.status === 401) {
      localStorage.removeItem('admin_token');
      navigateTo('/admin/login');
      return;
    }
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'audit_logs.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  } catch {}
};

onMounted(fetchLogs);
</script>
