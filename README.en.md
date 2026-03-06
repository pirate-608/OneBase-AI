<div align="center">
  <img src="./templates/frontend/public/onebase.svg" alt="OneBase Logo" width="120" />
  <h1>OneBase AI</h1>
  <p><strong>Configure like a static site, deploy dynamic AI services (RAG Base) with one command</strong></p>
</div>

[![PyPI Version][pypi-v-image]][pypi-v-link]
![License](https://img.shields.io/github/license/pirate-608/OneBase-AI)

## 🌟 Introduction
OneBase is a production-ready, modern RAG (Retrieval-Augmented Generation) framework scaffold. It encapsulates complex vector database configuration, file parsing, large model orchestration, and frontend UI rendering into minimal, straightforward commands. Whether you want to quickly build a personal knowledge base assistant or deploy a private-data Q&A system for your enterprise, OneBase enables you to go from "zero" to "live" in minutes.

## ✨ Core Features

- 🛠️ **One-Click Initialization & Build**: A single command generates configurations, automatically scans documents, and indexes them into chunks.
- 🧠 **Full Coverage of Mainstream LLMs**: Seamlessly connect with OpenAI, Claude, DeepSeek, Gemini, as well as leading domestic models like Zhipu AI (智谱) and Tongyi Qianwen (通义千问).
- 📚 **Powerful RAG Retrieval**: Built on langchain and pgvector, delivering high-precision semantic search.
- 💬 **Multi-Turn Dialogue with Persistent Memory**: Integrated PostgreSQL session storage ensures conversation context is maintained even after a page refresh.
- 📄 **Visual File Preview**: Features a VSCode-like left-side directory tree, supports click-to-preview Markdown files, and highlights code references within the chat.
- 📎 **Real-time Document Upload**: Drag and drop PDF/TXT/MD files directly in the frontend interface for immediate learning and questioning.
- 🐳 **Full-Stack Containerized Deployment**: Backend (FastAPI) + Frontend (Vue 3). Automatically generates a docker-compose.yml file for one-click deployment on any server.

## 📚 Documentation

Check out the [Product Documentation](https://onebase.67656.fun).

## 🤝 Contributing

Issues and Pull Requests are welcome! If you have ideas about supporting new models, improving the frontend UI, or optimizing RAG retrieval performance, feel free to start a discussion.

<!-- Badges -->
[pypi-v-image]: https://img.shields.io/pypi/v/onebase-ai.svg
[pypi-v-link]: https://pypi.python.org/pypi/onebase-ai/
<!-- Links -->
[OneBase AI]: https://onebase.67656.fun
[Issue]: https://github.com/OneBase-AI/OneBase-AI/issues
[Discussions]: https://github.com/OneBase-AI/OneBase-AI/discussions
[release-notes]: https://onebase.67656.fun/about/release-notes/
[Contributing Guide]: https://www.mkdocs.org/about/contributing/

## 📄 License

This project is open-sourced under the MIT License.