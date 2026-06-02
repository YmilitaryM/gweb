<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: #94a3b8;">
      &larr; 返回控制台
    </NuxtLink>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light tracking-tight mb-1" style="color: #1e293b">案例管理</h2>
        <p class="text-[13px]" style="color: #94a3b8;">管理服务案例</p>
      </div>
      <button
        @click="openCreate"
        class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all duration-200 hover:translate-y-[-1px]"
        style="background: linear-gradient(135deg, #2563eb, #1d4ed8); box-shadow: 0 2px 12px rgba(37,99,235,0.2);"
      >
        新建案例
      </button>
    </div>

    <!-- Category tabs -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button
        v-for="tab in categoryTabs"
        :key="tab.key"
        @click="selectedCategory = tab.key; page = 1; fetchCases()"
        class="text-[12px] border-none cursor-pointer px-4 py-1.5 rounded-full transition-colors"
        :style="selectedCategory === tab.key ? 'background: rgba(37,99,235,0.12); color: #60a5fa;' : 'background: #f1f5f9; color: #94a3b8;'"
      >
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="text-[13px] py-12 text-center" style="color: #94a3b8;">加载中...</div>

    <div v-else-if="error" class="mb-6 px-4 py-3 rounded-lg text-[13px]" style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;">
      {{ error }}
    </div>

    <template v-else>
      <div v-if="cases.length === 0" class="text-[13px] py-12 text-center" style="color: #94a3b8;">暂 无案例</div>
      <div v-else class="space-y-3">
        <div
          v-for="c in cases"
          :key="c.id"
          class="flex items-center justify-between px-5 py-4 rounded-xl"
          style="background: #ffffff; border: 1px solid #dbeafe;"
        >
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <img
              v-if="c.cover_image_id"
              :src="`${apiBase}/../../media/id/${c.cover_image_id}`"
              class="w-14 h-10 rounded-md object-cover flex-shrink-0"
            />
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-3">
                <span class="text-[14px] font-medium truncate" style="color: #1e293b">{{ c.name_zh }}</span>
                <span class="text-[12px] truncate" style="color: #94a3b8;">{{ c.name_en }}</span>
                <span class="text-[11px] px-2 py-0.5 rounded-full" :style="c.is_published ? 'background: rgba(37,99,235,0.12); color: #60a5fa;' : 'background: #f1f5f9; color: #94a3b8;'">{{ c.is_published ? '已发布' : '草稿' }}</span>
              </div>
              <div class="text-[12px] mt-0.5" style="color: #94a3b8;">
                {{ categoryLabel(c.category) }} &middot; 排序: {{ c.sort_order }} &middot; {{ formatDate(c.created_at) }}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0 ml-4">
            <button @click="openEdit(c)" class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors" style="color: #60a5fa; background: rgba(37,99,235,0.08);">编辑</button>
            <button @click="confirmDelete(c)" class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors" style="color: #f87171; background: rgba(239,68,68,0.08);">删除</button>
          </div>
        </div>
      </div>

      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
        <button
          v-for="p in totalPages"
          :key="p"
          @click="page = p; fetchCases()"
          class="text-[12px] border-none cursor-pointer w-8 h-8 rounded-lg transition-colors"
          :style="p === page ? 'background: rgba(37,99,235,0.15); color: #60a5fa;' : 'background: #f1f5f9; color: #94a3b8;'"
        >{{ p }}</button>
      </div>
    </template>

    <!-- Case Modal -->
    <div v-if="modalOpen" class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto py-10" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);" @click.self="modalOpen = false">
      <div class="rounded-2xl p-6 w-full max-w-3xl mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <h3 class="text-[15px] font-medium mb-5" style="color: #1e293b">{{ editing ? '编辑案例' : '新建案例' }}</h3>
        <form @submit.prevent="save" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">中文名称</label>
              <input v-model="form.name_zh" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文名称</label>
              <input v-model="form.name_en" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">分类</label>
              <select v-model="form.category" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;">
                <option v-for="cat in categoryOptions" :key="cat.key" :value="cat.key">{{ cat.label_zh }}</option>
              </select>
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">Slug</label>
              <input v-model="form.slug" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">排序</label>
              <input v-model.number="form.sort_order" type="number" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">封面图片</label>
            <AdminMediaPicker v-model="form.cover_image_id" />
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">中文简介</label>
              <textarea v-model="form.summary_zh" rows="2" class="w-full py-2.5 px-3 text-[13px] outline-none rounded-lg resize-y" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;"></textarea>
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文简介</label>
              <textarea v-model="form.summary_en" rows="2" class="w-full py-2.5 px-3 text-[13px] outline-none rounded-lg resize-y" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;"></textarea>
            </div>
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">中文详情</label>
            <AdminRichTextEditor v-model="form.content_zh" placeholder="输入中文详情..." />
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文详情</label>
            <AdminRichTextEditor v-model="form.content_en" placeholder="Enter English details..." />
          </div>
          <!-- Stats editor -->
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">统计数据</label>
            <div class="space-y-2">
              <div v-for="(stat, i) in form.stats" :key="i" class="flex gap-2 items-center">
                <input v-model="stat.label" placeholder="指标名" class="flex-1 py-2 px-3 text-[13px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
                <input v-model="stat.value" placeholder="数值" class="flex-1 py-2 px-3 text-[13px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
                <button type="button" @click="form.stats.splice(i, 1)" class="border-none cursor-pointer px-2 py-1 rounded text-[12px]" style="color: #f87171; background: rgba(239,68,68,0.08);">删除</button>
              </div>
              <button type="button" @click="form.stats.push({ label: '', value: '' })" class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg" style="color: #60a5fa; background: rgba(37,99,235,0.08);">+ 添加数据</button>
            </div>
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.is_published" type="checkbox" class="accent-blue-600" />
            <span class="text-[12px]" style="color: #64748b;">发布</span>
          </label>
          <div v-if="formError" class="text-[12px]" style="color: #f87171;">{{ formError }}</div>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="modalOpen = false" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">取消</button>
            <button type="submit" :disabled="saving" class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all disabled:opacity-40" style="background: linear-gradient(135deg, #2563eb, #1d4ed8);">{{ saving ? '保存中...' : '保存' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);" @click.self="deleteTarget = null">
      <div class="rounded-2xl p-6 w-full max-w-sm mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <p class="text-[14px] mb-1" style="color: #1e293b">确认删除</p>
        <p class="text-[12px] mb-5" style="color: #94a3b8;">确定要删除案例 "{{ deleteTarget.name_zh }}" 吗？</p>
        <div class="flex justify-end gap-3">
          <button @click="deleteTarget = null" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">取消</button>
          <button @click="doDelete" class="text-[13px] font-medium text-white border-none cursor-pointer px-4 py-2 rounded-lg" style="background: #ef4444;">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['admin-auth'] });

