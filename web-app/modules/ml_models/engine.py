"""
ML Models Engine - Main engine for pre-trained ML models
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from .models import (
    PretrainedModel,
    ModelPrediction,
    ModelEnsemble,
    HealthScore,
    TrainingConfig,
    EquipmentType,
    ModelType,
    ModelStatus,
    FailureMode,
    PRETRAINED_MODEL_CATALOG,
)
from .model_manager import ModelManager
from .inference import InferenceEngine

logger = logging.getLogger(__name__)


class MLModelsEngine:
    """
    Main ML Models Engine for SYNAPSIX.

    Features:
    - Pre-trained model library by equipment type
    - Anomaly detection
    - Remaining useful life prediction
    - Health index calculation
    - Model ensemble support
    """

    def __init__(self):
        self._model_manager = ModelManager()
        self._inference_engine = InferenceEngine(self._model_manager)

        logger.info("ML Models Engine initialized")

    # Model discovery

    def get_available_models(
        self,
        equipment_type: Optional[EquipmentType] = None,
        model_type: Optional[ModelType] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get available pre-trained models.

        Args:
            equipment_type: Filter by equipment type
            model_type: Filter by model type

        Returns:
            List of model summaries
        """
        models = self._model_manager.list_models(
            equipment_type=equipment_type,
            model_type=model_type,
            status=ModelStatus.READY,
        )

        return [
            {
                "model_id": m.model_id,
                "name": m.name,
                "description": m.description,
                "equipment_type": m.equipment_type.value,
                "model_type": m.model_type.value,
                "algorithm": m.algorithm,
                "accuracy": m.metrics.accuracy,
                "f1_score": m.metrics.f1_score,
                "input_features": [f.name for f in m.input_features],
            }
            for m in models
        ]

    def get_models_for_equipment(
        self,
        equipment_type: EquipmentType
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get all applicable models for an equipment type."""
        models_by_type = self._model_manager.find_models_for_equipment(equipment_type)

        result = {}
        for model_type, models in models_by_type.items():
            result[model_type] = [
                {
                    "model_id": m.model_id,
                    "name": m.name,
                    "description": m.description,
                    "algorithm": m.algorithm,
                    "accuracy": m.metrics.accuracy,
                }
                for m in models
            ]

        return result

    def get_model_details(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a model."""
        model = self._model_manager.get_model(model_id)
        if not model:
            return None

        return {
            "model_id": model.model_id,
            "name": model.name,
            "description": model.description,
            "version": model.version,
            "equipment_type": model.equipment_type.value,
            "model_type": model.model_type.value,
            "algorithm": model.algorithm,
            "framework": model.framework,
            "status": model.status.value,
            "failure_modes": [fm.value for fm in model.failure_modes],
            "input_features": [
                {
                    "name": f.name,
                    "description": f.description,
                    "unit": f.unit,
                    "required": f.required,
                    "min_value": f.min_value,
                    "max_value": f.max_value,
                }
                for f in model.input_features
            ],
            "output_spec": {
                "name": model.output_spec.name,
                "type": model.output_spec.output_type,
                "threshold": model.output_spec.threshold,
                "classes": model.output_spec.classes,
            },
            "metrics": model.metrics.model_dump(),
            "training_samples": model.training_samples,
            "created_at": model.created_at.isoformat(),
            "tags": model.tags,
        }

    def get_recommended_models(
        self,
        equipment_type: EquipmentType,
        use_case: str = "anomaly_detection"
    ) -> List[Dict[str, Any]]:
        """Get recommended models for a use case."""
        return self._model_manager.get_recommendations(equipment_type, use_case)

    # Prediction

    def detect_anomaly(
        self,
        model_id: str,
        sensor_data: Dict[str, float],
        equipment_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Run anomaly detection.

        Args:
            model_id: Anomaly detection model to use
            sensor_data: Current sensor readings
            equipment_id: Optional equipment identifier

        Returns:
            Anomaly detection result
        """
        prediction = self._inference_engine.predict(
            model_id, sensor_data, equipment_id
        )

        if not prediction:
            return None

        return {
            "is_anomaly": prediction.is_anomaly,
            "anomaly_score": prediction.output_value,
            "confidence": prediction.confidence,
            "alert_level": prediction.alert_level,
            "explanation": prediction.explanation,
            "contributing_factors": prediction.contributing_features,
            "timestamp": prediction.timestamp.isoformat(),
        }

    def predict_remaining_life(
        self,
        model_id: str,
        sensor_data: Dict[str, float],
        equipment_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Predict remaining useful life.

        Args:
            model_id: RUL model to use
            sensor_data: Current sensor readings
            equipment_id: Optional equipment identifier

        Returns:
            RUL prediction result
        """
        prediction = self._inference_engine.predict(
            model_id, sensor_data, equipment_id
        )

        if not prediction:
            return None

        return {
            "remaining_days": int(prediction.output_value),
            "confidence": prediction.confidence,
            "maintenance_urgency": prediction.alert_level,
            "explanation": prediction.explanation,
            "factors": prediction.contributing_features,
            "timestamp": prediction.timestamp.isoformat(),
        }

    def calculate_health(
        self,
        equipment_id: str,
        equipment_type: EquipmentType,
        sensor_data: Dict[str, float],
        historical_data: Optional[List[Dict[str, float]]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate equipment health score.

        Args:
            equipment_id: Equipment identifier
            equipment_type: Type of equipment
            sensor_data: Current sensor readings
            historical_data: Optional historical readings for trend

        Returns:
            Health score with details
        """
        health = self._inference_engine.calculate_health_score(
            equipment_id, equipment_type, sensor_data, historical_data
        )

        return {
            "equipment_id": health.equipment_id,
            "equipment_type": health.equipment_type.value,
            "overall_score": health.overall_score,
            "component_scores": health.component_scores,
            "trend": health.trend,
            "trend_slope": health.trend_slope,
            "days_to_maintenance": health.days_to_maintenance,
            "failure_probability_30d": health.failure_probability_30d,
            "predicted_failure_modes": health.predicted_failure_modes,
            "recommendations": health.recommendations,
            "timestamp": health.timestamp.isoformat(),
        }

    def run_prediction(
        self,
        model_id: str,
        input_data: Dict[str, float],
        equipment_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Run a generic prediction with any model.

        Args:
            model_id: Model to use
            input_data: Input feature values
            equipment_id: Optional equipment identifier

        Returns:
            Prediction result
        """
        prediction = self._inference_engine.predict(
            model_id, input_data, equipment_id
        )

        if not prediction:
            return None

        return {
            "prediction_id": prediction.prediction_id,
            "model_id": prediction.model_id,
            "model_name": prediction.model_name,
            "output_value": prediction.output_value,
            "confidence": prediction.confidence,
            "probabilities": prediction.probabilities,
            "label": prediction.prediction_label,
            "explanation": prediction.explanation,
            "contributing_features": prediction.contributing_features,
            "is_anomaly": prediction.is_anomaly,
            "alert_level": prediction.alert_level,
            "timestamp": prediction.timestamp.isoformat(),
        }

    # Ensemble

    def create_ensemble(
        self,
        name: str,
        model_ids: List[str],
        weights: Optional[Dict[str, float]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a model ensemble."""
        ensemble = self._model_manager.create_ensemble(
            name, model_ids, weights
        )

        if not ensemble:
            return None

        return {
            "ensemble_id": ensemble.ensemble_id,
            "name": ensemble.name,
            "model_ids": ensemble.model_ids,
            "weights": ensemble.weights,
            "equipment_type": ensemble.equipment_type.value,
        }

    def run_ensemble_prediction(
        self,
        ensemble_id: str,
        input_data: Dict[str, float],
        equipment_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Run prediction with a model ensemble."""
        prediction = self._inference_engine.predict_ensemble(
            ensemble_id, input_data, equipment_id
        )

        if not prediction:
            return None

        return {
            "prediction_id": prediction.prediction_id,
            "ensemble_id": ensemble_id,
            "output_value": prediction.output_value,
            "confidence": prediction.confidence,
            "label": prediction.prediction_label,
            "is_anomaly": prediction.is_anomaly,
            "alert_level": prediction.alert_level,
            "timestamp": prediction.timestamp.isoformat(),
        }

    # Model comparison

    def compare_models(self, model_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple models."""
        return self._model_manager.compare_models(model_ids)

    # Batch operations

    def batch_predict(
        self,
        model_id: str,
        data_points: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Run predictions on multiple data points.

        Args:
            model_id: Model to use
            data_points: List of {equipment_id, sensor_data} dicts

        Returns:
            List of prediction results
        """
        results = []

        for point in data_points:
            equipment_id = point.get("equipment_id")
            sensor_data = point.get("sensor_data", {})

            prediction = self.run_prediction(model_id, sensor_data, equipment_id)
            if prediction:
                results.append(prediction)

        return results

    def batch_health_check(
        self,
        equipment_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate health scores for multiple equipment.

        Args:
            equipment_list: List of equipment configs

        Returns:
            List of health scores
        """
        results = []

        for eq in equipment_list:
            health = self.calculate_health(
                equipment_id=eq.get("equipment_id", "unknown"),
                equipment_type=EquipmentType(eq.get("equipment_type", "generic")),
                sensor_data=eq.get("sensor_data", {}),
                historical_data=eq.get("historical_data"),
            )
            results.append(health)

        return results

    # Statistics

    def get_catalog_summary(self) -> Dict[str, Any]:
        """Get summary of model catalog."""
        return self._model_manager.get_catalog_summary()

    def get_model_statistics(self, model_id: str) -> Dict[str, Any]:
        """Get statistics for a specific model."""
        return self._model_manager.get_model_statistics(model_id)

    def get_equipment_types(self) -> List[str]:
        """Get list of supported equipment types."""
        return [et.value for et in EquipmentType]

    def get_model_types(self) -> List[str]:
        """Get list of supported model types."""
        return [mt.value for mt in ModelType]

    def get_failure_modes(
        self,
        equipment_type: Optional[EquipmentType] = None
    ) -> List[Dict[str, Any]]:
        """Get supported failure modes."""
        from .models import FAILURE_SIGNATURES

        modes = []
        for mode in FailureMode:
            sig = FAILURE_SIGNATURES.get(mode, {})

            # Filter by equipment type if applicable
            if equipment_type:
                # For now, include all modes
                pass

            modes.append({
                "mode": mode.value,
                "indicators": sig.get("indicators", []),
                "progression_days": sig.get("progression_days"),
            })

        return modes

    # Load management

    def preload_models(
        self,
        equipment_type: Optional[EquipmentType] = None
    ) -> int:
        """Preload models for faster inference."""
        models = self._model_manager.list_models(
            equipment_type=equipment_type,
            status=ModelStatus.READY,
        )

        loaded = 0
        for model in models:
            if self._model_manager.load_model(model.model_id):
                loaded += 1

        logger.info(f"Preloaded {loaded} models")
        return loaded

    def unload_all_models(self) -> int:
        """Unload all models from memory."""
        loaded = self._model_manager.get_loaded_models()
        count = 0

        for model_id in loaded:
            if self._model_manager.unload_model(model_id):
                count += 1

        logger.info(f"Unloaded {count} models")
        return count
