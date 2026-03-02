<div align="center">
  <img src="./templates/frontend/public/onebase.svg" alt="OneBase Logo" width="120" />
  <h1>OneBase AI</h1>
  <p><strong>像配置静态网站一样，一键构建与部署 AI 动态服务 (RAG 底座)</strong></p>
</div>

[![PyPI Version][pypi-v-image]][pypi-v-link]
![License](https://img.shields.io/github/license/pirate-608/OneBase-AI)

## 🌟 项目简介
OneBase 是一个开箱即用的现代化 RAG（检索增强生成）框架脚手架。它将复杂的向量数据库配置、文件解析、大模型调度以及前端 UI 渲染封装在极简的命令之中。无论你是想快速搭建一个专属的个人知识库助手，还是想为企业部署一套基于私有数据的问答系统，OneBase 都能让你在几分钟内完成从“0”到“上线”的全过程。

## ✨ 核心特性

- 🛠️ **一键初始化与构建**：一条命令生成配置，自动扫描文档并切片入库。
- 🧠 **主流大模型全覆盖**：无缝对接 OpenAI, Claude, DeepSeek, Gemini, 以及智谱、通义千问等国内外主流 LLM。
- 📚 **强大的 RAG 检索**：基于 langchain 和 pgvector，提供高精度的语义搜索。
- 💬 **多轮对话与持久化记忆**：内置 PostgreSQL 会话记录，刷新页面也不丢失对话上下文。
- 📄 **可视化文件预览**：类似 VSCode 的左侧目录树，支持点击实时预览 Markdown 文件，并在聊天中高亮引用代码。
- 📎 **实时文档上传**：前端界面直接拖拽上传 PDF/TXT/MD，即刻学习，即刻提问。
- 🐳 **全栈容器化部署**：后端 FastAPI + 前端 Vue 3，自动生成 docker-compose.yml，一键部署到任何服务器。

## 📚 产品文档

查看[产品文档](https://onebase.67656.fun)。


## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！如果你有任何关于支持新模型、改进前端 UI 或优化 RAG 检索效果的想法，请随时发起讨论。

<!-- Badges -->
[pypi-v-image]: https://img.shields.io/pypi/v/onebase-ai.svg
[pypi-v-link]: https://pypi.python.org/pypi/onebase-ai/
<!-- Links -->
[OneBase AI]: https://onebase.67656.fun
[Issue]: https://github.com/OneBase-AI/OneBase-AI/issues
[Discussions]: https://github.com/OneBase-AI/OneBase-AI/discussions
[release-notes]: https://onebase.67656.fun/about/release-notes/
[Contributing Guide]: https://www.mkdocs.org/about/contributing/


## 📄 许可证

本项目基于 MIT License 开源。

