"""
RCA Module Data Models
Models for root cause analysis
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class IncidentSeverity(str, Enum):
    """Severity levels for incidents."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IncidentCategory(str, Enum):
    """Categories of incidents."""
    PERFORMANCE = "performance"      # OEE drop, slow cycle time
    QUALITY = "quality"              # Defects, quality rate drop
    AVAILABILITY = "availability"    # Downtime, equipment failure
    EQUIPMENT = "equipment"          # Equipment-specific issues
    INFRASTRUCTURE = "infrastructure"  # IT infrastructure issues
    PROCESS = "process"              # Process parameter deviations
    SAFETY = "safety"                # Safety-related incidents


class NodeType(str, Enum):
    """Types of nodes in causal graph."""
    INCIDENT = "incident"            # The reported incident (effect)
    SYMPTOM = "symptom"              # Observable symptoms
    CAUSE = "cause"                  # Potential causes
    ROOT_CAUSE = "root_cause"        # Identified root cause
    METRIC = "metric"                # Metric anomaly
    EVENT = "event"                  # System/business event
    ALERT = "alert"                  # Alert/alarm


class Incident(BaseModel):
    """Represents an incident to analyze."""
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    category: IncidentCategory
    detected_at: datetime
    equipment: Optional[str] = None
    production_line: Optional[str] = None
    metrics_affected: List[str] = Field(default_factory=list)
    impact_description: str = ""
    tags: List[str] = Field(default_factory=list)


