"""
Intelligent Alerting - Data Models
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"     # Immediate action required
    HIGH = "high"             # Urgent attention needed
    MEDIUM = "medium"         # Should be addressed soon
    LOW = "low"               # Informational
    INFO = "info"             # For awareness only


class AlertState(str, Enum):
    """Alert lifecycle states."""
    ACTIVE = "active"                 # Alert is firing
    ACKNOWLEDGED = "acknowledged"     # Someone is aware
    SUPPRESSED = "suppressed"         # Temporarily suppressed
    RESOLVED = "resolved"             # Issue resolved
    CLOSED = "closed"                 # Manually closed


class AlertType(str, Enum):
    """Types of alerts."""
    THRESHOLD = "threshold"           # Value crossed threshold
    ANOMALY = "anomaly"               # Anomaly detected
    TREND = "trend"                   # Concerning trend
    AVAILABILITY = "availability"     # System/equipment down
    PREDICTION = "prediction"         # Predicted issue
    CORRELATION = "correlation"       # Correlated events
    PATTERN = "pattern"               # Pattern deviation


class ThresholdType(str, Enum):
    """Types of threshold evaluation."""
    STATIC = "static"                 # Fixed values
    ADAPTIVE = "adaptive"             # Dynamic based on history
    SEASONAL = "seasonal"             # Varies by time/season
    BASELINE = "baseline"             # Deviation from baseline
    RATE_OF_CHANGE = "rate_of_change" # Based on rate of change


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    SMS = "sms"
    WEBHOOK = "webhook"
    PAGERDUTY = "pagerduty"
    OPSGENIE = "opsgenie"
    IN_APP = "in_app"


class EscalationLevel(int, Enum):
    """Escalation levels."""
    L1 = 1  # First responder
    L2 = 2  # Technical specialist
    L3 = 3  # Senior engineer
    L4 = 4  # Management
    L5 = 5  # Executive


class ThresholdConfig(BaseModel):
    """Threshold configuration."""
    threshold_type: ThresholdType = ThresholdType.STATIC

    # Static thresholds
    warning_value: Optional[float] = None
    critical_value: Optional[float] = None
    comparison: str = "greater_than"  # greater_than, less_than, equals, not_equals

    # Adaptive thresholds
    adaptive_enabled: bool = False
    sensitivity: float = 2.0          # Standard deviations
    baseline_window_hours: int = 168  # 7 days
    min_samples: int = 100

    # Seasonal adjustment
    seasonal_enabled: bool = False
    seasonal_period_hours: int = 24

    # Rate of change
    rate_of_change_enabled: bool = False
    rate_window_minutes: int = 5
    max_rate_per_minute: Optional[float] = None

    # Hysteresis (to prevent flapping)
    hysteresis_percent: float = 5.0   # % buffer before clearing


class AlertRule(BaseModel):
    """Alert rule definition."""
    rule_id: str
    name: str
    description: str = ""
    enabled: bool = True

    # Targeting
    metric: str
    equipment_filter: Optional[str] = None  # Regex pattern
    labels: Dict[str, str] = Field(default_factory=dict)

    # Thresholds
    threshold: ThresholdConfig = Field(default_factory=ThresholdConfig)

    # Timing
    evaluation_interval_seconds: int = 60
    for_duration_seconds: int = 0     # Must be true for this long
    pending_period_seconds: int = 0   # Wait before first alert

    # Severity mapping
    warning_severity: AlertSeverity = AlertSeverity.MEDIUM
    critical_severity: AlertSeverity = AlertSeverity.HIGH

    # Notifications
    notification_channels: List[NotificationChannel] = Field(default_factory=list)
    notify_on_resolve: bool = True
    repeat_interval_minutes: int = 60  # Re-notify if still active

    # Grouping
    group_by: List[str] = Field(default_factory=list)  # e.g., ["equipment", "location"]
    group_wait_seconds: int = 30      # Wait for group to fill

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class Alert(BaseModel):
    """Alert instance."""
    alert_id: str
    rule_id: str
    rule_name: str

    # Classification
    severity: AlertSeverity
    alert_type: AlertType = AlertType.THRESHOLD
    state: AlertState = AlertState.ACTIVE

    # Context
    metric: str
    equipment: Optional[str] = None
    location: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)

    # Values
    current_value: float
    threshold_value: float
    baseline_value: Optional[float] = None
    deviation_percent: Optional[float] = None

    # Description
    title: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)

    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_triggered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    duration_seconds: int = 0

    # Ownership
    acknowledged_by: Optional[str] = None
    assigned_to: Optional[str] = None

    # Escalation
    escalation_level: EscalationLevel = EscalationLevel.L1
    escalation_count: int = 0
    last_escalated_at: Optional[datetime] = None

    # Notifications
    notifications_sent: int = 0
    last_notification_at: Optional[datetime] = None

    # Correlation
    correlation_id: Optional[str] = None  # Group of related alerts
    parent_alert_id: Optional[str] = None
    child_alert_ids: List[str] = Field(default_factory=list)

    # Deduplication
    fingerprint: str = ""             # Unique identifier for dedup
    occurrence_count: int = 1
    first_occurrence: datetime = Field(default_factory=datetime.utcnow)

    # Impact
    estimated_impact: Optional[str] = None
    affected_systems: List[str] = Field(default_factory=list)


class AlertGroup(BaseModel):
    """Group of related alerts."""
    group_id: str
    name: str
    description: str = ""

    # Grouping criteria
    group_key: str                    # Computed from group_by fields
    group_labels: Dict[str, str] = Field(default_factory=dict)

    # Alerts
    alert_ids: List[str] = Field(default_factory=list)
    alert_count: int = 0

    # Severity (highest in group)
    severity: AlertSeverity = AlertSeverity.LOW

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_alert_at: datetime = Field(default_factory=datetime.utcnow)

    # State
    state: AlertState = AlertState.ACTIVE


class AlertCorrelation(BaseModel):
    """Correlation between alerts."""
    correlation_id: str
    name: str
    description: str = ""

    # Correlated alerts
    alert_ids: List[str] = Field(default_factory=list)
    primary_alert_id: Optional[str] = None

    # Correlation info
    correlation_type: str = "temporal"  # temporal, causal, equipment
    correlation_score: float = 0.0
    time_window_seconds: int = 300

    # Root cause
    probable_root_cause: Optional[str] = None
    root_cause_confidence: float = 0.0

    # Timing
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationConfig(BaseModel):
    """Notification configuration."""
    channel: NotificationChannel
    enabled: bool = True

    # Channel-specific settings
    recipients: List[str] = Field(default_factory=list)
    webhook_url: Optional[str] = None

    # Filtering
    min_severity: AlertSeverity = AlertSeverity.LOW
    include_rules: List[str] = Field(default_factory=list)  # Rule IDs
    exclude_rules: List[str] = Field(default_factory=list)

    # Timing
    quiet_hours_start: Optional[str] = None  # "22:00"
    quiet_hours_end: Optional[str] = None    # "07:00"
    quiet_days: List[str] = Field(default_factory=list)  # ["Saturday", "Sunday"]

    # Rate limiting
    max_notifications_per_hour: int = 100


class EscalationConfig(BaseModel):
    """Escalation policy configuration."""
    policy_id: str
    name: str
    description: str = ""
    enabled: bool = True

    # Levels
    levels: List[Dict[str, Any]] = Field(default_factory=list)
    # Each level: {"level": 1, "delay_minutes": 15, "recipients": [...], "channels": [...]}

    # Timing
    repeat_interval_minutes: int = 30
    max_escalations: int = 5

    # Conditions
    auto_resolve_after_minutes: Optional[int] = None
    stop_on_acknowledge: bool = True


# Standard alert templates
ALERT_TEMPLATES = {
    "equipment_temperature": {
        "name": "Equipment Temperature Alert",
        "metric": "temperature",
        "threshold": {
            "threshold_type": "adaptive",
            "warning_value": 70,
            "critical_value": 85,
            "adaptive_enabled": True,
            "sensitivity": 2.5,
        },
        "message_template": "{equipment} temperature is {state}: {value}°C (threshold: {threshold}°C)",
    },
    "equipment_vibration": {
        "name": "Equipment Vibration Alert",
        "metric": "vibration",
        "threshold": {
            "threshold_type": "baseline",
            "sensitivity": 3.0,
        },
        "message_template": "{equipment} vibration anomaly: {value} mm/s ({deviation}% above baseline)",
    },
    "oee_drop": {
        "name": "OEE Performance Drop",
        "metric": "oee",
        "threshold": {
            "threshold_type": "rate_of_change",
            "comparison": "less_than",
            "warning_value": 80,
            "critical_value": 70,
        },
        "message_template": "OEE dropped to {value}% for {equipment}",
    },
    "connectivity": {
        "name": "Device Connectivity",
        "metric": "heartbeat",
        "threshold": {
            "threshold_type": "static",
            "for_duration_seconds": 300,  # 5 minutes
        },
        "message_template": "{equipment} has been offline for {duration}",
    },
}


# Severity to priority mapping
SEVERITY_PRIORITY = {
    AlertSeverity.CRITICAL: 1,
    AlertSeverity.HIGH: 2,
    AlertSeverity.MEDIUM: 3,
    AlertSeverity.LOW: 4,
    AlertSeverity.INFO: 5,
}


# Default escalation timing (minutes)
DEFAULT_ESCALATION_DELAYS = {
    AlertSeverity.CRITICAL: [5, 10, 15, 30],
    AlertSeverity.HIGH: [15, 30, 60, 120],
    AlertSeverity.MEDIUM: [60, 120, 240],
    AlertSeverity.LOW: [240, 480],
    AlertSeverity.INFO: [],
}
