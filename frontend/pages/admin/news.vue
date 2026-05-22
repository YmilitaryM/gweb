<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: rgba(255,255,255,0.25);">
      &larr; 返回控制台
    </NuxtLink>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light text-white tracking-tight mb-1">新闻管理</h2>
        <p class="text-[13px]" style="color: rgba(255,255,255,0.25);">发布和管理新闻文章</p>
      </div>
      <button
        @click="openCreate"
        class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all duration-200 hover:translate-y-[-1px]"
        style="background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 2px 12px rgba(5,150,105,0.2);"
      >
        新建文章
      </button>
    </div>

    <div v-if="loading" class="text-[13px] py-12 text-center" style="color: rgba(255,255,255,0.25);">加载中...</div>

    <div
      v-else-if="error"
      class="mb-6 px-4 py-3 rounded-lg text-[13px]"
      style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;"
    >
      {{ error }}
    </div>

    <template v-else>
      <div v-if="articles.length === 0" class="text-[13px] py-12 text-center" style="color: rgba(255,255,255,0.25);">
        暂无文章
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="article in articles"
          :key="article.id"
          class="flex items-center justify-between px-5 py-4 rounded-xl"
          style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);"
        >
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <img
              v-if="article.cover_image_id"
              :src="`${apiBase}/../../media/id/${article.cover_image_id}`"
              class="w-14 h-10 rounded-md object-cover flex-shrink-0"
              style="background: rgba(255,255,255,0.04);"
            />
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-3">
                <span class="text-[14px] font-medium text-white truncate">{{ article.title_zh }}</span>
                <span
                  class="text-[11px] px-2 py-0.5 rounded-full flex-shrink-0"
                  :style="article.is_published ? 'background: rgba(5,150,105,0.12); color: #34d399;' : 'background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.3);'"
                >
                  {{ article.is_published ? '已发布' : '草稿' }}
                </span>
              </div>
              <div class="text-[12px] mt-0.5 truncate" style="color: rgba(255,255,255,0.25);">
                {{ article.category }} &middot; {{ article.published_at ? new Date(article.published_at).toLocaleDateString('zh-CN') : '未发布' }}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0 ml-4">
            <button
              @click="openEdit(article)"
              class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors"
              style="color: #34d399; background: rgba(5,150,105,0.08);"
            >
              编辑
            </button>
            <button
              @click="confirmDelete(article)"
              class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors"
              style="color: #f87171; background: rgba(239,68,68,0.08);"
            >
              删除
            </button>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
        <button
          v-for="p in totalPages"
          :key="p"
          @click="page = p; fetchArticles()"
          class="text-[12px] border-none cursor-pointer w-8 h-8 rounded-lg transition-colors"
          :style="p === page ? 'background: rgba(5,150,105,0.15); color: #34d399;' : 'background: rgba(255,255,255,0.02); color: rgba(255,255,255,0.35);'"
        >
          {{ p }}
        </button>
      </div>
    </template>

    <!-- Article Modal -->
    <div
      v-if="modalOpen"
      class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto py-10"
      style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
      @click.self="modalOpen = false"
    >
      <div
        class="rounded-2xl p-6 w-full max-w-2xl mx-4"
        style="background: #11161e; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 20px 60px rgba(0,0,0,0.5);"
      >
        <h3 class="text-[15px] font-medium text-white mb-5">{{ editing ? '编辑文章' : '新建文章' }}</h3>
        <form @submit.prevent="save" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: rgba(255,255,255,0.3);">中文标题</label>
              <input v-model="form.title_zh" class="w-full py-2.5 px-3 text-[14px] text-white outline-none rounded-lg" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);" />
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: rgba(255,255,255,0.3);">英文标题</label>
              <input v-model="form.title_en" class="w-full py-2.5 px-3 text-[14px] text-white outline-none rounded-lg" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);" />
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: rgba(255,255,255,0.3);">中文摘要</label>
              <textarea v-model="form.summary_zh" rows="2" class="w-full py-2.5 px-3 text-[13px] text-white outline-none rounded-lg resize-y" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);"></textarea>
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: rgba(255,255,255,0.3);">英文摘要</label>
              <textarea v-model="form.summary_en" rows="2" class="w-full py-2.5 px-3 text-[13px] text-white outline-none rounded-lg resize-y" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);"></textarea>
            </div>
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: rgba(255,255,255,0.3);">中文内容</label>
            <textarea v-model="form.content_zh" rows="4" class="w-full py-2.5 px-3 text-[13px] text-white outline-none rounded-lg resize-y" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);"></textarea>
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: rgba(255,255,255,0.3);">英文内容</label>
            <textarea v-model="form.content_en" rows="4" class="w-full py-2.5 px-3 text-[13px] text-white outline-none rounded-lg resize-y" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);"></textarea>
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: rgba(255,255,255,0.3);">封面图片</label>
            <div class="flex items-start gap-4">
              <div v-if="coverPreview" class="relative flex-shrink-0">
                <img :src="coverPreview" class="w-32 h-20 rounded-lg object-cover" style="background: rgba(255,255,255,0.04);" />
                <button
                  type="button" @click="removeCover"
                  class="absolute -top-2 -right-2 w-5 h-5 rounded-full border-none cursor-pointer flex items-center justify-center text-[11px]"
                  style="background: #ef4444; color: white;"
                >&times;</button>
              </div>
              <label
                class="flex-shrink-0 w-32 h-20 rounded-lg flex flex-col items-center justify-center gap-1 cursor-pointer transition-colors border border-dashed text-[11px]"
                style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.08); color: rgba(255,255,255,0.25);"
                :style="uploadingCover ? 'opacity: 0.5; pointer-events: none;' : ''"
              >
                <span class="text-[16px]">&#8593;</span>
                <span>{{ uploadingCover ? '上传中...' : '点击上传' }}</span>
                <input type="file" accept="image/*" class="hidden" @change="uploadCover" :disabled="uploadingCover" />
              </label>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: rgba(255,255,255,0.3);">分类</label>
              <select v-model="form.category" class="w-full py-2.5 px-3 text-[14px] text-white outline-none rounded-lg appearance-none" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);">
                <option value="company_news">公司新闻</option>
                <option value="industry_news">行业动态</option>
                <option value="product_news">产品资讯</option>
              </select>
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: rgba(255,255,255,0.3);">发布时间</label>
              <input v-model="form.published_at" type="datetime-local" class="w-full py-2.5 px-3 text-[14px] text-white outline-none rounded-lg" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);" />
            </div>
            <div class="flex items-end pb-1">
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="form.is_published" type="checkbox" class="accent-emerald-600" />
                <span class="text-[12px]" style="color: rgba(255,255,255,0.4);">发布</span>
              </label>
            </div>
          </div>
          <div v-if="formError" class="text-[12px]" style="color: #f87171;">{{ formError }}</div>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="modalOpen = false" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: rgba(255,255,255,0.4); background: rgba(255,255,255,0.04);">取消</button>
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
      <div class="rounded-2xl p-6 w-full max-w-sm mx-4" style="background: #11161e; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <p class="text-[14px] text-white mb-1">确认删除</p>
        <p class="text-[12px] mb-5" style="color: rgba(255,255,255,0.3);">确定要删除文章 "{{ deleteTarget.title_zh }}" 吗？</p>
        <div class="flex justify-end gap-3">
          <button @click="deleteTarget = null" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: rgba(255,255,255,0.4); background: rgba(255,255,255,0.04);">取消</button>
          <button @click="doDelete" class="text-[13px] font-medium text-white border-none cursor-pointer px-4 py-2 rounded-lg" style="background: #ef4444;">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['admin-auth'] });

