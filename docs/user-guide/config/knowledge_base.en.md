# Knowledge Base Configuration

The `knowledge_base` field defines the document storage path, chunking strategy, and directory structure mapping.

---

## Basic Structure

```yaml title="onebase.yml"
knowledge_base:
  path: ./base
  chunk_size: 500
  struct: default
```

| Field        | Type           | Default   | Description                  |
| :----------- | :------------- | :-------- | :--------------------------- |
| `path`       | string         | `./base`  | Root directory for documents |
| `chunk_size` | int            | `500`     | Chunk size (characters), > 0 |
| `struct`     | string \| dict | `default` | Directory structure mapping  |

---

## path — Document Directory

`path` specifies the root directory for knowledge base documents. OneBase recursively scans all supported files under this directory.

Supported file formats:

| Format     | Extension | Description                   |
| :--------- | :-------- | :---------------------------- |
| Markdown   | `.md`     | Recommended, supports preview |
| PDF        | `.pdf`    | Automatic text extraction     |
| Plain Text | `.txt`    | Automatic encoding detection  |

Hidden files (starting with `.`) and unsupported formats are automatically ignored.

---

## chunk_size — Chunk Size

`chunk_size` controls the maximum character count per semantic chunk. OneBase uses LangChain's `RecursiveCharacterTextSplitter`, which preserves paragraph and sentence integrity.

```yaml
knowledge_base:
  chunk_size: 500   # Default, suitable for most scenarios
```

| Scenario                   | Recommended | Description                  |
| :------------------------- | :---------- | :--------------------------- |
| Short docs / precise Q&A   | 300-500     | Smaller chunks, more precise |
| Long docs / context needed | 800-1500    | Larger chunks, more context  |

!!! tip
    After modifying `chunk_size`, you need to re-run `onebase build` for changes to take effect.

---

## struct — Directory Structure Mapping

`struct` determines how knowledge base files are mapped to the frontend navigation tree. Two modes are available:

### Mode 1: Auto Scan (Default)

```yaml
knowledge_base:
  struct: default
```

When set to `default`, OneBase automatically scans the `path` directory recursively and generates the navigation tree based on the file system structure.

For example, given this directory:

```
base/
├── overview.md
├── dev-guide/
│   ├── quickstart.md
│   └── api-reference.md
└── product-docs/
    ├── design-spec.pdf
    └── faq.txt
```

The frontend automatically renders the corresponding directory tree:

```
overview
dev-guide/
├── quickstart
└── api-reference
product-docs/
├── design-spec
└── faq
```

File names (without extensions) are used as navigation titles. Empty directories are automatically ignored.

### Mode 2: Manual Specification

```yaml
knowledge_base:
  struct:
    - Overview: overview.md
    - Developer Docs:
        - Quick Start: dev/quickstart.md
        - API Reference: dev/api-reference.md
    - FAQ: faq.md
```

With manual specification, you can customize navigation titles and file mappings:

- **Key** is the title displayed in the frontend (any language)
- **Value** is the file path relative to the `path` directory
- Supports arbitrary nesting levels

!!! warning "Note"
    Manual specification **completely overrides** the auto-scan structure. Files not listed in `struct` will be ignored — they won't be chunked or indexed, and won't appear in the frontend navigation.

During build, OneBase validates that each path points to an actual file. Missing files are reported as warnings in the build log.

---

## Full Example

```yaml title="onebase.yml"
knowledge_base:
  path: ./base
  chunk_size: 800
  struct:
    - Product Overview: overview.md
    - User Manual:
        - Installation: manual/install.md
        - Tutorial: manual/tutorial.md
    - Technical Docs:
        - Architecture: tech/architecture.md
        - API Reference: tech/api.pdf
    - FAQ: faq.txt
```
