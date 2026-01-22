"""
LLM Telemetry Module.

Provides distributed tracing and structured logging for LLM operations
with OpenTelemetry integration.

Features:
- Distributed tracing with spans for LLM calls
- Automatic context propagation
- Structured logging with correlation IDs
- Integration with OTEL Collector
"""

import logging
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Callable
from functools import wraps

from .config import get_observability_config, TracingConfig, LoggingConfig
from .normalizer import (
    LLMDataNormalizer,
    NormalizedLLMEvent,
    ProviderDataFormat,
    CompletionStatus,
    get_provider_enum,
)
from .metrics import get_llm_metrics

logger = logging.getLogger(__name__)


# Try to import OpenTelemetry, with graceful fallback
try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode, SpanKind
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    from opentelemetry.context import get_current
    OTEL_TRACING_AVAILABLE = True
except ImportError:
    OTEL_TRACING_AVAILABLE = False
    logger.warning("OpenTelemetry tracing SDK not available. Tracing will be disabled.")

# Try to import OTEL logging
try:
    from opentelemetry._logs import set_logger_provider
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
    OTEL_LOGGING_AVAILABLE = True
except ImportError:
    OTEL_LOGGING_AVAILABLE = False
    logger.warning("OpenTelemetry logging SDK not available. Structured logging will use standard logging.")


