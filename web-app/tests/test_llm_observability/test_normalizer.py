"""
Tests for LLM Data Normalizer.

Tests normalization of responses from multiple LLM providers.
"""

import pytest
from datetime import datetime

from modules.llm_observability.normalizer import (
    LLMDataNormalizer,
    NormalizedLLMEvent,
    NormalizedTokenUsage,
    ProviderDataFormat,
    CompletionStatus,
    ErrorCategory,
    get_provider_enum,
    PROVIDER_NAME_MAP,
)


class TestProviderMapping:
    """Tests for provider name mapping."""

    def test_get_provider_enum_mistral(self):
        assert get_provider_enum("mistral") == ProviderDataFormat.MISTRAL
        assert get_provider_enum("MISTRAL") == ProviderDataFormat.MISTRAL

    def test_get_provider_enum_claude(self):
        assert get_provider_enum("claude") == ProviderDataFormat.CLAUDE
        assert get_provider_enum("anthropic") == ProviderDataFormat.CLAUDE

    def test_get_provider_enum_openai(self):
        assert get_provider_enum("openai") == ProviderDataFormat.OPENAI

    def test_get_provider_enum_ollama(self):
        assert get_provider_enum("ollama") == ProviderDataFormat.OLLAMA

    def test_get_provider_enum_azure(self):
        assert get_provider_enum("azure") == ProviderDataFormat.AZURE_OPENAI
        assert get_provider_enum("azure_openai") == ProviderDataFormat.AZURE_OPENAI

    def test_get_provider_enum_unknown(self):
        assert get_provider_enum("unknown_provider") == ProviderDataFormat.CUSTOM


class TestNormalizedTokenUsage:
    """Tests for NormalizedTokenUsage dataclass."""

    def test_default_values(self):
        usage = NormalizedTokenUsage()
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0
        assert usage.estimated_cost_usd == 0.0

    def test_to_dict(self):
        usage = NormalizedTokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            estimated_cost_usd=0.001
        )
        result = usage.to_dict()
        assert result["prompt_tokens"] == 100
        assert result["completion_tokens"] == 50
        assert result["total_tokens"] == 150
        assert result["estimated_cost_usd"] == 0.001


