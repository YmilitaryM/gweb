<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: #94a3b8;">
      &larr; 返回控制台
    </NuxtLink>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light tracking-tight mb-1" style="color: #1e293b">产品分类</h2>
        <p class="text-[13px]" style="color: #94a3b8;">管理产品分类</p>
      </div>
      <button
        @click="openCreate"
        class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all duration-200 hover:translate-y-[-1px]"
        style="background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 2px 12px rgba(5,150,105,0.2);"
      >
        新建分类
      </button>
    </div>

    <div v-if="loading" class="text-[13px] py-12 text-center" style="color: #94a3b8;">加载中...</div>

    <div v-else-if="error" class="mb-6 px-4 py-3 rounded-lg text-[13px]" style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;">
      {{ error }}
    </div>

    <template v-else>
      <div v-if="categories.length === 0" class="text-[13px] py-12 text-center" style="color: #94a3b8;">暂无分类</div>
      <div v-else class="space-y-3">
        <div
          v-for="cat in categories"
          :key="cat.id"
          class="flex items-center justify-between px-5 py-4 rounded-xl"
          style="background: #ffffff; border: 1px solid #e8f5e9;"
        >
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-3">
              <span class="text-[14px] font-medium" style="color: #1e293b">{{ cat.name_zh }}</span>
              <span class="text-[12px]" style="color: #94a3b8;">{{ cat.name_en }}</span>
              <span class="text-[11px] px-2 py-0.5 rounded-full" :style="cat.is_published ? 'background: rgba(5,150,105,0.12); color: #34d399;' : 'background: #f1f5f9; color: #94a3b8;'">{{ cat.is_published ? '已发布' : '草稿' }}</span>
            </div>
            <div class="text-[12px] mt-0.5" style="color: #94a3b8;">
              {{ cat.slug }} &middot; 排序: {{ cat.sort_order }} &middot; {{ cat.product_count }} 个产品
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0 ml-4">
            <button @click="openEdit(cat)" class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors" style="color: #34d399; background: rgba(5,150,105,0.08);">编辑</button>
            <button @click="confirmDelete(cat)" class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors" style="color: #f87171; background: rgba(239,68,68,0.08);">删除</button>
          </div>
        </div>
      </div>
    </template>

    <!-- Modal -->
    <div v-if="modalOpen" class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto py-10" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);" @click.self="modalOpen = false">
      <div class="rounded-2xl p-6 w-full max-w-lg mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <h3 class="text-[15px] font-medium mb-5" style="color: #1e293b">{{ editing ? '编辑分类' : '新建分类' }}</h3>
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
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">Slug</label>
              <input v-model="form.slug" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">排序</label>
              <input v-model.number="form.sort_order" type="number" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.is_published" type="checkbox" class="accent-emerald-600" />
            <span class="text-[12px]" style="color: #64748b;">发布</span>
          </label>
          <div v-if="formError" class="text-[12px]" style="color: #f87171;">{{ formError }}</div>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="modalOpen = false" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">取消</button>
            <button type="submit" :disabled="saving" class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all disabled:opacity-40" style="background: linear-gradient(135deg, #059669, #10b981);">{{ saving ? '保存中...' : '保存' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);" @click.self="deleteTarget = null">
      <div class="rounded-2xl p-6 w-full max-w-sm mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <p class="text-[14px] mb-1" style="color: #1e293b">确认删除</p>
        <p class="text-[12px] mb-5" style="color: #94a3b8;">确定要删除分类 "{{ deleteTarget.name_zh }}" 吗？</p>
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

interface Category {
  id: number;
  name_zh: string;
  name_en: string;
  slug: string;
  sort_order: number;
  is_published: boolean;
  product_count: number;
}

const categories = ref<Category[]>([]);
const loading = ref(true);
const error = ref('');

const fetchCategories = async () => {
  loading.value = true;
  error.value = '';
  try {
    categories.value = await api<Category[]>('/admin/product-categories');
  } catch (e: any) {
    error.value = e?.data?.detail || '加载分类列表失败';
  } finally {
    loading.value = false;
  }
};

const modalOpen = ref(false);
const saving = ref(false);
const formError = ref('');
const editing = ref<Category | null>(null);
const form = ref({ name_zh: '', name_en: '', slug: '', sort_order: 0, is_published: true });

const openCreate = () => {
  editing.value = null;
  form.value = { name_zh: '', name_en: '', slug: '', sort_order: 0, is_published: true };
  formError.value = '';
  modalOpen.value = true;
};

const openEdit = (cat: Category) => {
  editing.value = cat;
  form.value = { name_zh: cat.name_zh, name_en: cat.name_en, slug: cat.slug, sort_order: cat.sort_order, is_published: cat.is_published };
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
  try {
    if (editing.value) {
      await api(`/admin/product-categories/${editing.value.id}`, { method: 'PUT', body: form.value });
    } else {
      await api('/admin/product-categories', { method: 'POST', body: form.value });
    }
    modalOpen.value = false;
    await fetchCategories();
  } catch (e: any) {
    formError.value = e?.data?.detail || '保存失败';
  } finally {
    saving.value = false;
  }
};

const deleteTarget = ref<Category | null>(null);
const confirmDelete = (cat: Category) => { deleteTarget.value = cat; };
const doDelete = async () => {
  if (!deleteTarget.value) return;
  try {
    await api(`/admin/product-categories/${deleteTarget.value.id}`, { method: 'DELETE' });
    deleteTarget.value = null;
    await fetchCategories();
  } catch (e: any) {
    error.value = e?.data?.detail || '删除失败';
    deleteTarget.value = null;
  }
};

onMounted(fetchCategories);
</script>