class CausalNode(BaseModel):
    """A node in the causal graph."""
    id: str
    type: NodeType
    name: str
    description: str = ""
    timestamp: Optional[datetime] = None
    probability: float = 0.0  # Probability of being root cause (0-1)
    confidence: float = 0.0   # Confidence in the probability (0-1)
    metric_value: Optional[float] = None
    metric_baseline: Optional[float] = None
    deviation_percent: Optional[float] = None
    equipment: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CausalEdge(BaseModel):
    """An edge in the causal graph (cause -> effect)."""
    source_id: str
    target_id: str
    relationship: str = "causes"  # causes, contributes_to, correlates_with
    strength: float = 0.0         # Strength of causal relationship (0-1)
    lag_seconds: float = 0.0      # Time lag between cause and effect
    evidence: str = ""            # Evidence for this relationship
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CausalGraph(BaseModel):
    """Complete causal graph for an incident."""
    incident_id: str
    nodes: List[CausalNode] = Field(default_factory=list)
    edges: List[CausalEdge] = Field(default_factory=list)
    root_causes: List[str] = Field(default_factory=list)  # Node IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def get_node(self, node_id: str) -> Optional[CausalNode]:
        """Get node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_root_cause_nodes(self) -> List[CausalNode]:
        """Get all root cause nodes."""
        return [n for n in self.nodes if n.id in self.root_causes]

    def get_parents(self, node_id: str) -> List[CausalNode]:
        """Get parent nodes (causes) of a node."""
        parent_ids = [e.source_id for e in self.edges if e.target_id == node_id]
        return [n for n in self.nodes if n.id in parent_ids]

    def get_children(self, node_id: str) -> List[CausalNode]:
        """Get child nodes (effects) of a node."""
        child_ids = [e.target_id for e in self.edges if e.source_id == node_id]
        return [n for n in self.nodes if n.id in child_ids]

    def to_d3_format(self) -> Dict[str, Any]:
        """Convert to D3.js compatible format for visualization."""
        return {
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "type": n.type.value,
                    "probability": n.probability,
                    "isRootCause": n.id in self.root_causes
                }
                for n in self.nodes
            ],
            "links": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    "strength": e.strength,
                    "relationship": e.relationship
                }
                for e in self.edges
            ]
        }


class CorrelationResult(BaseModel):
    """Result of temporal correlation analysis."""
    metric_a: str
    metric_b: str
    correlation: float           # Pearson correlation coefficient
    lag_seconds: float           # Optimal time lag
    p_value: float               # Statistical significance
    is_significant: bool
    direction: str = ""          # "positive", "negative", "none"


class RemediationSuggestion(BaseModel):
    """Suggested remediation action."""
    id: str
    title: str
    description: str
    priority: int = 0            # 1 = highest priority
    category: str = ""           # restart, reconfigure, replace, etc.
    estimated_time_minutes: int = 0
    requires_downtime: bool = False
    auto_executable: bool = False  # Can be auto-remediated
    runbook_id: Optional[str] = None
    steps: List[str] = Field(default_factory=list)
    historical_success_rate: float = 0.0


class RootCauseResult(BaseModel):
    """A single root cause result."""
    node: CausalNode
    probability: float
    confidence: float
    evidence: List[str] = Field(default_factory=list)
    contributing_factors: List[str] = Field(default_factory=list)
    remediation: Optional[RemediationSuggestion] = None


class RCAAnalysis(BaseModel):
    """Complete RCA analysis result."""
    incident: Incident
    causal_graph: CausalGraph
    root_causes: List[RootCauseResult]
    correlations: List[CorrelationResult] = Field(default_factory=list)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    analysis_duration_ms: float = 0
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    summary: str = ""
    summary_html: str = ""

    def get_primary_root_cause(self) -> Optional[RootCauseResult]:
        """Get the most likely root cause."""
        if self.root_causes:
            return max(self.root_causes, key=lambda x: x.probability)
        return None


# Knowledge base for causal relationships
CAUSAL_KNOWLEDGE_BASE = {
    # Equipment -> Metric relationships
    "high_temperature": {
        "effects": ["reduced_oee", "quality_defects", "equipment_degradation"],
        "causes": ["cooling_failure", "overload", "ambient_temperature", "sensor_drift"],
        "category": "equipment"
    },
    "high_vibration": {
        "effects": ["equipment_failure", "quality_defects", "noise"],
        "causes": ["bearing_wear", "misalignment", "imbalance", "loose_parts"],
        "category": "equipment"
    },
    "high_pressure": {
        "effects": ["leaks", "equipment_damage", "safety_risk"],
        "causes": ["valve_stuck", "blockage", "pump_failure", "setpoint_error"],
        "category": "process"
    },
    "oee_drop": {
        "effects": ["production_target_miss", "cost_increase"],
        "causes": ["availability_drop", "performance_drop", "quality_drop", "unplanned_downtime"],
        "category": "performance"
    },
    "quality_drop": {
        "effects": ["oee_drop", "customer_complaints", "waste_increase"],
        "causes": ["process_drift", "material_issue", "equipment_calibration", "operator_error"],
        "category": "quality"
    },
    # IT/OT Infrastructure
    "high_cpu": {
        "effects": ["slow_response", "data_loss", "service_degradation"],
        "causes": ["memory_leak", "infinite_loop", "high_load", "malware"],
        "category": "infrastructure"
    },
    "high_memory": {
        "effects": ["service_crash", "slow_response", "oom_kill"],
        "causes": ["memory_leak", "cache_overflow", "insufficient_resources"],
        "category": "infrastructure"
    },
    "network_latency": {
        "effects": ["data_delay", "timeout", "sync_failure"],
        "causes": ["bandwidth_saturation", "packet_loss", "routing_issue", "dns_failure"],
        "category": "infrastructure"
    },
}

# Historical pattern database (simulated)
HISTORICAL_PATTERNS = [
    {
        "pattern_id": "PAT-001",
        "signature": ["high_temperature", "high_vibration"],
        "root_cause": "bearing_failure",
        "remediation": "replace_bearing",
        "occurrences": 15,
        "success_rate": 0.92
    },
    {
        "pattern_id": "PAT-002",
        "signature": ["oee_drop", "high_cycle_time"],
        "root_cause": "process_bottleneck",
        "remediation": "optimize_process",
        "occurrences": 8,
        "success_rate": 0.85
    },
    {
        "pattern_id": "PAT-003",
        "signature": ["quality_drop", "temperature_drift"],
        "root_cause": "sensor_calibration",
        "remediation": "recalibrate_sensor",
        "occurrences": 12,
        "success_rate": 0.95
    },
    {
        "pattern_id": "PAT-004",
        "signature": ["high_cpu", "slow_response", "data_loss"],
        "root_cause": "memory_leak",
        "remediation": "restart_service",
        "occurrences": 20,
        "success_rate": 0.98
    },
]
