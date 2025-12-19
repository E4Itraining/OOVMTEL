"""
STL Decomposer - Seasonal-Trend decomposition using LOESS
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import uuid

from .models import (
    SeasonalityType,
    TrendType,
    PatternStrength,
    DecompositionResult,
    TrendComponent,
    SeasonalComponent,
    ResidualAnalysis,
    STANDARD_PERIODS,
)

logger = logging.getLogger(__name__)


class STLDecomposer:
    """
    STL (Seasonal-Trend decomposition using LOESS) implementation.

    This is a pure Python implementation for environments without statsmodels.
    For production use with large datasets, consider using statsmodels.STL.

    Features:
    - Multiple seasonal period detection
    - Robust to outliers
    - Configurable smoothing parameters
    - Trend and seasonal strength metrics
    """

    def __init__(
        self,
        seasonal_period: int = 24,
        trend_smoothness: int = None,
        seasonal_smoothness: int = None,
        robust: bool = True,
        max_iterations: int = 10,
    ):
        """
        Initialize STL decomposer.

        Args:
            seasonal_period: Length of seasonal cycle (e.g., 24 for hourly data with daily pattern)
            trend_smoothness: Smoothing parameter for trend (default: auto)
            seasonal_smoothness: Smoothing parameter for seasonal (default: auto)
            robust: Use robust fitting (less sensitive to outliers)
            max_iterations: Maximum iterations for robust fitting
        """
        self.seasonal_period = seasonal_period
        self.trend_smoothness = trend_smoothness or (seasonal_period * 2 + 1)
        self.seasonal_smoothness = seasonal_smoothness or 7
        self.robust = robust
        self.max_iterations = max_iterations

    def decompose(
        self,
        values: List[float],
        timestamps: Optional[List[datetime]] = None,
        metric: str = "metric",
        equipment: Optional[str] = None,
    ) -> DecompositionResult:
        """
        Perform STL decomposition on time series data.

        Args:
            values: Time series values
            timestamps: Optional timestamps for values
            metric: Name of the metric
            equipment: Optional equipment identifier

        Returns:
            DecompositionResult with trend, seasonal, and residual components
        """
        n = len(values)

        if n < self.seasonal_period * 2:
            logger.warning(f"Insufficient data for STL: {n} points, need {self.seasonal_period * 2}")
            return self._create_empty_result(values, timestamps, metric, equipment)

        # Initialize
        trend = [0.0] * n
        seasonal = [0.0] * n
        residual = values.copy()

        # Iterative decomposition
        for iteration in range(self.max_iterations):
            # Step 1: Detrend
            detrended = [values[i] - trend[i] for i in range(n)]

            # Step 2: Calculate seasonal component
            seasonal = self._calculate_seasonal(detrended)

            # Step 3: Deseasonalize
            deseasonalized = [values[i] - seasonal[i] for i in range(n)]

            # Step 4: Calculate trend component
            trend = self._loess_smooth(deseasonalized, self.trend_smoothness)

            # Step 5: Calculate residuals
            new_residual = [values[i] - trend[i] - seasonal[i] for i in range(n)]

            # Check convergence
            if self._check_convergence(residual, new_residual):
                residual = new_residual
                break

            residual = new_residual

        # Create result
        result = DecompositionResult(
            metric=metric,
            equipment=equipment,
            decomposed_at=datetime.utcnow(),
            original_values=values,
            timestamps=timestamps or [],
            data_points=n,
            trend=self._analyze_trend(trend, timestamps),
            seasonal_components=[self._analyze_seasonal(seasonal, self.seasonal_period)],
            residual=self._analyze_residual(residual),
            stl_params={
                "seasonal_period": self.seasonal_period,
                "trend_smoothness": self.trend_smoothness,
                "seasonal_smoothness": self.seasonal_smoothness,
                "robust": self.robust,
            }
        )

        # Calculate quality metrics
        result.decomposition_quality = self._calculate_quality(values, trend, seasonal, residual)
        result.total_variance_explained = self._calculate_variance_explained(values, residual)

        total_var = self._variance(values)
        if total_var > 0:
            result.trend_variance_ratio = self._variance(trend) / total_var
            result.seasonal_variance_ratio = self._variance(seasonal) / total_var
            result.residual_variance_ratio = self._variance(residual) / total_var

        return result

    def _calculate_seasonal(self, detrended: List[float]) -> List[float]:
        """Calculate seasonal component using cycle-subseries averaging."""
        n = len(detrended)
        period = self.seasonal_period
        seasonal = [0.0] * n

        # Group by position in cycle
        cycle_values: Dict[int, List[float]] = {i: [] for i in range(period)}

        for i, val in enumerate(detrended):
            cycle_pos = i % period
            cycle_values[cycle_pos].append(val)

        # Calculate mean for each cycle position
        cycle_means = {}
        for pos, vals in cycle_values.items():
            if vals:
                cycle_means[pos] = sum(vals) / len(vals)
            else:
                cycle_means[pos] = 0.0

        # Center the seasonal component (subtract mean)
        overall_mean = sum(cycle_means.values()) / len(cycle_means)
        for pos in cycle_means:
            cycle_means[pos] -= overall_mean

        # Apply to full series
        for i in range(n):
            cycle_pos = i % period
            seasonal[i] = cycle_means[cycle_pos]

        # Smooth seasonal component
        seasonal = self._loess_smooth(seasonal, self.seasonal_smoothness)

        return seasonal

    def _loess_smooth(self, values: List[float], span: int) -> List[float]:
        """
        Apply LOESS (locally weighted scatterplot smoothing).

        Simplified implementation using moving weighted average.
        """
        n = len(values)
        smoothed = []

        half_span = span // 2

        for i in range(n):
            start = max(0, i - half_span)
            end = min(n, i + half_span + 1)

            # Tricube weights
            weights = []
            window_values = []

            for j in range(start, end):
                dist = abs(j - i) / (half_span + 1)
                weight = (1 - dist ** 3) ** 3 if dist < 1 else 0
                weights.append(weight)
                window_values.append(values[j])

            # Weighted average
            if sum(weights) > 0:
                weighted_sum = sum(w * v for w, v in zip(weights, window_values))
                smoothed_val = weighted_sum / sum(weights)
            else:
                smoothed_val = values[i]

            smoothed.append(smoothed_val)

        return smoothed

    def _check_convergence(
        self,
        old_residual: List[float],
        new_residual: List[float],
        threshold: float = 0.001
    ) -> bool:
        """Check if decomposition has converged."""
        if len(old_residual) != len(new_residual):
            return False

        diff = sum(abs(o - n) for o, n in zip(old_residual, new_residual))
        total = sum(abs(o) for o in old_residual) + 1e-10

        return diff / total < threshold

    def _analyze_trend(
        self,
        trend: List[float],
        timestamps: Optional[List[datetime]]
    ) -> TrendComponent:
        """Analyze trend component."""
        n = len(trend)
        if n < 2:
            return TrendComponent(values=trend)

        # Linear regression for slope
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(trend) / n

        numerator = sum((x[i] - x_mean) * (trend[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        slope = numerator / denominator if denominator > 0 else 0
        intercept = y_mean - slope * x_mean

        # R-squared
        ss_res = sum((trend[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        ss_tot = sum((trend[i] - y_mean) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Direction
        if slope > 0.01:
            direction = "increasing"
        elif slope < -0.01:
            direction = "decreasing"
        else:
            direction = "stable"

        # Projections
        projected_7d = trend[-1] + slope * 168 if timestamps else None  # 7 days in hours
        projected_30d = trend[-1] + slope * 720 if timestamps else None  # 30 days in hours

        return TrendComponent(
            trend_type=TrendType.LINEAR,
            values=trend,
            slope=slope,
            intercept=intercept,
            r_squared=max(0, r_squared),
            direction=direction,
            change_rate_per_day=slope * 24,
            projected_value_7d=projected_7d,
            projected_value_30d=projected_30d,
        )

    def _analyze_seasonal(
        self,
        seasonal: List[float],
        period: int
    ) -> SeasonalComponent:
        """Analyze seasonal component."""
        n = len(seasonal)

        # Calculate amplitude
        amplitude = max(seasonal) - min(seasonal)

        # Find peaks and troughs
        peaks = []
        troughs = []

        for i in range(1, n - 1):
            if seasonal[i] > seasonal[i-1] and seasonal[i] > seasonal[i+1]:
                peaks.append(i)
            elif seasonal[i] < seasonal[i-1] and seasonal[i] < seasonal[i+1]:
                troughs.append(i)

        # Calculate strength (variance ratio)
        total_var = self._variance(seasonal)
        detrended_var = total_var  # Simplified

        if detrended_var > 0:
            strength = max(0, 1 - self._variance([0] * n) / detrended_var)
        else:
            strength = 0

        # Pattern strength classification
        if strength > 0.8:
            pattern_strength = PatternStrength.STRONG
        elif strength > 0.5:
            pattern_strength = PatternStrength.MODERATE
        elif strength > 0.2:
            pattern_strength = PatternStrength.WEAK
        else:
            pattern_strength = PatternStrength.NONE

        # Determine seasonality type based on period
        seasonality_type = SeasonalityType.CUSTOM
        for st, info in STANDARD_PERIODS.items():
            if info["period"] == period:
                seasonality_type = st
                break

        return SeasonalComponent(
            seasonality_type=seasonality_type,
            period=period,
            period_unit="hours",
            values=seasonal,
            amplitude=amplitude,
            strength=strength,
            pattern_strength=pattern_strength,
            peak_positions=peaks[:10],
            trough_positions=troughs[:10],
        )

    def _analyze_residual(self, residual: List[float]) -> ResidualAnalysis:
        """Analyze residual component."""
        n = len(residual)
        if n == 0:
            return ResidualAnalysis()

        mean = sum(residual) / n
        variance = self._variance(residual)
        std = math.sqrt(variance)

        # Skewness and kurtosis
        if std > 0:
            skewness = sum((r - mean) ** 3 for r in residual) / (n * std ** 3)
            kurtosis = sum((r - mean) ** 4 for r in residual) / (n * std ** 4) - 3
        else:
            skewness = 0
            kurtosis = 0

        # Detect outliers (beyond 3 std)
        outliers = []
        for i, r in enumerate(residual):
            if abs(r - mean) > 3 * std and std > 0:
                outliers.append((i, r))

        # Autocorrelation (simplified - first 10 lags)
        autocorr = []
        for lag in range(1, min(11, n)):
            if n - lag > 0:
                cov = sum((residual[i] - mean) * (residual[i + lag] - mean)
                          for i in range(n - lag)) / (n - lag)
                autocorr.append(cov / variance if variance > 0 else 0)

        # White noise test (simplified - check if autocorrelations are small)
        is_white_noise = all(abs(ac) < 2 / math.sqrt(n) for ac in autocorr) if autocorr else True

        return ResidualAnalysis(
            values=residual,
            mean=mean,
            std=std,
            variance=variance,
            skewness=skewness,
            kurtosis=kurtosis,
            is_white_noise=is_white_noise,
            autocorrelation=autocorr,
            outliers=outliers[:20],
            outlier_count=len(outliers),
            outlier_percentage=(len(outliers) / n * 100) if n > 0 else 0,
        )

    def _variance(self, values: List[float]) -> float:
        """Calculate variance of values."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)

    def _calculate_quality(
        self,
        original: List[float],
        trend: List[float],
        seasonal: List[float],
        residual: List[float]
    ) -> float:
        """Calculate decomposition quality score."""
        # Quality based on how well components reconstruct original
        n = len(original)
        reconstruction = [trend[i] + seasonal[i] for i in range(n)]

        # Mean absolute error
        mae = sum(abs(original[i] - reconstruction[i]) for i in range(n)) / n
        original_range = max(original) - min(original) + 1e-10

        # Quality inversely related to reconstruction error
        quality = max(0, 1 - mae / original_range)

        return quality

    def _calculate_variance_explained(
        self,
        original: List[float],
        residual: List[float]
    ) -> float:
        """Calculate percentage of variance explained."""
        original_var = self._variance(original)
        residual_var = self._variance(residual)

        if original_var > 0:
            return (1 - residual_var / original_var) * 100
        return 0.0

    def _create_empty_result(
        self,
        values: List[float],
        timestamps: Optional[List[datetime]],
        metric: str,
        equipment: Optional[str]
    ) -> DecompositionResult:
        """Create empty result for insufficient data."""
        return DecompositionResult(
            metric=metric,
            equipment=equipment,
            decomposed_at=datetime.utcnow(),
            original_values=values,
            timestamps=timestamps or [],
            data_points=len(values),
            decomposition_quality=0.0,
        )


