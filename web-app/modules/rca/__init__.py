"""
OOVMTEL Auto-RCA (Root Cause Analysis) Module

This module provides automatic root cause analysis for industrial incidents.
It uses causal graph analysis to identify the most likely root causes.

Features:
- Automatic incident detection
- Causal graph construction
- Root cause probability scoring
- Historical pattern matching
- Remediation suggestions
"""

from .engine import RCAEngine
from .models import (
    Incident,
    IncidentSeverity,
    IncidentCategory,
    CausalNode,
    CausalEdge,
    CausalGraph,
    RootCauseResult,
    RCAAnalysis,
    CorrelationResult,
    RemediationSuggestion,
)
from .correlator import TemporalCorrelator
from .graph_builder import CausalGraphBuilder

__all__ = [
    'RCAEngine',
    'Incident',
    'IncidentSeverity',
    'IncidentCategory',
    'CausalNode',
    'CausalEdge',
    'CausalGraph',
    'RootCauseResult',
    'RCAAnalysis',
    'CorrelationResult',
    'RemediationSuggestion',
    'TemporalCorrelator',
    'CausalGraphBuilder',
]
