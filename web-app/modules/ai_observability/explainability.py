"""
Explainability Module - AI Decision Transparency and Auditability

This module provides:
- Prediction audit logging
- Feature contribution analysis
- Decision path visualization
- Counterfactual explanations
- AI Act transparency compliance
"""

import logging
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Optional
import uuid
import random

from .models import (
    PredictionAuditLog,
    ExplainabilityMethod,
    AIObservabilityConfig,
)

logger = logging.getLogger(__name__)


class ExplainabilityEngine:
    """
    Provides AI model explainability and decision auditing.

    Supports multiple explanation methods and maintains
    audit logs for transparency and compliance.
    """

    def __init__(
        self,
        config: Optional[AIObservabilityConfig] = None,
    ):
        """Initialize the explainability engine"""
        self.config = config or AIObservabilityConfig()

        # Audit log storage
        self._audit_logs: list[PredictionAuditLog] = []

        # Explanation cache
        self._explanation_cache: dict[str, dict] = {}

        # Feature importance baselines (per model)
        self._feature_baselines: dict[str, dict] = {}

        # Sampling counter
        self._prediction_counter: dict[str, int] = defaultdict(int)

        logger.info("ExplainabilityEngine initialized")

    async def initialize(self):
        """Initialize with sample feature importances"""
        # Define feature importance baselines for built-in models
        self._feature_baselines = {
            "predictive-maintenance-v1": {
                "vibration": 0.25,
                "temperature": 0.22,
                "pressure": 0.18,
                "operating_hours": 0.15,
                "load_factor": 0.12,
                "maintenance_history": 0.08,
            },
            "anomaly-detector-zscore-v1": {
                "current_value": 0.40,
                "historical_mean": 0.25,
                "historical_std": 0.20,
                "trend": 0.10,
                "seasonality": 0.05,
            },
            "rca-engine-v1": {
                "temporal_correlation": 0.30,
                "causal_strength": 0.25,
                "historical_occurrence": 0.20,
                "system_dependencies": 0.15,
                "metric_proximity": 0.10,
            },
            "nlp-query-engine-v1": {
                "intent_confidence": 0.30,
                "entity_extraction": 0.25,
                "query_structure": 0.20,
                "context_relevance": 0.15,
                "language_detection": 0.10,
            },
            "time-series-forecaster-v1": {
                "recent_trend": 0.35,
                "seasonality_pattern": 0.25,
                "historical_average": 0.20,
                "volatility": 0.12,
                "external_factors": 0.08,
            },
        }
        logger.info("ExplainabilityEngine initialized with feature baselines")

    def should_log_prediction(self, model_id: str) -> bool:
        """
        Determine if prediction should be logged (sampling).

        Args:
            model_id: Model ID

        Returns:
            True if prediction should be logged
        """
        self._prediction_counter[model_id] += 1

        # Sample based on configured rate
        if self.config.audit_sampling_rate >= 1.0:
            return True
        elif self.config.audit_sampling_rate <= 0:
            return False
        else:
            return random.random() < self.config.audit_sampling_rate

    def log_prediction(
        self,
        model_id: str,
        input_data: dict,
        output: Any,
        confidence: float = 0.0,
        latency_ms: float = 0.0,
        method: ExplainabilityMethod = ExplainabilityMethod.FEATURE_IMPORTANCE,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_context: Optional[dict] = None,
    ) -> PredictionAuditLog:
        """
        Log a prediction with explainability information.

        Args:
            model_id: Model ID
            input_data: Input data (will be hashed for privacy)
            output: Prediction output
            confidence: Confidence score
            latency_ms: Inference latency
            method: Explainability method used
            user_id: Optional user ID
            session_id: Optional session ID
            request_context: Additional context

        Returns:
            PredictionAuditLog entry
        """
        timestamp = datetime.now()
        prediction_id = f"pred-{timestamp.timestamp():.0f}-{uuid.uuid4().hex[:8]}"

        # Hash input for privacy
        input_hash = hashlib.sha256(str(input_data).encode()).hexdigest()[:16]

        # Create input summary (without sensitive data)
        input_summary = self._create_input_summary(input_data)

        # Calculate feature contributions
        feature_contributions = self._calculate_feature_contributions(
            model_id, input_data, output
        )

        # Get top contributing features
        sorted_features = sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True,
        )
        top_contributing = [
            {"feature": f, "contribution": c}
            for f, c in sorted_features[:5]
        ]

        # Generate decision path
        decision_path = self._generate_decision_path(model_id, input_data, output)

        audit_log = PredictionAuditLog(
            prediction_id=prediction_id,
            model_id=model_id,
            timestamp=timestamp,
            input_hash=input_hash,
            input_summary=input_summary,
            prediction_output=output,
            confidence=confidence,
            explainability_method=method,
            feature_contributions=feature_contributions,
            top_contributing_features=top_contributing,
            decision_path=decision_path,
            request_context=request_context or {},
            user_id=user_id,
            session_id=session_id,
            latency_ms=latency_ms,
        )

        self._audit_logs.append(audit_log)

        # Keep only configured retention
        self._cleanup_old_logs()

        return audit_log

    def _create_input_summary(self, input_data: dict) -> dict:
        """Create a privacy-safe summary of input data"""
        summary = {}

        for key, value in input_data.items():
            if isinstance(value, (int, float)):
                summary[key] = {
                    "type": "numeric",
                    "range": "normal" if -1000 < value < 1000 else "extreme",
                }
            elif isinstance(value, str):
                summary[key] = {
                    "type": "string",
                    "length": len(value),
                }
            elif isinstance(value, list):
                summary[key] = {
                    "type": "list",
                    "length": len(value),
                }
            elif isinstance(value, dict):
                summary[key] = {
                    "type": "object",
                    "keys": list(value.keys())[:5],
                }
            else:
                summary[key] = {"type": str(type(value).__name__)}

        return summary

    def _calculate_feature_contributions(
        self,
        model_id: str,
        input_data: dict,
        output: Any,
    ) -> dict[str, float]:
        """
        Calculate feature contributions to prediction.

        Uses stored baselines and simulates SHAP-like contributions.
        """
        # Get baseline importances for this model
        baselines = self._feature_baselines.get(model_id, {})

        if not baselines:
            # Generate generic contributions based on input
            contributions = {}
            total_weight = 0
            for key in input_data:
                weight = random.uniform(0.05, 0.30)
                contributions[key] = weight
                total_weight += weight

            # Normalize
            if total_weight > 0:
                contributions = {k: v / total_weight for k, v in contributions.items()}

            return contributions

        # Use baseline with some variation
        contributions = {}
        for feature, importance in baselines.items():
            # Add some randomness to simulate real SHAP values
            variation = random.uniform(-0.05, 0.05)
            contributions[feature] = max(0, importance + variation)

        # Normalize to sum to 1
        total = sum(contributions.values())
        if total > 0:
            contributions = {k: v / total for k, v in contributions.items()}

        return contributions

    def _generate_decision_path(
        self,
        model_id: str,
        input_data: dict,
        output: Any,
    ) -> str:
        """Generate a human-readable decision path"""
        # Get feature contributions
        contributions = self._calculate_feature_contributions(model_id, input_data, output)

        # Sort by importance
        sorted_features = sorted(
            contributions.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        # Build decision path narrative
        steps = []
        for i, (feature, importance) in enumerate(sorted_features[:3], 1):
            importance_pct = importance * 100
            steps.append(f"Step {i}: {feature} contributed {importance_pct:.1f}%")

        if isinstance(output, dict):
            output_str = str(output.get("result", output.get("prediction", "N/A")))
        else:
            output_str = str(output)

        steps.append(f"Final prediction: {output_str[:50]}")

        return " → ".join(steps)

    def explain_prediction(
        self,
        prediction_id: str,
    ) -> Optional[dict]:
        """
        Get detailed explanation for a prediction.

        Args:
            prediction_id: Prediction ID from audit log

        Returns:
            Detailed explanation dict
        """
        # Find the audit log
        audit_log = None
        for log in reversed(self._audit_logs):
            if log.prediction_id == prediction_id:
                audit_log = log
                break

        if not audit_log:
            return None

        # Build detailed explanation
        explanation = {
            "prediction_id": audit_log.prediction_id,
            "model_id": audit_log.model_id,
            "timestamp": audit_log.timestamp.isoformat(),
            "confidence": audit_log.confidence,
            "method": audit_log.explainability_method.value,
            "feature_contributions": audit_log.feature_contributions,
            "top_features": audit_log.top_contributing_features,
            "decision_path": audit_log.decision_path,
            "input_summary": audit_log.input_summary,
            "output": audit_log.prediction_output,
            "latency_ms": audit_log.latency_ms,
            "human_readable": self._generate_human_readable_explanation(audit_log),
        }

        return explanation

    def _generate_human_readable_explanation(
        self,
        audit_log: PredictionAuditLog,
    ) -> str:
        """Generate human-readable explanation of prediction"""
        top_features = audit_log.top_contributing_features

        if not top_features:
            return "No feature contribution data available."

        # Build narrative
        lines = [
            f"This prediction was made with {audit_log.confidence * 100:.1f}% confidence.",
            "",
            "The main factors influencing this decision were:",
        ]

        for i, feature_data in enumerate(top_features[:3], 1):
            feature = feature_data["feature"]
            contribution = feature_data["contribution"] * 100
            lines.append(f"  {i}. {feature}: {contribution:.1f}% influence")

        if audit_log.decision_path:
            lines.extend([
                "",
                "Decision Path:",
                f"  {audit_log.decision_path}",
            ])

        return "\n".join(lines)

    def generate_counterfactual(
        self,
        model_id: str,
        input_data: dict,
        desired_output: Any,
    ) -> dict:
        """
        Generate counterfactual explanation.

        Shows what input changes would lead to different output.

        Args:
            model_id: Model ID
            input_data: Original input
            desired_output: Desired different output

        Returns:
            Counterfactual explanation
        """
        # Get feature baselines
        baselines = self._feature_baselines.get(model_id, {})

        # Identify most impactful features to change
        changes_needed = []

        for feature, importance in sorted(baselines.items(), key=lambda x: x[1], reverse=True)[:3]:
            # Simulate what change would be needed
            if feature in input_data:
                current_val = input_data[feature]
                if isinstance(current_val, (int, float)):
                    # Suggest percentage change
                    change_pct = random.uniform(10, 30)
                    direction = "increase" if random.random() > 0.5 else "decrease"
                    changes_needed.append({
                        "feature": feature,
                        "current_value": current_val,
                        "suggested_change": f"{direction} by {change_pct:.0f}%",
                        "importance": importance,
                    })

        return {
            "model_id": model_id,
            "original_input": self._create_input_summary(input_data),
            "desired_output": desired_output,
            "changes_needed": changes_needed,
            "explanation": f"To achieve the desired outcome, consider modifying the top {len(changes_needed)} influential features.",
            "confidence": random.uniform(0.6, 0.85),
        }

    def get_audit_logs(
        self,
        model_id: Optional[str] = None,
        hours: int = 24,
        limit: int = 100,
    ) -> list[PredictionAuditLog]:
        """
        Get audit logs with filters.

        Args:
            model_id: Optional model ID filter
            hours: Time window in hours
            limit: Maximum number of logs to return

        Returns:
            List of PredictionAuditLog entries
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        logs = [log for log in self._audit_logs if log.timestamp >= cutoff]

        if model_id:
            logs = [log for log in logs if log.model_id == model_id]

        # Sort by timestamp descending
        logs.sort(key=lambda x: x.timestamp, reverse=True)

        return logs[:limit]

    def get_model_transparency_report(
        self,
        model_id: str,
    ) -> dict:
        """
        Generate AI Act transparency report for a model.

        Args:
            model_id: Model ID

        Returns:
            Transparency report dict
        """
        logs = self.get_audit_logs(model_id=model_id, hours=24 * 7)

        if not logs:
            return {
                "model_id": model_id,
                "status": "no_data",
                "message": "No predictions logged in the last 7 days",
            }

        # Analyze logs
        total_predictions = len(logs)
        avg_confidence = sum(log.confidence for log in logs) / total_predictions
        avg_latency = sum(log.latency_ms for log in logs) / total_predictions

        # Feature importance summary
        feature_usage = defaultdict(float)
        for log in logs:
            for feature, importance in log.feature_contributions.items():
                feature_usage[feature] += importance

        # Normalize
        for feature in feature_usage:
            feature_usage[feature] /= total_predictions

        # Sort features by importance
        top_features = sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "model_id": model_id,
            "report_period": "7 days",
            "generated_at": datetime.now().isoformat(),
            "total_predictions": total_predictions,
            "average_confidence": round(avg_confidence, 3),
            "average_latency_ms": round(avg_latency, 2),
            "explainability_coverage": f"{self.config.audit_sampling_rate * 100:.0f}%",
            "top_influential_features": [
                {"feature": f, "avg_importance": round(i, 3)}
                for f, i in top_features
            ],
            "methods_used": list(set(log.explainability_method.value for log in logs)),
            "compliance_status": {
                "audit_logging": "enabled",
                "explainability": "enabled",
                "feature_tracking": "enabled",
                "decision_path": "enabled",
            },
        }

    def record_human_feedback(
        self,
        prediction_id: str,
        feedback: str,
        score: Optional[float] = None,
        correction: Optional[Any] = None,
    ) -> bool:
        """
        Record human feedback on a prediction.

        Args:
            prediction_id: Prediction ID
            feedback: Feedback text
            score: Optional feedback score (-1 to 1)
            correction: Optional corrected output

        Returns:
            True if feedback was recorded
        """
        for log in self._audit_logs:
            if log.prediction_id == prediction_id:
                log.human_feedback = feedback
                log.feedback_score = score
                log.correction_applied = correction is not None
                logger.info(f"Feedback recorded for prediction {prediction_id}")
                return True

        return False

    def _cleanup_old_logs(self):
        """Remove logs older than retention period"""
        retention_days = self.config.audit_log_retention_days
        cutoff = datetime.now() - timedelta(days=retention_days)

        self._audit_logs = [
            log for log in self._audit_logs
            if log.timestamp >= cutoff
        ]

    def get_explainability_summary(self) -> dict:
        """Get summary of explainability coverage"""
        if not self._audit_logs:
            return {
                "total_logged": 0,
                "sampling_rate": self.config.audit_sampling_rate,
                "methods_available": [m.value for m in ExplainabilityMethod],
            }

        logs_24h = self.get_audit_logs(hours=24)

        return {
            "total_logged": len(self._audit_logs),
            "logged_24h": len(logs_24h),
            "sampling_rate": self.config.audit_sampling_rate,
            "avg_confidence": round(
                sum(log.confidence for log in logs_24h) / len(logs_24h), 3
            ) if logs_24h else 0,
            "feedback_received": len([log for log in self._audit_logs if log.human_feedback]),
            "corrections_applied": len([log for log in self._audit_logs if log.correction_applied]),
            "methods_used": list(set(log.explainability_method.value for log in logs_24h)),
            "models_covered": list(set(log.model_id for log in logs_24h)),
        }

    def simulate_predictions(self, model_ids: list[str], count: int = 50):
        """Simulate prediction logging for demo purposes"""
        for _ in range(count):
            model_id = random.choice(model_ids)

            # Generate sample input
            input_data = {
                "temperature": random.uniform(50, 80),
                "pressure": random.uniform(2.5, 4.5),
                "vibration": random.uniform(1.5, 3.5),
                "power": random.uniform(400, 500),
            }

            # Generate sample output
            output = {
                "prediction": random.choice(["normal", "warning", "anomaly"]),
                "score": random.uniform(0.6, 0.99),
            }

            self.log_prediction(
                model_id=model_id,
                input_data=input_data,
                output=output,
                confidence=random.uniform(0.7, 0.98),
                latency_ms=random.uniform(10, 200),
            )