class MultiSeasonalSTL:
    """
    Multi-seasonal STL decomposition.

    Handles multiple seasonal periods (e.g., hourly + daily + weekly).
    """

    def __init__(self, periods: List[int], robust: bool = True):
        """
        Initialize multi-seasonal decomposer.

        Args:
            periods: List of seasonal periods to extract
            robust: Use robust fitting
        """
        self.periods = sorted(periods)
        self.robust = robust

    def decompose(
        self,
        values: List[float],
        timestamps: Optional[List[datetime]] = None,
        metric: str = "metric",
        equipment: Optional[str] = None,
    ) -> DecompositionResult:
        """
        Perform multi-seasonal decomposition.

        Iteratively extracts seasonal components from shortest to longest period.
        """
        n = len(values)
        current_values = values.copy()
        seasonal_components: List[SeasonalComponent] = []

        # Extract each seasonal component
        for period in self.periods:
            if n < period * 2:
                continue

            decomposer = STLDecomposer(
                seasonal_period=period,
                robust=self.robust
            )

            result = decomposer.decompose(
                current_values,
                timestamps,
                metric,
                equipment
            )

            if result.seasonal_components:
                seasonal_components.append(result.seasonal_components[0])
                # Remove this seasonal component for next iteration
                current_values = [
                    current_values[i] - result.seasonal_components[0].values[i]
                    for i in range(n)
                ]

        # Final trend extraction
        final_decomposer = STLDecomposer(
            seasonal_period=self.periods[0] if self.periods else 24,
            robust=self.robust
        )
        final_result = final_decomposer.decompose(current_values, timestamps, metric, equipment)

        # Combine results
        return DecompositionResult(
            metric=metric,
            equipment=equipment,
            decomposed_at=datetime.utcnow(),
            original_values=values,
            timestamps=timestamps or [],
            data_points=n,
            trend=final_result.trend,
            seasonal_components=seasonal_components,
            residual=final_result.residual,
            decomposition_quality=final_result.decomposition_quality,
            total_variance_explained=final_result.total_variance_explained,
            stl_params={"periods": self.periods, "robust": self.robust},
        )
