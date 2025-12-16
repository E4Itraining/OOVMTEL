"""
HPC Models - Data models for High Performance Computing module
"""

from enum import Enum
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ClusterStatus(str, Enum):
    """HPC cluster status."""
    INITIALIZING = "initializing"
    ONLINE = "online"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class NodeStatus(str, Enum):
    """HPC node status."""
    AVAILABLE = "available"
    BUSY = "busy"
    RESERVED = "reserved"
    DRAINING = "draining"
    OFFLINE = "offline"
    ERROR = "error"


class JobStatus(str, Enum):
    """HPC job status."""
    QUEUED = "queued"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class JobPriority(str, Enum):
    """Job priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


class ComputeBackend(str, Enum):
    """Available compute backends."""
    CPU = "cpu"
    CUDA = "cuda"
    OPENCL = "opencl"
    VULKAN_COMPUTE = "vulkan_compute"
    METAL = "metal"
    HYBRID = "hybrid"


class GPUDevice(BaseModel):
    """GPU device information."""
    id: str
    name: str
    vendor: str  # NVIDIA, AMD, Intel
    memory_total_gb: float
    memory_used_gb: float = 0
    memory_available_gb: float = 0
    compute_capability: str = ""  # CUDA compute capability
    driver_version: str = ""
    temperature_celsius: float = 0
    utilization_percent: float = 0
    power_watts: float = 0
    power_limit_watts: float = 0
    clock_speed_mhz: int = 0
    status: NodeStatus = NodeStatus.AVAILABLE


class HPCNode(BaseModel):
    """HPC compute node."""
    id: str
    hostname: str
    ip_address: str
    status: NodeStatus = NodeStatus.AVAILABLE

    # CPU resources
    cpu_cores: int = 8
    cpu_threads: int = 16
    cpu_model: str = ""
    cpu_usage_percent: float = 0

    # Memory resources
    memory_total_gb: float = 32
    memory_used_gb: float = 0
    memory_available_gb: float = 32

    # GPU resources
    gpus: List[GPUDevice] = Field(default_factory=list)
    total_gpu_memory_gb: float = 0

    # Storage
    storage_total_gb: float = 500
    storage_used_gb: float = 0

    # Network
    network_bandwidth_gbps: float = 10
    infiniband_enabled: bool = False

    # Performance metrics
    jobs_completed: int = 0
    jobs_failed: int = 0
    avg_job_duration_seconds: float = 0
    uptime_hours: float = 0

    # Metadata
    tags: List[str] = Field(default_factory=list)
    location: str = ""
    rack: str = ""
    last_heartbeat: Optional[datetime] = None


class HPCCluster(BaseModel):
    """HPC cluster configuration and status."""
    id: str
    name: str
    description: str = ""
    status: ClusterStatus = ClusterStatus.INITIALIZING

    # Nodes
    nodes: List[HPCNode] = Field(default_factory=list)
    total_nodes: int = 0
    available_nodes: int = 0

    # Aggregate resources
    total_cpu_cores: int = 0
    total_memory_gb: float = 0
    total_gpu_count: int = 0
    total_gpu_memory_gb: float = 0

    # Utilization
    cpu_utilization_percent: float = 0
    memory_utilization_percent: float = 0
    gpu_utilization_percent: float = 0

    # Job queue
    jobs_queued: int = 0
    jobs_running: int = 0
    jobs_completed_24h: int = 0

    # Performance
    avg_queue_time_seconds: float = 0
    avg_execution_time_seconds: float = 0
    throughput_jobs_per_hour: float = 0

    # Configuration
    scheduler_type: str = "slurm"  # slurm, pbs, kubernetes
    default_backend: ComputeBackend = ComputeBackend.HYBRID
    max_job_duration_hours: int = 24

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class ComputeTask(BaseModel):
    """Individual compute task within a job."""
    id: str
    name: str
    type: str  # ml_training, simulation, batch_processing, etc.

    # Resource requirements
    cpu_cores: int = 1
    memory_gb: float = 4
    gpu_count: int = 0
    gpu_memory_gb: float = 0

    # Execution
    command: str = ""
    arguments: List[str] = Field(default_factory=list)
    environment: Dict[str, str] = Field(default_factory=dict)
    working_directory: str = ""

    # Input/Output
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_path: str = ""

    # Status
    status: JobStatus = JobStatus.QUEUED
    progress_percent: float = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results
    result: Optional[Dict[str, Any]] = None
    error_message: str = ""
    exit_code: int = 0


class HPCJob(BaseModel):
    """HPC job containing one or more compute tasks."""
    id: str
    name: str
    description: str = ""
    user_id: str = "system"

    # Job configuration
    priority: JobPriority = JobPriority.NORMAL
    backend: ComputeBackend = ComputeBackend.HYBRID

    # Tasks
    tasks: List[ComputeTask] = Field(default_factory=list)
    parallel_tasks: int = 1  # Number of tasks to run in parallel

    # Resource requirements (aggregate)
    total_cpu_cores: int = 0
    total_memory_gb: float = 0
    total_gpu_count: int = 0

    # Scheduling
    scheduled_start: Optional[datetime] = None
    max_runtime_hours: float = 24
    retry_count: int = 0
    max_retries: int = 3

    # Status
    status: JobStatus = JobStatus.QUEUED
    progress_percent: float = 0
    tasks_completed: int = 0
    tasks_failed: int = 0

    # Execution
    assigned_nodes: List[str] = Field(default_factory=list)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results
    output: Dict[str, Any] = Field(default_factory=dict)
    error_message: str = ""

    # Metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimulationScenario(BaseModel):
    """What-if simulation scenario."""
    id: str
    name: str
    description: str = ""

    # Scenario type
    type: str  # equipment_failure, production_change, maintenance_delay, etc.

    # Parameters
    base_metrics: Dict[str, Any] = Field(default_factory=dict)
    modifications: Dict[str, Any] = Field(default_factory=dict)

    # Time range
    simulation_horizon_hours: int = 24
    time_step_minutes: int = 15

    # Configuration
    monte_carlo_iterations: int = 1000
    confidence_level: float = 0.95
    random_seed: Optional[int] = None

    # Constraints
    constraints: Dict[str, Any] = Field(default_factory=dict)

    # Status
    status: JobStatus = JobStatus.QUEUED
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SimulationResult(BaseModel):
    """Results from a what-if simulation."""
    scenario_id: str
    scenario_name: str

    # Execution info
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    iterations_completed: int

    # Primary results
    predicted_outcomes: Dict[str, Any] = Field(default_factory=dict)
    probability_distribution: Dict[str, List[float]] = Field(default_factory=dict)

    # KPI impacts
    oee_impact: float = 0  # Change in OEE %
    production_impact: int = 0  # Change in units
    quality_impact: float = 0  # Change in quality %
    cost_impact: float = 0  # Cost in currency

    # Risk analysis
    risk_score: float = 0  # 0-100
    risk_factors: List[str] = Field(default_factory=list)
    mitigation_suggestions: List[str] = Field(default_factory=list)

    # Confidence
    confidence_interval_lower: Dict[str, float] = Field(default_factory=dict)
    confidence_interval_upper: Dict[str, float] = Field(default_factory=dict)
    confidence_level: float = 0.95

    # Statistical summary
    statistics: Dict[str, Dict[str, float]] = Field(default_factory=dict)

    # Visualizations
    charts: List[Dict[str, Any]] = Field(default_factory=list)


class HPCMetrics(BaseModel):
    """Aggregate HPC metrics."""
    # Cluster overview
    total_clusters: int = 0
    total_nodes: int = 0
    total_gpus: int = 0

    # Resource utilization
    cpu_utilization_avg: float = 0
    memory_utilization_avg: float = 0
    gpu_utilization_avg: float = 0

    # Job statistics
    jobs_queued: int = 0
    jobs_running: int = 0
    jobs_completed_24h: int = 0
    jobs_failed_24h: int = 0

    # Performance
    avg_queue_wait_seconds: float = 0
    avg_job_duration_seconds: float = 0
    throughput_jobs_per_hour: float = 0

    # Simulations
    simulations_running: int = 0
    simulations_completed_24h: int = 0

    # Cost efficiency
    compute_hours_24h: float = 0
    gpu_hours_24h: float = 0
    efficiency_score: float = 0  # 0-100

    # Health
    nodes_healthy: int = 0
    nodes_warning: int = 0
    nodes_error: int = 0

    # Timestamp
    collected_at: datetime = Field(default_factory=datetime.utcnow)


# =========================================
# Presets for different HPC configurations
# =========================================

HPC_PRESETS = {
    "small": {
        "nodes": 2,
        "cpu_cores_per_node": 8,
        "memory_gb_per_node": 32,
        "gpus_per_node": 1,
        "gpu_memory_gb": 8,
        "description": "Small cluster for development and testing"
    },
    "medium": {
        "nodes": 8,
        "cpu_cores_per_node": 32,
        "memory_gb_per_node": 128,
        "gpus_per_node": 2,
        "gpu_memory_gb": 16,
        "description": "Medium cluster for production workloads"
    },
    "large": {
        "nodes": 32,
        "cpu_cores_per_node": 64,
        "memory_gb_per_node": 256,
        "gpus_per_node": 4,
        "gpu_memory_gb": 32,
        "description": "Large cluster for heavy ML training"
    },
    "gpu_intensive": {
        "nodes": 16,
        "cpu_cores_per_node": 32,
        "memory_gb_per_node": 128,
        "gpus_per_node": 8,
        "gpu_memory_gb": 80,
        "description": "GPU-optimized cluster for deep learning"
    },
    "simulation": {
        "nodes": 24,
        "cpu_cores_per_node": 128,
        "memory_gb_per_node": 512,
        "gpus_per_node": 2,
        "gpu_memory_gb": 24,
        "description": "High-memory cluster for simulations"
    }
}


# =========================================
# Simulation scenario templates
# =========================================

SIMULATION_TEMPLATES = {
    "equipment_failure": {
        "type": "equipment_failure",
        "description": "Simulate impact of equipment failure",
        "default_horizon_hours": 48,
        "parameters": ["equipment_name", "failure_type", "downtime_hours"]
    },
    "production_increase": {
        "type": "production_change",
        "description": "Simulate production volume increase",
        "default_horizon_hours": 168,
        "parameters": ["increase_percent", "ramp_up_hours"]
    },
    "maintenance_delay": {
        "type": "maintenance_delay",
        "description": "Simulate delayed maintenance impact",
        "default_horizon_hours": 720,
        "parameters": ["equipment_name", "delay_days", "current_health_score"]
    },
    "supply_chain_disruption": {
        "type": "supply_chain",
        "description": "Simulate supply chain disruption",
        "default_horizon_hours": 336,
        "parameters": ["disruption_severity", "affected_materials"]
    },
    "energy_cost_increase": {
        "type": "cost_change",
        "description": "Simulate energy cost increase impact",
        "default_horizon_hours": 720,
        "parameters": ["cost_increase_percent", "affected_equipment"]
    }
}
