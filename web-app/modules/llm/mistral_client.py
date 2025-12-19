"""
Mistral AI Provider Implementation.

Implements the BaseLLMProvider interface for Mistral AI's API.
Supports chat completions, streaming, and function calling.
"""

import asyncio
import logging
import time
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from .base import (
    BaseLLMProvider,
    LLMCapability,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    MessageRole,
    ProviderType,
)

logger = logging.getLogger(__name__)


class MistralProvider(BaseLLMProvider):
    """
    Mistral AI LLM Provider.

    Implements the BaseLLMProvider interface for Mistral's API.
    Supports all major Mistral models including mistral-large, mistral-medium,
    mistral-small, and codestral.

    Example:
        >>> config = LLMConfig(
        ...     provider=ProviderType.MISTRAL,
        ...     api_key="your-key",
        ...     model="mistral-large-latest"
        ... )
        >>> provider = MistralProvider(config)
        >>> await provider.initialize()
        >>> response = await provider.generate([
        ...     LLMMessage(role=MessageRole.USER, content="Hello!")
        ... ])
        >>> print(response.content)
    """

    CHAT_ENDPOINT = "/chat/completions"
    MODELS_ENDPOINT = "/models"

    def __init__(self, config: LLMConfig):
        """Initialize the Mistral provider."""
        super().__init__(config)
        self._client: Optional[httpx.AsyncClient] = None
        self._available_models: List[str] = []

    @property
    def provider_type(self) -> ProviderType:
        """Return the provider type."""
        return ProviderType.MISTRAL

    @property
    def capabilities(self) -> List[LLMCapability]:
        """Return list of supported capabilities."""
        return [
            LLMCapability.CHAT,
            LLMCapability.COMPLETION,
            LLMCapability.STREAMING,
            LLMCapability.FUNCTION_CALLING,
            LLMCapability.JSON_MODE,
            LLMCapability.CODE_GENERATION,
        ]

    async def initialize(self) -> bool:
        """
        Initialize the HTTP client and validate configuration.

        Returns:
            True if initialization successful
        """
        if self._initialized:
            return True

        if not self.config.api_key:
            logger.error("Mistral API key not configured")
            return False

        try:
            self._client = httpx.AsyncClient(
                base_url=self.config.api_base or "https://api.mistral.ai/v1",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.config.timeout_seconds,
            )

            # Validate connection by fetching models
            response = await self._client.get(self.MODELS_ENDPOINT)
            if response.status_code == 200:
                data = response.json()
                self._available_models = [m["id"] for m in data.get("data", [])]
                logger.info(f"Mistral provider initialized. Available models: {len(self._available_models)}")
                self._initialized = True
                return True
            else:
                logger.error(f"Failed to connect to Mistral API: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize Mistral provider: {e}")
            return False

    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from Mistral.

        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            LLMResponse with the generated content
        """
        if not self._initialized:
            await self.initialize()

        if not self._client:
            raise RuntimeError("Mistral client not initialized")

        start_time = time.time()

        # Prepare request body
        request_body = self._prepare_request(messages, **kwargs)

        try:
            response = await self._client.post(
                self.CHAT_ENDPOINT,
                json=request_body,
            )

            latency_ms = (time.time() - start_time) * 1000

            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"Mistral API error: {response.status_code} - {error_detail}")
                raise RuntimeError(f"Mistral API error: {response.status_code}")

            data = response.json()
            return self._parse_response(data, latency_ms)

        except httpx.TimeoutException:
            logger.error("Mistral API request timed out")
            raise
        except Exception as e:
            logger.error(f"Mistral generation error: {e}")
            raise

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response from Mistral.

        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters

        Yields:
            String chunks of the response
        """
        if not self._initialized:
            await self.initialize()

        if not self._client:
            raise RuntimeError("Mistral client not initialized")

        # Prepare request body with streaming
        request_body = self._prepare_request(messages, **kwargs)
        request_body["stream"] = True

        try:
            async with self._client.stream(
                "POST",
                self.CHAT_ENDPOINT,
                json=request_body,
            ) as response:
                if response.status_code != 200:
                    error_detail = await response.aread()
                    logger.error(f"Mistral streaming error: {response.status_code}")
                    raise RuntimeError(f"Mistral API error: {response.status_code}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break

                        try:
                            import json
                            data = json.loads(data_str)
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except Exception as e:
                            logger.warning(f"Failed to parse streaming chunk: {e}")
                            continue

        except httpx.TimeoutException:
            logger.error("Mistral streaming request timed out")
            raise
        except Exception as e:
            logger.error(f"Mistral streaming error: {e}")
            raise

    async def generate_json(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a JSON response from Mistral.

        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters

        Returns:
            Parsed JSON response
        """
        kwargs["response_format"] = {"type": "json_object"}
        response = await self.generate(messages, **kwargs)

        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {response.content[:100]}")

    def _prepare_request(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare the request body for Mistral API."""
        # Convert messages to Mistral format
        formatted_messages = []
        for msg in messages:
            formatted_msg = {
                "role": msg.role.value,
                "content": msg.content
            }
            if msg.tool_calls:
                formatted_msg["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                formatted_msg["tool_call_id"] = msg.tool_call_id
            formatted_messages.append(formatted_msg)

        request_body = {
            "model": kwargs.get("model", self.config.model),
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p),
        }

        # Add safe_prompt for Mistral safety filter
        if self.config.safe_prompt:
            request_body["safe_prompt"] = True

        # Add response format if specified
        if kwargs.get("response_format"):
            request_body["response_format"] = kwargs["response_format"]

        # Add tools if specified (for function calling)
        if kwargs.get("tools"):
            request_body["tools"] = kwargs["tools"]
            if kwargs.get("tool_choice"):
                request_body["tool_choice"] = kwargs["tool_choice"]

        return request_body

    def _parse_response(
        self,
        data: Dict[str, Any],
        latency_ms: float
    ) -> LLMResponse:
        """Parse Mistral API response into LLMResponse."""
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        usage = data.get("usage", {})

        # Extract tool calls if present
        tool_calls = None
        if "tool_calls" in message:
            tool_calls = message["tool_calls"]

        return LLMResponse(
            content=message.get("content", ""),
            model=data.get("model", self.config.model),
            provider=ProviderType.MISTRAL,
            finish_reason=choice.get("finish_reason"),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            latency_ms=latency_ms,
            raw_response=data,
            tool_calls=tool_calls,
        )

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            self._initialized = False

    def get_available_models(self) -> List[str]:
        """Return list of available models."""
        return self._available_models

    async def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Note: This is an approximation. Mistral doesn't provide a tokenizer API.

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token for French/English
        return len(text) // 4


class MistralEmbeddingProvider:
    """
    Mistral Embeddings Provider.

    Provides text embedding capabilities using Mistral's embedding models.
    Useful for semantic search and similarity comparisons.
    """

    EMBEDDINGS_ENDPOINT = "/embeddings"

    def __init__(self, config: LLMConfig):
        """Initialize the embeddings provider."""
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> bool:
        """Initialize the HTTP client."""
        if self._client:
            return True

        if not self.config.api_key:
            logger.error("Mistral API key not configured")
            return False

        self._client = httpx.AsyncClient(
            base_url=self.config.api_base or "https://api.mistral.ai/v1",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        return True

    async def embed(
        self,
        texts: List[str],
        model: str = "mistral-embed"
    ) -> List[List[float]]:
        """
        Generate embeddings for texts.

        Args:
            texts: List of texts to embed
            model: Embedding model to use

        Returns:
            List of embedding vectors
        """
        if not self._client:
            await self.initialize()

        response = await self._client.post(
            self.EMBEDDINGS_ENDPOINT,
            json={
                "model": model,
                "input": texts,
            },
        )

        if response.status_code != 200:
            raise RuntimeError(f"Embedding error: {response.status_code}")

        data = response.json()
        embeddings = [item["embedding"] for item in data.get("data", [])]
        return embeddings

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
