"""
OOVMTEL Predictive Maintenance Module

This module provides predictive analytics for industrial equipment maintenance.
It uses statistical analysis and machine learning to predict failures before they occur.

Features:
- Anomaly detection (multivariate)
- Trend analysis and forecasting
- Remaining Useful Life (RUL) estimation
- Failure probability scoring
- Maintenance scheduling recommendations
"""

from .engine import PredictiveEngine
from .models import (
    AnomalyResult,
    AnomalyType,
    TrendAnalysis,
    TrendDirection,
    RULPrediction,
    FailurePrediction,
    MaintenanceRecommendation,
    EquipmentHealth,
    PredictiveAnalysis,
)
from .anomaly_detector import AnomalyDetector
from .forecaster import TimeSeriesForecaster
from .rul_estimator import RULEstimator

__all__ = [
    'PredictiveEngine',
    'AnomalyResult',
    'AnomalyType',
    'TrendAnalysis',
    'TrendDirection',
    'RULPrediction',
    'FailurePrediction',
    'MaintenanceRecommendation',
    'EquipmentHealth',
    'PredictiveAnalysis',
    'AnomalyDetector',
    'TimeSeriesForecaster',
    'RULEstimator',
]
