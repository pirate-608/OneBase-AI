# 前端实现

OneBase 前端是一个 Vue 3 单页应用，构建后随 Python 包一起分发，由 FastAPI 后端托管。

---

## 技术栈

| 技术         | 版本   | 用途                       |
| :----------- | :----- | :------------------------- |
| Vue 3        | ^3.5   | UI 框架（Composition API） |
| Vite         | ^7.3   | 构建工具                   |
| Tailwind CSS | ^4.2   | 原子化样式                 |
| Marked       | ^17.0  | Markdown 渲染              |
| highlight.js | ^11.11 | 代码语法高亮               |
| DOMPurify    | ^3.2   | XSS 过滤                   |

---

## 组件架构

```
App.vue
├── Sidebar.vue         侧边栏
│   ├── TreeNode.vue    知识库目录树（递归组件）
│   └── ChatList.vue    历史会话列表
├── ChatArea.vue        对话主区域
└── FilePreview.vue     文档预览面板
```

### App.vue — 根组件

**职责：**

- 页面级布局（flex 三栏）
- 初始化时调用 `/api/health` 获取 Feature Flags 和站点名称
- 调用 `/api/tree` 获取目录树
- 配置 Markdown 渲染管线（Marked + highlight.js + DOMPurify）
- 从 `useChat()` 解构出状态与方法，透传给子组件

**Feature Flags 传递链：**

```
/api/health
  → App.vue (featureUpload, featureChatHistory)
    → Sidebar.vue (featureChatHistory → 控制双 Tab 显示)
    → ChatArea.vue (featureUpload → 控制上传按钮显示)
```

### Sidebar.vue — 侧边栏

**功能：**

- 显示站点 Logo 和名称
- **双 Tab 切换**：「历史对话」和「知识库」（仅 `chat_history: true` 时显示 Tab）
- 知识库 Tab：递归渲染 `TreeNode` 目录树
- 对话 Tab：渲染 `ChatList` 会话列表

**Props：**

| Prop                 | 类型    | 说明              |
| :------------------- | :------ | :---------------- |
| `siteName`           | String  | 站点名称          |
| `navTree`            | Array   | 目录树数据        |
| `sessions`           | Array   | 会话列表          |
| `currentSessionId`   | String  | 当前激活的会话 ID |
| `featureChatHistory` | Boolean | 是否启用历史对话  |

### ChatArea.vue — 对话区域

**功能：**

- 消息列表渲染（用户/AI 双侧气泡布局）
- AI 消息的 Markdown 实时渲染
- 输入框 + 发送按钮
- 文件上传按钮（`featureUpload` 控制）
- AI 消息附带**复制**和**下载**（MD/TXT 格式）按钮

**交互细节：**

- 流式生成中显示打字指示器，完成后显示操作按钮
- 复制按钮点击后显示"已复制！"反馈，2 秒后恢复
- 下载按钮展开格式选择菜单

### FilePreview.vue — 文档预览

通过 `/api/file/{path}` 获取文档内容，渲染 Markdown 或显示纯文本。

### TreeNode.vue — 递归目录树

接收嵌套的 `nodes` 数组，文件夹可折叠展开，文件项点击触发预览。

### ChatList.vue — 会话列表

显示历史会话列表，支持新建、选择、重命名、删除操作。

---

## 组合式函数

### useChat.js

封装全部聊天业务逻辑，与 UI 组件解耦。

**导出的响应式状态：**

| 状态           | 类型           | 说明               |
| :------------- | :------------- | :----------------- |
| `sessionId`    | Ref\<string\>  | 当前会话 ID        |
| `sessions`     | Ref\<Array\>   | 会话列表           |
| `messages`     | Ref\<Array\>   | 当前会话的消息列表 |
| `isGenerating` | Ref\<boolean\> | 是否正在生成回复   |

**导出的方法：**

| 方法                         | 说明                                |
| :--------------------------- | :---------------------------------- |
| `loadHistory(id?)`           | 从 `/api/history/{id}` 加载会话历史 |
| `fetchSessions()`            | 从 `/api/sessions` 获取会话列表     |
| `createNewSession()`         | 生成随机 ID，重置消息列表           |
| `selectSession(id)`          | 切换到指定会话并加载历史            |
| `deleteSession(id)`          | 删除会话（带确认弹窗）              |
| `renameSession({id, title})` | 重命名会话标题                      |
| `sendMessage(text)`          | 发送消息并处理 SSE 流               |

**会话 ID 策略：**

- 格式：`session_` + 8 位随机字符（`Math.random().toString(36)`）
- 存储于 `localStorage`（key: `onebase_session_id`）
- 关闭浏览器后重新打开会恢复上次的会话

**SSE 流式解析：**

```javascript
const reader = response.body.getReader()
const decoder = new TextDecoder('utf-8')
let buffer = ''

while (true) {
  const { done, value } = await reader.read()
  if (done) break

  buffer += decoder.decode(value, { stream: true })
  const lines = buffer.split('\n\n')
  buffer = lines.pop()  // 保留不完整的行

  for (const line of lines) {
    const dataStr = line.replace(/^data:\s*/, '').trim()
    if (dataStr === '[DONE]') return
    const parsed = JSON.parse(dataStr)
    messages.value[aiIndex].content += parsed.content
  }
}
```

关键点：使用 `buffer` 处理 TCP 分片导致的不完整数据行。

---

## Markdown 渲染管线

```
原始文本
  → Marked.parse()           # Markdown → HTML
  → markedHighlight           # 代码块语法高亮（highlight.js）
  → DOMPurify.sanitize()     # XSS 过滤
  → v-html 渲染               # 注入 DOM
```

配置代码（`App.vue`）：

```javascript
const marked = new Marked(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code, lang) {
      const language = hljs.getLanguage(lang) ? lang : 'plaintext'
      return hljs.highlight(code, { language }).value
    }
  })
)
const renderMarkdown = (text) =>
  text ? DOMPurify.sanitize(marked.parse(text)) : ''
```

---

## 构建与分发

### 开发模式

```bash
cd templates/frontend
npm install
npm run dev      # Vite 开发服务器（HMR）
```

### 生产构建

```bash
npm run build    # 输出到 dist/
```

构建产物 `dist/` 随 Python 包一起分发。`onebase serve` 时，`docker_runner.py` 将 `dist/` 拷贝到后端容器的 `static/` 目录。

### Vite 构建优化

`vite.config.js` 中配置了 `manualChunks`，将第三方库拆分为独立 chunk：

- `vendor` — Vue、Marked 等核心库
- 带 hash 的文件名确保长期缓存有效

---

## 相关文档

- [后端实现](backend.md) — 静态文件托管与 API 设计
- [API 文档](api.md) — 前端调用的全部接口
- [目录结构](project_structure.md) — 前端文件位置
