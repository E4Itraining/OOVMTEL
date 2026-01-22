"""
AI Observability Models - Data structures for monitoring AI/ML systems

This module defines all the data models used for AI observability:
- Model registry and lifecycle tracking
- Drift detection (data and model)
- Performance metrics and SLOs
- Explainability and decision audit
- AI health scoring
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


# =============================================================================
# ENUMS - AI Model and Observability States
# =============================================================================

class ModelStatus(str, Enum):
    """Lifecycle status of an AI model"""
    REGISTERED = "registered"       # Model registered but not deployed
    DEPLOYING = "deploying"         # Currently being deployed
    ACTIVE = "active"               # Running in production
    DEGRADED = "degraded"           # Performance below threshold
    SHADOW = "shadow"               # Running in shadow mode (no production impact)
    CANARY = "canary"               # Canary deployment (partial traffic)
    RETIRED = "retired"             # Deprecated, no longer in use
    FAILED = "failed"               # Deployment or runtime failure


class ModelType(str, Enum):
    """Type/category of AI model"""
    ANOMALY_DETECTION = "anomaly_detection"
    PREDICTIVE_MAINTENANCE = "predictive_maintenance"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    NLP_QUERY = "nlp_query"
    TIME_SERIES_FORECAST = "time_series_forecast"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    RECOMMENDATION = "recommendation"
    LLM_ASSISTANT = "llm_assistant"
    EDGE_INFERENCE = "edge_inference"
    CUSTOM = "custom"


class DriftType(str, Enum):
    """Type of drift detected"""
    DATA_DRIFT = "data_drift"               # Input data distribution shift
    CONCEPT_DRIFT = "concept_drift"         # Relationship between X and Y changes
    PREDICTION_DRIFT = "prediction_drift"   # Output distribution shift
    FEATURE_DRIFT = "feature_drift"         # Individual feature distribution shift
    LABEL_DRIFT = "label_drift"             # Target variable distribution shift
    COVARIATE_SHIFT = "covariate_shift"     # Input distribution changes


class DriftSeverity(str, Enum):
    """Severity level of detected drift"""
    NONE = "none"               # No drift detected
    LOW = "low"                 # Minor drift, monitoring
    MEDIUM = "medium"           # Significant drift, attention needed
    HIGH = "high"               # Critical drift, action required
    CRITICAL = "critical"       # Severe drift, immediate action


class AIRiskLevel(str, Enum):
    """EU AI Act risk classification"""
    UNACCEPTABLE = "unacceptable"   # Prohibited AI systems
    HIGH = "high"                    # Subject to strict requirements
    LIMITED = "limited"              # Transparency obligations
    MINIMAL = "minimal"              # Voluntary codes of conduct


class ExplainabilityMethod(str, Enum):
    """Method used for model explainability"""
    SHAP = "shap"                       # SHAP values
    LIME = "lime"                       # Local Interpretable Model-agnostic Explanations
    INTEGRATED_GRADIENTS = "integrated_gradients"
    ATTENTION_WEIGHTS = "attention_weights"
    FEATURE_IMPORTANCE = "feature_importance"
    COUNTERFACTUAL = "counterfactual"
    RULE_EXTRACTION = "rule_extraction"
    DECISION_PATH = "decision_path"


# =============================================================================
# CORE DATA MODELS
# =============================================================================

@dataclass
class AIModel:
    """Registered AI/ML model with metadata"""
    model_id: str
    name: str
    version: str
    model_type: ModelType
    status: ModelStatus = ModelStatus.REGISTERED

    # Deployment info
    deployed_at: Optional[datetime] = None
    deployment_target: str = "central"  # central, edge, hpc
    endpoint: Optional[str] = None

    # Performance baseline
    baseline_latency_ms: float = 100.0
    baseline_throughput_rps: float = 100.0
    baseline_accuracy: float = 0.95

    # SLO definitions
    slo_latency_p99_ms: float = 500.0
    slo_error_rate_pct: float = 1.0
    slo_availability_pct: float = 99.9

    # AI Act compliance
    risk_level: AIRiskLevel = AIRiskLevel.MINIMAL
    human_oversight_required: bool = False
    transparency_documented: bool = True

    # Training info
    training_date: Optional[datetime] = None
    training_dataset: Optional[str] = None
    training_samples: int = 0

    # Metadata
    owner: str = "system"
    description: str = ""
    tags: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ModelPerformanceMetrics:
    """Real-time performance metrics for a model"""
    model_id: str
    timestamp: datetime

    # Latency metrics (milliseconds)
    latency_p50: float = 0.0
    latency_p95: float = 0.0
    latency_p99: float = 0.0
    latency_avg: float = 0.0
    latency_max: float = 0.0

    # Throughput metrics
    requests_total: int = 0
    requests_per_second: float = 0.0

    # Error metrics
    errors_total: int = 0
    error_rate_pct: float = 0.0
    timeouts_total: int = 0

    # Model-specific metrics
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mse: Optional[float] = None
    mae: Optional[float] = None

    # Resource usage
    cpu_usage_pct: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_usage_pct: Optional[float] = None
    gpu_memory_mb: Optional[float] = None

    # Inference details
    batch_size_avg: float = 1.0
    input_size_avg_bytes: float = 0.0
    output_size_avg_bytes: float = 0.0


@dataclass
class DriftDetectionResult:
    """Result of drift detection analysis"""
    model_id: str
    timestamp: datetime
    drift_type: DriftType
    severity: DriftSeverity

    # Statistical measures
    drift_score: float = 0.0              # 0-1 normalized drift score
    statistical_distance: float = 0.0      # KL divergence, PSI, etc.
    p_value: Optional[float] = None        # Statistical significance

    # Affected features/dimensions
    affected_features: list = field(default_factory=list)
    feature_drift_scores: dict = field(default_factory=dict)

    # Reference period comparison
    reference_start: Optional[datetime] = None
    reference_end: Optional[datetime] = None
    current_start: Optional[datetime] = None
    current_end: Optional[datetime] = None

    # Recommendations
    recommendation: str = ""
    requires_retraining: bool = False
    requires_immediate_action: bool = False

    # Details
    details: dict = field(default_factory=dict)


@dataclass
class PredictionAuditLog:
    """Audit log for individual predictions (explainability)"""
    prediction_id: str
    model_id: str
    timestamp: datetime

    # Input/Output
    input_hash: str = ""  # Hash of input for privacy
    input_summary: dict = field(default_factory=dict)
    prediction_output: Any = None
    confidence: float = 0.0

    # Explainability
    explainability_method: ExplainabilityMethod = ExplainabilityMethod.FEATURE_IMPORTANCE
    feature_contributions: dict = field(default_factory=dict)
    top_contributing_features: list = field(default_factory=list)
    decision_path: Optional[str] = None
    counterfactual_example: Optional[dict] = None

    # Context
    request_context: dict = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # Performance
    latency_ms: float = 0.0

    # Feedback
    human_feedback: Optional[str] = None
    feedback_score: Optional[float] = None
    correction_applied: bool = False


@dataclass
class AIHealthScore:
    """Composite health score for AI system"""
    model_id: str
    timestamp: datetime

    # Overall score (0-100)
    overall_score: float = 100.0
    status: str = "healthy"  # healthy, warning, critical

    # Component scores (0-100)
    performance_score: float = 100.0
    accuracy_score: float = 100.0
    drift_score: float = 100.0
    availability_score: float = 100.0
    resource_score: float = 100.0
    compliance_score: float = 100.0

    # SLO compliance
    slo_violations: list = field(default_factory=list)
    slo_compliance_pct: float = 100.0

    # Issues detected
    active_issues: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)

    # Trend
    score_trend: str = "stable"  # improving, stable, degrading
    score_change_24h: float = 0.0


@dataclass
class AIAlert:
    """Alert generated by AI observability system"""
    alert_id: str
    model_id: str
    timestamp: datetime

    # Alert details
    severity: str = "warning"  # info, warning, critical
    category: str = "performance"  # performance, drift, error, slo, compliance
    title: str = ""
    description: str = ""

    # Metrics
    metric_name: str = ""
    metric_value: float = 0.0
    threshold_value: float = 0.0

    # State
    state: str = "firing"  # firing, resolved
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

    # Remediation
    suggested_actions: list = field(default_factory=list)
    runbook_link: Optional[str] = None
    auto_remediation_available: bool = False


@dataclass
class ModelComparison:
    """Comparison between model versions or candidates"""
    comparison_id: str
    timestamp: datetime

    # Models being compared
    model_a_id: str
    model_a_version: str
    model_b_id: str
    model_b_version: str

    # Performance comparison
    latency_diff_pct: float = 0.0
    accuracy_diff_pct: float = 0.0
    throughput_diff_pct: float = 0.0
    error_rate_diff_pct: float = 0.0

    # Statistical significance
    sample_size: int = 0
    confidence_level: float = 0.95
    statistically_significant: bool = False

    # Resource comparison
    cpu_diff_pct: float = 0.0
    memory_diff_pct: float = 0.0

    # Winner
    recommended_model: str = ""
    recommendation_reason: str = ""


@dataclass
class FeatureStore:
    """Feature store metadata for ML features"""
    feature_id: str
    name: str
    description: str = ""

    # Source
    source_system: str = ""  # scada, mes, plm, opcua
    source_metric: str = ""

    # Statistics (for drift detection baseline)
    baseline_mean: float = 0.0
    baseline_std: float = 0.0
    baseline_min: float = 0.0
    baseline_max: float = 0.0
    baseline_distribution: dict = field(default_factory=dict)

    # Current statistics
    current_mean: float = 0.0
    current_std: float = 0.0

    # Metadata
    data_type: str = "float"
    unit: str = ""
    update_frequency_sec: int = 60
    last_updated: datetime = field(default_factory=datetime.now)

    # Usage
    used_by_models: list = field(default_factory=list)
    importance_scores: dict = field(default_factory=dict)


@dataclass
class AIObservabilityConfig:
    """Configuration for AI observability"""
    # Drift detection
    drift_detection_enabled: bool = True
    drift_check_interval_min: int = 15
    drift_threshold_low: float = 0.1
    drift_threshold_medium: float = 0.25
    drift_threshold_high: float = 0.5
    drift_window_hours: int = 24

    # Performance monitoring
    performance_sampling_rate: float = 1.0  # 100% sampling
    latency_slo_p99_ms: float = 500.0
    error_rate_slo_pct: float = 1.0

    # Alerting
    alerting_enabled: bool = True
    alert_cooldown_min: int = 5

    # Explainability
    explainability_enabled: bool = True
    audit_sampling_rate: float = 0.1  # 10% of predictions

    # Retention
    metrics_retention_days: int = 30
    audit_log_retention_days: int = 90

    # AI Act compliance
    compliance_mode: bool = True
    require_human_oversight: bool = False
