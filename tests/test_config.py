"""Tests for OneBaseConfig loading & validation."""

import pytest
import tempfile
from pathlib import Path
from pydantic import ValidationError
from onebase.config import OneBaseConfig


MINIMAL_YAML = """\
site_name: test-site
engine:
  reasoning:
    provider: openai
    model: gpt-4o
  embedding:
    provider: openai
    model: text-embedding-3-small
database:
  type: postgresql
  vector_store: pgvector
knowledge_base:
  path: ./base
"""


def _write_yaml(content: str) -> Path:
    """Write YAML content to a temp file and return the path."""
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".yml", delete=False, encoding="utf-8"
    )
    f.write(content)
    f.close()
    return Path(f.name)


class TestConfigLoad:
    def test_minimal_valid(self):
        path = _write_yaml(MINIMAL_YAML)
        cfg = OneBaseConfig.load(path)
        assert cfg.site_name == "test-site"
        assert cfg.engine.reasoning.provider == "openai"
        assert cfg.engine.embedding.model == "text-embedding-3-small"
        # defaults
        assert cfg.features.chat_history is True
        assert cfg.features.file_upload is True
        assert cfg.performance.redis_cache_enabled is True
        path.unlink()

    def test_custom_features(self):
        yaml_text = (
            MINIMAL_YAML + "features:\n  chat_history: false\n  file_upload: false\n"
        )
        path = _write_yaml(yaml_text)
        cfg = OneBaseConfig.load(path)
        assert cfg.features.chat_history is False
        assert cfg.features.file_upload is False
        path.unlink()

    def test_custom_performance(self):
        yaml_text = (
            MINIMAL_YAML
            + "performance:\n  redis_cache_enabled: false\n  chat_rate_limit_per_minute: 100\n"
        )
        path = _write_yaml(yaml_text)
        cfg = OneBaseConfig.load(path)
        assert cfg.performance.redis_cache_enabled is False
        assert cfg.performance.chat_rate_limit_per_minute == 100
        path.unlink()

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            OneBaseConfig.load("/nonexistent/path.yml")

    def test_invalid_yaml_syntax(self):
        path = _write_yaml("site_name: :\n  bad: [unclosed")
        with pytest.raises(ValueError, match="YAML"):
            OneBaseConfig.load(path)
        path.unlink()

    def test_missing_required_field(self):
        path = _write_yaml("site_name: test\n")
        with pytest.raises(ValidationError):
            OneBaseConfig.load(path)
        path.unlink()

    def test_invalid_chunk_size_zero(self):
        yaml_text = MINIMAL_YAML.replace(
            "path: ./base", "path: ./base\n  chunk_size: 0"
        )
        path = _write_yaml(yaml_text)
        with pytest.raises(ValidationError):
            OneBaseConfig.load(path)
        path.unlink()

    def test_database_type_literal(self):
        yaml_text = MINIMAL_YAML.replace("type: postgresql", "type: mysql")
        path = _write_yaml(yaml_text)
        with pytest.raises(ValidationError):
            OneBaseConfig.load(path)
        path.unlink()

    def test_knowledge_base_default_struct(self):
        path = _write_yaml(MINIMAL_YAML)
        cfg = OneBaseConfig.load(path)
        assert cfg.knowledge_base.struct == "default"
        path.unlink()
