<template>
  <div>
    <!-- Trigger area (model mode only) -->
    <div v-if="mode === 'model'" class="flex items-start gap-4">
      <div v-if="previewUrl" class="relative flex-shrink-0">
        <img :src="previewUrl" class="w-32 h-20 rounded-lg object-cover" style="background: #ffffff;" />
        <button
          type="button" @click="clear"
          class="absolute -top-2 -right-2 w-5 h-5 rounded-full border-none cursor-pointer flex items-center justify-center text-[11px]"
          style="background: #ef4444; color: white;"
        >&times;</button>
      </div>
      <div
        class="flex-shrink-0 w-32 h-20 rounded-lg flex flex-col items-center justify-center gap-1 cursor-pointer transition-colors border border-dashed text-[11px]"
        style="background: #ffffff; border-color: #d1d5db; color: #94a3b8;"
        @click="openPicker"
      >
        <span class="text-[16px]">&#8593;</span>
        <span>选择图片</span>
      </div>
    </div>

    <!-- Picker Modal -->
    <Teleport to="body">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center"
        style="background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);"
        @click.self="show = false"
      >
        <div
          class="rounded-2xl p-6 w-full max-w-2xl mx-4"
          style="background: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 20px 60px rgba(0,0,0,0.5);"
        >
          <!-- Tabs -->
          <div class="flex items-center gap-4 mb-5">
            <button
              type="button"
              @click="tab = 'library'"
              class="text-[14px] border-none bg-transparent cursor-pointer pb-1.5 transition-colors"
              :style="tab === 'library' ? 'color: #2563eb; border-bottom: 2px solid #2563eb;' : 'color: #94a3b8;'"
            >媒体库</button>
            <button
              type="button"
              @click="tab = 'upload'"
              class="text-[14px] border-none bg-transparent cursor-pointer pb-1.5 transition-colors"
              :style="tab === 'upload' ? 'color: #2563eb; border-bottom: 2px solid #2563eb;' : 'color: #94a3b8;'"
            >本地上传</button>
            <button
              type="button"
              @click="show = false"
              class="ml-auto text-[13px] border-none cursor-pointer px-3 py-1.5 rounded-lg"
              style="color: #64748b; background: #f1f5f9;"
            >取消</button>
          </div>

          <!-- Media Library Tab -->
          <div v-if="tab === 'library'">
            <div v-if="libLoading" class="text-[13px] py-10 text-center" style="color: #94a3b8;">加载中...</div>

            <!-- Category grid view -->
            <template v-else-if="pickerView === 'categories'">
              <div v-if="pickerCategories.length === 0" class="text-[13px] py-10 text-center" style="color: #94a3b8;">暂无媒体</div>
              <div v-else class="grid grid-cols-3 gap-3 max-h-[360px] overflow-y-auto">
                <!-- All media -->
                <div
                  class="rounded-xl overflow-hidden cursor-pointer transition-all duration-200 hover:translate-y-[-1px]"
                  style="background: #ffffff; border: 1px solid #e5e7eb;"
                  @click="enterPickerCategory(null)"
                >
                  <div class="aspect-[4/3] flex items-center justify-center" style="background: linear-gradient(135deg, #eff6ff, #bfdbfe);">
                    <span class="text-[28px]">&#128444;</span>
                  </div>
                  <div class="p-2.5">
                    <div class="text-[13px] font-medium" style="color: #1e293b;">全部媒体</div>
                    <div class="text-[11px] mt-0.5" style="color: #94a3b8;">{{ pickerTotalCount }} 个文件</div>
                  </div>
                </div>
                <!-- Category cards -->
                <div
                  v-for="cat in pickerCategories"
                  :key="cat.name"
                  class="rounded-xl overflow-hidden cursor-pointer transition-all duration-200 hover:translate-y-[-1px]"
                  style="background: #ffffff; border: 1px solid #e5e7eb;"
                  @click="enterPickerCategory(cat.name)"
                >
                  <div class="aspect-[4/3] flex items-center justify-center overflow-hidden" style="background: #f1f5f9;">
                    <img
                      v-if="cat.cover_image_id"
                      :src="`${apiBase}/../../media/id/${cat.cover_image_id}`"
                      class="w-full h-full object-cover"
                    />
                    <span v-else class="text-[28px]">&#128193;</span>
                  </div>
                  <div class="p-2.5">
                    <div class="text-[13px] font-medium truncate" style="color: #1e293b;">{{ cat.name }}</div>
                    <div class="text-[11px] mt-0.5" style="color: #94a3b8;">{{ cat.count }} 个文件</div>
                  </div>
                </div>
              </div>
            </template>

            <!-- Category detail view (media grid) -->
            <template v-else>
              <div class="flex items-center gap-2 mb-3">
                <button
                  type="button"
                  @click="pickerView = 'categories'"
                  class="text-[12px] border-none cursor-pointer px-2.5 py-1 rounded-lg"
                  style="color: #64748b; background: #f1f5f9;"
                >&larr; 返回</button>
                <span class="text-[14px] font-medium" style="color: #1e293b;">{{ pickerActiveCategory || '全部媒体' }}</span>
              </div>
              <!-- Search -->
              <div class="flex gap-2 mb-3">
                <input
                  v-model="pickerSearch" placeholder="搜索..."
                  class="flex-1 py-1.5 px-3 text-[12px] outline-none rounded-lg"
                  style="color: #1e293b; background: #ffffff; border: 1px solid #d1d5db;"
                  @keyup.enter="pickerPage = 1; fetchPickerMedia()"
                />
                <button
                  type="button"
                  @click="pickerPage = 1; fetchPickerMedia()"
                  class="text-[11px] border-none cursor-pointer px-3 py-1.5 rounded-lg"
                  style="color: #2563eb; background: rgba(37,99,235,0.08);"
                >搜索</button>
              </div>
              <!-- Media grid -->
              <div v-if="pickerMediaItems.length === 0" class="text-[13px] py-10 text-center" style="color: #94a3b8;">暂无媒体</div>
              <div v-else class="grid grid-cols-4 gap-3 max-h-[300px] overflow-y-auto">
                <div
                  v-for="item in pickerMediaItems"
                  :key="item.id"
                  class="relative rounded-lg overflow-hidden cursor-pointer border-2 transition-colors"
                  :style="pickerSelectedId === item.id ? 'border-color: #2563eb;' : 'border-color: transparent;'"
                  @click="pickerSelectedId = item.id"
                >
                  <img
                    v-if="item.mime_type?.startsWith('image/')"
                    :src="`${apiBase}/../../media/id/${item.id}`"
                    class="w-full h-24 object-cover"
                  />
                  <div v-else class="w-full h-24 flex items-center justify-center text-[11px]" style="color: #94a3b8; background: #f1f5f9;">
                    {{ item.mime_type || 'unknown' }}
                  </div>
                  <div
                    v-if="pickerSelectedId === item.id"
                    class="absolute top-1.5 right-1.5 w-5 h-5 rounded-full flex items-center justify-center"
                    style="background: #2563eb; color: white; font-size: 12px;"
                  >&#10003;</div>
                </div>
              </div>
              <!-- Pagination -->
              <div v-if="pickerTotalPages > 1" class="flex justify-center gap-2 mt-4">
                <button
                  v-for="p in pickerTotalPages"
                  :key="p"
                  type="button"
                  @click="pickerPage = p; fetchPickerMedia()"
                  class="text-[12px] border-none cursor-pointer w-7 h-7 rounded-lg transition-colors"
                  :style="p === pickerPage ? 'background: rgba(37,99,235,0.15); color: #60a5fa;' : 'background: #f1f5f9; color: #94a3b8;'"
                >{{ p }}</button>
              </div>
              <div class="flex justify-end mt-4">
                <button
                  type="button"
                  @click="confirmPickerSelection"
                  :disabled="!pickerSelectedId"
                  class="text-[13px] font-medium text-white border-none cursor-pointer px-5 py-2 rounded-lg transition-all disabled:opacity-40"
                  style="background: linear-gradient(135deg, #2563eb, #1d4ed8);"
                >确定</button>
              </div>
            </template>
          </div>

          <!-- Upload Tab -->
          <div v-if="tab === 'upload'">
            <div class="flex flex-col items-center gap-4 py-8">
              <div
                class="w-full max-w-[300px] h-40 rounded-xl flex flex-col items-center justify-center gap-2 cursor-pointer transition-colors border-2 border-dashed"
                :style="uploading ? 'opacity: 0.5; pointer-events: none; border-color: #d1d5db; color: #94a3b8; background: #f8fafc;' : 'border-color: #d1d5db; color: #94a3b8; background: #f8fafc;'"
                @click="triggerPickerUpload"
              >
                <span v-if="uploading" class="w-6 h-6 border-2 border-t-transparent rounded-full animate-spin" style="border-color: #94a3b8; border-top-color: transparent;"></span>
                <span v-else class="text-[28px]">&#8593;</span>
                <span class="text-[12px]">{{ uploading ? '上传中...' : '点击上传图片' }}</span>
              </div>
              <input ref="pickerFileInput" type="file" accept="image/*" class="hidden" @change="onPickerUpload" />
              <div v-if="uploadError" class="text-[12px]" style="color: #f87171;">{{ uploadError }}</div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue?: number | null
  /** 'model' for v-model (cover image), 'insert' for callback (rich text editor) */
  mode?: 'model' | 'insert'
}>(), { modelValue: null, mode: 'model' })

