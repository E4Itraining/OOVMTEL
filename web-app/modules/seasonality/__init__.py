"""
Seasonality Detection Module
Advanced time-series decomposition and pattern analysis for SYNAPSIX
"""

from .engine import SeasonalityEngine
from .stl_decomposer import STLDecomposer
from .pattern_detector import PatternDetector
from .models import (
    SeasonalityType,
    DecompositionResult,
    SeasonalPattern,
    TrendComponent,
    ResidualAnalysis,
    SeasonalityAnalysis,
)

__all__ = [
    'SeasonalityEngine',
    'STLDecomposer',
    'PatternDetector',
    'SeasonalityType',
    'DecompositionResult',
    'SeasonalPattern',
    'TrendComponent',
    'ResidualAnalysis',
    'SeasonalityAnalysis',
]
