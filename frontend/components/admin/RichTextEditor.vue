<template>
  <div class="rich-editor" style="border: 1px solid #d1d5db; border-radius: 8px; overflow: hidden;">
    <div v-if="editor" class="flex flex-wrap items-center gap-0.5 px-2 py-1.5" style="background: #f8fafc; border-bottom: 1px solid #e5e7eb;">
      <!-- Headings -->
      <button type="button" title="正文" @click="editor.chain().focus().setParagraph().run()"
        class="tool-btn" :class="{ 'is-active': editor.isActive('paragraph') }">P</button>
      <button type="button" title="标题1" @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
        class="tool-btn font-bold" :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }">H1</button>
      <button type="button" title="标题2" @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
        class="tool-btn font-bold" :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }">H2</button>
      <button type="button" title="标题3" @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
        class="tool-btn font-bold" :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }">H3</button>

      <span class="w-px h-5 mx-0.5" style="background: #e5e7eb;"></span>

      <!-- Formatting -->
      <button type="button" title="加粗" @click="editor.chain().focus().toggleBold().run()"
        class="tool-btn font-bold" :class="{ 'is-active': editor.isActive('bold') }">B</button>
      <button type="button" title="斜体" @click="editor.chain().focus().toggleItalic().run()"
        class="tool-btn italic" :class="{ 'is-active': editor.isActive('italic') }">I</button>
      <button type="button" title="删除线" @click="editor.chain().focus().toggleStrike().run()"
        class="tool-btn line-through" :class="{ 'is-active': editor.isActive('strike') }">S</button>

      <span class="w-px h-5 mx-0.5" style="background: #e5e7eb;"></span>

      <!-- Lists -->
      <button type="button" title="无序列表" @click="editor.chain().focus().toggleBulletList().run()"
        class="tool-btn" :class="{ 'is-active': editor.isActive('bulletList') }">&bull;</button>
      <button type="button" title="有序列表" @click="editor.chain().focus().toggleOrderedList().run()"
        class="tool-btn" :class="{ 'is-active': editor.isActive('orderedList') }">1.</button>
      <button type="button" title="引用" @click="editor.chain().focus().toggleBlockquote().run()"
        class="tool-btn" :class="{ 'is-active': editor.isActive('blockquote') }">&ldquo;</button>

      <span class="w-px h-5 mx-0.5" style="background: #e5e7eb;"></span>

      <!-- Horizontal rule -->
      <button type="button" title="分割线" @click="editor.chain().focus().setHorizontalRule().run()"
        class="tool-btn">&mdash;</button>

      <!-- Image upload -->
      <button type="button" title="插入图片" @click="openMediaPicker" class="tool-btn">&#128247;</button>

      <!-- Video embed -->
      <button type="button" title="插入视频" @click="insertVideo" class="tool-btn">&#9654;</button>
    </div>
    <EditorContent :editor="editor" class="editor-content" />
    <AdminMediaPicker ref="mediaPickerRef" mode="insert" @select="onMediaSelect" />
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import ImageExt from '@tiptap/extension-image'
import Placeholder from '@tiptap/extension-placeholder'
import Youtube from '@tiptap/extension-youtube'

// -- Resizable Image extension ------------------------------------------------

