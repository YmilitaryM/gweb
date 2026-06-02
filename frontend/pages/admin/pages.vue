<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: #94a3b8;">
      &larr; 返回控制台
    </NuxtLink>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light tracking-tight mb-1" style="color: #1e293b;">页面管理</h2>
        <p class="text-[13px]" style="color: #94a3b8;">管理网站页面和内容区块</p>
      </div>
      <button
        @click="openCreatePage"
        class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all duration-200 hover:translate-y-[-1px]"
        style="background: linear-gradient(135deg, #2563eb, #1d4ed8); box-shadow: 0 2px 12px rgba(37,99,235,0.2);"
      >
        新建页面
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-[13px] py-12 text-center" style="color: #94a3b8;">
      加载中...
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="mb-6 px-4 py-3 rounded-lg text-[13px]"
      style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;"
    >
      {{ error }}
    </div>

    <!-- Page list -->
    <template v-else>
      <div v-if="pages.length === 0" class="text-[13px] py-12 text-center" style="color: #94a3b8;">
        暂无页面
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="page in pages"
          :key="page.id"
          class="rounded-xl"
          style="background: #ffffff; border: 1px solid #dbeafe;"
        >
          <!-- Page row -->
          <div class="flex items-center justify-between px-5 py-4">
            <div class="flex-1">
              <div class="flex items-center gap-3">
                <span class="text-[14px] font-medium" style="color: #1e293b;">{{ page.name_zh }}</span>
                <span class="text-[12px] px-2 py-0.5 rounded-full" :style="page.is_published ? 'background: rgba(37,99,235,0.12); color: #60a5fa;' : 'background: #f1f5f9; color: #94a3b8;'">
                  {{ page.is_published ? '已发布' : '草稿' }}
                </span>
                <span class="text-[11px] px-2 py-0.5 rounded-full" :style="page.type === 'content' ? 'background: #f1f5f9; color: #64748b;' : 'background: rgba(59,130,246,0.08); color: #60a5fa;'">
                  {{ page.type }}
                </span>
              </div>
              <div class="text-[12px] mt-0.5" style="color: #94a3b8;">
                /{{ page.slug }} &middot; {{ page.name_en }} &middot; 排序: {{ page.sort_order }}
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="toggleBlocks(page)"
                class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors"
                style="color: #64748b; background: #f1f5f9;"
              >
                {{ expandedPageId === page.id ? '收起' : '区块' }}
              </button>
              <button
                @click="openEditPage(page)"
                class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors"
                style="color: #60a5fa; background: rgba(37,99,235,0.08);"
              >
                编辑
              </button>
              <button
                @click="confirmDeletePage(page)"
                class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors"
                style="color: #f87171; background: rgba(239,68,68,0.08);"
              >
                删除
              </button>
            </div>
          </div>

          <!-- Blocks section -->
          <div
            v-if="expandedPageId === page.id"
            class="px-5 pb-4 border-t"
            style="border-color: #dbeafe;"
          >
            <div class="flex items-center justify-between pt-4 mb-3">
              <span class="text-[12px]" style="color: #94a3b8;">内容区块</span>
              <button
                @click="openCreateBlock(page)"
                class="text-[12px] border-none cursor-pointer px-3 py-1 rounded-lg transition-colors"
                style="color: #60a5fa; background: rgba(37,99,235,0.08);"
              >
                + 添加区块
              </button>
            </div>
            <div v-if="blocksLoading" class="text-[12px] py-4 text-center" style="color: #94a3b8;">
              加载中...
            </div>
            <div v-else-if="page._blocks?.length === 0" class="text-[12px] py-4 text-center" style="color: #94a3b8;">
              暂无区块
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="block in page._blocks"
                :key="block.id"
                class="flex items-center justify-between px-4 py-2.5 rounded-lg"
                style="background: #f8fafc;"
              >
                <div class="flex items-center gap-3">
                  <span class="text-[11px] px-2 py-0.5 rounded" style="background: #f1f5f9; color: #94a3b8;">
                    {{ block.type }}
                  </span>
                  <span class="text-[12px]" style="color: #64748b;">#{{ block.order }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    @click="openEditBlock(block, page.id)"
                    class="text-[11px] border-none cursor-pointer px-2.5 py-1 rounded-lg transition-colors"
                    style="color: #60a5fa; background: rgba(37,99,235,0.08);"
                  >
                    编辑
                  </button>
                  <button
                    @click="confirmDeleteBlock(block, page.id)"
                    class="text-[11px] border-none cursor-pointer px-2.5 py-1 rounded-lg transition-colors"
                    style="color: #f87171; background: rgba(239,68,68,0.08);"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Page Modal -->
    <div
      v-if="pageModal"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
      @click.self="pageModal = false"
    >
      <div
        class="rounded-2xl p-6 w-full max-w-lg mx-4"
        style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);"
      >
        <h3 class="text-[15px] font-medium mb-5" style="color: #1e293b;">{{ editingPage ? '编辑页面' : '新建页面' }}</h3>
        <form @submit.prevent="savePage" class="space-y-4">
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">中文名称</label>
            <input
              v-model="pageForm.name_zh"
              class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg transition-colors"
              style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
              :style="{ borderColor: pageFormFocused === 'name_zh' ? '#2563eb' : '#d1d5db' }"
              @focus="pageFormFocused = 'name_zh'"
              @blur="pageFormFocused = null"
            />
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文名称</label>
            <input
              v-model="pageForm.name_en"
              class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg transition-colors"
              style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
              :style="{ borderColor: pageFormFocused === 'name_en' ? '#2563eb' : '#d1d5db' }"
              @focus="pageFormFocused = 'name_en'"
              @blur="pageFormFocused = null"
            />
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">Slug</label>
            <input
              v-model="pageForm.slug"
              class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg transition-colors"
              style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
              :style="{ borderColor: pageFormFocused === 'slug' ? '#2563eb' : '#d1d5db' }"
              @focus="pageFormFocused = 'slug'"
              @blur="pageFormFocused = null"
            />
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">页面类型</label>
            <select
              v-model="pageForm.type"
              class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg appearance-none"
              style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
            >
              <option value="content">content — 通用内容页</option>
              <option value="news">news — 新闻中心</option>
              <option value="products">products — 产品中心</option>
              <option value="faq">faq — 常见问题</option>
              <option value="contact">contact — 联系我们</option>
            </select>
          </div>
          <div class="flex items-center gap-6">
            <div class="flex-1">
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">排序</label>
              <input v-model.number="pageForm.sort_order" type="number" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;" />
            </div>
            <div class="flex items-end pb-1 pt-5">
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="pageForm.is_published" type="checkbox" class="accent-blue-600" />
                <span class="text-[12px]" style="color: #64748b;">已发布</span>
              </label>
            </div>
          </div>
          <div v-if="pageFormError" class="text-[12px]" style="color: #f87171;">{{ pageFormError }}</div>
          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              @click="pageModal = false"
              class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg transition-colors"
              style="color: #64748b; background: #f1f5f9;"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="pageSaving"
              class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all disabled:opacity-40"
              style="background: linear-gradient(135deg, #2563eb, #1d4ed8);"
            >
              {{ pageSaving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Block Modal -->
    <div
      v-if="blockModal"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
      @click.self="blockModal = false"
    >
      <div
        class="rounded-2xl p-6 w-full max-w-lg mx-4"
        style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);"
      >
        <h3 class="text-[15px] font-medium mb-5" style="color: #1e293b;">{{ editingBlock ? '编辑区块' : '添加区块' }}</h3>
        <form @submit.prevent="saveBlock" class="space-y-4">
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">类型</label>
            <input
              v-model="blockForm.type"
              class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg transition-colors"
              style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
              placeholder="hero, cta, video_banner, ..."
            />
          </div>
          <!-- Visual block content editor -->
          <div v-if="blockForm.type">
            <BlockContentEditor
              :block-type="blockForm.type"
              :content="blockContent"
              :config-str="blockForm.config_str"
              :content-str="blockForm.content_str"
              @update:content="blockContent = $event"
              @update:config-str="blockForm.config_str = $event"
              @update:content-str="blockForm.content_str = $event"
            />
          </div>
          <div v-else class="text-[12px] py-4 text-center" style="color: #94a3b8;">
            请先输入区块类型
          </div>
          <div v-if="blockFormError" class="text-[12px]" style="color: #f87171;">{{ blockFormError }}</div>
          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              @click="blockModal = false"
              class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg transition-colors"
              style="color: #64748b; background: #f1f5f9;"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="blockSaving"
              class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all disabled:opacity-40"
              style="background: linear-gradient(135deg, #2563eb, #1d4ed8);"
            >
              {{ blockSaving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Page Confirm -->
    <div
      v-if="deletePageTarget"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
      @click.self="deletePageTarget = null"
    >
      <div
        class="rounded-2xl p-6 w-full max-w-sm mx-4"
        style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);"
      >
        <p class="text-[14px] mb-1" style="color: #1e293b;">确认删除</p>
        <p class="text-[12px] mb-5" style="color: #94a3b8;">
          确定要删除页面 "{{ deletePageTarget.name_zh }}" 吗？此操作不可撤销。
        </p>
        <div class="flex justify-end gap-3">
          <button @click="deletePageTarget = null" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">
            取消
          </button>
          <button @click="doDeletePage" class="text-[13px] font-medium text-white border-none cursor-pointer px-4 py-2 rounded-lg" style="background: #ef4444;">
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Block Confirm -->
    <div
      v-if="deleteBlockTarget"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
      @click.self="deleteBlockTarget = null"
    >
      <div
        class="rounded-2xl p-6 w-full max-w-sm mx-4"
        style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);"
      >
        <p class="text-[14px] mb-1" style="color: #1e293b;">确认删除区块</p>
        <p class="text-[12px] mb-5" style="color: #94a3b8;">确定要删除这个区块吗？此操作不可撤销。</p>
        <div class="flex justify-end gap-3">
          <button @click="deleteBlockTarget = null" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">
            取消
          </button>
          <button @click="doDeleteBlock" class="text-[13px] font-medium text-white border-none cursor-pointer px-4 py-2 rounded-lg" style="background: #ef4444;">
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['admin-auth'] });

