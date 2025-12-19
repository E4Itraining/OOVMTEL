"""
Data Lineage - Data Models
Track data flow from source to visualization
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class NodeType(str, Enum):
    """Types of lineage nodes."""
    SOURCE = "source"           # Data source (sensor, database, API)
    INGESTION = "ingestion"     # Data ingestion point
    TRANSFORM = "transform"     # Transformation step
    AGGREGATION = "aggregation" # Aggregation step
    STORAGE = "storage"         # Storage destination
    MODEL = "model"             # ML model
    METRIC = "metric"           # Calculated metric
    VISUALIZATION = "visualization"  # Dashboard/chart
    ALERT = "alert"             # Alert definition
    EXPORT = "export"           # Data export


class EdgeType(str, Enum):
    """Types of lineage edges."""
    FLOW = "flow"               # Data flows from A to B
    DERIVES = "derives"         # B is derived from A
    USES = "uses"               # B uses A as input
    TRIGGERS = "triggers"       # A triggers B
    VALIDATES = "validates"     # A validates B


class DataQuality(str, Enum):
    """Data quality levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNKNOWN = "unknown"


class LineageNode(BaseModel):
    """A node in the data lineage graph."""
    node_id: str = Field(default_factory=lambda: f"node_{uuid.uuid4().hex[:8]}")
    name: str
    node_type: NodeType
    description: str = ""

    # Location
    system: str = ""            # System name (e.g., "SCADA", "InfluxDB")
    location: str = ""          # Path or identifier within system

    # Metadata
    owner: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)

    # Schema information
    schema_fields: List[Dict[str, str]] = Field(default_factory=list)
    # e.g., [{"name": "temperature", "type": "float", "unit": "°C"}]

    # Quality
    data_quality: DataQuality = DataQuality.UNKNOWN
    freshness_seconds: Optional[int] = None
    update_frequency: Optional[str] = None  # e.g., "1m", "1h", "daily"

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)

    # Status
    is_active: bool = True
    is_deprecated: bool = False


class LineageEdge(BaseModel):
    """An edge connecting two nodes in the lineage graph."""
    edge_id: str = Field(default_factory=lambda: f"edge_{uuid.uuid4().hex[:8]}")
    source_node_id: str
    target_node_id: str
    edge_type: EdgeType = EdgeType.FLOW

    # Transformation details
    transformation: Optional[str] = None  # Description or SQL/formula
    transformation_type: Optional[str] = None  # e.g., "filter", "aggregate", "join"

    # Data flow characteristics
    latency_ms: Optional[float] = None
    throughput_records_per_sec: Optional[float] = None

    # Metadata
    properties: Dict[str, Any] = Field(default_factory=dict)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Status
    is_active: bool = True


class LineageGraph(BaseModel):
    """Complete data lineage graph."""
    graph_id: str = Field(default_factory=lambda: f"graph_{uuid.uuid4().hex[:8]}")
    name: str = "Data Lineage"
    description: str = ""

    nodes: Dict[str, LineageNode] = Field(default_factory=dict)
    edges: List[LineageEdge] = Field(default_factory=list)

    # Computed
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DataFlowPath(BaseModel):
    """A path through the lineage graph."""
    path_id: str = Field(default_factory=lambda: f"path_{uuid.uuid4().hex[:8]}")
    nodes: List[str] = Field(default_factory=list)  # Node IDs in order
    edges: List[str] = Field(default_factory=list)  # Edge IDs in order

    # Computed metrics
    total_latency_ms: float = 0.0
    transformation_count: int = 0
    quality_score: float = 0.0


class ImpactAnalysis(BaseModel):
    """Analysis of impact when a node changes."""
    source_node_id: str
    source_node_name: str

    # Downstream impact
    affected_nodes: List[Dict[str, Any]] = Field(default_factory=list)
    # e.g., [{"node_id": "...", "name": "...", "type": "...", "distance": 2}]

    affected_visualizations: List[str] = Field(default_factory=list)
    affected_alerts: List[str] = Field(default_factory=list)
    affected_models: List[str] = Field(default_factory=list)

    # Metrics
    total_affected: int = 0
    max_distance: int = 0

    # Recommendations
    risk_level: str = "low"  # low, medium, high, critical
    recommendations: List[str] = Field(default_factory=list)


