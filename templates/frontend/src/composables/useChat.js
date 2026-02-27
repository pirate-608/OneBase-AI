// src/composables/useChat.js
import { ref } from 'vue'

export function useChat() {
  // --- 1. 状态管理 ---
  const messages = ref([])
  const isGenerating = ref(false)

  // --- 2. Session 管理 ---
  const getOrCreateSessionId = () => {
    let sid = localStorage.getItem('onebase_session_id')
    if (!sid) {
      sid = 'session_' + Math.random().toString(36).substring(2, 10)
      localStorage.setItem('onebase_session_id', sid)
    }
    return sid
  }
  const sessionId = ref(getOrCreateSessionId())

  // --- 3. 加载历史记录 ---
  const loadHistory = async () => {
    try {
      const res = await fetch(`/api/history/${sessionId.value}`)
      if (res.ok) {
        const history = await res.json()
        if (history.length > 0) {
          messages.value = history
        } else {
          messages.value.push({ 
            role: 'assistant', 
            content: '你好！我是基于你专属知识库的 AI 助手。请问有什么我可以帮你的？' 
          })
        }
      }
    } catch (e) {
      console.error("无法加载聊天历史", e)
    }
  }

  // --- 4. 核心：发送消息与流式解析 ---
  const sendMessage = async (text) => {
    if (isGenerating.value) return
    
    messages.value.push({ role: 'user', content: text })
    isGenerating.value = true
    
    // 占位 AI 的空消息
    messages.value.push({ role: 'assistant', content: '' })
    const aiMessageIndex = messages.value.length - 1

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId.value,
          messages: messages.value.slice(0, aiMessageIndex),
          stream: true
        })
      })

      if (!response.ok) throw new Error(`HTTP 错误！状态码: ${response.status}`)

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop() // 保留不完整的片段

        for (const line of lines) {
          const dataStr = line.replace(/^data:\s*/, '').trim()
          if (!dataStr) continue
          
          if (dataStr === '[DONE]') {
            isGenerating.value = false
            return
          }
          
          try {
            const parsedData = JSON.parse(dataStr)
            if (parsedData.content) {
              messages.value[aiMessageIndex].content += parsedData.content
            } else if (parsedData.error) {
               messages.value[aiMessageIndex].content += `\n[系统报错: ${parsedData.error}]`
            }
          } catch (e) {
            console.warn('JSON 解析失败:', e, dataStr)
          }
        }
      }
    } catch (error) {
      messages.value[aiMessageIndex].content = `网络请求失败: ${error.message}。`
    } finally {
      isGenerating.value = false
    }
  }

  // 将状态和方法暴露出去
  return {
    sessionId,
    messages,
    isGenerating,
    loadHistory,
    sendMessage
  }
}