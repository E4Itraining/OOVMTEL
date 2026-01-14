"""
Prometheus Metrics for OOVMTEL Self-Monitoring
"""

import logging
import time
from typing import Optional, Callable
from functools import wraps

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse

logger = logging.getLogger(__name__)

# =============================================
# Prometheus Metrics Definitions
# =============================================

# Application Info
APP_INFO = Info(
    "oovmtel_unified_view",
    "OOVMTEL Unified View Application Information"
)

# Request Metrics
REQUEST_COUNT = Counter(
    "oovmtel_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "oovmtel_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0]
)

# WebSocket Metrics
WEBSOCKET_CONNECTIONS = Gauge(
    "oovmtel_websocket_connections",
    "Current number of WebSocket connections"
)

WEBSOCKET_MESSAGES = Counter(
    "oovmtel_websocket_messages_total",
    "Total WebSocket messages sent",
    ["direction"]  # "sent" or "received"
)

# Cache Metrics
CACHE_HITS = Counter(
    "oovmtel_cache_hits_total",
    "Total cache hits",
    ["cache_type"]
)

CACHE_MISSES = Counter(
    "oovmtel_cache_misses_total",
    "Total cache misses",
    ["cache_type"]
)

CACHE_SIZE = Gauge(
    "oovmtel_cache_size",
    "Current cache size",
    ["cache_type"]
)

# Game-Changer Module Metrics
NLP_QUERIES = Counter(
    "oovmtel_nlp_queries_total",
    "Total NLP queries processed",
    ["language", "intent", "success"]
)

NLP_LATENCY = Histogram(
    "oovmtel_nlp_latency_seconds",
    "NLP query processing latency",
    ["language"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

RCA_ANALYSES = Counter(
    "oovmtel_rca_analyses_total",
    "Total RCA analyses performed",
    ["severity", "success"]
)

PREDICTIVE_ANALYSES = Counter(
    "oovmtel_predictive_analyses_total",
    "Total predictive analyses performed",
    ["equipment_type", "success"]
)

REMEDIATION_ACTIONS = Counter(
    "oovmtel_remediation_actions_total",
    "Total remediation actions",
    ["runbook", "status"]
)

# External Service Metrics
EXTERNAL_SERVICE_REQUESTS = Counter(
    "oovmtel_external_service_requests_total",
    "Requests to external services",
    ["service", "status"]
)

EXTERNAL_SERVICE_LATENCY = Histogram(
    "oovmtel_external_service_latency_seconds",
    "External service request latency",
    ["service"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Data Ingestion Metrics
DATA_POINTS_PROCESSED = Counter(
    "oovmtel_data_points_processed_total",
    "Total data points processed",
    ["source", "type"]
)

# Error Metrics
ERRORS = Counter(
    "oovmtel_errors_total",
    "Total errors",
    ["type", "module"]
)


class MetricsManager:
    """Manager for Prometheus metrics collection."""

    def __init__(self):
        self._initialized = False

    def initialize(self, app_version: str = "1.0.0"):
        """Initialize metrics with app info."""
        if self._initialized:
            return

        APP_INFO.info({
            "version": app_version,
            "service": "unified-view",
            "platform": "oovmtel"
        })
        self._initialized = True
        logger.info("Prometheus metrics initialized")

    # Request tracking
    def track_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float
    ):
        """Track an HTTP request."""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    # WebSocket tracking
    def ws_connected(self):
        """Track WebSocket connection opened."""
        WEBSOCKET_CONNECTIONS.inc()

    def ws_disconnected(self):
        """Track WebSocket connection closed."""
        WEBSOCKET_CONNECTIONS.dec()

    def ws_message(self, direction: str = "sent"):
        """Track WebSocket message."""
        WEBSOCKET_MESSAGES.labels(direction=direction).inc()

    # Cache tracking
    def cache_hit(self, cache_type: str = "memory"):
        """Track cache hit."""
        CACHE_HITS.labels(cache_type=cache_type).inc()

    def cache_miss(self, cache_type: str = "memory"):
        """Track cache miss."""
        CACHE_MISSES.labels(cache_type=cache_type).inc()

    def set_cache_size(self, size: int, cache_type: str = "memory"):
        """Set current cache size."""
        CACHE_SIZE.labels(cache_type=cache_type).set(size)

    # Module tracking
    def track_nlp_query(
        self,
        language: str,
        intent: str,
        success: bool,
        duration: float
    ):
        """Track NLP query."""
        NLP_QUERIES.labels(
            language=language,
            intent=intent,
            success=str(success).lower()
        ).inc()
        NLP_LATENCY.labels(language=language).observe(duration)

    def track_rca_analysis(self, severity: str, success: bool):
        """Track RCA analysis."""
        RCA_ANALYSES.labels(
            severity=severity,
            success=str(success).lower()
        ).inc()

    def track_predictive_analysis(self, equipment_type: str, success: bool):
        """Track predictive analysis."""
        PREDICTIVE_ANALYSES.labels(
            equipment_type=equipment_type,
            success=str(success).lower()
        ).inc()

    def track_remediation(self, runbook: str, status: str):
        """Track remediation action."""
        REMEDIATION_ACTIONS.labels(runbook=runbook, status=status).inc()

    # External service tracking
    def track_external_request(
        self,
        service: str,
        status: str,
        duration: float
    ):
        """Track external service request."""
        EXTERNAL_SERVICE_REQUESTS.labels(
            service=service,
            status=status
        ).inc()
        EXTERNAL_SERVICE_LATENCY.labels(service=service).observe(duration)

    # Data tracking
    def track_data_points(self, source: str, data_type: str, count: int = 1):
        """Track data points processed."""
        DATA_POINTS_PROCESSED.labels(source=source, type=data_type).inc(count)

    # Error tracking
    def track_error(self, error_type: str, module: str):
        """Track an error."""
        ERRORS.labels(type=error_type, module=module).inc()


# Global metrics manager
_metrics_manager: Optional[MetricsManager] = None


def get_metrics_manager() -> MetricsManager:
    """Get or create metrics manager instance."""
    global _metrics_manager
    if _metrics_manager is None:
        _metrics_manager = MetricsManager()
    return _metrics_manager


def setup_instrumentator(app: FastAPI):
    """
    Setup automatic instrumentation for FastAPI.
    Adds middleware for request tracking and /metrics endpoint.
    """
    metrics = get_metrics_manager()
    metrics.initialize()

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        """Middleware to track request metrics."""
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        endpoint = request.url.path

        # Skip metrics endpoint itself to avoid recursion
        if endpoint != "/metrics":
            metrics.track_request(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration
            )

        return response

    @app.get("/metrics", include_in_schema=False)
    async def metrics_endpoint():
        """Prometheus metrics endpoint."""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )

    logger.info("Prometheus instrumentator setup complete")


def timed_metric(metric_callback: Callable):
    """Decorator to time function execution and report to metrics."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                metric_callback(duration=duration, success=True)
                return result
            except Exception as e:
                duration = time.time() - start
                metric_callback(duration=duration, success=False)
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                metric_callback(duration=duration, success=True)
                return result
            except Exception as e:
                duration = time.time() - start
                metric_callback(duration=duration, success=False)
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


# Import asyncio for the decorator
import asyncio
