"""
LLM Data Normalizer.

Handles heterogeneous data from multiple LLM providers and normalizes them
into a unified format for consistent telemetry and analysis.

Supported Providers:
- Mistral AI
- Anthropic Claude
- OpenAI GPT
- Ollama (local)
- Custom providers

This module ensures data coherence across different response formats,
error structures, and token counting methods.
"""

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class ProviderDataFormat(str, Enum):
    """LLM Provider data format identifiers."""
    MISTRAL = "mistral"
    CLAUDE = "claude"
    OPENAI = "openai"
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure_openai"
    CUSTOM = "custom"


# Centralized provider name mapping for consistency across modules
PROVIDER_NAME_MAP = {
    "mistral": ProviderDataFormat.MISTRAL,
    "claude": ProviderDataFormat.CLAUDE,
    "anthropic": ProviderDataFormat.CLAUDE,
    "openai": ProviderDataFormat.OPENAI,
    "azure": ProviderDataFormat.AZURE_OPENAI,
    "azure_openai": ProviderDataFormat.AZURE_OPENAI,
    "ollama": ProviderDataFormat.OLLAMA,
}


def get_provider_enum(provider_name: str) -> ProviderDataFormat:
    """
    Convert provider name string to ProviderDataFormat enum.

    Args:
        provider_name: Provider name (case-insensitive)

    Returns:
        ProviderDataFormat enum value
    """
    return PROVIDER_NAME_MAP.get(provider_name.lower(), ProviderDataFormat.CUSTOM)


class CompletionStatus(str, Enum):
    """Standardized completion status."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    CONTENT_FILTERED = "content_filtered"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class ErrorCategory(str, Enum):
    """Standardized error categories for analysis."""
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    QUOTA_EXCEEDED = "quota_exceeded"
    INVALID_REQUEST = "invalid_request"
    MODEL_UNAVAILABLE = "model_unavailable"
    CONTENT_POLICY = "content_policy"
    TIMEOUT = "timeout"
    NETWORK = "network"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


@dataclass
class NormalizedTokenUsage:
    """Normalized token usage across providers."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    # Additional details (provider-specific)
    cached_tokens: int = 0  # For Claude prompt caching
    reasoning_tokens: int = 0  # For OpenAI o1 models
    audio_tokens: int = 0  # For audio models

    # Cost calculation
    estimated_cost_usd: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cached_tokens": self.cached_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "audio_tokens": self.audio_tokens,
            "estimated_cost_usd": self.estimated_cost_usd,
        }


@dataclass
class NormalizedError:
    """Normalized error representation."""
    category: ErrorCategory
    code: str
    message: str
    provider_code: Optional[str] = None
    provider_message: Optional[str] = None
    retryable: bool = False
    retry_after_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category.value,
            "code": self.code,
            "message": self.message,
            "provider_code": self.provider_code,
            "provider_message": self.provider_message,
            "retryable": self.retryable,
            "retry_after_seconds": self.retry_after_seconds,
        }


