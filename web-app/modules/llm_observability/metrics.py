"""
LLM Metrics Module.

Defines and manages OpenTelemetry metrics for LLM observability.
Exports metrics to OTEL Collector for storage in VictoriaMetrics.

Metrics follow GenAI semantic conventions where applicable.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from collections import defaultdict
from threading import Lock, RLock

from .config import get_observability_config, MetricsConfig
from .normalizer import (
    NormalizedLLMEvent,
    CompletionStatus,
    ErrorCategory,
    ProviderDataFormat,
)

logger = logging.getLogger(__name__)


# Try to import OpenTelemetry, with graceful fallback
try:
    from opentelemetry import metrics
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import (
        PeriodicExportingMetricReader,
    )
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logger.warning("OpenTelemetry SDK not available. Metrics will be collected locally only.")


@dataclass
class MetricSnapshot:
    """Point-in-time snapshot of a metric value."""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for a time window."""
    window_start: datetime
    window_end: datetime

    # Request counts
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cached_requests: int = 0

    # Token usage
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0

    # Costs
    total_cost_usd: float = 0.0

    # Latency stats (in ms)
    latency_sum: float = 0.0
    latency_count: int = 0
    latency_min: float = float("inf")
    latency_max: float = 0.0
    latency_values: List[float] = field(default_factory=list)

    # Breakdowns
    requests_by_provider: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    requests_by_model: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    requests_by_status: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    errors_by_category: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    tokens_by_provider: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    cost_by_provider: Dict[str, float] = field(default_factory=lambda: defaultdict(float))

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def error_rate(self) -> float:
        """Calculate error rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100

    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency."""
        if self.latency_count == 0:
            return 0.0
        return self.latency_sum / self.latency_count

    @property
    def p50_latency_ms(self) -> float:
        """Calculate 50th percentile latency."""
        return self._percentile(50)

    @property
    def p95_latency_ms(self) -> float:
        """Calculate 95th percentile latency."""
        return self._percentile(95)

    @property
    def p99_latency_ms(self) -> float:
        """Calculate 99th percentile latency."""
        return self._percentile(99)

    def _percentile(self, p: int) -> float:
        """Calculate percentile from latency values."""
        if not self.latency_values:
            return 0.0
        sorted_values = sorted(self.latency_values)
        idx = int(len(sorted_values) * (p / 100))
        idx = min(idx, len(sorted_values) - 1)
        return sorted_values[idx]

    @property
    def avg_tokens_per_request(self) -> float:
        """Calculate average tokens per request."""
        if self.total_requests == 0:
            return 0.0
        return self.total_tokens / self.total_requests

    @property
    def requests_per_minute(self) -> float:
        """Calculate requests per minute."""
        duration = (self.window_end - self.window_start).total_seconds()
        if duration == 0:
            return 0.0
        return (self.total_requests / duration) * 60

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "window_start": self.window_start.isoformat(),
            "window_end": self.window_end.isoformat(),
            "requests": {
                "total": self.total_requests,
                "successful": self.successful_requests,
                "failed": self.failed_requests,
                "cached": self.cached_requests,
                "success_rate_pct": round(self.success_rate, 2),
                "error_rate_pct": round(self.error_rate, 2),
                "requests_per_minute": round(self.requests_per_minute, 2),
            },
            "tokens": {
                "prompt": self.total_prompt_tokens,
                "completion": self.total_completion_tokens,
                "total": self.total_tokens,
                "avg_per_request": round(self.avg_tokens_per_request, 2),
            },
            "cost": {
                "total_usd": round(self.total_cost_usd, 4),
                "by_provider": dict(self.cost_by_provider),
            },
            "latency_ms": {
                "avg": round(self.avg_latency_ms, 2),
                "min": round(self.latency_min, 2) if self.latency_min != float("inf") else 0,
                "max": round(self.latency_max, 2),
                "p50": round(self.p50_latency_ms, 2),
                "p95": round(self.p95_latency_ms, 2),
                "p99": round(self.p99_latency_ms, 2),
            },
            "breakdown": {
                "by_provider": dict(self.requests_by_provider),
                "by_model": dict(self.requests_by_model),
                "by_status": dict(self.requests_by_status),
                "errors_by_category": dict(self.errors_by_category),
            },
        }


