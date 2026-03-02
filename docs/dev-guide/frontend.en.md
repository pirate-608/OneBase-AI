# Frontend Implementation

The OneBase frontend is a Vue 3 single-page application, distributed with the Python package and hosted by the FastAPI backend.

---

## Tech Stack

| Technology   | Version | Purpose                        |
| :----------- | :------ | :----------------------------- |
| Vue 3        | ^3.5    | UI framework (Composition API) |
| Vite         | ^7.3    | Build tool                     |
| Tailwind CSS | ^4.2    | Utility-first styling          |
| Marked       | ^17.0   | Markdown rendering             |
| highlight.js | ^11.11  | Code syntax highlighting       |
| DOMPurify    | ^3.2    | XSS sanitization               |

---

## Component Architecture

```
App.vue
├── Sidebar.vue         Sidebar
│   ├── TreeNode.vue    Knowledge base tree (recursive)
│   └── ChatList.vue    Session history list
├── ChatArea.vue        Main chat area
└── FilePreview.vue     Document preview panel
```

### App.vue — Root Component

**Responsibilities:**

- Page-level layout (flex 3-column)
- On init, calls `/api/health` to get Feature Flags and site name
- Calls `/api/tree` to get the directory tree
- Configures Markdown rendering pipeline (Marked + highlight.js + DOMPurify)
- Destructures state and methods from `useChat()`, passes to child components

**Feature Flags propagation:**

```
/api/health
  → App.vue (featureUpload, featureChatHistory)
    → Sidebar.vue (featureChatHistory → controls dual tab display)
    → ChatArea.vue (featureUpload → controls upload button display)
```

### Sidebar.vue — Sidebar

**Features:**

- Displays site logo and name
- **Dual tab switching**: "Chat History" and "Knowledge Base" (tabs only shown when `chat_history: true`)
- Knowledge Base tab: recursively renders `TreeNode` directory tree
- Chat tab: renders `ChatList` session list

**Props:**

| Prop                 | Type    | Description              |
| :------------------- | :------ | :----------------------- |
| `siteName`           | String  | Site name                |
| `navTree`            | Array   | Directory tree data      |
| `sessions`           | Array   | Session list             |
| `currentSessionId`   | String  | Currently active session |
| `featureChatHistory` | Boolean | Chat history enabled     |

### ChatArea.vue — Chat Area

**Features:**

- Message list rendering (user/AI dual-side bubble layout)
- Real-time Markdown rendering for AI messages
- Input box + send button
- File upload button (controlled by `featureUpload`)
- AI messages include **copy** and **download** (MD/TXT format) buttons

**Interaction details:**

- Typing indicator during streaming; action buttons appear after completion
- Copy button shows "Copied!" feedback for 2 seconds
- Download button expands format selection menu

### FilePreview.vue — Document Preview

Fetches document content via `/api/file/{path}`, renders Markdown or displays plain text.

### TreeNode.vue — Recursive Directory Tree

Receives nested `nodes` array. Folders can be collapsed/expanded; file items trigger preview on click.

### ChatList.vue — Session List

Displays session history with create, select, rename, and delete operations.

---

## Composables

### useChat.js

Encapsulates all chat business logic, decoupled from UI components.

**Exported reactive state:**

| State          | Type           | Description              |
| :------------- | :------------- | :----------------------- |
| `sessionId`    | Ref\<string\>  | Current session ID       |
| `sessions`     | Ref\<Array\>   | Session list             |
| `messages`     | Ref\<Array\>   | Current session messages |
| `isGenerating` | Ref\<boolean\> | Currently generating     |

**Exported methods:**

| Method                       | Description                           |
| :--------------------------- | :------------------------------------ |
| `loadHistory(id?)`           | Load session from `/api/history/{id}` |
| `fetchSessions()`            | Fetch sessions from `/api/sessions`   |
| `createNewSession()`         | Generate random ID, reset messages    |
| `selectSession(id)`          | Switch to session and load history    |
| `deleteSession(id)`          | Delete session (with confirmation)    |
| `renameSession({id, title})` | Rename session title                  |
| `sendMessage(text)`          | Send message and handle SSE stream    |

**Session ID strategy:**

- Format: `session_` + 8 random characters (`Math.random().toString(36)`)
- Stored in `localStorage` (key: `onebase_session_id`)
- Reopening the browser restores the last session

**SSE streaming parser:**

```javascript
const reader = response.body.getReader()
const decoder = new TextDecoder('utf-8')
let buffer = ''

while (true) {
  const { done, value } = await reader.read()
  if (done) break

  buffer += decoder.decode(value, { stream: true })
  const lines = buffer.split('\n\n')
  buffer = lines.pop()  // Keep incomplete line

  for (const line of lines) {
    const dataStr = line.replace(/^data:\s*/, '').trim()
    if (dataStr === '[DONE]') return
    const parsed = JSON.parse(dataStr)
    messages.value[aiIndex].content += parsed.content
  }
}
```

Key point: Uses a `buffer` to handle incomplete data lines caused by TCP fragmentation.

---

## Markdown Rendering Pipeline

```
Raw text
  → Marked.parse()           # Markdown → HTML
  → markedHighlight           # Code block syntax highlighting (highlight.js)
  → DOMPurify.sanitize()     # XSS filtering
  → v-html rendering          # Inject into DOM
```

Configuration (in `App.vue`):

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

## Build & Distribution

### Development Mode

```bash
cd templates/frontend
npm install
npm run dev      # Vite dev server (HMR)
```

### Production Build

```bash
npm run build    # Output to dist/
```

The `dist/` build output is distributed with the Python package. During `onebase serve`, `docker_runner.py` copies `dist/` to the backend container's `static/` directory.

### Vite Build Optimization

`vite.config.js` configures `manualChunks` to split third-party libraries into separate chunks:

- `vendor` — Vue, Marked, and other core libraries
- Hashed filenames ensure long-term cache effectiveness

---

## Related Documentation

- [Backend Implementation](backend.md) — Static file hosting and API design
- [API Reference](api.md) — All endpoints called by the frontend
- [Project Structure](project_structure.md) — Frontend file locations
