--- 
    hide: 
    - navigation 
---

<div class="ob-hero">
  <div class="ob-hero__logo">
    <img src="../assets/images/onebase.svg" alt="OneBase Logo" />
  </div>
  <div class="ob-hero__content">
    <h1>OneBase AI</h1>
    <p class="ob-hero__tagline"><strong>Build and deploy AI-powered services (RAG) as easily as configuring a static site</strong></p>
    <div class="ob-hero__actions">
      <a class="ob-button" href="./getting-started">Getting Started</a>
      <a class="ob-button ob-button--ghost" href="./user-guide/config/overview">User Guide</a>
      <a class="ob-button ob-button--ghost" href="./dev-guide/api">Developer Guide</a>
    </div>
    <div class="ob-hero__meta">
      <span class="ob-chip">RAG Framework Scaffold</span>
      <span class="ob-chip">Custom Knowledge Base</span>
      <span class="ob-chip">Multi-Model Support</span>
      <span class="ob-chip">CLI-Simplified Deployment</span>
    </div>
  </div>
</div>

OneBase is a modern, ready-to-use RAG (Retrieval-Augmented Generation) framework scaffold. It encapsulates the complex configuration of vector databases, file parsing, LLM orchestration, and frontend UI rendering into minimal commands. Whether you want to quickly set up a personal knowledge base assistant or deploy an enterprise Q&A system based on private data, OneBase lets you go from zero to production in minutes.

**Core Philosophy: Convention over Configuration**

Simply drop your Markdown or PDF files into the `base/` directory, and OneBase will automatically generate a visual knowledge tree and complete vectorized retrieval.

<div class="ob-kpis">
  <div class="ob-kpi"><strong>5 Minutes</strong><br />From init to ready</div>
  <div class="ob-kpi"><strong>1 Command</strong><br />Auto build & deploy</div>
  <div class="ob-kpi"><strong>Multi-Engine</strong><br />OpenAI / Ollama / DeepSeek & more, local models supported</div>
  <div class="ob-kpi"><strong>Full Stack</strong><br />Frontend + Backend + Database</div>
</div>

<div class="ob-section">
  <h2>✨ Core Features</h2>
  <p>Efficient, reliable, production-ready RAG infrastructure.</p>
  <div class="ob-card-grid">
    <div class="ob-card">
      <h3>🛠️ One-Click Init & Build</h3>
      <p>A single command generates config, auto-scans documents, and chunks them into the vector store.</p>
      <a href="getting-started">View Getting Started</a>
    </div>
    <div class="ob-card">
      <h3>🧠 Full LLM Coverage</h3>
      <p>Seamless integration with OpenAI, Claude, DeepSeek, Gemini, and major Chinese LLMs.</p>
      <a href="user-guide/config/MODELS">Model Support List</a>
    </div>
    <div class="ob-card">
      <h3>📚 Powerful RAG Retrieval</h3>
      <p>High-precision semantic search powered by LangChain and PGVector.</p>
      <a href="dev-guide/database_design">Database Design</a>
    </div>
    <div class="ob-card">
      <h3>💬 Multi-Turn Chat with Persistent Memory</h3>
      <p>Built-in PostgreSQL session records — context persists even after page refresh.</p>
      <a href="user-guide/config/features">Feature Flags</a>
    </div>
    <div class="ob-card">
      <h3>📄 Visual File Preview</h3>
      <p>Sidebar directory tree + real-time Markdown preview with clear reference positioning.</p>
      <a href="user-guide/config/knowledge_base">Knowledge Base Config</a>
    </div>
    <div class="ob-card">
      <h3>🐳 Full-Stack Containerized Deployment</h3>
      <p>FastAPI + Vue 3, one-click docker-compose generation.</p>
      <a href="user-guide/cli/args">CLI Arguments</a>
    </div>
  </div>
</div>

<div class="ob-section">
  <h2>🚀 Three Steps to Launch</h2>
  <p>The shortest path from zero to production.</p>
  <ol class="ob-steps">
    <li>Run <code>onebase init</code> to generate project structure and default config.</li>
    <li>Place documents in <code>base/</code> and configure your model and database settings.</li>
    <li>Run <code>onebase build</code> and <code>onebase serve</code> to start the service.</li>
  </ol>
</div>

<div class="ob-section">
  <h2>🎯 Use Cases</h2>
  <div class="ob-note-grid">
    <div class="ob-note">Enterprise Private Knowledge Base Q&A</div>
    <div class="ob-note">Product Documentation & Customer Service Bot</div>
    <div class="ob-note">Team Collaboration & Internal Search</div>
    <div class="ob-note">Multi-Model Comparison & Evaluation Sandbox</div>
  </div>
</div>

<div class="ob-section">
  <h2>📌 Next Steps</h2>
  <p>Achieve deeper customization in less time.</p>
  <div class="ob-hero__actions">
    <a class="ob-button" href="user-guide/config/engine">Configure Model Engine</a>
    <a class="ob-button ob-button--ghost" href="user-guide/deploy/cloud_deploy">Cloud Deployment</a>
  </div>
</div>
