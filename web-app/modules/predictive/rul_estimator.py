"""
RUL Estimator - Estimates Remaining Useful Life for equipment
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .models import (
    RULPrediction,
    AnomalyResult,
    TrendAnalysis,
    TrendDirection,
    DEGRADATION_MODELS,
)


class RULEstimator:
    """
    Remaining Useful Life (RUL) estimator for industrial equipment.

    Uses multiple factors:
    - Equipment type and typical MTBF
    - Current condition (sensor values)
    - Anomaly count and severity
    - Degradation trends
    - Historical maintenance data
    """

    def __init__(self):
        self.degradation_models = DEGRADATION_MODELS

    def estimate(
        self,
        equipment: Dict[str, Any],
        metrics_data: Dict[str, Any],
        anomalies: List[AnomalyResult],
        trends: List[TrendAnalysis]
    ) -> Optional[RULPrediction]:
        """
        Estimate RUL for a piece of equipment.

        Args:
            equipment: Equipment info dict
            metrics_data: Current metrics data
            anomalies: Detected anomalies
            trends: Trend analysis results

        Returns:
            RUL prediction or None if cannot estimate
        """
        name = equipment.get("name", "Unknown")
        eq_type = equipment.get("type", "default")
        status = equipment.get("status", "unknown")

        # Get degradation model
        model = self.degradation_models.get(eq_type, self.degradation_models["default"])

        # Base RUL from MTBF
        base_mtbf_hours = model.get("typical_mtbf_hours", 8760)

        # Calculate health score (0-100)
        health_score = self._calculate_health_score(equipment, model, anomalies, trends)

        # Calculate degradation rate
        degradation_rate = self._calculate_degradation_rate(equipment, model, anomalies, trends)

        # Estimate RUL
        if degradation_rate > 0:
            # RUL = remaining health / degradation rate
            rul_hours = (health_score / 100) * base_mtbf_hours * (1 - degradation_rate)
        else:
            # No degradation detected, use health-adjusted MTBF
            rul_hours = (health_score / 100) * base_mtbf_hours

        # Apply minimum RUL for equipment in warning state
        if status == "warning":
            rul_hours = min(rul_hours, 168)  # Max 7 days

        # Stopped equipment
        if status == "stopped":
            rul_hours = 0

        # Calculate confidence interval (simplified)
        confidence_low = rul_hours * 0.7
        confidence_high = rul_hours * 1.3

        # Calculate confidence in prediction
        confidence = self._calculate_confidence(equipment, anomalies, trends)

        # Determine failure mode
        failure_mode = self._predict_failure_mode(equipment, model, anomalies, trends)

        # Key indicators
        key_indicators = self._get_key_indicators(equipment, anomalies, trends)

        # Recommended action
        recommended_action = self._get_recommended_action(rul_hours, health_score)

        # Predicted failure date
        predicted_failure_date = None
        if rul_hours > 0:
            predicted_failure_date = datetime.utcnow() + timedelta(hours=rul_hours)

        return RULPrediction(
            equipment=name,
            component=None,  # Could be specific component
            rul_hours=max(0, rul_hours),
            rul_days=max(0, rul_hours / 24),
            confidence_interval_low=max(0, confidence_low),
            confidence_interval_high=max(0, confidence_high),
            confidence=confidence,
            health_score=health_score,
            degradation_rate=degradation_rate,
            failure_mode=failure_mode,
            key_indicators=key_indicators,
            recommended_action=recommended_action,
            predicted_failure_date=predicted_failure_date
        )

    def _calculate_health_score(
        self,
        equipment: Dict[str, Any],
        model: Dict[str, Any],
        anomalies: List[AnomalyResult],
        trends: List[TrendAnalysis]
    ) -> float:
        """Calculate equipment health score (0-100)."""
        score = 100.0
        name = equipment.get("name", "")

        # Deduct for status
        status = equipment.get("status", "running")
        if status == "warning":
            score -= 20
        elif status == "stopped":
            score -= 50

        # Deduct for sensor values exceeding thresholds
        indicators = model.get("degradation_indicators", {})

        # Temperature
        temp = equipment.get("temperature", 0)
        if "temperature" in indicators:
            thresholds = indicators["temperature"]
            if temp >= thresholds.get("critical", 90):
                score -= 30
            elif temp >= thresholds.get("warning", 70):
                score -= 15

        # Vibration
        vibration = equipment.get("vibration", 0)
        if "vibration" in indicators and vibration > 0:
            thresholds = indicators["vibration"]
            if vibration >= thresholds.get("critical", 10):
                score -= 30
            elif vibration >= thresholds.get("warning", 5):
                score -= 15

        # Deduct for anomalies
        eq_anomalies = [a for a in anomalies if a.equipment == name]
        for anomaly in eq_anomalies:
            if anomaly.severity.value == "critical":
                score -= 15
            elif anomaly.severity.value == "high":
                score -= 10
            else:
                score -= 5

        # Deduct for concerning trends
        eq_trends = [t for t in trends if t.equipment == name]
        for trend in eq_trends:
            if trend.is_concerning:
                score -= 10
            elif trend.direction == TrendDirection.DECREASING:
                score -= 5

        return max(0, min(100, score))

    def _calculate_degradation_rate(
        self,
        equipment: Dict[str, Any],
        model: Dict[str, Any],
        anomalies: List[AnomalyResult],
        trends: List[TrendAnalysis]
    ) -> float:
        """Calculate degradation rate (0-1, where 1 = critical degradation)."""
        rate = 0.0
        name = equipment.get("name", "")

        # Base rate from status
        status = equipment.get("status", "running")
        if status == "warning":
            rate += 0.3
        elif status == "stopped":
            rate += 0.8

        # Rate from anomaly severity
        eq_anomalies = [a for a in anomalies if a.equipment == name]
        for anomaly in eq_anomalies:
            if anomaly.severity.value == "critical":
                rate += 0.2
            elif anomaly.severity.value == "high":
                rate += 0.1
            else:
                rate += 0.05

        # Rate from trends
        eq_trends = [t for t in trends if t.equipment == name]
        for trend in eq_trends:
            if trend.is_concerning:
                rate += 0.15
            elif trend.direction in [TrendDirection.INCREASING, TrendDirection.DECREASING]:
                rate += 0.05

        return min(1.0, rate)

    def _calculate_confidence(
        self,
        equipment: Dict[str, Any],
        anomalies: List[AnomalyResult],
        trends: List[TrendAnalysis]
    ) -> float:
        """Calculate confidence in RUL prediction."""
        confidence = 0.5  # Base confidence

        name = equipment.get("name", "")

        # More data = higher confidence
        eq_anomalies = [a for a in anomalies if a.equipment == name]
        eq_trends = [t for t in trends if t.equipment == name]

        # Having anomaly data increases confidence
        if eq_anomalies:
            confidence += 0.1

        # Having trend data increases confidence
        if eq_trends:
            confidence += 0.1
            # High R-squared in trends = higher confidence
            avg_r2 = sum(t.r_squared for t in eq_trends) / len(eq_trends)
            confidence += avg_r2 * 0.2

        # Equipment with consistent status has higher confidence
        if equipment.get("status") == "running":
            confidence += 0.1

        return min(0.95, confidence)

    def _predict_failure_mode(
        self,
        equipment: Dict[str, Any],
        model: Dict[str, Any],
        anomalies: List[AnomalyResult],
        trends: List[TrendAnalysis]
    ) -> str:
        """Predict most likely failure mode."""
        name = equipment.get("name", "")
        failure_modes = model.get("failure_modes", ["general_failure"])

        # Check anomalies for hints
        eq_anomalies = [a for a in anomalies if a.equipment == name]

        for anomaly in eq_anomalies:
            metric = anomaly.metric.lower()

            if "temperature" in metric and "overheat" in failure_modes:
                return "overheat"
            if "vibration" in metric:
                if "bearing_failure" in failure_modes:
                    return "bearing_failure"
                if "bearing_wear" in failure_modes:
                    return "bearing_wear"
            if "pressure" in metric and "seal_leak" in failure_modes:
                return "seal_leak"

        # Default to first failure mode
        return failure_modes[0] if failure_modes else "unknown"

    def _get_key_indicators(
        self,
        equipment: Dict[str, Any],
        anomalies: List[AnomalyResult],
        trends: List[TrendAnalysis]
    ) -> List[str]:
        """Get key indicators affecting RUL."""
        indicators = []
        name = equipment.get("name", "")

        # Status
        status = equipment.get("status", "running")
        if status != "running":
            indicators.append(f"Status: {status}")

        # Sensor values
        temp = equipment.get("temperature", 0)
        if temp > 60:
            indicators.append(f"Temperature: {temp}°C")

        vibration = equipment.get("vibration", 0)
        if vibration > 3:
            indicators.append(f"Vibration: {vibration} mm/s")

        # Anomalies
        eq_anomalies = [a for a in anomalies if a.equipment == name]
        if eq_anomalies:
            indicators.append(f"{len(eq_anomalies)} anomalies detected")

        # Trends
        eq_trends = [t for t in trends if t.equipment == name and t.is_concerning]
        if eq_trends:
            indicators.append(f"{len(eq_trends)} concerning trends")

        return indicators[:5]

    def _get_recommended_action(self, rul_hours: float, health_score: float) -> str:
        """Get recommended action based on RUL and health."""
        if rul_hours <= 0:
            return "Immediate maintenance required - equipment at end of life"
        elif rul_hours < 24:
            return "Critical: Schedule maintenance within 24 hours"
        elif rul_hours < 168:
            return "Schedule preventive maintenance within this week"
        elif health_score < 50:
            return "Plan comprehensive inspection"
        elif health_score < 75:
            return "Monitor closely, consider early maintenance"
        else:
            return "Continue normal operation with routine monitoring"

    def batch_estimate(
        self,
        equipment_list: List[Dict[str, Any]],
        metrics_data: Dict[str, Any],
        anomalies: List[AnomalyResult],
        trends: List[TrendAnalysis]
    ) -> List[RULPrediction]:
        """Estimate RUL for multiple equipment."""
        predictions = []

        for equipment in equipment_list:
            prediction = self.estimate(equipment, metrics_data, anomalies, trends)
            if prediction:
                predictions.append(prediction)

        # Sort by RUL (most urgent first)
        predictions.sort(key=lambda x: x.rul_hours)

        return predictions
