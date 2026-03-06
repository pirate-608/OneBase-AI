import { ref } from 'vue'
import { apiFetch } from './useAuth'

export function useChat() {
  const messages = ref([])
  const isGenerating = ref(false)
  const sessions = ref([])

  const generateNewSessionId = () => 'session_' + Math.random().toString(36).substring(2, 10)

  const getOrCreateSessionId = () => {
    let sid = localStorage.getItem('onebase_session_id')
    if (!sid) {
      sid = generateNewSessionId()
      localStorage.setItem('onebase_session_id', sid)
    }
    return sid
  }
  const sessionId = ref(getOrCreateSessionId())

  const loadHistory = async (id) => {
    const targetId = id || sessionId.value
    try {
      const res = await apiFetch(`/api/history/${targetId}`)
      if (res.ok) {
        const history = await res.json()
        if (history.length > 0) {
          messages.value = history
        } else {
          messages.value = [{ role: 'assistant', content: '你好！我是基于你专属知识库的 AI 助手。请问有什么我可以帮你的？' }]
        }
      }
    } catch (e) { console.error("无法加载聊天历史", e) }
  }

  const fetchSessions = async () => {
    try {
      const res = await apiFetch('/api/sessions')
      if (res.ok) sessions.value = await res.json()
    } catch (e) { console.error("无法加载会话列表", e) }
  }

  const createNewSession = () => {
    sessionId.value = generateNewSessionId()
    localStorage.setItem('onebase_session_id', sessionId.value)
    messages.value = [{ role: 'assistant', content: '你好！我是基于你专属知识库的 AI 助手。请问有什么我可以帮你的？' }]
  }

  const selectSession = async (id) => {
    if (sessionId.value === id) return
    sessionId.value = id
    localStorage.setItem('onebase_session_id', id)
    messages.value = []
    await loadHistory(id)
  }

  const deleteSession = async (id) => {
    if (!confirm('确定要彻底删除这个对话吗？')) return
    try {
      const res = await apiFetch(`/api/history/${id}`, { method: 'DELETE' })
      if (res.ok) {
        sessions.value = sessions.value.filter(s => s.id !== id)
        if (sessionId.value === id) createNewSession()
      }
    } catch (e) { console.error("删除会话失败", e) }
  }

  // 🌟 新增：重命名接口请求
  const renameSession = async ({ id, title }) => {
    try {
      const res = await apiFetch(`/api/sessions/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      })
      if (res.ok) {
        const session = sessions.value.find(s => s.id === id)
        if (session) session.title = title
      }
    } catch (e) { console.error("重命名失败", e) }
  }

  const sendMessage = async (text) => {
    if (isGenerating.value) return

    const isFirstMessage = messages.value.filter(m => m.role === 'user').length === 0

    messages.value.push({ role: 'user', content: text })
    isGenerating.value = true
    messages.value.push({ role: 'assistant', content: '' })
    const aiMessageIndex = messages.value.length - 1

    try {
      const response = await apiFetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId.value,
          messages: messages.value.slice(0, aiMessageIndex),
          stream: true
        })
      })

      if (!response.ok) throw new Error(`HTTP 错误！状态码: ${response.status}`)

      // 第一条消息发送成功后刷新列表产生默认标题
      if (isFirstMessage) fetchSessions()

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop()

        for (const line of lines) {
          const dataStr = line.replace(/^data:\s*/, '').trim()
          if (!dataStr) continue
          if (dataStr === '[DONE]') {
            isGenerating.value = false
            return
          }
          try {
            const parsedData = JSON.parse(dataStr)
            if (parsedData.content) messages.value[aiMessageIndex].content += parsedData.content
            else if (parsedData.error) messages.value[aiMessageIndex].content += `\n[系统报错: ${parsedData.error}]`
          } catch (e) { console.warn('JSON 解析失败:', e, dataStr) }
        }
      }
    } catch (error) {
      messages.value[aiMessageIndex].content = `网络请求失败: ${error.message}。`
    } finally {
      isGenerating.value = false
    }
  }

  return {
    sessionId, sessions, messages, isGenerating,
    loadHistory, fetchSessions, createNewSession, selectSession, deleteSession, renameSession, sendMessage
  }
}