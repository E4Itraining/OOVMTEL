"""
Predictive Maintenance Module Data Models
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class AnomalyType(str, Enum):
    """Types of anomalies detected."""
    POINT = "point"              # Single point anomaly
    CONTEXTUAL = "contextual"    # Anomaly in context (e.g., night vs day)
    COLLECTIVE = "collective"    # Group of points forming anomaly
    TREND = "trend"              # Trend-based anomaly
    SEASONAL = "seasonal"        # Deviation from seasonal pattern


class AnomalySeverity(str, Enum):
    """Severity levels for anomalies."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TrendDirection(str, Enum):
    """Direction of a trend."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class AnomalyResult(BaseModel):
    """Result of anomaly detection."""
    id: str
    metric: str
    equipment: Optional[str] = None
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    timestamp: datetime
    value: float
    expected_value: float
    deviation_score: float  # Z-score or similar
    confidence: float
    description: str = ""
    contributing_factors: List[str] = Field(default_factory=list)
    is_correlated: bool = False  # Part of correlated anomaly cluster
    related_anomalies: List[str] = Field(default_factory=list)


class TrendAnalysis(BaseModel):
    """Result of trend analysis."""
    metric: str
    equipment: Optional[str] = None
    direction: TrendDirection
    slope: float                    # Rate of change
    slope_unit: str = "per_hour"    # Unit of slope
    r_squared: float = 0.0          # Goodness of fit
    start_value: float
    current_value: float
    projected_value_24h: float
    projected_value_7d: float
    change_percent_24h: float
    is_concerning: bool = False
    threshold_breach_eta: Optional[timedelta] = None  # Time until threshold breach
    analysis_period: str = ""


class RULPrediction(BaseModel):
    """Remaining Useful Life prediction."""
    equipment: str
    component: Optional[str] = None
    rul_hours: float                # Estimated remaining hours
    rul_days: float                 # Estimated remaining days
    confidence_interval_low: float  # Lower bound (hours)
    confidence_interval_high: float # Upper bound (hours)
    confidence: float               # Confidence in prediction
    health_score: float             # Current health (0-100)
    degradation_rate: float         # Rate of degradation
    failure_mode: str = ""          # Expected failure mode
    key_indicators: List[str] = Field(default_factory=list)
    recommended_action: str = ""
    last_maintenance: Optional[datetime] = None
    predicted_failure_date: Optional[datetime] = None


class FailurePrediction(BaseModel):
    """Failure probability prediction."""
    equipment: str
    component: Optional[str] = None
    failure_probability_24h: float  # P(failure) in next 24h
    failure_probability_7d: float   # P(failure) in next 7 days
    failure_probability_30d: float  # P(failure) in next 30 days
    risk_level: str                 # critical, high, medium, low
    primary_risk_factors: List[str] = Field(default_factory=list)
    warning_signs: List[str] = Field(default_factory=list)
    historical_mtbf: Optional[float] = None  # Mean Time Between Failures (hours)
    similar_failures_count: int = 0


class MaintenanceRecommendation(BaseModel):
    """Maintenance scheduling recommendation."""
    id: str
    equipment: str
    recommendation_type: str  # preventive, predictive, corrective
    priority: int             # 1 = highest
    title: str
    description: str
    recommended_date: datetime
    deadline_date: Optional[datetime] = None
    estimated_duration_hours: float
    required_parts: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    estimated_cost: Optional[float] = None
    risk_if_delayed: str = ""
    based_on: List[str] = Field(default_factory=list)  # What triggered this recommendation


class EquipmentHealth(BaseModel):
    """Overall equipment health assessment."""
    equipment: str
    overall_score: float            # 0-100
    availability_score: float
    performance_score: float
    quality_score: float
    condition_score: float          # Physical condition based on sensors
    trend: TrendDirection
    status: str                     # healthy, degrading, critical
    anomalies_count: int = 0
    active_warnings: List[str] = Field(default_factory=list)
    rul: Optional[RULPrediction] = None
    failure_prediction: Optional[FailurePrediction] = None
    maintenance_recommendations: List[MaintenanceRecommendation] = Field(default_factory=list)
    last_maintenance: Optional[datetime] = None
    next_scheduled_maintenance: Optional[datetime] = None


class PredictiveAnalysis(BaseModel):
    """Complete predictive analysis result."""
    analysis_id: str
    analyzed_at: datetime
    analysis_duration_ms: float
    equipment_health: List[EquipmentHealth] = Field(default_factory=list)
    anomalies: List[AnomalyResult] = Field(default_factory=list)
    trends: List[TrendAnalysis] = Field(default_factory=list)
    rul_predictions: List[RULPrediction] = Field(default_factory=list)
    failure_predictions: List[FailurePrediction] = Field(default_factory=list)
    maintenance_recommendations: List[MaintenanceRecommendation] = Field(default_factory=list)
    summary: str = ""
    alerts: List[Dict[str, Any]] = Field(default_factory=list)


# Equipment degradation models (simplified)
DEGRADATION_MODELS = {
    "pump": {
        "critical_metrics": ["vibration", "temperature", "pressure", "flow_rate"],
        "failure_modes": ["bearing_failure", "seal_leak", "impeller_damage", "motor_burnout"],
        "typical_mtbf_hours": 8760,  # 1 year
        "degradation_indicators": {
            "vibration": {"warning": 5.0, "critical": 10.0, "unit": "mm/s"},
            "temperature": {"warning": 70, "critical": 85, "unit": "°C"},
            "pressure_drop": {"warning": 10, "critical": 20, "unit": "%"},
        }
    },
    "reactor": {
        "critical_metrics": ["temperature", "pressure", "flow_rate"],
        "failure_modes": ["overheat", "pressure_breach", "corrosion"],
        "typical_mtbf_hours": 17520,  # 2 years
        "degradation_indicators": {
            "temperature": {"warning": 150, "critical": 200, "unit": "°C"},
            "pressure": {"warning": 8, "critical": 10, "unit": "bar"},
        }
    },
    "conveyor": {
        "critical_metrics": ["vibration", "motor_current", "belt_tension"],
        "failure_modes": ["belt_wear", "motor_failure", "bearing_failure"],
        "typical_mtbf_hours": 4380,  # 6 months
        "degradation_indicators": {
            "vibration": {"warning": 3.0, "critical": 6.0, "unit": "mm/s"},
            "motor_current": {"warning": 110, "critical": 130, "unit": "% rated"},
        }
    },
    "mixer": {
        "critical_metrics": ["vibration", "temperature", "power"],
        "failure_modes": ["seal_failure", "bearing_wear", "blade_damage"],
        "typical_mtbf_hours": 6000,
        "degradation_indicators": {
            "vibration": {"warning": 4.0, "critical": 8.0, "unit": "mm/s"},
            "temperature": {"warning": 60, "critical": 80, "unit": "°C"},
        }
    },
    "furnace": {
        "critical_metrics": ["temperature", "fuel_consumption", "emissions"],
        "failure_modes": ["refractory_damage", "burner_failure", "control_failure"],
        "typical_mtbf_hours": 26280,  # 3 years
        "degradation_indicators": {
            "temperature_uniformity": {"warning": 5, "critical": 10, "unit": "%"},
            "fuel_efficiency": {"warning": 90, "critical": 85, "unit": "%"},
        }
    },
    "default": {
        "critical_metrics": ["temperature", "vibration", "power"],
        "failure_modes": ["general_failure"],
        "typical_mtbf_hours": 8760,
        "degradation_indicators": {
            "temperature": {"warning": 70, "critical": 90, "unit": "°C"},
            "vibration": {"warning": 5.0, "critical": 10.0, "unit": "mm/s"},
        }
    }
}


# Maintenance interval recommendations
MAINTENANCE_INTERVALS = {
    "inspection": timedelta(days=7),
    "lubrication": timedelta(days=30),
    "filter_change": timedelta(days=90),
    "calibration": timedelta(days=180),
    "major_overhaul": timedelta(days=365),
}
