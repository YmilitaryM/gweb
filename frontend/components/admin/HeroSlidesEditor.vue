<template>
  <div>
    <!-- Thumbnail strip -->
    <div class="flex items-center gap-2 mb-4 overflow-x-auto pb-2">
      <div
        v-for="(slide, i) in slides" :key="i"
        @click="activeIndex = i"
        class="flex-shrink-0 w-20 h-14 rounded-lg overflow-hidden border-2 cursor-pointer transition-all relative group"
        :class="activeIndex === i ? 'border-brand-600 shadow-md' : 'border-slate-200 hover:border-slate-300'"
      >
        <img
          v-if="slide.image_id"
          :src="`${apiBase}/../../media/id/${slide.image_id}`"
          class="w-full h-full object-cover"
        />
        <div v-else class="w-full h-full flex items-center justify-center text-xs font-bold bg-slate-100 text-slate-400">
          {{ i + 1 }}
        </div>
        <button
          v-if="slides.length > 1"
          @click.stop="removeSlide(i)"
          class="absolute top-0 right-0 w-4 h-4 bg-red-500 text-white text-[10px] flex items-center justify-center rounded-bl opacity-0 group-hover:opacity-100 transition-opacity"
        >×</button>
      </div>
      <button
        @click="addSlide"
        class="flex-shrink-0 w-20 h-14 rounded-lg border-2 border-dashed border-slate-300 flex items-center justify-center text-slate-400 hover:border-brand-400 hover:text-brand-500 transition-colors cursor-pointer"
      >
        <span class="text-2xl leading-none">+</span>
      </button>
    </div>

    <!-- Active slide editor -->
    <div v-if="activeSlide" class="rounded-xl p-5 space-y-4" style="background: #f8fafc; border: 1px solid #e2e8f0;">
      <div class="flex items-center gap-2 text-sm font-medium" style="color: #1e293b;">
        幻灯片 {{ activeIndex + 1 }} / {{ slides.length }}
        <span class="text-[11px] font-normal" style="color: #94a3b8;">（{{ slides.length }} 张，点击上方缩略图切换）</span>
      </div>

      <!-- Image -->
      <AdminMediaPicker
        :key="`slide-${activeIndex}`"
        :model-value="activeSlide.image_id"
        @update:model-value="(id: number | null) => updateSlide(activeIndex, 'image_id', id)"
      />

      <!-- Title -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-[11px] font-medium mb-1 block" style="color: #64748b;">标题 (中文)</label>
          <input :value="activeSlide.title_zh || ''"
            @input="updateSlide(activeIndex, 'title_zh', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-sm outline-none rounded-lg border" style="border-color: #d1d5db;"
            placeholder="金捷利AI绿色空间运营商" />
        </div>
        <div>
          <label class="text-[11px] font-medium mb-1 block" style="color: #64748b;">标题 (英文)</label>
          <input :value="activeSlide.title_en || ''"
            @input="updateSlide(activeIndex, 'title_en', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-sm outline-none rounded-lg border" style="border-color: #d1d5db;"
            placeholder="Smart Buildings, Smarter Future" />
        </div>
      </div>

      <!-- Subtitle -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-[11px] font-medium mb-1 block" style="color: #64748b;">副标题 (中文)</label>
          <textarea :value="activeSlide.subtitle_zh || ''"
            @input="updateSlide(activeIndex, 'subtitle_zh', ($event.target as HTMLTextAreaElement).value)"
            rows="2" class="w-full py-2 px-3 text-sm outline-none rounded-lg border resize-none" style="border-color: #d1d5db;"
            placeholder="智能研发低碳算法与设备集群控制..."></textarea>
        </div>
        <div>
          <label class="text-[11px] font-medium mb-1 block" style="color: #64748b;">副标题 (英文)</label>
          <textarea :value="activeSlide.subtitle_en || ''"
            @input="updateSlide(activeIndex, 'subtitle_en', ($event.target as HTMLTextAreaElement).value)"
            rows="2" class="w-full py-2 px-3 text-sm outline-none rounded-lg border resize-none" style="border-color: #d1d5db;"
            placeholder="Empowering smart building operations..."></textarea>
        </div>
      </div>

      <!-- Buttons -->
      <div>
        <label class="text-[11px] font-medium mb-2 block" style="color: #64748b;">按钮</label>
        <div v-for="(btn, bi) in (activeSlide.buttons || [])" :key="bi" class="flex items-center gap-2 mb-2">
          <input :value="btn.label_zh || ''" @input="updateButton(activeIndex, bi, 'label_zh', ($event.target as HTMLInputElement).value)"
            class="flex-1 py-1.5 px-2 text-xs outline-none rounded border" style="border-color: #d1d5db;" placeholder="按钮文字(中)" />
          <input :value="btn.label_en || ''" @input="updateButton(activeIndex, bi, 'label_en', ($event.target as HTMLInputElement).value)"
            class="flex-1 py-1.5 px-2 text-xs outline-none rounded border" style="border-color: #d1d5db;" placeholder="Button(EN)" />
          <input :value="btn.link || ''" @input="updateButton(activeIndex, bi, 'link', ($event.target as HTMLInputElement).value)"
            class="w-32 py-1.5 px-2 text-xs outline-none rounded border" style="border-color: #d1d5db;" placeholder="链接" />
          <button type="button" @click="removeButton(activeIndex, bi)"
            class="w-6 h-6 text-xs rounded-full border-none cursor-pointer flex items-center justify-center"
            style="color: #f87171; background: rgba(239,68,68,0.08);">×</button>
        </div>
        <button type="button" @click="addButton(activeIndex)"
          class="text-[11px] border-none cursor-pointer px-3 py-1 rounded-lg"
          style="color: #60a5fa; background: rgba(37,99,235,0.08);">+ 添加按钮</button>
      </div>

      <!-- Reorder -->
      <div class="flex gap-2 pt-2 border-t" style="border-color: #e2e8f0;">
        <button type="button" @click="moveSlide(activeIndex, -1)" :disabled="activeIndex === 0"
          class="text-[11px] border-none cursor-pointer px-3 py-1 rounded disabled:opacity-30"
          :style="activeIndex === 0 ? 'background: #f1f5f9; color: #94a3b8;' : 'background: #e2e8f0; color: #64748b;'">← 前移</button>
        <button type="button" @click="moveSlide(activeIndex, 1)" :disabled="activeIndex === slides.length - 1"
          class="text-[11px] border-none cursor-pointer px-3 py-1 rounded disabled:opacity-30"
          :style="activeIndex === slides.length - 1 ? 'background: #f1f5f9; color: #94a3b8;' : 'background: #e2e8f0; color: #64748b;'">后移 →</button>
      </div>
    </div>

    <p v-if="!slides.length" class="text-sm py-8 text-center" style="color: #94a3b8;">
      还没有幻灯片，点击上方 <span class="text-brand-600">+</span> 添加
    </p>
  </div>
