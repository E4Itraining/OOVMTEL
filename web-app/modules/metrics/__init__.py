"""
Prometheus Metrics Module for OOVMTEL Unified View
Self-monitoring and observability
"""

from .prometheus_metrics import (
    MetricsManager,
    get_metrics_manager,
    setup_instrumentator,
    REQUEST_COUNT,
    REQUEST_LATENCY,
    WEBSOCKET_CONNECTIONS,
    CACHE_HITS,
    CACHE_MISSES,
    NLP_QUERIES,
    RCA_ANALYSES,
    PREDICTIVE_ANALYSES,
)

__all__ = [
    "MetricsManager",
    "get_metrics_manager",
    "setup_instrumentator",
    "REQUEST_COUNT",
    "REQUEST_LATENCY",
    "WEBSOCKET_CONNECTIONS",
    "CACHE_HITS",
    "CACHE_MISSES",
    "NLP_QUERIES",
    "RCA_ANALYSES",
    "PREDICTIVE_ANALYSES",
]
