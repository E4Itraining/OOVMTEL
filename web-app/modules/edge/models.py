"""
Edge Computing Module Data Models
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class EdgeStatus(str, Enum):
    """Status of an edge agent."""
    ONLINE = "online"
    OFFLINE = "offline"
    SYNCING = "syncing"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class SyncStatus(str, Enum):
    """Status of data sync."""
    SYNCED = "synced"
    PENDING = "pending"
    SYNCING = "syncing"
    FAILED = "failed"
    BUFFERED = "buffered"


class AggregationType(str, Enum):
    """Types of data aggregation."""
    NONE = "none"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    SUM = "sum"
    COUNT = "count"
    P50 = "p50"
    P95 = "p95"
    P99 = "p99"


class EdgeConfig(BaseModel):
    """Configuration for an edge agent."""
    model_config = {"protected_namespaces": ()}

    agent_id: str
    site_name: str
    location: str = ""

    # Central connection
    central_url: str
    api_key: Optional[str] = None

    # Data collection
    collection_interval_seconds: int = 10
    aggregation_interval_seconds: int = 60
    aggregation_type: AggregationType = AggregationType.AVG

    # Buffer settings
    buffer_size_mb: int = 100
    buffer_retention_hours: int = 24
    sync_batch_size: int = 1000

    # Network settings
    sync_interval_seconds: int = 60
    offline_mode_threshold_seconds: int = 300
    compression_enabled: bool = True

    # Processing settings
    local_anomaly_detection: bool = True
    anomaly_threshold: float = 2.5
    local_alerting: bool = True

    # Resource limits
    max_cpu_percent: int = 50
    max_memory_mb: int = 512

    # Model deployment
    models_enabled: bool = True
    model_update_interval_hours: int = 24


class EdgeMetrics(BaseModel):
    """Metrics collected by edge agent."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Performance
    cpu_usage: float = 0
    memory_usage_mb: float = 0
    disk_usage_mb: float = 0

    # Data flow
    data_points_collected: int = 0
    data_points_aggregated: int = 0
    data_points_synced: int = 0
    data_points_buffered: int = 0

    # Network
    bytes_sent: int = 0
    bytes_received: int = 0
    last_sync_at: Optional[datetime] = None
    sync_latency_ms: float = 0

    # Processing
    anomalies_detected: int = 0
    alerts_generated: int = 0
    models_deployed: int = 0

    # Health
    uptime_seconds: int = 0
    errors_count: int = 0


class DataPoint(BaseModel):
    """A single data point."""
    timestamp: datetime
    metric: str
    value: float
    equipment: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    source: str = "edge"


class AggregatedData(BaseModel):
    """Aggregated data ready for sync."""
    start_time: datetime
    end_time: datetime
    metric: str
    equipment: Optional[str] = None

    # Aggregated values
    count: int = 0
    sum: float = 0
    min: float = 0
    max: float = 0
    avg: float = 0
    p50: Optional[float] = None
    p95: Optional[float] = None
    p99: Optional[float] = None

    # Metadata
    labels: Dict[str, str] = Field(default_factory=dict)
    source_agent: str = ""
    sync_status: SyncStatus = SyncStatus.PENDING


class DataBuffer(BaseModel):
    """Buffer for storing data when offline."""
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    size_bytes: int = 0
    data_points_count: int = 0
    oldest_data: Optional[datetime] = None
    newest_data: Optional[datetime] = None
    sync_status: SyncStatus = SyncStatus.BUFFERED
    sync_attempts: int = 0
    last_sync_attempt: Optional[datetime] = None
    last_sync_error: Optional[str] = None


class EdgeAlert(BaseModel):
    """Alert generated at the edge."""
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: str                       # critical, warning, info
    metric: str
    equipment: Optional[str] = None
    message: str
    value: float
    threshold: float
    acknowledged: bool = False
    synced: bool = False
    agent_id: str = ""


class ModelDeployment(BaseModel):
    """ML model deployed to edge."""
    model_config = {"protected_namespaces": ()}

    id: str
    name: str
    version: str
    type: str                           # anomaly_detection, forecasting, classification
    deployed_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"              # active, inactive, updating
    accuracy: float = 0.0
    predictions_made: int = 0
    model_size_kb: int = 0
    input_features: List[str] = Field(default_factory=list)
    output_labels: List[str] = Field(default_factory=list)


class EdgeSite(BaseModel):
    """Representation of an edge site."""
    agent_id: str
    site_name: str
    location: str
    status: EdgeStatus = EdgeStatus.OFFLINE
    last_seen: Optional[datetime] = None
    config: Optional[EdgeConfig] = None
    metrics: Optional[EdgeMetrics] = None
    deployed_models: List[ModelDeployment] = Field(default_factory=list)
    active_alerts: List[EdgeAlert] = Field(default_factory=list)
    buffer_status: Optional[DataBuffer] = None


# Default edge configurations for different scenarios
EDGE_PRESETS = {
    "high_volume": EdgeConfig(
        agent_id="",
        site_name="",
        central_url="",
        collection_interval_seconds=5,
        aggregation_interval_seconds=30,
        aggregation_type=AggregationType.AVG,
        buffer_size_mb=500,
        sync_interval_seconds=30,
        compression_enabled=True,
        local_anomaly_detection=True,
        max_cpu_percent=70,
        max_memory_mb=1024
    ),
    "low_bandwidth": EdgeConfig(
        agent_id="",
        site_name="",
        central_url="",
        collection_interval_seconds=30,
        aggregation_interval_seconds=300,
        aggregation_type=AggregationType.AVG,
        buffer_size_mb=200,
        sync_interval_seconds=300,
        compression_enabled=True,
        local_anomaly_detection=True,
        max_cpu_percent=30,
        max_memory_mb=256
    ),
    "real_time": EdgeConfig(
        agent_id="",
        site_name="",
        central_url="",
        collection_interval_seconds=1,
        aggregation_interval_seconds=10,
        aggregation_type=AggregationType.NONE,
        buffer_size_mb=100,
        sync_interval_seconds=10,
        compression_enabled=False,
        local_anomaly_detection=True,
        local_alerting=True,
        max_cpu_percent=80,
        max_memory_mb=512
    ),
    "minimal": EdgeConfig(
        agent_id="",
        site_name="",
        central_url="",
        collection_interval_seconds=60,
        aggregation_interval_seconds=600,
        aggregation_type=AggregationType.AVG,
        buffer_size_mb=50,
        sync_interval_seconds=600,
        compression_enabled=True,
        local_anomaly_detection=False,
        models_enabled=False,
        max_cpu_percent=20,
        max_memory_mb=128
    )
}
