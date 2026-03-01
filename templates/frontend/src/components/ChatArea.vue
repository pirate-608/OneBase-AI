<template>
  <main class="flex-1 flex flex-col h-full bg-gray-50 relative">
    
    <div ref="chatContainer" class="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
      <div class="max-w-4xl mx-auto space-y-6 w-full">
        <div v-for="(msg, index) in messages" :key="index"
             :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
          <div :class="[
            'max-w-[80%] rounded-2xl px-5 py-3.5 shadow-sm overflow-x-auto',
            msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-sm' : 'bg-white text-gray-800 border border-gray-100 rounded-tl-sm'
          ]">
            <div v-if="msg.role === 'user'" class="whitespace-pre-wrap text-[15px] leading-relaxed">
              {{ msg.content }}
            </div>
            <div v-else class="prose prose-sm md:prose-base max-w-none prose-p:leading-relaxed prose-pre:p-0" v-html="renderMarkdown(msg.content)"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="p-4 bg-white border-t border-gray-200">
      <div class="max-w-4xl mx-auto flex items-end gap-3 bg-white p-2 rounded-2xl border border-gray-300 shadow-sm focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-400 transition-all">
        <!-- 🌟 [Step2] 仅在 feature_upload 开启时渲染上传按钮 -->
        <template v-if="featureUpload">
          <input type="file" ref="fileInput" class="hidden" @change="handleUpload" accept=".pdf,.txt,.md">
          <button 
            @click="triggerUpload" 
            :disabled="isUploading || isGenerating"
            class="p-2.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-colors disabled:opacity-50"
            title="上传文档 (PDF/TXT/MD)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.699-9.941l-7.81 7.81a1.5 1.5 0 002.112 2.13" />
            </svg>
          </button>
        </template>

        <textarea
          v-model="inputMessage"
          rows="1"
          placeholder="向 OneBase 提问，按 Enter 发送，Shift+Enter 换行..."
          class="flex-1 bg-transparent resize-none outline-none max-h-32 p-2 pl-3 text-[15px] text-gray-700 placeholder-gray-400"
          @keydown.enter.exact.prevent="handleSend"
        ></textarea>

        <button 
          @click="handleSend" 
          :disabled="!inputMessage.trim() || isGenerating"
          class="p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="isGenerating" class="block w-5 h-5 text-center text-sm font-bold animate-pulse">...</span>
          <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
          </svg>
        </button>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  messages: { type: Array, required: true },
  isGenerating: { type: Boolean, required: true },
  isUploading: { type: Boolean, required: true },
  renderMarkdown: { type: Function, required: true },
  featureUpload: { type: Boolean, default: true }
})

const emit = defineEmits(['send', 'upload'])

const inputMessage = ref('')
const chatContainer = ref(null)
const fileInput = ref(null)

// 自动滚动逻辑封装在组件内
const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// 监听消息变化自动滚动
watch(() => props.messages, scrollToBottom, { deep: true })

const triggerUpload = () => {
  if (fileInput.value) fileInput.value.click()
}

const handleUpload = (event) => {
  emit('upload', event)
  event.target.value = '' // 清空以允许重复上传同一文件
}

const handleSend = () => {
  const text = inputMessage.value.trim()
  if (!text || props.isGenerating) return
  emit('send', text)
  inputMessage.value = ''
}
</script>