@dataclass
class NormalizedLLMEvent:
    """
    Normalized LLM event for telemetry.

    This is the unified format for all LLM interactions regardless of provider.
    Used for metrics, traces, and logs.
    """
    # Event identification
    event_id: str
    timestamp: datetime
    request_id: Optional[str] = None
    session_id: Optional[str] = None

    # Provider information
    provider: ProviderDataFormat = ProviderDataFormat.CUSTOM
    model: str = ""
    model_version: Optional[str] = None

    # Request details
    operation: str = "chat"  # chat, completion, embedding, etc.
    messages_count: int = 0
    system_prompt_hash: Optional[str] = None  # Hash for privacy
    user_prompt_hash: Optional[str] = None  # Hash for privacy

    # Request parameters
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    stream: bool = False
    tools_count: int = 0

    # Response details
    status: CompletionStatus = CompletionStatus.SUCCESS
    finish_reason: Optional[str] = None
    response_hash: Optional[str] = None  # Hash for privacy

    # Token usage
    token_usage: NormalizedTokenUsage = field(default_factory=NormalizedTokenUsage)

    # Performance
    latency_ms: float = 0.0
    time_to_first_token_ms: Optional[float] = None  # For streaming
    tokens_per_second: Optional[float] = None

    # Error (if any)
    error: Optional[NormalizedError] = None

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Trace context
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "request_id": self.request_id,
            "session_id": self.session_id,
            "provider": self.provider.value,
            "model": self.model,
            "model_version": self.model_version,
            "operation": self.operation,
            "messages_count": self.messages_count,
            "system_prompt_hash": self.system_prompt_hash,
            "user_prompt_hash": self.user_prompt_hash,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stream": self.stream,
            "tools_count": self.tools_count,
            "status": self.status.value,
            "finish_reason": self.finish_reason,
            "response_hash": self.response_hash,
            "token_usage": self.token_usage.to_dict(),
            "latency_ms": self.latency_ms,
            "time_to_first_token_ms": self.time_to_first_token_ms,
            "tokens_per_second": self.tokens_per_second,
            "error": self.error.to_dict() if self.error else None,
            "metadata": self.metadata,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
        }

    def to_otel_attributes(self) -> Dict[str, Any]:
        """
        Convert to OpenTelemetry semantic convention attributes.

        Following GenAI semantic conventions:
        https://opentelemetry.io/docs/specs/semconv/gen-ai/
        """
        attrs = {
            # GenAI semantic conventions
            "gen_ai.system": self.provider.value,
            "gen_ai.request.model": self.model,
            "gen_ai.operation.name": self.operation,

            # Token usage
            "gen_ai.usage.prompt_tokens": self.token_usage.prompt_tokens,
            "gen_ai.usage.completion_tokens": self.token_usage.completion_tokens,

            # Response
            "gen_ai.response.finish_reasons": [self.finish_reason] if self.finish_reason else [],

            # Custom SYNAPSIX attributes
            "synapsix.llm.event_id": self.event_id,
            "synapsix.llm.latency_ms": self.latency_ms,
            "synapsix.llm.status": self.status.value,
            "synapsix.llm.messages_count": self.messages_count,
            "synapsix.llm.stream": self.stream,
            "synapsix.llm.tools_count": self.tools_count,
            "synapsix.llm.estimated_cost_usd": self.token_usage.estimated_cost_usd,
        }

        # Add optional attributes
        if self.temperature is not None:
            attrs["gen_ai.request.temperature"] = self.temperature
        if self.max_tokens is not None:
            attrs["gen_ai.request.max_tokens"] = self.max_tokens
        if self.top_p is not None:
            attrs["gen_ai.request.top_p"] = self.top_p
        if self.request_id:
            attrs["synapsix.llm.request_id"] = self.request_id
        if self.session_id:
            attrs["synapsix.llm.session_id"] = self.session_id
        if self.time_to_first_token_ms is not None:
            attrs["synapsix.llm.time_to_first_token_ms"] = self.time_to_first_token_ms
        if self.tokens_per_second is not None:
            attrs["synapsix.llm.tokens_per_second"] = self.tokens_per_second

        # Error attributes
        if self.error:
            attrs["synapsix.llm.error.category"] = self.error.category.value
            attrs["synapsix.llm.error.code"] = self.error.code
            attrs["synapsix.llm.error.message"] = self.error.message
            attrs["synapsix.llm.error.retryable"] = self.error.retryable

        return attrs


