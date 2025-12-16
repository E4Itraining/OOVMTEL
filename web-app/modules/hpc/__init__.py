"""
HPC Module - High Performance Computing Integration for Industrial Observability

This module provides HPC capabilities including:
- GPU Acceleration for ML/AI workloads
- Distributed Computing cluster management
- Parallel Processing pipelines
- "What-if" Simulation engine
- Real-time batch processing optimization
"""

from .models import (
    HPCCluster,
    HPCNode,
    HPCJob,
    GPUDevice,
    ComputeTask,
    SimulationScenario,
    SimulationResult,
    HPCMetrics,
    ClusterStatus,
    NodeStatus,
    JobStatus,
    JobPriority,
    ComputeBackend,
    HPC_PRESETS,
)
from .engine import HPCEngine
from .cluster_manager import ClusterManager
from .simulation_engine import SimulationEngine
from .parallel_processor import ParallelProcessor

__all__ = [
    # Models
    "HPCCluster",
    "HPCNode",
    "HPCJob",
    "GPUDevice",
    "ComputeTask",
    "SimulationScenario",
    "SimulationResult",
    "HPCMetrics",
    "ClusterStatus",
    "NodeStatus",
    "JobStatus",
    "JobPriority",
    "ComputeBackend",
    "HPC_PRESETS",
    # Engines
    "HPCEngine",
    "ClusterManager",
    "SimulationEngine",
    "ParallelProcessor",
]
