"""
Seasonality Detection - Data Models
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field


class SeasonalityType(str, Enum):
    """Types of seasonality patterns."""
    HOURLY = "hourly"           # Intra-day patterns (e.g., shifts)
    DAILY = "daily"             # Day-of-week patterns
    WEEKLY = "weekly"           # Week patterns
    MONTHLY = "monthly"         # Month patterns
    QUARTERLY = "quarterly"     # Quarter patterns
    YEARLY = "yearly"           # Annual patterns
    CUSTOM = "custom"           # Custom periodicity


class TrendType(str, Enum):
    """Types of trend components."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    POLYNOMIAL = "polynomial"
    PIECEWISE = "piecewise"
    NONE = "none"


class PatternStrength(str, Enum):
    """Strength of detected patterns."""
    STRONG = "strong"       # Very clear pattern (>0.8)
    MODERATE = "moderate"   # Noticeable pattern (0.5-0.8)
    WEAK = "weak"           # Slight pattern (0.2-0.5)
    NONE = "none"           # No pattern (<0.2)


class TrendComponent(BaseModel):
    """Trend component from decomposition."""
    trend_type: TrendType = TrendType.LINEAR
    values: List[float] = Field(default_factory=list)
    slope: float = 0.0                      # Rate of change
    intercept: float = 0.0
    r_squared: float = 0.0                  # Goodness of fit
    direction: str = "stable"               # increasing, decreasing, stable
    change_rate_per_day: float = 0.0
    projected_value_7d: Optional[float] = None
    projected_value_30d: Optional[float] = None
    change_points: List[datetime] = Field(default_factory=list)  # Detected change points


class SeasonalComponent(BaseModel):
    """Seasonal component from decomposition."""
    seasonality_type: SeasonalityType
    period: int                             # Period length in data points
    period_unit: str = "hours"              # hours, days, weeks, months
    values: List[float] = Field(default_factory=list)
    amplitude: float = 0.0                  # Peak-to-trough range
    phase_shift: float = 0.0                # Phase offset
    strength: float = 0.0                   # Seasonal strength (0-1)
    pattern_strength: PatternStrength = PatternStrength.NONE
    peak_positions: List[int] = Field(default_factory=list)  # Indices of peaks
    trough_positions: List[int] = Field(default_factory=list)  # Indices of troughs


class ResidualAnalysis(BaseModel):
    """Analysis of residual (irregular) component."""
    values: List[float] = Field(default_factory=list)
    mean: float = 0.0
    std: float = 0.0
    variance: float = 0.0
    skewness: float = 0.0
    kurtosis: float = 0.0
    is_white_noise: bool = True             # Ljung-Box test result
    autocorrelation: List[float] = Field(default_factory=list)
    outliers: List[Tuple[int, float]] = Field(default_factory=list)  # (index, value)
    outlier_count: int = 0
    outlier_percentage: float = 0.0


class DecompositionResult(BaseModel):
    """Complete STL decomposition result."""
    metric: str
    equipment: Optional[str] = None
    decomposed_at: datetime = Field(default_factory=datetime.utcnow)

    # Original data
    original_values: List[float] = Field(default_factory=list)
    timestamps: List[datetime] = Field(default_factory=list)
    data_points: int = 0

    # Decomposed components
    trend: TrendComponent = Field(default_factory=TrendComponent)
    seasonal_components: List[SeasonalComponent] = Field(default_factory=list)
    residual: ResidualAnalysis = Field(default_factory=ResidualAnalysis)

    # Quality metrics
    decomposition_quality: float = 0.0       # 0-1 quality score
    total_variance_explained: float = 0.0    # Percentage of variance explained
    seasonal_variance_ratio: float = 0.0     # Seasonal / Total variance
    trend_variance_ratio: float = 0.0        # Trend / Total variance
    residual_variance_ratio: float = 0.0     # Residual / Total variance

    # Configuration used
    stl_params: Dict[str, Any] = Field(default_factory=dict)


