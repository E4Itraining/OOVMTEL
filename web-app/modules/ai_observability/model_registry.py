"""
AI Model Registry - Centralized registry for all AI/ML models

This module provides:
- Model registration and lifecycle management
- Version control and deployment tracking
- Model metadata and lineage
- Discovery and inventory for AI Act compliance
"""

import logging
from datetime import datetime
from typing import Optional
import uuid

from .models import (
    AIModel,
    ModelStatus,
    ModelType,
    AIRiskLevel,
)

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Centralized registry for AI/ML models.

    Provides model lifecycle management, version tracking,
    and AI Act compliance inventory.
    """

    def __init__(self):
        """Initialize the model registry"""
        self._models: dict[str, AIModel] = {}
        self._version_history: dict[str, list[str]] = {}  # model_name -> [version_ids]
        self._initialized = False
        logger.info("ModelRegistry initialized")

    async def initialize(self):
        """Initialize registry with built-in SYNAPSIX models"""
        if self._initialized:
            return

        # Register built-in AI modules
        builtin_models = [
            {
                "model_id": "nlp-query-engine-v1",
                "name": "NLP Query Engine",
                "version": "1.0.0",
                "model_type": ModelType.NLP_QUERY,
                "description": "Natural language query processing for industrial metrics. "
                              "Converts French/English queries to PromQL.",
                "risk_level": AIRiskLevel.MINIMAL,
                "baseline_latency_ms": 150.0,
                "baseline_accuracy": 0.92,
                "tags": ["nlp", "query", "promql", "multilingual"],
            },
            {
                "model_id": "rca-engine-v1",
                "name": "Root Cause Analysis Engine",
                "version": "1.0.0",
                "model_type": ModelType.ROOT_CAUSE_ANALYSIS,
                "description": "Automated root cause analysis using causal graphs "
                              "and temporal correlation for industrial incidents.",
                "risk_level": AIRiskLevel.LIMITED,
                "baseline_latency_ms": 500.0,
                "baseline_accuracy": 0.85,
                "tags": ["rca", "causal", "incident", "correlation"],
            },
            {
                "model_id": "predictive-maintenance-v1",
                "name": "Predictive Maintenance Engine",
                "version": "1.0.0",
                "model_type": ModelType.PREDICTIVE_MAINTENANCE,
                "description": "Anomaly detection and RUL prediction for industrial equipment. "
                              "Uses statistical methods and trend analysis.",
                "risk_level": AIRiskLevel.LIMITED,
                "baseline_latency_ms": 300.0,
                "baseline_accuracy": 0.88,
                "human_oversight_required": True,
                "tags": ["predictive", "rul", "anomaly", "maintenance"],
            },
            {
                "model_id": "anomaly-detector-zscore-v1",
                "name": "Z-Score Anomaly Detector",
                "version": "1.0.0",
                "model_type": ModelType.ANOMALY_DETECTION,
                "description": "Statistical anomaly detection using Z-score analysis "
                              "for real-time metric monitoring.",
                "risk_level": AIRiskLevel.MINIMAL,
                "baseline_latency_ms": 50.0,
                "baseline_accuracy": 0.90,
                "tags": ["anomaly", "zscore", "realtime", "statistical"],
            },
            {
                "model_id": "time-series-forecaster-v1",
                "name": "Time Series Forecaster",
                "version": "1.0.0",
                "model_type": ModelType.TIME_SERIES_FORECAST,
                "description": "ARIMA-based time series forecasting for metric prediction "
                              "and capacity planning.",
                "risk_level": AIRiskLevel.MINIMAL,
                "baseline_latency_ms": 200.0,
                "baseline_accuracy": 0.82,
                "tags": ["forecast", "arima", "timeseries", "capacity"],
            },
            {
                "model_id": "llm-assistant-mistral-v1",
                "name": "LLM Industrial Assistant",
                "version": "1.0.0",
                "model_type": ModelType.LLM_ASSISTANT,
                "description": "Mistral-powered conversational assistant for industrial "
                              "observability queries and insights.",
                "risk_level": AIRiskLevel.LIMITED,
                "baseline_latency_ms": 2000.0,
                "baseline_accuracy": 0.95,
                "human_oversight_required": True,
                "tags": ["llm", "mistral", "conversational", "assistant"],
            },
            {
                "model_id": "edge-anomaly-detector-v1",
                "name": "Edge Anomaly Detector",
                "version": "1.0.0",
                "model_type": ModelType.EDGE_INFERENCE,
                "description": "Lightweight anomaly detection model optimized for edge deployment. "
                              "Runs on edge agents with limited resources.",
                "risk_level": AIRiskLevel.MINIMAL,
                "deployment_target": "edge",
                "baseline_latency_ms": 20.0,
                "baseline_accuracy": 0.85,
                "tags": ["edge", "anomaly", "lightweight", "onnx"],
            },
            {
                "model_id": "adaptive-threshold-v1",
                "name": "Adaptive Threshold Engine",
                "version": "1.0.0",
                "model_type": ModelType.ANOMALY_DETECTION,
                "description": "Dynamic threshold adjustment based on seasonality "
                              "and historical patterns.",
                "risk_level": AIRiskLevel.MINIMAL,
                "baseline_latency_ms": 30.0,
                "baseline_accuracy": 0.88,
                "tags": ["threshold", "adaptive", "seasonality", "dynamic"],
            },
        ]

        for model_data in builtin_models:
            model = AIModel(
                model_id=model_data["model_id"],
                name=model_data["name"],
                version=model_data["version"],
                model_type=model_data["model_type"],
                status=ModelStatus.ACTIVE,
                deployed_at=datetime.now(),
                deployment_target=model_data.get("deployment_target", "central"),
                description=model_data["description"],
                risk_level=model_data.get("risk_level", AIRiskLevel.MINIMAL),
                baseline_latency_ms=model_data.get("baseline_latency_ms", 100.0),
                baseline_accuracy=model_data.get("baseline_accuracy", 0.90),
                human_oversight_required=model_data.get("human_oversight_required", False),
                tags=model_data.get("tags", []),
                owner="synapsix",
            )
            self._models[model.model_id] = model
            self._version_history[model.name] = [model.model_id]

        self._initialized = True
        logger.info(f"ModelRegistry initialized with {len(self._models)} built-in models")

    def register_model(
        self,
        name: str,
        version: str,
        model_type: ModelType,
        description: str = "",
        risk_level: AIRiskLevel = AIRiskLevel.MINIMAL,
        deployment_target: str = "central",
        **kwargs,
    ) -> AIModel:
        """
        Register a new AI model.

        Args:
            name: Human-readable model name
            version: Semantic version string
            model_type: Type of model
            description: Model description
            risk_level: EU AI Act risk classification
            deployment_target: Where model runs (central, edge, hpc)
            **kwargs: Additional model attributes

        Returns:
            Registered AIModel instance
        """
        model_id = f"{name.lower().replace(' ', '-')}-{version.replace('.', '-')}-{uuid.uuid4().hex[:8]}"

        model = AIModel(
            model_id=model_id,
            name=name,
            version=version,
            model_type=model_type,
            status=ModelStatus.REGISTERED,
            description=description,
            risk_level=risk_level,
            deployment_target=deployment_target,
            **kwargs,
        )

        self._models[model_id] = model

        # Track version history
        if name not in self._version_history:
            self._version_history[name] = []
        self._version_history[name].append(model_id)

        logger.info(f"Model registered: {model_id} ({name} v{version})")
        return model

    def get_model(self, model_id: str) -> Optional[AIModel]:
        """Get a model by ID"""
        return self._models.get(model_id)

    def get_all_models(self) -> list[AIModel]:
        """Get all registered models"""
        return list(self._models.values())

    def get_active_models(self) -> list[AIModel]:
        """Get all active/deployed models"""
        return [m for m in self._models.values() if m.status == ModelStatus.ACTIVE]

    def get_models_by_type(self, model_type: ModelType) -> list[AIModel]:
        """Get models by type"""
        return [m for m in self._models.values() if m.model_type == model_type]

    def get_models_by_status(self, status: ModelStatus) -> list[AIModel]:
        """Get models by status"""
        return [m for m in self._models.values() if m.status == status]

    def get_models_by_risk_level(self, risk_level: AIRiskLevel) -> list[AIModel]:
        """Get models by AI Act risk level"""
        return [m for m in self._models.values() if m.risk_level == risk_level]

    def get_high_risk_models(self) -> list[AIModel]:
        """Get all high/unacceptable risk models (AI Act compliance)"""
        high_risk_levels = [AIRiskLevel.HIGH, AIRiskLevel.UNACCEPTABLE]
        return [m for m in self._models.values() if m.risk_level in high_risk_levels]

    def get_models_requiring_oversight(self) -> list[AIModel]:
        """Get models requiring human oversight"""
        return [m for m in self._models.values() if m.human_oversight_required]

    def update_model_status(self, model_id: str, status: ModelStatus) -> bool:
        """Update model status"""
        if model_id not in self._models:
            logger.warning(f"Model not found: {model_id}")
            return False

        old_status = self._models[model_id].status
        self._models[model_id].status = status
        self._models[model_id].updated_at = datetime.now()

        if status == ModelStatus.ACTIVE and old_status != ModelStatus.ACTIVE:
            self._models[model_id].deployed_at = datetime.now()

        logger.info(f"Model {model_id} status changed: {old_status} -> {status}")
        return True

    def retire_model(self, model_id: str) -> bool:
        """Retire a model (soft delete)"""
        return self.update_model_status(model_id, ModelStatus.RETIRED)

    def get_model_versions(self, name: str) -> list[AIModel]:
        """Get all versions of a model by name"""
        if name not in self._version_history:
            return []
        return [self._models[mid] for mid in self._version_history[name] if mid in self._models]

    def get_latest_version(self, name: str) -> Optional[AIModel]:
        """Get the latest version of a model"""
        versions = self.get_model_versions(name)
        if not versions:
            return None
        # Return the most recently registered version
        return max(versions, key=lambda m: m.created_at)

    def get_inventory_summary(self) -> dict:
        """
        Get AI model inventory summary for compliance reporting.

        Returns:
            Summary dict with counts by type, status, risk level
        """
        models = list(self._models.values())

        return {
            "total_models": len(models),
            "active_models": len([m for m in models if m.status == ModelStatus.ACTIVE]),
            "by_type": {
                t.value: len([m for m in models if m.model_type == t])
                for t in ModelType
            },
            "by_status": {
                s.value: len([m for m in models if m.status == s])
                for s in ModelStatus
            },
            "by_risk_level": {
                r.value: len([m for m in models if m.risk_level == r])
                for r in AIRiskLevel
            },
            "by_deployment_target": {
                target: len([m for m in models if m.deployment_target == target])
                for target in set(m.deployment_target for m in models)
            },
            "requiring_oversight": len([m for m in models if m.human_oversight_required]),
            "high_risk_count": len([m for m in models if m.risk_level in [AIRiskLevel.HIGH, AIRiskLevel.UNACCEPTABLE]]),
            "generated_at": datetime.now().isoformat(),
        }

    def search_models(self, query: str) -> list[AIModel]:
        """Search models by name, description, or tags"""
        query_lower = query.lower()
        results = []

        for model in self._models.values():
            if (
                query_lower in model.name.lower()
                or query_lower in model.description.lower()
                or any(query_lower in tag.lower() for tag in model.tags)
            ):
                results.append(model)

        return results

    def to_dict(self) -> dict:
        """Export registry to dictionary format"""
        return {
            "models": {
                mid: {
                    "model_id": m.model_id,
                    "name": m.name,
                    "version": m.version,
                    "model_type": m.model_type.value,
                    "status": m.status.value,
                    "risk_level": m.risk_level.value,
                    "deployment_target": m.deployment_target,
                    "description": m.description,
                    "baseline_latency_ms": m.baseline_latency_ms,
                    "baseline_accuracy": m.baseline_accuracy,
                    "human_oversight_required": m.human_oversight_required,
                    "tags": m.tags,
                    "owner": m.owner,
                    "deployed_at": m.deployed_at.isoformat() if m.deployed_at else None,
                    "created_at": m.created_at.isoformat(),
                }
                for mid, m in self._models.items()
            },
            "inventory": self.get_inventory_summary(),
        }
