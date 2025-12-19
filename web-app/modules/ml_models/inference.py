"""
Inference Engine - Run predictions with pre-trained models
"""

import logging
import time
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from .models import (
    PretrainedModel,
    ModelPrediction,
    HealthScore,
    EquipmentType,
    ModelType,
    FailureMode,
    FAILURE_SIGNATURES,
    FEATURE_IMPORTANCE_TEMPLATES,
)
from .model_manager import ModelManager

logger = logging.getLogger(__name__)


class InferenceEngine:
    """
    Run inference with pre-trained models.

    Features:
    - Single model prediction
    - Ensemble prediction
    - Health score calculation
    - Feature contribution analysis
    """

    def __init__(self, model_manager: ModelManager):
        self._model_manager = model_manager

        # Simulated thresholds for demo
        self._anomaly_thresholds = {
            "pump": {"vibration": 8.0, "temperature": 85.0},
            "motor": {"current_imbalance": 5.0, "temperature": 100.0},
            "compressor": {"vibration": 10.0, "discharge_temperature": 150.0},
        }

        logger.info("Inference Engine initialized")

    def predict(
        self,
        model_id: str,
        input_values: Dict[str, float],
        equipment_id: Optional[str] = None,
    ) -> Optional[ModelPrediction]:
        """
        Run prediction with a single model.

        Args:
            model_id: Model to use
            input_values: Input feature values
            equipment_id: Optional equipment identifier

        Returns:
            Prediction result
        """
        model = self._model_manager.get_model(model_id)
        if not model:
            logger.error(f"Model not found: {model_id}")
            return None

        start_time = time.time()

        # Ensure model is loaded
        if not self._model_manager.is_loaded(model_id):
            self._model_manager.load_model(model_id)

        # Validate inputs
        validated_inputs = self._validate_inputs(model, input_values)

        # Run inference (simulated for demo)
        output_value, confidence, probabilities = self._run_inference(
            model, validated_inputs
        )

        # Interpret results
        prediction_label, explanation = self._interpret_result(
            model, output_value, validated_inputs
        )

        # Get feature contributions
        contributing_features = self._get_feature_contributions(
            model, validated_inputs
        )

        # Determine alert level
        is_anomaly, alert_level = self._determine_alert(
            model, output_value, confidence
        )

        prediction_time = (time.time() - start_time) * 1000

        prediction = ModelPrediction(
            model_id=model_id,
            model_name=model.name,
            input_values=validated_inputs,
            output_value=output_value,
            confidence=confidence,
            probabilities=probabilities,
            equipment_id=equipment_id,
            prediction_label=prediction_label,
            explanation=explanation,
            contributing_features=contributing_features,
            is_anomaly=is_anomaly,
            alert_level=alert_level,
        )

        # Record stats
        self._model_manager.record_prediction(model_id, prediction_time)

        return prediction

    def predict_ensemble(
        self,
        ensemble_id: str,
        input_values: Dict[str, float],
        equipment_id: Optional[str] = None,
    ) -> Optional[ModelPrediction]:
        """Run prediction with a model ensemble."""
        ensemble = self._model_manager.get_ensemble(ensemble_id)
        if not ensemble:
            logger.error(f"Ensemble not found: {ensemble_id}")
            return None

        # Get predictions from all models
        predictions = []
        weights = []

        for model_id in ensemble.model_ids:
            pred = self.predict(model_id, input_values, equipment_id)
            if pred:
                predictions.append(pred)
                weights.append(ensemble.weights.get(model_id, 1.0))

        if not predictions:
            return None

        # Aggregate based on method
        if ensemble.aggregation_method == "weighted_average":
            output_value = self._weighted_average(
                [p.output_value for p in predictions],
                weights
            )
            confidence = self._weighted_average(
                [p.confidence for p in predictions],
                weights
            )
        elif ensemble.aggregation_method == "voting":
            # Majority voting for classification
            labels = [p.prediction_label for p in predictions]
            output_value = max(set(labels), key=labels.count)
            confidence = labels.count(output_value) / len(labels)
        else:
            # Default to average
            output_value = sum(p.output_value for p in predictions) / len(predictions)
            confidence = sum(p.confidence for p in predictions) / len(predictions)

        # Aggregate anomaly detection
        is_anomaly = any(p.is_anomaly for p in predictions)
        alert_levels = {"none": 0, "info": 1, "warning": 2, "critical": 3}
        max_alert = max(alert_levels.get(p.alert_level, 0) for p in predictions)
        alert_level = ["none", "info", "warning", "critical"][max_alert]

        return ModelPrediction(
            model_id=ensemble.ensemble_id,
            model_name=ensemble.name,
            input_values=input_values,
            output_value=output_value,
            confidence=confidence,
            equipment_id=equipment_id,
            prediction_label=f"Ensemble: {len(predictions)} models",
            is_anomaly=is_anomaly,
            alert_level=alert_level,
        )

    def calculate_health_score(
        self,
        equipment_id: str,
        equipment_type: EquipmentType,
        sensor_data: Dict[str, float],
        historical_data: Optional[List[Dict[str, float]]] = None,
    ) -> HealthScore:
        """
        Calculate equipment health score.

        Args:
            equipment_id: Equipment identifier
            equipment_type: Type of equipment
            sensor_data: Current sensor readings
            historical_data: Optional historical data for trend

        Returns:
            Health score with components
        """
        # Find health index model
        models = self._model_manager.find_models_for_equipment(equipment_type)
        health_models = models.get("health_index", [])

        # Calculate component scores
        component_scores = self._calculate_component_scores(
            equipment_type, sensor_data
        )

        # Calculate overall score (weighted average)
        weights = {
            "vibration": 0.30,
            "temperature": 0.25,
            "electrical": 0.20,
            "efficiency": 0.15,
            "other": 0.10,
        }

        overall_score = 0.0
        total_weight = 0.0

        for component, score in component_scores.items():
            weight = weights.get(component, 0.10)
            overall_score += score * weight
            total_weight += weight

        if total_weight > 0:
            overall_score = overall_score / total_weight

        # Calculate trend
        trend, trend_slope = self._calculate_trend(historical_data)

        # Predict maintenance
        days_to_maintenance = self._estimate_maintenance_days(
            overall_score, trend_slope
        )

        # Failure probability
        failure_prob = self._calculate_failure_probability(
            overall_score, equipment_type, sensor_data
        )

        # Predicted failure modes
        failure_modes = self._predict_failure_modes(
            equipment_type, sensor_data, component_scores
        )

        # Recommendations
        recommendations = self._generate_recommendations(
            component_scores, failure_modes
        )

        return HealthScore(
            equipment_id=equipment_id,
            equipment_type=equipment_type,
            overall_score=round(overall_score, 1),
            component_scores=component_scores,
            trend=trend,
            trend_slope=round(trend_slope, 3),
            days_to_maintenance=days_to_maintenance,
            failure_probability_30d=round(failure_prob, 3),
            predicted_failure_modes=failure_modes,
            recommendations=recommendations,
        )

    def _validate_inputs(
        self,
        model: PretrainedModel,
        input_values: Dict[str, float]
    ) -> Dict[str, float]:
        """Validate and clean input values."""
        validated = {}

        for feature in model.input_features:
            name = feature.name
            value = input_values.get(name)

            if value is None:
                if feature.required:
                    value = feature.default_value or 0.0
                else:
                    continue

            # Apply bounds
            if feature.min_value is not None:
                value = max(value, feature.min_value)
            if feature.max_value is not None:
                value = min(value, feature.max_value)

            validated[name] = float(value)

        return validated

    def _run_inference(
        self,
        model: PretrainedModel,
        inputs: Dict[str, float]
    ) -> Tuple[float, float, Dict[str, float]]:
        """
        Run model inference.

        Note: This is a simulation. In production, this would run actual ML models.
        """
        # Simulate based on model type
        if model.model_type == ModelType.ANOMALY_DETECTION:
            # Calculate anomaly score based on deviation from normal
            anomaly_score = self._simulate_anomaly_score(model, inputs)
            confidence = 0.85 + random.uniform(-0.1, 0.1)
            probabilities = {
                "normal": 1 - anomaly_score,
                "anomaly": anomaly_score,
            }
            return anomaly_score, confidence, probabilities

        elif model.model_type == ModelType.REMAINING_USEFUL_LIFE:
            # Simulate RUL prediction
            rul_days = self._simulate_rul(model, inputs)
            confidence = 0.80 + random.uniform(-0.1, 0.1)
            return rul_days, confidence, {}

        elif model.model_type == ModelType.HEALTH_INDEX:
            # Simulate health index
            health = self._simulate_health_index(model, inputs)
            confidence = 0.88 + random.uniform(-0.08, 0.08)
            return health, confidence, {}

        elif model.model_type == ModelType.DEGRADATION:
            # Simulate degradation level
            level = self._simulate_degradation(model, inputs)
            confidence = 0.82 + random.uniform(-0.1, 0.1)
            probabilities = {
                "healthy": max(0, 1 - level),
                "slight_degradation": level * 0.4,
                "moderate_degradation": level * 0.4,
                "severe_degradation": level * 0.2,
            }
            return level, confidence, probabilities

        else:
            # Generic prediction
            return 0.5, 0.75, {}

    def _simulate_anomaly_score(
        self,
        model: PretrainedModel,
        inputs: Dict[str, float]
    ) -> float:
        """Simulate anomaly score calculation."""
        score = 0.0
        count = 0

        # Check each input against typical ranges
        for feature in model.input_features:
            value = inputs.get(feature.name, 0)
            if feature.max_value and feature.min_value:
                range_size = feature.max_value - feature.min_value
                mid = (feature.max_value + feature.min_value) / 2

                # Deviation from middle
                deviation = abs(value - mid) / (range_size / 2)
                score += min(deviation, 1.0)
                count += 1

        if count > 0:
            score = score / count

        # Add some randomness
        score = score * 0.8 + random.uniform(0, 0.2)

        return min(max(score, 0.0), 1.0)

    def _simulate_rul(
        self,
        model: PretrainedModel,
        inputs: Dict[str, float]
    ) -> float:
        """Simulate RUL prediction."""
        # Base RUL
        base_rul = 180  # days

        # Reduce based on degradation indicators
        vibration = inputs.get("vibration_rms", inputs.get("vibration", 0))
        temp = inputs.get("temperature", 0)
        hours = inputs.get("operating_hours", 0)

        # Vibration impact
        if vibration > 5:
            base_rul -= (vibration - 5) * 10

        # Temperature impact
        if temp > 70:
            base_rul -= (temp - 70) * 2

        # Operating hours impact
        if hours > 10000:
            base_rul -= (hours - 10000) / 100

        # Add noise
        base_rul += random.uniform(-10, 10)

        return max(base_rul, 7)

    def _simulate_health_index(
        self,
        model: PretrainedModel,
        inputs: Dict[str, float]
    ) -> float:
        """Simulate health index calculation."""
        score = 100.0

        # Deduct based on sensor values
        for name, value in inputs.items():
            if "vibration" in name.lower():
                if value > 5:
                    score -= (value - 5) * 5
            elif "temperature" in name.lower():
                if value > 70:
                    score -= (value - 70) * 0.5
            elif "imbalance" in name.lower():
                score -= value * 2

        # Add noise
        score += random.uniform(-3, 3)

        return max(min(score, 100), 0)

    def _simulate_degradation(
        self,
        model: PretrainedModel,
        inputs: Dict[str, float]
    ) -> float:
        """Simulate degradation level (0-1)."""
        level = 0.0

        for name, value in inputs.items():
            if "vibration" in name.lower():
                level += min(value / 20, 0.3)
            elif "temperature" in name.lower():
                if value > 80:
                    level += (value - 80) / 100
            elif "kurtosis" in name.lower():
                if value > 3:
                    level += (value - 3) * 0.1

        level += random.uniform(-0.05, 0.05)

        return max(min(level, 1.0), 0.0)

    def _interpret_result(
        self,
        model: PretrainedModel,
        output_value: float,
        inputs: Dict[str, float]
    ) -> Tuple[str, str]:
        """Interpret model output."""
        threshold = model.output_spec.threshold or 0.5

        if model.model_type == ModelType.ANOMALY_DETECTION:
            if output_value > threshold:
                label = "Anomalie détectée"
                explanation = f"Score d'anomalie: {output_value:.2f} (seuil: {threshold})"
            else:
                label = "Normal"
                explanation = f"Comportement normal (score: {output_value:.2f})"

        elif model.model_type == ModelType.REMAINING_USEFUL_LIFE:
            label = f"{int(output_value)} jours restants"
            if output_value < 30:
                explanation = "Maintenance urgente recommandée"
            elif output_value < 90:
                explanation = "Planifier la maintenance prochainement"
            else:
                explanation = "Équipement en bon état"

        elif model.model_type == ModelType.HEALTH_INDEX:
            if output_value >= 80:
                label = "Excellent"
            elif output_value >= 60:
                label = "Bon"
            elif output_value >= 40:
                label = "Attention requise"
            else:
                label = "Critique"
            explanation = f"Score de santé: {output_value:.1f}/100"

        elif model.model_type == ModelType.DEGRADATION:
            if output_value < 0.25:
                label = "Sain"
            elif output_value < 0.5:
                label = "Dégradation légère"
            elif output_value < 0.75:
                label = "Dégradation modérée"
            else:
                label = "Dégradation sévère"
            explanation = f"Niveau de dégradation: {output_value:.1%}"

        else:
            label = str(output_value)
            explanation = ""

        return label, explanation

    def _get_feature_contributions(
        self,
        model: PretrainedModel,
        inputs: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Get feature contribution to prediction."""
        contributions = []

        # Use template if available
        template_key = model.equipment_type.value
        importance = FEATURE_IMPORTANCE_TEMPLATES.get(template_key, {})

        for feature in model.input_features:
            name = feature.name
            value = inputs.get(name, 0)

            # Calculate contribution (simplified)
            weight = importance.get(name, 0.1)
            normalized_value = value

            if feature.max_value and feature.min_value:
                range_size = feature.max_value - feature.min_value
                if range_size > 0:
                    normalized_value = (value - feature.min_value) / range_size

            contribution = weight * normalized_value

            contributions.append({
                "feature": name,
                "value": value,
                "importance": weight,
                "contribution": round(contribution, 4),
            })

        # Sort by contribution
        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)

        return contributions[:5]

    def _determine_alert(
        self,
        model: PretrainedModel,
        output_value: float,
        confidence: float
    ) -> Tuple[bool, str]:
        """Determine if alert should be raised."""
        threshold = model.output_spec.threshold or 0.5

        if model.model_type == ModelType.ANOMALY_DETECTION:
            if output_value > threshold * 1.5:
                return True, "critical"
            elif output_value > threshold:
                return True, "warning"
            elif output_value > threshold * 0.8:
                return False, "info"
            return False, "none"

        elif model.model_type == ModelType.REMAINING_USEFUL_LIFE:
            if output_value < 14:
                return True, "critical"
            elif output_value < 30:
                return True, "warning"
            elif output_value < 60:
                return False, "info"
            return False, "none"

        elif model.model_type == ModelType.HEALTH_INDEX:
            if output_value < 40:
                return True, "critical"
            elif output_value < 60:
                return True, "warning"
            elif output_value < 80:
                return False, "info"
            return False, "none"

        return False, "none"

    def _weighted_average(
        self,
        values: List[float],
        weights: List[float]
    ) -> float:
        """Calculate weighted average."""
        if not values:
            return 0.0

        total = sum(v * w for v, w in zip(values, weights))
        weight_sum = sum(weights)

        return total / weight_sum if weight_sum > 0 else 0.0

    def _calculate_component_scores(
        self,
        equipment_type: EquipmentType,
        sensor_data: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate component health scores."""
        scores = {}

        # Vibration score
        vib = sensor_data.get("vibration", sensor_data.get("vibration_rms", 0))
        vib_score = max(0, 100 - vib * 10)
        scores["vibration"] = round(vib_score, 1)

        # Temperature score
        temp = sensor_data.get("temperature", sensor_data.get("temperature_bearing", 0))
        temp_score = 100 if temp < 60 else max(0, 100 - (temp - 60) * 2)
        scores["temperature"] = round(temp_score, 1)

        # Electrical score (for motors)
        if equipment_type in [EquipmentType.MOTOR, EquipmentType.PUMP]:
            current = sensor_data.get("current", 0)
            power_factor = sensor_data.get("power_factor", 0.9)
            elec_score = 100 * min(power_factor / 0.95, 1.0)
            scores["electrical"] = round(elec_score, 1)

        # Efficiency score
        efficiency = sensor_data.get("efficiency", 85)
        eff_score = min(100, efficiency * 1.1)
        scores["efficiency"] = round(eff_score, 1)

        return scores

    def _calculate_trend(
        self,
        historical_data: Optional[List[Dict[str, float]]]
    ) -> Tuple[str, float]:
        """Calculate health trend from historical data."""
        if not historical_data or len(historical_data) < 2:
            return "stable", 0.0

        # Simple linear regression on health scores
        n = len(historical_data)
        x = list(range(n))
        y = [d.get("health_score", 50) for d in historical_data]

        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable", 0.0

        slope = numerator / denominator

        if slope > 0.5:
            return "improving", slope
        elif slope < -0.5:
            return "degrading", slope
        else:
            return "stable", slope

    def _estimate_maintenance_days(
        self,
        health_score: float,
        trend_slope: float
    ) -> Optional[int]:
        """Estimate days until maintenance needed."""
        if health_score >= 80:
            return None  # No maintenance needed soon

        # Target score for maintenance
        maintenance_threshold = 40

        if trend_slope >= 0:
            # Not degrading, estimate based on current score
            if health_score > maintenance_threshold:
                return 90  # ~3 months
            else:
                return 14  # 2 weeks

        # Days to reach threshold
        score_to_drop = health_score - maintenance_threshold
        days = int(score_to_drop / abs(trend_slope))

        return max(7, min(days, 365))

    def _calculate_failure_probability(
        self,
        health_score: float,
        equipment_type: EquipmentType,
        sensor_data: Dict[str, float]
    ) -> float:
        """Calculate 30-day failure probability."""
        # Base probability from health score
        if health_score >= 80:
            base_prob = 0.01
        elif health_score >= 60:
            base_prob = 0.05
        elif health_score >= 40:
            base_prob = 0.15
        else:
            base_prob = 0.35

        # Adjust for specific indicators
        vib = sensor_data.get("vibration", 0)
        if vib > 10:
            base_prob += 0.1

        temp = sensor_data.get("temperature", 0)
        if temp > 90:
            base_prob += 0.1

        return min(base_prob, 0.95)

    def _predict_failure_modes(
        self,
        equipment_type: EquipmentType,
        sensor_data: Dict[str, float],
        component_scores: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Predict likely failure modes."""
        failure_modes = []

        # Check vibration-related failures
        vib_score = component_scores.get("vibration", 100)
        if vib_score < 70:
            failure_modes.append({
                "mode": FailureMode.BEARING_FAILURE.value,
                "probability": round((100 - vib_score) / 100, 2),
                "indicators": ["Vibration élevée"],
            })

        # Check temperature-related failures
        temp_score = component_scores.get("temperature", 100)
        if temp_score < 70:
            failure_modes.append({
                "mode": FailureMode.OVERHEATING.value,
                "probability": round((100 - temp_score) / 100, 2),
                "indicators": ["Température élevée"],
            })

        # Equipment-specific
        if equipment_type == EquipmentType.PUMP:
            flow = sensor_data.get("flow_rate", 0)
            pressure_diff = abs(
                sensor_data.get("pressure_outlet", 0) -
                sensor_data.get("pressure_inlet", 0)
            )
            if flow < 10 and pressure_diff > 5:
                failure_modes.append({
                    "mode": FailureMode.CAVITATION.value,
                    "probability": 0.4,
                    "indicators": ["Faible débit", "Différence de pression"],
                })

        # Sort by probability
        failure_modes.sort(key=lambda x: x["probability"], reverse=True)

        return failure_modes[:3]

    def _generate_recommendations(
        self,
        component_scores: Dict[str, float],
        failure_modes: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate maintenance recommendations."""
        recommendations = []

        # Based on component scores
        for component, score in component_scores.items():
            if score < 50:
                if component == "vibration":
                    recommendations.append(
                        "Vérifier l'alignement et l'équilibrage"
                    )
                    recommendations.append(
                        "Inspecter les roulements"
                    )
                elif component == "temperature":
                    recommendations.append(
                        "Vérifier le système de refroidissement"
                    )
                    recommendations.append(
                        "Contrôler la lubrification"
                    )
                elif component == "electrical":
                    recommendations.append(
                        "Vérifier les connexions électriques"
                    )
            elif score < 70:
                if component == "vibration":
                    recommendations.append(
                        "Planifier une analyse vibratoire détaillée"
                    )
                elif component == "temperature":
                    recommendations.append(
                        "Surveiller la température plus fréquemment"
                    )

        # Based on failure modes
        for fm in failure_modes:
            if fm["probability"] > 0.3:
                mode = fm["mode"]
                sig = FAILURE_SIGNATURES.get(FailureMode(mode), {})
                if sig.get("progression_days", 0) < 30:
                    recommendations.append(
                        f"Action urgente: risque de {mode}"
                    )

        # Deduplicate and limit
        seen = set()
        unique_recs = []
        for r in recommendations:
            if r not in seen:
                seen.add(r)
                unique_recs.append(r)

        return unique_recs[:5]
