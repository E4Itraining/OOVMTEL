"""
LLM Observability Configuration.

Manages settings for telemetry collection, metrics export, and normalization.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


class ExportProtocol(str, Enum):
    """Telemetry export protocol."""
    OTLP_GRPC = "otlp_grpc"
    OTLP_HTTP = "otlp_http"
    PROMETHEUS = "prometheus"
    CONSOLE = "console"


class LogLevel(str, Enum):
    """Logging verbosity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class OTLPExporterConfig:
    """OTLP Exporter configuration."""
    # Endpoints (defaults to local OTEL collector)
    traces_endpoint: str = "http://localhost:4318/v1/traces"
    metrics_endpoint: str = "http://localhost:4318/v1/metrics"
    logs_endpoint: str = "http://localhost:4318/v1/logs"

    # Connection settings
    timeout_seconds: float = 10.0
    compression: str = "gzip"  # gzip, none
    headers: Dict[str, str] = field(default_factory=dict)

    # Retry settings
    max_retries: int = 3
    retry_delay_ms: int = 1000

    @classmethod
    def from_env(cls) -> "OTLPExporterConfig":
        """Create config from environment variables."""
        return cls(
            traces_endpoint=os.getenv(
                "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
                os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318") + "/v1/traces"
            ),
            metrics_endpoint=os.getenv(
                "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
                os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318") + "/v1/metrics"
            ),
            logs_endpoint=os.getenv(
                "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT",
                os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318") + "/v1/logs"
            ),
            timeout_seconds=float(os.getenv("OTEL_EXPORTER_OTLP_TIMEOUT", "10")),
            compression=os.getenv("OTEL_EXPORTER_OTLP_COMPRESSION", "gzip"),
        )


@dataclass
class MetricsConfig:
    """Metrics collection configuration."""
    # Enable/disable metrics
    enabled: bool = True

    # Export interval
    export_interval_seconds: float = 60.0

    # Histogram buckets for latency (in milliseconds)
    latency_buckets: List[float] = field(default_factory=lambda: [
        10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 30000
    ])

    # Token bucket sizes for cost tracking
    token_buckets: List[int] = field(default_factory=lambda: [
        10, 50, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000
    ])

    # Cost calculation (per million tokens, in USD)
    cost_per_million_prompt_tokens: Dict[str, float] = field(default_factory=lambda: {
        "mistral": 2.0,      # $2/M prompt tokens
        "claude": 3.0,       # $3/M prompt tokens (Sonnet)
        "openai": 5.0,       # $5/M prompt tokens (GPT-4)
        "ollama": 0.0,       # Local, no cost
    })
    cost_per_million_completion_tokens: Dict[str, float] = field(default_factory=lambda: {
        "mistral": 6.0,      # $6/M completion tokens
        "claude": 15.0,      # $15/M completion tokens (Sonnet)
        "openai": 15.0,      # $15/M completion tokens (GPT-4)
        "ollama": 0.0,       # Local, no cost
    })

    @classmethod
    def from_env(cls) -> "MetricsConfig":
        """Create config from environment variables."""
        return cls(
            enabled=os.getenv("LLM_METRICS_ENABLED", "true").lower() == "true",
            export_interval_seconds=float(os.getenv("LLM_METRICS_EXPORT_INTERVAL", "60")),
        )


@dataclass
class TracingConfig:
    """Distributed tracing configuration."""
    # Enable/disable tracing
    enabled: bool = True

    # Sampling
    sample_rate: float = 1.0  # 1.0 = 100% of requests

    # Span attributes to include
    include_prompt: bool = False  # Privacy: don't log prompts by default
    include_response: bool = False  # Privacy: don't log responses by default
    include_model_params: bool = True
    include_token_counts: bool = True

    # Max content length to log (if enabled)
    max_prompt_length: int = 1000
    max_response_length: int = 1000

    # Propagation
    propagation_format: str = "w3c"  # w3c, b3, jaeger

    @classmethod
    def from_env(cls) -> "TracingConfig":
        """Create config from environment variables."""
        return cls(
            enabled=os.getenv("LLM_TRACING_ENABLED", "true").lower() == "true",
            sample_rate=float(os.getenv("LLM_TRACING_SAMPLE_RATE", "1.0")),
            include_prompt=os.getenv("LLM_TRACING_INCLUDE_PROMPT", "false").lower() == "true",
            include_response=os.getenv("LLM_TRACING_INCLUDE_RESPONSE", "false").lower() == "true",
            include_model_params=os.getenv("LLM_TRACING_INCLUDE_MODEL_PARAMS", "true").lower() == "true",
            include_token_counts=os.getenv("LLM_TRACING_INCLUDE_TOKEN_COUNTS", "true").lower() == "true",
        )


