"""
Adaptive Threshold Manager - Dynamic threshold calculation
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from .models import (
    ThresholdConfig,
    ThresholdType,
    AlertSeverity,
)

logger = logging.getLogger(__name__)


class AdaptiveThresholdManager:
    """
    Adaptive threshold management for intelligent alerting.

    Features:
    - Statistical baseline calculation
    - Seasonal adjustments
    - Equipment state awareness
    - Gradual threshold adaptation
    - Anomaly-resistant updates
    """

    def __init__(
        self,
        default_sensitivity: float = 2.5,
        min_samples: int = 100,
        baseline_window_hours: int = 168,
        update_interval_minutes: int = 60,
    ):
        self.default_sensitivity = default_sensitivity
        self.min_samples = min_samples
        self.baseline_window_hours = baseline_window_hours
        self.update_interval_minutes = update_interval_minutes

        # Baseline storage
        self._baselines: Dict[str, Dict[str, Any]] = {}
        # Key format: "{metric}:{equipment}"

        # Seasonal patterns
        self._seasonal_patterns: Dict[str, Dict[int, Dict[str, float]]] = {}
        # Key format: "{metric}:{equipment}", value: {hour_of_day: {mean, std}}

        # Recent values for streaming updates
        self._recent_values: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)

        logger.info("Adaptive Threshold Manager initialized")

    def get_threshold(
        self,
        metric: str,
        equipment: Optional[str],
        config: ThresholdConfig,
        current_time: Optional[datetime] = None,
    ) -> Dict[str, float]:
        """
        Get current threshold values for a metric.

        Args:
            metric: Metric name
            equipment: Equipment identifier
            config: Threshold configuration
            current_time: Current timestamp (for seasonal)

        Returns:
            Dict with warning and critical thresholds
        """
        current_time = current_time or datetime.utcnow()
        key = self._make_key(metric, equipment)

        # Start with static thresholds
        thresholds = {
            "warning": config.warning_value,
            "critical": config.critical_value,
        }

        if config.threshold_type == ThresholdType.STATIC:
            return thresholds

        elif config.threshold_type == ThresholdType.ADAPTIVE:
            return self._get_adaptive_threshold(key, config, thresholds)

        elif config.threshold_type == ThresholdType.SEASONAL:
            return self._get_seasonal_threshold(key, config, current_time, thresholds)

        elif config.threshold_type == ThresholdType.BASELINE:
            return self._get_baseline_threshold(key, config, thresholds)

        return thresholds

    def _get_adaptive_threshold(
        self,
        key: str,
        config: ThresholdConfig,
        fallback: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate adaptive threshold based on statistics."""
        baseline = self._baselines.get(key)

        if not baseline or baseline.get("sample_count", 0) < self.min_samples:
            return fallback

        mean = baseline["mean"]
        std = baseline["std"]
        sensitivity = config.sensitivity or self.default_sensitivity

        # Warning: mean + sensitivity * std
        # Critical: mean + (sensitivity + 1) * std
        warning = mean + sensitivity * std
        critical = mean + (sensitivity + 1) * std

        # Apply comparison direction
        if config.comparison == "less_than":
            warning = mean - sensitivity * std
            critical = mean - (sensitivity + 1) * std

        # Override with static limits if they're more restrictive
        if fallback["warning"] is not None:
            if config.comparison == "greater_than":
                warning = min(warning, fallback["warning"])
            else:
                warning = max(warning, fallback["warning"])

        if fallback["critical"] is not None:
            if config.comparison == "greater_than":
                critical = min(critical, fallback["critical"])
            else:
                critical = max(critical, fallback["critical"])

        return {"warning": warning, "critical": critical}

    def _get_seasonal_threshold(
        self,
        key: str,
        config: ThresholdConfig,
        current_time: datetime,
        fallback: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate seasonal-adjusted threshold."""
        patterns = self._seasonal_patterns.get(key)

        if not patterns:
            return self._get_adaptive_threshold(key, config, fallback)

        hour = current_time.hour
        if hour not in patterns:
            return self._get_adaptive_threshold(key, config, fallback)

        seasonal = patterns[hour]
        mean = seasonal["mean"]
        std = seasonal.get("std", 1.0)
        sensitivity = config.sensitivity or self.default_sensitivity

        warning = mean + sensitivity * std
        critical = mean + (sensitivity + 1) * std

        if config.comparison == "less_than":
            warning = mean - sensitivity * std
            critical = mean - (sensitivity + 1) * std

        return {"warning": warning, "critical": critical}

    def _get_baseline_threshold(
        self,
        key: str,
        config: ThresholdConfig,
        fallback: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate baseline deviation threshold."""
        baseline = self._baselines.get(key)

        if not baseline:
            return fallback

        mean = baseline["mean"]
        sensitivity = config.sensitivity or self.default_sensitivity

        # Percentage deviation from baseline
        warning_deviation = mean * (sensitivity * 0.1)  # 10% per sensitivity unit
        critical_deviation = mean * ((sensitivity + 1) * 0.1)

        if config.comparison == "greater_than":
            warning = mean + warning_deviation
            critical = mean + critical_deviation
        else:
            warning = mean - warning_deviation
            critical = mean - critical_deviation

        return {"warning": warning, "critical": critical}

    def update_baseline(
        self,
        metric: str,
        equipment: Optional[str],
        value: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Update baseline with a new value.

        Uses Welford's online algorithm for streaming statistics.
        """
        timestamp = timestamp or datetime.utcnow()
        key = self._make_key(metric, equipment)

        # Add to recent values
        self._recent_values[key].append((timestamp, value))

        # Trim old values
        cutoff = timestamp - timedelta(hours=self.baseline_window_hours)
        self._recent_values[key] = [
            (t, v) for t, v in self._recent_values[key]
            if t > cutoff
        ]

        # Update baseline statistics
        if key not in self._baselines:
            self._baselines[key] = {
                "mean": value,
                "m2": 0,
                "std": 0,
                "min": value,
                "max": value,
                "sample_count": 1,
                "last_update": timestamp,
            }
        else:
            baseline = self._baselines[key]
            n = baseline["sample_count"] + 1

            # Welford's algorithm
            delta = value - baseline["mean"]
            baseline["mean"] += delta / n
            delta2 = value - baseline["mean"]
            baseline["m2"] += delta * delta2

            if n > 1:
                baseline["std"] = math.sqrt(baseline["m2"] / (n - 1))

            baseline["min"] = min(baseline["min"], value)
            baseline["max"] = max(baseline["max"], value)
            baseline["sample_count"] = n
            baseline["last_update"] = timestamp

    def update_seasonal_pattern(
        self,
        metric: str,
        equipment: Optional[str],
        value: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Update seasonal pattern with a new value."""
        timestamp = timestamp or datetime.utcnow()
        key = self._make_key(metric, equipment)
        hour = timestamp.hour

        if key not in self._seasonal_patterns:
            self._seasonal_patterns[key] = {}

        if hour not in self._seasonal_patterns[key]:
            self._seasonal_patterns[key][hour] = {
                "mean": value,
                "m2": 0,
                "std": 0,
                "count": 1,
            }
        else:
            pattern = self._seasonal_patterns[key][hour]
            n = pattern["count"] + 1

            delta = value - pattern["mean"]
            pattern["mean"] += delta / n
            delta2 = value - pattern["mean"]
            pattern["m2"] += delta * delta2

            if n > 1:
                pattern["std"] = math.sqrt(pattern["m2"] / (n - 1))

            pattern["count"] = n

    def check_value(
        self,
        metric: str,
        equipment: Optional[str],
        value: float,
        config: ThresholdConfig,
        current_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Check a value against thresholds.

        Returns:
            Dict with breach info: {breached, severity, threshold, deviation}
        """
        current_time = current_time or datetime.utcnow()
        thresholds = self.get_threshold(metric, equipment, config, current_time)
        key = self._make_key(metric, equipment)
        baseline = self._baselines.get(key, {})

        result = {
            "breached": False,
            "severity": None,
            "threshold": None,
            "value": value,
            "warning_threshold": thresholds["warning"],
            "critical_threshold": thresholds["critical"],
            "baseline_mean": baseline.get("mean"),
            "baseline_std": baseline.get("std"),
            "deviation_percent": None,
        }

        # Check for breach
        is_greater = config.comparison in ["greater_than", "greater_or_equal"]

        if thresholds["critical"] is not None:
            critical_breached = (
                value >= thresholds["critical"] if is_greater
                else value <= thresholds["critical"]
            )
            if critical_breached:
                result["breached"] = True
                result["severity"] = AlertSeverity.CRITICAL
                result["threshold"] = thresholds["critical"]

        if not result["breached"] and thresholds["warning"] is not None:
            warning_breached = (
                value >= thresholds["warning"] if is_greater
                else value <= thresholds["warning"]
            )
            if warning_breached:
                result["breached"] = True
                result["severity"] = AlertSeverity.MEDIUM
                result["threshold"] = thresholds["warning"]

        # Calculate deviation from baseline
        if baseline.get("mean") is not None and baseline["mean"] != 0:
            result["deviation_percent"] = (
                (value - baseline["mean"]) / baseline["mean"] * 100
            )

        return result

    def check_rate_of_change(
        self,
        metric: str,
        equipment: Optional[str],
        value: float,
        config: ThresholdConfig,
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Check rate of change threshold."""
        timestamp = timestamp or datetime.utcnow()
        key = self._make_key(metric, equipment)

        result = {
            "breached": False,
            "rate_per_minute": None,
            "max_rate": config.max_rate_per_minute,
        }

        if not config.rate_of_change_enabled:
            return result

        # Get recent values
        recent = self._recent_values.get(key, [])
        if len(recent) < 2:
            return result

        # Calculate rate over window
        window_start = timestamp - timedelta(minutes=config.rate_window_minutes)
        window_values = [(t, v) for t, v in recent if t >= window_start]

        if len(window_values) < 2:
            return result

        oldest = window_values[0]
        newest = window_values[-1]

        time_diff_minutes = (newest[0] - oldest[0]).total_seconds() / 60
        if time_diff_minutes > 0:
            rate = (newest[1] - oldest[1]) / time_diff_minutes
            result["rate_per_minute"] = rate

            if config.max_rate_per_minute is not None:
                if abs(rate) > config.max_rate_per_minute:
                    result["breached"] = True

        return result

    def get_baseline_stats(
        self,
        metric: str,
        equipment: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Get baseline statistics for a metric."""
        key = self._make_key(metric, equipment)
        return self._baselines.get(key)

    def get_seasonal_pattern(
        self,
        metric: str,
        equipment: Optional[str]
    ) -> Optional[Dict[int, Dict[str, float]]]:
        """Get seasonal pattern for a metric."""
        key = self._make_key(metric, equipment)
        return self._seasonal_patterns.get(key)

    def reset_baseline(
        self,
        metric: str,
        equipment: Optional[str]
    ) -> None:
        """Reset baseline for a metric."""
        key = self._make_key(metric, equipment)
        if key in self._baselines:
            del self._baselines[key]
        if key in self._recent_values:
            del self._recent_values[key]

    def apply_hysteresis(
        self,
        is_currently_alerting: bool,
        value: float,
        threshold: float,
        config: ThresholdConfig,
    ) -> bool:
        """
        Apply hysteresis to prevent alert flapping.

        Returns:
            True if alert should remain active, False if should clear
        """
        if not is_currently_alerting:
            return False

        hysteresis = config.hysteresis_percent / 100.0
        clear_threshold = threshold * (1 - hysteresis)

        is_greater = config.comparison in ["greater_than", "greater_or_equal"]

        if is_greater:
            # Alert clears when value drops below threshold - hysteresis
            return value >= clear_threshold
        else:
            # Alert clears when value rises above threshold + hysteresis
            clear_threshold = threshold * (1 + hysteresis)
            return value <= clear_threshold

    def _make_key(self, metric: str, equipment: Optional[str]) -> str:
        """Create storage key."""
        if equipment:
            return f"{metric}:{equipment}"
        return metric