class LLMMetrics:
    """
    LLM Metrics collector with OpenTelemetry integration.

    Collects and exports metrics for:
    - Request counts (total, success, error)
    - Token usage (prompt, completion, total)
    - Latency (histogram)
    - Costs (by provider, model)
    - Error rates (by category)
    """

    def __init__(self, config: Optional[MetricsConfig] = None):
        """
        Initialize metrics collector.

        Args:
            config: Metrics configuration (uses default if not provided)
        """
        self.config = config or get_observability_config().metrics
        self._lock = Lock()
        self._active_requests_lock = Lock()  # Separate lock for active requests counter
        self._initialized = False

        # Local metrics storage (for non-OTEL fallback and aggregation)
        self._events: List[NormalizedLLMEvent] = []
        self._max_events = 10000  # Rolling window
        self._max_event_age_hours = 24  # Maximum age of events to keep

        # OTEL instruments (initialized lazily)
        self._meter = None
        self._request_counter = None
        self._token_counter = None
        self._latency_histogram = None
        self._cost_counter = None
        self._error_counter = None
        self._active_requests_gauge = None

        # Rate tracking
        self._hourly_tokens: Dict[str, int] = defaultdict(int)
        self._hourly_costs: Dict[str, float] = defaultdict(float)
        self._last_hour_reset = datetime.utcnow()

        if self.config.enabled:
            self._initialize_otel()

    def _initialize_otel(self):
        """Initialize OpenTelemetry metrics instruments."""
        if not OTEL_AVAILABLE:
            logger.info("Running in local metrics mode (OTEL not available)")
            self._initialized = True
            return

        try:
            obs_config = get_observability_config()

            # Create resource
            resource = Resource.create({
                SERVICE_NAME: obs_config.service_name,
                SERVICE_VERSION: obs_config.service_version,
                "deployment.environment": obs_config.environment,
            })

            # Create OTLP exporter
            exporter = OTLPMetricExporter(
                endpoint=obs_config.otlp.metrics_endpoint,
                timeout=int(obs_config.otlp.timeout_seconds),
            )

            # Create metric reader
            reader = PeriodicExportingMetricReader(
                exporter,
                export_interval_millis=int(self.config.export_interval_seconds * 1000),
            )

            # Create meter provider
            provider = MeterProvider(resource=resource, metric_readers=[reader])
            metrics.set_meter_provider(provider)

            # Get meter
            self._meter = metrics.get_meter(
                "synapsix.llm",
                version="1.0.0",
                schema_url="https://opentelemetry.io/schemas/1.21.0",
            )

            # Create instruments
            self._create_instruments()

            self._initialized = True
            logger.info("OpenTelemetry metrics initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize OTEL metrics: {e}")
            self._initialized = True  # Continue with local metrics

    def _create_instruments(self):
        """Create OTEL metric instruments."""
        if not self._meter:
            return

        # Request counter
        self._request_counter = self._meter.create_counter(
            name="llm.request.count",
            description="Total number of LLM requests",
            unit="1",
        )

        # Token counter
        self._token_counter = self._meter.create_counter(
            name="llm.token.usage",
            description="Total tokens used",
            unit="tokens",
        )

        # Latency histogram
        self._latency_histogram = self._meter.create_histogram(
            name="llm.request.duration",
            description="LLM request latency",
            unit="ms",
        )

        # Cost counter
        self._cost_counter = self._meter.create_counter(
            name="llm.cost.usd",
            description="Estimated LLM costs in USD",
            unit="USD",
        )

        # Error counter
        self._error_counter = self._meter.create_counter(
            name="llm.error.count",
            description="Total number of LLM errors",
            unit="1",
        )

        # Active requests gauge (using observable gauge)
        self._active_requests = 0
        self._active_requests_gauge = self._meter.create_observable_gauge(
            name="llm.request.active",
            description="Number of active LLM requests",
            unit="1",
            callbacks=[self._get_active_requests],
        )

    def _get_active_requests(self, options):
        """Callback for active requests gauge."""
        yield metrics.Observation(self._active_requests)

    def record_event(self, event: NormalizedLLMEvent):
        """
        Record an LLM event and emit metrics.

        Args:
            event: Normalized LLM event to record
        """
        with self._lock:
            # Store event locally
            self._events.append(event)

            # Trim by size
            if len(self._events) > self._max_events:
                self._events = self._events[-self._max_events:]

            # Trim by age (only periodically to avoid overhead)
            if len(self._events) % 100 == 0:
                cutoff = datetime.utcnow() - timedelta(hours=self._max_event_age_hours)
                self._events = [e for e in self._events if e.timestamp > cutoff]

            # Update hourly tracking
            self._update_hourly_tracking(event)

        # Emit OTEL metrics
        self._emit_otel_metrics(event)

        logger.debug(f"Recorded LLM event: {event.event_id} ({event.status.value})")

    def _update_hourly_tracking(self, event: NormalizedLLMEvent):
        """Update hourly token and cost tracking."""
        now = datetime.utcnow()

        # Reset hourly counters if hour changed
        if now.hour != self._last_hour_reset.hour or (now - self._last_hour_reset).seconds > 3600:
            self._hourly_tokens.clear()
            self._hourly_costs.clear()
            self._last_hour_reset = now

        hour_key = now.strftime("%Y-%m-%d-%H")
        self._hourly_tokens[hour_key] += event.token_usage.total_tokens
        self._hourly_costs[hour_key] += event.token_usage.estimated_cost_usd

    def _emit_otel_metrics(self, event: NormalizedLLMEvent):
        """Emit metrics to OpenTelemetry."""
        if not OTEL_AVAILABLE or not self._meter:
            return

        # Common attributes
        attrs = {
            "gen_ai.system": event.provider.value,
            "gen_ai.request.model": event.model,
            "gen_ai.operation.name": event.operation,
            "status": event.status.value,
        }

        try:
            # Record request
            if self._request_counter:
                self._request_counter.add(1, attrs)

            # Record tokens
            if self._token_counter and event.token_usage.total_tokens > 0:
                token_attrs = {**attrs, "token_type": "prompt"}
                self._token_counter.add(event.token_usage.prompt_tokens, token_attrs)

                token_attrs["token_type"] = "completion"
                self._token_counter.add(event.token_usage.completion_tokens, token_attrs)

            # Record latency
            if self._latency_histogram and event.latency_ms > 0:
                self._latency_histogram.record(event.latency_ms, attrs)

            # Record cost
            if self._cost_counter and event.token_usage.estimated_cost_usd > 0:
                self._cost_counter.add(event.token_usage.estimated_cost_usd, attrs)

            # Record error
            if self._error_counter and event.status == CompletionStatus.ERROR:
                error_attrs = {**attrs}
                if event.error:
                    error_attrs["error_category"] = event.error.category.value
                self._error_counter.add(1, error_attrs)

        except Exception as e:
            logger.warning(f"Failed to emit OTEL metrics: {e}")

    def increment_active_requests(self):
        """Increment active requests counter (thread-safe)."""
        with self._active_requests_lock:
            self._active_requests += 1

    def decrement_active_requests(self):
        """Decrement active requests counter (thread-safe)."""
        with self._active_requests_lock:
            self._active_requests = max(0, self._active_requests - 1)

    def get_aggregated_metrics(
        self,
        window_minutes: int = 60,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AggregatedMetrics:
        """
        Get aggregated metrics for a time window.

        Args:
            window_minutes: Time window in minutes (default: 60)
            provider: Filter by provider (optional)
            model: Filter by model (optional)

        Returns:
            AggregatedMetrics for the specified window
        """
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)

        agg = AggregatedMetrics(
            window_start=window_start,
            window_end=now,
        )

        with self._lock:
            for event in self._events:
                # Filter by time window
                if event.timestamp < window_start:
                    continue

                # Filter by provider
                if provider and event.provider.value != provider:
                    continue

                # Filter by model
                if model and event.model != model:
                    continue

                # Aggregate
                agg.total_requests += 1
                agg.requests_by_provider[event.provider.value] += 1
                agg.requests_by_model[event.model] += 1
                agg.requests_by_status[event.status.value] += 1

                if event.status == CompletionStatus.SUCCESS:
                    agg.successful_requests += 1
                else:
                    agg.failed_requests += 1
                    if event.error:
                        agg.errors_by_category[event.error.category.value] += 1

                # Tokens
                agg.total_prompt_tokens += event.token_usage.prompt_tokens
                agg.total_completion_tokens += event.token_usage.completion_tokens
                agg.total_tokens += event.token_usage.total_tokens
                agg.tokens_by_provider[event.provider.value] += event.token_usage.total_tokens

                # Cost
                agg.total_cost_usd += event.token_usage.estimated_cost_usd
                agg.cost_by_provider[event.provider.value] += event.token_usage.estimated_cost_usd

                # Latency
                if event.latency_ms > 0:
                    agg.latency_sum += event.latency_ms
                    agg.latency_count += 1
                    agg.latency_min = min(agg.latency_min, event.latency_ms)
                    agg.latency_max = max(agg.latency_max, event.latency_ms)
                    agg.latency_values.append(event.latency_ms)

        return agg

    def get_current_hour_usage(self) -> Dict[str, Any]:
        """Get current hour's token and cost usage."""
        now = datetime.utcnow()
        hour_key = now.strftime("%Y-%m-%d-%H")

        with self._lock:
            return {
                "hour": hour_key,
                "tokens": self._hourly_tokens.get(hour_key, 0),
                "cost_usd": round(self._hourly_costs.get(hour_key, 0.0), 4),
                "token_limit": get_observability_config().alerting.hourly_token_limit,
                "cost_limit_usd": get_observability_config().alerting.hourly_cost_limit_usd,
            }

    def check_alerts(self) -> List[Dict[str, Any]]:
        """
        Check for alert conditions.

        Returns:
            List of active alerts
        """
        alerts = []
        config = get_observability_config().alerting

        # Get recent metrics
        metrics_5m = self.get_aggregated_metrics(window_minutes=5)
        metrics_1h = self.get_aggregated_metrics(window_minutes=60)
        hourly = self.get_current_hour_usage()

        # Check latency
        if metrics_5m.p95_latency_ms > config.latency_critical_ms:
            alerts.append({
                "type": "latency_critical",
                "severity": "critical",
                "message": f"P95 latency ({metrics_5m.p95_latency_ms:.0f}ms) exceeds critical threshold ({config.latency_critical_ms}ms)",
                "value": metrics_5m.p95_latency_ms,
                "threshold": config.latency_critical_ms,
            })
        elif metrics_5m.p95_latency_ms > config.latency_warning_ms:
            alerts.append({
                "type": "latency_warning",
                "severity": "warning",
                "message": f"P95 latency ({metrics_5m.p95_latency_ms:.0f}ms) exceeds warning threshold ({config.latency_warning_ms}ms)",
                "value": metrics_5m.p95_latency_ms,
                "threshold": config.latency_warning_ms,
            })

        # Check error rate
        if metrics_5m.error_rate > config.error_rate_critical_pct:
            alerts.append({
                "type": "error_rate_critical",
                "severity": "critical",
                "message": f"Error rate ({metrics_5m.error_rate:.1f}%) exceeds critical threshold ({config.error_rate_critical_pct}%)",
                "value": metrics_5m.error_rate,
                "threshold": config.error_rate_critical_pct,
            })
        elif metrics_5m.error_rate > config.error_rate_warning_pct:
            alerts.append({
                "type": "error_rate_warning",
                "severity": "warning",
                "message": f"Error rate ({metrics_5m.error_rate:.1f}%) exceeds warning threshold ({config.error_rate_warning_pct}%)",
                "value": metrics_5m.error_rate,
                "threshold": config.error_rate_warning_pct,
            })

        # Check hourly token limit
        if hourly["tokens"] > config.hourly_token_limit:
            alerts.append({
                "type": "token_limit_exceeded",
                "severity": "warning",
                "message": f"Hourly token usage ({hourly['tokens']}) exceeds limit ({config.hourly_token_limit})",
                "value": hourly["tokens"],
                "threshold": config.hourly_token_limit,
            })

        # Check hourly cost limit
        if hourly["cost_usd"] > config.hourly_cost_limit_usd:
            alerts.append({
                "type": "cost_limit_exceeded",
                "severity": "warning",
                "message": f"Hourly cost (${hourly['cost_usd']:.2f}) exceeds limit (${config.hourly_cost_limit_usd})",
                "value": hourly["cost_usd"],
                "threshold": config.hourly_cost_limit_usd,
            })

        # Check rate limiting
        if metrics_5m.requests_per_minute > config.requests_per_minute_critical:
            alerts.append({
                "type": "rate_limit_critical",
                "severity": "critical",
                "message": f"Request rate ({metrics_5m.requests_per_minute:.1f}/min) approaching rate limit ({config.requests_per_minute_critical}/min)",
                "value": metrics_5m.requests_per_minute,
                "threshold": config.requests_per_minute_critical,
            })

        return alerts

    def get_status(self) -> Dict[str, Any]:
        """Get metrics collector status."""
        return {
            "enabled": self.config.enabled,
            "otel_available": OTEL_AVAILABLE,
            "initialized": self._initialized,
            "events_stored": len(self._events),
            "max_events": self._max_events,
            "active_requests": self._active_requests,
        }


# Singleton instance
_llm_metrics: Optional[LLMMetrics] = None


def get_llm_metrics() -> LLMMetrics:
    """
    Get LLM metrics singleton.

    Returns:
        LLMMetrics instance
    """
    global _llm_metrics
    if _llm_metrics is None:
        _llm_metrics = LLMMetrics()
    return _llm_metrics


def reset_metrics():
    """Reset metrics singleton (for testing)."""
    global _llm_metrics
    _llm_metrics = None
