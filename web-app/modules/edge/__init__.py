"""
OOVMTEL Edge Computing Module

This module provides edge computing capabilities for industrial IoT.
It enables local data processing, buffering, and anomaly detection at the edge.

Features:
- Local data aggregation and filtering
- Edge-based anomaly detection
- Offline buffering with sync
- Model inference at the edge
- Bandwidth optimization
"""

from .agent import EdgeAgent
from .models import (
    EdgeConfig,
    EdgeMetrics,
    EdgeStatus,
    DataBuffer,
    AggregatedData,
    EdgeAlert,
    SyncStatus,
    ModelDeployment,
)
from .processor import EdgeProcessor
from .buffer_manager import BufferManager
from .sync_manager import SyncManager

__all__ = [
    'EdgeAgent',
    'EdgeConfig',
    'EdgeMetrics',
    'EdgeStatus',
    'DataBuffer',
    'AggregatedData',
    'EdgeAlert',
    'SyncStatus',
    'ModelDeployment',
    'EdgeProcessor',
    'BufferManager',
    'SyncManager',
]
