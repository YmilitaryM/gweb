<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: #94a3b8;">
      &larr; 返回控制台
    </NuxtLink>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light tracking-tight mb-1" style="color: #1e293b">新闻管理</h2>
        <p class="text-[13px]" style="color: #94a3b8;">发布和管理新闻文章</p>
      </div>
      <button
        @click="openCreate"
        class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all duration-200 hover:translate-y-[-1px]"
        style="background: linear-gradient(135deg, #2563eb, #1d4ed8); box-shadow: 0 2px 12px rgba(37,99,235,0.2);"
      >
        新建文章
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
      <div v-if="articles.length === 0" class="text-[13px] py-12 text-center" style="color: #94a3b8;">
        暂无文章
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="article in articles"
          :key="article.id"
          class="flex items-center justify-between px-5 py-4 rounded-xl"
          style="background: #ffffff; border: 1px solid #dbeafe;"
        >
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <img
              v-if="article.cover_image_id"
              :src="`${apiBase}/../../media/id/${article.cover_image_id}`"
              class="w-14 h-10 rounded-md object-cover flex-shrink-0"
              style="background: #ffffff;"
            />
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-3">
                <span class="text-[14px] font-medium truncate" style="color: #1e293b">{{ article.title_zh }}</span>
                <span
                  class="text-[11px] px-2 py-0.5 rounded-full flex-shrink-0"
                  :style="article.is_published ? 'background: rgba(37,99,235,0.12); color: #60a5fa;' : 'background: #f1f5f9; color: #94a3b8;'"
                >
                  {{ article.is_published ? '已发布' : '草稿' }}
                </span>
              </div>
              <div class="text-[12px] mt-0.5 truncate" style="color: #94a3b8;">
                {{ article.category }} &middot; {{ article.published_at ? new Date(article.published_at).toLocaleDateString('zh-CN') : '未发布' }}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0 ml-4">
            <button
              @click="openEdit(article)"
              class="text-[12px] border-none cursor-pointer px-3 py-1.5 rounded-lg transition-colors"
              style="color: #60a5fa; background: rgba(37,99,235,0.08);"
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
          :style="p === page ? 'background: rgba(37,99,235,0.15); color: #60a5fa;' : 'background: #f1f5f9; color: #94a3b8;'"
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
        style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);"
      >
        <h3 class="text-[15px] font-medium mb-5" style="color: #1e293b">{{ editing ? '编辑文章' : '新建文章' }}</h3>
        <form @submit.prevent="save" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">中文标题</label>
              <input v-model="form.title_zh" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文标题</label>
              <input v-model="form.title_en" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">中文摘要</label>
              <textarea v-model="form.summary_zh" rows="2" class="w-full py-2.5 px-3 text-[13px] outline-none rounded-lg resize-y" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;"></textarea>
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文摘要</label>
              <textarea v-model="form.summary_en" rows="2" class="w-full py-2.5 px-3 text-[13px] outline-none rounded-lg resize-y" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;"></textarea>
            </div>
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">中文内容</label>
            <AdminRichTextEditor v-model="form.content_zh" placeholder="输入中文内容..." />
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">英文内容</label>
            <AdminRichTextEditor v-model="form.content_en" placeholder="Enter English content..." />
          </div>
          <div>
            <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">封面图片</label>
            <AdminMediaPicker v-model="form.cover_image_id" />
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">分类</label>
              <select v-model="form.category" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg appearance-none" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;">
                <option value="company_news">公司新闻</option>
                <option value="industry_news">行业动态</option>
                <option value="product_news">产品资讯</option>
              </select>
            </div>
            <div>
              <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">发布时间</label>
              <input v-model="form.published_at" type="datetime-local" class="w-full py-2.5 px-3 text-[14px] outline-none rounded-lg" style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;" />
            </div>
            <div class="flex items-end pb-1">
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="form.is_published" type="checkbox" class="accent-blue-600" />
                <span class="text-[12px]" style="color: #64748b;">发布</span>
              </label>
            </div>
          </div>
          <div v-if="formError" class="text-[12px]" style="color: #f87171;">{{ formError }}</div>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="modalOpen = false" class="text-[13px] border-none cursor-pointer px-4 py-2 rounded-lg" style="color: #64748b; background: #f1f5f9;">取消</button>
            <button type="submit" :disabled="saving" class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all disabled:opacity-40" style="background: linear-gradient(135deg, #2563eb, #1d4ed8);">
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
        <p class="text-[14px] mb-1" style="color: #1e293b">确认删除</p>
        <p class="text-[12px] mb-5" style="color: #94a3b8;">确定要删除文章 "{{ deleteTarget.title_zh }}" 吗？</p>
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
    const data = await api<{ items: Article[]; total: number; page: number; size: number }>(`/admin/news?page=${page.value}&size=20`);
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

const openCreate = () => {
  editing.value = null;
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
      await api(`/admin/news/${editing.value.id}`, {
        method: 'PUT', body,
      });
    } else {
      await api(`/admin/news`, {
        method: 'POST', body,
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
    await api(`/admin/news/${deleteTarget.value.id}`, {
      method: 'DELETE', 
    });
    deleteTarget.value = null;
    await fetchArticles();
  } catch {}
};

onMounted(fetchArticles);
</script>