const { api, getHeaders } = useAdminApi();

interface Page {
  id: number;
  name_zh: string;
  name_en: string;
  slug: string;
  type: string;
  sort_order: number;
  is_published: boolean;
  _blocks?: Block[];
}

interface Block {
  id: number;
  type: string;
  config: Record<string, any>;
  content: Record<string, any>;
  order: number;
  page_id: number;
}

// --- Pages ---
const pages = ref<Page[]>([]);
const loading = ref(true);
const error = ref('');

const fetchPages = async () => {
  loading.value = true;
  error.value = '';
  try {
    pages.value = await api<Page[]>('/admin/pages');
  } catch (e: any) {
    error.value = e?.data?.detail || '加载页面列表失败';
  } finally {
    loading.value = false;
  }
};

const pageModal = ref(false);
const pageSaving = ref(false);
const pageFormError = ref('');
const pageFormFocused = ref<string | null>(null);
const editingPage = ref<Page | null>(null);
const pageForm = ref({ name_zh: '', name_en: '', slug: '', type: 'content', sort_order: 0, is_published: false });

const openCreatePage = () => {
  editingPage.value = null;
  pageForm.value = { name_zh: '', name_en: '', slug: '', type: 'content', sort_order: 0, is_published: false };
  pageFormError.value = '';
  pageModal.value = true;
};

