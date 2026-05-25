<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: #94a3b8;">
      &larr; 返回控制台
    </NuxtLink>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light tracking-tight mb-1" style="color: #1e293b;">菜单管理</h2>
        <p class="text-[13px]" style="color: #94a3b8;">配置导航菜单结构</p>
      </div>
      <button
        @click="openCreate(null)"
        class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all duration-200 hover:translate-y-[-1px]"
        style="background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 2px 12px rgba(5,150,105,0.2);"
      >
        新建菜单
      </button>
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
      <div v-if="menuTree.length === 0" class="text-[13px] py-12 text-center" style="color: #94a3b8;">
        暂无菜单
      </div>
      <div v-else class="space-y-1">
        <MenuNode
          v-for="node in menuTree"
          :key="node.id"
          :node="node"
          :depth="0"
          @edit="openEdit"
          @delete="confirmDelete"
          @add-child="openCreate"
        />
      </div>
    </template>

    <!-- Menu Modal -->
    <div
      v-if="modalOpen"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
      @click.self="modalOpen = false"
    >
      <div
        class="rounded-2xl p-6 w-full max-w-lg mx-4"
        style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);"
      >
        <h3 class="text-[15px] font-medium mb-5" style="color: #1e293b;">
          {{ editing ? '编辑菜单' : parentId ? '添加子菜单' : '新建菜单' }}
        </h3>
        <form @submit.prevent="save" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">中文名称</label>
              <input v-model="form.name_zh" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;" />
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文名称</label>
              <input v-model="form.name_en" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;" />
            </div>
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">关联页面</label>
            <select v-model="form.page_id" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg appearance-none" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;">
              <option :value="0">— 无关联 —</option>
              <option v-for="p in pageOptions" :key="p.id" :value="p.id">
                /{{ p.slug }} — {{ p.name_zh }} ({{ p.type }})
              </option>
            </select>
            <p v-if="selectedPageSlug" class="text-[11px] mt-1" style="color: #34d399;">
              链接: /{{ selectedPageSlug === 'home' ? '' : selectedPageSlug }}
            </p>
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">链接</label>
            <input v-model="form.link" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;" placeholder="/about" />
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">图标</label>
            <input v-model="form.icon" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;" placeholder="例如: home, info, mail" />
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">位置</label>
              <select v-model="form.location" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg appearance-none" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;">
                <option value="header">顶部导航</option>
                <option value="footer">底部导航</option>
              </select>
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">排序</label>
              <input v-model.number="form.order" type="number" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;" />
            </div>
            <div class="flex items-end pb-1">
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="form.is_visible" type="checkbox" class="accent-emerald-600" />
                <span class="text-[12px]" style="color: #64748b;">可见</span>
              </label>
            </div>
          </div>
          <div v-if="formError" class="text-[12px]" style="color: #f87171;">{{ formError }}</div>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="modalOpen = false" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">取消</button>
            <button type="submit" :disabled="saving" class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all disabled:opacity-40" style="background: linear-gradient(135deg, #059669, #10b981);">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div
      v-if="deleteTarget"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
      @click.self="deleteTarget = null"
    >
      <div class="rounded-2xl p-6 w-full max-w-sm mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <p class="text-[14px] mb-1" style="color: #1e293b;">确认删除</p>
        <p class="text-[12px] mb-5" style="color: #94a3b8;">确定要删除菜单 "{{ deleteTarget.name_zh }}" 吗？如有子菜单也将一并处理。</p>
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

const { api, getHeaders } = useAdminApi();

interface MenuNode {
  id: number;
  name_zh: string;
  name_en: string;
  link: string;
  page_id: number | null;
  page_slug: string | null;
  icon: string | null;
  order: number;
  is_visible: boolean;
  location: string;
  parent_id: number | null;
  children: MenuNode[];
}

const menuTree = ref<MenuNode[]>([]);
const loading = ref(true);
const error = ref('');

const fetchMenus = async () => {
  loading.value = true;
  error.value = '';
  try {
    menuTree.value = await api<MenuNode[]>('/menus');
  } catch (e: any) {
    error.value = e?.data?.detail || '加载菜单失败';
  } finally {
    loading.value = false;
  }
};

const modalOpen = ref(false);
const saving = ref(false);
const formError = ref('');
const editing = ref<MenuNode | null>(null);
const parentId = ref<number | null>(null);
const form = ref({
  name_zh: '', name_en: '', link: '', icon: '',
  order: 0, is_visible: true, location: 'header', page_id: 0,
});

interface PageOption { id: number; name_zh: string; slug: string; type: string; }
const pageOptions = ref<PageOption[]>([]);

const fetchPageOptions = async () => {
  try {
    const data = await api<any[]>('/pages');
    pageOptions.value = data.map((p: any) => ({ id: p.id, name_zh: p.name_zh, slug: p.slug, type: p.type }));
  } catch {}
};

const selectedPageSlug = computed(() => {
  if (!form.value.page_id || form.value.page_id === 0) return null;
  return pageOptions.value.find(p => p.id === form.value.page_id)?.slug || null;
});

const openCreate = (parent: MenuNode | null) => {
  editing.value = null;
  parentId.value = parent?.id || null;
  form.value = {
    name_zh: '', name_en: '', link: '', icon: '',
    order: 0, is_visible: true, location: parent?.location || 'header', page_id: 0,
  };
  formError.value = '';
  modalOpen.value = true;
};

const openEdit = (menu: MenuNode) => {
  editing.value = menu;
  parentId.value = null;
  form.value = {
    name_zh: menu.name_zh,
    name_en: menu.name_en,
    link: menu.link || '',
    icon: menu.icon || '',
    order: menu.order,
    is_visible: menu.is_visible,
    location: menu.location,
    page_id: menu.page_id || 0,
  };
  formError.value = '';
  modalOpen.value = true;
};

const save = async () => {
  if (!form.value.name_zh || !form.value.name_en) {
    formError.value = '请填写名称';
    return;
  }
  saving.value = true;
  formError.value = '';
  const body: any = { ...form.value };
  if (!body.page_id || body.page_id === 0) body.page_id = null;
  if (parentId.value && !editing.value) body.parent_id = parentId.value;
  try {
    if (editing.value) {
      await api(`/admin/menus/${editing.value.id}`, {
        method: 'PUT', body,
      });
    } else {
      await api(`/admin/menus`, {
        method: 'POST', body,
      });
    }
    modalOpen.value = false;
    await fetchMenus();
  } catch (e: any) {
    formError.value = e?.data?.detail || '保存失败';
  } finally {
    saving.value = false;
  }
};

const deleteTarget = ref<MenuNode | null>(null);
const confirmDelete = (menu: MenuNode) => { deleteTarget.value = menu; };
const doDelete = async () => {
  if (!deleteTarget.value) return;
  try {
    await api(`/admin/menus/${deleteTarget.value.id}`, {
      method: 'DELETE', 
    });
    deleteTarget.value = null;
    await fetchMenus();
  } catch {}
};

onMounted(() => { fetchMenus(); fetchPageOptions(); });
</script>
