<div class="ob-card">
  <p>
    <a href="https://github.com/pirate-608/OneBase-AI" 
       class="ob-link" target="_blank">
       🚀 访问代码仓库
    </a>
  </p>
  <p class="ob-note">
    欢迎提交 <strong>Issue</strong> 和 <strong>Pull Request</strong>！<br>
    如果你有任何关于 <em>支持新模型</em>、<em>改进前端 UI</em> 或 <em>优化 RAG 检索效果</em> 的想法，
    请随时发起讨论。
  </p>
</div>

---

## 测试

OneBase 使用 **pytest** 框架，测试文件位于项目根目录的 `tests/` 下。

### 环境准备

```bash
# 安装项目及测试依赖
pip install -e ".[test]"
```

测试依赖包含：`pytest`、`pytest-cov`、`fastapi`、`httpx`、`python-multipart`。

### 运行测试

```bash
# 运行全部测试
pytest -v

# 运行并生成覆盖率报告
pytest --cov=onebase --cov-report=term-missing

# 运行单个测试文件
pytest tests/test_auth.py -v
```

### 测试结构

| 文件                   | 覆盖范围                                                                           |
| :--------------------- | :--------------------------------------------------------------------------------- |
| `test_config.py`       | `OneBaseConfig` 加载、校验、字段默认值                                             |
| `test_factory.py`      | `ModelFactory` provider 字符串验证、初始化异常处理                                 |
| `test_builder.py`      | `KnowledgeBuilder` 自动扫描、手动结构、空目录处理                                  |
| `test_chunker.py`      | `DocumentProcessor` 切块大小、元数据注入、空文件处理                               |
| `test_rate_limiter.py` | `FixedWindowRateLimiter` 窗口滑动、计数、时间过期重置                              |
| `test_schemas.py`      | `ChatMessage` role/content、`ChatRequest` session_id、`RenameSessionRequest` title |
| `test_auth.py`         | Bearer Token 验证、白名单放行、401 响应头、非 API 路径                             |

### 添加新测试

1. 在 `tests/` 下创建 `test_<模块名>.py`
2. 测试函数以 `test_` 前缀命名
3. 对于需要 FastAPI 环境的测试，使用自包含的 `TestClient` 方式（参考 `test_auth.py`）
4. CI 中会自动运行 `pytest`，PR 提交前请确保所有测试通过