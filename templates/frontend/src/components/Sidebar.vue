<template>
  <aside class="w-64 bg-white border-r border-gray-200 flex flex-col shrink-0">
    <div class="h-16 flex items-center px-6 border-b border-gray-100">
      <h1 class="text-lg font-bold text-gray-800 tracking-tight">🤖 {{ siteName }}</h1>
    </div>
    
    <div class="flex-1 overflow-y-auto p-4">
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 px-2">知识库结构</p>
      <TreeNode :nodes="navTree" @select-file="$emit('select-file', $event)" />
    </div>
  </aside>
</template>

<script setup>
import TreeNode from './TreeNode.vue'

defineProps({
  siteName: { type: String, required: true },
  navTree: { type: Array, required: true }
})

defineEmits(['select-file'])
</script>