class SeasonalPattern(BaseModel):
    """Detected seasonal pattern."""
    pattern_id: str
    metric: str
    equipment: Optional[str] = None
    seasonality_type: SeasonalityType
    period: int
    period_unit: str = "hours"
    strength: PatternStrength
    strength_score: float = 0.0              # 0-1 numeric score

    # Pattern characteristics
    peak_time: str = ""                      # e.g., "14:00" for hourly, "Tuesday" for daily
    trough_time: str = ""
    amplitude: float = 0.0
    amplitude_percent: float = 0.0           # As percentage of mean

    # Pattern description
    description: str = ""
    typical_high: float = 0.0
    typical_low: float = 0.0
    mean_value: float = 0.0

    # Confidence and validation
    confidence: float = 0.0
    sample_size: int = 0
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class SeasonalForecast(BaseModel):
    """Forecast based on seasonal patterns."""
    metric: str
    equipment: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # Forecast data
    forecast_values: List[float] = Field(default_factory=list)
    forecast_timestamps: List[datetime] = Field(default_factory=list)
    confidence_lower: List[float] = Field(default_factory=list)
    confidence_upper: List[float] = Field(default_factory=list)
    confidence_level: float = 0.95           # Default 95% CI

    # Forecast horizon
    horizon_hours: int = 168                 # Default 7 days
    horizon_description: str = ""

    # Components contribution
    trend_contribution: List[float] = Field(default_factory=list)
    seasonal_contribution: List[float] = Field(default_factory=list)


class AnomalyContext(BaseModel):
    """Contextual anomaly based on seasonal patterns."""
    anomaly_id: str
    metric: str
    equipment: Optional[str] = None
    timestamp: datetime
    value: float

    # Expected values from seasonal model
    expected_value: float
    expected_range_low: float
    expected_range_high: float
    deviation: float
    deviation_percent: float

    # Anomaly classification
    anomaly_type: str = "contextual"         # contextual, trend_break, pattern_break
    severity: str = "medium"                 # low, medium, high, critical
    confidence: float = 0.0

    # Context
    seasonal_context: str = ""               # e.g., "Higher than expected for Tuesday 2PM"
    trend_context: str = ""                  # e.g., "Against increasing trend"
    description: str = ""


class SeasonalityAnalysis(BaseModel):
    """Complete seasonality analysis result."""
    analysis_id: str
    metric: str
    equipment: Optional[str] = None
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    analysis_duration_ms: float = 0.0

    # Decomposition
    decomposition: Optional[DecompositionResult] = None

    # Detected patterns
    patterns: List[SeasonalPattern] = Field(default_factory=list)
    dominant_pattern: Optional[SeasonalPattern] = None

    # Forecast
    forecast: Optional[SeasonalForecast] = None

    # Contextual anomalies
    contextual_anomalies: List[AnomalyContext] = Field(default_factory=list)

    # Summary
    has_seasonality: bool = False
    seasonality_types_detected: List[SeasonalityType] = Field(default_factory=list)
    summary: str = ""

    # Recommendations
    recommendations: List[str] = Field(default_factory=list)


# Standard seasonal periods
STANDARD_PERIODS = {
    SeasonalityType.HOURLY: {
        "period": 24,
        "unit": "hours",
        "description": "Intra-day pattern (24-hour cycle)",
    },
    SeasonalityType.DAILY: {
        "period": 7,
        "unit": "days",
        "description": "Day-of-week pattern (7-day cycle)",
    },
    SeasonalityType.WEEKLY: {
        "period": 4,
        "unit": "weeks",
        "description": "Weekly pattern (4-week cycle)",
    },
    SeasonalityType.MONTHLY: {
        "period": 12,
        "unit": "months",
        "description": "Monthly pattern (12-month cycle)",
    },
    SeasonalityType.QUARTERLY: {
        "period": 4,
        "unit": "quarters",
        "description": "Quarterly pattern (4-quarter cycle)",
    },
    SeasonalityType.YEARLY: {
        "period": 1,
        "unit": "years",
        "description": "Annual pattern",
    },
}


# Industry-specific seasonal patterns
INDUSTRIAL_PATTERNS = {
    "manufacturing": {
        "shift_pattern": {
            "periods": [8, 24],  # 8-hour shifts, 24-hour day
            "description": "Production shift patterns",
        },
        "maintenance_window": {
            "periods": [168],  # Weekly
            "description": "Weekly maintenance windows",
        },
    },
    "energy": {
        "demand_pattern": {
            "periods": [24, 168, 8760],  # Daily, weekly, yearly
            "description": "Energy demand patterns",
        },
    },
    "process": {
        "batch_cycle": {
            "periods": [4, 8, 12, 24],  # Common batch durations
            "description": "Batch process cycles",
        },
    },
}
