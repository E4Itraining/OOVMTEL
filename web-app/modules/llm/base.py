"""
Base classes for LLM integration.

Provides abstract interfaces and common data structures for all LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from pydantic import BaseModel


class ProviderType(str, Enum):
    """Supported LLM provider types."""
    MISTRAL = "mistral"
    CLAUDE = "claude"
    OPENAI = "openai"
    OLLAMA = "ollama"  # For local/edge deployment
    CUSTOM = "custom"


class LLMCapability(str, Enum):
    """LLM capabilities that providers may support."""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    FUNCTION_CALLING = "function_calling"
    JSON_MODE = "json_mode"
    VISION = "vision"
    STREAMING = "streaming"
    CODE_GENERATION = "code_generation"


class MessageRole(str, Enum):
    """Message roles in a conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class LLMMessage:
    """Represents a message in a conversation."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        result = {
            "role": self.role.value,
            "content": self.content
        }
        if self.name:
            result["name"] = self.name
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result


@dataclass
class TokenUsage:
    """Token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    @property
    def estimated_cost_usd(self) -> float:
        """Estimate cost based on typical Mistral pricing."""
        # Approximate pricing (adjust based on model)
        prompt_cost = self.prompt_tokens * 0.000002  # $2 per 1M tokens
        completion_cost = self.completion_tokens * 0.000006  # $6 per 1M tokens
        return prompt_cost + completion_cost


class LLMResponse(BaseModel):
    """Standardized response from any LLM provider."""
    content: str
    model: str
    provider: ProviderType
    finish_reason: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0
    timestamp: datetime = None
    raw_response: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None

    class Config:
        use_enum_values = True

    def __init__(self, **data):
        if data.get("timestamp") is None:
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)

    @property
    def usage(self) -> TokenUsage:
        """Get token usage as TokenUsage object."""
        return TokenUsage(
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            total_tokens=self.total_tokens
        )


@dataclass
class LLMConfig:
    """Configuration for an LLM provider."""
    provider: ProviderType
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model: str = "mistral-large-latest"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    timeout_seconds: float = 30.0
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0

    # Model-specific options
    safe_prompt: bool = True  # Mistral safety filter
    json_mode: bool = False   # Force JSON output

    # Rate limiting
    requests_per_minute: int = 60
    tokens_per_minute: int = 100000

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "timeout_seconds": self.timeout_seconds,
        }


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All LLM integrations (Mistral, Claude, OpenAI, etc.) must implement this interface
    to ensure consistent behavior across the platform.
    """

    def __init__(self, config: LLMConfig):
        """
        Initialize the provider with configuration.

        Args:
            config: LLMConfig instance with provider settings
        """
        self.config = config
        self._initialized = False

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the provider type."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[LLMCapability]:
        """Return list of supported capabilities."""
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the provider (e.g., validate API key, establish connection).

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            messages: List of conversation messages
            **kwargs: Additional generation parameters

        Returns:
            LLMResponse with the generated content
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response from the LLM.

        Args:
            messages: List of conversation messages
            **kwargs: Additional generation parameters

        Yields:
            String chunks of the response
        """
        pass

    async def generate_with_context(
        self,
        user_message: str,
        system_prompt: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[List[LLMMessage]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response with system prompt and optional context.

        Args:
            user_message: The user's message
            system_prompt: System prompt to set context
            context: Additional context data to include
            history: Previous conversation messages
            **kwargs: Additional generation parameters

        Returns:
            LLMResponse with the generated content
        """
        messages = []

        # Add system prompt with optional context
        system_content = system_prompt
        if context:
            context_str = "\n\nContexte actuel:\n" + "\n".join(
                f"- {k}: {v}" for k, v in context.items()
            )
            system_content += context_str

        messages.append(LLMMessage(role=MessageRole.SYSTEM, content=system_content))

        # Add history if provided
        if history:
            messages.extend(history)

        # Add user message
        messages.append(LLMMessage(role=MessageRole.USER, content=user_message))

        return await self.generate(messages, **kwargs)

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the provider is healthy and accessible.

        Returns:
            Dictionary with health status information
        """
        try:
            # Simple test generation
            test_messages = [
                LLMMessage(role=MessageRole.USER, content="Respond with 'OK'")
            ]
            response = await self.generate(test_messages, max_tokens=10)

            return {
                "healthy": True,
                "provider": self.provider_type.value,
                "model": self.config.model,
                "latency_ms": response.latency_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "healthy": False,
                "provider": self.provider_type.value,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def supports(self, capability: LLMCapability) -> bool:
        """Check if provider supports a specific capability."""
        return capability in self.capabilities

    async def close(self):
        """Clean up resources (e.g., close HTTP clients)."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(provider={self.provider_type.value}, model={self.config.model})"
