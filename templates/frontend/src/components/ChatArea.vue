<template>
  <main class="flex-1 flex flex-col h-full bg-gray-50 relative">
    
    <div ref="chatContainer" class="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
      <div class="max-w-4xl mx-auto space-y-6 w-full">
        <div v-for="(msg, index) in messages" :key="index"
             :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
          <div class="max-w-[80%]">
            <div :class="[
              'rounded-2xl px-5 py-3.5 shadow-sm overflow-x-auto',
              msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-sm' : 'bg-white text-gray-800 border border-gray-100 rounded-tl-sm'
            ]">
              <div v-if="msg.role === 'user'" class="whitespace-pre-wrap text-[15px] leading-relaxed">
                {{ msg.content }}
              </div>
              <div v-else class="prose prose-sm md:prose-base max-w-none prose-p:leading-relaxed prose-pre:p-0" v-html="renderMarkdown(msg.content)"></div>
            </div>

            <!-- AI 消息操作栏：复制 + 下载 -->
            <div v-if="msg.role === 'assistant' && msg.content && !isGenerating"
                 class="flex items-center gap-1 mt-1.5 ml-1">
              <!-- 复制按钮 -->
              <button
                @click="copyToClipboard(msg.content, index)"
                class="flex items-center gap-1 px-2 py-1 text-xs text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
                :title="copiedIndex === index ? 'Copied!' : 'Copy'"
              >
                <svg v-if="copiedIndex !== index" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-3.5 h-3.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9.75a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-3.5 h-3.5 text-green-500">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
                <span>{{ copiedIndex === index ? 'Copied' : 'Copy' }}</span>
              </button>

              <!-- 下载按钮（带格式选择） -->
              <div class="relative" ref="downloadMenuRefs">
                <button
                  @click="toggleDownloadMenu(index)"
                  class="flex items-center gap-1 px-2 py-1 text-xs text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
                  title="Download"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-3.5 h-3.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                  </svg>
                  <span>Download</span>
                </button>
                <!-- 格式选择下拉 -->
                <div v-if="downloadMenuIndex === index"
                     class="absolute left-0 bottom-full mb-1 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-10 min-w-[120px]">
                  <button @click="downloadContent(msg.content, 'md', index)"
                          class="w-full text-left px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-50 hover:text-gray-800 transition-colors">
                    📄 Markdown (.md)
                  </button>
                  <button @click="downloadContent(msg.content, 'txt', index)"
                          class="w-full text-left px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-50 hover:text-gray-800 transition-colors">
                    📝 Plain Text (.txt)
                  </button>
                </div>
              </div>
            </div>
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
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'

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
const copiedIndex = ref(null)
const downloadMenuIndex = ref(null)
const downloadMenuRefs = ref(null)

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

// ---- 复制到剪贴板 ----
const copyToClipboard = async (content, index) => {
  try {
    await navigator.clipboard.writeText(content)
    copiedIndex.value = index
    setTimeout(() => { copiedIndex.value = null }, 2000)
  } catch {
    // fallback for older browsers
    const ta = document.createElement('textarea')
    ta.value = content
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copiedIndex.value = index
    setTimeout(() => { copiedIndex.value = null }, 2000)
  }
}

// ---- 下载 ----
const toggleDownloadMenu = (index) => {
  downloadMenuIndex.value = downloadMenuIndex.value === index ? null : index
}

const downloadContent = (content, format, index) => {
  const timestamp = new Date().toISOString().slice(0, 19).replace(/[T:]/g, '-')
  const ext = format === 'md' ? 'md' : 'txt'
  const mime = format === 'md' ? 'text/markdown' : 'text/plain'
  const filename = `onebase-reply-${timestamp}.${ext}`
  const blob = new Blob([content], { type: `${mime};charset=utf-8` })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  downloadMenuIndex.value = null
}

// 点击外部关闭下载菜单
const handleClickOutside = (e) => {
  if (downloadMenuIndex.value !== null) {
    downloadMenuIndex.value = null
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside, true))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside, true))
</script>