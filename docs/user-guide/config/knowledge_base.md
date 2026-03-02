# Knowledge Base 知识库配置

`knowledge_base` 字段定义了文档的存放路径、切片策略和目录结构映射方式。

---

## 基本结构

```yaml title="onebase.yml"
knowledge_base:
  path: ./base
  chunk_size: 500
  struct: default
```

| 字段         | 类型           | 默认值    | 说明                               |
| :----------- | :------------- | :-------- | :--------------------------------- |
| `path`       | string         | `./base`  | 知识库文档根目录路径               |
| `chunk_size` | int            | `500`     | 文本切块大小（字符数），必须大于 0 |
| `struct`     | string \| dict | `default` | 目录结构映射规则                   |

---

## path — 文档目录

`path` 指定知识库文档的根目录。OneBase 会递归扫描该目录下所有支持的文件。

支持的文件格式：

| 格式     | 扩展名 | 说明                     |
| :------- | :----- | :----------------------- |
| Markdown | `.md`  | 推荐，支持前端可视化预览 |
| PDF      | `.pdf` | 自动提取文本内容         |
| 纯文本   | `.txt` | 自动检测编码             |

隐藏文件（以 `.` 开头）和不支持的格式会被自动忽略。

---

## chunk_size — 切块大小

`chunk_size` 控制文档被切分为语义块时每个块的最大字符数。OneBase 使用 LangChain 的 `RecursiveCharacterTextSplitter`，会尽量保持段落和句子的完整性。

```yaml
knowledge_base:
  chunk_size: 500   # 默认值，适合大多数场景
```

| 场景                | 推荐值   | 说明                 |
| :------------------ | :------- | :------------------- |
| 短文档 / 精确问答   | 300-500  | 块更小，检索更精准   |
| 长文档 / 需要上下文 | 800-1500 | 块更大，保留更多语境 |

!!! tip
    修改 `chunk_size` 后需要重新执行 `onebase build` 才能生效。

---

## struct — 目录结构映射

`struct` 决定了知识库文件如何映射为前端导航树。有两种模式：

### 模式一：自动扫描（默认）

```yaml
knowledge_base:
  struct: default
```

设置为 `default` 时，OneBase 自动递归扫描 `path` 目录，按文件系统结构生成导航树。

例如，你的文件目录为：

```
base/
├── overview.md
├── 开发指南/
│   ├── 快速入门.md
│   └── API接口.md
└── 产品文档/
    ├── 设计规范.pdf
    └── 常见问题.txt
```

前端将自动渲染出对应的目录树：

```
overview
开发指南/
├── 快速入门
└── API接口
产品文档/
├── 设计规范
└── 常见问题
```

文件名去掉扩展名后作为导航标题显示。空目录会被自动忽略。

### 模式二：手动指定

```yaml
knowledge_base:
  struct:
    - 概述: overview.md
    - 开发文档:
        - 快速入门: dev/quickstart.md
        - API 参考: dev/api-reference.md
    - FAQ: faq.md
```

手动指定时，你可以自定义导航标题和文件映射关系：

- **Key** 为前端显示的标题（可以是任意中文/英文）
- **Value** 为相对于 `path` 目录的文件路径
- 支持任意层级嵌套

!!! warning "注意"
    手动指定会**完全覆盖**自动扫描结构。未列入 `struct` 的文件将被忽略，不会被切片入库，也不会出现在前端导航中。

构建时，OneBase 会校验每个路径是否指向实际存在的文件。缺失的文件会在构建日志中列出警告。

---

## 完整示例

```yaml title="onebase.yml"
knowledge_base:
  path: ./base
  chunk_size: 800
  struct:
    - 产品简介: overview.md
    - 用户手册:
        - 安装部署: manual/install.md
        - 使用教程: manual/tutorial.md
    - 技术文档:
        - 架构设计: tech/architecture.md
        - API 接口: tech/api.pdf
    - 常见问题: faq.txt
```
