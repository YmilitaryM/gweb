<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: #94a3b8;">
      &larr; 返回控制台
    </NuxtLink>
    <div class="mb-8">
      <h2 class="text-xl font-light tracking-tight mb-1" style="color: #1e293b;">咨询管理</h2>
      <p class="text-[13px]" style="color: #94a3b8;">查看用户提交的咨询</p>
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
      <div v-if="inquiries.length === 0" class="text-[13px] py-12 text-center" style="color: #94a3b8;">
        暂无咨询
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="inq in inquiries"
          :key="inq.id"
          class="flex items-center justify-between px-5 py-4 rounded-xl cursor-pointer transition-colors"
          :style="inq.is_read ? 'background: #ffffff; border: 1px solid #dbeafe;' : 'background: rgba(37,99,235,0.03); border: 1px solid rgba(37,99,235,0.06);'"
          @click="openDetail(inq)"
        >
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3">
              <span class="text-[14px] font-medium" style="color: #1e293b;">{{ inq.company_name }}</span>
              <span
                v-if="!inq.is_read"
                class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                style="background: #60a5fa;"
              ></span>
            </div>
            <div class="text-[12px] mt-0.5 truncate" style="color: #94a3b8;">
              {{ inq.contact_name }} &middot; {{ inq.phone }} &middot; {{ new Date(inq.created_at).toLocaleDateString('zh-CN') }}
            </div>
          </div>
          <button
            v-if="!inq.is_read"
            @click.stop="markRead(inq)"
            class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors flex-shrink-0 ml-4"
            style="color: #60a5fa; background: rgba(37,99,235,0.08);"
          >
            标记已读
          </button>
          <span
            v-else
            class="text-[12px] px-3 py-1.5 flex-shrink-0 ml-4"
            style="color: #cbd5e1;"
          >
            已读
          </span>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
        <button
          v-for="p in totalPages"
          :key="p"
          @click="page = p; fetchInquiries()"
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
        <h3 class="text-[15px] font-medium mb-5" style="color: #1e293b;">咨询详情</h3>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <div class="text-[11px] tracking-wider uppercase mb-1" style="color: #94a3b8;">公司名称</div>
              <div class="text-[14px]" style="color: #1e293b;">{{ detail.company_name }}</div>
            </div>
            <div>
              <div class="text-[11px] tracking-wider uppercase mb-1" style="color: #94a3b8;">联系人</div>
              <div class="text-[14px]" style="color: #1e293b;">{{ detail.contact_name }}</div>
            </div>
          </div>
          <div>
            <div class="text-[11px] tracking-wider uppercase mb-1" style="color: #94a3b8;">电话</div>
            <div class="text-[14px]" style="color: #1e293b;">{{ detail.phone }}</div>
          </div>
          <div>
            <div class="text-[11px] tracking-wider uppercase mb-1" style="color: #94a3b8;">留言内容</div>
            <div class="text-[14px] leading-relaxed whitespace-pre-wrap" style="color: #1e293b;">{{ detail.message }}</div>
          </div>
          <div>
            <div class="text-[11px] tracking-wider uppercase mb-1" style="color: #94a3b8;">提交时间</div>
            <div class="text-[13px]" style="color: #1e293b;">{{ new Date(detail.created_at).toLocaleString('zh-CN') }}</div>
          </div>
        </div>
        <div class="flex justify-between items-center pt-5 mt-2" style="border-top: 1px solid #e5e7eb;">
          <button
            v-if="!detail.is_read"
            @click="markRead(detail); detail.is_read = true"
            class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors"
            style="color: #60a5fa; background: rgba(37,99,235,0.08);"
          >
            标记已读
          </button>
          <span v-else></span>
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

const { api, getHeaders } = useAdminApi();

interface Inquiry {
  id: number;
  company_name: string;
  contact_name: string;
  phone: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

const inquiries = ref<Inquiry[]>([]);
const loading = ref(true);
const error = ref('');
const page = ref(1);
const totalPages = ref(1);

const fetchInquiries = async () => {
  loading.value = true;
  error.value = '';
  try {
    const data = await api<{ items: Inquiry[]; total: number; page: number; size: number }>(`/admin/inquiries?page=${page.value}&size=20`);
    inquiries.value = data.items;
    totalPages.value = Math.ceil(data.total / data.size);
  } catch (e: any) {
    error.value = e?.data?.detail || '加载咨询列表失败';
  } finally {
    loading.value = false;
  }
};

const detail = ref<Inquiry | null>(null);
const openDetail = (inq: Inquiry) => { detail.value = inq; };

const markRead = async (inq: Inquiry) => {
  try {
    await api(`/admin/inquiries/${inq.id}/read`, {
      method: 'PUT', 
    });
    inq.is_read = true;
    const idx = inquiries.value.findIndex(i => i.id === inq.id);
    if (idx >= 0) inquiries.value[idx]!.is_read = true;
  } catch {}
};

onMounted(fetchInquiries);
</script>
