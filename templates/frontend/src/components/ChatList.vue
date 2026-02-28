<template>
  <div class="flex flex-col gap-2 h-full" @click="openMenuId = null">
    <!-- 新建对话按钮 -->
    <button 
      @click="$emit('new-session')" 
      class="w-full py-2 mb-2 bg-blue-50 text-blue-600 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors flex items-center justify-center gap-1 border border-blue-100 shrink-0"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
      </svg>
      开启新对话
    </button>
    
    <div class="flex-1 overflow-y-auto space-y-2 pr-1">
      <div 
        v-for="session in sessions" 
        :key="session.id" 
        @click="$emit('select-session', session.id)"
        :class="['group p-3 rounded-xl cursor-pointer transition-all relative border', session.id === currentSessionId ? 'bg-blue-600 text-white border-blue-600 shadow-md' : 'bg-white hover:bg-gray-50 text-gray-700 border-gray-100 hover:border-gray-300']"
      >
        <!-- 正常展示 / 编辑框切换 -->
        <div v-if="editingId === session.id" class="mr-6">
          <input 
            :id="'rename-' + session.id"
            v-model="editTitle" 
            @keydown.enter="saveRename(session.id)" 
            @blur="saveRename(session.id)"
            @click.stop
            class="w-full bg-white text-gray-800 border-none outline-none ring-2 ring-blue-300 rounded px-1.5 py-0.5 text-sm"
          />
        </div>
        <div v-else class="text-sm font-medium truncate pr-6">{{ session.title }}</div>
        
        <div :class="['text-xs mt-1 truncate', session.id === currentSessionId ? 'text-blue-200' : 'text-gray-400']">
          {{ new Date(session.created_at).toLocaleString() }}
        </div>

        <!-- 悬浮三点按钮 -->
        <button 
          v-if="editingId !== session.id"
          @click.stop="toggleMenu(session.id)" 
          :class="['absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-md transition-opacity', openMenuId === session.id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100', session.id === currentSessionId ? 'hover:bg-blue-700 text-white' : 'hover:bg-gray-200 text-gray-500']"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 256 256"><path fill="currentColor" d="M140 128a12 12 0 1 1-12-12a12 12 0 0 1 12 12Zm56-12a12 12 0 1 0 12 12a12 12 0 0 0-12-12Zm-136 0a12 12 0 1 0 12 12a12 12 0 0 0-12-12Z"/></svg>
        </button>

        <!-- 下拉菜单 -->
        <div 
          v-if="openMenuId === session.id" 
          class="absolute right-8 top-8 z-50 w-24 bg-white border border-gray-100 shadow-lg rounded-md overflow-hidden text-sm"
        >
          <div @click.stop="startRename(session)" class="px-3 py-2 hover:bg-gray-50 cursor-pointer text-gray-700">重命名</div>
          <div @click.stop="handleDelete(session.id)" class="px-3 py-2 hover:bg-red-50 cursor-pointer text-red-600">删除</div>
        </div>
      </div>
      
      <div v-if="sessions.length === 0" class="text-center text-gray-400 text-sm mt-4">
        暂无历史对话
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  sessions: { type: Array, required: true },
  currentSessionId: { type: String, required: true }
})

const emit = defineEmits(['new-session', 'select-session', 'delete-session', 'rename-session'])

const openMenuId = ref(null)
const editingId = ref(null)
const editTitle = ref('')

const toggleMenu = (id) => {
  openMenuId.value = openMenuId.value === id ? null : id
}

const startRename = async (session) => {
  editingId.value = session.id
  editTitle.value = session.title
  openMenuId.value = null // 隐藏菜单
  
  // 等待 input 渲染后自动聚焦
  await nextTick()
  const input = document.getElementById(`rename-${session.id}`)
  if (input) input.focus()
}

const saveRename = (id) => {
  if (editingId.value === null) return
  if (editTitle.value.trim() && editTitle.value !== props.sessions.find(s => s.id === id)?.title) {
    emit('rename-session', { id, title: editTitle.value.trim() })
  }
  editingId.value = null
}

const handleDelete = (id) => {
  openMenuId.value = null
  emit('delete-session', id)
}
</script>