@dataclass
class SpanContext:
    """Context for an active span."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    start_time: datetime = None
    attributes: Dict[str, Any] = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.utcnow()
        if self.attributes is None:
            self.attributes = {}


class LLMTelemetry:
    """
    Main telemetry class for LLM observability.

    Provides:
    - Distributed tracing with OpenTelemetry
    - Structured logging
    - Automatic metrics emission
    - Context propagation
    """

    def __init__(self):
        """Initialize telemetry components."""
        self.config = get_observability_config()
        self._tracer = None
        self._propagator = None
        self._normalizer = LLMDataNormalizer()
        self._initialized = False

        # Initialize components
        if self.config.tracing.enabled:
            self._initialize_tracing()

        if self.config.logging.enabled:
            self._initialize_logging()

        self._initialized = True

    def _initialize_tracing(self):
        """Initialize OpenTelemetry tracing."""
        if not OTEL_TRACING_AVAILABLE:
            logger.info("Tracing running in no-op mode (OTEL not available)")
            return

        try:
            # Create resource
            resource = Resource.create({
                SERVICE_NAME: self.config.service_name,
                SERVICE_VERSION: self.config.service_version,
                "deployment.environment": self.config.environment,
                **self.config.resource_attributes,
            })

            # Create OTLP exporter
            exporter = OTLPSpanExporter(
                endpoint=self.config.otlp.traces_endpoint,
                timeout=int(self.config.otlp.timeout_seconds),
            )

            # Create tracer provider
            provider = TracerProvider(resource=resource)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            trace.set_tracer_provider(provider)

            # Get tracer
            self._tracer = trace.get_tracer(
                "synapsix.llm",
                version="1.0.0",
                schema_url="https://opentelemetry.io/schemas/1.21.0",
            )

            # Initialize propagator
            self._propagator = TraceContextTextMapPropagator()

            logger.info("OpenTelemetry tracing initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize OTEL tracing: {e}")

    def _initialize_logging(self):
        """Initialize OpenTelemetry logging."""
        if not OTEL_LOGGING_AVAILABLE:
            logger.info("Structured logging running in standard mode (OTEL logging not available)")
            return

        try:
            # Create resource
            resource = Resource.create({
                SERVICE_NAME: self.config.service_name,
                SERVICE_VERSION: self.config.service_version,
            })

            # Create OTLP log exporter
            log_exporter = OTLPLogExporter(
                endpoint=self.config.otlp.logs_endpoint,
                timeout=int(self.config.otlp.timeout_seconds),
            )

            # Create logger provider
            logger_provider = LoggerProvider(resource=resource)
            logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
            set_logger_provider(logger_provider)

            # Add OTEL handler to root logger
            handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
            logging.getLogger().addHandler(handler)

            logger.info("OpenTelemetry logging initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize OTEL logging: {e}")

    @contextmanager
    def trace_llm_call(
        self,
        operation: str,
        provider: str,
        model: str,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Generator[SpanContext, None, None]:
        """
        Context manager for tracing an LLM call.

        Usage:
            with telemetry.trace_llm_call("chat", "mistral", "mistral-large") as ctx:
                response = await provider.generate(messages)
                ctx.attributes["response_tokens"] = response.total_tokens

        Args:
            operation: Operation type (chat, completion, embedding)
            provider: Provider name
            model: Model name
            request_id: Optional request correlation ID
            session_id: Optional session ID
            attributes: Additional span attributes

        Yields:
            SpanContext with trace information
        """
        request_id = request_id or str(uuid.uuid4())
        start_time = time.time()
        metrics = get_llm_metrics()

        # Track active requests
        metrics.increment_active_requests()

        # Create span context
        ctx = SpanContext(
            trace_id=str(uuid.uuid4()),
            span_id=str(uuid.uuid4())[:16],
            attributes=attributes or {},
        )

        # Base attributes following GenAI semantic conventions
        base_attrs = {
            "gen_ai.system": provider,
            "gen_ai.request.model": model,
            "gen_ai.operation.name": operation,
            "synapsix.llm.request_id": request_id,
        }
        if session_id:
            base_attrs["synapsix.llm.session_id"] = session_id

        if attributes:
            base_attrs.update(attributes)

        if OTEL_TRACING_AVAILABLE and self._tracer:
            # Use OTEL tracing
            with self._tracer.start_as_current_span(
                name=f"llm.{operation}",
                kind=SpanKind.CLIENT,
                attributes=base_attrs,
            ) as span:
                # Get trace context
                span_ctx = span.get_span_context()
                ctx.trace_id = format(span_ctx.trace_id, "032x")
                ctx.span_id = format(span_ctx.span_id, "016x")

                try:
                    yield ctx

                    # Record success
                    latency_ms = (time.time() - start_time) * 1000
                    span.set_attribute("synapsix.llm.latency_ms", latency_ms)
                    span.set_attribute("synapsix.llm.status", "success")

                    # Add dynamic attributes from context
                    for key, value in ctx.attributes.items():
                        if isinstance(value, (str, int, float, bool)):
                            span.set_attribute(f"synapsix.llm.{key}", value)

                    span.set_status(Status(StatusCode.OK))

                except Exception as e:
                    # Record error
                    latency_ms = (time.time() - start_time) * 1000
                    span.set_attribute("synapsix.llm.latency_ms", latency_ms)
                    span.set_attribute("synapsix.llm.status", "error")
                    span.set_attribute("synapsix.llm.error.message", str(e))
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

                finally:
                    metrics.decrement_active_requests()
        else:
            # Fallback without OTEL
            try:
                yield ctx
            finally:
                metrics.decrement_active_requests()

    def record_llm_event(
        self,
        provider: str,
        response: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
    ) -> NormalizedLLMEvent:
        """
        Record an LLM event with full telemetry.

        Args:
            provider: Provider name (mistral, claude, openai, ollama)
            response: Raw API response
            request_data: Original request data
            latency_ms: Measured latency in milliseconds
            request_id: Request correlation ID
            session_id: Session ID
            trace_id: Trace ID from span context
            span_id: Span ID from span context

        Returns:
            NormalizedLLMEvent with all telemetry data
        """
        # Map provider string to enum using centralized function
        provider_enum = get_provider_enum(provider)

        # Normalize the event
        event = self._normalizer.normalize_response(
            provider=provider_enum,
            response=response,
            request_data=request_data,
            latency_ms=latency_ms,
        )

        # Add correlation IDs
        event.request_id = request_id
        event.session_id = session_id
        event.trace_id = trace_id
        event.span_id = span_id

        # Record metrics
        get_llm_metrics().record_event(event)

        # Log the event
        self._log_event(event)

        return event

    def record_llm_error(
        self,
        provider: str,
        error: Exception,
        request_data: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0,
        request_id: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> NormalizedLLMEvent:
        """
        Record an LLM error event.

        Args:
            provider: Provider name
            error: The exception that occurred
            request_data: Original request data
            latency_ms: Time before error
            request_id: Request correlation ID
            status_code: HTTP status code if available

        Returns:
            NormalizedLLMEvent with error details
        """
        # Map provider string to enum using centralized function
        provider_enum = get_provider_enum(provider)

        # Normalize error
        normalized_error = self._normalizer.normalize_error(
            error=error,
            provider=provider_enum,
            status_code=status_code,
        )

        # Create error event
        event = NormalizedLLMEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            provider=provider_enum,
            model=request_data.get("model", "unknown") if request_data else "unknown",
            operation="chat",
            status=CompletionStatus.ERROR,
            error=normalized_error,
            latency_ms=latency_ms,
            request_id=request_id,
        )

        # Record metrics
        get_llm_metrics().record_event(event)

        # Log error
        self._log_error(event)

        return event

    def _log_event(self, event: NormalizedLLMEvent):
        """Log an LLM event with structured data."""
        log_data = {
            "event_type": "llm_request",
            "event_id": event.event_id,
            "provider": event.provider.value,
            "model": event.model,
            "status": event.status.value,
            "latency_ms": event.latency_ms,
            "prompt_tokens": event.token_usage.prompt_tokens,
            "completion_tokens": event.token_usage.completion_tokens,
            "total_tokens": event.token_usage.total_tokens,
            "cost_usd": event.token_usage.estimated_cost_usd,
        }

        if event.request_id:
            log_data["request_id"] = event.request_id
        if event.trace_id:
            log_data["trace_id"] = event.trace_id
        if event.span_id:
            log_data["span_id"] = event.span_id

        logger.info(f"LLM request completed: {log_data}")

    def _log_error(self, event: NormalizedLLMEvent):
        """Log an LLM error with structured data."""
        log_data = {
            "event_type": "llm_error",
            "event_id": event.event_id,
            "provider": event.provider.value,
            "model": event.model,
            "latency_ms": event.latency_ms,
        }

        if event.error:
            log_data["error_category"] = event.error.category.value
            log_data["error_code"] = event.error.code
            log_data["error_message"] = event.error.message
            log_data["retryable"] = event.error.retryable

        if event.request_id:
            log_data["request_id"] = event.request_id

        logger.error(f"LLM request failed: {log_data}")

    def inject_context(self, carrier: Dict[str, str]) -> Dict[str, str]:
        """
        Inject trace context into a carrier (e.g., HTTP headers).

        Args:
            carrier: Dictionary to inject context into

        Returns:
            Carrier with trace context
        """
        if OTEL_TRACING_AVAILABLE and self._propagator:
            self._propagator.inject(carrier)
        return carrier

    def extract_context(self, carrier: Dict[str, str]):
        """
        Extract trace context from a carrier.

        Args:
            carrier: Dictionary containing trace context

        Returns:
            Extracted context
        """
        if OTEL_TRACING_AVAILABLE and self._propagator:
            return self._propagator.extract(carrier)
        return None

    def get_current_trace_id(self) -> Optional[str]:
        """Get current trace ID if available."""
        if OTEL_TRACING_AVAILABLE:
            span = trace.get_current_span()
            if span and span.get_span_context().is_valid:
                return format(span.get_span_context().trace_id, "032x")
        return None

    def get_current_span_id(self) -> Optional[str]:
        """Get current span ID if available."""
        if OTEL_TRACING_AVAILABLE:
            span = trace.get_current_span()
            if span and span.get_span_context().is_valid:
                return format(span.get_span_context().span_id, "016x")
        return None

    def get_status(self) -> Dict[str, Any]:
        """Get telemetry status."""
        return {
            "tracing_enabled": self.config.tracing.enabled,
            "logging_enabled": self.config.logging.enabled,
            "otel_tracing_available": OTEL_TRACING_AVAILABLE,
            "otel_logging_available": OTEL_LOGGING_AVAILABLE,
            "initialized": self._initialized,
            "service_name": self.config.service_name,
            "environment": self.config.environment,
        }


# Singleton instance
_llm_telemetry: Optional[LLMTelemetry] = None


def get_llm_telemetry() -> LLMTelemetry:
    """
    Get LLM telemetry singleton.

    Returns:
        LLMTelemetry instance
    """
    global _llm_telemetry
    if _llm_telemetry is None:
        _llm_telemetry = LLMTelemetry()
    return _llm_telemetry


def init_llm_telemetry() -> LLMTelemetry:
    """
    Initialize LLM telemetry.

    Call this at application startup to initialize all telemetry components.

    Returns:
        LLMTelemetry instance
    """
    global _llm_telemetry
    _llm_telemetry = LLMTelemetry()
    return _llm_telemetry


def reset_telemetry():
    """Reset telemetry singleton (for testing)."""
    global _llm_telemetry
    _llm_telemetry = None