const config = useRuntimeConfig();
const apiBase = config.public.apiBase as string;

const getHeaders = () => {
  const token = import.meta.client ? localStorage.getItem('admin_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

interface Article {
  id: number;
  title_zh: string;
  title_en: string;
  summary_zh: string;
  summary_en: string;
  content_zh: string;
  content_en: string;
  cover_image_id: number | null;
  category: string;
  published_at: string | null;
  is_published: boolean;
}

const articles = ref<Article[]>([]);
const loading = ref(true);
const error = ref('');
const page = ref(1);
const totalPages = ref(1);

const fetchArticles = async () => {
  loading.value = true;
  error.value = '';
  try {
    const data = await $fetch<{ items: Article[]; total: number; page: number; size: number }>(
      `${apiBase}/admin/news?page=${page.value}&size=20`,
      { headers: getHeaders() }
    );
    articles.value = data.items;
    totalPages.value = Math.ceil(data.total / data.size);
  } catch (e: any) {
    error.value = e?.data?.detail || '加载文章列表失败';
  } finally {
    loading.value = false;
  }
};

const modalOpen = ref(false);
const saving = ref(false);
const formError = ref('');
const editing = ref<Article | null>(null);
const form = ref({
  title_zh: '', title_en: '',
  summary_zh: '', summary_en: '',
  content_zh: '', content_en: '',
  cover_image_id: null as number | null,
  category: 'company_news',
  published_at: '',
  is_published: false,
});

const coverPreview = ref<string | null>(null);
const uploadingCover = ref(false);

const uploadCover = async (e: Event) => {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  uploadingCover.value = true;
  try {
    const token = import.meta.client ? localStorage.getItem('admin_token') : null;
    const fd = new FormData();
    fd.append('file', file);
    const res = await $fetch<{ id: number; url: string }>(`${apiBase}/admin/media/upload`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: fd,
    });
    form.value.cover_image_id = res.id;
    coverPreview.value = `${apiBase}/../../media/id/${res.id}`;
  } catch {
    formError.value = '封面上传失败';
  } finally {
    uploadingCover.value = false;
    input.value = '';
  }
};

const removeCover = () => {
  form.value.cover_image_id = null;
  coverPreview.value = null;
};

const openCreate = () => {
  editing.value = null;
  coverPreview.value = null;
  form.value = {
    title_zh: '', title_en: '',
    summary_zh: '', summary_en: '',
    content_zh: '', content_en: '',
    cover_image_id: null,
    category: 'company_news',
    published_at: '',
    is_published: false,
  };
  formError.value = '';
  modalOpen.value = true;
};

const openEdit = (article: Article) => {
  editing.value = article;
  coverPreview.value = article.cover_image_id ? `${apiBase}/../../media/id/${article.cover_image_id}` : null;
  form.value = {
    title_zh: article.title_zh,
    title_en: article.title_en,
    summary_zh: article.summary_zh || '',
    summary_en: article.summary_en || '',
    content_zh: article.content_zh || '',
    content_en: article.content_en || '',
    cover_image_id: article.cover_image_id,
    category: article.category,
    published_at: article.published_at ? new Date(article.published_at).toISOString().slice(0, 16) : '',
    is_published: article.is_published,
  };
  formError.value = '';
  modalOpen.value = true;
};

const save = async () => {
  if (!form.value.title_zh || !form.value.title_en) {
    formError.value = '请填写标题';
    return;
  }
  saving.value = true;
  formError.value = '';
  const body: any = { ...form.value };
  if (!body.published_at) body.published_at = null;
  try {
    if (editing.value) {
      await $fetch(`${apiBase}/admin/news/${editing.value.id}`, {
        method: 'PUT', headers: getHeaders(), body,
      });
    } else {
      await $fetch(`${apiBase}/admin/news`, {
        method: 'POST', headers: getHeaders(), body,
      });
    }
    modalOpen.value = false;
    await fetchArticles();
  } catch (e: any) {
    formError.value = e?.data?.detail || '保存失败';
  } finally {
    saving.value = false;
  }
};

const deleteTarget = ref<Article | null>(null);
const confirmDelete = (article: Article) => { deleteTarget.value = article; };
const doDelete = async () => {
  if (!deleteTarget.value) return;
  try {
    await $fetch(`${apiBase}/admin/news/${deleteTarget.value.id}`, {
      method: 'DELETE', headers: getHeaders(),
    });
    deleteTarget.value = null;
    await fetchArticles();
  } catch {}
};

onMounted(fetchArticles);
</script>
