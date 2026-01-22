"""
Tests for LLM Metrics module.

Tests metrics collection, aggregation, and alerting.
"""

import pytest
from datetime import datetime, timedelta
from threading import Thread
import time

from modules.llm_observability.metrics import (
    LLMMetrics,
    AggregatedMetrics,
    get_llm_metrics,
    reset_metrics,
)
from modules.llm_observability.normalizer import (
    NormalizedLLMEvent,
    NormalizedTokenUsage,
    NormalizedError,
    ProviderDataFormat,
    CompletionStatus,
    ErrorCategory,
)


@pytest.fixture(autouse=True)
def reset_metrics_singleton():
    """Reset metrics singleton before each test."""
    reset_metrics()
    yield
    reset_metrics()


class TestAggregatedMetrics:
    """Tests for AggregatedMetrics dataclass."""

    def test_success_rate_all_success(self):
        agg = AggregatedMetrics(
            window_start=datetime.utcnow() - timedelta(minutes=5),
            window_end=datetime.utcnow(),
            total_requests=100,
            successful_requests=100,
            failed_requests=0
        )
        assert agg.success_rate == 100.0

    def test_success_rate_partial(self):
        agg = AggregatedMetrics(
            window_start=datetime.utcnow() - timedelta(minutes=5),
            window_end=datetime.utcnow(),
            total_requests=100,
            successful_requests=80,
            failed_requests=20
        )
        assert agg.success_rate == 80.0
        assert agg.error_rate == 20.0

    def test_success_rate_no_requests(self):
        agg = AggregatedMetrics(
            window_start=datetime.utcnow() - timedelta(minutes=5),
            window_end=datetime.utcnow(),
            total_requests=0,
            successful_requests=0,
            failed_requests=0
        )
        assert agg.success_rate == 100.0
        assert agg.error_rate == 0.0

    def test_avg_latency(self):
        agg = AggregatedMetrics(
            window_start=datetime.utcnow() - timedelta(minutes=5),
            window_end=datetime.utcnow(),
            latency_sum=1000,
            latency_count=10
        )
        assert agg.avg_latency_ms == 100.0

    def test_avg_latency_no_requests(self):
        agg = AggregatedMetrics(
            window_start=datetime.utcnow() - timedelta(minutes=5),
            window_end=datetime.utcnow(),
            latency_sum=0,
            latency_count=0
        )
        assert agg.avg_latency_ms == 0.0

    def test_percentiles(self):
        agg = AggregatedMetrics(
            window_start=datetime.utcnow() - timedelta(minutes=5),
            window_end=datetime.utcnow(),
            latency_values=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        )
        assert agg.p50_latency_ms == 50  # Median
        assert agg.p95_latency_ms == 100
        assert agg.p99_latency_ms == 100

    def test_percentiles_empty(self):
        agg = AggregatedMetrics(
            window_start=datetime.utcnow() - timedelta(minutes=5),
            window_end=datetime.utcnow(),
            latency_values=[]
        )
        assert agg.p50_latency_ms == 0.0
        assert agg.p95_latency_ms == 0.0

    def test_requests_per_minute(self):
        start = datetime.utcnow() - timedelta(minutes=5)
        end = datetime.utcnow()
        agg = AggregatedMetrics(
            window_start=start,
            window_end=end,
            total_requests=50
        )
        # 50 requests in 5 minutes = 10 requests/minute
        assert agg.requests_per_minute == 10.0

    def test_to_dict(self):
        agg = AggregatedMetrics(
            window_start=datetime.utcnow() - timedelta(minutes=5),
            window_end=datetime.utcnow(),
            total_requests=10,
            successful_requests=8,
            failed_requests=2,
            total_tokens=1000,
            total_cost_usd=0.05
        )
        result = agg.to_dict()

        assert "requests" in result
        assert "tokens" in result
        assert "cost" in result
        assert "latency_ms" in result
        assert result["requests"]["total"] == 10
        assert result["requests"]["success_rate_pct"] == 80.0


