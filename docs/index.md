--- 
    hide: 
    - navigation 
---

<div class="ob-hero">
  <div class="ob-hero__logo">
    <img src="./assets/images/onebase.svg" alt="OneBase Logo" />
  </div>
  <div class="ob-hero__content">
    <h1>OneBase AI</h1>
    <p class="ob-hero__tagline"><strong>像配置静态网站一样，一键构建与部署 AI 动态服务 (RAG 底座)</strong></p>
    <div class="ob-hero__actions">
      <a class="ob-button" href="./getting-started">快速入门</a>
      <a class="ob-button ob-button--ghost" href="./user-guide/config/overview">用户指南</a>
      <a class="ob-button ob-button--ghost" href="./dev-guide/api">开发者指南</a>
    </div>
    <div class="ob-hero__meta">
      <span class="ob-chip">RAG 框架脚手架</span>
      <span class="ob-chip">自定义知识库</span>
      <span class="ob-chip">多模型支持</span>
      <span class="ob-chip">命令行简化部署</span>
    </div>
  </div>
</div>

OneBase 是一个开箱即用的现代化 RAG（检索增强生成）框架脚手架。它将复杂的向量数据库配置、文件解析、大模型调度以及前端 UI 渲染封装在极简的命令之中。无论你是想快速搭建一个专属的个人知识库助手，还是想为企业部署一套基于私有数据的问答系统，OneBase 都能让你在几分钟内完成从“0”到“上线”的全过程。

**核心理念：约定大于配置 (Convention over Configuration)**

你只需要把 Markdown 或 PDF 文件丢进 `base/` 目录，OneBase 就会自动为你生成可视化的知识树，并完成向量化检索。

<div class="ob-kpis">
  <div class="ob-kpi"><strong>5 分钟</strong><br />从初始化到可用</div>
  <div class="ob-kpi"><strong>1 条命令</strong><br />自动构建与部署</div>
  <div class="ob-kpi"><strong>多引擎</strong><br />OpenAI / Ollama / DeepSeek等，也支持本地模型</div>
  <div class="ob-kpi"><strong>全栈</strong><br />前端 + 后端 + 数据库</div>
</div>

<div class="ob-section">
  <h2>✨ 核心特性</h2>
  <p>高效、可靠、面向生产环境的 RAG 基础设施。</p>
  <div class="ob-card-grid">
    <div class="ob-card">
      <h3>🛠️ 一键初始化与构建</h3>
      <p>一条命令生成配置，自动扫描文档并切片入库。</p>
      <a href="getting-started">查看快速入门</a>
    </div>
    <div class="ob-card">
      <h3>🧠 主流大模型全覆盖</h3>
      <p>无缝对接 OpenAI、Claude、DeepSeek、Gemini 及国内主流 LLM。</p>
      <a href="user-guide/config/MODELS">模型支持列表</a>
    </div>
    <div class="ob-card">
      <h3>📚 强大的 RAG 检索</h3>
      <p>基于 langchain 与 pgvector，提供高精度语义搜索。</p>
      <a href="dev-guide/database_design">数据库设计</a>
    </div>
    <div class="ob-card">
      <h3>💬 多轮对话与持久化记忆</h3>
      <p>内置 PostgreSQL 会话记录，刷新页面也不丢失上下文。</p>
      <a href="user-guide/config/features">功能开关</a>
    </div>
    <div class="ob-card">
      <h3>📄 可视化文件预览</h3>
      <p>侧边栏目录树 + Markdown 实时预览，引用定位清晰。</p>
      <a href="user-guide/config/knowledge_base">知识库配置</a>
    </div>
    <div class="ob-card">
      <h3>🐳 全栈容器化部署</h3>
      <p>FastAPI + Vue 3，一键生成 docker-compose。</p>
      <a href="user-guide/cli/args"><命令行参数/a>
    </div>
  </div>
</div>

<div class="ob-section">
  <h2>🚀 三步上线</h2>
  <p>从 0 到上线的最短路径。</p>
  <ol class="ob-steps">
    <li>执行 <code>onebase init</code> 生成项目结构与默认配置。</li>
    <li>将文档放入 <code>base/</code> 并完成模型与数据库配置。</li>
    <li>运行 <code>onebase build</code> 与 <code>onebase serve</code> 启动服务。</li>
  </ol>
</div>

<div class="ob-section">
  <h2>🎯 适用场景</h2>
  <div class="ob-note-grid">
    <div class="ob-note">企业私有知识库问答系统</div>
    <div class="ob-note">产品文档与客服机器人</div>
    <div class="ob-note">技术团队协作与内部检索</div>
    <div class="ob-note">多模型对比与评测沙盒</div>
  </div>
</div>

<div class="ob-section">
  <h2>📌 下一步</h2>
  <p>用更短时间完成更深度的定制。</p>
  <div class="ob-hero__actions">
    <a class="ob-button" href="user-guide/config/engine">配置模型引擎</a>
    <a class="ob-button ob-button--ghost" href="user-guide/deploy/cloud_deploy">云端部署</a>
  </div>
</div>