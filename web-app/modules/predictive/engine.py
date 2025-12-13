"""
Predictive Engine - Main predictive maintenance engine
"""

import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .models import (
    AnomalyResult,
    TrendAnalysis,
    RULPrediction,
    FailurePrediction,
    MaintenanceRecommendation,
    EquipmentHealth,
    PredictiveAnalysis,
    TrendDirection,
    DEGRADATION_MODELS,
)
from .anomaly_detector import AnomalyDetector
from .forecaster import TimeSeriesForecaster
from .rul_estimator import RULEstimator

logger = logging.getLogger(__name__)


class PredictiveEngine:
    """
    Main Predictive Maintenance Engine.

    Features:
    - Multi-variate anomaly detection
    - Trend analysis and forecasting
    - Remaining Useful Life estimation
    - Failure probability prediction
    - Maintenance scheduling optimization
    """

    def __init__(
        self,
        victoria_metrics_url: str = "http://victoria-metrics:8428",
        anomaly_threshold: float = 2.5,
        prediction_horizon_hours: int = 168,  # 7 days
    ):
        self.victoria_metrics_url = victoria_metrics_url
        self.anomaly_threshold = anomaly_threshold
        self.prediction_horizon_hours = prediction_horizon_hours

        self.anomaly_detector = AnomalyDetector(threshold=anomaly_threshold)
        self.forecaster = TimeSeriesForecaster()
        self.rul_estimator = RULEstimator()

        # Cache for predictions
        self.prediction_cache: Dict[str, PredictiveAnalysis] = {}

        logger.info("Predictive Engine initialized")

    async def analyze(
        self,
        metrics_data: Dict[str, Any],
        equipment_filter: Optional[List[str]] = None
    ) -> PredictiveAnalysis:
        """
        Perform comprehensive predictive analysis.

        Args:
            metrics_data: Current metrics data
            equipment_filter: Optional list of equipment to analyze

        Returns:
            Complete predictive analysis
        """
        start_time = time.time()
        analysis_id = f"PA-{uuid.uuid4().hex[:8].upper()}"

        try:
            # 1. Extract equipment data
            equipment_list = self._extract_equipment(metrics_data, equipment_filter)

            # 2. Detect anomalies
            anomalies = self.anomaly_detector.detect_all(metrics_data)

            # 3. Analyze trends
            trends = self._analyze_trends(metrics_data)

            # 4. Estimate RUL for each equipment
            rul_predictions = []
            for equipment in equipment_list:
                rul = self.rul_estimator.estimate(equipment, metrics_data, anomalies, trends)
                if rul:
                    rul_predictions.append(rul)

            # 5. Calculate failure probabilities
            failure_predictions = self._calculate_failure_probabilities(
                equipment_list, anomalies, trends, rul_predictions
            )

            # 6. Generate maintenance recommendations
            maintenance_recommendations = self._generate_maintenance_recommendations(
                equipment_list, anomalies, trends, rul_predictions, failure_predictions
            )

            # 7. Calculate overall equipment health
            equipment_health = self._calculate_equipment_health(
                equipment_list, metrics_data, anomalies, trends,
                rul_predictions, failure_predictions, maintenance_recommendations
            )

            # 8. Generate alerts
            alerts = self._generate_alerts(anomalies, failure_predictions, rul_predictions)

            # 9. Generate summary
            summary = self._generate_summary(
                equipment_health, anomalies, failure_predictions, maintenance_recommendations
            )

            analysis = PredictiveAnalysis(
                analysis_id=analysis_id,
                analyzed_at=datetime.utcnow(),
                analysis_duration_ms=(time.time() - start_time) * 1000,
                equipment_health=equipment_health,
                anomalies=anomalies,
                trends=trends,
                rul_predictions=rul_predictions,
                failure_predictions=failure_predictions,
                maintenance_recommendations=maintenance_recommendations,
                summary=summary,
                alerts=alerts
            )

            # Cache the analysis
            self.prediction_cache[analysis_id] = analysis

            return analysis

        except Exception as e:
            logger.error(f"Error in predictive analysis: {e}")
            raise

    def _extract_equipment(
        self,
        metrics_data: Dict[str, Any],
        equipment_filter: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """Extract equipment list from metrics data."""
        equipment_list = []
        business = metrics_data.get("business", {})

        for eq in business.get("equipment", []):
            name = eq.get("name", "")

            # Apply filter if specified
            if equipment_filter and name not in equipment_filter:
                continue

            # Determine equipment type
            eq_type = "default"
            name_lower = name.lower()
            for type_name in DEGRADATION_MODELS.keys():
                if type_name in name_lower:
                    eq_type = type_name
                    break

            equipment_list.append({
                "name": name,
                "type": eq_type,
                "status": eq.get("status", "unknown"),
                "temperature": eq.get("temp", 0),
                "pressure": eq.get("pressure", 0),
                "power": eq.get("power", 0),
                "vibration": eq.get("vibration", 0),
            })

        return equipment_list

    def _analyze_trends(self, metrics_data: Dict[str, Any]) -> List[TrendAnalysis]:
        """Analyze trends in key metrics."""
        trends = []
        business = metrics_data.get("business", {})
        tech = metrics_data.get("tech", {})

        # Analyze business metrics
        business_metrics = ["oee", "quality_rate", "availability", "performance"]
        for metric in business_metrics:
            if metric in business:
                trend = self.forecaster.analyze_trend(
                    metric=metric,
                    current_value=business[metric],
                    historical_values=None  # Would use real historical data
                )
                if trend:
                    trends.append(trend)

        # Analyze tech metrics
        tech_metrics = ["cpu_usage", "memory_usage", "disk_usage"]
        for metric in tech_metrics:
            if metric in tech:
                trend = self.forecaster.analyze_trend(
                    metric=metric,
                    current_value=tech[metric],
                    historical_values=None
                )
                if trend:
                    trends.append(trend)

        # Analyze equipment metrics
        for eq in business.get("equipment", []):
            temp_trend = self.forecaster.analyze_trend(
                metric="temperature",
                current_value=eq.get("temp", 0),
                equipment=eq.get("name")
            )
            if temp_trend:
                trends.append(temp_trend)

        return trends

    def _calculate_failure_probabilities(
        self,
        equipment_list: List[Dict],
        anomalies: List[AnomalyResult],
        trends: List[TrendAnalysis],
        rul_predictions: List[RULPrediction]
    ) -> List[FailurePrediction]:
        """Calculate failure probabilities for each equipment."""
        predictions = []

        for equipment in equipment_list:
            name = equipment["name"]
            eq_type = equipment["type"]
            model = DEGRADATION_MODELS.get(eq_type, DEGRADATION_MODELS["default"])

            # Base failure probability from MTBF
            mtbf_hours = model["typical_mtbf_hours"]
            base_prob_24h = 24 / mtbf_hours

            # Adjust based on anomalies
            eq_anomalies = [a for a in anomalies if a.equipment == name]
            anomaly_factor = 1 + (len(eq_anomalies) * 0.2)

            # Adjust based on trends
            eq_trends = [t for t in trends if t.equipment == name]
            trend_factor = 1.0
            for trend in eq_trends:
                if trend.direction == TrendDirection.INCREASING and trend.is_concerning:
                    trend_factor += 0.3

            # Adjust based on RUL
            rul_factor = 1.0
            eq_rul = next((r for r in rul_predictions if r.equipment == name), None)
            if eq_rul:
                if eq_rul.rul_hours < 24:
                    rul_factor = 3.0
                elif eq_rul.rul_hours < 168:  # 7 days
                    rul_factor = 2.0
                elif eq_rul.rul_hours < 720:  # 30 days
                    rul_factor = 1.5

            # Calculate final probabilities
            prob_24h = min(base_prob_24h * anomaly_factor * trend_factor * rul_factor, 0.95)
            prob_7d = min(prob_24h * 5, 0.95)  # Simplified
            prob_30d = min(prob_7d * 3, 0.95)

            # Determine risk level
            if prob_24h > 0.5:
                risk_level = "critical"
            elif prob_24h > 0.2:
                risk_level = "high"
            elif prob_7d > 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"

            # Identify risk factors
            risk_factors = []
            warning_signs = []

            for anomaly in eq_anomalies:
                risk_factors.append(f"Anomaly: {anomaly.description}")

            for trend in eq_trends:
                if trend.is_concerning:
                    warning_signs.append(f"Concerning trend in {trend.metric}")

            if equipment["status"] == "warning":
                warning_signs.append("Equipment in warning state")

            predictions.append(FailurePrediction(
                equipment=name,
                failure_probability_24h=prob_24h,
                failure_probability_7d=prob_7d,
                failure_probability_30d=prob_30d,
                risk_level=risk_level,
                primary_risk_factors=risk_factors[:5],
                warning_signs=warning_signs[:5],
                historical_mtbf=mtbf_hours,
                similar_failures_count=len(eq_anomalies)
            ))

        return predictions

    def _generate_maintenance_recommendations(
        self,
        equipment_list: List[Dict],
        anomalies: List[AnomalyResult],
        trends: List[TrendAnalysis],
        rul_predictions: List[RULPrediction],
        failure_predictions: List[FailurePrediction]
    ) -> List[MaintenanceRecommendation]:
        """Generate maintenance recommendations."""
        recommendations = []
        now = datetime.utcnow()

        for equipment in equipment_list:
            name = equipment["name"]
            eq_type = equipment["type"]

            # Get failure prediction
            failure_pred = next(
                (f for f in failure_predictions if f.equipment == name),
                None
            )

            # Get RUL prediction
            rul_pred = next(
                (r for r in rul_predictions if r.equipment == name),
                None
            )

            # Get anomalies for this equipment
            eq_anomalies = [a for a in anomalies if a.equipment == name]

            # Generate recommendations based on conditions
            if failure_pred and failure_pred.risk_level in ["critical", "high"]:
                # Urgent maintenance needed
                recommendations.append(MaintenanceRecommendation(
                    id=f"MR-{uuid.uuid4().hex[:8].upper()}",
                    equipment=name,
                    recommendation_type="predictive",
                    priority=1 if failure_pred.risk_level == "critical" else 2,
                    title=f"Urgent inspection required for {name}",
                    description=f"High failure probability detected ({failure_pred.failure_probability_24h*100:.0f}% in 24h). Immediate inspection recommended.",
                    recommended_date=now + timedelta(hours=4),
                    deadline_date=now + timedelta(hours=24),
                    estimated_duration_hours=2,
                    required_skills=["equipment_specialist"],
                    risk_if_delayed="High risk of unplanned downtime",
                    based_on=failure_pred.primary_risk_factors
                ))

            elif rul_pred and rul_pred.rul_hours < 168:
                # Proactive maintenance before RUL ends
                recommendations.append(MaintenanceRecommendation(
                    id=f"MR-{uuid.uuid4().hex[:8].upper()}",
                    equipment=name,
                    recommendation_type="predictive",
                    priority=2,
                    title=f"Scheduled maintenance for {name}",
                    description=f"Estimated remaining life: {rul_pred.rul_hours:.0f} hours. Plan maintenance before failure.",
                    recommended_date=now + timedelta(hours=rul_pred.rul_hours * 0.5),
                    deadline_date=now + timedelta(hours=rul_pred.rul_hours * 0.8),
                    estimated_duration_hours=4,
                    required_parts=["spare_parts_kit"],
                    required_skills=["maintenance_technician"],
                    risk_if_delayed=f"Failure expected in {rul_pred.rul_days:.1f} days",
                    based_on=[f"RUL: {rul_pred.rul_hours:.0f}h", rul_pred.failure_mode]
                ))

            elif eq_anomalies:
                # Investigation needed for anomalies
                recommendations.append(MaintenanceRecommendation(
                    id=f"MR-{uuid.uuid4().hex[:8].upper()}",
                    equipment=name,
                    recommendation_type="corrective",
                    priority=3,
                    title=f"Investigate anomalies on {name}",
                    description=f"{len(eq_anomalies)} anomaly(ies) detected. Investigation recommended.",
                    recommended_date=now + timedelta(days=1),
                    estimated_duration_hours=1,
                    required_skills=["operator"],
                    risk_if_delayed="Anomalies may indicate developing issues",
                    based_on=[a.description for a in eq_anomalies[:3]]
                ))

            # Routine preventive maintenance
            if equipment["status"] == "running":
                recommendations.append(MaintenanceRecommendation(
                    id=f"MR-{uuid.uuid4().hex[:8].upper()}",
                    equipment=name,
                    recommendation_type="preventive",
                    priority=4,
                    title=f"Routine inspection for {name}",
                    description="Scheduled preventive maintenance inspection",
                    recommended_date=now + timedelta(days=7),
                    estimated_duration_hours=0.5,
                    required_skills=["operator"],
                    based_on=["Preventive maintenance schedule"]
                ))

        # Sort by priority
        recommendations.sort(key=lambda x: x.priority)

        return recommendations

    def _calculate_equipment_health(
        self,
        equipment_list: List[Dict],
        metrics_data: Dict[str, Any],
        anomalies: List[AnomalyResult],
        trends: List[TrendAnalysis],
        rul_predictions: List[RULPrediction],
        failure_predictions: List[FailurePrediction],
        maintenance_recommendations: List[MaintenanceRecommendation]
    ) -> List[EquipmentHealth]:
        """Calculate overall health score for each equipment."""
        health_scores = []
        business = metrics_data.get("business", {})

        for equipment in equipment_list:
            name = equipment["name"]

            # Base scores from metrics
            availability = business.get("availability", 90)
            performance = business.get("performance", 90)
            quality = business.get("quality_rate", 95)

            # Condition score based on sensor values
            condition_score = 100
            if equipment.get("temperature", 0) > 70:
                condition_score -= 20
            if equipment.get("vibration", 0) > 5:
                condition_score -= 15
            if equipment["status"] == "warning":
                condition_score -= 25

            # Adjust for anomalies
            eq_anomalies = [a for a in anomalies if a.equipment == name]
            condition_score -= len(eq_anomalies) * 5

            condition_score = max(condition_score, 0)

            # Calculate overall score (weighted average)
            overall_score = (
                availability * 0.25 +
                performance * 0.25 +
                quality * 0.25 +
                condition_score * 0.25
            )

            # Determine status
            if overall_score >= 85:
                status = "healthy"
                trend = TrendDirection.STABLE
            elif overall_score >= 70:
                status = "degrading"
                trend = TrendDirection.DECREASING
            else:
                status = "critical"
                trend = TrendDirection.DECREASING

            # Get related predictions
            rul = next((r for r in rul_predictions if r.equipment == name), None)
            failure = next((f for f in failure_predictions if f.equipment == name), None)
            recommendations = [r for r in maintenance_recommendations if r.equipment == name]

            # Active warnings
            warnings = []
            if failure and failure.risk_level in ["critical", "high"]:
                warnings.append(f"High failure risk: {failure.failure_probability_24h*100:.0f}%")
            for anomaly in eq_anomalies:
                warnings.append(anomaly.description)

            health_scores.append(EquipmentHealth(
                equipment=name,
                overall_score=overall_score,
                availability_score=availability,
                performance_score=performance,
                quality_score=quality,
                condition_score=condition_score,
                trend=trend,
                status=status,
                anomalies_count=len(eq_anomalies),
                active_warnings=warnings[:5],
                rul=rul,
                failure_prediction=failure,
                maintenance_recommendations=recommendations
            ))

        return health_scores

    def _generate_alerts(
        self,
        anomalies: List[AnomalyResult],
        failure_predictions: List[FailurePrediction],
        rul_predictions: List[RULPrediction]
    ) -> List[Dict[str, Any]]:
        """Generate alerts from predictions."""
        alerts = []

        # Critical anomalies
        for anomaly in anomalies:
            if anomaly.severity.value in ["critical", "high"]:
                alerts.append({
                    "type": "anomaly",
                    "severity": anomaly.severity.value,
                    "equipment": anomaly.equipment,
                    "message": anomaly.description,
                    "timestamp": anomaly.timestamp.isoformat()
                })

        # High failure risk
        for pred in failure_predictions:
            if pred.risk_level in ["critical", "high"]:
                alerts.append({
                    "type": "failure_risk",
                    "severity": pred.risk_level,
                    "equipment": pred.equipment,
                    "message": f"Failure probability: {pred.failure_probability_24h*100:.0f}% in 24h",
                    "timestamp": datetime.utcnow().isoformat()
                })

        # Low RUL
        for rul in rul_predictions:
            if rul.rul_hours < 48:
                alerts.append({
                    "type": "rul_warning",
                    "severity": "critical" if rul.rul_hours < 24 else "high",
                    "equipment": rul.equipment,
                    "message": f"Estimated remaining life: {rul.rul_hours:.0f} hours",
                    "timestamp": datetime.utcnow().isoformat()
                })

        return alerts

    def _generate_summary(
        self,
        equipment_health: List[EquipmentHealth],
        anomalies: List[AnomalyResult],
        failure_predictions: List[FailurePrediction],
        maintenance_recommendations: List[MaintenanceRecommendation]
    ) -> str:
        """Generate human-readable summary."""
        lines = ["## Analyse Prédictive - Résumé\n"]

        # Overall status
        healthy_count = len([e for e in equipment_health if e.status == "healthy"])
        degrading_count = len([e for e in equipment_health if e.status == "degrading"])
        critical_count = len([e for e in equipment_health if e.status == "critical"])

        lines.append(f"**Équipements analysés:** {len(equipment_health)}")
        lines.append(f"- 🟢 En bonne santé: {healthy_count}")
        lines.append(f"- 🟡 En dégradation: {degrading_count}")
        lines.append(f"- 🔴 Critiques: {critical_count}\n")

        # Anomalies
        if anomalies:
            critical_anomalies = len([a for a in anomalies if a.severity.value == "critical"])
            lines.append(f"**Anomalies détectées:** {len(anomalies)} ({critical_anomalies} critiques)\n")

        # High-risk equipment
        high_risk = [f for f in failure_predictions if f.risk_level in ["critical", "high"]]
        if high_risk:
            lines.append("**⚠️ Équipements à risque élevé:**")
            for pred in high_risk[:3]:
                lines.append(f"- {pred.equipment}: {pred.failure_probability_24h*100:.0f}% risque 24h")
            lines.append("")

        # Upcoming maintenance
        urgent = [r for r in maintenance_recommendations if r.priority <= 2]
        if urgent:
            lines.append(f"**🔧 Maintenances urgentes:** {len(urgent)}")
            for rec in urgent[:3]:
                lines.append(f"- {rec.title}")

        return "\n".join(lines)
