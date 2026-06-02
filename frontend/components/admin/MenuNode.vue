<template>
  <div>
    <div
      class="flex items-center justify-between px-4 py-2.5 rounded-lg group"
      :style="{
        marginLeft: depth * 24 + 'px',
        background: depth === 0 ? '#ffffff' : '#f8fafc',
        border: '1px solid #dbeafe',
      }"
    >
      <div class="flex items-center gap-3">
        <span class="text-[13px] font-medium" style="color: #1e293b;">{{ node.name_zh }}</span>
        <span class="text-[12px]" style="color: #94a3b8;">{{ node.name_en }}</span>
        <span class="text-[11px] px-1.5 py-0.5 rounded" style="background: #f1f5f9; color: #94a3b8;">{{ node.link || '/' }}</span>
        <span v-if="!node.is_visible" class="text-[10px] px-1.5 py-0.5 rounded" style="background: #fef2f2; color: #f87171;">隐藏</span>
        <span class="text-[10px] px-1.5 py-0.5 rounded" style="background: #f1f5f9; color: #64748b;">{{ node.location === 'header' ? '顶部' : '底部' }}</span>
      </div>
      <div class="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          @click="$emit('addChild', node)"
          class="text-[11px] border-none cursor-pointer px-2 py-1 rounded-lg transition-colors"
          style="color: #64748b; background: #f1f5f9;"
        >
          + 子菜单
        </button>
        <button
          @click="$emit('edit', node)"
          class="text-[11px] border-none cursor-pointer px-2.5 py-1 rounded-lg transition-colors"
          style="color: #60a5fa; background: rgba(37,99,235,0.08);"
        >
          编辑
        </button>
        <button
          @click="$emit('delete', node)"
          class="text-[11px] border-none cursor-pointer px-2.5 py-1 rounded-lg transition-colors"
          style="color: #f87171; background: rgba(239,68,68,0.08);"
        >
          删除
        </button>
      </div>
    </div>
    <AdminMenuNode
      v-for="child in node.children"
      :key="child.id"
      :node="child"
      :depth="depth + 1"
      @edit="$emit('edit', $event)"
      @delete="$emit('delete', $event)"
      @add-child="$emit('addChild', $event)"
    />
  </div>
</template>

<script setup lang="ts">
interface MenuNode {
  id: number;
  name_zh: string;
  name_en: string;
  link: string;
  icon: string | null;
  order: number;
  is_visible: boolean;
  location: string;
  parent_id: number | null;
  children: MenuNode[];
}

defineProps<{ node: MenuNode; depth: number }>();
defineEmits<{
  edit: [node: MenuNode];
  delete: [node: MenuNode];
  addChild: [node: MenuNode];
}>();
</script>
