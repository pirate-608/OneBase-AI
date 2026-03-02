# Features (Feature Flags)

The `features` field controls optional features in the frontend and backend. Enable or disable specific capabilities with simple boolean values — no code changes required.

---

## Basic Structure

```yaml title="onebase.yml"
features:
  chat_history: true
  file_upload: true
```

| Field          | Type | Default | Description             |
| :------------- | :--- | :-----: | :---------------------- |
| `chat_history` | bool | `true`  | Multi-turn chat history |
| `file_upload`  | bool | `true`  | Frontend file upload    |

---

## chat_history — Chat History

Controls whether multi-turn conversation memory is enabled.

**When enabled (`true`):**

- The backend persists each conversation turn (user question + AI answer) to PostgreSQL
- Chat context is preserved across page refreshes
- The sidebar displays a "Chats" tab for viewing and switching between sessions

**When disabled (`false`):**

- The backend stores no conversation records; each question is an independent single-turn Q&A
- The sidebar hides the "Chats" tab and only shows the knowledge base file tree
- Suitable for privacy-sensitive scenarios or pure retrieval applications

---

## file_upload — File Upload

Controls whether users can upload documents through the frontend.

**When enabled (`true`):**

- A file upload button (📎) appears next to the input box
- Supports uploading PDF / TXT / MD files
- Uploaded documents are chunked and indexed immediately — no need to re-run `onebase build`
- The backend registers the `/upload` route to handle files

**When disabled (`false`):**

- The upload button is hidden
- The backend `/upload` route is not registered; upload requests return 403
- Knowledge base content is entirely managed by `onebase build`, suitable for read-only knowledge bases

---

## Configuration Flow

The complete pipeline from configuration to runtime:

```
onebase.yml → CLI reads → Docker env vars injection → Backend conditional routing → Frontend conditional rendering
```

1. `onebase.yml` defines `features.chat_history` / `features.file_upload`
2. `onebase build` / `onebase serve` injects them as container environment variables `FEATURE_CHAT_HISTORY` / `FEATURE_FILE_UPLOAD`
3. The backend decides whether to register routes and store conversations based on environment variables
4. The frontend reads flag states from `/config` and conditionally renders UI components

!!! tip
    After modifying `features`, you need to re-run `onebase serve` for changes to take effect (no need to re-`build`).
