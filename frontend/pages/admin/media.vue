<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: #94a3b8;">
      &larr; 返回控制台
    </NuxtLink>

    <!-- Category View -->
    <template v-if="view === 'categories'">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-xl font-light tracking-tight mb-1" style="color: #1e293b;">媒体管理</h2>
          <p class="text-[13px]" style="color: #94a3b8;">按分类浏览和管理媒体资源</p>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="openAddCategory"
            class="text-[13px] font-medium border-none cursor-pointer px-4 py-2 rounded-lg transition-all duration-200"
            style="color: #2563eb; background: rgba(37,99,235,0.08);"
          >+ 添加分类</button>
          <button
            @click="openUpload(null)"
            class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all duration-200 hover:translate-y-[-1px]"
            style="background: linear-gradient(135deg, #2563eb, #1d4ed8); box-shadow: 0 2px 12px rgba(37,99,235,0.2);"
          >
            上传文件
          </button>
        </div>
      </div>

      <div v-if="categoriesLoading" class="text-[13px] py-12 text-center" style="color: #94a3b8;">加载中...</div>

      <template v-else>
        <div v-if="categoryItems.length === 0" class="text-[13px] py-12 text-center" style="color: #94a3b8;">
          暂无分类，请先上传文件并指定分类
        </div>
        <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <!-- All Media card -->
          <div
            class="rounded-xl overflow-hidden cursor-pointer transition-all duration-200 hover:translate-y-[-2px]"
            style="background: #ffffff; border: 1px solid #dbeafe; box-shadow: 0 1px 3px rgba(0,0,0,0.04);"
            @click="enterCategory(null)"
          >
            <div class="aspect-[4/3] flex items-center justify-center" style="background: linear-gradient(135deg, #eff6ff, #bfdbfe);">
              <span class="text-[36px]">&#128444;</span>
            </div>
            <div class="p-3">
              <div class="text-[14px] font-medium" style="color: #1e293b;">全部媒体</div>
              <div class="text-[12px] mt-0.5" style="color: #94a3b8;">{{ totalMediaCount }} 个文件</div>
            </div>
          </div>

          <!-- Category cards -->
          <div
            v-for="cat in categoryItems"
            :key="cat.name"
            class="group rounded-xl overflow-hidden relative transition-all duration-200 hover:translate-y-[-2px]"
            style="background: #ffffff; border: 1px solid #dbeafe; box-shadow: 0 1px 3px rgba(0,0,0,0.04);"
          >
            <div class="aspect-[4/3] flex items-center justify-center overflow-hidden cursor-pointer" style="background: #f1f5f9;" @click="enterCategory(cat.name)">
              <img
                v-if="cat.cover_image_id"
                :src="mediaUrl(cat.cover_image_id)"
                class="w-full h-full object-cover"
              />
              <span v-else class="text-[36px]">&#128193;</span>
            </div>
            <div class="p-3 cursor-pointer" @click="enterCategory(cat.name)">
              <div class="text-[14px] font-medium" style="color: #1e293b;">{{ cat.name }}</div>
              <div class="text-[12px] mt-0.5" style="color: #94a3b8;">{{ cat.count }} 个文件</div>
            </div>
            <!-- Category actions -->
            <div class="absolute top-2 right-2 flex gap-1">
              <button
                @click.stop="openRenameCategory(cat)"
                class="text-[11px] border-none cursor-pointer px-2 py-1 rounded transition-colors"
                style="background: rgba(0,0,0,0.55); color: white;"
              >重命名</button>
              <button
                @click.stop="confirmDeleteCategory(cat)"
                class="text-[11px] border-none cursor-pointer px-2 py-1 rounded transition-colors"
                style="background: rgba(239,68,68,0.85); color: white;"
              >删除</button>
            </div>
          </div>
        </div>
      </template>
    </template>

    <!-- Category Detail View -->
    <template v-else>
      <div class="flex items-center gap-3 mb-6">
        <button
          @click="view = 'categories'; fetchCategories()"
          class="text-[13px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors"
          style="color: #64748b; background: #f1f5f9;"
        >&larr; 返回分类</button>
        <div>
          <h2 class="text-xl font-light tracking-tight" style="color: #1e293b;">{{ activeCategory || '全部媒体' }}</h2>
          <p class="text-[13px]" style="color: #94a3b8;" v-if="activeCategory">分类下的媒体文件</p>
        </div>
      </div>

      <!-- Search & Filters -->
      <div class="flex flex-wrap items-center gap-3 mb-6">
        <input
          v-model="searchQ" placeholder="搜索文件名或名称..."
          class="py-2 px-3 text-[13px] outline-none rounded-lg w-56"
          style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;"
          @keyup.enter="page = 1; fetchMedia()"
        />
        <input
          v-model="filterDateFrom" type="date"
          class="py-2 px-3 text-[13px] outline-none rounded-lg"
          style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;"
          @change="page = 1; fetchMedia()"
        />
        <span class="text-[13px]" style="color: #94a3b8;">至</span>
        <input
          v-model="filterDateTo" type="date"
          class="py-2 px-3 text-[13px] outline-none rounded-lg"
          style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;"
          @change="page = 1; fetchMedia()"
        />
        <button
          @click="page = 1; fetchMedia()"
          class="text-[12px] border-none cursor-pointer px-4 py-2 rounded-lg transition-colors"
          style="color: #2563eb; background: rgba(37,99,235,0.08);"
        >搜索</button>
        <button
          @click="resetFilters"
          class="text-[12px] border-none cursor-pointer px-3 py-2 rounded-lg transition-colors"
          style="color: #94a3b8; background: #f1f5f9;"
        >重置</button>
        <button
          @click="openUpload(activeCategory)"
          class="text-[12px] font-medium text-white border-none cursor-pointer px-4 py-2 rounded-lg ml-auto"
          style="background: linear-gradient(135deg, #2563eb, #1d4ed8);"
        >+ 上传文件</button>
      </div>

      <div v-if="uploadError" class="mb-4 px-4 py-3 rounded-lg text-[13px]" style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;">
        {{ uploadError }}
      </div>

      <div v-if="loading" class="text-[13px] py-12 text-center" style="color: #94a3b8;">加载中...</div>
      <div v-else-if="error" class="mb-6 px-4 py-3 rounded-lg text-[13px]" style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;">
        {{ error }}
      </div>

      <template v-else>
        <div v-if="items.length === 0" class="text-[13px] py-12 text-center" style="color: #94a3b8;">
          暂无媒体文件
        </div>
        <div v-else class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <div
            v-for="m in items"
            :key="m.id"
            class="group rounded-xl overflow-hidden relative"
            style="background: #ffffff; border: 1px solid #dbeafe;"
          >
            <div class="aspect-video flex items-center justify-center overflow-hidden" style="background: #f1f5f9;">
              <img
                v-if="m.mime_type?.startsWith('image/')"
                :src="mediaUrl(m.id)"
                class="w-full h-full object-cover"
                loading="lazy"
              />
              <div v-else class="text-[11px] text-center px-2" style="color: #94a3b8;">
                {{ m.mime_type || 'unknown' }}
              </div>
            </div>
            <div class="p-2.5">
              <div class="text-[12px] truncate font-medium" :title="m.name_zh || m.filename" style="color: #1e293b;">
                {{ m.name_zh || m.filename }}
              </div>
              <div class="text-[10px] mt-0.5 flex items-center justify-between" style="color: #94a3b8;">
                <span>{{ formatSize(m.size) }}</span>
                <a
                  :href="mediaUrl(m.id)"
                  target="_blank"
                  class="no-underline transition-colors hover:text-white"
                  :style="{ color: 'inherit' }"
                  title="查看原文件"
                >&#8599;</a>
              </div>
            </div>
            <button
              @click="confirmDelete(m)"
              class="absolute top-2 right-2 w-6 h-6 rounded-lg border-none cursor-pointer flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
              style="background: rgba(0,0,0,0.6); color: #f87171; font-size: 12px;"
              title="删除"
            >&times;</button>
          </div>
        </div>

        <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
          <button
            v-for="p in totalPages"
            :key="p"
            @click="page = p; fetchMedia()"
            class="text-[12px] border-none cursor-pointer w-8 h-8 rounded-lg transition-colors"
            :style="p === page ? 'background: rgba(37,99,235,0.15); color: #60a5fa;' : 'background: #f1f5f9; color: #94a3b8;'"
          >{{ p }}</button>
        </div>
      </template>
    </template>

    <!-- Upload Modal -->
    <Teleport to="body">
      <div
        v-if="uploadModalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center"
        style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
        @click.self="uploadModalOpen = false"
      >
        <div class="rounded-2xl p-6 w-full max-w-lg mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
          <h3 class="text-[15px] font-medium mb-5" style="color: #1e293b">上传文件</h3>
          <form @submit.prevent="doUpload" class="space-y-4">
            <div
              v-if="!uploadPreview"
              class="w-full h-32 rounded-xl flex flex-col items-center justify-center gap-1 cursor-pointer transition-colors border-2 border-dashed"
              :style="uploading ? 'opacity: 0.5; pointer-events: none; border-color: #d1d5db; color: #94a3b8; background: #f8fafc;' : 'border-color: #d1d5db; color: #94a3b8; background: #f8fafc;'"
              @click="triggerFileInput"
            >
              <span v-if="uploading" class="w-6 h-6 border-2 border-t-transparent rounded-full animate-spin" style="border-color: #94a3b8; border-top-color: transparent;"></span>
              <span v-else class="text-[24px]">&#8593;</span>
              <span class="text-[12px]">{{ uploading ? '上传中...' : '点击选择文件' }}</span>
            </div>
            <div
              v-else
              class="relative w-full h-40 rounded-xl overflow-hidden cursor-pointer"
              style="background: #f1f5f9;"
              @click="triggerFileInput"
            >
              <img :src="uploadPreview" class="w-full h-full object-contain" />
              <div class="absolute bottom-0 left-0 right-0 px-3 py-1.5 text-[12px] truncate" style="background: rgba(0,0,0,0.6); color: white;">
                {{ uploadFile?.name }}
              </div>
            </div>
            <input ref="fileInputRef" type="file" accept="image/*,video/*" class="hidden" @change="onFileSelect" />
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">中文名称</label>
                <input v-model="uploadForm.name_zh" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" placeholder="可选" />
              </div>
              <div>
                <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">英文名称</label>
                <input v-model="uploadForm.name_en" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" placeholder="可选" />
              </div>
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">分类</label>
              <select v-model="uploadForm.category" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;">
                <option value="">无分类</option>
                <option v-for="c in categoryItems" :key="c.name" :value="c.name">{{ c.name }}</option>
              </select>
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">描述</label>
              <textarea v-model="uploadForm.description" rows="2" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg resize-y" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" placeholder="可选"></textarea>
            </div>
            <div v-if="uploadError" class="text-[12px]" style="color: #f87171;">{{ uploadError }}</div>
            <div class="flex justify-end gap-3 pt-1">
              <button type="button" @click="uploadModalOpen = false" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">取消</button>
              <button type="submit" :disabled="uploading" class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all disabled:opacity-40" style="background: linear-gradient(135deg, #2563eb, #1d4ed8);">{{ uploading ? '上传中...' : '上传' }}</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Add/Rename Category Modal -->
    <Teleport to="body">
      <div
        v-if="categoryModalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center"
        style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
        @click.self="categoryModalOpen = false"
      >
        <div class="rounded-2xl p-6 w-full max-w-sm mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
          <h3 class="text-[15px] font-medium mb-4" style="color: #1e293b">{{ renamingCategory ? '重命名分类' : '添加分类' }}</h3>
          <form @submit.prevent="saveCategory" class="space-y-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">分类名称</label>
              <input v-model="categoryFormName" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" placeholder="输入分类名称" />
            </div>
            <div v-if="categoryError" class="text-[12px]" style="color: #f87171;">{{ categoryError }}</div>
            <div class="flex justify-end gap-3">
              <button type="button" @click="categoryModalOpen = false" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">取消</button>
              <button type="submit" class="text-[13px] font-medium text-white border-none cursor-pointer px-4 py-2 rounded-lg" style="background: linear-gradient(135deg, #2563eb, #1d4ed8);">{{ renamingCategory ? '保存' : '添加' }}</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Delete Category Confirm -->
    <div
      v-if="deleteCategoryTarget"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
      @click.self="deleteCategoryTarget = null"
    >
      <div class="rounded-2xl p-6 w-full max-w-sm mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <p class="text-[14px] mb-1" style="color: #1e293b;">确认删除分类</p>
        <p class="text-[12px] mb-5" style="color: #94a3b8;">确定要删除分类 "{{ deleteCategoryTarget.name }}" 吗？文件不会被删除，仅清除分类标记（{{ deleteCategoryTarget.count }} 个文件）。</p>
        <div class="flex justify-end gap-3">
          <button @click="deleteCategoryTarget = null" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">取消</button>
          <button @click="doDeleteCategory" class="text-[13px] font-medium text-white border-none cursor-pointer px-4 py-2 rounded-lg" style="background: #ef4444;">删除</button>
        </div>
      </div>
    </div>

    <!-- Delete Media Confirm -->
    <div
      v-if="deleteTarget"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
      @click.self="deleteTarget = null"
    >
      <div class="rounded-2xl p-6 w-full max-w-sm mx-4" style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <p class="text-[14px] mb-1" style="color: #1e293b;">确认删除</p>
        <p class="text-[12px] mb-5" style="color: #94a3b8;">确定要删除文件 "{{ deleteTarget.filename }}" 吗？此操作不可撤销。</p>
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

// -- View state --
const view = ref<'categories' | 'detail'>('categories');
const activeCategory = ref<string | null>(null);

// -- Categories --
interface CategoryItem {
  name: string;
  count: number;
  cover_image_id: number | null;
}

const categoryItems = ref<CategoryItem[]>([]);
const categoriesLoading = ref(true);
const totalMediaCount = ref(0);

const fetchCategories = async () => {
  categoriesLoading.value = true;
  try {
    categoryItems.value = await api<CategoryItem[]>('/admin/media/categories');
    totalMediaCount.value = categoryItems.value.reduce((s, c) => s + c.count, 0);
  } catch {
    categoryItems.value = [];
  } finally {
    categoriesLoading.value = false;
  }
};

const enterCategory = (name: string | null) => {
  activeCategory.value = name;
  searchQ.value = '';
  filterDateFrom.value = '';
  filterDateTo.value = '';
  page.value = 1;
  view.value = 'detail';
  fetchMedia();
};

// -- Category CRUD --
const categoryModalOpen = ref(false);
const categoryFormName = ref('');
const categoryError = ref('');
const renamingCategory = ref<CategoryItem | null>(null);

const openAddCategory = () => {
  renamingCategory.value = null;
  categoryFormName.value = '';
  categoryError.value = '';
  categoryModalOpen.value = true;
};

const openRenameCategory = (cat: CategoryItem) => {
  renamingCategory.value = cat;
  categoryFormName.value = cat.name;
  categoryError.value = '';
  categoryModalOpen.value = true;
};

const saveCategory = async () => {
  const name = categoryFormName.value.trim();
  if (!name) { categoryError.value = '请输入分类名称'; return; }

  if (renamingCategory.value) {
    try {
      await api(`/admin/media/categories/rename?old_name=${encodeURIComponent(renamingCategory.value.name)}&new_name=${encodeURIComponent(name)}`, { method: 'PUT' });
    } catch (e: any) {
      categoryError.value = e?.data?.detail || '重命名失败';
      return;
    }
    if (activeCategory.value === renamingCategory.value.name) {
      activeCategory.value = name;
    }
  } else {
    try {
      await api('/admin/media/categories', { method: 'POST', body: { name } });
    } catch (e: any) {
      categoryError.value = e?.data?.detail || '创建失败';
      return;
    }
  }
  categoryModalOpen.value = false;
  await fetchCategories();
};

const deleteCategoryTarget = ref<CategoryItem | null>(null);
const confirmDeleteCategory = (cat: CategoryItem) => { deleteCategoryTarget.value = cat; };
const doDeleteCategory = async () => {
  if (!deleteCategoryTarget.value) return;
  try {
    await api(`/admin/media/categories/${encodeURIComponent(deleteCategoryTarget.value.name)}`, { method: 'DELETE' });
    deleteCategoryTarget.value = null;
    await fetchCategories();
  } catch {}
};

// -- Media list --
interface MediaItem {
  id: number;
  filename: string;
  mime_type: string;
  url: string;
  size: number;
  thumbnail_url: string | null;
  category: string | null;
  name_zh: string | null;
  name_en: string | null;
  description: string | null;
}

const items = ref<MediaItem[]>([]);
const loading = ref(false);
const error = ref('');
const page = ref(1);
const totalPages = ref(1);

const searchQ = ref('');
const filterDateFrom = ref('');
const filterDateTo = ref('');

const fetchMedia = async () => {
  loading.value = true;
  error.value = '';
  try {
    const params = new URLSearchParams({ page: String(page.value), size: '24' });
    if (activeCategory.value) params.set('category', activeCategory.value);
    if (searchQ.value) params.set('q', searchQ.value);
    if (filterDateFrom.value) params.set('date_from', filterDateFrom.value);
    if (filterDateTo.value) params.set('date_to', filterDateTo.value);

    const data = await api<{ items: MediaItem[]; total: number; pages: number }>(`/admin/media?${params}`);
    items.value = data.items;
    totalPages.value = data.pages;
  } catch (e: any) {
    error.value = e?.data?.detail || '加载媒体列表失败';
  } finally {
    loading.value = false;
  }
};

const resetFilters = () => {
  searchQ.value = '';
  filterDateFrom.value = '';
  filterDateTo.value = '';
  page.value = 1;
  fetchMedia();
};

// -- Upload --
const uploadModalOpen = ref(false);
const uploading = ref(false);
const uploadError = ref('');
const uploadFile = ref<File | null>(null);
const uploadPreview = ref<string | null>(null);
const fileInputRef = ref<HTMLInputElement>();

const uploadForm = ref({ name_zh: '', name_en: '', category: '', description: '' });

const openUpload = (presetCategory: string | null) => {
  uploadForm.value = {
    name_zh: '', name_en: '',
    category: presetCategory || '',
    description: '',
  };
  uploadFile.value = null;
  uploadPreview.value = null;
  uploadError.value = '';
  uploadModalOpen.value = true;
};

const triggerFileInput = () => { fileInputRef.value?.click(); };
const onFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0] || null;
  uploadFile.value = file;
  if (uploadPreview.value) { URL.revokeObjectURL(uploadPreview.value); uploadPreview.value = null; }
  if (file && file.type.startsWith('image/')) {
    uploadPreview.value = URL.createObjectURL(file);
  }
};

