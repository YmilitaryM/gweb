<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: #94a3b8;">
      &larr; 返回控制台
    </NuxtLink>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light tracking-tight mb-1" style="color: #1e293b">产品管理</h2>
        <p class="text-[13px]" style="color: #94a3b8;">管理产品信息</p>
      </div>
      <button
        @click="openCreate"
        class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all duration-200 hover:translate-y-[-1px]"
        style="background: linear-gradient(135deg, #2563eb, #1d4ed8); box-shadow: 0 2px 12px rgba(37,99,235,0.2);"
      >
        新建产品
      </button>
    </div>

    <!-- Category tabs -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button
        v-for="tab in categoryTabs"
        :key="tab.id"
        @click="selectedCategoryId = tab.id; page = 1; fetchProducts()"
        class="text-[12px] border-none cursor-pointer px-4 py-1.5 rounded-full transition-colors"
        :style="selectedCategoryId === tab.id ? 'background: rgba(37,99,235,0.12); color: #60a5fa;' : 'background: #f1f5f9; color: #94a3b8;'"
      >
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="text-[13px] py-12 text-center" style="color: #94a3b8;">加载中...</div>

    <div v-else-if="error" class="mb-6 px-4 py-3 rounded-lg text-[13px]" style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;">
      {{ error }}
    </div>

    <template v-else>
      <div v-if="products.length === 0" class="text-[13px] py-12 text-center" style="color: #94a3b8;">暂无产品</div>
      <div v-else class="space-y-3">
        <div
          v-for="prod in products"
          :key="prod.id"
          class="flex items-center justify-between px-5 py-4 rounded-xl"
          style="background: #ffffff; border: 1px solid #dbeafe;"
        >
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <img
              v-if="prod.cover_image_id"
              :src="mediaUrl(prod.cover_image_id)"
              class="w-14 h-10 rounded-md object-cover flex-shrink-0"
            />
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-3">
                <span class="text-[14px] font-medium truncate" style="color: #1e293b">{{ prod.name_zh }}</span>
                <span class="text-[12px] truncate" style="color: #94a3b8;">{{ prod.name_en }}</span>
                <span class="text-[11px] px-2 py-0.5 rounded-full" :style="prod.is_published ? 'background: rgba(37,99,235,0.12); color: #60a5fa;' : 'background: #f1f5f9; color: #94a3b8;'">{{ prod.is_published ? '已发布' : '草稿' }}</span>
              </div>
              <div class="text-[12px] mt-0.5" style="color: #94a3b8;">
                {{ prod.category?.name_zh || '-' }} &middot; 排序: {{ prod.sort_order }}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0 ml-4">
            <button @click="openEdit(prod)" class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors" style="color: #60a5fa; background: rgba(37,99,235,0.08);">编辑</button>
            <button @click="confirmDelete(prod)" class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors" style="color: #f87171; background: rgba(239,68,68,0.08);">删除</button>
          </div>
        </div>
      </div>

      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
        <button
          v-for="p in totalPages"
          :key="p"
          @click="page = p; fetchProducts()"
          class="text-[12px] border-none cursor-pointer w-8 h-8 rounded-lg transition-colors"
          :style="p === page ? 'background: rgba(37,99,235,0.15); color: #60a5fa;' : 'background: #f1f5f9; color: #94a3b8;'"
        >{{ p }}</button>
      </div>
    </template>

    <!-- Product Modal -->
    <div v-if="modalOpen" class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto py-10" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);" @click.self="modalOpen = false">
      <div class="rounded-2xl p-6 w-full max-w-3xl mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <h3 class="text-[15px] font-medium mb-5" style="color: #1e293b">{{ editing ? '编辑产品' : '新建产品' }}</h3>
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
              <select v-model="form.category_id" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;">
                <option :value="0" disabled>选择分类</option>
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name_zh }}</option>
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
            <AdminRichTextEditor v-model="form.description_zh" placeholder="输入中文详情..." />
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文详情</label>
            <AdminRichTextEditor v-model="form.description_en" placeholder="Enter English details..." />
          </div>
          <!-- Specs editor -->
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">规格参数</label>
            <div class="space-y-2">
              <div v-for="(spec, i) in form.specs" :key="i" class="flex gap-2 items-center">
                <input v-model="spec.key" placeholder="参数名" class="flex-1 py-2 px-3 text-[13px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
                <input v-model="spec.value" placeholder="参数值" class="flex-1 py-2 px-3 text-[13px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
                <button type="button" @click="form.specs.splice(i, 1)" class="border-none cursor-pointer px-2 py-1 rounded text-[12px]" style="color: #f87171; background: rgba(239,68,68,0.08);">删除</button>
              </div>
              <button type="button" @click="form.specs.push({ key: '', value: '' })" class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg" style="color: #60a5fa; background: rgba(37,99,235,0.08);">+ 添加参数</button>
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
        <p class="text-[12px] mb-5" style="color: #94a3b8;">确定要删除产品 "{{ deleteTarget.name_zh }}" 吗？</p>
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

