<template>
  <div class="p-8">
    <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 text-[12px] mb-4 no-underline transition-colors hover:opacity-80" style="color: rgba(255,255,255,0.25);">
      &larr; 返回控制台
    </NuxtLink>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-light text-white tracking-tight mb-1">媒体管理</h2>
        <p class="text-[13px]" style="color: rgba(255,255,255,0.25);">上传和管理图片、视频等媒体资源</p>
      </div>
      <label
        class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all duration-200 hover:translate-y-[-1px]"
        :style="uploading ? 'opacity: 0.5; pointer-events: none;' : ''"
        style="background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 2px 12px rgba(5,150,105,0.2);"
      >
        {{ uploading ? '上传中...' : '上传文件' }}
        <input type="file" accept="image/*,video/*" class="hidden" @change="doUpload" :disabled="uploading" />
      </label>
    </div>

    <div v-if="uploadError" class="mb-4 px-4 py-3 rounded-lg text-[13px]" style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;">
      {{ uploadError }}
    </div>

    <div v-if="loading" class="text-[13px] py-12 text-center" style="color: rgba(255,255,255,0.25);">加载中...</div>

    <div v-else-if="error" class="mb-6 px-4 py-3 rounded-lg text-[13px]" style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171;">
      {{ error }}
    </div>

    <template v-else>
      <div v-if="items.length === 0" class="text-[13px] py-12 text-center" style="color: rgba(255,255,255,0.25);">
        暂无媒体文件
      </div>
      <div v-else class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div
          v-for="m in items"
          :key="m.id"
          class="group rounded-xl overflow-hidden relative"
          style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);"
        >
          <div class="aspect-video flex items-center justify-center overflow-hidden" style="background: rgba(0,0,0,0.3);">
            <img
              v-if="m.mime_type?.startsWith('image/')"
              :src="`${apiBase}/../../media/id/${m.id}`"
              class="w-full h-full object-cover"
              loading="lazy"
            />
            <div v-else class="text-[11px] text-center px-2" style="color: rgba(255,255,255,0.25);">
              {{ m.mime_type || 'unknown' }}
            </div>
          </div>
          <div class="p-2.5">
            <div class="text-[12px] text-white truncate" :title="m.filename">{{ m.filename }}</div>
            <div class="text-[10px] mt-0.5 flex items-center justify-between" style="color: rgba(255,255,255,0.25);">
              <span>{{ formatSize(m.size) }}</span>
              <a
                :href="`${apiBase}/../../media/id/${m.id}`"
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
          :style="p === page ? 'background: rgba(5,150,105,0.15); color: #34d399;' : 'background: rgba(255,255,255,0.02); color: rgba(255,255,255,0.35);'"
        >
          {{ p }}
        </button>
      </div>
    </template>

    <!-- Delete Confirm -->
    <div
      v-if="deleteTarget"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
      @click.self="deleteTarget = null"
    >
      <div class="rounded-2xl p-6 w-full max-w-sm mx-4" style="background: #11161e; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
        <p class="text-[14px] text-white mb-1">确认删除</p>
        <p class="text-[12px] mb-5" style="color: rgba(255,255,255,0.3);">确定要删除文件 "{{ deleteTarget.filename }}" 吗？此操作不可撤销。</p>
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

const getHeaders = (json = true) => {
  const token = import.meta.client ? localStorage.getItem('admin_token') : null;
  const h: Record<string, string> = {};
  if (json) h['Content-Type'] = 'application/json';
  if (token) h['Authorization'] = `Bearer ${token}`;
  return h;
};

interface MediaItem {
  id: number;
  filename: string;
  mime_type: string;
  url: string;
  size: number;
  thumbnail_url: string | null;
}

const items = ref<MediaItem[]>([]);
const loading = ref(true);
const error = ref('');
const page = ref(1);
const totalPages = ref(1);

const fetchMedia = async () => {
  loading.value = true;
  error.value = '';
  try {
    const data = await $fetch<{ items: MediaItem[]; total: number; pages: number }>(
      `${apiBase}/admin/media?page=${page.value}&size=24`,
      { headers: getHeaders() }
    );
    items.value = data.items;
    totalPages.value = data.pages;
  } catch (e: any) {
    error.value = e?.data?.detail || '加载媒体列表失败';
  } finally {
    loading.value = false;
  }
};

const uploading = ref(false);
const uploadError = ref('');

const doUpload = async (e: Event) => {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  uploading.value = true;
  uploadError.value = '';
  try {
    const token = import.meta.client ? localStorage.getItem('admin_token') : null;
    const fd = new FormData();
    fd.append('file', file);
    await $fetch(`${apiBase}/admin/media/upload`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: fd,
    });
    page.value = 1;
    await fetchMedia();
  } catch (e: any) {
    uploadError.value = e?.data?.detail || '上传失败';
  } finally {
    uploading.value = false;
    input.value = '';
  }
};

const deleteTarget = ref<MediaItem | null>(null);
const confirmDelete = (m: MediaItem) => { deleteTarget.value = m; };
const doDelete = async () => {
  if (!deleteTarget.value) return;
  try {
    await $fetch(`${apiBase}/admin/media/${deleteTarget.value.id}`, {
      method: 'DELETE', headers: getHeaders(),
    });
    deleteTarget.value = null;
    await fetchMedia();
  } catch {}
};

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

onMounted(fetchMedia);
</script>