const emit = defineEmits<{
  'update:modelValue': [id: number | null]
  'select': [item: { id: number; url: string }]
}>()

const { api, apiBase } = useAdminApi()

const show = ref(false)
const tab = ref<'library' | 'upload'>('library')

// Preview computed from modelValue
const previewUrl = computed(() => {
  if (!props.modelValue) return null
  return `${apiBase}/../../media/id/${props.modelValue}`
})

// -- Category view ------------------------------------------------------------

interface PickerCategory {
  name: string
  count: number
  cover_image_id: number | null
}

const pickerCategories = ref<PickerCategory[]>([])
const pickerTotalCount = ref(0)
const pickerView = ref<'categories' | 'detail'>('categories')
const pickerActiveCategory = ref<string | null>(null)

const fetchPickerCategories = async () => {
  try {
    pickerCategories.value = await api<PickerCategory[]>('/admin/media/categories')
    pickerTotalCount.value = pickerCategories.value.reduce((s, c) => s + c.count, 0)
  } catch {
    pickerCategories.value = []
  }
}

const enterPickerCategory = (name: string | null) => {
  pickerActiveCategory.value = name
  pickerSearch.value = ''
  pickerPage.value = 1
  pickerSelectedId.value = null
  pickerView.value = 'detail'
  fetchPickerMedia()
}

