<template>
  <div class="space-y-4">
    <!-- hero: slides editor (delegated) -->
    <template v-if="blockType === 'hero'">
      <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">幻灯片</label>
      <AdminHeroSlidesEditor v-model="slides" />
    </template>

    <!-- richtext: simple textarea with RichTextEditor hint -->
    <template v-else-if="blockType === 'richtext'">
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">内容 (中文/HTML)</label>
          <textarea :model-value="content.html_content_zh || ''" @input="setContent('html_content_zh', ($event.target as HTMLTextAreaElement).value)"
            rows="8" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border resize-y font-mono"
            style="border-color: #d1d5db; color: #1e293b;"></textarea>
        </div>
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">内容 (英文/HTML)</label>
          <textarea :model-value="content.html_content_en || ''" @input="setContent('html_content_en', ($event.target as HTMLTextAreaElement).value)"
            rows="8" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border resize-y font-mono"
            style="border-color: #d1d5db; color: #1e293b;"></textarea>
        </div>
      </div>
      <p class="text-[11px] mt-1" style="color: #94a3b8;">支持 HTML 标签。可使用管理端 RichTextEditor 编辑后粘贴。</p>
    </template>

    <!-- stats_counter: key-value list -->
    <template v-else-if="blockType === 'stats_counter'">
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">标题 (中文)</label>
          <input :value="content.title_zh || ''" @input="setContent('title_zh', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;">
        </div>
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">标题 (英文)</label>
          <input :value="content.title_en || ''" @input="setContent('title_en', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;">
        </div>
      </div>
      <div class="grid grid-cols-2 gap-3 mb-4">
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">副标题 (中文)</label>
          <input :value="content.subtitle_zh || ''" @input="setContent('subtitle_zh', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;">
        </div>
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">副标题 (英文)</label>
          <input :value="content.subtitle_en || ''" @input="setContent('subtitle_en', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;">
        </div>
      </div>
      <label class="text-[11px] tracking-wider uppercase mb-2 block" style="color: #94a3b8;">统计数据</label>
      <div v-for="(stat, i) in statsList" :key="i" class="grid grid-cols-5 gap-2 mb-2">
        <input :value="stat.label" @input="updateStat(i, 'label', ($event.target as HTMLInputElement).value)"
          class="col-span-2 py-1.5 px-2 text-[12px] outline-none rounded border" placeholder="标签" style="border-color: #d1d5db;">
        <input :value="stat.value" @input="updateStat(i, 'value', ($event.target as HTMLInputElement).value)"
          class="col-span-2 py-1.5 px-2 text-[12px] outline-none rounded border" placeholder="数值" style="border-color: #d1d5db;">
        <button type="button" @click="removeStat(i)" class="text-[11px] border-none cursor-pointer rounded" style="color: #f87171; background: rgba(239,68,68,0.08);">✕</button>
      </div>
      <button type="button" @click="addStat" class="text-[11px] border-none cursor-pointer px-3 py-1 rounded-lg"
        style="color: #60a5fa; background: rgba(37,99,235,0.08);">+ 添加数据</button>
    </template>

    <!-- cta_banner: simple form -->
    <template v-else-if="blockType === 'cta_banner'">
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">标题 (中文)</label>
          <input :value="content.title_zh || ''" @input="setContent('title_zh', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;">
        </div>
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">标题 (英文)</label>
          <input :value="content.title_en || ''" @input="setContent('title_en', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;">
        </div>
      </div>
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">描述 (中文)</label>
          <textarea :value="content.description_zh || ''" @input="setContent('description_zh', ($event.target as HTMLTextAreaElement).value)"
            rows="2" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border resize-none" style="border-color: #d1d5db;"></textarea>
        </div>
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">描述 (英文)</label>
          <textarea :value="content.description_en || ''" @input="setContent('description_en', ($event.target as HTMLTextAreaElement).value)"
            rows="2" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border resize-none" style="border-color: #d1d5db;"></textarea>
        </div>
      </div>
      <div class="grid grid-cols-3 gap-3">
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">按钮文字 (中文)</label>
          <input :value="content.button_zh || ''" @input="setContent('button_zh', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;">
        </div>
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">按钮文字 (英文)</label>
          <input :value="content.button_en || ''" @input="setContent('button_en', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;">
        </div>
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">链接</label>
          <input :value="content.button_link || ''" @input="setContent('button_link', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" placeholder="/contact" style="border-color: #d1d5db;">
        </div>
      </div>
    </template>

    <!-- contact_form: simple config -->
    <template v-else-if="blockType === 'contact_form'">
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div><label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">标题 (中文)</label>
          <input :value="content.title_zh || ''" @input="setContent('title_zh', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;"></div>
        <div><label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">标题 (英文)</label>
          <input :value="content.title_en || ''" @input="setContent('title_en', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;"></div>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div><label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">按钮文字 (中文)</label>
          <input :value="content.submit_button_zh || ''" @input="setContent('submit_button_zh', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;"></div>
        <div><label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">按钮文字 (英文)</label>
          <input :value="content.submit_button_en || ''" @input="setContent('submit_button_en', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;"></div>
      </div>
    </template>

    <!-- news_list / product_cards: simple title config -->
    <template v-else-if="blockType === 'news_list' || blockType === 'product_cards'">
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">标题 (中文)</label>
          <input :value="content.title_zh || ''" @input="setContent('title_zh', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;">
        </div>
        <div>
          <label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">标题 (英文)</label>
          <input :value="content.title_en || ''" @input="setContent('title_en', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;">
        </div>
      </div>
      <div v-if="blockType === 'news_list'" class="grid grid-cols-3 gap-3">
        <div><label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">显示数量</label>
          <input :value="content.count || 6" @input="setContent('count', Number(($event.target as HTMLInputElement).value))"
            type="number" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;"></div>
        <div class="flex items-end pb-1"><label class="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" :checked="content.show_image !== false" @change="setContent('show_image', ($event.target as HTMLInputElement).checked)"
            class="accent-blue-600"><span class="text-[12px]" style="color: #64748b;">显示图片</span></label></div>
        <div class="flex items-end pb-1"><label class="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" :checked="content.show_date !== false" @change="setContent('show_date', ($event.target as HTMLInputElement).checked)"
            class="accent-blue-600"><span class="text-[12px]" style="color: #64748b;">显示日期</span></label></div>
      </div>
    </template>

    <!-- solution_cards: tab titles only (tabs managed via seed/admin) -->
    <template v-else-if="blockType === 'solution_cards'">
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div><label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">标题 (中文)</label>
          <input :value="content.title_zh || ''" @input="setContent('title_zh', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;"></div>
        <div><label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">标题 (英文)</label>
          <input :value="content.title_en || ''" @input="setContent('title_en', ($event.target as HTMLInputElement).value)"
            class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border" style="border-color: #d1d5db;"></div>
      </div>
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div><label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">副标题 (中文)</label>
          <textarea :value="content.subtitle_zh || ''" @input="setContent('subtitle_zh', ($event.target as HTMLTextAreaElement).value)"
            rows="2" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border resize-none" style="border-color: #d1d5db;"></textarea></div>
        <div><label class="text-[11px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">副标题 (英文)</label>
          <textarea :value="content.subtitle_en || ''" @input="setContent('subtitle_en', ($event.target as HTMLTextAreaElement).value)"
            rows="2" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg border resize-none" style="border-color: #d1d5db;"></textarea></div>
      </div>
      <p class="text-[11px]" style="color: #94a3b8;">Tab 内容（方案详情）需通过 JSON 编辑。点击下方「高级模式」切换。</p>
    </template>

    <!-- Fallback: raw JSON for unknown types -->
    <template v-else>
      <div>
        <label class="text-[11px] tracking-wider uppercase mb-1.5 block" style="color: #94a3b8;">Content (JSON)</label>
        <textarea
          :value="contentStr"
          @input="emit('update:contentStr', ($event.target as HTMLTextAreaElement).value)"
          rows="6" class="w-full py-2 px-3 text-[13px] outline-none rounded-lg font-mono resize-y"
          style="background: #ffffff; border: 1px solid #d1d5db; color: #1e293b;"
          placeholder='{}'
        ></textarea>
      </div>
    </template>

    <!-- Toggle: Advanced JSON mode -->
    <div class="pt-2 border-t" style="border-color: #e2e8f0;">
      <button type="button" @click="showAdvanced = !showAdvanced"
        class="text-[10px] border-none bg-transparent cursor-pointer" style="color: #94a3b8;">
        {{ showAdvanced ? '收起高级模式' : '高级模式 (JSON)' }}
      </button>
      <div v-if="showAdvanced" class="mt-3 space-y-3">
        <div>
          <label class="text-[10px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">Config (JSON)</label>
          <textarea
            :value="configStr"
            @input="emit('update:configStr', ($event.target as HTMLTextAreaElement).value)"
            rows="4" class="w-full py-2 px-3 text-[12px] outline-none rounded-lg font-mono resize-y"
            style="background: #f8fafc; border: 1px solid #d1d5db; color: #1e293b;" placeholder='{}'
          ></textarea>
        </div>
        <div>
          <label class="text-[10px] tracking-wider uppercase mb-1 block" style="color: #94a3b8;">Content (JSON 覆盖)</label>
          <textarea
            :value="contentStr"
            @input="emit('update:contentStr', ($event.target as HTMLTextAreaElement).value)"
            rows="6" class="w-full py-2 px-3 text-[12px] outline-none rounded-lg font-mono resize-y"
            style="background: #f8fafc; border: 1px solid #d1d5db; color: #1e293b;" placeholder='{}'
          ></textarea>
        </div>
        <p class="text-[10px]" style="color: #f87171;">高级模式下修改的内容会覆盖可视化编辑器的数据</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  blockType: string
  content: Record<string, any>
  configStr: string
  contentStr: string
}>()

const emit = defineEmits<{
  'update:content': [content: Record<string, any>]
  'update:configStr': [value: string]
  'update:contentStr': [value: string]
}>()

const showAdvanced = ref(false)

// For hero type
const slides = computed({
  get: () => props.content?.slides || [],
  set: (val) => emit('update:content', { ...props.content, slides: val }),
})

// For stats_counter type
const statsList = computed({
  get: () => props.content?.stats || [],
  set: (val) => emit('update:content', { ...props.content, stats: val }),
})

function setContent(key: string, value: any) {
  emit('update:content', { ...props.content, [key]: value })
}

function addStat() {
  const list = [...(props.content?.stats || []), { label: '', value: '' }]
  emit('update:content', { ...props.content, stats: list })
}

function removeStat(i: number) {
  const list = (props.content?.stats || []).filter((_: any, idx: number) => idx !== i)
  emit('update:content', { ...props.content, stats: list })
}

function updateStat(i: number, key: string, value: string) {
  const list = [...(props.content?.stats || [])]
  list[i] = { ...list[i], [key]: value }
  emit('update:content', { ...props.content, stats: list })
}
</script>
