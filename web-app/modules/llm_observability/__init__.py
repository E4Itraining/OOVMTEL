"""
LLM Observability Module for SYNAPSIX.

Provides comprehensive monitoring, tracing, and metrics for LLM operations
with OpenTelemetry integration and heterogeneous data normalization.

Features:
- Distributed tracing for LLM calls (spans with full context)
- Custom metrics (latency, tokens, costs, errors)
- Structured logging with correlation IDs
- Multi-provider data normalization
- Real-time dashboards via Grafana

Semantic Conventions:
Following OpenTelemetry GenAI semantic conventions for LLM observability.
https://opentelemetry.io/docs/specs/semconv/gen-ai/
"""

from .telemetry import (
    LLMTelemetry,
    get_llm_telemetry,
    init_llm_telemetry,
)
from .metrics import (
    LLMMetrics,
    get_llm_metrics,
)
from .normalizer import (
    LLMDataNormalizer,
    NormalizedLLMEvent,
    ProviderDataFormat,
)
from .config import (
    LLMObservabilityConfig,
    get_observability_config,
)
from .decorators import (
    trace_llm_call,
    measure_llm_latency,
)

__all__ = [
    # Telemetry
    "LLMTelemetry",
    "get_llm_telemetry",
    "init_llm_telemetry",
    # Metrics
    "LLMMetrics",
    "get_llm_metrics",
    # Normalizer
    "LLMDataNormalizer",
    "NormalizedLLMEvent",
    "ProviderDataFormat",
    # Config
    "LLMObservabilityConfig",
    "get_observability_config",
    # Decorators
    "trace_llm_call",
    "measure_llm_latency",
]

__version__ = "1.0.0"
