"""
Drift Detector - Data and Model Drift Detection

This module provides:
- Data drift detection (input distribution changes)
- Concept drift detection (relationship changes)
- Prediction drift detection (output distribution changes)
- Feature-level drift analysis
- Statistical significance testing
"""

import logging
import math
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional
import numpy as np

from .models import (
    DriftDetectionResult,
    DriftType,
    DriftSeverity,
    FeatureStore,
    AIObservabilityConfig,
)

logger = logging.getLogger(__name__)


class DriftDetector:
    """
    Detects data, concept, and model drift.

    Uses statistical methods to compare current data distributions
    with baseline/reference distributions.
    """

    def __init__(
        self,
        config: Optional[AIObservabilityConfig] = None,
        victoria_metrics_url: str = "http://victoria-metrics:8428",
    ):
        """Initialize the drift detector"""
        self.config = config or AIObservabilityConfig()
        self.vm_url = victoria_metrics_url

        # Feature store (baseline distributions)
        self._feature_store: dict[str, FeatureStore] = {}

        # Detection history
        self._drift_history: list[DriftDetectionResult] = []

        # Thresholds
        self.threshold_low = self.config.drift_threshold_low
        self.threshold_medium = self.config.drift_threshold_medium
        self.threshold_high = self.config.drift_threshold_high

        logger.info("DriftDetector initialized")

    async def initialize(self):
        """Initialize with default industrial features"""
        # Define common industrial features and their expected baselines
        industrial_features = [
            # SCADA features
            {"name": "temperature", "source": "scada", "unit": "celsius", "mean": 65.0, "std": 10.0},
            {"name": "pressure", "source": "scada", "unit": "bar", "mean": 3.5, "std": 0.5},
            {"name": "flow_rate", "source": "scada", "unit": "m3/h", "mean": 120.0, "std": 20.0},
            {"name": "vibration", "source": "scada", "unit": "mm/s", "mean": 2.5, "std": 0.8},
            {"name": "power_consumption", "source": "scada", "unit": "kW", "mean": 450.0, "std": 50.0},
            # MES features
            {"name": "cycle_time", "source": "mes", "unit": "seconds", "mean": 45.0, "std": 5.0},
            {"name": "oee", "source": "mes", "unit": "percent", "mean": 85.0, "std": 5.0},
            {"name": "quality_rate", "source": "mes", "unit": "percent", "mean": 98.0, "std": 1.0},
            {"name": "defect_rate", "source": "mes", "unit": "percent", "mean": 2.0, "std": 0.5},
        ]

        for feature in industrial_features:
            feature_id = f"{feature['source']}_{feature['name']}"
            self._feature_store[feature_id] = FeatureStore(
                feature_id=feature_id,
                name=feature["name"],
                description=f"{feature['name'].replace('_', ' ').title()} from {feature['source'].upper()}",
                source_system=feature["source"],
                source_metric=f"{feature['source']}_{feature['name']}_{feature['unit']}",
                baseline_mean=feature["mean"],
                baseline_std=feature["std"],
                baseline_min=feature["mean"] - 3 * feature["std"],
                baseline_max=feature["mean"] + 3 * feature["std"],
                current_mean=feature["mean"],
                current_std=feature["std"],
                data_type="float",
                unit=feature["unit"],
            )

        logger.info(f"DriftDetector initialized with {len(self._feature_store)} features")

    def calculate_psi(
        self,
        expected: list[float],
        actual: list[float],
        buckets: int = 10,
    ) -> float:
        """
        Calculate Population Stability Index (PSI).

        PSI measures how much a variable has shifted over time.

        Args:
            expected: Baseline/reference distribution
            actual: Current distribution
            buckets: Number of bins for bucketing

        Returns:
            PSI value (0 = no change, >0.25 = significant shift)
        """
        if len(expected) < 2 or len(actual) < 2:
            return 0.0

        # Create bucket boundaries from expected distribution
        breakpoints = np.percentile(expected, np.linspace(0, 100, buckets + 1))
        breakpoints = np.unique(breakpoints)

        # Calculate proportions in each bucket
        expected_counts, _ = np.histogram(expected, bins=breakpoints)
        actual_counts, _ = np.histogram(actual, bins=breakpoints)

        expected_props = expected_counts / len(expected)
        actual_props = actual_counts / len(actual)

        # Avoid division by zero
        expected_props = np.clip(expected_props, 0.0001, 1)
        actual_props = np.clip(actual_props, 0.0001, 1)

        # Calculate PSI
        psi = np.sum((actual_props - expected_props) * np.log(actual_props / expected_props))

        return float(psi)

    def calculate_kl_divergence(
        self,
        p: list[float],
        q: list[float],
        buckets: int = 10,
    ) -> float:
        """
        Calculate Kullback-Leibler divergence.

        Measures how one probability distribution differs from another.

        Args:
            p: Reference distribution
            q: Current distribution
            buckets: Number of bins

        Returns:
            KL divergence value
        """
        if len(p) < 2 or len(q) < 2:
            return 0.0

        # Create histograms
        min_val = min(min(p), min(q))
        max_val = max(max(p), max(q))
        bins = np.linspace(min_val, max_val, buckets + 1)

        p_hist, _ = np.histogram(p, bins=bins, density=True)
        q_hist, _ = np.histogram(q, bins=bins, density=True)

        # Avoid log(0)
        p_hist = np.clip(p_hist, 1e-10, None)
        q_hist = np.clip(q_hist, 1e-10, None)

        # Normalize
        p_hist = p_hist / p_hist.sum()
        q_hist = q_hist / q_hist.sum()

        # Calculate KL divergence
        kl_div = np.sum(p_hist * np.log(p_hist / q_hist))

        return float(kl_div)

    def calculate_wasserstein(
        self,
        distribution1: list[float],
        distribution2: list[float],
    ) -> float:
        """
        Calculate Wasserstein distance (Earth Mover's Distance).

        Measures the minimum "work" required to transform one distribution
        into another.

        Args:
            distribution1: First distribution
            distribution2: Second distribution

        Returns:
            Wasserstein distance
        """
        if len(distribution1) < 2 or len(distribution2) < 2:
            return 0.0

        sorted1 = np.sort(distribution1)
        sorted2 = np.sort(distribution2)

        # Interpolate to same length
        n = max(len(sorted1), len(sorted2))
        cdf1 = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(sorted1)), sorted1)
        cdf2 = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(sorted2)), sorted2)

        return float(np.mean(np.abs(cdf1 - cdf2)))

    def detect_drift_zscore(
        self,
        baseline_mean: float,
        baseline_std: float,
        current_values: list[float],
    ) -> tuple[float, DriftSeverity]:
        """
        Detect drift using Z-score analysis.

        Args:
            baseline_mean: Baseline mean
            baseline_std: Baseline standard deviation
            current_values: Current data points

        Returns:
            Tuple of (drift_score, severity)
        """
        if not current_values or baseline_std == 0:
            return 0.0, DriftSeverity.NONE

        current_mean = np.mean(current_values)
        z_score = abs(current_mean - baseline_mean) / baseline_std

        # Map z-score to drift severity
        if z_score < 1.0:
            severity = DriftSeverity.NONE
        elif z_score < 2.0:
            severity = DriftSeverity.LOW
        elif z_score < 3.0:
            severity = DriftSeverity.MEDIUM
        elif z_score < 4.0:
            severity = DriftSeverity.HIGH
        else:
            severity = DriftSeverity.CRITICAL

        # Normalize score to 0-1
        drift_score = min(z_score / 5.0, 1.0)

        return drift_score, severity

    async def detect_data_drift(
        self,
        model_id: str,
        feature_id: str,
        current_data: list[float],
        reference_data: Optional[list[float]] = None,
    ) -> DriftDetectionResult:
        """
        Detect data drift for a specific feature.

        Args:
            model_id: Model ID for context
            feature_id: Feature to analyze
            current_data: Current data points
            reference_data: Optional reference data (uses stored baseline if not provided)

        Returns:
            DriftDetectionResult with drift metrics
        """
        timestamp = datetime.now()

        # Get baseline from feature store
        feature = self._feature_store.get(feature_id)
        if feature and not reference_data:
            # Generate synthetic reference data from stored baseline
            np.random.seed(42)  # Reproducible for consistency
            reference_data = list(np.random.normal(
                feature.baseline_mean,
                feature.baseline_std,
                len(current_data) if current_data else 100,
            ))

        if not reference_data or not current_data:
            return DriftDetectionResult(
                model_id=model_id,
                timestamp=timestamp,
                drift_type=DriftType.DATA_DRIFT,
                severity=DriftSeverity.NONE,
                drift_score=0.0,
                recommendation="Insufficient data for drift detection",
            )

        # Calculate multiple drift metrics
        psi = self.calculate_psi(reference_data, current_data)
        kl_div = self.calculate_kl_divergence(reference_data, current_data)
        wasserstein = self.calculate_wasserstein(reference_data, current_data)

        # Use PSI as primary metric
        drift_score = psi

        # Determine severity based on PSI thresholds
        if psi < self.threshold_low:
            severity = DriftSeverity.NONE
        elif psi < self.threshold_medium:
            severity = DriftSeverity.LOW
        elif psi < self.threshold_high:
            severity = DriftSeverity.MEDIUM
        else:
            severity = DriftSeverity.HIGH if psi < 0.75 else DriftSeverity.CRITICAL

        # Build recommendation
        recommendations = []
        if severity == DriftSeverity.NONE:
            recommendation = "No significant drift detected. Continue monitoring."
        elif severity == DriftSeverity.LOW:
            recommendation = "Minor drift detected. Increase monitoring frequency."
            recommendations = ["Review recent data changes", "Check for seasonal patterns"]
        elif severity == DriftSeverity.MEDIUM:
            recommendation = "Significant drift detected. Investigate root cause."
            recommendations = ["Analyze feature distributions", "Consider model recalibration"]
        elif severity == DriftSeverity.HIGH:
            recommendation = "Critical drift detected. Model retraining recommended."
            recommendations = ["Retrain model with recent data", "Validate model performance"]
        else:
            recommendation = "Severe drift detected. Immediate action required."
            recommendations = ["Consider fallback model", "Urgent retraining needed"]

        result = DriftDetectionResult(
            model_id=model_id,
            timestamp=timestamp,
            drift_type=DriftType.DATA_DRIFT,
            severity=severity,
            drift_score=drift_score,
            statistical_distance=kl_div,
            affected_features=[feature_id],
            feature_drift_scores={feature_id: psi},
            recommendation=recommendation,
            requires_retraining=severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL],
            requires_immediate_action=severity == DriftSeverity.CRITICAL,
            details={
                "psi": round(psi, 4),
                "kl_divergence": round(kl_div, 4),
                "wasserstein_distance": round(wasserstein, 4),
                "current_mean": round(float(np.mean(current_data)), 4),
                "current_std": round(float(np.std(current_data)), 4),
                "reference_mean": round(float(np.mean(reference_data)), 4),
                "reference_std": round(float(np.std(reference_data)), 4),
                "sample_size": len(current_data),
                "recommendations": recommendations,
            },
        )

        self._drift_history.append(result)
        return result

    async def detect_prediction_drift(
        self,
        model_id: str,
        predictions_baseline: list[float],
        predictions_current: list[float],
    ) -> DriftDetectionResult:
        """
        Detect drift in model predictions.

        Args:
            model_id: Model ID
            predictions_baseline: Baseline predictions
            predictions_current: Current predictions

        Returns:
            DriftDetectionResult for prediction drift
        """
        timestamp = datetime.now()

        if not predictions_baseline or not predictions_current:
            return DriftDetectionResult(
                model_id=model_id,
                timestamp=timestamp,
                drift_type=DriftType.PREDICTION_DRIFT,
                severity=DriftSeverity.NONE,
                drift_score=0.0,
                recommendation="Insufficient prediction data",
            )

        # Calculate drift metrics
        psi = self.calculate_psi(predictions_baseline, predictions_current)
        wasserstein = self.calculate_wasserstein(predictions_baseline, predictions_current)

        # Normalize wasserstein by range
        pred_range = max(predictions_baseline) - min(predictions_baseline)
        normalized_wasserstein = wasserstein / pred_range if pred_range > 0 else 0

        # Combined score
        drift_score = (psi + normalized_wasserstein) / 2

        # Determine severity
        if drift_score < self.threshold_low:
            severity = DriftSeverity.NONE
        elif drift_score < self.threshold_medium:
            severity = DriftSeverity.LOW
        elif drift_score < self.threshold_high:
            severity = DriftSeverity.MEDIUM
        else:
            severity = DriftSeverity.HIGH

        return DriftDetectionResult(
            model_id=model_id,
            timestamp=timestamp,
            drift_type=DriftType.PREDICTION_DRIFT,
            severity=severity,
            drift_score=drift_score,
            statistical_distance=psi,
            recommendation=self._get_prediction_drift_recommendation(severity),
            requires_retraining=severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL],
            details={
                "psi": round(psi, 4),
                "wasserstein_normalized": round(normalized_wasserstein, 4),
                "baseline_mean": round(float(np.mean(predictions_baseline)), 4),
                "current_mean": round(float(np.mean(predictions_current)), 4),
            },
        )

    async def detect_multi_feature_drift(
        self,
        model_id: str,
        feature_data: dict[str, list[float]],
    ) -> DriftDetectionResult:
        """
        Detect drift across multiple features.

        Args:
            model_id: Model ID
            feature_data: Dict mapping feature_id to current data

        Returns:
            Aggregated DriftDetectionResult
        """
        timestamp = datetime.now()
        feature_drift_scores = {}
        affected_features = []
        max_severity = DriftSeverity.NONE

        for feature_id, current_data in feature_data.items():
            result = await self.detect_data_drift(model_id, feature_id, current_data)
            feature_drift_scores[feature_id] = result.drift_score

            if result.severity != DriftSeverity.NONE:
                affected_features.append(feature_id)

            if self._severity_to_int(result.severity) > self._severity_to_int(max_severity):
                max_severity = result.severity

        # Calculate aggregate drift score
        if feature_drift_scores:
            avg_drift = np.mean(list(feature_drift_scores.values()))
            max_drift = max(feature_drift_scores.values())
            # Weighted average favoring max drift
            drift_score = 0.6 * max_drift + 0.4 * avg_drift
        else:
            drift_score = 0.0

        return DriftDetectionResult(
            model_id=model_id,
            timestamp=timestamp,
            drift_type=DriftType.DATA_DRIFT,
            severity=max_severity,
            drift_score=drift_score,
            affected_features=affected_features,
            feature_drift_scores=feature_drift_scores,
            recommendation=f"{len(affected_features)} features showing drift",
            requires_retraining=max_severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL],
            details={
                "total_features": len(feature_data),
                "affected_features_count": len(affected_features),
                "avg_drift_score": round(float(np.mean(list(feature_drift_scores.values()))), 4) if feature_drift_scores else 0,
            },
        )

    def update_feature_baseline(
        self,
        feature_id: str,
        new_data: list[float],
    ):
        """Update feature baseline with new reference data"""
        if feature_id not in self._feature_store:
            return

        feature = self._feature_store[feature_id]
        feature.baseline_mean = float(np.mean(new_data))
        feature.baseline_std = float(np.std(new_data))
        feature.baseline_min = float(np.min(new_data))
        feature.baseline_max = float(np.max(new_data))
        feature.last_updated = datetime.now()

        logger.info(f"Updated baseline for feature {feature_id}")

    def get_drift_history(
        self,
        model_id: Optional[str] = None,
        hours: int = 24,
    ) -> list[DriftDetectionResult]:
        """Get drift detection history"""
        cutoff = datetime.now() - timedelta(hours=hours)
        results = [r for r in self._drift_history if r.timestamp >= cutoff]

        if model_id:
            results = [r for r in results if r.model_id == model_id]

        return results

    def get_feature_store(self) -> dict[str, FeatureStore]:
        """Get feature store with baselines"""
        return self._feature_store

    def get_drift_summary(self) -> dict:
        """Get summary of recent drift detection"""
        recent_results = self.get_drift_history(hours=24)

        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)
        affected_models = set()

        for result in recent_results:
            severity_counts[result.severity.value] += 1
            type_counts[result.drift_type.value] += 1
            if result.severity != DriftSeverity.NONE:
                affected_models.add(result.model_id)

        return {
            "total_checks": len(recent_results),
            "by_severity": dict(severity_counts),
            "by_type": dict(type_counts),
            "affected_models": list(affected_models),
            "features_monitored": len(self._feature_store),
            "critical_drifts": severity_counts.get("critical", 0),
            "high_drifts": severity_counts.get("high", 0),
            "requires_action": severity_counts.get("critical", 0) + severity_counts.get("high", 0),
        }

    def _severity_to_int(self, severity: DriftSeverity) -> int:
        """Convert severity to integer for comparison"""
        mapping = {
            DriftSeverity.NONE: 0,
            DriftSeverity.LOW: 1,
            DriftSeverity.MEDIUM: 2,
            DriftSeverity.HIGH: 3,
            DriftSeverity.CRITICAL: 4,
        }
        return mapping.get(severity, 0)

    def _get_prediction_drift_recommendation(self, severity: DriftSeverity) -> str:
        """Get recommendation based on prediction drift severity"""
        recommendations = {
            DriftSeverity.NONE: "Prediction distribution stable. No action needed.",
            DriftSeverity.LOW: "Minor prediction shift. Monitor for trend continuation.",
            DriftSeverity.MEDIUM: "Prediction drift detected. Validate model accuracy.",
            DriftSeverity.HIGH: "Significant prediction drift. Consider model update.",
            DriftSeverity.CRITICAL: "Critical prediction drift. Immediate model review required.",
        }
        return recommendations.get(severity, "Unknown severity")
