"""
Pattern Detector - Automatic seasonality pattern detection
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import uuid

from .models import (
    SeasonalityType,
    PatternStrength,
    SeasonalPattern,
    AnomalyContext,
    STANDARD_PERIODS,
    INDUSTRIAL_PATTERNS,
)

logger = logging.getLogger(__name__)


class PatternDetector:
    """
    Automatic detection of seasonal patterns in time series data.

    Features:
    - Auto-correlation based period detection
    - FFT-based frequency analysis
    - Multiple pattern detection
    - Pattern strength scoring
    - Contextual anomaly detection
    """

    def __init__(
        self,
        min_periods: int = 2,
        strength_threshold: float = 0.2,
        candidate_periods: Optional[List[int]] = None,
    ):
        """
        Initialize pattern detector.

        Args:
            min_periods: Minimum number of complete periods required
            strength_threshold: Minimum strength to report a pattern
            candidate_periods: List of periods to test (None = auto-detect)
        """
        self.min_periods = min_periods
        self.strength_threshold = strength_threshold
        self.candidate_periods = candidate_periods or [
            6, 8, 12, 24,        # Intra-day (hourly data)
            7, 14, 28,           # Weekly patterns (daily data)
            30, 90, 180, 365,    # Monthly/yearly patterns
        ]

    def detect_patterns(
        self,
        values: List[float],
        timestamps: Optional[List[datetime]] = None,
        metric: str = "metric",
        equipment: Optional[str] = None,
    ) -> List[SeasonalPattern]:
        """
        Detect seasonal patterns in time series.

        Args:
            values: Time series values
            timestamps: Optional timestamps
            metric: Metric name
            equipment: Equipment identifier

        Returns:
            List of detected seasonal patterns
        """
        n = len(values)
        if n < 10:
            return []

        patterns = []

        # Method 1: Autocorrelation analysis
        acf_periods = self._detect_via_autocorrelation(values)

        # Method 2: FFT frequency analysis
        fft_periods = self._detect_via_fft(values)

        # Combine and filter candidates
        all_candidates = set(acf_periods + fft_periods + self.candidate_periods)
        valid_candidates = [p for p in all_candidates if n >= p * self.min_periods]

        # Score each candidate period
        for period in valid_candidates:
            strength = self._calculate_period_strength(values, period)

            if strength >= self.strength_threshold:
                pattern = self._create_pattern(
                    values, timestamps, period, strength, metric, equipment
                )
                patterns.append(pattern)

        # Sort by strength descending
        patterns.sort(key=lambda p: p.strength_score, reverse=True)

        return patterns

    def _detect_via_autocorrelation(
        self,
        values: List[float],
        max_lag: Optional[int] = None
    ) -> List[int]:
        """Detect periods using autocorrelation function."""
        n = len(values)
        max_lag = max_lag or min(n // 2, 200)

        # Calculate mean and variance
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n

        if variance == 0:
            return []

        # Calculate ACF
        acf = []
        for lag in range(1, max_lag + 1):
            if lag >= n:
                break
            cov = sum((values[i] - mean) * (values[i + lag] - mean)
                      for i in range(n - lag)) / (n - lag)
            acf.append(cov / variance)

        # Find peaks in ACF (significant periods)
        periods = []
        threshold = 2 / math.sqrt(n)  # Significance threshold

        for i in range(1, len(acf) - 1):
            if acf[i] > acf[i-1] and acf[i] > acf[i+1] and acf[i] > threshold:
                periods.append(i + 1)  # +1 because lag starts at 1

        return periods[:5]  # Return top 5 candidates

    def _detect_via_fft(self, values: List[float]) -> List[int]:
        """Detect periods using FFT frequency analysis."""
        n = len(values)

        # Simple DFT implementation (for environments without numpy)
        # Note: For large datasets, use numpy.fft for efficiency
        frequencies = []

        for k in range(1, n // 2):
            real = sum(values[i] * math.cos(2 * math.pi * k * i / n) for i in range(n))
            imag = sum(values[i] * math.sin(2 * math.pi * k * i / n) for i in range(n))
            power = real ** 2 + imag ** 2
            frequencies.append((k, power))

        # Sort by power
        frequencies.sort(key=lambda x: x[1], reverse=True)

        # Convert frequency to period
        periods = []
        for freq_idx, power in frequencies[:10]:
            if freq_idx > 0:
                period = n // freq_idx
                if 2 <= period <= n // self.min_periods:
                    periods.append(period)

        return list(set(periods))[:5]

    def _calculate_period_strength(
        self,
        values: List[float],
        period: int
    ) -> float:
        """
        Calculate the strength of a given period.

        Uses variance ratio approach: how much variance is explained by the period.
        """
        n = len(values)

        if n < period * 2:
            return 0.0

        # Group values by position in period
        groups: Dict[int, List[float]] = {i: [] for i in range(period)}
        for i, val in enumerate(values):
            groups[i % period].append(val)

        # Calculate between-group variance (seasonal)
        group_means = [sum(g) / len(g) if g else 0 for g in groups.values()]
        overall_mean = sum(values) / n

        between_var = sum((gm - overall_mean) ** 2 for gm in group_means) / period

        # Calculate total variance
        total_var = sum((v - overall_mean) ** 2 for v in values) / n

        if total_var == 0:
            return 0.0

        # Strength is ratio of between-group variance to total variance
        strength = between_var / total_var

        return min(1.0, strength)

    def _create_pattern(
        self,
        values: List[float],
        timestamps: Optional[List[datetime]],
        period: int,
        strength: float,
        metric: str,
        equipment: Optional[str],
    ) -> SeasonalPattern:
        """Create a SeasonalPattern object."""
        n = len(values)
        mean_value = sum(values) / n

        # Group by period position
        groups: Dict[int, List[float]] = {i: [] for i in range(period)}
        for i, val in enumerate(values):
            groups[i % period].append(val)

        group_means = {i: sum(g) / len(g) if g else mean_value for i, g in groups.items()}

        # Find peak and trough
        peak_pos = max(group_means.keys(), key=lambda k: group_means[k])
        trough_pos = min(group_means.keys(), key=lambda k: group_means[k])

        typical_high = group_means[peak_pos]
        typical_low = group_means[trough_pos]
        amplitude = typical_high - typical_low
        amplitude_percent = (amplitude / mean_value * 100) if mean_value != 0 else 0

        # Determine seasonality type
        seasonality_type = self._infer_seasonality_type(period, timestamps)

        # Pattern strength classification
        if strength > 0.8:
            pattern_strength = PatternStrength.STRONG
        elif strength > 0.5:
            pattern_strength = PatternStrength.MODERATE
        elif strength > 0.2:
            pattern_strength = PatternStrength.WEAK
        else:
            pattern_strength = PatternStrength.NONE

        # Time labels for peak/trough
        peak_time = self._format_time_label(peak_pos, period, seasonality_type)
        trough_time = self._format_time_label(trough_pos, period, seasonality_type)

        # Description
        description = self._generate_description(
            metric, seasonality_type, period, amplitude_percent, peak_time, trough_time
        )

        return SeasonalPattern(
            pattern_id=f"PAT-{uuid.uuid4().hex[:8].upper()}",
            metric=metric,
            equipment=equipment,
            seasonality_type=seasonality_type,
            period=period,
            period_unit=self._get_period_unit(period, seasonality_type),
            strength=pattern_strength,
            strength_score=strength,
            peak_time=peak_time,
            trough_time=trough_time,
            amplitude=amplitude,
            amplitude_percent=amplitude_percent,
            description=description,
            typical_high=typical_high,
            typical_low=typical_low,
            mean_value=mean_value,
            confidence=strength,
            sample_size=n,
        )

    def _infer_seasonality_type(
        self,
        period: int,
        timestamps: Optional[List[datetime]]
    ) -> SeasonalityType:
        """Infer the type of seasonality based on period."""
        # Common periods for hourly data
        if period in [24, 23, 25]:
            return SeasonalityType.DAILY
        elif period in [168, 167, 169]:  # 24*7
            return SeasonalityType.WEEKLY
        elif period in [720, 730, 744]:  # ~30 days in hours
            return SeasonalityType.MONTHLY
        elif period in [8760, 8784]:  # Year in hours
            return SeasonalityType.YEARLY
        elif period in [7, 6, 8]:
            return SeasonalityType.DAILY  # Daily data with weekly pattern
        elif period in [30, 31, 28, 29]:
            return SeasonalityType.MONTHLY  # Daily data with monthly pattern
        elif period in [365, 366]:
            return SeasonalityType.YEARLY  # Daily data with yearly pattern
        elif period in [4, 8, 12]:
            return SeasonalityType.HOURLY  # Shift patterns
        else:
            return SeasonalityType.CUSTOM

    def _format_time_label(
        self,
        position: int,
        period: int,
        seasonality_type: SeasonalityType
    ) -> str:
        """Format a position as a human-readable time label."""
        if seasonality_type == SeasonalityType.DAILY:
            if period == 24:
                return f"{position:02d}:00"
            elif period == 7:
                days = ["Monday", "Tuesday", "Wednesday", "Thursday",
                        "Friday", "Saturday", "Sunday"]
                return days[position % 7]
        elif seasonality_type == SeasonalityType.WEEKLY:
            if period == 168:
                day = position // 24
                hour = position % 24
                days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                return f"{days[day % 7]} {hour:02d}:00"
        elif seasonality_type == SeasonalityType.MONTHLY:
            return f"Day {position + 1}"
        elif seasonality_type == SeasonalityType.HOURLY:
            return f"Hour {position}"

        return f"Position {position}"

    def _get_period_unit(
        self,
        period: int,
        seasonality_type: SeasonalityType
    ) -> str:
        """Get the unit for a period."""
        if seasonality_type in [SeasonalityType.DAILY, SeasonalityType.WEEKLY]:
            if period >= 24:
                return "hours"
            return "days"
        elif seasonality_type == SeasonalityType.MONTHLY:
            return "days"
        elif seasonality_type == SeasonalityType.YEARLY:
            return "days"
        return "points"

    def _generate_description(
        self,
        metric: str,
        seasonality_type: SeasonalityType,
        period: int,
        amplitude_percent: float,
        peak_time: str,
        trough_time: str,
    ) -> str:
        """Generate human-readable pattern description."""
        type_desc = {
            SeasonalityType.HOURLY: "intra-journalier",
            SeasonalityType.DAILY: "journalier",
            SeasonalityType.WEEKLY: "hebdomadaire",
            SeasonalityType.MONTHLY: "mensuel",
            SeasonalityType.YEARLY: "annuel",
            SeasonalityType.CUSTOM: f"cyclique ({period} points)",
        }

        desc = f"Pattern {type_desc.get(seasonality_type, 'cyclique')} détecté pour {metric}. "
        desc += f"Variation de {amplitude_percent:.1f}% entre pic ({peak_time}) et creux ({trough_time})."

        return desc

    def detect_contextual_anomalies(
        self,
        values: List[float],
        pattern: SeasonalPattern,
        timestamps: Optional[List[datetime]] = None,
        threshold_std: float = 2.0,
    ) -> List[AnomalyContext]:
        """
        Detect anomalies based on seasonal pattern.

        Args:
            values: Time series values
            pattern: Detected seasonal pattern
            timestamps: Optional timestamps
            threshold_std: Standard deviations for anomaly threshold

        Returns:
            List of contextual anomalies
        """
        n = len(values)
        period = pattern.period
        anomalies = []

        # Calculate expected values based on pattern
        groups: Dict[int, List[float]] = {i: [] for i in range(period)}
        for i, val in enumerate(values):
            groups[i % period].append(val)

        # Expected value and std for each position
        expectations = {}
        for pos, vals in groups.items():
            if vals:
                mean = sum(vals) / len(vals)
                std = math.sqrt(sum((v - mean) ** 2 for v in vals) / len(vals)) if len(vals) > 1 else 0
                expectations[pos] = {"mean": mean, "std": max(std, 1e-10)}

        # Detect anomalies
        for i, val in enumerate(values):
            pos = i % period
            exp = expectations.get(pos, {"mean": val, "std": 1})

            deviation = abs(val - exp["mean"])
            if exp["std"] > 0 and deviation > threshold_std * exp["std"]:
                deviation_pct = (deviation / exp["mean"] * 100) if exp["mean"] != 0 else 0

                # Determine severity
                z_score = deviation / exp["std"]
                if z_score > 4:
                    severity = "critical"
                elif z_score > 3:
                    severity = "high"
                elif z_score > 2:
                    severity = "medium"
                else:
                    severity = "low"

                timestamp = timestamps[i] if timestamps and i < len(timestamps) else datetime.utcnow()

                anomalies.append(AnomalyContext(
                    anomaly_id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                    metric=pattern.metric,
                    equipment=pattern.equipment,
                    timestamp=timestamp,
                    value=val,
                    expected_value=exp["mean"],
                    expected_range_low=exp["mean"] - threshold_std * exp["std"],
                    expected_range_high=exp["mean"] + threshold_std * exp["std"],
                    deviation=deviation,
                    deviation_percent=deviation_pct,
                    anomaly_type="contextual",
                    severity=severity,
                    confidence=pattern.strength_score,
                    seasonal_context=f"Valeur inattendue à {self._format_time_label(pos, period, pattern.seasonality_type)}",
                    description=f"Valeur {val:.2f} vs attendu {exp['mean']:.2f} ({deviation_pct:+.1f}%)",
                ))

        return anomalies