const openEditPage = (page: Page) => {
  editingPage.value = page;
  pageForm.value = { name_zh: page.name_zh, name_en: page.name_en, slug: page.slug, type: page.type, sort_order: page.sort_order, is_published: page.is_published };
  pageFormError.value = '';
  pageModal.value = true;
};

const savePage = async () => {
  if (!pageForm.value.name_zh || !pageForm.value.name_en || !pageForm.value.slug) {
    pageFormError.value = '请填写所有字段';
    return;
  }
  pageSaving.value = true;
  pageFormError.value = '';
  try {
    if (editingPage.value) {
      await api(`/admin/pages/${editingPage.value.id}`, {
        method: 'PUT', body: pageForm.value,
      });
    } else {
      await api(`/admin/pages`, {
        method: 'POST', body: pageForm.value,
      });
    }
    pageModal.value = false;
    await fetchPages();
  } catch (e: any) {
    pageFormError.value = e?.data?.detail || '保存失败';
  } finally {
    pageSaving.value = false;
  }
};

const deletePageTarget = ref<Page | null>(null);
const confirmDeletePage = (page: Page) => { deletePageTarget.value = page; };
const doDeletePage = async () => {
  if (!deletePageTarget.value) return;
  try {
    await api(`/admin/pages/${deletePageTarget.value.id}`, {
      method: 'DELETE', 
    });
    deletePageTarget.value = null;
    if (expandedPageId.value === deletePageTarget.value?.id) expandedPageId.value = null;
    await fetchPages();
  } catch {}
};