const ResizableImage = ImageExt.extend({
  addAttributes() {
    return {
      ...this.parent?.(),
      width: { default: null },
    }
  },

  addNodeView() {
    const component = this
    return ({ node, getPos, editor }) => {
      const wrap = document.createElement('div')
      Object.assign(wrap.style, { display: 'inline-block', position: 'relative', maxWidth: '100%', verticalAlign: 'bottom', width: 'fit-content' })
      wrap.contentEditable = 'false'
      wrap.draggable = true

      const img = document.createElement('img')
      img.src = node.attrs.src
      img.alt = node.attrs.alt || ''
      img.title = node.attrs.title || ''
      Object.assign(img.style, {
        display: 'block',
        maxWidth: '100%',
        width: node.attrs.width || 'auto',
        height: 'auto',
        pointerEvents: 'none',
      })
      wrap.appendChild(img)

      const handle = document.createElement('div')
      handle.style.cssText = 'position:absolute;right:0;bottom:0;width:10px;height:10px;cursor:nwse-resize;background:rgba(37,99,235,0.6);border-radius:2px 0 2px 0;z-index:2'
      handle.addEventListener('mousedown', (e) => {
        e.preventDefault()
        e.stopPropagation()
        const startX = e.clientX
        const startWidth = img.getBoundingClientRect().width
        const onMove = (ev: MouseEvent) => {
          const newWidth = Math.max(40, startWidth + (ev.clientX - startX))
          img.style.width = newWidth + 'px'
        }
        const onUp = () => {
          document.removeEventListener('mousemove', onMove)
          document.removeEventListener('mouseup', onUp)
          const final = img.style.width
          if (final && getPos() !== undefined) {
            const pos = getPos() as number
            editor.chain().setNodeSelection(pos).updateAttributes('image', { width: final }).run()
          }
        }
        document.addEventListener('mousemove', onMove)
        document.addEventListener('mouseup', onUp)
      })
      wrap.appendChild(handle)

      return {
        dom: wrap,
        contentDOM: null,
        ignoreMutation: () => true,
      }
    }
  },

  renderHTML({ node, HTMLAttributes }) {
    const w = node.attrs.width
    const style = [w ? `width:${w};height:auto;` : '', 'display:block;max-width:100%;'].join(';')
    return ['img', { ...HTMLAttributes, style }]
  },

  parseHTML() {
    return [{ tag: 'img' }]
  },
})

// ---------------------------------------------------------------------------

const props = withDefaults(defineProps<{
  modelValue?: string
  placeholder?: string
}>(), {
  modelValue: '',
  placeholder: '输入内容...',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit.configure({
      heading: { levels: [1, 2, 3] },
    }),
    ResizableImage.configure({
      inline: false,
      allowBase64: false,
    }),
    Placeholder.configure({
      placeholder: props.placeholder,
    }),
    Youtube.configure({
      widthMode: 'auto',
      modestBranding: true,
    }),
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
})

watch(() => props.modelValue, (val) => {
  const current = editor.value?.getHTML() || ''
  if (val !== current) {
    editor.value?.commands.setContent(val || '', false)
  }
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})

// -- Image upload -----------------------------------------------------------

const mediaPickerRef = ref<InstanceType<typeof AdminMediaPicker>>()

const openMediaPicker = () => {
  mediaPickerRef.value?.openPicker()
}

const onMediaSelect = (item: { id: number; url: string }) => {
  editor.value?.chain().focus().setImage({ src: item.url }).run()
}

// -- Video embed ------------------------------------------------------------

const insertVideo = () => {
  const url = window.prompt('输入 YouTube / 视频 URL:')
  if (!url) return
  editor.value?.commands.setYoutubeVideo({
    src: url,
    width: 640,
    height: 360,
  })
}
</script>

<style scoped>
.rich-editor :deep(.editor-content) {
  padding: 12px 16px;
  min-height: 200px;
  max-height: 500px;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.7;
  color: #1e293b;
  background: #ffffff;
  outline: none;
}

.rich-editor :deep(.editor-content p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  color: #94a3b8;
  pointer-events: none;
  height: 0;
}

.rich-editor :deep(.editor-content h1) { font-size: 1.5em; font-weight: 700; margin: 0.67em 0; }
.rich-editor :deep(.editor-content h2) { font-size: 1.25em; font-weight: 600; margin: 0.6em 0; }
.rich-editor :deep(.editor-content h3) { font-size: 1.1em; font-weight: 600; margin: 0.5em 0; }
.rich-editor :deep(.editor-content ul) { padding-left: 1.5em; list-style: disc; }
.rich-editor :deep(.editor-content ol) { padding-left: 1.5em; list-style: decimal; }
.rich-editor :deep(.editor-content blockquote) { border-left: 3px solid #60a5fa; padding-left: 1em; margin-left: 0; color: #64748b; }
.rich-editor :deep(.editor-content hr) { border: none; border-top: 1px solid #e5e7eb; margin: 1em 0; }
.rich-editor :deep(.editor-content img) { max-width: 100%; border-radius: 6px; }
.rich-editor :deep(.editor-content iframe) { max-width: 100%; border-radius: 6px; }
.rich-editor :deep(.editor-content a) { color: #2563eb; text-decoration: underline; }

.tool-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #64748b;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.tool-btn:hover { background: #e2e8f0; color: #1e293b; }
.tool-btn.is-active { background: rgba(37,99,235,0.12); color: #2563eb; }
.tool-btn:disabled { opacity: 0.4; cursor: default; }
</style>