const { api, apiBase } = useAdminApi();

interface CaseStat {
  label: string;
  value: string;
}

interface CaseItem {
  id: number;
  name_zh: string;
  name_en: string;
  slug: string;
  cover_image_id: number | null;
  summary_zh: string;
  summary_en: string;
  content_zh: string;
  content_en: string;
  category: string;
  stats: CaseStat[] | null;
  sort_order: number;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

const categoryOptions = [
  { key: 'park', label_zh: '产业园区', label_en: 'Industrial Park' },
  { key: 'medical', label_zh: '医疗建筑', label_en: 'Medical' },
  { key: 'office', label_zh: '写字楼', label_en: 'Office' },
  { key: 'commercial', label_zh: '商业综合体', label_en: 'Commercial' },
];

const cases = ref<CaseItem[]>([]);
const loading = ref(true);
const error = ref('');
const page = ref(1);
const totalPages = ref(1);
const selectedCategory = ref('');

const categoryTabs = computed(() => {
  const tabs: { key: string; label: string }[] = [{ key: '', label: '全部' }];
  for (const c of categoryOptions) {
    tabs.push({ key: c.key, label: c.label_zh });
  }
  return tabs;
});

function categoryLabel(key: string): string {
  const cat = categoryOptions.find(c => c.key === key);
  return cat ? cat.label_zh : key;
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
}

const fetchCases = async () => {
  loading.value = true;
  error.value = '';
  try {
    const params = new URLSearchParams({ page: String(page.value), size: '20' });
    if (selectedCategory.value) params.set('category', selectedCategory.value);
    const data = await api<{ items: CaseItem[]; total: number; page: number; size: number }>(`/admin/cases?${params}`);
    cases.value = data.items;
    totalPages.value = Math.ceil(data.total / data.size);
  } catch (e: any) {
    error.value = e?.data?.detail || '加载案例列表失败';
  } finally {
    loading.value = false;
  }
};

const modalOpen = ref(false);
const saving = ref(false);
const formError = ref('');
const editing = ref<CaseItem | null>(null);
const form = ref({
  name_zh: '',
  name_en: '',
  slug: '',
  cover_image_id: null as number | null,
  summary_zh: '',
  summary_en: '',
  content_zh: '',
  content_en: '',
  category: 'park',
  stats: [] as CaseStat[],
  sort_order: 0,
  is_published: true,
});

const resetForm = () => {
  form.value = { name_zh: '', name_en: '', slug: '', cover_image_id: null, summary_zh: '', summary_en: '', content_zh: '', content_en: '', category: 'park', stats: [], sort_order: 0, is_published: true };
  formError.value = '';
};

const openCreate = () => {
  editing.value = null;
  resetForm();
  modalOpen.value = true;
};

const openEdit = (c: CaseItem) => {
  editing.value = c;
  form.value = {
    name_zh: c.name_zh,
    name_en: c.name_en,
    slug: c.slug,
    cover_image_id: c.cover_image_id,
    summary_zh: c.summary_zh || '',
    summary_en: c.summary_en || '',
    content_zh: c.content_zh || '',
    content_en: c.content_en || '',
    category: c.category || 'park',
    stats: c.stats ? c.stats.map(s => ({ ...s })) : [],
    sort_order: c.sort_order,
    is_published: c.is_published,
  };
  formError.value = '';
  modalOpen.value = true;
};

const save = async () => {
  if (!form.value.name_zh || !form.value.name_en || !form.value.slug) {
    formError.value = '请填写所有必填字段';
    return;
  }
  saving.value = true;
  formError.value = '';
  const body: any = {
    ...form.value,
    stats: form.value.stats.length > 0 ? form.value.stats : null,
  };
  try {
    if (editing.value) {
      await api(`/admin/cases/${editing.value.id}`, { method: 'PUT', body });
    } else {
      await api('/admin/cases', { method: 'POST', body });
    }
    modalOpen.value = false;
    await fetchCases();
  } catch (e: any) {
    formError.value = e?.data?.detail || '保存失败';
  } finally {
    saving.value = false;
  }
};

const deleteTarget = ref<CaseItem | null>(null);
const confirmDelete = (c: CaseItem) => { deleteTarget.value = c; };
const doDelete = async () => {
  if (!deleteTarget.value) return;
  try {
    await api(`/admin/cases/${deleteTarget.value.id}`, { method: 'DELETE' });
    deleteTarget.value = null;
    await fetchCases();
  } catch {}
};

onMounted(async () => {
  await fetchCases();
});
</script>
