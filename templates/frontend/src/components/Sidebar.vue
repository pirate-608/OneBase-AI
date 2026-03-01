<template>
  <aside class="w-64 bg-white border-r border-gray-200 flex flex-col shrink-0">
    <!-- 头部 Logo 与 标题 -->
    <div class="h-16 flex items-center px-6 border-b border-gray-100 gap-3">
      <div class="w-8 h-8 flex-shrink-0">
        <img src="../assets/onebase.svg" alt="OneBase Logo" class="w-full h-full object-contain" />
      </div>
      <h1 class="text-lg font-bold text-gray-800 tracking-tight truncate">
        {{ siteName }}
      </h1>
    </div>
    
    <!-- 🌟 [Step2] Tab 切换 — 仅在开启聊天历史时显示双 Tab -->
    <div v-if="featureChatHistory" class="flex border-b border-gray-100 bg-gray-50/50 shrink-0">
      <button 
        @click="activeTab = 'chat'" 
        :class="['flex-1 py-2.5 text-sm font-medium transition-colors', activeTab === 'chat' ? 'text-blue-600 border-b-2 border-blue-600 bg-white' : 'text-gray-500 hover:text-gray-700']"
      >
        历史对话
      </button>
      <button 
        @click="activeTab = 'knowledge'" 
        :class="['flex-1 py-2.5 text-sm font-medium transition-colors', activeTab === 'knowledge' ? 'text-blue-600 border-b-2 border-blue-600 bg-white' : 'text-gray-500 hover:text-gray-700']"
      >
        知识库
      </button>
    </div>

    <!-- 知识库内容 -->
    <div v-show="!featureChatHistory || activeTab === 'knowledge'" class="flex-1 overflow-y-auto p-4">
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 px-2">目录结构</p>
      <TreeNode :nodes="navTree" @select-file="$emit('select-file', $event)" />
    </div>

    <!-- 聊天列表内容（仅在开启聊天历史时可见） -->
    <div v-if="featureChatHistory" v-show="activeTab === 'chat'" class="flex-1 overflow-hidden p-4">
      <ChatList 
        :sessions="sessions" 
        :current-session-id="currentSessionId"
        @new-session="$emit('new-session')"
        @select-session="$emit('select-session', $event)"
        @delete-session="$emit('delete-session', $event)"
        @rename-session="$emit('rename-session', $event)"
      />
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import TreeNode from './TreeNode.vue'
import ChatList from './ChatList.vue'

const props = defineProps({
  siteName: { type: String, required: true },
  navTree: { type: Array, required: true },
  sessions: { type: Array, required: true },
  currentSessionId: { type: String, required: true },
  featureChatHistory: { type: Boolean, default: true }
})

defineEmits(['select-file', 'new-session', 'select-session', 'delete-session', 'rename-session'])

// 🌟 [Step2] 关闭历史对话时默认显示知识库 Tab
const activeTab = ref(props.featureChatHistory ? 'chat' : 'knowledge')
</script>