"""
LLM Observability Decorators.

Provides easy-to-use decorators for instrumenting LLM operations
with automatic tracing, metrics, and logging.

Usage:
    @trace_llm_call(provider="mistral", model="mistral-large")
    async def generate_response(messages):
        ...

    @measure_llm_latency
    async def process_request():
        ...
"""

import asyncio
import functools
import logging
import time
import uuid
from typing import Any, Callable, Optional, TypeVar, Union

from .telemetry import get_llm_telemetry
from .metrics import get_llm_metrics
from .normalizer import (
    LLMDataNormalizer,
    NormalizedLLMEvent,
    ProviderDataFormat,
    CompletionStatus,
)

logger = logging.getLogger(__name__)

# Type variable for generic function signatures
F = TypeVar("F", bound=Callable[..., Any])


def trace_llm_call(
    provider: str = "unknown",
    model: str = "unknown",
    operation: str = "chat",
    capture_response: bool = False,
) -> Callable[[F], F]:
    """
    Decorator to trace LLM calls with OpenTelemetry.

    Automatically:
    - Creates a span for the LLM call
    - Records latency metrics
    - Logs request/response
    - Handles errors

    Args:
        provider: LLM provider name (mistral, claude, openai, ollama)
        model: Model name
        operation: Operation type (chat, completion, embedding)
        capture_response: Whether to capture response in span attributes

    Returns:
        Decorated function

    Example:
        @trace_llm_call(provider="mistral", model="mistral-large")
        async def generate(self, messages):
            response = await self._client.post(...)
            return response
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            telemetry = get_llm_telemetry()
            request_id = kwargs.pop("__request_id", None) or str(uuid.uuid4())
            session_id = kwargs.pop("__session_id", None)

            # Extract model from kwargs if available
            actual_model = kwargs.get("model", model)

            with telemetry.trace_llm_call(
                operation=operation,
                provider=provider,
                model=actual_model,
                request_id=request_id,
                session_id=session_id,
            ) as ctx:
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)

                    # Record response metrics
                    latency_ms = (time.time() - start_time) * 1000
                    ctx.attributes["latency_ms"] = latency_ms

                    # Try to extract token usage from result
                    if hasattr(result, "total_tokens"):
                        ctx.attributes["total_tokens"] = result.total_tokens
                    elif hasattr(result, "usage"):
                        usage = result.usage
                        if hasattr(usage, "total_tokens"):
                            ctx.attributes["total_tokens"] = usage.total_tokens
                    elif isinstance(result, dict):
                        if "usage" in result:
                            ctx.attributes["total_tokens"] = result["usage"].get("total_tokens", 0)
                        elif "total_tokens" in result:
                            ctx.attributes["total_tokens"] = result["total_tokens"]

                    return result

                except Exception as e:
                    latency_ms = (time.time() - start_time) * 1000
                    ctx.attributes["latency_ms"] = latency_ms
                    ctx.attributes["error"] = str(e)

                    # Record error event
                    telemetry.record_llm_error(
                        provider=provider,
                        error=e,
                        latency_ms=latency_ms,
                        request_id=request_id,
                    )
                    raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            telemetry = get_llm_telemetry()
            request_id = kwargs.pop("__request_id", None) or str(uuid.uuid4())
            session_id = kwargs.pop("__session_id", None)

            actual_model = kwargs.get("model", model)

            with telemetry.trace_llm_call(
                operation=operation,
                provider=provider,
                model=actual_model,
                request_id=request_id,
                session_id=session_id,
            ) as ctx:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    latency_ms = (time.time() - start_time) * 1000
                    ctx.attributes["latency_ms"] = latency_ms
                    return result
                except Exception as e:
                    latency_ms = (time.time() - start_time) * 1000
                    ctx.attributes["error"] = str(e)
                    telemetry.record_llm_error(
                        provider=provider,
                        error=e,
                        latency_ms=latency_ms,
                        request_id=request_id,
                    )
                    raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def measure_llm_latency(func: F) -> F:
    """
    Simple decorator to measure and log LLM call latency.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with latency measurement

    Example:
        @measure_llm_latency
        async def my_llm_call():
            ...
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            latency_ms = (time.time() - start_time) * 1000
            logger.debug(f"{func.__name__} completed in {latency_ms:.2f}ms")
            return result
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} failed after {latency_ms:.2f}ms: {e}")
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            latency_ms = (time.time() - start_time) * 1000
            logger.debug(f"{func.__name__} completed in {latency_ms:.2f}ms")
            return result
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} failed after {latency_ms:.2f}ms: {e}")
            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def record_llm_response(
    provider: str = "unknown",
    model: str = "unknown",
) -> Callable[[F], F]:
    """
    Decorator to automatically record LLM response as a telemetry event.

    The decorated function must return an LLMResponse object or dict with
    response data.

    Args:
        provider: LLM provider name
        model: Model name

    Returns:
        Decorated function

    Example:
        @record_llm_response(provider="mistral", model="mistral-large")
        async def generate(self, messages):
            response = await self._make_request(messages)
            return response  # Must be LLMResponse or compatible dict
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            telemetry = get_llm_telemetry()
            request_id = kwargs.get("__request_id") or str(uuid.uuid4())

            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000

                # Extract response data
                if hasattr(result, "raw_response"):
                    # LLMResponse object
                    response_data = result.raw_response or {}
                elif isinstance(result, dict):
                    response_data = result
                else:
                    response_data = {}

                # Extract request data if available
                request_data = None
                if args and hasattr(args[0], "config"):
                    # Likely a provider instance
                    request_data = {
                        "model": getattr(args[0].config, "model", model),
                        "temperature": getattr(args[0].config, "temperature", None),
                        "max_tokens": getattr(args[0].config, "max_tokens", None),
                    }

                # Record the event
                telemetry.record_llm_event(
                    provider=provider,
                    response=response_data,
                    request_data=request_data,
                    latency_ms=latency_ms,
                    request_id=request_id,
                )

                return result

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                telemetry.record_llm_error(
                    provider=provider,
                    error=e,
                    latency_ms=latency_ms,
                    request_id=request_id,
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            telemetry = get_llm_telemetry()
            request_id = kwargs.get("__request_id") or str(uuid.uuid4())

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000

                if hasattr(result, "raw_response"):
                    response_data = result.raw_response or {}
                elif isinstance(result, dict):
                    response_data = result
                else:
                    response_data = {}

                telemetry.record_llm_event(
                    provider=provider,
                    response=response_data,
                    latency_ms=latency_ms,
                    request_id=request_id,
                )

                return result

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                telemetry.record_llm_error(
                    provider=provider,
                    error=e,
                    latency_ms=latency_ms,
                    request_id=request_id,
                )
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class LLMCallContext:
    """
    Context manager for manual LLM call instrumentation.

    Provides more control than decorators for complex scenarios.

    Example:
        async with LLMCallContext(provider="mistral", model="mistral-large") as ctx:
            response = await provider.generate(messages)
            ctx.set_response(response)
            ctx.add_attribute("custom_metric", 42)
    """

    def __init__(
        self,
        provider: str,
        model: str,
        operation: str = "chat",
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """
        Initialize context.

        Args:
            provider: LLM provider name
            model: Model name
            operation: Operation type
            request_id: Request correlation ID
            session_id: Session ID
        """
        self.provider = provider
        self.model = model
        self.operation = operation
        self.request_id = request_id or str(uuid.uuid4())
        self.session_id = session_id

        self._telemetry = get_llm_telemetry()
        self._start_time: Optional[float] = None
        self._span_ctx = None
        self._response_data: Optional[dict] = None
        self._request_data: Optional[dict] = None
        self._attributes: dict = {}
        self._error: Optional[Exception] = None

    async def __aenter__(self):
        """Enter async context."""
        self._start_time = time.time()
        get_llm_metrics().increment_active_requests()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        get_llm_metrics().decrement_active_requests()

        latency_ms = (time.time() - self._start_time) * 1000

        if exc_type is not None:
            # Error occurred
            self._telemetry.record_llm_error(
                provider=self.provider,
                error=exc_val,
                request_data=self._request_data,
                latency_ms=latency_ms,
                request_id=self.request_id,
            )
        elif self._response_data is not None:
            # Success with response
            self._telemetry.record_llm_event(
                provider=self.provider,
                response=self._response_data,
                request_data=self._request_data,
                latency_ms=latency_ms,
                request_id=self.request_id,
                session_id=self.session_id,
            )

        return False  # Don't suppress exceptions

    def __enter__(self):
        """Enter sync context."""
        self._start_time = time.time()
        get_llm_metrics().increment_active_requests()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit sync context."""
        get_llm_metrics().decrement_active_requests()

        latency_ms = (time.time() - self._start_time) * 1000

        if exc_type is not None:
            self._telemetry.record_llm_error(
                provider=self.provider,
                error=exc_val,
                request_data=self._request_data,
                latency_ms=latency_ms,
                request_id=self.request_id,
            )
        elif self._response_data is not None:
            self._telemetry.record_llm_event(
                provider=self.provider,
                response=self._response_data,
                request_data=self._request_data,
                latency_ms=latency_ms,
                request_id=self.request_id,
                session_id=self.session_id,
            )

        return False

    def set_request(self, request_data: dict):
        """Set request data for telemetry."""
        self._request_data = request_data

    def set_response(self, response: Union[dict, Any]):
        """Set response data for telemetry."""
        if hasattr(response, "raw_response"):
            self._response_data = response.raw_response or {}
        elif isinstance(response, dict):
            self._response_data = response
        else:
            self._response_data = {"raw": str(response)}

    def add_attribute(self, key: str, value: Any):
        """Add custom attribute to telemetry."""
        self._attributes[key] = value

    @property
    def latency_ms(self) -> float:
        """Get current latency in milliseconds."""
        if self._start_time is None:
            return 0.0
        return (time.time() - self._start_time) * 1000


# Convenience function for one-off recording
def record_llm_call(
    provider: str,
    model: str,
    response: dict,
    request_data: Optional[dict] = None,
    latency_ms: float = 0.0,
    request_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> NormalizedLLMEvent:
    """
    Record a single LLM call event.

    Convenience function for recording LLM calls without decorators.

    Args:
        provider: Provider name
        model: Model name
        response: API response data
        request_data: Original request data
        latency_ms: Call latency
        request_id: Request correlation ID
        session_id: Session ID

    Returns:
        NormalizedLLMEvent
    """
    telemetry = get_llm_telemetry()
    return telemetry.record_llm_event(
        provider=provider,
        response=response,
        request_data=request_data,
        latency_ms=latency_ms,
        request_id=request_id,
        session_id=session_id,
    )
