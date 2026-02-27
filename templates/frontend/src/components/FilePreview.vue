<template>
  <div class="w-1/3 bg-white border-r border-gray-200 flex flex-col shadow-2xl z-10">
    <div class="h-16 border-b border-gray-100 flex items-center justify-between px-4 bg-gray-50/50">
      <div class="flex items-center gap-2 text-sm font-semibold text-gray-700">
         <span>📄</span>
         <span class="truncate max-w-[180px]">{{ fileName }}</span>
      </div>
      <button @click="$emit('close')" class="p-1.5 hover:bg-gray-200 rounded-md text-gray-500 transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
      </button>
    </div>
    <div class="flex-1 overflow-y-auto p-6 bg-white">
      <div class="prose prose-sm md:prose-base max-w-none text-gray-600 prose-pre:p-0" v-html="renderMarkdown(content)"></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  fileName: { type: String, required: true },
  content: { type: String, required: true },
  renderMarkdown: { type: Function, required: true }
})

defineEmits(['close'])
</script>