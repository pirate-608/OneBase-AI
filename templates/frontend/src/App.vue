<template>
  <div class="flex h-screen bg-gray-50 text-gray-800 font-sans overflow-hidden">
    
    <!-- 🌟 更新：传入历史会话相关的所有 Props 和 Events -->
    <Sidebar 
      :site-name="siteName" 
      :nav-tree="navTree" 
      :sessions="sessions"
      :current-session-id="sessionId"
      :feature-chat-history="featureChatHistory"
      @select-file="openFilePreview" 
      @new-session="createNewSession"
      @select-session="selectSession"
      @delete-session="deleteSession"
      @rename-session="renameSession"
    />

    <FilePreview 
      v-if="previewFile" 
      :file-name="previewFile" 
      :content="previewContent" 
      :render-markdown="renderMarkdown"
      @close="previewFile = null" 
    />

    <ChatArea 
      :messages="messages" 
      :is-generating="isGenerating"
      :is-uploading="isUploading"
      :render-markdown="renderMarkdown"
      :feature-upload="featureUpload"
      @send="sendMessage"
      @upload="handleFileUpload"
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'

// 引入拆分后的 UI 组件
import Sidebar from './components/Sidebar.vue'
import FilePreview from './components/FilePreview.vue'
import ChatArea from './components/ChatArea.vue'

// 🌟 引入刚刚封装的 Chat 逻辑模块
import { useChat } from './composables/useChat'
import { apiFetch } from './composables/useAuth'

// --- Markdown 配置 ---
const marked = new Marked(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code, lang) {
      const language = hljs.getLanguage(lang) ? lang : 'plaintext'
      return hljs.highlight(code, { language }).value
    }
  })
)
// 🌟 [3-3] 使用 DOMPurify 过滤 XSS，防止恶意脚本经由 Markdown 注入
import DOMPurify from 'dompurify'
const renderMarkdown = (text) => text ? DOMPurify.sanitize(marked.parse(text)) : ''

// --- 全局视图状态 ---
const siteName = ref("OneBase AI")
const navTree = ref([])
const previewFile = ref(null)
const previewContent = ref('')
const isUploading = ref(false)

// 🌟 [Step2] Feature Flags：从 /api/health 获取
const featureUpload = ref(true)
const featureChatHistory = ref(true)

// 🌟 全量解构出聊天核心状态与方法
const { 
  sessionId, sessions, messages, isGenerating, 
  loadHistory, fetchSessions, createNewSession, selectSession, deleteSession, renameSession, sendMessage 
} = useChat()

// --- 页面初始化 API ---
onMounted(async () => {
  // 1. 获取目录树
  try {
    const res = await apiFetch('/api/tree')
    if (res.ok) navTree.value = await res.json()
  } catch (e) { console.error("无法加载目录树", e) }

  // 2. 🌟 [Step2] 获取 feature flags
  try {
    const healthRes = await fetch('/api/health')
    if (healthRes.ok) {
      const healthData = await healthRes.json()
      if (healthData.site_name) siteName.value = healthData.site_name
      if (healthData.features) {
        featureUpload.value = healthData.features.file_upload ?? true
        featureChatHistory.value = healthData.features.chat_history ?? true
      }
    }
  } catch (e) { console.error('无法获取服务状态', e) }

  // 3. 🌟 调用封装好的加载历史记录和会话列表方法（仅在开启聊天历史时）
  if (featureChatHistory.value) {
    await fetchSessions()
    await loadHistory()
  }
  
  // 4. 让浏览器标签页标题同步 siteName 的值
  document.title = siteName.value;
})

// --- 交互逻辑 (文件预览与上传) ---
const openFilePreview = async (node) => {
  previewFile.value = node.title
  previewContent.value = '正在加载内容...'
  try {
    const res = await apiFetch(`/api/file/${encodeURIComponent(node.path)}`)
    const data = await res.json()
    previewContent.value = data.content
  } catch (e) {
    previewContent.value = '加载失败'
  }
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  isUploading.value = true
  messages.value.push({ role: 'assistant', content: `正在解析并学习文档：**${file.name}**，请稍候...` })

  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await apiFetch('/api/upload', { method: 'POST', body: formData })
    const result = await response.json()
    
    messages.value.pop() 
    if (response.ok) {
      messages.value.push({ role: 'assistant', content: `✅ 我已成功学习了 **${file.name}**！\n\n该文档被切分为了 **${result.chunks}** 个记忆片段并入库。你可以随时向我提问关于它的内容。` })
    } else {
      messages.value.push({ role: 'assistant', content: `❌ 上传失败: ${result.detail}` })
    }
  } catch (error) {
    messages.value.pop()
    messages.value.push({ role: 'assistant', content: `❌ 网络错误: 无法连接到上传服务。` })
  } finally {
    isUploading.value = false
  }
}
</script>