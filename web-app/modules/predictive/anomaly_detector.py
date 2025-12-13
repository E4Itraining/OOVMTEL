"""
Anomaly Detector - Detects anomalies in industrial metrics
"""

import uuid
import math
from datetime import datetime
from typing import Dict, List, Any, Optional

from .models import (
    AnomalyResult,
    AnomalyType,
    AnomalySeverity,
    DEGRADATION_MODELS,
)


class AnomalyDetector:
    """
    Multi-variate anomaly detection for industrial metrics.

    Methods:
    - Z-score based detection
    - IQR-based detection
    - Threshold-based detection (using domain knowledge)
    - Correlation-based detection (multivariate)
    """

    def __init__(self, threshold: float = 2.5):
        self.threshold = threshold  # Z-score threshold for anomaly

    def detect_all(self, metrics_data: Dict[str, Any]) -> List[AnomalyResult]:
        """Detect anomalies in all metrics."""
        anomalies = []

        # Detect business metric anomalies
        anomalies.extend(self._detect_business_anomalies(metrics_data))

        # Detect tech metric anomalies
        anomalies.extend(self._detect_tech_anomalies(metrics_data))

        # Detect equipment anomalies
        anomalies.extend(self._detect_equipment_anomalies(metrics_data))

        # Detect correlated anomalies (multivariate)
        anomalies = self._detect_correlated_anomalies(anomalies)

        return anomalies

    def _detect_business_anomalies(self, metrics_data: Dict[str, Any]) -> List[AnomalyResult]:
        """Detect anomalies in business metrics."""
        anomalies = []
        business = metrics_data.get("business", {})

        # OEE anomaly detection
        oee = business.get("oee", 0)
        if oee > 0:
            anomaly = self._check_threshold_anomaly(
                metric="oee",
                value=oee,
                expected=85,
                lower_warning=75,
                lower_critical=65,
                unit="%"
            )
            if anomaly:
                anomalies.append(anomaly)

        # Quality rate anomaly
        quality = business.get("quality_rate", 0)
        if quality > 0:
            anomaly = self._check_threshold_anomaly(
                metric="quality_rate",
                value=quality,
                expected=98,
                lower_warning=95,
                lower_critical=90,
                unit="%"
            )
            if anomaly:
                anomalies.append(anomaly)

        # Defects anomaly
        defects = business.get("defects_today", 0)
        anomaly = self._check_threshold_anomaly(
            metric="defects",
            value=defects,
            expected=5,
            upper_warning=10,
            upper_critical=20,
            unit=" units"
        )
        if anomaly:
            anomalies.append(anomaly)

        return anomalies

    def _detect_tech_anomalies(self, metrics_data: Dict[str, Any]) -> List[AnomalyResult]:
        """Detect anomalies in tech metrics."""
        anomalies = []
        tech = metrics_data.get("tech", {})

        # CPU anomaly
        cpu = tech.get("cpu_usage", 0)
        anomaly = self._check_threshold_anomaly(
            metric="cpu_usage",
            value=cpu,
            expected=40,
            upper_warning=80,
            upper_critical=95,
            unit="%"
        )
        if anomaly:
            anomalies.append(anomaly)

        # Memory anomaly
        memory = tech.get("memory_usage", 0)
        anomaly = self._check_threshold_anomaly(
            metric="memory_usage",
            value=memory,
            expected=60,
            upper_warning=85,
            upper_critical=95,
            unit="%"
        )
        if anomaly:
            anomalies.append(anomaly)

        # Disk anomaly
        disk = tech.get("disk_usage", 0)
        anomaly = self._check_threshold_anomaly(
            metric="disk_usage",
            value=disk,
            expected=50,
            upper_warning=80,
            upper_critical=90,
            unit="%"
        )
        if anomaly:
            anomalies.append(anomaly)

        # Error rate anomaly
        error_rate = tech.get("error_rate", 0)
        anomaly = self._check_threshold_anomaly(
            metric="error_rate",
            value=error_rate * 100,  # Convert to percentage
            expected=0.5,
            upper_warning=2,
            upper_critical=5,
            unit="%"
        )
        if anomaly:
            anomalies.append(anomaly)

        return anomalies

    def _detect_equipment_anomalies(self, metrics_data: Dict[str, Any]) -> List[AnomalyResult]:
        """Detect anomalies in equipment metrics."""
        anomalies = []
        business = metrics_data.get("business", {})

        for equipment in business.get("equipment", []):
            name = equipment.get("name", "Unknown")
            status = equipment.get("status", "unknown")

            # Determine equipment type
            eq_type = "default"
            name_lower = name.lower()
            for type_name in DEGRADATION_MODELS.keys():
                if type_name in name_lower:
                    eq_type = type_name
                    break

            model = DEGRADATION_MODELS.get(eq_type, DEGRADATION_MODELS["default"])
            indicators = model.get("degradation_indicators", {})

            # Check temperature
            temp = equipment.get("temp", 0)
            if "temperature" in indicators:
                thresholds = indicators["temperature"]
                anomaly = self._check_threshold_anomaly(
                    metric="temperature",
                    value=temp,
                    expected=50,
                    upper_warning=thresholds.get("warning", 70),
                    upper_critical=thresholds.get("critical", 90),
                    unit="°C",
                    equipment=name
                )
                if anomaly:
                    anomalies.append(anomaly)

            # Check vibration
            vibration = equipment.get("vibration", 0)
            if "vibration" in indicators and vibration > 0:
                thresholds = indicators["vibration"]
                anomaly = self._check_threshold_anomaly(
                    metric="vibration",
                    value=vibration,
                    expected=2,
                    upper_warning=thresholds.get("warning", 5),
                    upper_critical=thresholds.get("critical", 10),
                    unit=" mm/s",
                    equipment=name
                )
                if anomaly:
                    anomalies.append(anomaly)

            # Check pressure
            pressure = equipment.get("pressure", 0)
            if pressure > 0:
                anomaly = self._check_threshold_anomaly(
                    metric="pressure",
                    value=pressure,
                    expected=4,
                    upper_warning=7,
                    upper_critical=9,
                    lower_warning=2,
                    lower_critical=1,
                    unit=" bar",
                    equipment=name
                )
                if anomaly:
                    anomalies.append(anomaly)

            # Equipment in warning state
            if status == "warning":
                anomalies.append(AnomalyResult(
                    id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                    metric="equipment_status",
                    equipment=name,
                    anomaly_type=AnomalyType.POINT,
                    severity=AnomalySeverity.MEDIUM,
                    timestamp=datetime.utcnow(),
                    value=1,
                    expected_value=0,
                    deviation_score=2.0,
                    confidence=0.9,
                    description=f"Equipment {name} is in warning state"
                ))

            # Equipment stopped unexpectedly
            if status == "stopped" and "tank" not in name_lower:
                anomalies.append(AnomalyResult(
                    id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                    metric="equipment_status",
                    equipment=name,
                    anomaly_type=AnomalyType.POINT,
                    severity=AnomalySeverity.HIGH,
                    timestamp=datetime.utcnow(),
                    value=0,
                    expected_value=1,
                    deviation_score=3.0,
                    confidence=0.95,
                    description=f"Equipment {name} is stopped"
                ))

        return anomalies

    def _check_threshold_anomaly(
        self,
        metric: str,
        value: float,
        expected: float,
        upper_warning: Optional[float] = None,
        upper_critical: Optional[float] = None,
        lower_warning: Optional[float] = None,
        lower_critical: Optional[float] = None,
        unit: str = "",
        equipment: Optional[str] = None
    ) -> Optional[AnomalyResult]:
        """Check if value exceeds thresholds."""

        # Check critical upper
        if upper_critical and value >= upper_critical:
            deviation = (value - expected) / expected if expected != 0 else value
            return AnomalyResult(
                id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                metric=metric,
                equipment=equipment,
                anomaly_type=AnomalyType.POINT,
                severity=AnomalySeverity.CRITICAL,
                timestamp=datetime.utcnow(),
                value=value,
                expected_value=expected,
                deviation_score=abs(deviation) * 2,
                confidence=0.95,
                description=f"Critical: {metric.replace('_', ' ')} at {value}{unit} (threshold: {upper_critical}{unit})"
            )

        # Check warning upper
        if upper_warning and value >= upper_warning:
            deviation = (value - expected) / expected if expected != 0 else value
            return AnomalyResult(
                id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                metric=metric,
                equipment=equipment,
                anomaly_type=AnomalyType.POINT,
                severity=AnomalySeverity.MEDIUM,
                timestamp=datetime.utcnow(),
                value=value,
                expected_value=expected,
                deviation_score=abs(deviation),
                confidence=0.85,
                description=f"Warning: {metric.replace('_', ' ')} at {value}{unit} (threshold: {upper_warning}{unit})"
            )

        # Check critical lower
        if lower_critical and value <= lower_critical:
            deviation = (expected - value) / expected if expected != 0 else -value
            return AnomalyResult(
                id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                metric=metric,
                equipment=equipment,
                anomaly_type=AnomalyType.POINT,
                severity=AnomalySeverity.CRITICAL,
                timestamp=datetime.utcnow(),
                value=value,
                expected_value=expected,
                deviation_score=abs(deviation) * 2,
                confidence=0.95,
                description=f"Critical: {metric.replace('_', ' ')} at {value}{unit} (min: {lower_critical}{unit})"
            )

        # Check warning lower
        if lower_warning and value <= lower_warning:
            deviation = (expected - value) / expected if expected != 0 else -value
            return AnomalyResult(
                id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                metric=metric,
                equipment=equipment,
                anomaly_type=AnomalyType.POINT,
                severity=AnomalySeverity.MEDIUM,
                timestamp=datetime.utcnow(),
                value=value,
                expected_value=expected,
                deviation_score=abs(deviation),
                confidence=0.85,
                description=f"Warning: {metric.replace('_', ' ')} at {value}{unit} (min: {lower_warning}{unit})"
            )

        return None

    def _detect_correlated_anomalies(
        self,
        anomalies: List[AnomalyResult]
    ) -> List[AnomalyResult]:
        """Detect correlations between anomalies (multivariate patterns)."""

        # Group by equipment
        by_equipment: Dict[str, List[AnomalyResult]] = {}
        for anomaly in anomalies:
            eq = anomaly.equipment or "system"
            if eq not in by_equipment:
                by_equipment[eq] = []
            by_equipment[eq].append(anomaly)

        # Mark correlated anomalies
        for equipment, eq_anomalies in by_equipment.items():
            if len(eq_anomalies) > 1:
                # Multiple anomalies on same equipment = likely correlated
                ids = [a.id for a in eq_anomalies]
                for anomaly in eq_anomalies:
                    anomaly.is_correlated = True
                    anomaly.related_anomalies = [id for id in ids if id != anomaly.id]

                    # Add contributing factors
                    anomaly.contributing_factors = [
                        f"Correlated with {len(ids) - 1} other anomalies on {equipment}"
                    ]

        # Detect known multivariate patterns
        known_patterns = [
            {
                "metrics": ["temperature", "vibration"],
                "pattern": "bearing_degradation",
                "severity_boost": 1
            },
            {
                "metrics": ["cpu_usage", "memory_usage"],
                "pattern": "resource_exhaustion",
                "severity_boost": 1
            },
            {
                "metrics": ["oee", "quality_rate"],
                "pattern": "production_issue",
                "severity_boost": 0
            }
        ]

        for equipment, eq_anomalies in by_equipment.items():
            metrics_with_anomalies = {a.metric for a in eq_anomalies}

            for pattern in known_patterns:
                pattern_metrics = set(pattern["metrics"])
                if pattern_metrics.issubset(metrics_with_anomalies):
                    # Pattern matched
                    for anomaly in eq_anomalies:
                        if anomaly.metric in pattern_metrics:
                            anomaly.contributing_factors.append(
                                f"Part of {pattern['pattern']} pattern"
                            )

        return anomalies

    def detect_z_score_anomaly(
        self,
        values: List[float],
        current_value: float
    ) -> Optional[float]:
        """Calculate Z-score for current value."""
        if not values or len(values) < 3:
            return None

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std = math.sqrt(variance) if variance > 0 else 1

        z_score = (current_value - mean) / std

        if abs(z_score) >= self.threshold:
            return z_score

        return None
