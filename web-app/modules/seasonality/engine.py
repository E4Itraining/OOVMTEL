"""
Seasonality Engine - Main engine for seasonality analysis
"""

import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .models import (
    SeasonalityType,
    PatternStrength,
    DecompositionResult,
    SeasonalPattern,
    SeasonalForecast,
    SeasonalityAnalysis,
    AnomalyContext,
    STANDARD_PERIODS,
)
from .stl_decomposer import STLDecomposer, MultiSeasonalSTL
from .pattern_detector import PatternDetector

logger = logging.getLogger(__name__)


class SeasonalityEngine:
    """
    Main Seasonality Analysis Engine.

    Features:
    - Automatic pattern detection
    - STL decomposition
    - Multi-seasonal support
    - Seasonal forecasting
    - Contextual anomaly detection
    - Industrial pattern templates
    """

    def __init__(
        self,
        auto_detect_periods: bool = True,
        default_periods: Optional[List[int]] = None,
        strength_threshold: float = 0.2,
        forecast_horizon_hours: int = 168,  # 7 days
    ):
        """
        Initialize Seasonality Engine.

        Args:
            auto_detect_periods: Automatically detect seasonal periods
            default_periods: Default periods to test if not auto-detecting
            strength_threshold: Minimum strength to report patterns
            forecast_horizon_hours: Default forecast horizon
        """
        self.auto_detect_periods = auto_detect_periods
        self.default_periods = default_periods or [24, 168, 720]
        self.strength_threshold = strength_threshold
        self.forecast_horizon_hours = forecast_horizon_hours

        self.pattern_detector = PatternDetector(
            strength_threshold=strength_threshold
        )

        logger.info("Seasonality Engine initialized")

    async def analyze(
        self,
        values: List[float],
        timestamps: Optional[List[datetime]] = None,
        metric: str = "metric",
        equipment: Optional[str] = None,
        periods: Optional[List[int]] = None,
        include_forecast: bool = True,
        detect_anomalies: bool = True,
    ) -> SeasonalityAnalysis:
        """
        Perform comprehensive seasonality analysis.

        Args:
            values: Time series values
            timestamps: Optional timestamps
            metric: Metric name
            equipment: Equipment identifier
            periods: Specific periods to analyze (None = auto-detect)
            include_forecast: Generate forecast
            detect_anomalies: Detect contextual anomalies

        Returns:
            Complete seasonality analysis
        """
        start_time = time.time()
        analysis_id = f"SA-{uuid.uuid4().hex[:8].upper()}"

        try:
            # 1. Detect patterns
            if self.auto_detect_periods and periods is None:
                patterns = self.pattern_detector.detect_patterns(
                    values, timestamps, metric, equipment
                )
                detected_periods = [p.period for p in patterns]
            else:
                detected_periods = periods or self.default_periods
                patterns = []
                for period in detected_periods:
                    p = self.pattern_detector.detect_patterns(values, timestamps, metric, equipment)
                    patterns.extend([pat for pat in p if pat.period == period])

            # 2. Perform STL decomposition
            if detected_periods:
                if len(detected_periods) == 1:
                    decomposer = STLDecomposer(seasonal_period=detected_periods[0])
                else:
                    decomposer = MultiSeasonalSTL(periods=detected_periods)

                decomposition = decomposer.decompose(values, timestamps, metric, equipment)
            else:
                decomposition = None

            # 3. Determine dominant pattern
            dominant_pattern = patterns[0] if patterns else None

            # 4. Generate forecast
            forecast = None
            if include_forecast and dominant_pattern:
                forecast = self._generate_forecast(
                    values, timestamps, patterns, decomposition
                )

            # 5. Detect contextual anomalies
            contextual_anomalies = []
            if detect_anomalies and dominant_pattern:
                contextual_anomalies = self.pattern_detector.detect_contextual_anomalies(
                    values, dominant_pattern, timestamps
                )

            # 6. Generate summary and recommendations
            has_seasonality = len(patterns) > 0 and any(
                p.strength_score >= self.strength_threshold for p in patterns
            )

            seasonality_types = list(set(p.seasonality_type for p in patterns))
            summary = self._generate_summary(patterns, decomposition, contextual_anomalies)
            recommendations = self._generate_recommendations(patterns, decomposition)

            return SeasonalityAnalysis(
                analysis_id=analysis_id,
                metric=metric,
                equipment=equipment,
                analyzed_at=datetime.utcnow(),
                analysis_duration_ms=(time.time() - start_time) * 1000,
                decomposition=decomposition,
                patterns=patterns,
                dominant_pattern=dominant_pattern,
                forecast=forecast,
                contextual_anomalies=contextual_anomalies,
                has_seasonality=has_seasonality,
                seasonality_types_detected=seasonality_types,
                summary=summary,
                recommendations=recommendations,
            )

        except Exception as e:
            logger.error(f"Seasonality analysis failed: {e}")
            return SeasonalityAnalysis(
                analysis_id=analysis_id,
                metric=metric,
                equipment=equipment,
                analyzed_at=datetime.utcnow(),
                analysis_duration_ms=(time.time() - start_time) * 1000,
                summary=f"Analyse échouée: {str(e)}",
            )

    def _generate_forecast(
        self,
        values: List[float],
        timestamps: Optional[List[datetime]],
        patterns: List[SeasonalPattern],
        decomposition: Optional[DecompositionResult],
    ) -> SeasonalForecast:
        """Generate seasonal forecast."""
        n = len(values)
        horizon = self.forecast_horizon_hours

        # Use decomposition if available
        if decomposition and decomposition.trend and decomposition.seasonal_components:
            trend_vals = decomposition.trend.values
            seasonal_vals = decomposition.seasonal_components[0].values if decomposition.seasonal_components else [0] * n

            # Project trend
            slope = decomposition.trend.slope
            last_trend = trend_vals[-1] if trend_vals else values[-1]

            # Generate forecast
            forecast_values = []
            trend_contribution = []
            seasonal_contribution = []

            for h in range(horizon):
                # Trend projection
                trend_val = last_trend + slope * h
                trend_contribution.append(trend_val)

                # Seasonal value (repeat pattern)
                period = decomposition.seasonal_components[0].period if decomposition.seasonal_components else 24
                seasonal_idx = (n + h) % period
                seasonal_val = seasonal_vals[seasonal_idx] if seasonal_idx < len(seasonal_vals) else 0
                seasonal_contribution.append(seasonal_val)

                forecast_values.append(trend_val + seasonal_val)

            # Confidence intervals (simplified)
            residual_std = decomposition.residual.std if decomposition.residual else 0
            confidence_lower = [v - 1.96 * residual_std for v in forecast_values]
            confidence_upper = [v + 1.96 * residual_std for v in forecast_values]

        else:
            # Simple forecast based on patterns
            if patterns:
                pattern = patterns[0]
                period = pattern.period
                mean_val = pattern.mean_value

                forecast_values = []
                for h in range(horizon):
                    # Repeat pattern
                    pos = (n + h) % period
                    # Interpolate between typical high and low
                    forecast_values.append(mean_val)

                trend_contribution = [mean_val] * horizon
                seasonal_contribution = [0] * horizon
                confidence_lower = [v * 0.9 for v in forecast_values]
                confidence_upper = [v * 1.1 for v in forecast_values]
            else:
                # Fallback to last value
                last_val = values[-1] if values else 0
                forecast_values = [last_val] * horizon
                trend_contribution = [last_val] * horizon
                seasonal_contribution = [0] * horizon
                confidence_lower = [last_val * 0.8] * horizon
                confidence_upper = [last_val * 1.2] * horizon

        # Generate timestamps
        forecast_timestamps = []
        if timestamps and len(timestamps) >= 2:
            last_ts = timestamps[-1]
            interval = timestamps[-1] - timestamps[-2]
            for h in range(horizon):
                forecast_timestamps.append(last_ts + interval * (h + 1))
        else:
            base_ts = datetime.utcnow()
            for h in range(horizon):
                forecast_timestamps.append(base_ts + timedelta(hours=h + 1))

        return SeasonalForecast(
            metric=patterns[0].metric if patterns else "metric",
            equipment=patterns[0].equipment if patterns else None,
            forecast_values=forecast_values,
            forecast_timestamps=forecast_timestamps,
            confidence_lower=confidence_lower,
            confidence_upper=confidence_upper,
            confidence_level=0.95,
            horizon_hours=horizon,
            horizon_description=f"Prévision sur {horizon // 24} jours",
            trend_contribution=trend_contribution,
            seasonal_contribution=seasonal_contribution,
        )

    def _generate_summary(
        self,
        patterns: List[SeasonalPattern],
        decomposition: Optional[DecompositionResult],
        anomalies: List[AnomalyContext],
    ) -> str:
        """Generate human-readable summary."""
        lines = ["## Analyse de Saisonnalité\n"]

        if not patterns:
            lines.append("Aucun pattern saisonnier significatif détecté.")
            return "\n".join(lines)

        # Pattern summary
        lines.append(f"**Patterns détectés:** {len(patterns)}\n")

        for i, pattern in enumerate(patterns[:3], 1):
            type_labels = {
                SeasonalityType.HOURLY: "Intra-journalier",
                SeasonalityType.DAILY: "Journalier",
                SeasonalityType.WEEKLY: "Hebdomadaire",
                SeasonalityType.MONTHLY: "Mensuel",
                SeasonalityType.YEARLY: "Annuel",
                SeasonalityType.CUSTOM: "Personnalisé",
            }
            type_label = type_labels.get(pattern.seasonality_type, "Autre")

            strength_labels = {
                PatternStrength.STRONG: "Fort",
                PatternStrength.MODERATE: "Modéré",
                PatternStrength.WEAK: "Faible",
                PatternStrength.NONE: "Aucun",
            }
            strength_label = strength_labels.get(pattern.strength, "Inconnu")

            lines.append(f"{i}. **{type_label}** ({strength_label})")
            lines.append(f"   - Période: {pattern.period} {pattern.period_unit}")
            lines.append(f"   - Amplitude: {pattern.amplitude_percent:.1f}%")
            lines.append(f"   - Pic: {pattern.peak_time}, Creux: {pattern.trough_time}")
            lines.append("")

        # Decomposition quality
        if decomposition:
            lines.append(f"**Qualité de décomposition:** {decomposition.decomposition_quality*100:.0f}%")
            lines.append(f"**Variance expliquée:** {decomposition.total_variance_explained:.0f}%\n")

            # Trend info
            if decomposition.trend:
                lines.append(f"**Tendance:** {decomposition.trend.direction}")
                if decomposition.trend.change_rate_per_day != 0:
                    lines.append(f"   - Variation: {decomposition.trend.change_rate_per_day:+.2f}/jour")

        # Anomalies
        if anomalies:
            critical = len([a for a in anomalies if a.severity == "critical"])
            high = len([a for a in anomalies if a.severity == "high"])
            lines.append(f"\n**Anomalies contextuelles:** {len(anomalies)}")
            if critical:
                lines.append(f"   - 🔴 Critiques: {critical}")
            if high:
                lines.append(f"   - 🟠 Hautes: {high}")

        return "\n".join(lines)

    def _generate_recommendations(
        self,
        patterns: List[SeasonalPattern],
        decomposition: Optional[DecompositionResult],
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if not patterns:
            recommendations.append(
                "Collecter plus de données pour détecter des patterns saisonniers"
            )
            return recommendations

        # Pattern-based recommendations
        dominant = patterns[0] if patterns else None

        if dominant:
            if dominant.seasonality_type == SeasonalityType.DAILY:
                recommendations.append(
                    f"Ajuster les seuils d'alertes selon l'heure: "
                    f"plus bas autour de {dominant.trough_time}, plus hauts autour de {dominant.peak_time}"
                )
            elif dominant.seasonality_type == SeasonalityType.WEEKLY:
                recommendations.append(
                    "Planifier les maintenances lors des périodes de basse activité identifiées"
                )

            if dominant.amplitude_percent > 30:
                recommendations.append(
                    f"Variation importante ({dominant.amplitude_percent:.0f}%): "
                    "considérer des seuils dynamiques basés sur la saisonnalité"
                )

        # Trend-based recommendations
        if decomposition and decomposition.trend:
            if decomposition.trend.direction == "increasing":
                recommendations.append(
                    "Tendance à la hausse détectée: surveiller l'approche des seuils critiques"
                )
            elif decomposition.trend.direction == "decreasing":
                recommendations.append(
                    "Tendance à la baisse détectée: investiguer les causes potentielles"
                )

        # Residual-based recommendations
        if decomposition and decomposition.residual:
            if decomposition.residual.outlier_percentage > 5:
                recommendations.append(
                    f"{decomposition.residual.outlier_percentage:.1f}% de valeurs aberrantes: "
                    "vérifier la qualité des données ou les conditions anormales"
                )

        return recommendations

    async def get_seasonal_baseline(
        self,
        metric: str,
        equipment: Optional[str],
        timestamp: datetime,
        patterns: List[SeasonalPattern],
    ) -> Dict[str, float]:
        """
        Get expected baseline value for a specific timestamp.

        Useful for real-time anomaly detection with seasonal context.
        """
        if not patterns:
            return {"expected": 0, "lower": 0, "upper": 0}

        dominant = patterns[0]
        period = dominant.period

        # Calculate position in period
        if dominant.seasonality_type == SeasonalityType.DAILY:
            position = timestamp.hour
        elif dominant.seasonality_type == SeasonalityType.WEEKLY:
            position = timestamp.weekday() * 24 + timestamp.hour
        else:
            position = 0

        position = position % period

        # Interpolate expected value
        # Simple linear interpolation between typical high and low
        cycle_progress = position / period
        expected = (
            dominant.typical_low +
            (dominant.typical_high - dominant.typical_low) * abs(0.5 - cycle_progress) * 2
        )

        margin = dominant.amplitude * 0.5  # 50% of amplitude as margin

        return {
            "expected": expected,
            "lower": expected - margin,
            "upper": expected + margin,
            "position_in_cycle": position,
            "cycle_progress_percent": cycle_progress * 100,
        }
