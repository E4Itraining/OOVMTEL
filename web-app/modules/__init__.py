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

# P2-P3 Modules - Advanced Features
from .visualization3d import (
    Visualization3DEngine, SceneBuilder, HeatmapGenerator,
    Scene3D, Equipment3D, HeatmapData
)
from .voice import (
    VoiceEngine, SpeechRecognizer, VoiceCommandHandler,
    VoiceCommand, VoiceSession, SpeechResult
)
from .kpi_builder import (
    KPIBuilderEngine, KPICalculator, BenchmarkManager,
    KPIDefinition, KPIResult, KPICategory, Benchmark
)
from .lineage import (
    DataLineageEngine, GraphManager, ImpactAnalyzer,
    LineageNode, LineageEdge, NodeType, EdgeType
)
from .ml_models import (
    MLModelsEngine, ModelManager, InferenceEngine,
    PretrainedModel, HealthScore, EquipmentType, ModelType
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
    # Visualization 3D Module (P2)
    'Visualization3DEngine',
    'SceneBuilder',
    'HeatmapGenerator',
    'Scene3D',
    'Equipment3D',
    'HeatmapData',
    # Voice Module (P2)
    'VoiceEngine',
    'SpeechRecognizer',
    'VoiceCommandHandler',
    'VoiceCommand',
    'VoiceSession',
    'SpeechResult',
    # KPI Builder Module (P2)
    'KPIBuilderEngine',
    'KPICalculator',
    'BenchmarkManager',
    'KPIDefinition',
    'KPIResult',
    'KPICategory',
    'Benchmark',
    # Data Lineage Module (P3)
    'DataLineageEngine',
    'GraphManager',
    'ImpactAnalyzer',
    'LineageNode',
    'LineageEdge',
    'NodeType',
    'EdgeType',
    # ML Models Module (P3)
    'MLModelsEngine',
    'ModelManager',
    'InferenceEngine',
    'PretrainedModel',
    'HealthScore',
    'EquipmentType',
    'ModelType',
]
