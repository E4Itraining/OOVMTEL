"""
Intelligent Alerting Module
Advanced alerting with adaptive thresholds, deduplication, and escalation for SYNAPSIX
"""

from .engine import AlertingEngine
from .adaptive_thresholds import AdaptiveThresholdManager
from .deduplication import AlertDeduplicator
from .escalation import EscalationManager, EscalationPolicy
from .models import (
    Alert,
    AlertSeverity,
    AlertState,
    AlertRule,
    ThresholdConfig,
    EscalationLevel,
    NotificationChannel,
    AlertGroup,
    AlertCorrelation,
)

__all__ = [
    # Engine
    'AlertingEngine',
    # Adaptive Thresholds
    'AdaptiveThresholdManager',
    # Deduplication
    'AlertDeduplicator',
    # Escalation
    'EscalationManager',
    'EscalationPolicy',
    # Models
    'Alert',
    'AlertSeverity',
    'AlertState',
    'AlertRule',
    'ThresholdConfig',
    'EscalationLevel',
    'NotificationChannel',
    'AlertGroup',
    'AlertCorrelation',
]