</template>

<script setup lang="ts">
interface SlideButton { label_zh: string; label_en: string; link: string }
interface Slide {
  image_id?: number
  title_zh?: string; title_en?: string
  subtitle_zh?: string; subtitle_en?: string
  buttons?: SlideButton[]
}

const props = defineProps<{ modelValue: Slide[] }>()
const emit = defineEmits<{ 'update:modelValue': [slides: Slide[]] }>()

const apiBase = useRuntimeConfig().public.apiBase

const slides = ref<Slide[]>(JSON.parse(JSON.stringify(props.modelValue || [])))
const activeIndex = ref(0)

watch(() => props.modelValue, (val) => {
  slides.value = JSON.parse(JSON.stringify(val || []))
  if (activeIndex.value >= slides.value.length) activeIndex.value = Math.max(0, slides.value.length - 1)
}, { deep: true })

watch(slides, (val) => {
  emit('update:modelValue', JSON.parse(JSON.stringify(val)))
}, { deep: true })

const activeSlide = computed(() => slides.value[activeIndex.value])

function addSlide() {
  slides.value.push({ title_zh: '', title_en: '', subtitle_zh: '', subtitle_en: '', buttons: [] })
  activeIndex.value = slides.value.length - 1
}

function removeSlide(i: number) {
  slides.value.splice(i, 1)
  if (activeIndex.value >= slides.value.length) activeIndex.value = Math.max(0, slides.value.length - 1)
}

function moveSlide(i: number, dir: number) {
  const target = i + dir
  if (target < 0 || target >= slides.value.length) return
  const tmp = slides.value[i]; slides.value[i] = slides.value[target]; slides.value[target] = tmp
  activeIndex.value = target
}

function updateSlide(i: number, key: string, value: any) {
  slides.value[i] = { ...slides.value[i], [key]: value }
}

function addButton(si: number) {
  const s = slides.value[si]; s.buttons = [...(s.buttons || []), { label_zh: '', label_en: '', link: '' }]
}
function removeButton(si: number, bi: number) {
  const s = slides.value[si]; s.buttons = (s.buttons || []).filter((_, i) => i !== bi)
}
function updateButton(si: number, bi: number, key: string, value: string) {
  const btns = [...(slides.value[si].buttons || [])]; btns[bi] = { ...btns[bi], [key]: value }
  slides.value[si].buttons = btns
}
</script>