@dataclass
class LoggingConfig:
    """Structured logging configuration."""
    # Enable/disable OTEL logging
    enabled: bool = True

    # Log level
    level: LogLevel = LogLevel.INFO

    # Include correlation IDs
    include_trace_id: bool = True
    include_span_id: bool = True

    # Structured fields
    include_request_id: bool = True
    include_user_id: bool = False  # Privacy
    include_session_id: bool = True

    @classmethod
    def from_env(cls) -> "LoggingConfig":
        """Create config from environment variables."""
        level_str = os.getenv("LLM_LOG_LEVEL", "info").lower()
        level = LogLevel(level_str) if level_str in [l.value for l in LogLevel] else LogLevel.INFO

        return cls(
            enabled=os.getenv("LLM_LOGGING_ENABLED", "true").lower() == "true",
            level=level,
            include_trace_id=os.getenv("LLM_LOG_INCLUDE_TRACE_ID", "true").lower() == "true",
            include_span_id=os.getenv("LLM_LOG_INCLUDE_SPAN_ID", "true").lower() == "true",
        )


@dataclass
class AlertingConfig:
    """Alerting thresholds configuration."""
    # Latency thresholds (ms)
    latency_warning_ms: float = 5000  # 5 seconds
    latency_critical_ms: float = 15000  # 15 seconds

    # Error rate thresholds (percentage)
    error_rate_warning_pct: float = 5.0
    error_rate_critical_pct: float = 10.0

    # Token usage thresholds
    daily_token_limit: int = 1000000  # 1M tokens/day
    hourly_token_limit: int = 100000  # 100k tokens/hour

    # Cost thresholds (USD)
    daily_cost_limit_usd: float = 100.0
    hourly_cost_limit_usd: float = 20.0

    # Rate limiting
    requests_per_minute_warning: int = 50
    requests_per_minute_critical: int = 55

    @classmethod
    def from_env(cls) -> "AlertingConfig":
        """Create config from environment variables."""
        return cls(
            latency_warning_ms=float(os.getenv("LLM_ALERT_LATENCY_WARNING_MS", "5000")),
            latency_critical_ms=float(os.getenv("LLM_ALERT_LATENCY_CRITICAL_MS", "15000")),
            error_rate_warning_pct=float(os.getenv("LLM_ALERT_ERROR_RATE_WARNING_PCT", "5.0")),
            error_rate_critical_pct=float(os.getenv("LLM_ALERT_ERROR_RATE_CRITICAL_PCT", "10.0")),
            daily_token_limit=int(os.getenv("LLM_ALERT_DAILY_TOKEN_LIMIT", "1000000")),
            hourly_token_limit=int(os.getenv("LLM_ALERT_HOURLY_TOKEN_LIMIT", "100000")),
            daily_cost_limit_usd=float(os.getenv("LLM_ALERT_DAILY_COST_LIMIT_USD", "100.0")),
            hourly_cost_limit_usd=float(os.getenv("LLM_ALERT_HOURLY_COST_LIMIT_USD", "20.0")),
        )