class DataProvenance(BaseModel):
    """Provenance information for a data point."""
    data_id: str
    value: Any
    timestamp: datetime

    # Source
    source_node_id: str
    source_system: str

    # Lineage
    path: DataFlowPath
    transformations_applied: List[str] = Field(default_factory=list)

    # Quality
    confidence: float = 1.0  # 0.0 to 1.0
    quality: DataQuality = DataQuality.UNKNOWN

    # Audit
    processing_timestamps: Dict[str, datetime] = Field(default_factory=dict)


class LineageSnapshot(BaseModel):
    """Point-in-time snapshot of lineage state."""
    snapshot_id: str = Field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:8]}")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # State
    graph: LineageGraph

    # Statistics
    node_count: int = 0
    edge_count: int = 0
    source_count: int = 0
    visualization_count: int = 0

    # Health
    active_paths: int = 0
    broken_paths: int = 0
    deprecated_nodes: int = 0


class LineageEvent(BaseModel):
    """Event in lineage history."""
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    event_type: str  # node_added, node_removed, edge_added, schema_changed, etc.
    node_id: Optional[str] = None
    edge_id: Optional[str] = None

    # Details
    description: str = ""
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None

    # Actor
    actor: Optional[str] = None  # User or system that made the change


# Standard data source templates
STANDARD_DATA_SOURCES = {
    "opcua_server": LineageNode(
        node_id="tpl_opcua",
        name="OPC-UA Server",
        node_type=NodeType.SOURCE,
        description="Industrial OPC-UA data source",
        system="OPC-UA",
        properties={"protocol": "opc.tcp", "port": 4840},
        update_frequency="100ms",
    ),
    "mqtt_broker": LineageNode(
        node_id="tpl_mqtt",
        name="MQTT Broker",
        node_type=NodeType.SOURCE,
        description="MQTT message broker",
        system="MQTT",
        properties={"protocol": "mqtt", "port": 1883},
    ),
    "influxdb": LineageNode(
        node_id="tpl_influxdb",
        name="InfluxDB",
        node_type=NodeType.STORAGE,
        description="Time-series database",
        system="InfluxDB",
        properties={"type": "tsdb"},
    ),
    "postgresql": LineageNode(
        node_id="tpl_postgres",
        name="PostgreSQL",
        node_type=NodeType.STORAGE,
        description="Relational database",
        system="PostgreSQL",
        properties={"type": "rdbms"},
    ),
    "grafana_dashboard": LineageNode(
        node_id="tpl_grafana",
        name="Grafana Dashboard",
        node_type=NodeType.VISUALIZATION,
        description="Grafana visualization",
        system="Grafana",
    ),
    "synapsix_dashboard": LineageNode(
        node_id="tpl_synapsix",
        name="SYNAPSIX Dashboard",
        node_type=NodeType.VISUALIZATION,
        description="SYNAPSIX analytics dashboard",
        system="SYNAPSIX",
    ),
}


# Standard transformation types
TRANSFORMATION_TYPES = {
    "filter": {
        "name": "Filter",
        "description": "Filter data based on conditions",
        "icon": "filter",
    },
    "aggregate": {
        "name": "Aggregate",
        "description": "Aggregate data (sum, avg, min, max)",
        "icon": "sigma",
    },
    "join": {
        "name": "Join",
        "description": "Join multiple data sources",
        "icon": "git-merge",
    },
    "enrich": {
        "name": "Enrich",
        "description": "Add additional data fields",
        "icon": "plus-circle",
    },
    "normalize": {
        "name": "Normalize",
        "description": "Normalize or scale values",
        "icon": "sliders",
    },
    "calculate": {
        "name": "Calculate",
        "description": "Calculate derived values",
        "icon": "calculator",
    },
    "clean": {
        "name": "Clean",
        "description": "Clean and validate data",
        "icon": "check-circle",
    },
    "downsample": {
        "name": "Downsample",
        "description": "Reduce data resolution",
        "icon": "trending-down",
    },
}
