<div class="ob-card">
  <p>
    <a href="https://github.com/pirate-608/OneBase-AI" 
       class="ob-link" target="_blank">
       🚀 Visit the Repository
    </a>
  </p>
  <p class="ob-note">
    We welcome <strong>Issues</strong> and <strong>Pull Requests</strong>!<br>
    If you have any ideas about <em>supporting new models</em>, <em>improving the frontend UI</em>, or <em>optimizing RAG retrieval</em>,
    please feel free to start a discussion.
  </p>
</div>

---

## Testing

OneBase uses the **pytest** framework. Test files are located in the `tests/` directory at the project root.

### Setup

```bash
# Install project and test dependencies
pip install -e ".[test]"
```

Test dependencies include: `pytest`, `pytest-cov`, `fastapi`, `httpx`, `python-multipart`.

### Running Tests

```bash
# Run all tests
pytest -v

# Run with coverage report
pytest --cov=onebase --cov-report=term-missing

# Run a single test file
pytest tests/test_auth.py -v
```

### Test Structure

| File                   | Coverage                                                                           |
| :--------------------- | :--------------------------------------------------------------------------------- |
| `test_config.py`       | `OneBaseConfig` loading, validation, field defaults                                |
| `test_factory.py`      | `ModelFactory` provider string validation, init error handling                     |
| `test_builder.py`      | `KnowledgeBuilder` auto-scan, manual struct, empty directory                       |
| `test_chunker.py`      | `DocumentProcessor` chunk size, metadata injection, empty files                    |
| `test_rate_limiter.py` | `FixedWindowRateLimiter` window sliding, counting, time expiry                     |
| `test_schemas.py`      | `ChatMessage` role/content, `ChatRequest` session_id, `RenameSessionRequest` title |
| `test_auth.py`         | Bearer Token validation, whitelist passthrough, 401 headers, non-API paths         |

### Adding New Tests

1. Create `test_<module_name>.py` under `tests/`
2. Name test functions with the `test_` prefix
3. For tests requiring a FastAPI environment, use a self-contained `TestClient` approach (see `test_auth.py`)
4. CI runs `pytest` automatically — ensure all tests pass before submitting a PR
