<template>
  <ul class="space-y-0.5">
    <li v-for="node in nodes" :key="node.title">
      <div 
        class="flex items-center text-sm py-1.5 px-2 hover:bg-gray-200/50 rounded-md cursor-pointer text-gray-700 transition-colors select-none"
        :style="{ paddingLeft: (depth * 12 + 8) + 'px' }"
        @click="handleClick(node)"
      >
        <span v-if="node.type === 'folder'" class="mr-1.5 w-4 h-4 flex items-center justify-center text-gray-400 transition-transform">
          <svg v-if="node.isOpen" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" /></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4 -rotate-90"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" /></svg>
        </span>
        <span v-else class="mr-1.5 w-4 h-4 flex items-center justify-center text-gray-400">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5"><path fill-rule="evenodd" d="M4.5 2A1.5 1.5 0 003 3.5v13A1.5 1.5 0 004.5 18h11a1.5 1.5 0 001.5-1.5V7.621a1.5 1.5 0 00-.44-1.06l-4.12-4.122A1.5 1.5 0 0011.378 2H4.5zm2.25 8.5a.75.75 0 000 1.5h6.5a.75.75 0 000-1.5h-6.5zm0 3a.75.75 0 000 1.5h6.5a.75.75 0 000-1.5h-6.5z" clip-rule="evenodd" /></svg>
        </span>
        <span class="truncate">{{ node.title }}</span>
      </div>
      
      <div v-show="node.type === 'folder' && node.isOpen">
        <TreeNode 
          v-if="node.children && node.children.length > 0"
          :nodes="node.children" 
          :depth="depth + 1"
          @select-file="$emit('select-file', $event)"
        />
      </div>
    </li>
  </ul>
</template>

<script setup>
defineProps({
  nodes: { type: Array, required: true },
  depth: { type: Number, default: 0 }
})
const emit = defineEmits(['select-file'])

const handleClick = (node) => {
  if (node.type === 'folder') {
    node.isOpen = !node.isOpen // 切换文件夹展开状态
  } else {
    emit('select-file', node) // 向上派发文件点击事件
  }
}
</script>