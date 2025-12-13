"""
Temporal Correlator - Analyzes time-based correlations between metrics
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from .models import CorrelationResult


class TemporalCorrelator:
    """
    Analyzes temporal correlations between metrics and events.

    Features:
    - Pearson correlation calculation
    - Cross-correlation with time lag detection
    - Granger causality hints
    - Anomaly co-occurrence detection
    """

    def __init__(self, correlation_threshold: float = 0.7):
        self.correlation_threshold = correlation_threshold

    def analyze_correlations(
        self,
        metrics: Dict[str, List[Dict]],
        events: List[Dict],
        max_lag_minutes: int = 30
    ) -> List[CorrelationResult]:
        """
        Analyze correlations between all pairs of metrics.

        Args:
            metrics: Dict of metric name -> list of {timestamp, value}
            events: List of events with timestamps
            max_lag_minutes: Maximum time lag to consider

        Returns:
            List of significant correlations
        """
        results = []
        metric_names = list(metrics.keys())

        # Analyze metric-metric correlations
        for i, metric_a in enumerate(metric_names):
            for metric_b in metric_names[i + 1:]:
                correlation = self._calculate_correlation_with_lag(
                    metrics[metric_a],
                    metrics[metric_b],
                    max_lag_minutes
                )
                if correlation and correlation.is_significant:
                    results.append(correlation)

        # Analyze event-metric correlations
        for metric_name, metric_values in metrics.items():
            event_correlation = self._correlate_with_events(
                metric_values, events, metric_name
            )
            if event_correlation and event_correlation.is_significant:
                results.append(event_correlation)

        # Sort by absolute correlation strength
        results.sort(key=lambda x: abs(x.correlation), reverse=True)

        return results

    def _calculate_correlation_with_lag(
        self,
        series_a: List[Dict],
        series_b: List[Dict],
        max_lag_minutes: int
    ) -> Optional[CorrelationResult]:
        """Calculate correlation between two time series with optimal lag detection."""
        if not series_a or not series_b:
            return None

        # Extract values (assume aligned by index for simplicity)
        values_a = [item.get("value", 0) for item in series_a]
        values_b = [item.get("value", 0) for item in series_b]

        if len(values_a) < 3 or len(values_b) < 3:
            return None

        # Ensure same length
        min_len = min(len(values_a), len(values_b))
        values_a = values_a[:min_len]
        values_b = values_b[:min_len]

        # Calculate correlations at different lags
        best_correlation = 0
        best_lag = 0

        for lag in range(0, min(max_lag_minutes // 5, len(values_a) - 2)):
            if lag == 0:
                corr = self._pearson_correlation(values_a, values_b)
            else:
                # Shift series_b by lag
                corr = self._pearson_correlation(values_a[:-lag], values_b[lag:])

            if abs(corr) > abs(best_correlation):
                best_correlation = corr
                best_lag = lag

        # Calculate p-value approximation
        n = min_len - best_lag
        if n > 2 and abs(best_correlation) < 1:
            t_stat = best_correlation * math.sqrt(n - 2) / math.sqrt(1 - best_correlation ** 2)
            # Approximate p-value (simplified)
            p_value = 2 * (1 - self._t_cdf(abs(t_stat), n - 2))
        else:
            p_value = 1.0

        # Determine direction
        if best_correlation > 0.1:
            direction = "positive"
        elif best_correlation < -0.1:
            direction = "negative"
        else:
            direction = "none"

        metric_a_name = series_a[0].get("metric", "metric_a") if series_a else "metric_a"
        metric_b_name = series_b[0].get("metric", "metric_b") if series_b else "metric_b"

        return CorrelationResult(
            metric_a=metric_a_name,
            metric_b=metric_b_name,
            correlation=best_correlation,
            lag_seconds=best_lag * 300,  # Convert to seconds (5 min intervals)
            p_value=p_value,
            is_significant=abs(best_correlation) >= self.correlation_threshold and p_value < 0.05,
            direction=direction
        )

    def _correlate_with_events(
        self,
        metric_values: List[Dict],
        events: List[Dict],
        metric_name: str
    ) -> Optional[CorrelationResult]:
        """Correlate metric changes with events."""
        if not metric_values or not events:
            return None

        # Convert events to binary time series
        event_times = [e.get("timestamp") for e in events if e.get("timestamp")]
        if not event_times:
            return None

        # Check if metric values changed around event times
        changes_around_events = 0
        total_events = 0

        for event_time in event_times:
            if isinstance(event_time, str):
                try:
                    event_time = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
                except ValueError:
                    continue

            # Find metric values around this event
            before_values = []
            after_values = []

            for mv in metric_values:
                mv_time = mv.get("timestamp")
                if isinstance(mv_time, str):
                    try:
                        mv_time = datetime.fromisoformat(mv_time.replace("Z", "+00:00"))
                    except ValueError:
                        continue

                if mv_time and event_time:
                    diff = (event_time - mv_time).total_seconds()
                    if -600 <= diff < 0:  # 10 min before
                        before_values.append(mv.get("value", 0))
                    elif 0 <= diff <= 600:  # 10 min after
                        after_values.append(mv.get("value", 0))

            if before_values and after_values:
                avg_before = sum(before_values) / len(before_values)
                avg_after = sum(after_values) / len(after_values)

                # Check for significant change (>5%)
                if avg_before != 0:
                    change_pct = abs(avg_after - avg_before) / abs(avg_before) * 100
                    if change_pct > 5:
                        changes_around_events += 1

                total_events += 1

        if total_events == 0:
            return None

        # Correlation is based on how often metrics change around events
        correlation = changes_around_events / total_events

        return CorrelationResult(
            metric_a=metric_name,
            metric_b="events",
            correlation=correlation,
            lag_seconds=0,
            p_value=0.1 if correlation > 0.5 else 0.5,  # Simplified
            is_significant=correlation >= 0.5,
            direction="positive" if correlation > 0 else "none"
        )

    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        n = len(x)
        if n != len(y) or n == 0:
            return 0

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))

        std_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
        std_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))

        if std_x == 0 or std_y == 0:
            return 0

        return numerator / (std_x * std_y)

    def _t_cdf(self, t: float, df: int) -> float:
        """Approximate t-distribution CDF (simplified)."""
        # Simplified approximation for p-value calculation
        x = df / (df + t ** 2)
        return 1 - 0.5 * x ** (df / 2)

    def detect_anomaly_clusters(
        self,
        metrics: Dict[str, List[Dict]],
        threshold_std: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Detect clusters of anomalies that occur together.

        Returns list of anomaly clusters with timestamps and affected metrics.
        """
        # Find anomalies in each metric
        anomalies_by_time = defaultdict(list)

        for metric_name, values in metrics.items():
            if not values:
                continue

            # Calculate mean and std
            numeric_values = [v.get("value", 0) for v in values]
            if not numeric_values:
                continue

            mean = sum(numeric_values) / len(numeric_values)
            variance = sum((v - mean) ** 2 for v in numeric_values) / len(numeric_values)
            std = math.sqrt(variance) if variance > 0 else 1

            # Find anomalies
            for item in values:
                value = item.get("value", 0)
                timestamp = item.get("timestamp")

                if abs(value - mean) > threshold_std * std:
                    # Round timestamp to nearest minute for clustering
                    if timestamp:
                        if isinstance(timestamp, datetime):
                            minute_key = timestamp.replace(second=0, microsecond=0)
                        else:
                            minute_key = timestamp
                        anomalies_by_time[str(minute_key)].append({
                            "metric": metric_name,
                            "value": value,
                            "deviation": (value - mean) / std
                        })

        # Convert to cluster list
        clusters = []
        for timestamp, anomalies in anomalies_by_time.items():
            if len(anomalies) > 1:  # Only clusters with multiple anomalies
                clusters.append({
                    "timestamp": timestamp,
                    "anomalies": anomalies,
                    "affected_metrics": [a["metric"] for a in anomalies],
                    "severity": max(abs(a["deviation"]) for a in anomalies)
                })

        # Sort by severity
        clusters.sort(key=lambda x: x["severity"], reverse=True)

        return clusters
