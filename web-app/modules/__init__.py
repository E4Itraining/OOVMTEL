"""
SYNAPSIX Advanced Modules
Game-changer features for industrial observability
"""

from .nlp import NLPEngine, ConversationalQuery
from .rca import RCAEngine, CausalGraph, RootCauseResult
from .predictive import PredictiveEngine, AnomalyResult, RULPrediction
from .remediation import RemediationEngine, Runbook, RemediationAction
from .edge import EdgeAgent, EdgeConfig, EdgeMetrics

# P1 Modules - New Features
from .connectors import (
    BaseConnector, SAPConnector, KEPWAREConnector, FactoryTalkConnector,
    ConnectorConfig, SyncResult
)
from .seasonality import (
    SeasonalityEngine, STLDecomposer, PatternDetector,
    SeasonalPattern, DecompositionResult
)
from .mqtt import (
    MQTTClient, MQTTConfig, MQTTBrokerManager, MessageProcessor,
    MQTTMessage, IoTDevice, TelemetryData
)
from .alerting import (
    AlertingEngine, AdaptiveThresholdManager, AlertDeduplicator, EscalationManager,
    Alert, AlertRule, AlertSeverity
)

__all__ = [
    # NLP Module
    'NLPEngine',
    'ConversationalQuery',
    # RCA Module
    'RCAEngine',
    'CausalGraph',
    'RootCauseResult',
    # Predictive Module
    'PredictiveEngine',
    'AnomalyResult',
    'RULPrediction',
    # Remediation Module
    'RemediationEngine',
    'Runbook',
    'RemediationAction',
    # Edge Module
    'EdgeAgent',
    'EdgeConfig',
    'EdgeMetrics',
    # Connectors Module (P1)
    'BaseConnector',
    'SAPConnector',
    'KEPWAREConnector',
    'FactoryTalkConnector',
    'ConnectorConfig',
    'SyncResult',
    # Seasonality Module (P1)
    'SeasonalityEngine',
    'STLDecomposer',
    'PatternDetector',
    'SeasonalPattern',
    'DecompositionResult',
    # MQTT Module (P1)
    'MQTTClient',
    'MQTTConfig',
    'MQTTBrokerManager',
    'MessageProcessor',
    'MQTTMessage',
    'IoTDevice',
    'TelemetryData',
    # Alerting Module (P1)
    'AlertingEngine',
    'AdaptiveThresholdManager',
    'AlertDeduplicator',
    'EscalationManager',
    'Alert',
    'AlertRule',
    'AlertSeverity',
]
