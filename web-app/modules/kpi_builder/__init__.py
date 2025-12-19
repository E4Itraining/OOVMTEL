"""
KPI Builder Module
Custom KPI definition and benchmarking for SYNAPSIX
"""

from .engine import KPIBuilderEngine
from .calculator import KPICalculator
from .benchmarking import BenchmarkManager
from .models import (
    KPIDefinition,
    KPIResult,
    KPIFormula,
    KPIThreshold,
    Benchmark,
    BenchmarkComparison,
    AggregationType,
    KPICategory,
)

__all__ = [
    'KPIBuilderEngine',
    'KPICalculator',
    'BenchmarkManager',
    'KPIDefinition',
    'KPIResult',
    'KPIFormula',
    'KPIThreshold',
    'Benchmark',
    'BenchmarkComparison',
    'AggregationType',
    'KPICategory',
]