// -- Media grid ---------------------------------------------------------------

interface MediaItem {
  id: number
  filename: string
  mime_type: string
  url: string
  size: number
  thumbnail_url: string | null
}

const pickerMediaItems = ref<MediaItem[]>([])
const pickerSelectedId = ref<number | null>(null)
const pickerPage = ref(1)
const pickerTotalPages = ref(1)
const pickerSearch = ref('')
const libLoading = ref(false)

const fetchPickerMedia = async () => {
  libLoading.value = true
  try {
    const params = new URLSearchParams({ page: String(pickerPage.value), size: '20' })
    if (pickerActiveCategory.value) params.set('category', pickerActiveCategory.value)
    if (pickerSearch.value) params.set('q', pickerSearch.value)

    const data = await api<{ items: MediaItem[]; total: number; pages: number }>(`/admin/media?${params}`)
    pickerMediaItems.value = data.items
    pickerTotalPages.value = data.pages
  } catch (e: any) {
    console.error('Media fetch error:', e)
  } finally {
    libLoading.value = false
  }
}

const confirmPickerSelection = () => {
  if (!pickerSelectedId.value) return
  const url = `${apiBase}/../../media/id/${pickerSelectedId.value}`
  if (props.mode === 'insert') {
    emit('select', { id: pickerSelectedId.value, url })
  } else {
    emit('update:modelValue', pickerSelectedId.value)
  }
  show.value = false
}

// -- Upload -------------------------------------------------------------------

const pickerFileInput = ref<HTMLInputElement>()
const uploading = ref(false)
const uploadError = ref('')

const triggerPickerUpload = () => {
  pickerFileInput.value?.click()
}

const onPickerUpload = async (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  uploading.value = true
  uploadError.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api<{ id: number; url: string }>('/admin/media/upload', { method: 'POST', body: fd })
    if (props.mode === 'insert') {
      emit('select', { id: res.id, url: `${apiBase}/../../media/id/${res.id}` })
    } else {
      emit('update:modelValue', res.id)
    }
    show.value = false
  } catch {
    uploadError.value = '上传失败'
  } finally {
    uploading.value = false
    input.value = ''
  }
}

// -- Open / clear -------------------------------------------------------------

const openPicker = () => {
  show.value = true
  tab.value = 'library'
  pickerView.value = 'categories'
  pickerSelectedId.value = null
  pickerSearch.value = ''
  fetchPickerCategories()
}

const clear = () => {
  emit('update:modelValue', null)
}

defineExpose({ openPicker })
</script>
