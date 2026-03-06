"""Tests for ModelFactory provider validation (no real LLM imports needed)."""

import pytest
from onebase.factory import ModelFactory


class TestModelFactoryValidation:
    def test_unsupported_reasoning_provider(self):
        with pytest.raises(ValueError, match="不支持的 Reasoning Provider"):
            ModelFactory.get_reasoning_model("unknown-provider", "some-model")

    def test_unsupported_embedding_provider(self):
        with pytest.raises(ValueError, match="不支持的 Embedding Provider"):
            ModelFactory.get_embedding_model("unknown-provider", "some-model")

    def test_supported_reasoning_list(self):
        expected = {
            "openai",
            "ollama",
            "docker-model",
            "dashscope",
            "zhipu",
            "anthropic",
            "google",
            "deepseek",
            "qianfan",
            "groq",
            "modelscope",
            "google-vertex",
            "doubao",
            "siliconflow",
        }
        assert set(ModelFactory.SUPPORTED_REASONING) == expected

    def test_supported_embedding_list(self):
        expected = {
            "openai",
            "ollama",
            "docker-model",
            "dashscope",
            "zhipu",
            "google",
            "qianfan",
            "modelscope",
            "google-vertex",
            "doubao",
            "siliconflow",
        }
        assert set(ModelFactory.SUPPORTED_EMBEDDING) == expected

    def test_provider_case_insensitive(self):
        """Provider should be lowercased internally — uppercase should not raise ValueError."""
        try:
            ModelFactory.get_reasoning_model("OPENAI", "gpt-4o")
        except ValueError:
            pytest.fail("OPENAI (uppercase) should be accepted as valid provider")
        except Exception:
            pass  # Import or network errors are fine in test env

    def test_provider_openai_lowered(self):
        """Verify uppercase provider passes validation (won't raise ValueError)."""
        try:
            ModelFactory.get_reasoning_model("OpenAI", "gpt-4o")
        except ValueError:
            pytest.fail("OpenAI (mixed case) should be accepted as valid provider")
        except Exception:
            pass  # Import errors are expected in test env
