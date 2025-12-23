"""
Performance Tracker - AI/ML Model Performance Monitoring

This module provides:
- Real-time latency and throughput tracking
- Error rate and SLO monitoring
- Accuracy and quality metrics
- Resource utilization tracking
- Health score calculation
- Alerting on performance degradation
"""

import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Optional
import numpy as np

from .models import (
    ModelPerformanceMetrics,
    AIHealthScore,
    AIAlert,
    AIModel,
    ModelStatus,
    AIObservabilityConfig,
)

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Tracks and analyzes AI/ML model performance.

    Provides real-time metrics, health scoring, SLO tracking,
    and alerting capabilities.
    """

    def __init__(
        self,
        config: Optional[AIObservabilityConfig] = None,
    ):
        """Initialize the performance tracker"""
        self.config = config or AIObservabilityConfig()

        # Metrics storage (sliding window)
        self._metrics_window: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

        # Latency tracking (for percentile calculations)
        self._latencies: dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))

        # Error tracking
        self._errors: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

        # Request counts (per minute)
        self._request_counts: dict[str, dict] = defaultdict(lambda: {"total": 0, "last_minute": datetime.now()})

        # Health scores cache
        self._health_scores: dict[str, AIHealthScore] = {}

        # Alerts
        self._active_alerts: list[AIAlert] = []
        self._alert_history: list[AIAlert] = []
        self._alert_cooldowns: dict[str, datetime] = {}

        # Model baselines (from registry)
        self._model_baselines: dict[str, dict] = {}

        logger.info("PerformanceTracker initialized")

    def set_model_baseline(self, model: AIModel):
        """Set baseline metrics for a model"""
        self._model_baselines[model.model_id] = {
            "latency_p99_ms": model.slo_latency_p99_ms,
            "error_rate_pct": model.slo_error_rate_pct,
            "availability_pct": model.slo_availability_pct,
            "baseline_latency_ms": model.baseline_latency_ms,
            "baseline_throughput_rps": model.baseline_throughput_rps,
            "baseline_accuracy": model.baseline_accuracy,
        }

    def record_inference(
        self,
        model_id: str,
        latency_ms: float,
        success: bool = True,
        accuracy: Optional[float] = None,
        batch_size: int = 1,
        input_size_bytes: int = 0,
        output_size_bytes: int = 0,
    ):
        """
        Record a single inference/prediction.

        Args:
            model_id: Model ID
            latency_ms: Inference latency in milliseconds
            success: Whether the inference was successful
            accuracy: Optional accuracy metric for this prediction
            batch_size: Number of samples in batch
            input_size_bytes: Size of input data
            output_size_bytes: Size of output data
        """
        timestamp = datetime.now()

        # Record latency
        self._latencies[model_id].append({
            "timestamp": timestamp,
            "latency_ms": latency_ms,
            "batch_size": batch_size,
        })

        # Record request
        count_entry = self._request_counts[model_id]
        count_entry["total"] += 1

        # Reset counter every minute
        if (timestamp - count_entry["last_minute"]).seconds >= 60:
            count_entry["last_minute_count"] = count_entry.get("current_minute_count", 0)
            count_entry["current_minute_count"] = 1
            count_entry["last_minute"] = timestamp
        else:
            count_entry["current_minute_count"] = count_entry.get("current_minute_count", 0) + 1

        # Record error if failed
        if not success:
            self._errors[model_id].append({
                "timestamp": timestamp,
                "type": "inference_error",
            })

        # Check for SLO violations
        self._check_slo_violations(model_id, latency_ms, success)

    def record_error(
        self,
        model_id: str,
        error_type: str,
        error_message: str = "",
    ):
        """Record an error event"""
        self._errors[model_id].append({
            "timestamp": datetime.now(),
            "type": error_type,
            "message": error_message,
        })

    def get_metrics(
        self,
        model_id: str,
        window_minutes: int = 5,
    ) -> ModelPerformanceMetrics:
        """
        Get performance metrics for a model.

        Args:
            model_id: Model ID
            window_minutes: Time window for calculations

        Returns:
            ModelPerformanceMetrics with current stats
        """
        timestamp = datetime.now()
        cutoff = timestamp - timedelta(minutes=window_minutes)

        # Get latencies in window
        latencies = [
            entry["latency_ms"]
            for entry in self._latencies[model_id]
            if entry["timestamp"] >= cutoff
        ]

        # Get errors in window
        errors = [
            entry
            for entry in self._errors[model_id]
            if entry["timestamp"] >= cutoff
        ]

        # Calculate latency percentiles
        if latencies:
            latency_p50 = float(np.percentile(latencies, 50))
            latency_p95 = float(np.percentile(latencies, 95))
            latency_p99 = float(np.percentile(latencies, 99))
            latency_avg = float(np.mean(latencies))
            latency_max = float(np.max(latencies))
        else:
            latency_p50 = latency_p95 = latency_p99 = latency_avg = latency_max = 0.0

        # Calculate throughput
        requests_total = len(latencies)
        requests_per_second = requests_total / (window_minutes * 60) if window_minutes > 0 else 0

        # Calculate error rate
        errors_total = len(errors)
        error_rate_pct = (errors_total / requests_total * 100) if requests_total > 0 else 0.0

        return ModelPerformanceMetrics(
            model_id=model_id,
            timestamp=timestamp,
            latency_p50=latency_p50,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            latency_avg=latency_avg,
            latency_max=latency_max,
            requests_total=requests_total,
            requests_per_second=requests_per_second,
            errors_total=errors_total,
            error_rate_pct=error_rate_pct,
        )

    def calculate_health_score(
        self,
        model_id: str,
        model: Optional[AIModel] = None,
    ) -> AIHealthScore:
        """
        Calculate composite health score for a model.

        Args:
            model_id: Model ID
            model: Optional AIModel for baseline comparison

        Returns:
            AIHealthScore with component breakdowns
        """
        timestamp = datetime.now()
        metrics = self.get_metrics(model_id)

        # Get baselines
        baselines = self._model_baselines.get(model_id, {})
        baseline_latency = baselines.get("baseline_latency_ms", 100.0)
        slo_latency_p99 = baselines.get("latency_p99_ms", 500.0)
        slo_error_rate = baselines.get("error_rate_pct", 1.0)

        # Calculate component scores (0-100)

        # Performance score (based on latency)
        if metrics.latency_p99 > 0 and slo_latency_p99 > 0:
            latency_ratio = metrics.latency_p99 / slo_latency_p99
            performance_score = max(0, min(100, 100 * (1 - (latency_ratio - 1)) if latency_ratio > 1 else 100))
        else:
            performance_score = 100.0

        # Error rate score
        if slo_error_rate > 0:
            error_ratio = metrics.error_rate_pct / slo_error_rate
            accuracy_score = max(0, min(100, 100 * (1 - error_ratio) if error_ratio <= 1 else 100 / (1 + error_ratio)))
        else:
            accuracy_score = 100.0 if metrics.error_rate_pct == 0 else 50.0

        # Drift score (placeholder - integrated from drift detector)
        drift_score = 100.0  # Default healthy

        # Availability score (based on request volume)
        # If we're getting requests, we're available
        availability_score = 100.0 if metrics.requests_total > 0 else 80.0

        # Resource score (placeholder - would integrate with system metrics)
        resource_score = 95.0

        # Compliance score (placeholder - would check AI Act requirements)
        compliance_score = 100.0

        # Calculate overall score (weighted average)
        weights = {
            "performance": 0.25,
            "accuracy": 0.25,
            "drift": 0.20,
            "availability": 0.15,
            "resource": 0.10,
            "compliance": 0.05,
        }

        overall_score = (
            weights["performance"] * performance_score +
            weights["accuracy"] * accuracy_score +
            weights["drift"] * drift_score +
            weights["availability"] * availability_score +
            weights["resource"] * resource_score +
            weights["compliance"] * compliance_score
        )

        # Determine status
        if overall_score >= 90:
            status = "healthy"
        elif overall_score >= 70:
            status = "warning"
        else:
            status = "critical"

        # Detect SLO violations
        slo_violations = []
        if metrics.latency_p99 > slo_latency_p99:
            slo_violations.append(f"Latency P99 ({metrics.latency_p99:.1f}ms) exceeds SLO ({slo_latency_p99}ms)")
        if metrics.error_rate_pct > slo_error_rate:
            slo_violations.append(f"Error rate ({metrics.error_rate_pct:.2f}%) exceeds SLO ({slo_error_rate}%)")

        slo_compliance_pct = ((2 - len(slo_violations)) / 2) * 100

        # Build recommendations
        recommendations = []
        if performance_score < 80:
            recommendations.append("Consider optimizing model inference or scaling resources")
        if accuracy_score < 80:
            recommendations.append("Investigate error patterns and model accuracy")
        if drift_score < 80:
            recommendations.append("Review data distribution and consider retraining")

        # Determine trend (compare with previous score)
        previous_score = self._health_scores.get(model_id)
        if previous_score:
            score_diff = overall_score - previous_score.overall_score
            if score_diff > 2:
                score_trend = "improving"
            elif score_diff < -2:
                score_trend = "degrading"
            else:
                score_trend = "stable"
            score_change_24h = score_diff
        else:
            score_trend = "stable"
            score_change_24h = 0.0

        health_score = AIHealthScore(
            model_id=model_id,
            timestamp=timestamp,
            overall_score=overall_score,
            status=status,
            performance_score=performance_score,
            accuracy_score=accuracy_score,
            drift_score=drift_score,
            availability_score=availability_score,
            resource_score=resource_score,
            compliance_score=compliance_score,
            slo_violations=slo_violations,
            slo_compliance_pct=slo_compliance_pct,
            recommendations=recommendations,
            score_trend=score_trend,
            score_change_24h=score_change_24h,
        )

        # Cache the score
        self._health_scores[model_id] = health_score

        return health_score

    def get_all_health_scores(
        self,
        models: list[AIModel],
    ) -> dict[str, AIHealthScore]:
        """Get health scores for all models"""
        scores = {}
        for model in models:
            self.set_model_baseline(model)
            scores[model.model_id] = self.calculate_health_score(model.model_id, model)
        return scores

    def _check_slo_violations(
        self,
        model_id: str,
        latency_ms: float,
        success: bool,
    ):
        """Check for SLO violations and generate alerts"""
        baselines = self._model_baselines.get(model_id, {})
        slo_latency = baselines.get("latency_p99_ms", 500.0)

        # Check latency SLO
        if latency_ms > slo_latency * 2:  # 2x SLO is alert-worthy
            self._create_alert(
                model_id=model_id,
                category="performance",
                severity="warning" if latency_ms < slo_latency * 3 else "critical",
                title=f"High latency detected for {model_id}",
                description=f"Latency {latency_ms:.1f}ms exceeds SLO threshold {slo_latency}ms",
                metric_name="latency_ms",
                metric_value=latency_ms,
                threshold_value=slo_latency,
            )

        # Check error
        if not success:
            self._create_alert(
                model_id=model_id,
                category="error",
                severity="warning",
                title=f"Inference error for {model_id}",
                description="Model inference failed",
                metric_name="error",
                metric_value=1,
                threshold_value=0,
            )

    def _create_alert(
        self,
        model_id: str,
        category: str,
        severity: str,
        title: str,
        description: str,
        metric_name: str,
        metric_value: float,
        threshold_value: float,
    ):
        """Create an alert if not in cooldown"""
        alert_key = f"{model_id}_{category}_{metric_name}"
        now = datetime.now()

        # Check cooldown
        if alert_key in self._alert_cooldowns:
            cooldown_until = self._alert_cooldowns[alert_key]
            if now < cooldown_until:
                return  # Still in cooldown

        # Create alert
        alert = AIAlert(
            alert_id=f"alert-{now.timestamp():.0f}-{model_id[:8]}",
            model_id=model_id,
            timestamp=now,
            severity=severity,
            category=category,
            title=title,
            description=description,
            metric_name=metric_name,
            metric_value=metric_value,
            threshold_value=threshold_value,
            state="firing",
            suggested_actions=self._get_suggested_actions(category, severity),
        )

        self._active_alerts.append(alert)
        self._alert_history.append(alert)

        # Set cooldown
        cooldown_minutes = self.config.alert_cooldown_min
        self._alert_cooldowns[alert_key] = now + timedelta(minutes=cooldown_minutes)

        logger.warning(f"Alert created: {title}")

    def _get_suggested_actions(self, category: str, severity: str) -> list[str]:
        """Get suggested remediation actions"""
        actions = {
            "performance": [
                "Check model resource allocation",
                "Review recent input data patterns",
                "Consider model optimization or scaling",
            ],
            "error": [
                "Check model logs for error details",
                "Validate input data format",
                "Review model health and dependencies",
            ],
            "drift": [
                "Analyze data distribution changes",
                "Compare with baseline metrics",
                "Consider model retraining",
            ],
            "slo": [
                "Review SLO thresholds",
                "Investigate root cause of violation",
                "Consider scaling or optimization",
            ],
        }
        return actions.get(category, ["Investigate the issue"])

    def get_active_alerts(
        self,
        model_id: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> list[AIAlert]:
        """Get active (firing) alerts"""
        alerts = [a for a in self._active_alerts if a.state == "firing"]

        if model_id:
            alerts = [a for a in alerts if a.model_id == model_id]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        for alert in self._active_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self._active_alerts:
            if alert.alert_id == alert_id:
                alert.state = "resolved"
                alert.resolved_at = datetime.now()
                return True
        return False

    def get_performance_summary(self) -> dict:
        """Get overall performance summary"""
        all_health_scores = list(self._health_scores.values())

        if not all_health_scores:
            return {
                "models_tracked": 0,
                "avg_health_score": 0,
                "healthy_count": 0,
                "warning_count": 0,
                "critical_count": 0,
                "active_alerts": 0,
            }

        return {
            "models_tracked": len(all_health_scores),
            "avg_health_score": round(np.mean([s.overall_score for s in all_health_scores]), 1),
            "healthy_count": len([s for s in all_health_scores if s.status == "healthy"]),
            "warning_count": len([s for s in all_health_scores if s.status == "warning"]),
            "critical_count": len([s for s in all_health_scores if s.status == "critical"]),
            "active_alerts": len([a for a in self._active_alerts if a.state == "firing"]),
            "total_requests_tracked": sum(
                self._request_counts[mid]["total"]
                for mid in self._request_counts
            ),
            "slo_violations": sum(len(s.slo_violations) for s in all_health_scores),
        }

    def simulate_model_activity(self, models: list[AIModel]):
        """Simulate model activity for demo purposes"""
        import random

        for model in models:
            self.set_model_baseline(model)

            # Simulate some inferences
            for _ in range(random.randint(50, 200)):
                # Generate realistic latencies
                base_latency = model.baseline_latency_ms
                latency = base_latency * random.uniform(0.5, 2.0)

                # Occasional spikes
                if random.random() < 0.05:
                    latency *= random.uniform(2, 5)

                # Occasional errors
                success = random.random() > 0.02

                self.record_inference(
                    model_id=model.model_id,
                    latency_ms=latency,
                    success=success,
                    batch_size=random.choice([1, 4, 8, 16]),
                )