class TestLLMDataNormalizer:
    """Tests for LLMDataNormalizer class."""

    @pytest.fixture
    def normalizer(self):
        return LLMDataNormalizer()

    # Mistral normalization tests
    def test_normalize_mistral_response(self, normalizer):
        response = {
            "id": "chat-12345",
            "object": "chat.completion",
            "model": "mistral-large-latest",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Hello!"},
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }

        event = normalizer.normalize_mistral_response(
            response=response,
            latency_ms=150.5
        )

        assert isinstance(event, NormalizedLLMEvent)
        assert event.provider == ProviderDataFormat.MISTRAL
        assert event.model == "mistral-large-latest"
        assert event.status == CompletionStatus.SUCCESS
        assert event.finish_reason == "stop"
        assert event.token_usage.prompt_tokens == 10
        assert event.token_usage.completion_tokens == 20
        assert event.token_usage.total_tokens == 30
        assert event.latency_ms == 150.5

    def test_normalize_mistral_with_request_data(self, normalizer):
        response = {
            "id": "chat-12345",
            "model": "mistral-large",
            "choices": [{"finish_reason": "stop", "message": {"content": "Hi"}}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 1, "total_tokens": 6}
        }
        request_data = {
            "model": "mistral-large",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.7,
            "max_tokens": 100
        }

        event = normalizer.normalize_mistral_response(
            response=response,
            request_data=request_data,
            latency_ms=100
        )

        assert event.temperature == 0.7
        assert event.max_tokens == 100
        assert event.messages_count == 1

    # Claude normalization tests
    def test_normalize_claude_response(self, normalizer):
        response = {
            "id": "msg_12345",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Hello!"}],
            "model": "claude-3-sonnet-20240229",
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 15,
                "output_tokens": 25
            }
        }

        event = normalizer.normalize_claude_response(
            response=response,
            latency_ms=200
        )

        assert event.provider == ProviderDataFormat.CLAUDE
        assert event.model == "claude-3-sonnet-20240229"
        assert event.status == CompletionStatus.SUCCESS
        assert event.finish_reason == "stop"  # Mapped from end_turn
        assert event.token_usage.prompt_tokens == 15
        assert event.token_usage.completion_tokens == 25
        assert event.token_usage.total_tokens == 40

    # OpenAI normalization tests
    def test_normalize_openai_response(self, normalizer):
        response = {
            "id": "chatcmpl-12345",
            "object": "chat.completion",
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Hi there!"},
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 10,
                "total_tokens": 30
            }
        }

        event = normalizer.normalize_openai_response(
            response=response,
            latency_ms=300
        )

        assert event.provider == ProviderDataFormat.OPENAI
        assert event.model == "gpt-4"
        assert event.token_usage.prompt_tokens == 20
        assert event.token_usage.completion_tokens == 10

    # Ollama normalization tests
    def test_normalize_ollama_response(self, normalizer):
        response = {
            "model": "llama2",
            "message": {"role": "assistant", "content": "Hello!"},
            "done": True,
            "total_duration": 500000000,  # 500ms in nanoseconds
            "prompt_eval_count": 10,
            "eval_count": 5
        }

        event = normalizer.normalize_ollama_response(response=response)

        assert event.provider == ProviderDataFormat.OLLAMA
        assert event.model == "llama2"
        assert event.token_usage.prompt_tokens == 10
        assert event.token_usage.completion_tokens == 5
        assert event.token_usage.estimated_cost_usd == 0.0  # Ollama is free

    # Auto-detection tests
    def test_normalize_response_auto_detect(self, normalizer):
        mistral_response = {
            "id": "chat-123",
            "model": "mistral-large",
            "choices": [{"finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
        }

        event = normalizer.normalize_response(
            provider=ProviderDataFormat.MISTRAL,
            response=mistral_response,
            latency_ms=100
        )

        assert event.provider == ProviderDataFormat.MISTRAL

    # Error normalization tests
    def test_normalize_error_rate_limit(self, normalizer):
        error = Exception("Rate limit exceeded. Please retry after 60 seconds.")

        normalized = normalizer.normalize_error(
            error=error,
            provider=ProviderDataFormat.OPENAI,
            status_code=429
        )

        assert normalized.category == ErrorCategory.RATE_LIMIT
        assert normalized.retryable is True

    def test_normalize_error_authentication(self, normalizer):
        error = {"message": "Invalid API key", "code": "invalid_api_key"}

        normalized = normalizer.normalize_error(
            error=error,
            provider=ProviderDataFormat.MISTRAL,
            status_code=401
        )

        assert normalized.category == ErrorCategory.AUTHENTICATION
        assert normalized.retryable is False

    def test_normalize_error_timeout(self, normalizer):
        error = Exception("Connection timed out")

        normalized = normalizer.normalize_error(
            error=error,
            provider=ProviderDataFormat.CLAUDE
        )

        assert normalized.category == ErrorCategory.TIMEOUT
        assert normalized.retryable is True

    # Cost calculation tests
    def test_calculate_cost_mistral(self, normalizer):
        cost = normalizer._calculate_cost("mistral", 1000, 500)
        # Mistral: $2/M prompt + $6/M completion
        expected = (1000 / 1_000_000 * 2.0) + (500 / 1_000_000 * 6.0)
        assert cost == pytest.approx(expected, rel=1e-6)

    def test_calculate_cost_ollama(self, normalizer):
        cost = normalizer._calculate_cost("ollama", 10000, 5000)
        assert cost == 0.0  # Ollama is free

    # Hash content tests
    def test_hash_content(self, normalizer):
        content = "Hello, world!"
        hash1 = normalizer._hash_content(content)
        hash2 = normalizer._hash_content(content)

        assert hash1 == hash2  # Same content = same hash
        assert len(hash1) == 16  # Truncated to 16 chars
        assert hash1 != content  # Not the original content

    def test_hash_content_none(self, normalizer):
        assert normalizer._hash_content(None) is None
        assert normalizer._hash_content("") is None


class TestNormalizedLLMEvent:
    """Tests for NormalizedLLMEvent dataclass."""

    def test_to_dict(self):
        event = NormalizedLLMEvent(
            event_id="test-123",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            provider=ProviderDataFormat.MISTRAL,
            model="mistral-large",
            latency_ms=100.5
        )

        result = event.to_dict()

        assert result["event_id"] == "test-123"
        assert result["provider"] == "mistral"
        assert result["model"] == "mistral-large"
        assert result["latency_ms"] == 100.5

    def test_to_otel_attributes(self):
        event = NormalizedLLMEvent(
            event_id="test-456",
            timestamp=datetime(2024, 1, 1),
            provider=ProviderDataFormat.CLAUDE,
            model="claude-3-sonnet",
            operation="chat",
            latency_ms=200,
            token_usage=NormalizedTokenUsage(
                prompt_tokens=10,
                completion_tokens=20,
                total_tokens=30,
                estimated_cost_usd=0.001
            )
        )

        attrs = event.to_otel_attributes()

        assert attrs["gen_ai.system"] == "claude"
        assert attrs["gen_ai.request.model"] == "claude-3-sonnet"
        assert attrs["gen_ai.operation.name"] == "chat"
        assert attrs["gen_ai.usage.prompt_tokens"] == 10
        assert attrs["gen_ai.usage.completion_tokens"] == 20
        assert attrs["synapsix.llm.latency_ms"] == 200
        assert attrs["synapsix.llm.estimated_cost_usd"] == 0.001
