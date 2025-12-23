"""
AI Observability Module - Monitoring AI/ML Systems

This module provides comprehensive observability for AI/ML systems:

1. Model Registry
   - Track and manage all AI models
   - Version control and lifecycle management
   - AI Act risk classification

2. Drift Detection
   - Data drift (input distribution changes)
   - Concept drift (relationship changes)
   - Prediction drift (output changes)
   - Statistical significance testing

3. Performance Tracking
   - Real-time latency and throughput
   - Error rates and SLO monitoring
   - Health scoring and alerts

4. Explainability
   - Prediction audit logging
   - Feature contribution analysis
   - Decision path visualization
   - EU AI Act transparency compliance

Usage:
    from modules.ai_observability import AIObservabilityEngine

    engine = AIObservabilityEngine()
    await engine.initialize()

    # Get dashboard data
    data = engine.get_dashboard_data()

    # Record inference
    engine.record_inference(
        model_id="my-model",
        latency_ms=50.0,
        success=True,
        input_data={"feature1": 1.0},
        output={"prediction": "normal"},
    )

    # Get health score
    health = engine.get_health_score("my-model")
"""

from .models import (
    AIModel,
    ModelStatus,
    ModelType,
    AIRiskLevel,
    DriftType,
    DriftSeverity,
    ExplainabilityMethod,
    ModelPerformanceMetrics,
    DriftDetectionResult,
    PredictionAuditLog,
    AIHealthScore,
    AIAlert,
    FeatureStore,
    AIObservabilityConfig,
)

from .model_registry import ModelRegistry
from .drift_detector import DriftDetector
from .performance_tracker import PerformanceTracker
from .explainability import ExplainabilityEngine
from .engine import AIObservabilityEngine

__all__ = [
    # Main Engine
    "AIObservabilityEngine",

    # Components
    "ModelRegistry",
    "DriftDetector",
    "PerformanceTracker",
    "ExplainabilityEngine",

    # Models
    "AIModel",
    "ModelStatus",
    "ModelType",
    "AIRiskLevel",
    "DriftType",
    "DriftSeverity",
    "ExplainabilityMethod",
    "ModelPerformanceMetrics",
    "DriftDetectionResult",
    "PredictionAuditLog",
    "AIHealthScore",
    "AIAlert",
    "FeatureStore",
    "AIObservabilityConfig",
]