class LLMDataNormalizer:
    """
    Normalizes heterogeneous LLM provider data into unified format.

    Handles:
    - Different response structures (Mistral, Claude, OpenAI, Ollama)
    - Various error formats
    - Token counting discrepancies
    - Metadata extraction
    """

    # Mapping of provider finish reasons to standard ones
    FINISH_REASON_MAP = {
        # Mistral
        "stop": "stop",
        "length": "length",
        "tool_calls": "tool_calls",

        # OpenAI
        "stop": "stop",
        "length": "length",
        "content_filter": "content_filter",
        "tool_calls": "tool_calls",
        "function_call": "tool_calls",

        # Claude
        "end_turn": "stop",
        "max_tokens": "length",
        "stop_sequence": "stop",
        "tool_use": "tool_calls",

        # Ollama
        "stop": "stop",
    }

    # Error code mapping to categories
    ERROR_CODE_MAP = {
        # HTTP codes
        "401": ErrorCategory.AUTHENTICATION,
        "403": ErrorCategory.AUTHENTICATION,
        "429": ErrorCategory.RATE_LIMIT,
        "500": ErrorCategory.INTERNAL,
        "502": ErrorCategory.NETWORK,
        "503": ErrorCategory.MODEL_UNAVAILABLE,
        "504": ErrorCategory.TIMEOUT,

        # Provider-specific codes
        "rate_limit_exceeded": ErrorCategory.RATE_LIMIT,
        "insufficient_quota": ErrorCategory.QUOTA_EXCEEDED,
        "invalid_api_key": ErrorCategory.AUTHENTICATION,
        "model_not_found": ErrorCategory.MODEL_UNAVAILABLE,
        "context_length_exceeded": ErrorCategory.INVALID_REQUEST,
        "content_policy_violation": ErrorCategory.CONTENT_POLICY,
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the normalizer.

        Args:
            config: Optional configuration dict with cost settings
        """
        self.config = config or {}

        # Default cost per million tokens
        self.cost_per_million_prompt = self.config.get("cost_per_million_prompt", {
            "mistral": 2.0,
            "claude": 3.0,
            "openai": 5.0,
            "ollama": 0.0,
        })
        self.cost_per_million_completion = self.config.get("cost_per_million_completion", {
            "mistral": 6.0,
            "claude": 15.0,
            "openai": 15.0,
            "ollama": 0.0,
        })

    def normalize_mistral_response(
        self,
        response: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0,
        event_id: Optional[str] = None,
    ) -> NormalizedLLMEvent:
        """
        Normalize Mistral API response.

        Mistral response format:
        {
            "id": "chat-...",
            "object": "chat.completion",
            "model": "mistral-large-latest",
            "choices": [{"index": 0, "message": {...}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        }
        """
        event_id = event_id or str(uuid.uuid4())
        request_data = request_data or {}

        # Extract usage
        usage = response.get("usage", {})
        token_usage = NormalizedTokenUsage(
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
        )

        # Calculate cost
        token_usage.estimated_cost_usd = self._calculate_cost(
            "mistral", token_usage.prompt_tokens, token_usage.completion_tokens
        )

        # Extract finish reason
        choices = response.get("choices", [{}])
        finish_reason = choices[0].get("finish_reason", "unknown") if choices else "unknown"
        normalized_finish_reason = self.FINISH_REASON_MAP.get(finish_reason, finish_reason)

        # Extract model info
        model = response.get("model", request_data.get("model", "unknown"))

        # Build normalized event
        event = NormalizedLLMEvent(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            provider=ProviderDataFormat.MISTRAL,
            model=model,
            operation="chat",
            messages_count=len(request_data.get("messages", [])),
            temperature=request_data.get("temperature"),
            max_tokens=request_data.get("max_tokens"),
            top_p=request_data.get("top_p"),
            stream=request_data.get("stream", False),
            tools_count=len(request_data.get("tools", [])),
            status=CompletionStatus.SUCCESS,
            finish_reason=normalized_finish_reason,
            token_usage=token_usage,
            latency_ms=latency_ms,
            metadata={"provider_response_id": response.get("id")},
        )

        # Hash prompts for privacy
        if request_data.get("messages"):
            event.user_prompt_hash = self._hash_content(
                self._extract_user_prompt(request_data["messages"])
            )
            event.system_prompt_hash = self._hash_content(
                self._extract_system_prompt(request_data["messages"])
            )

        # Hash response
        if choices and choices[0].get("message", {}).get("content"):
            event.response_hash = self._hash_content(choices[0]["message"]["content"])

        # Calculate tokens per second if available
        if latency_ms > 0 and token_usage.completion_tokens > 0:
            event.tokens_per_second = (token_usage.completion_tokens / latency_ms) * 1000

        return event

    def normalize_claude_response(
        self,
        response: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0,
        event_id: Optional[str] = None,
    ) -> NormalizedLLMEvent:
        """
        Normalize Anthropic Claude API response.

        Claude response format:
        {
            "id": "msg_...",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "..."}],
            "model": "claude-3-sonnet-20240229",
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 10, "output_tokens": 20}
        }
        """
        event_id = event_id or str(uuid.uuid4())
        request_data = request_data or {}

        # Extract usage (Claude uses input_tokens/output_tokens)
        usage = response.get("usage", {})
        token_usage = NormalizedTokenUsage(
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            cached_tokens=usage.get("cache_read_input_tokens", 0),
        )

        # Calculate cost
        token_usage.estimated_cost_usd = self._calculate_cost(
            "claude", token_usage.prompt_tokens, token_usage.completion_tokens
        )

        # Extract finish reason (Claude uses stop_reason)
        stop_reason = response.get("stop_reason", "unknown")
        normalized_finish_reason = self.FINISH_REASON_MAP.get(stop_reason, stop_reason)

        # Extract model info
        model = response.get("model", request_data.get("model", "unknown"))

        # Extract content
        content_blocks = response.get("content", [])
        content = "".join(
            block.get("text", "") for block in content_blocks if block.get("type") == "text"
        )

        # Count tool uses
        tool_uses = sum(1 for block in content_blocks if block.get("type") == "tool_use")

        event = NormalizedLLMEvent(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            provider=ProviderDataFormat.CLAUDE,
            model=model,
            operation="chat",
            messages_count=len(request_data.get("messages", [])),
            temperature=request_data.get("temperature"),
            max_tokens=request_data.get("max_tokens"),
            top_p=request_data.get("top_p"),
            stream=request_data.get("stream", False),
            tools_count=len(request_data.get("tools", [])),
            status=CompletionStatus.SUCCESS,
            finish_reason=normalized_finish_reason,
            token_usage=token_usage,
            latency_ms=latency_ms,
            metadata={
                "provider_response_id": response.get("id"),
                "tool_uses_count": tool_uses,
            },
        )

        # Hash content
        if content:
            event.response_hash = self._hash_content(content)

        # Calculate tokens per second
        if latency_ms > 0 and token_usage.completion_tokens > 0:
            event.tokens_per_second = (token_usage.completion_tokens / latency_ms) * 1000

        return event

    def normalize_openai_response(
        self,
        response: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0,
        event_id: Optional[str] = None,
    ) -> NormalizedLLMEvent:
        """
        Normalize OpenAI API response.

        OpenAI response format:
        {
            "id": "chatcmpl-...",
            "object": "chat.completion",
            "model": "gpt-4",
            "choices": [{"index": 0, "message": {...}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        }
        """
        event_id = event_id or str(uuid.uuid4())
        request_data = request_data or {}

        # Extract usage
        usage = response.get("usage", {})
        token_usage = NormalizedTokenUsage(
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            reasoning_tokens=usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0),
        )

        # Calculate cost
        token_usage.estimated_cost_usd = self._calculate_cost(
            "openai", token_usage.prompt_tokens, token_usage.completion_tokens
        )

        # Extract finish reason
        choices = response.get("choices", [{}])
        finish_reason = choices[0].get("finish_reason", "unknown") if choices else "unknown"
        normalized_finish_reason = self.FINISH_REASON_MAP.get(finish_reason, finish_reason)

        # Extract model info
        model = response.get("model", request_data.get("model", "unknown"))

        event = NormalizedLLMEvent(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            provider=ProviderDataFormat.OPENAI,
            model=model,
            operation="chat",
            messages_count=len(request_data.get("messages", [])),
            temperature=request_data.get("temperature"),
            max_tokens=request_data.get("max_tokens"),
            top_p=request_data.get("top_p"),
            stream=request_data.get("stream", False),
            tools_count=len(request_data.get("tools", [])),
            status=CompletionStatus.SUCCESS,
            finish_reason=normalized_finish_reason,
            token_usage=token_usage,
            latency_ms=latency_ms,
            metadata={"provider_response_id": response.get("id")},
        )

        # Hash content
        if choices and choices[0].get("message", {}).get("content"):
            event.response_hash = self._hash_content(choices[0]["message"]["content"])

        # Calculate tokens per second
        if latency_ms > 0 and token_usage.completion_tokens > 0:
            event.tokens_per_second = (token_usage.completion_tokens / latency_ms) * 1000

        return event

    def normalize_ollama_response(
        self,
        response: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0,
        event_id: Optional[str] = None,
    ) -> NormalizedLLMEvent:
        """
        Normalize Ollama API response.

        Ollama response format:
        {
            "model": "llama2",
            "message": {"role": "assistant", "content": "..."},
            "done": true,
            "total_duration": 123456789,
            "load_duration": 123456,
            "prompt_eval_count": 10,
            "eval_count": 20
        }
        """
        event_id = event_id or str(uuid.uuid4())
        request_data = request_data or {}

        # Extract usage (Ollama uses different field names)
        token_usage = NormalizedTokenUsage(
            prompt_tokens=response.get("prompt_eval_count", 0),
            completion_tokens=response.get("eval_count", 0),
            total_tokens=response.get("prompt_eval_count", 0) + response.get("eval_count", 0),
        )
        # Ollama is local, no cost
        token_usage.estimated_cost_usd = 0.0

        # Extract model info
        model = response.get("model", request_data.get("model", "unknown"))

        # Determine finish reason
        done = response.get("done", False)
        finish_reason = "stop" if done else "unknown"

        # Calculate actual latency from Ollama timings if available
        total_duration_ns = response.get("total_duration", 0)
        if total_duration_ns > 0:
            latency_ms = total_duration_ns / 1_000_000  # ns to ms

        event = NormalizedLLMEvent(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            provider=ProviderDataFormat.OLLAMA,
            model=model,
            operation="chat",
            messages_count=len(request_data.get("messages", [])),
            temperature=request_data.get("temperature"),
            stream=request_data.get("stream", False),
            status=CompletionStatus.SUCCESS,
            finish_reason=finish_reason,
            token_usage=token_usage,
            latency_ms=latency_ms,
            metadata={
                "load_duration_ns": response.get("load_duration"),
                "prompt_eval_duration_ns": response.get("prompt_eval_duration"),
                "eval_duration_ns": response.get("eval_duration"),
            },
        )

        # Hash content
        message = response.get("message", {})
        if message.get("content"):
            event.response_hash = self._hash_content(message["content"])

        # Calculate tokens per second from eval_duration
        eval_duration_ns = response.get("eval_duration", 0)
        if eval_duration_ns > 0 and token_usage.completion_tokens > 0:
            eval_duration_s = eval_duration_ns / 1_000_000_000
            event.tokens_per_second = token_usage.completion_tokens / eval_duration_s

        return event

    def normalize_error(
        self,
        error: Union[Exception, Dict[str, Any], str],
        provider: ProviderDataFormat,
        status_code: Optional[int] = None,
    ) -> NormalizedError:
        """
        Normalize error from any provider.

        Args:
            error: The error (Exception, dict, or string)
            provider: The provider that raised the error
            status_code: HTTP status code if available

        Returns:
            NormalizedError with categorization
        """
        # Extract error details
        if isinstance(error, Exception):
            error_message = str(error)
            error_code = type(error).__name__
        elif isinstance(error, dict):
            error_message = error.get("message", error.get("error", str(error)))
            error_code = str(error.get("code", error.get("type", "unknown")))
        else:
            error_message = str(error)
            error_code = "unknown"

        # Determine category
        category = ErrorCategory.UNKNOWN
        retryable = False
        retry_after = None

        # Check HTTP status code
        if status_code:
            code_str = str(status_code)
            if code_str in self.ERROR_CODE_MAP:
                category = self.ERROR_CODE_MAP[code_str]
            elif status_code >= 500:
                category = ErrorCategory.INTERNAL
                retryable = True
            elif status_code == 429:
                category = ErrorCategory.RATE_LIMIT
                retryable = True
                retry_after = 60.0  # Default retry after

        # Check error code/message for more specific categorization
        error_lower = error_message.lower() + " " + error_code.lower()

        if any(k in error_lower for k in ["rate limit", "rate_limit", "too many requests"]):
            category = ErrorCategory.RATE_LIMIT
            retryable = True
        elif any(k in error_lower for k in ["timeout", "timed out"]):
            category = ErrorCategory.TIMEOUT
            retryable = True
        elif any(k in error_lower for k in ["auth", "api key", "unauthorized", "forbidden"]):
            category = ErrorCategory.AUTHENTICATION
        elif any(k in error_lower for k in ["quota", "exceeded", "billing"]):
            category = ErrorCategory.QUOTA_EXCEEDED
        elif any(k in error_lower for k in ["content filter", "safety", "policy"]):
            category = ErrorCategory.CONTENT_POLICY
        elif any(k in error_lower for k in ["network", "connection", "dns"]):
            category = ErrorCategory.NETWORK
            retryable = True
        elif any(k in error_lower for k in ["model", "not found", "unavailable"]):
            category = ErrorCategory.MODEL_UNAVAILABLE

        return NormalizedError(
            category=category,
            code=f"{provider.value}_{error_code}",
            message=error_message[:500],  # Truncate long messages
            provider_code=error_code,
            provider_message=error_message,
            retryable=retryable,
            retry_after_seconds=retry_after,
        )

    def normalize_response(
        self,
        provider: ProviderDataFormat,
        response: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0,
        event_id: Optional[str] = None,
    ) -> NormalizedLLMEvent:
        """
        Auto-detect and normalize response from any provider.

        Args:
            provider: The provider type
            response: Raw API response
            request_data: Original request data
            latency_ms: Measured latency
            event_id: Optional event ID

        Returns:
            NormalizedLLMEvent
        """
        normalizers = {
            ProviderDataFormat.MISTRAL: self.normalize_mistral_response,
            ProviderDataFormat.CLAUDE: self.normalize_claude_response,
            ProviderDataFormat.OPENAI: self.normalize_openai_response,
            ProviderDataFormat.AZURE_OPENAI: self.normalize_openai_response,  # Same format
            ProviderDataFormat.OLLAMA: self.normalize_ollama_response,
        }

        normalizer = normalizers.get(provider)
        if normalizer:
            return normalizer(response, request_data, latency_ms, event_id)
        else:
            # Generic normalization for custom providers
            return self._normalize_generic(provider, response, request_data, latency_ms, event_id)

    def _normalize_generic(
        self,
        provider: ProviderDataFormat,
        response: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0,
        event_id: Optional[str] = None,
    ) -> NormalizedLLMEvent:
        """Generic normalization for unknown providers."""
        event_id = event_id or str(uuid.uuid4())
        request_data = request_data or {}

        # Try to extract common fields
        usage = response.get("usage", {})
        token_usage = NormalizedTokenUsage(
            prompt_tokens=usage.get("prompt_tokens", usage.get("input_tokens", 0)),
            completion_tokens=usage.get("completion_tokens", usage.get("output_tokens", 0)),
        )
        token_usage.total_tokens = token_usage.prompt_tokens + token_usage.completion_tokens

        return NormalizedLLMEvent(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            provider=provider,
            model=response.get("model", request_data.get("model", "unknown")),
            operation="chat",
            status=CompletionStatus.SUCCESS,
            token_usage=token_usage,
            latency_ms=latency_ms,
            metadata={"raw_response_keys": list(response.keys())},
        )

    def _calculate_cost(self, provider: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate estimated cost in USD."""
        prompt_rate = self.cost_per_million_prompt.get(provider, 0.0)
        completion_rate = self.cost_per_million_completion.get(provider, 0.0)

        prompt_cost = (prompt_tokens / 1_000_000) * prompt_rate
        completion_cost = (completion_tokens / 1_000_000) * completion_rate

        return round(prompt_cost + completion_cost, 6)

    def _hash_content(self, content: Optional[str]) -> Optional[str]:
        """Generate SHA256 hash of content for privacy-preserving tracking."""
        if not content:
            return None
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _extract_user_prompt(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        """Extract the last user message from conversation."""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return msg.get("content", "")
        return None

    def _extract_system_prompt(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        """Extract system prompt from conversation."""
        for msg in messages:
            if msg.get("role") == "system":
                return msg.get("content", "")
        return None


# Convenience function for quick normalization
def normalize_llm_event(
    provider: str,
    response: Dict[str, Any],
    request_data: Optional[Dict[str, Any]] = None,
    latency_ms: float = 0.0,
) -> NormalizedLLMEvent:
    """
    Quick normalization helper.

    Args:
        provider: Provider name (mistral, claude, openai, ollama)
        response: Raw API response
        request_data: Original request data
        latency_ms: Measured latency

    Returns:
        NormalizedLLMEvent
    """
    provider_enum = get_provider_enum(provider)
    normalizer = LLMDataNormalizer()

    return normalizer.normalize_response(
        provider=provider_enum,
        response=response,
        request_data=request_data,
        latency_ms=latency_ms,
    )
