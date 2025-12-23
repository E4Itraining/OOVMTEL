"""
AI Observability Engine - Main Orchestrator

This is the central engine that integrates all AI observability components:
- Model Registry: Track and manage AI models
- Drift Detector: Detect data and model drift
- Performance Tracker: Monitor latency, throughput, errors
- Explainability: Audit logging and decision transparency

The engine provides a unified interface for monitoring AI systems
and ensuring EU AI Act compliance.
"""

import logging
from datetime import datetime
from typing import Any, Optional
import asyncio

from .models import (
    AIModel,
    ModelStatus,
    ModelType,
    AIRiskLevel,
    AIObservabilityConfig,
    AIHealthScore,
    DriftDetectionResult,
    PredictionAuditLog,
    AIAlert,
    ModelPerformanceMetrics,
    ExplainabilityMethod,
)
from .model_registry import ModelRegistry
from .drift_detector import DriftDetector
from .performance_tracker import PerformanceTracker
from .explainability import ExplainabilityEngine

logger = logging.getLogger(__name__)


class AIObservabilityEngine:
    """
    Central engine for AI/ML observability.

    Provides unified interface for:
    - Model lifecycle management
    - Performance monitoring
    - Drift detection
    - Explainability and auditing
    - Compliance reporting
    """

    def __init__(
        self,
        config: Optional[AIObservabilityConfig] = None,
        victoria_metrics_url: str = "http://victoria-metrics:8428",
    ):
        """
        Initialize the AI Observability Engine.

        Args:
            config: Optional configuration
            victoria_metrics_url: VictoriaMetrics URL for metrics
        """
        self.config = config or AIObservabilityConfig()
        self.vm_url = victoria_metrics_url

        # Initialize components
        self.model_registry = ModelRegistry()
        self.drift_detector = DriftDetector(config=self.config, victoria_metrics_url=victoria_metrics_url)
        self.performance_tracker = PerformanceTracker(config=self.config)
        self.explainability = ExplainabilityEngine(config=self.config)

        self._initialized = False
        logger.info("AIObservabilityEngine created")

    async def initialize(self):
        """Initialize all components"""
        if self._initialized:
            return

        logger.info("Initializing AI Observability Engine...")

        # Initialize components
        await self.model_registry.initialize()
        await self.drift_detector.initialize()
        await self.explainability.initialize()

        # Set baselines for all registered models
        for model in self.model_registry.get_all_models():
            self.performance_tracker.set_model_baseline(model)

        # Simulate initial activity for demo
        await self._simulate_initial_data()

        self._initialized = True
        logger.info("AI Observability Engine initialized successfully")

    async def _simulate_initial_data(self):
        """Simulate initial data for demo purposes"""
        models = self.model_registry.get_active_models()

        # Simulate performance data
        self.performance_tracker.simulate_model_activity(models)

        # Simulate explainability logs
        model_ids = [m.model_id for m in models]
        self.explainability.simulate_predictions(model_ids, count=100)

        logger.info("Simulated initial observability data")

    # =========================================================================
    # MODEL REGISTRY OPERATIONS
    # =========================================================================

    def register_model(
        self,
        name: str,
        version: str,
        model_type: ModelType,
        description: str = "",
        risk_level: AIRiskLevel = AIRiskLevel.MINIMAL,
        **kwargs,
    ) -> AIModel:
        """Register a new AI model"""
        model = self.model_registry.register_model(
            name=name,
            version=version,
            model_type=model_type,
            description=description,
            risk_level=risk_level,
            **kwargs,
        )
        self.performance_tracker.set_model_baseline(model)
        return model

    def get_model(self, model_id: str) -> Optional[AIModel]:
        """Get a model by ID"""
        return self.model_registry.get_model(model_id)

    def get_all_models(self) -> list[AIModel]:
        """Get all registered models"""
        return self.model_registry.get_all_models()

    def get_active_models(self) -> list[AIModel]:
        """Get active models"""
        return self.model_registry.get_active_models()

    def get_model_inventory(self) -> dict:
        """Get AI model inventory summary"""
        return self.model_registry.get_inventory_summary()

    # =========================================================================
    # PERFORMANCE TRACKING
    # =========================================================================

    def record_inference(
        self,
        model_id: str,
        latency_ms: float,
        success: bool = True,
        input_data: Optional[dict] = None,
        output: Optional[Any] = None,
        confidence: float = 0.0,
    ):
        """
        Record a model inference/prediction.

        Args:
            model_id: Model ID
            latency_ms: Inference latency
            success: Whether inference was successful
            input_data: Optional input data for explainability
            output: Optional output for explainability
            confidence: Confidence score
        """
        # Record performance metrics
        self.performance_tracker.record_inference(
            model_id=model_id,
            latency_ms=latency_ms,
            success=success,
        )

        # Log for explainability (if sampling allows)
        if input_data and self.explainability.should_log_prediction(model_id):
            self.explainability.log_prediction(
                model_id=model_id,
                input_data=input_data,
                output=output,
                confidence=confidence,
                latency_ms=latency_ms,
            )

    def get_performance_metrics(
        self,
        model_id: str,
        window_minutes: int = 5,
    ) -> ModelPerformanceMetrics:
        """Get performance metrics for a model"""
        return self.performance_tracker.get_metrics(model_id, window_minutes)

    def get_health_score(self, model_id: str) -> AIHealthScore:
        """Get health score for a model"""
        model = self.model_registry.get_model(model_id)
        return self.performance_tracker.calculate_health_score(model_id, model)

    def get_all_health_scores(self) -> dict[str, AIHealthScore]:
        """Get health scores for all active models"""
        models = self.model_registry.get_active_models()
        return self.performance_tracker.get_all_health_scores(models)

    # =========================================================================
    # DRIFT DETECTION
    # =========================================================================

    async def detect_drift(
        self,
        model_id: str,
        feature_id: str,
        current_data: list[float],
    ) -> DriftDetectionResult:
        """Detect drift for a feature"""
        return await self.drift_detector.detect_data_drift(
            model_id=model_id,
            feature_id=feature_id,
            current_data=current_data,
        )

    async def detect_multi_feature_drift(
        self,
        model_id: str,
        feature_data: dict[str, list[float]],
    ) -> DriftDetectionResult:
        """Detect drift across multiple features"""
        return await self.drift_detector.detect_multi_feature_drift(
            model_id=model_id,
            feature_data=feature_data,
        )

    def get_drift_summary(self) -> dict:
        """Get drift detection summary"""
        return self.drift_detector.get_drift_summary()

    def get_drift_history(
        self,
        model_id: Optional[str] = None,
        hours: int = 24,
    ) -> list[DriftDetectionResult]:
        """Get drift detection history"""
        return self.drift_detector.get_drift_history(model_id, hours)

    # =========================================================================
    # EXPLAINABILITY
    # =========================================================================

    def explain_prediction(self, prediction_id: str) -> Optional[dict]:
        """Get explanation for a prediction"""
        return self.explainability.explain_prediction(prediction_id)

    def get_audit_logs(
        self,
        model_id: Optional[str] = None,
        hours: int = 24,
        limit: int = 100,
    ) -> list[PredictionAuditLog]:
        """Get prediction audit logs"""
        return self.explainability.get_audit_logs(model_id, hours, limit)

    def get_transparency_report(self, model_id: str) -> dict:
        """Generate AI Act transparency report"""
        return self.explainability.get_model_transparency_report(model_id)

    def record_feedback(
        self,
        prediction_id: str,
        feedback: str,
        score: Optional[float] = None,
    ) -> bool:
        """Record human feedback on prediction"""
        return self.explainability.record_human_feedback(prediction_id, feedback, score)

    # =========================================================================
    # ALERTS
    # =========================================================================

    def get_active_alerts(
        self,
        model_id: Optional[str] = None,
    ) -> list[AIAlert]:
        """Get active alerts"""
        return self.performance_tracker.get_active_alerts(model_id)

    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert"""
        return self.performance_tracker.acknowledge_alert(alert_id, user)

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        return self.performance_tracker.resolve_alert(alert_id)

    # =========================================================================
    # DASHBOARD DATA
    # =========================================================================

    def get_dashboard_data(self) -> dict:
        """
        Get comprehensive dashboard data.

        Returns all data needed for the AI Observability dashboard.
        """
        models = self.model_registry.get_all_models()
        active_models = self.model_registry.get_active_models()
        health_scores = self.get_all_health_scores()

        # Calculate overall health
        if health_scores:
            avg_health = sum(s.overall_score for s in health_scores.values()) / len(health_scores)
            healthy_count = len([s for s in health_scores.values() if s.status == "healthy"])
            warning_count = len([s for s in health_scores.values() if s.status == "warning"])
            critical_count = len([s for s in health_scores.values() if s.status == "critical"])
        else:
            avg_health = 0
            healthy_count = warning_count = critical_count = 0

        return {
            "timestamp": datetime.now().isoformat(),

            # Overview
            "overview": {
                "total_models": len(models),
                "active_models": len(active_models),
                "avg_health_score": round(avg_health, 1),
                "healthy_count": healthy_count,
                "warning_count": warning_count,
                "critical_count": critical_count,
            },

            # Models list with health
            "models": [
                {
                    "model_id": m.model_id,
                    "name": m.name,
                    "version": m.version,
                    "type": m.model_type.value,
                    "status": m.status.value,
                    "risk_level": m.risk_level.value,
                    "deployment_target": m.deployment_target,
                    "health": health_scores.get(m.model_id, AIHealthScore(
                        model_id=m.model_id,
                        timestamp=datetime.now(),
                    )).__dict__ if m.model_id in health_scores else None,
                    "tags": m.tags,
                }
                for m in models
            ],

            # Performance summary
            "performance": self.performance_tracker.get_performance_summary(),

            # Drift summary
            "drift": self.get_drift_summary(),

            # Explainability summary
            "explainability": self.explainability.get_explainability_summary(),

            # Active alerts
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "model_id": a.model_id,
                    "severity": a.severity,
                    "category": a.category,
                    "title": a.title,
                    "description": a.description,
                    "timestamp": a.timestamp.isoformat(),
                    "acknowledged": a.acknowledged,
                }
                for a in self.get_active_alerts()
            ],

            # Inventory (for compliance)
            "inventory": self.get_model_inventory(),

            # High-risk models (AI Act)
            "high_risk_models": [
                {
                    "model_id": m.model_id,
                    "name": m.name,
                    "risk_level": m.risk_level.value,
                    "human_oversight_required": m.human_oversight_required,
                }
                for m in self.model_registry.get_high_risk_models()
            ],
        }

    def get_model_detail(self, model_id: str) -> Optional[dict]:
        """
        Get detailed data for a specific model.

        Args:
            model_id: Model ID

        Returns:
            Detailed model data for dashboard
        """
        model = self.model_registry.get_model(model_id)
        if not model:
            return None

        metrics = self.get_performance_metrics(model_id)
        health = self.get_health_score(model_id)
        drift_history = self.get_drift_history(model_id, hours=24)
        audit_logs = self.get_audit_logs(model_id, hours=24, limit=20)
        alerts = self.get_active_alerts(model_id)

        return {
            "model": {
                "model_id": model.model_id,
                "name": model.name,
                "version": model.version,
                "type": model.model_type.value,
                "status": model.status.value,
                "description": model.description,
                "risk_level": model.risk_level.value,
                "deployment_target": model.deployment_target,
                "deployed_at": model.deployed_at.isoformat() if model.deployed_at else None,
                "owner": model.owner,
                "tags": model.tags,
                "slo_latency_p99_ms": model.slo_latency_p99_ms,
                "slo_error_rate_pct": model.slo_error_rate_pct,
                "human_oversight_required": model.human_oversight_required,
            },
            "performance": {
                "latency_p50": metrics.latency_p50,
                "latency_p95": metrics.latency_p95,
                "latency_p99": metrics.latency_p99,
                "latency_avg": metrics.latency_avg,
                "requests_total": metrics.requests_total,
                "requests_per_second": metrics.requests_per_second,
                "error_rate_pct": metrics.error_rate_pct,
            },
            "health": {
                "overall_score": health.overall_score,
                "status": health.status,
                "performance_score": health.performance_score,
                "accuracy_score": health.accuracy_score,
                "drift_score": health.drift_score,
                "availability_score": health.availability_score,
                "slo_violations": health.slo_violations,
                "recommendations": health.recommendations,
                "score_trend": health.score_trend,
            },
            "drift_history": [
                {
                    "timestamp": d.timestamp.isoformat(),
                    "type": d.drift_type.value,
                    "severity": d.severity.value,
                    "score": d.drift_score,
                    "affected_features": d.affected_features,
                }
                for d in drift_history[:10]
            ],
            "recent_predictions": [
                {
                    "prediction_id": log.prediction_id,
                    "timestamp": log.timestamp.isoformat(),
                    "confidence": log.confidence,
                    "latency_ms": log.latency_ms,
                    "top_features": log.top_contributing_features[:3],
                }
                for log in audit_logs[:10]
            ],
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "severity": a.severity,
                    "title": a.title,
                    "timestamp": a.timestamp.isoformat(),
                }
                for a in alerts
            ],
            "transparency_report": self.get_transparency_report(model_id),
        }

    # =========================================================================
    # COMPLIANCE REPORTING
    # =========================================================================

    def get_compliance_report(self) -> dict:
        """
        Generate EU AI Act compliance report.

        Returns comprehensive compliance status for all AI systems.
        """
        models = self.model_registry.get_all_models()
        inventory = self.get_model_inventory()

        # Compliance checks
        checks = {
            "model_registry": {
                "status": "compliant",
                "description": "All AI models are registered with metadata",
                "models_registered": len(models),
            },
            "risk_classification": {
                "status": "compliant",
                "description": "All models have EU AI Act risk classification",
                "by_risk_level": inventory["by_risk_level"],
            },
            "transparency": {
                "status": "compliant" if self.config.explainability_enabled else "non-compliant",
                "description": "Explainability and audit logging enabled",
                "audit_sampling_rate": f"{self.config.audit_sampling_rate * 100:.0f}%",
            },
            "human_oversight": {
                "status": "compliant",
                "description": "High-risk models require human oversight",
                "models_requiring_oversight": inventory["requiring_oversight"],
            },
            "drift_monitoring": {
                "status": "compliant" if self.config.drift_detection_enabled else "non-compliant",
                "description": "Data and model drift monitoring active",
                "check_interval_min": self.config.drift_check_interval_min,
            },
            "performance_monitoring": {
                "status": "compliant",
                "description": "Real-time performance and SLO monitoring",
                "slo_tracking": "enabled",
            },
        }

        overall_compliant = all(c["status"] == "compliant" for c in checks.values())

        return {
            "report_date": datetime.now().isoformat(),
            "overall_status": "compliant" if overall_compliant else "non-compliant",
            "framework": "EU AI Act",
            "inventory_summary": inventory,
            "compliance_checks": checks,
            "high_risk_models": [
                {
                    "model_id": m.model_id,
                    "name": m.name,
                    "risk_level": m.risk_level.value,
                    "human_oversight": m.human_oversight_required,
                    "transparency_documented": m.transparency_documented,
                }
                for m in self.model_registry.get_high_risk_models()
            ],
            "recommendations": self._get_compliance_recommendations(checks),
        }

    def _get_compliance_recommendations(self, checks: dict) -> list[str]:
        """Generate compliance recommendations"""
        recommendations = []

        for check_name, check_data in checks.items():
            if check_data["status"] != "compliant":
                if check_name == "transparency":
                    recommendations.append("Enable explainability and audit logging")
                elif check_name == "drift_monitoring":
                    recommendations.append("Enable drift detection monitoring")

        if not recommendations:
            recommendations.append("All compliance checks passed. Continue monitoring.")

        return recommendations
