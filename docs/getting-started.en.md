# Getting Started

Welcome to OneBase! Follow these steps to get your private knowledge base running in minutes.

---

## Requirements

| Requirement | Minimum Version | Notes                       |
| :---------- | :-------------- | :-------------------------- |
| Python      | 3.10+           | Recommended 3.11            |
| pip         | 22.0+           | `pip install --upgrade pip` |
| Docker      | 24.0+           | Including Docker Compose    |
| Git         | 2.30+           | For version tracking        |

!!! tip "GPU Acceleration"
    If using a local model (Ollama), an NVIDIA GPU with ≥8GB VRAM is recommended for better inference speed.

---

## Step 1: Install OneBase

```bash
pip install onebase
```

Verify the installation:

```bash
onebase --help
```

You should see the OneBase CLI help output.

---

## Step 2: Initialize Project

```bash
onebase init my-kb
cd my-kb
```

This creates the following structure:

```
my-kb/
├── onebase.yml       # Core configuration
├── base/             # Knowledge base document directory
│   ├── overview.md
│   ├── section1/
│   └── section2/
└── .env              # API keys (auto-generated)
```

---

## Step 3: Configure Model Engine

Edit `onebase.yml` to select your model provider:

=== "OpenAI (Cloud)"

    ```yaml
    engine:
      reasoning:
        provider: openai
        model: gpt-4o-mini
      embedding:
        provider: openai
        model: text-embedding-3-small
    ```

    Add your API key to `.env`:
    ```
    OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
    ```

=== "Ollama (Local)"

    ```yaml
    engine:
      reasoning:
        provider: ollama
        model: qwen3:4b
      embedding:
        provider: ollama
        model: nomic-embed-text
    ```

    Make sure Ollama is running locally:
    ```bash
    ollama pull qwen3:4b
    ollama pull nomic-embed-text
    ```

=== "DashScope (Alibaba Cloud)"

    ```yaml
    engine:
      reasoning:
        provider: dashscope
        model: qwen-plus
      embedding:
        provider: dashscope
        model: text-embedding-v3
    ```

    Add your API key to `.env`:
    ```
    DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
    ```

---

## Step 4: Add Knowledge Base Documents

Place your documents in the `base/` directory:

```bash
# Copy existing documents
cp ~/docs/*.md base/

# Or organize by subdirectory
mkdir base/product-docs
cp ~/product/*.pdf base/product-docs/
```

Supported file formats: **Markdown** (.md) · **Plain Text** (.txt) · **PDF** (.pdf)

!!! info "Directory Structure"
    The `base/` directory structure maps directly to navigation in the web UI. Using clear subdirectories helps users locate documents quickly.

---

## Step 5: Install Dependencies

```bash
onebase install
```

This command automatically installs all backend and frontend dependencies.

---

## Step 6: Build the Project

```bash
onebase build
```

This performs the following:

1. Scans documents in `base/`
2. Chunks text intelligently based on document type
3. Generates embedding vectors
4. Stores vectors in PGVector
5. Builds the frontend
6. Packages Docker images

!!! warning "Build Time"
    Initial build may take 1–5 minutes depending on document count and embedding model speed.

---

## Step 7: Start the Service

```bash
onebase serve
```

Visit [http://localhost:8080](http://localhost:8080) in your browser to see the knowledge base.

---

## Stop the Service

```bash
onebase stop
```

---

## GPU Acceleration

If using a local model like Ollama, enable GPU acceleration to significantly improve performance:

```yaml title="onebase.yml"
engine:
  reasoning:
    provider: ollama
    model: qwen3:4b
```

Ensure the NVIDIA driver, CUDA, and [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) are installed.

---

## Command Reference

| Command           | Description                                     |
| :---------------- | :---------------------------------------------- |
| `onebase init`    | Initialize a new project                        |
| `onebase install` | Install all dependencies                        |
| `onebase build`   | Build the project (chunk + vectorize + package) |
| `onebase serve`   | Start the service                               |
| `onebase stop`    | Stop the service                                |
| `onebase --help`  | Show help                                       |

---

## Next Steps

<div class="grid cards" markdown>

-   :material-cog: **Configuration Guide**

    ---

    Explore all `onebase.yml` options for customization

    [:octicons-arrow-right-24: Configuration Details](user-guide/config/overview.md)

-   :material-robot: **Choose Your Model**

    ---

    View all supported model providers and how to configure them

    [:octicons-arrow-right-24: Model Support](user-guide/config/MODELS.md)

-   :material-console: **CLI Reference**

    ---

    Master all commands and arguments

    [:octicons-arrow-right-24: CLI Reference](user-guide/cli/basic.md)

-   :material-code-braces: **Developer Guide**

    ---

    Understand the internal architecture

    [:octicons-arrow-right-24: Developer Guide](dev-guide/project_structure.md)

</div>
