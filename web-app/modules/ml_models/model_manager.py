"""
Model Manager - Load and manage pre-trained models
"""

import logging
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from .models import (
    PretrainedModel,
    ModelPrediction,
    ModelEnsemble,
    HealthScore,
    EquipmentType,
    ModelType,
    ModelStatus,
    FailureMode,
    PRETRAINED_MODEL_CATALOG,
    FAILURE_SIGNATURES,
)

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manage pre-trained ML models.

    Features:
    - Model registry
    - Model loading/unloading
    - Version management
    - Performance tracking
    """

    def __init__(self):
        # Model registry
        self._models: Dict[str, PretrainedModel] = {}
        self._loaded_models: Dict[str, Any] = {}  # Actual model objects

        # Ensembles
        self._ensembles: Dict[str, ModelEnsemble] = {}

        # Statistics
        self._prediction_counts: Dict[str, int] = defaultdict(int)
        self._prediction_times: Dict[str, List[float]] = defaultdict(list)

        # Load catalog
        self._load_catalog()

        logger.info("Model Manager initialized")

    def _load_catalog(self) -> None:
        """Load pre-trained model catalog."""
        for model_id, model in PRETRAINED_MODEL_CATALOG.items():
            self._models[model_id] = model

        logger.info(f"Loaded {len(self._models)} pre-trained models")

    # Model registry

    def get_model(self, model_id: str) -> Optional[PretrainedModel]:
        """Get model by ID."""
        return self._models.get(model_id)

    def list_models(
        self,
        equipment_type: Optional[EquipmentType] = None,
        model_type: Optional[ModelType] = None,
        status: Optional[ModelStatus] = None,
    ) -> List[PretrainedModel]:
        """List models with optional filters."""
        models = list(self._models.values())

        if equipment_type:
            models = [m for m in models if m.equipment_type == equipment_type]

        if model_type:
            models = [m for m in models if m.model_type == model_type]

        if status:
            models = [m for m in models if m.status == status]

        return models

    def find_models_for_equipment(
        self,
        equipment_type: EquipmentType
    ) -> Dict[str, List[PretrainedModel]]:
        """Find all applicable models for an equipment type."""
        result = defaultdict(list)

        for model in self._models.values():
            if model.equipment_type == equipment_type or model.equipment_type == EquipmentType.GENERIC:
                result[model.model_type.value].append(model)

        return dict(result)

    def register_model(self, model: PretrainedModel) -> str:
        """Register a new model."""
        self._models[model.model_id] = model
        logger.info(f"Registered model: {model.name} ({model.model_id})")
        return model.model_id

    def update_model_status(
        self,
        model_id: str,
        status: ModelStatus
    ) -> bool:
        """Update model status."""
        if model_id not in self._models:
            return False

        self._models[model_id].status = status
        self._models[model_id].updated_at = datetime.utcnow()
        return True

    # Model loading

    def load_model(self, model_id: str) -> bool:
        """
        Load a model into memory.

        Note: In a real implementation, this would load actual ML model files.
        Here we simulate the loading process.
        """
        if model_id not in self._models:
            logger.error(f"Model not found: {model_id}")
            return False

        model = self._models[model_id]

        # Simulate model loading
        self._loaded_models[model_id] = {
            "model": model,
            "loaded_at": datetime.utcnow(),
            "algorithm": model.algorithm,
        }

        logger.info(f"Loaded model: {model.name}")
        return True

    def unload_model(self, model_id: str) -> bool:
        """Unload a model from memory."""
        if model_id in self._loaded_models:
            del self._loaded_models[model_id]
            logger.info(f"Unloaded model: {model_id}")
            return True
        return False

    def is_loaded(self, model_id: str) -> bool:
        """Check if model is loaded."""
        return model_id in self._loaded_models

    def get_loaded_models(self) -> List[str]:
        """Get list of loaded model IDs."""
        return list(self._loaded_models.keys())

    # Ensembles

    def create_ensemble(
        self,
        name: str,
        model_ids: List[str],
        weights: Optional[Dict[str, float]] = None,
        aggregation_method: str = "weighted_average"
    ) -> Optional[ModelEnsemble]:
        """Create a model ensemble."""
        # Verify all models exist
        for mid in model_ids:
            if mid not in self._models:
                logger.error(f"Model not found for ensemble: {mid}")
                return None

        # Default equal weights
        if not weights:
            weights = {mid: 1.0 / len(model_ids) for mid in model_ids}

        # Normalize weights
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}

        # Get equipment type from first model
        equipment_type = self._models[model_ids[0]].equipment_type

        ensemble = ModelEnsemble(
            name=name,
            model_ids=model_ids,
            weights=weights,
            aggregation_method=aggregation_method,
            equipment_type=equipment_type,
        )

        self._ensembles[ensemble.ensemble_id] = ensemble
        logger.info(f"Created ensemble: {name}")

        return ensemble

    def get_ensemble(self, ensemble_id: str) -> Optional[ModelEnsemble]:
        """Get ensemble by ID."""
        return self._ensembles.get(ensemble_id)

    def list_ensembles(self) -> List[ModelEnsemble]:
        """List all ensembles."""
        return list(self._ensembles.values())

    # Model comparison

    def compare_models(
        self,
        model_ids: List[str]
    ) -> Dict[str, Any]:
        """Compare multiple models."""
        models = []
        for mid in model_ids:
            model = self._models.get(mid)
            if model:
                models.append(model)

        if not models:
            return {}

        comparison = {
            "models": [],
            "best_accuracy": None,
            "best_f1": None,
        }

        best_acc = 0
        best_f1 = 0
        best_acc_model = None
        best_f1_model = None

        for model in models:
            metrics = model.metrics
            model_info = {
                "model_id": model.model_id,
                "name": model.name,
                "algorithm": model.algorithm,
                "equipment_type": model.equipment_type.value,
                "metrics": {
                    "accuracy": metrics.accuracy,
                    "precision": metrics.precision,
                    "recall": metrics.recall,
                    "f1_score": metrics.f1_score,
                    "rmse": metrics.rmse,
                    "r2_score": metrics.r2_score,
                },
                "training_samples": model.training_samples,
            }
            comparison["models"].append(model_info)

            if metrics.accuracy and metrics.accuracy > best_acc:
                best_acc = metrics.accuracy
                best_acc_model = model.model_id

            if metrics.f1_score and metrics.f1_score > best_f1:
                best_f1 = metrics.f1_score
                best_f1_model = model.model_id

        comparison["best_accuracy"] = {
            "model_id": best_acc_model,
            "value": best_acc,
        }
        comparison["best_f1"] = {
            "model_id": best_f1_model,
            "value": best_f1,
        }

        return comparison

    # Statistics

    def get_model_statistics(self, model_id: str) -> Dict[str, Any]:
        """Get statistics for a model."""
        model = self._models.get(model_id)
        if not model:
            return {}

        prediction_count = self._prediction_counts.get(model_id, 0)
        prediction_times = self._prediction_times.get(model_id, [])

        avg_time = sum(prediction_times) / len(prediction_times) if prediction_times else 0

        return {
            "model_id": model_id,
            "name": model.name,
            "status": model.status.value,
            "is_loaded": self.is_loaded(model_id),
            "prediction_count": prediction_count,
            "avg_prediction_time_ms": round(avg_time, 2),
            "training_samples": model.training_samples,
            "metrics": model.metrics.model_dump(),
        }

    def get_catalog_summary(self) -> Dict[str, Any]:
        """Get summary of model catalog."""
        by_equipment = defaultdict(int)
        by_type = defaultdict(int)
        by_status = defaultdict(int)

        for model in self._models.values():
            by_equipment[model.equipment_type.value] += 1
            by_type[model.model_type.value] += 1
            by_status[model.status.value] += 1

        return {
            "total_models": len(self._models),
            "loaded_models": len(self._loaded_models),
            "ensembles": len(self._ensembles),
            "by_equipment": dict(by_equipment),
            "by_type": dict(by_type),
            "by_status": dict(by_status),
        }

    def record_prediction(
        self,
        model_id: str,
        prediction_time_ms: float
    ) -> None:
        """Record a prediction for statistics."""
        self._prediction_counts[model_id] += 1
        self._prediction_times[model_id].append(prediction_time_ms)

        # Keep last 1000 times
        if len(self._prediction_times[model_id]) > 1000:
            self._prediction_times[model_id] = self._prediction_times[model_id][-1000:]

    def get_recommendations(
        self,
        equipment_type: EquipmentType,
        use_case: str = "anomaly_detection"
    ) -> List[Dict[str, Any]]:
        """Get model recommendations for a use case."""
        recommendations = []

        # Map use case to model type
        use_case_mapping = {
            "anomaly_detection": ModelType.ANOMALY_DETECTION,
            "predictive_maintenance": ModelType.REMAINING_USEFUL_LIFE,
            "failure_prediction": ModelType.FAILURE_PREDICTION,
            "health_monitoring": ModelType.HEALTH_INDEX,
        }

        target_type = use_case_mapping.get(use_case, ModelType.ANOMALY_DETECTION)

        # Find matching models
        for model in self._models.values():
            if model.status != ModelStatus.READY:
                continue

            if model.equipment_type not in [equipment_type, EquipmentType.GENERIC]:
                continue

            if model.model_type != target_type:
                continue

            score = 0.0
            if model.metrics.f1_score:
                score = model.metrics.f1_score

            recommendations.append({
                "model_id": model.model_id,
                "name": model.name,
                "description": model.description,
                "score": score,
                "algorithm": model.algorithm,
                "training_samples": model.training_samples,
            })

        # Sort by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)

        return recommendations[:5]