@dataclass
class LLMObservabilityConfig:
    """
    Main configuration for LLM Observability module.

    Combines all sub-configurations for comprehensive telemetry management.
    """
    # Service identification
    service_name: str = "synapsix-llm"
    service_version: str = "1.0.0"
    environment: str = "production"

    # Sub-configurations
    otlp: OTLPExporterConfig = field(default_factory=OTLPExporterConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    tracing: TracingConfig = field(default_factory=TracingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    alerting: AlertingConfig = field(default_factory=AlertingConfig)

    # Resource attributes (added to all telemetry)
    resource_attributes: Dict[str, str] = field(default_factory=lambda: {
        "deployment.environment": "production",
        "service.namespace": "synapsix",
    })

    @classmethod
    def from_env(cls) -> "LLMObservabilityConfig":
        """Create complete config from environment variables."""
        return cls(
            service_name=os.getenv("OTEL_SERVICE_NAME", "synapsix-llm"),
            service_version=os.getenv("SERVICE_VERSION", "1.0.0"),
            environment=os.getenv("DEPLOYMENT_ENVIRONMENT", "production"),
            otlp=OTLPExporterConfig.from_env(),
            metrics=MetricsConfig.from_env(),
            tracing=TracingConfig.from_env(),
            logging=LoggingConfig.from_env(),
            alerting=AlertingConfig.from_env(),
            resource_attributes={
                "deployment.environment": os.getenv("DEPLOYMENT_ENVIRONMENT", "production"),
                "service.namespace": os.getenv("SERVICE_NAMESPACE", "synapsix"),
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "service_name": self.service_name,
            "service_version": self.service_version,
            "environment": self.environment,
            "metrics_enabled": self.metrics.enabled,
            "tracing_enabled": self.tracing.enabled,
            "logging_enabled": self.logging.enabled,
            "sample_rate": self.tracing.sample_rate,
            "otlp_endpoint": self.otlp.traces_endpoint.rsplit("/", 2)[0],
            "alerting": {
                "latency_warning_ms": self.alerting.latency_warning_ms,
                "latency_critical_ms": self.alerting.latency_critical_ms,
                "error_rate_warning_pct": self.alerting.error_rate_warning_pct,
                "daily_token_limit": self.alerting.daily_token_limit,
            },
        }


# Singleton pattern
_config: Optional[LLMObservabilityConfig] = None


def get_observability_config() -> LLMObservabilityConfig:
    """
    Get observability config singleton.

    Returns:
        LLMObservabilityConfig instance loaded from environment
    """
    global _config
    if _config is None:
        _config = LLMObservabilityConfig.from_env()
    return _config


def reload_config() -> LLMObservabilityConfig:
    """
    Reload configuration from environment.

    Returns:
        New LLMObservabilityConfig instance
    """
    global _config
    _config = LLMObservabilityConfig.from_env()
    return _config


# Environment variable template for documentation
ENV_TEMPLATE = """
# ==============================================
# SYNAPSIX LLM Observability Configuration
# ==============================================

# Service Identification
OTEL_SERVICE_NAME=synapsix-llm
SERVICE_VERSION=1.0.0
DEPLOYMENT_ENVIRONMENT=production
SERVICE_NAMESPACE=synapsix

# OTLP Exporter (to OTEL Collector)
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
OTEL_EXPORTER_OTLP_TIMEOUT=10
OTEL_EXPORTER_OTLP_COMPRESSION=gzip

# Metrics
LLM_METRICS_ENABLED=true
LLM_METRICS_EXPORT_INTERVAL=60

# Tracing
LLM_TRACING_ENABLED=true
LLM_TRACING_SAMPLE_RATE=1.0
LLM_TRACING_INCLUDE_PROMPT=false
LLM_TRACING_INCLUDE_RESPONSE=false
LLM_TRACING_INCLUDE_MODEL_PARAMS=true
LLM_TRACING_INCLUDE_TOKEN_COUNTS=true

# Logging
LLM_LOGGING_ENABLED=true
LLM_LOG_LEVEL=info
LLM_LOG_INCLUDE_TRACE_ID=true
LLM_LOG_INCLUDE_SPAN_ID=true

# Alerting Thresholds
LLM_ALERT_LATENCY_WARNING_MS=5000
LLM_ALERT_LATENCY_CRITICAL_MS=15000
LLM_ALERT_ERROR_RATE_WARNING_PCT=5.0
LLM_ALERT_ERROR_RATE_CRITICAL_PCT=10.0
LLM_ALERT_DAILY_TOKEN_LIMIT=1000000
LLM_ALERT_HOURLY_TOKEN_LIMIT=100000
LLM_ALERT_DAILY_COST_LIMIT_USD=100.0
LLM_ALERT_HOURLY_COST_LIMIT_USD=20.0
"""
