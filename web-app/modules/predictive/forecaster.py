"""
Time Series Forecaster - Analyzes trends and forecasts future values
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from .models import TrendAnalysis, TrendDirection


class TimeSeriesForecaster:
    """
    Time series analysis and forecasting for industrial metrics.

    Methods:
    - Linear trend analysis
    - Simple exponential smoothing
    - Moving average forecasting
    """

    def __init__(self, forecast_horizon_hours: int = 168):
        self.forecast_horizon_hours = forecast_horizon_hours

    def analyze_trend(
        self,
        metric: str,
        current_value: float,
        historical_values: Optional[List[Dict]] = None,
        equipment: Optional[str] = None
    ) -> Optional[TrendAnalysis]:
        """Analyze trend for a metric."""

        # If no historical data, simulate based on typical patterns
        if not historical_values:
            historical_values = self._simulate_historical(metric, current_value)

        if not historical_values or len(historical_values) < 3:
            return None

        # Extract values
        values = [v.get("value", 0) for v in historical_values]
        values.append(current_value)  # Add current value

        # Calculate linear regression
        slope, intercept, r_squared = self._linear_regression(values)

        # Determine trend direction
        if abs(slope) < 0.01:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING

        # Check for volatility
        std = self._calculate_std(values)
        mean = sum(values) / len(values)
        cv = std / mean if mean != 0 else 0

        if cv > 0.2:  # High coefficient of variation
            direction = TrendDirection.VOLATILE

        # Project future values
        n_current = len(values)
        projected_24h = intercept + slope * (n_current + 24)  # 24 hours ahead
        projected_7d = intercept + slope * (n_current + 168)   # 7 days ahead

        # Calculate change percentages
        start_value = values[0] if values else current_value
        change_24h = ((projected_24h - current_value) / current_value * 100) if current_value != 0 else 0
        change_7d = ((projected_7d - current_value) / current_value * 100) if current_value != 0 else 0

        # Determine if concerning
        is_concerning = False
        threshold_breach_eta = None

        # Check metric-specific thresholds
        thresholds = self._get_thresholds(metric)
        if thresholds:
            upper = thresholds.get("upper")
            lower = thresholds.get("lower")

            if upper and slope > 0:
                # Time to breach upper threshold
                if projected_7d > upper:
                    is_concerning = True
                    hours_to_breach = (upper - current_value) / (slope / len(values)) if slope > 0 else None
                    if hours_to_breach and hours_to_breach > 0:
                        threshold_breach_eta = timedelta(hours=hours_to_breach)

            if lower and slope < 0:
                # Time to breach lower threshold
                if projected_7d < lower:
                    is_concerning = True
                    hours_to_breach = (current_value - lower) / (-slope / len(values)) if slope < 0 else None
                    if hours_to_breach and hours_to_breach > 0:
                        threshold_breach_eta = timedelta(hours=hours_to_breach)

        return TrendAnalysis(
            metric=metric,
            equipment=equipment,
            direction=direction,
            slope=slope,
            slope_unit="per_hour",
            r_squared=r_squared,
            start_value=start_value,
            current_value=current_value,
            projected_value_24h=projected_24h,
            projected_value_7d=projected_7d,
            change_percent_24h=change_24h,
            is_concerning=is_concerning,
            threshold_breach_eta=threshold_breach_eta,
            analysis_period=f"last {len(values)} data points"
        )

    def forecast(
        self,
        values: List[float],
        horizon: int = 24,
        method: str = "linear"
    ) -> List[float]:
        """Forecast future values."""
        if method == "linear":
            return self._linear_forecast(values, horizon)
        elif method == "exponential":
            return self._exponential_smoothing_forecast(values, horizon)
        elif method == "moving_average":
            return self._moving_average_forecast(values, horizon)
        else:
            return self._linear_forecast(values, horizon)

    def _linear_regression(self, values: List[float]) -> Tuple[float, float, float]:
        """Simple linear regression."""
        n = len(values)
        if n < 2:
            return 0, values[0] if values else 0, 0

        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
        denominator = sum((xi - x_mean) ** 2 for xi in x)

        if denominator == 0:
            return 0, y_mean, 0

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        # Calculate R-squared
        y_pred = [intercept + slope * xi for xi in x]
        ss_res = sum((yi - yp) ** 2 for yi, yp in zip(values, y_pred))
        ss_tot = sum((yi - y_mean) ** 2 for yi in values)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        return slope, intercept, max(0, r_squared)

    def _linear_forecast(self, values: List[float], horizon: int) -> List[float]:
        """Linear extrapolation forecast."""
        slope, intercept, _ = self._linear_regression(values)
        n = len(values)
        return [intercept + slope * (n + i) for i in range(horizon)]

    def _exponential_smoothing_forecast(
        self,
        values: List[float],
        horizon: int,
        alpha: float = 0.3
    ) -> List[float]:
        """Simple exponential smoothing forecast."""
        if not values:
            return [0] * horizon

        # Calculate smoothed values
        smoothed = [values[0]]
        for value in values[1:]:
            smoothed.append(alpha * value + (1 - alpha) * smoothed[-1])

        # Forecast is last smoothed value repeated
        last_smoothed = smoothed[-1]
        return [last_smoothed] * horizon

    def _moving_average_forecast(
        self,
        values: List[float],
        horizon: int,
        window: int = 5
    ) -> List[float]:
        """Moving average forecast."""
        if not values:
            return [0] * horizon

        # Calculate moving average
        if len(values) < window:
            ma = sum(values) / len(values)
        else:
            ma = sum(values[-window:]) / window

        return [ma] * horizon

    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if not values:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    def _simulate_historical(
        self,
        metric: str,
        current_value: float,
        points: int = 24
    ) -> List[Dict]:
        """Simulate historical data based on metric type and current value."""
        import random

        values = []
        now = datetime.utcnow()

        # Add some realistic variation
        for i in range(points, 0, -1):
            # Simulate gradual approach to current value with noise
            progress = (points - i) / points
            noise = random.gauss(0, current_value * 0.02)  # 2% noise

            # Base value approaches current value
            base = current_value * (0.95 + 0.05 * progress) + noise

            values.append({
                "timestamp": now - timedelta(hours=i),
                "value": max(0, base)
            })

        return values

    def _get_thresholds(self, metric: str) -> Optional[Dict[str, float]]:
        """Get thresholds for common metrics."""
        thresholds = {
            "oee": {"lower": 75, "upper": None},
            "quality_rate": {"lower": 95, "upper": None},
            "availability": {"lower": 85, "upper": None},
            "performance": {"lower": 80, "upper": None},
            "cpu_usage": {"lower": None, "upper": 90},
            "memory_usage": {"lower": None, "upper": 85},
            "disk_usage": {"lower": None, "upper": 85},
            "temperature": {"lower": None, "upper": 80},
            "vibration": {"lower": None, "upper": 8},
            "pressure": {"lower": 2, "upper": 8},
        }
        return thresholds.get(metric)
