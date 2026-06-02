<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <span class="text-[11px] tracking-wider uppercase" style="color: #94a3b8;">幻灯片 ({{ slides.length }})</span>
      <button
        type="button" @click="addSlide"
        class="text-[11px] border-none cursor-pointer px-3 py-1 rounded-lg transition-colors"
        style="color: #60a5fa; background: rgba(37,99,235,0.08);"
      >+ 添加幻灯片</button>
    </div>

    <!-- Slide list -->
    <div v-for="(slide, i) in slides" :key="i" class="rounded-xl p-4 space-y-3" style="background: #f8fafc; border: 1px solid #e2e8f0;">
      <div class="flex items-center justify-between">
        <span class="text-[11px] font-medium" style="color: #64748b;">幻灯片 #{{ i + 1 }}</span>
        <div class="flex items-center gap-2">
          <button v-if="i > 0" type="button" @click="moveSlide(i, -1)"
            class="text-[10px] border-none cursor-pointer px-2 py-0.5 rounded" style="background: #e2e8f0; color: #64748b;">↑</button>
          <button v-if="i < slides.length - 1" type="button" @click="moveSlide(i, 1)"
            class="text-[10px] border-none cursor-pointer px-2 py-0.5 rounded" style="background: #e2e8f0; color: #64748b;">↓</button>
          <button v-if="slides.length > 1" type="button" @click="removeSlide(i)"
            class="text-[10px] border-none cursor-pointer px-2 py-0.5 rounded" style="background: rgba(239,68,68,0.1); color: #f87171;">删除</button>
        </div>
      </div>

      <!-- Image -->
      <div>
        <label class="text-[10px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">背景图片</label>
        <AdminMediaPicker
          :key="`slide-img-${i}`"
          :model-value="slide.image_id"
          @update:model-value="(mediaId: number | null) => updateSlide(i, 'image_id', mediaId)"
        />
      </div>

      <!-- Title -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-[10px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">标题 (中文)</label>
          <input
            :value="slide.title_zh || ''"
            @input="updateSlide(i, 'title_zh', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border"
            style="border-color: #d1d5db; color: #1e293b;"
            placeholder="金捷利AI绿色空间运营商"
          />
        </div>
        <div>
          <label class="text-[10px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">标题 (英文)</label>
          <input
            :value="slide.title_en || ''"
            @input="updateSlide(i, 'title_en', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border"
            style="border-color: #d1d5db; color: #1e293b;"
            placeholder="Smart Buildings, Smarter Future"
          />
        </div>
      </div>

      <!-- Subtitle -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-[10px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">副标题 (中文)</label>
          <textarea
            :value="slide.subtitle_zh || ''"
            @input="updateSlide(i, 'subtitle_zh', ($event.target as HTMLTextAreaElement).value)"
            rows="2" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border resize-none"
            style="border-color: #d1d5db; color: #1e293b;"
            placeholder="智能研发低碳算法..."
          ></textarea>
        </div>
        <div>
          <label class="text-[10px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">副标题 (英文)</label>
          <textarea
            :value="slide.subtitle_en || ''"
            @input="updateSlide(i, 'subtitle_en', ($event.target as HTMLTextAreaElement).value)"
            rows="2" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border resize-none"
            style="border-color: #d1d5db; color: #1e293b;"
            placeholder="Empowering smart building..."
          ></textarea>
        </div>
      </div>

      <!-- Buttons -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="text-[10px] tracking-wider uppercase" style="color: #94a3b8;">按钮</label>
          <button type="button" @click="addButton(i)"
            class="text-[10px] border-none cursor-pointer px-2 py-0.5 rounded"
            style="color: #60a5fa; background: rgba(37,99,235,0.08);">+ 按钮</button>
        </div>
        <div v-for="(btn, bi) in (slide.buttons || [])" :key="bi" class="grid grid-cols-7 gap-2 mb-2">
          <input
            :value="btn.label_zh || ''"
            @input="updateButton(i, bi, 'label_zh', ($event.target as HTMLInputElement).value)"
            class="col-span-2 py-1.5 px-2 text-[12px] outline-none rounded border"
            style="border-color: #d1d5db;" placeholder="按钮(中)"
          />
          <input
            :value="btn.label_en || ''"
            @input="updateButton(i, bi, 'label_en', ($event.target as HTMLInputElement).value)"
            class="col-span-2 py-1.5 px-2 text-[12px] outline-none rounded border"
            style="border-color: #d1d5db;" placeholder="Button(EN)"
          />
          <input
            :value="btn.link || ''"
            @input="updateButton(i, bi, 'link', ($event.target as HTMLInputElement).value)"
            class="col-span-2 py-1.5 px-2 text-[12px] outline-none rounded border"
            style="border-color: #d1d5db;" placeholder="/cooperation"
          />
          <button type="button" @click="removeButton(i, bi)"
            class="text-[11px] border-none cursor-pointer rounded" style="color: #f87171; background: rgba(239,68,68,0.08);">✕</button>
        </div>
        <p v-if="!slide.buttons?.length" class="text-[11px]" style="color: #94a3b8;">暂无按钮</p>
      </div>
    </div>

    <p v-if="!slides.length" class="text-[12px] py-6 text-center" style="color: #94a3b8;">
      暂无幻灯片，点击上方按钮添加
    </p>
  </div>
</template>

<script setup lang="ts">
interface SlideButton { label_zh: string; label_en: string; link: string }
interface Slide {
  image_id?: number
  title_zh?: string
  title_en?: string
  subtitle_zh?: string
  subtitle_en?: string
  buttons?: SlideButton[]
}

const props = defineProps<{ modelValue: Slide[] }>()
const emit = defineEmits<{ 'update:modelValue': [slides: Slide[]] }>()

const slides = ref<Slide[]>(JSON.parse(JSON.stringify(props.modelValue || [])))

watch(() => props.modelValue, (val) => {
  slides.value = JSON.parse(JSON.stringify(val || []))
}, { deep: true })

watch(slides, (val) => {
  emit('update:modelValue', JSON.parse(JSON.stringify(val)))
}, { deep: true })

function addSlide() {
  slides.value.push({ title_zh: '', title_en: '', subtitle_zh: '', subtitle_en: '', buttons: [] })
}

function removeSlide(i: number) { slides.value.splice(i, 1) }

function moveSlide(i: number, dir: number) {
  const target = i + dir
  if (target < 0 || target >= slides.value.length) return
  const tmp = slides.value[i]
  slides.value[i] = slides.value[target]
  slides.value[target] = tmp
}

function updateSlide(i: number, key: string, value: any) {
  slides.value[i] = { ...slides.value[i], [key]: value }
}

function addButton(si: number) {
  const s = slides.value[si]
  s.buttons = [...(s.buttons || []), { label_zh: '', label_en: '', link: '' }]
}

function removeButton(si: number, bi: number) {
  const s = slides.value[si]
  s.buttons = (s.buttons || []).filter((_, i) => i !== bi)
}

function updateButton(si: number, bi: number, key: string, value: string) {
  const s = slides.value[si]
  const btns = [...(s.buttons || [])]
  btns[bi] = { ...btns[bi], [key]: value }
  s.buttons = btns
}
</script>