// --- Blocks ---
const expandedPageId = ref<number | null>(null);
const blocksLoading = ref(false);

const toggleBlocks = async (page: Page) => {
  if (expandedPageId.value === page.id) {
    expandedPageId.value = null;
    return;
  }
  expandedPageId.value = page.id;
  if (!page._blocks) {
    blocksLoading.value = true;
    try {
      // Use the public page endpoint to get blocks
      const fullPageData = await api<any>(`/pages/${page.slug}`);
      page._blocks = fullPageData?.blocks || [];
    } catch {
      page._blocks = [];
    } finally {
      blocksLoading.value = false;
    }
  }
};

const blockModal = ref(false);
const blockSaving = ref(false);
const blockFormError = ref('');
const editingBlock = ref<Block | null>(null);
const blockFormPageId = ref<number>(0);
const blockForm = ref({ type: '', config_str: '{}', content_str: '{}' });
const blockContent = ref<Record<string, any>>({});

const openCreateBlock = (page: Page) => {
  editingBlock.value = null;
  blockFormPageId.value = page.id;
  blockForm.value = { type: '', config_str: '{}', content_str: '{}' };
  blockContent.value = {};
  blockFormError.value = '';
  blockModal.value = true;
};

const openEditBlock = (block: Block, pageId: number) => {
  editingBlock.value = block;
  blockFormPageId.value = pageId;
  blockForm.value = {
    type: block.type,
    config_str: JSON.stringify(block.config, null, 2),
    content_str: JSON.stringify(block.content, null, 2),
  };
  blockContent.value = JSON.parse(JSON.stringify(block.content || {}));
  blockFormError.value = '';
  blockModal.value = true;
};

const saveBlock = async () => {
  if (!blockForm.value.type) {
    blockFormError.value = '请填写类型';
    return;
  }
  let config: any = {};
  let content: any = {};
  try { config = JSON.parse(blockForm.value.config_str); } catch { blockFormError.value = 'Config JSON 格式错误'; return; }

  // Use visual editor content; if advanced JSON was edited, merge it
  try {
    const raw = JSON.parse(blockForm.value.content_str);
    if (raw && Object.keys(raw).length > 0 && Object.keys(raw).length >= Object.keys(blockContent.value).length) {
      content = raw; // advanced mode took precedence
    } else {
      content = JSON.parse(JSON.stringify(blockContent.value));
    }
  } catch {
    content = JSON.parse(JSON.stringify(blockContent.value));
  }

  blockSaving.value = true;
  blockFormError.value = '';
  try {
    if (editingBlock.value) {
      await api(`/admin/blocks/${editingBlock.value.id}`, {
        method: 'PUT', body: { type: blockForm.value.type, config, content },
      });
    } else {
      await api(`/admin/pages/${blockFormPageId.value}/blocks`, {
        method: 'POST', body: { type: blockForm.value.type, config, content },
      });
    }
    blockModal.value = false;
    // Refresh blocks for the current page
    const page = pages.value.find(p => p.id === blockFormPageId.value);
    if (page) page._blocks = undefined;
    if (expandedPageId.value === blockFormPageId.value) {
      expandedPageId.value = null;
      nextTick(() => {
        const p = pages.value.find(p2 => p2.id === blockFormPageId.value);
        if (p) toggleBlocks(p);
      });
    }
  } catch (e: any) {
    blockFormError.value = e?.data?.detail || '保存失败';
  } finally {
    blockSaving.value = false;
  }
};

const deleteBlockTarget = ref<Block | null>(null);
const confirmDeleteBlock = (block: Block, _pageId: number) => {
  deleteBlockTarget.value = block;
  blockFormPageId.value = _pageId;
};
const doDeleteBlock = async () => {
  if (!deleteBlockTarget.value) return;
  try {
    await api(`/admin/blocks/${deleteBlockTarget.value.id}`, {
      method: 'DELETE', 
    });
    deleteBlockTarget.value = null;
    const page = pages.value.find(p => p.id === blockFormPageId.value);
    if (page) page._blocks = undefined;
    if (expandedPageId.value === blockFormPageId.value) {
      expandedPageId.value = null;
      nextTick(() => {
        const p = pages.value.find(p2 => p2.id === blockFormPageId.value);
        if (p) toggleBlocks(p);
      });
    }
  } catch {}
};

onMounted(fetchPages);
</script>