const doUpload = async () => {
  if (!uploadFile.value) { uploadError.value = '请选择文件'; return; }
  uploading.value = true;
  uploadError.value = '';
  try {
    const fd = new FormData();
    fd.append('file', uploadFile.value);
    if (uploadForm.value.category) fd.append('category', uploadForm.value.category);
    if (uploadForm.value.name_zh) fd.append('name_zh', uploadForm.value.name_zh);
    if (uploadForm.value.name_en) fd.append('name_en', uploadForm.value.name_en);
    if (uploadForm.value.description) fd.append('description', uploadForm.value.description);

    await api('/admin/media/upload', { method: 'POST', body: fd });
    uploadModalOpen.value = false;
    page.value = 1;
    // Navigate to show the uploaded file: go to the chosen category or "all media"
    const targetCat = uploadForm.value.category || null;
    activeCategory.value = targetCat;
    searchQ.value = '';
    filterDateFrom.value = '';
    filterDateTo.value = '';
    view.value = 'detail';
    await fetchMedia();
    await fetchCategories();
  } catch (e: any) {
    uploadError.value = e?.data?.detail || '上传失败';
  } finally {
    uploading.value = false;
  }
};

// -- Delete media --
const deleteTarget = ref<MediaItem | null>(null);
const confirmDelete = (m: MediaItem) => { deleteTarget.value = m; };
const doDelete = async () => {
  if (!deleteTarget.value) return;
  try {
    await api(`/admin/media/${deleteTarget.value.id}`, { method: 'DELETE' });
    deleteTarget.value = null;
    await fetchMedia();
  } catch {}
};

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

watch(uploadModalOpen, (open) => {
  if (!open && uploadPreview.value) {
    URL.revokeObjectURL(uploadPreview.value);
    uploadPreview.value = null;
  }
});

onBeforeUnmount(() => {
  if (uploadPreview.value) URL.revokeObjectURL(uploadPreview.value);
});

onMounted(fetchCategories);
</script>