const { api } = useAdminApi();
const mediaUrl = useMediaUrl();

interface Category {
  id: number;
  name_zh: string;
  name_en: string;
  slug: string;
  sort_order: number;
  is_published: boolean;
}

interface ProductItem {
  id: number;
  category_id: number;
  name_zh: string;
  name_en: string;
  slug: string;
  cover_image_id: number | null;
  summary_zh: string;
  summary_en: string;
  description_zh: string;
  description_en: string;
  specs: { key: string; value: string }[] | null;
  images: number[] | null;
  sort_order: number;
  is_published: boolean;
  category: Category | null;
}

const products = ref<ProductItem[]>([]);
const categories = ref<Category[]>([]);
const loading = ref(true);
const error = ref('');
const page = ref(1);
const totalPages = ref(1);
const selectedCategoryId = ref<number | null>(null);

const categoryTabs = computed(() => {
  const tabs: { id: number | null; label: string }[] = [{ id: null, label: '全部' }];
  for (const c of categories.value) {
    tabs.push({ id: c.id, label: c.name_zh });
  }
  return tabs;
});

const fetchCategories = async () => {
  try {
    categories.value = await api<Category[]>('/admin/product-categories');
  } catch {}
};

const fetchProducts = async () => {
  loading.value = true;
  error.value = '';
  try {
    const params = new URLSearchParams({ page: String(page.value), size: '20' });
    if (selectedCategoryId.value) params.set('category_id', String(selectedCategoryId.value));
    const data = await api<{ items: ProductItem[]; total: number; page: number; size: number }>(`/admin/products?${params}`);
    products.value = data.items;
    totalPages.value = Math.ceil(data.total / data.size);
  } catch (e: any) {
    error.value = e?.data?.detail || '加载产品列表失败';
  } finally {
    loading.value = false;
  }
};

const modalOpen = ref(false);
const saving = ref(false);
const formError = ref('');
const editing = ref<ProductItem | null>(null);
const form = ref({
  category_id: 0,
  name_zh: '',
  name_en: '',
  slug: '',
  cover_image_id: null as number | null,
  summary_zh: '',
  summary_en: '',
  description_zh: '',
  description_en: '',
  specs: [] as { key: string; value: string }[],
  images: [] as number[],
  sort_order: 0,
  is_published: true,
});

const resetForm = () => {
  form.value = { category_id: 0, name_zh: '', name_en: '', slug: '', cover_image_id: null, summary_zh: '', summary_en: '', description_zh: '', description_en: '', specs: [], images: [], sort_order: 0, is_published: true };
  formError.value = '';
};

const openCreate = () => {
  editing.value = null;
  resetForm();
  modalOpen.value = true;
};

const openEdit = (prod: ProductItem) => {
  editing.value = prod;
  form.value = {
    category_id: prod.category_id,
    name_zh: prod.name_zh,
    name_en: prod.name_en,
    slug: prod.slug,
    cover_image_id: prod.cover_image_id,
    summary_zh: prod.summary_zh || '',
    summary_en: prod.summary_en || '',
    description_zh: prod.description_zh || '',
    description_en: prod.description_en || '',
    specs: prod.specs ? [...prod.specs] : [],
    images: prod.images ? [...prod.images] : [],
    sort_order: prod.sort_order,
    is_published: prod.is_published,
  };
  formError.value = '';
  modalOpen.value = true;
};

const save = async () => {
  if (!form.value.name_zh || !form.value.name_en || !form.value.slug || !form.value.category_id) {
    formError.value = '请填写所有必填字段';
    return;
  }
  saving.value = true;
  formError.value = '';
  const body: any = { ...form.value, specs: form.value.specs.length > 0 ? form.value.specs : null, images: form.value.images.length > 0 ? form.value.images : null };
  try {
    if (editing.value) {
      await api(`/admin/products/${editing.value.id}`, { method: 'PUT', body });
    } else {
      await api('/admin/products', { method: 'POST', body });
    }
    modalOpen.value = false;
    await fetchProducts();
  } catch (e: any) {
    formError.value = e?.data?.detail || '保存失败';
  } finally {
    saving.value = false;
  }
};

const deleteTarget = ref<ProductItem | null>(null);
const confirmDelete = (prod: ProductItem) => { deleteTarget.value = prod; };
const doDelete = async () => {
  if (!deleteTarget.value) return;
  try {
    await api(`/admin/products/${deleteTarget.value.id}`, { method: 'DELETE' });
    deleteTarget.value = null;
    await fetchProducts();
  } catch {}
};

onMounted(async () => {
  await fetchCategories();
  await fetchProducts();
});
</script>
