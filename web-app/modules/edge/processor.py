"""
Edge Processor - Local data processing at the edge
"""

import math
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from .models import DataPoint, EdgeAlert, ModelDeployment

logger = logging.getLogger(__name__)


class EdgeProcessor:
    """
    Processes data locally at the edge.

    Features:
    - Anomaly detection
    - Data filtering
    - Local alerting
    - Model inference
    """

    def __init__(
        self,
        anomaly_threshold: float = 2.5,
        local_alerting: bool = True
    ):
        self.anomaly_threshold = anomaly_threshold
        self.local_alerting = local_alerting

        # Running statistics for anomaly detection
        self.metric_stats: Dict[str, Dict[str, float]] = {}

    def detect_anomalies(self, data_points: List[DataPoint]) -> List[EdgeAlert]:
        """Detect anomalies in data points."""
        alerts = []

        for dp in data_points:
            key = f"{dp.metric}:{dp.equipment or 'none'}"

            # Initialize stats for new metrics
            if key not in self.metric_stats:
                self.metric_stats[key] = {
                    "count": 0,
                    "sum": 0,
                    "sum_sq": 0,
                    "min": float('inf'),
                    "max": float('-inf')
                }

            stats = self.metric_stats[key]

            # Update running statistics
            stats["count"] += 1
            stats["sum"] += dp.value
            stats["sum_sq"] += dp.value ** 2
            stats["min"] = min(stats["min"], dp.value)
            stats["max"] = max(stats["max"], dp.value)

            # Need at least 10 data points for meaningful detection
            if stats["count"] < 10:
                continue

            # Calculate mean and standard deviation
            mean = stats["sum"] / stats["count"]
            variance = (stats["sum_sq"] / stats["count"]) - (mean ** 2)
            std = math.sqrt(max(0, variance))

            if std == 0:
                continue

            # Calculate Z-score
            z_score = (dp.value - mean) / std

            # Check for anomaly
            if abs(z_score) > self.anomaly_threshold:
                severity = self._determine_severity(z_score)

                alert = EdgeAlert(
                    id=f"EDGE-{uuid.uuid4().hex[:8].upper()}",
                    timestamp=dp.timestamp,
                    severity=severity,
                    metric=dp.metric,
                    equipment=dp.equipment,
                    message=f"Anomaly detected: {dp.metric} = {dp.value:.2f} (z-score: {z_score:.2f})",
                    value=dp.value,
                    threshold=mean + (self.anomaly_threshold * std)
                )
                alerts.append(alert)

                if self.local_alerting:
                    logger.warning(f"Edge alert: {alert.message}")

        return alerts

    def _determine_severity(self, z_score: float) -> str:
        """Determine alert severity based on z-score."""
        abs_z = abs(z_score)
        if abs_z > 4:
            return "critical"
        elif abs_z > 3:
            return "warning"
        else:
            return "info"

    def filter_data(
        self,
        data_points: List[DataPoint],
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        metrics: Optional[List[str]] = None,
        equipment: Optional[List[str]] = None
    ) -> List[DataPoint]:
        """Filter data points based on criteria."""
        filtered = data_points

        if min_value is not None:
            filtered = [dp for dp in filtered if dp.value >= min_value]

        if max_value is not None:
            filtered = [dp for dp in filtered if dp.value <= max_value]

        if metrics:
            filtered = [dp for dp in filtered if dp.metric in metrics]

        if equipment:
            filtered = [dp for dp in filtered if dp.equipment in equipment]

        return filtered

    def run_model_inference(
        self,
        model: ModelDeployment,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run inference on a deployed model."""
        # Simulated model inference
        # In production, would load and run actual ML model

        if model.type == "anomaly_detection":
            # Simple threshold-based anomaly score
            values = list(input_data.values())
            if values:
                score = sum(abs(v) for v in values if isinstance(v, (int, float))) / len(values)
                is_anomaly = score > 50  # Simplified
                return {
                    "anomaly_score": score,
                    "is_anomaly": is_anomaly,
                    "model_id": model.id
                }

        elif model.type == "forecasting":
            # Simple linear extrapolation
            return {
                "forecast": [input_data.get("current", 0) * 1.01] * 10,
                "confidence": 0.8,
                "model_id": model.id
            }

        elif model.type == "classification":
            # Simulated classification
            return {
                "class": "normal",
                "confidence": 0.85,
                "probabilities": {"normal": 0.85, "warning": 0.10, "critical": 0.05},
                "model_id": model.id
            }

        return {"error": "Unknown model type", "model_id": model.id}

    def reset_stats(self, metric: Optional[str] = None):
        """Reset running statistics."""
        if metric:
            keys_to_remove = [k for k in self.metric_stats if k.startswith(metric)]
            for key in keys_to_remove:
                del self.metric_stats[key]
        else:
            self.metric_stats.clear()

    def get_stats(self, metric: Optional[str] = None) -> Dict[str, Any]:
        """Get current statistics."""
        if metric:
            return {
                k: v for k, v in self.metric_stats.items()
                if k.startswith(metric)
            }
        return self.metric_stats.copy()