class TestLLMMetrics:
    """Tests for LLMMetrics class."""

    def create_test_event(
        self,
        provider: ProviderDataFormat = ProviderDataFormat.MISTRAL,
        status: CompletionStatus = CompletionStatus.SUCCESS,
        latency_ms: float = 100.0,
        prompt_tokens: int = 10,
        completion_tokens: int = 20,
        timestamp: datetime = None
    ) -> NormalizedLLMEvent:
        """Create a test event."""
        return NormalizedLLMEvent(
            event_id=f"test-{datetime.utcnow().timestamp()}",
            timestamp=timestamp or datetime.utcnow(),
            provider=provider,
            model="test-model",
            status=status,
            latency_ms=latency_ms,
            token_usage=NormalizedTokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                estimated_cost_usd=0.001
            )
        )

    def test_record_event(self):
        metrics = LLMMetrics()
        event = self.create_test_event()

        metrics.record_event(event)

        assert metrics.get_status()["events_stored"] == 1

    def test_record_multiple_events(self):
        metrics = LLMMetrics()

        for _ in range(10):
            event = self.create_test_event()
            metrics.record_event(event)

        assert metrics.get_status()["events_stored"] == 10

    def test_get_aggregated_metrics(self):
        metrics = LLMMetrics()

        # Add success events
        for _ in range(8):
            event = self.create_test_event(
                status=CompletionStatus.SUCCESS,
                latency_ms=100.0
            )
            metrics.record_event(event)

        # Add failure events
        for _ in range(2):
            event = self.create_test_event(
                status=CompletionStatus.ERROR,
                latency_ms=50.0
            )
            event.error = NormalizedError(
                category=ErrorCategory.RATE_LIMIT,
                code="rate_limit",
                message="Rate limited"
            )
            metrics.record_event(event)

        agg = metrics.get_aggregated_metrics(window_minutes=60)

        assert agg.total_requests == 10
        assert agg.successful_requests == 8
        assert agg.failed_requests == 2
        assert agg.success_rate == 80.0

    def test_get_aggregated_metrics_by_provider(self):
        metrics = LLMMetrics()

        # Add Mistral events
        for _ in range(5):
            event = self.create_test_event(provider=ProviderDataFormat.MISTRAL)
            metrics.record_event(event)

        # Add Claude events
        for _ in range(3):
            event = self.create_test_event(provider=ProviderDataFormat.CLAUDE)
            metrics.record_event(event)

        # Get only Mistral metrics
        agg = metrics.get_aggregated_metrics(
            window_minutes=60,
            provider="mistral"
        )

        assert agg.total_requests == 5

    def test_increment_decrement_active_requests(self):
        metrics = LLMMetrics()

        assert metrics._active_requests == 0

        metrics.increment_active_requests()
        assert metrics._active_requests == 1

        metrics.increment_active_requests()
        assert metrics._active_requests == 2

        metrics.decrement_active_requests()
        assert metrics._active_requests == 1

        metrics.decrement_active_requests()
        assert metrics._active_requests == 0

    def test_decrement_never_goes_negative(self):
        metrics = LLMMetrics()

        metrics.decrement_active_requests()
        metrics.decrement_active_requests()

        assert metrics._active_requests == 0

    def test_active_requests_thread_safety(self):
        """Test that active_requests counter is thread-safe."""
        metrics = LLMMetrics()
        num_threads = 10
        iterations = 100

        def increment_decrement():
            for _ in range(iterations):
                metrics.increment_active_requests()
                time.sleep(0.001)  # Small delay to increase chance of race conditions
                metrics.decrement_active_requests()

        threads = [Thread(target=increment_decrement) for _ in range(num_threads)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # After all increments and decrements, should be back to 0
        assert metrics._active_requests == 0

    def test_get_current_hour_usage(self):
        metrics = LLMMetrics()

        for _ in range(5):
            event = self.create_test_event(
                prompt_tokens=100,
                completion_tokens=50
            )
            metrics.record_event(event)

        usage = metrics.get_current_hour_usage()

        assert usage["tokens"] == 750  # 5 events * 150 tokens each
        assert "cost_usd" in usage
        assert "token_limit" in usage
        assert "cost_limit_usd" in usage

    def test_check_alerts_no_alerts(self):
        metrics = LLMMetrics()

        # Add some normal events
        for _ in range(10):
            event = self.create_test_event(
                status=CompletionStatus.SUCCESS,
                latency_ms=100.0  # Well below warning threshold
            )
            metrics.record_event(event)

        alerts = metrics.check_alerts()

        # Should have no alerts with normal latency and 100% success rate
        latency_alerts = [a for a in alerts if "latency" in a["type"]]
        error_alerts = [a for a in alerts if "error_rate" in a["type"]]

        assert len(latency_alerts) == 0
        assert len(error_alerts) == 0

    def test_check_alerts_high_latency(self):
        metrics = LLMMetrics()

        # Add events with high latency
        for _ in range(10):
            event = self.create_test_event(
                status=CompletionStatus.SUCCESS,
                latency_ms=20000.0  # Above critical threshold (15000ms)
            )
            metrics.record_event(event)

        alerts = metrics.check_alerts()

        latency_alerts = [a for a in alerts if "latency" in a["type"]]
        assert len(latency_alerts) > 0
        assert any(a["severity"] == "critical" for a in latency_alerts)

    def test_check_alerts_high_error_rate(self):
        metrics = LLMMetrics()

        # Add mostly failed events
        for _ in range(2):
            event = self.create_test_event(status=CompletionStatus.SUCCESS)
            metrics.record_event(event)

        for _ in range(8):
            event = self.create_test_event(status=CompletionStatus.ERROR)
            event.error = NormalizedError(
                category=ErrorCategory.INTERNAL,
                code="internal",
                message="Internal error"
            )
            metrics.record_event(event)

        alerts = metrics.check_alerts()

        error_alerts = [a for a in alerts if "error_rate" in a["type"]]
        assert len(error_alerts) > 0

    def test_get_status(self):
        metrics = LLMMetrics()

        status = metrics.get_status()

        assert "enabled" in status
        assert "otel_available" in status
        assert "initialized" in status
        assert "events_stored" in status
        assert "max_events" in status
        assert "active_requests" in status


class TestMetricsSingleton:
    """Tests for metrics singleton pattern."""

    def test_get_llm_metrics_singleton(self):
        metrics1 = get_llm_metrics()
        metrics2 = get_llm_metrics()

        assert metrics1 is metrics2

    def test_reset_metrics(self):
        metrics1 = get_llm_metrics()
        reset_metrics()
        metrics2 = get_llm_metrics()

        assert metrics1 is not metrics2
