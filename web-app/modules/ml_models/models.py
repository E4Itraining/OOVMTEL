"""
ML Models Library - Data Models
Pre-trained models for industrial equipment
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class EquipmentType(str, Enum):
    """Types of industrial equipment."""
    PUMP = "pump"
    MOTOR = "motor"
    COMPRESSOR = "compressor"
    TURBINE = "turbine"
    CONVEYOR = "conveyor"
    VALVE = "valve"
    HEAT_EXCHANGER = "heat_exchanger"
    GEARBOX = "gearbox"
    BEARING = "bearing"
    FAN = "fan"
    GENERATOR = "generator"
    TRANSFORMER = "transformer"
    GENERIC = "generic"


class ModelType(str, Enum):
    """Types of ML models."""
    ANOMALY_DETECTION = "anomaly_detection"
    REMAINING_USEFUL_LIFE = "remaining_useful_life"
    FAILURE_PREDICTION = "failure_prediction"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    HEALTH_INDEX = "health_index"
    DEGRADATION = "degradation"


class ModelStatus(str, Enum):
    """Model status."""
    READY = "ready"
    TRAINING = "training"
    VALIDATING = "validating"
    FAILED = "failed"
    DEPRECATED = "deprecated"


class FailureMode(str, Enum):
    """Common failure modes."""
    BEARING_FAILURE = "bearing_failure"
    OVERHEATING = "overheating"
    VIBRATION_EXCESS = "vibration_excess"
    CAVITATION = "cavitation"
    SEAL_LEAK = "seal_leak"
    IMBALANCE = "imbalance"
    MISALIGNMENT = "misalignment"
    ELECTRICAL_FAULT = "electrical_fault"
    LUBRICATION_ISSUE = "lubrication_issue"
    CORROSION = "corrosion"
    FATIGUE = "fatigue"
    WEAR = "wear"
    BLOCKAGE = "blockage"
    UNKNOWN = "unknown"


class ModelMetrics(BaseModel):
    """Model performance metrics."""
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mse: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None
    r2_score: Optional[float] = None
    auc_roc: Optional[float] = None

    # Specific metrics
    false_positive_rate: Optional[float] = None
    false_negative_rate: Optional[float] = None
    detection_delay_hours: Optional[float] = None


class InputFeature(BaseModel):
    """Model input feature specification."""
    name: str
    description: str = ""
    unit: str = ""
    data_type: str = "float"  # float, int, categorical
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default_value: Optional[float] = None
    required: bool = True


class OutputSpec(BaseModel):
    """Model output specification."""
    name: str
    description: str = ""
    output_type: str = "float"  # float, int, categorical, probability
    classes: List[str] = Field(default_factory=list)  # For classification
    threshold: Optional[float] = None  # Decision threshold


class PretrainedModel(BaseModel):
    """Pre-trained ML model definition."""
    model_id: str = Field(default_factory=lambda: f"model_{uuid.uuid4().hex[:8]}")
    name: str
    description: str = ""

    # Type information
    equipment_type: EquipmentType
    model_type: ModelType
    failure_modes: List[FailureMode] = Field(default_factory=list)

    # Version
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Status
    status: ModelStatus = ModelStatus.READY

    # I/O specification
    input_features: List[InputFeature] = Field(default_factory=list)
    output_spec: OutputSpec = Field(default_factory=lambda: OutputSpec(name="output"))

    # Model details
    algorithm: str = ""  # e.g., "isolation_forest", "lstm", "random_forest"
    framework: str = "sklearn"  # sklearn, tensorflow, pytorch
    model_size_mb: float = 0.0

    # Performance
    metrics: ModelMetrics = Field(default_factory=ModelMetrics)
    training_samples: int = 0
    validation_samples: int = 0

    # Metadata
    tags: List[str] = Field(default_factory=list)
    author: str = ""
    license: str = "proprietary"


class ModelPrediction(BaseModel):
    """Prediction result from a model."""
    prediction_id: str = Field(default_factory=lambda: f"pred_{uuid.uuid4().hex[:8]}")
    model_id: str
    model_name: str

    # Input/Output
    input_values: Dict[str, float] = Field(default_factory=dict)
    output_value: Any = None
    confidence: float = 0.0
    probabilities: Dict[str, float] = Field(default_factory=dict)

    # Context
    equipment_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Interpretation
    prediction_label: str = ""
    explanation: str = ""
    contributing_features: List[Dict[str, Any]] = Field(default_factory=list)

    # Alerts
    is_anomaly: bool = False
    alert_level: str = "none"  # none, info, warning, critical


class ModelEnsemble(BaseModel):
    """Ensemble of multiple models."""
    ensemble_id: str = Field(default_factory=lambda: f"ens_{uuid.uuid4().hex[:8]}")
    name: str
    description: str = ""

    # Models
    model_ids: List[str] = Field(default_factory=list)
    weights: Dict[str, float] = Field(default_factory=dict)

    # Aggregation
    aggregation_method: str = "weighted_average"  # weighted_average, voting, stacking

    # Equipment
    equipment_type: EquipmentType = EquipmentType.GENERIC


class TrainingConfig(BaseModel):
    """Model training configuration."""
    model_type: ModelType
    equipment_type: EquipmentType

    # Data
    feature_columns: List[str] = Field(default_factory=list)
    target_column: str = ""
    time_column: str = "timestamp"

    # Training parameters
    train_test_split: float = 0.8
    validation_split: float = 0.1
    random_state: int = 42

    # Algorithm specific
    algorithm_params: Dict[str, Any] = Field(default_factory=dict)


class HealthScore(BaseModel):
    """Equipment health score."""
    equipment_id: str
    equipment_type: EquipmentType
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Scores
    overall_score: float  # 0-100
    component_scores: Dict[str, float] = Field(default_factory=dict)

    # Trend
    trend: str = "stable"  # improving, stable, degrading
    trend_slope: float = 0.0

    # Predictions
    days_to_maintenance: Optional[int] = None
    failure_probability_30d: float = 0.0
    predicted_failure_modes: List[Dict[str, Any]] = Field(default_factory=list)

    # Recommendations
    recommendations: List[str] = Field(default_factory=list)


# Pre-defined model templates
PRETRAINED_MODEL_CATALOG = {
    # Pump models
    "pump_anomaly_v1": PretrainedModel(
        model_id="pump_anomaly_v1",
        name="Pump Anomaly Detection",
        description="Détecte les anomalies dans les pompes centrifuges",
        equipment_type=EquipmentType.PUMP,
        model_type=ModelType.ANOMALY_DETECTION,
        failure_modes=[FailureMode.CAVITATION, FailureMode.BEARING_FAILURE, FailureMode.SEAL_LEAK],
        algorithm="isolation_forest",
        input_features=[
            InputFeature(name="vibration_x", unit="mm/s", min_value=0, max_value=50),
            InputFeature(name="vibration_y", unit="mm/s", min_value=0, max_value=50),
            InputFeature(name="temperature", unit="°C", min_value=0, max_value=150),
            InputFeature(name="pressure_inlet", unit="bar", min_value=0, max_value=20),
            InputFeature(name="pressure_outlet", unit="bar", min_value=0, max_value=50),
            InputFeature(name="flow_rate", unit="m³/h", min_value=0, max_value=1000),
            InputFeature(name="current", unit="A", min_value=0, max_value=500),
        ],
        output_spec=OutputSpec(
            name="is_anomaly",
            output_type="probability",
            threshold=0.5,
        ),
        metrics=ModelMetrics(
            accuracy=0.94,
            precision=0.91,
            recall=0.89,
            f1_score=0.90,
            auc_roc=0.95,
        ),
        training_samples=50000,
        tags=["pump", "centrifugal", "anomaly"],
    ),
    "pump_rul_v1": PretrainedModel(
        model_id="pump_rul_v1",
        name="Pump Remaining Useful Life",
        description="Prédit la durée de vie restante des pompes",
        equipment_type=EquipmentType.PUMP,
        model_type=ModelType.REMAINING_USEFUL_LIFE,
        algorithm="lstm",
        framework="tensorflow",
        input_features=[
            InputFeature(name="vibration_rms", unit="mm/s"),
            InputFeature(name="temperature", unit="°C"),
            InputFeature(name="power", unit="kW"),
            InputFeature(name="efficiency", unit="%"),
            InputFeature(name="operating_hours", unit="h"),
        ],
        output_spec=OutputSpec(
            name="rul_days",
            output_type="float",
            description="Jours restants avant maintenance",
        ),
        metrics=ModelMetrics(
            rmse=5.2,
            mae=3.8,
            r2_score=0.87,
        ),
        training_samples=30000,
        tags=["pump", "rul", "predictive"],
    ),

    # Motor models
    "motor_anomaly_v1": PretrainedModel(
        model_id="motor_anomaly_v1",
        name="Motor Anomaly Detection",
        description="Détecte les anomalies dans les moteurs électriques",
        equipment_type=EquipmentType.MOTOR,
        model_type=ModelType.ANOMALY_DETECTION,
        failure_modes=[FailureMode.BEARING_FAILURE, FailureMode.OVERHEATING, FailureMode.ELECTRICAL_FAULT],
        algorithm="autoencoder",
        framework="tensorflow",
        input_features=[
            InputFeature(name="current_phase_a", unit="A"),
            InputFeature(name="current_phase_b", unit="A"),
            InputFeature(name="current_phase_c", unit="A"),
            InputFeature(name="voltage", unit="V"),
            InputFeature(name="vibration", unit="mm/s"),
            InputFeature(name="temperature_stator", unit="°C"),
            InputFeature(name="temperature_bearing", unit="°C"),
            InputFeature(name="speed", unit="rpm"),
        ],
        output_spec=OutputSpec(
            name="reconstruction_error",
            output_type="float",
            threshold=0.1,
        ),
        metrics=ModelMetrics(
            accuracy=0.93,
            precision=0.90,
            recall=0.92,
            f1_score=0.91,
        ),
        training_samples=80000,
        tags=["motor", "electric", "anomaly"],
    ),
    "motor_health_v1": PretrainedModel(
        model_id="motor_health_v1",
        name="Motor Health Index",
        description="Calcule un indice de santé global du moteur",
        equipment_type=EquipmentType.MOTOR,
        model_type=ModelType.HEALTH_INDEX,
        algorithm="gradient_boosting",
        input_features=[
            InputFeature(name="current_imbalance", unit="%"),
            InputFeature(name="vibration_velocity", unit="mm/s"),
            InputFeature(name="temperature_rise", unit="°C"),
            InputFeature(name="power_factor", unit=""),
            InputFeature(name="insulation_resistance", unit="MΩ"),
        ],
        output_spec=OutputSpec(
            name="health_index",
            output_type="float",
            description="Score de santé 0-100",
        ),
        metrics=ModelMetrics(
            rmse=4.5,
            mae=3.2,
            r2_score=0.91,
        ),
        training_samples=45000,
        tags=["motor", "health", "index"],
    ),

    # Compressor models
    "compressor_anomaly_v1": PretrainedModel(
        model_id="compressor_anomaly_v1",
        name="Compressor Anomaly Detection",
        description="Détecte les anomalies dans les compresseurs",
        equipment_type=EquipmentType.COMPRESSOR,
        model_type=ModelType.ANOMALY_DETECTION,
        failure_modes=[FailureMode.VIBRATION_EXCESS, FailureMode.OVERHEATING, FailureMode.VALVE_FAILURE],
        algorithm="isolation_forest",
        input_features=[
            InputFeature(name="suction_pressure", unit="bar"),
            InputFeature(name="discharge_pressure", unit="bar"),
            InputFeature(name="suction_temperature", unit="°C"),
            InputFeature(name="discharge_temperature", unit="°C"),
            InputFeature(name="oil_pressure", unit="bar"),
            InputFeature(name="oil_temperature", unit="°C"),
            InputFeature(name="vibration", unit="mm/s"),
            InputFeature(name="current", unit="A"),
        ],
        output_spec=OutputSpec(
            name="anomaly_score",
            output_type="probability",
            threshold=0.6,
        ),
        metrics=ModelMetrics(
            accuracy=0.92,
            precision=0.89,
            recall=0.91,
            f1_score=0.90,
        ),
        training_samples=40000,
        tags=["compressor", "reciprocating", "anomaly"],
    ),

    # Bearing models
    "bearing_degradation_v1": PretrainedModel(
        model_id="bearing_degradation_v1",
        name="Bearing Degradation Model",
        description="Surveille la dégradation des roulements",
        equipment_type=EquipmentType.BEARING,
        model_type=ModelType.DEGRADATION,
        failure_modes=[FailureMode.BEARING_FAILURE, FailureMode.LUBRICATION_ISSUE, FailureMode.FATIGUE],
        algorithm="random_forest",
        input_features=[
            InputFeature(name="vibration_rms", unit="mm/s"),
            InputFeature(name="vibration_peak", unit="mm/s"),
            InputFeature(name="vibration_crest_factor", unit=""),
            InputFeature(name="kurtosis", unit=""),
            InputFeature(name="temperature", unit="°C"),
            InputFeature(name="speed", unit="rpm"),
        ],
        output_spec=OutputSpec(
            name="degradation_level",
            output_type="categorical",
            classes=["healthy", "slight_degradation", "moderate_degradation", "severe_degradation"],
        ),
        metrics=ModelMetrics(
            accuracy=0.91,
            precision=0.88,
            recall=0.90,
            f1_score=0.89,
        ),
        training_samples=60000,
        tags=["bearing", "degradation", "vibration"],
    ),

    # Gearbox models
    "gearbox_failure_v1": PretrainedModel(
        model_id="gearbox_failure_v1",
        name="Gearbox Failure Prediction",
        description="Prédit les défaillances des réducteurs",
        equipment_type=EquipmentType.GEARBOX,
        model_type=ModelType.FAILURE_PREDICTION,
        failure_modes=[FailureMode.WEAR, FailureMode.MISALIGNMENT, FailureMode.LUBRICATION_ISSUE],
        algorithm="xgboost",
        input_features=[
            InputFeature(name="vibration_1x", unit="mm/s"),
            InputFeature(name="vibration_2x", unit="mm/s"),
            InputFeature(name="gear_mesh_frequency", unit="Hz"),
            InputFeature(name="oil_particle_count", unit="ppm"),
            InputFeature(name="oil_temperature", unit="°C"),
            InputFeature(name="torque", unit="Nm"),
        ],
        output_spec=OutputSpec(
            name="failure_probability_7d",
            output_type="probability",
            threshold=0.7,
        ),
        metrics=ModelMetrics(
            accuracy=0.89,
            precision=0.85,
            recall=0.88,
            f1_score=0.86,
            auc_roc=0.92,
        ),
        training_samples=35000,
        tags=["gearbox", "failure", "prediction"],
    ),

    # Generic models
    "generic_anomaly_v1": PretrainedModel(
        model_id="generic_anomaly_v1",
        name="Generic Anomaly Detection",
        description="Détection d'anomalies générique multi-équipement",
        equipment_type=EquipmentType.GENERIC,
        model_type=ModelType.ANOMALY_DETECTION,
        algorithm="isolation_forest",
        input_features=[
            InputFeature(name="sensor_1", description="Capteur principal"),
            InputFeature(name="sensor_2", description="Capteur secondaire"),
            InputFeature(name="sensor_3", description="Capteur tertiaire"),
        ],
        output_spec=OutputSpec(
            name="anomaly_score",
            output_type="probability",
            threshold=0.5,
        ),
        metrics=ModelMetrics(
            accuracy=0.88,
            precision=0.85,
            recall=0.83,
            f1_score=0.84,
        ),
        training_samples=100000,
        tags=["generic", "anomaly", "multivariate"],
    ),
}


# Feature importance for interpretability
FEATURE_IMPORTANCE_TEMPLATES = {
    "pump": {
        "vibration_x": 0.25,
        "vibration_y": 0.23,
        "temperature": 0.18,
        "pressure_outlet": 0.15,
        "flow_rate": 0.12,
        "current": 0.07,
    },
    "motor": {
        "current_imbalance": 0.28,
        "vibration_velocity": 0.24,
        "temperature_rise": 0.20,
        "power_factor": 0.15,
        "insulation_resistance": 0.13,
    },
    "compressor": {
        "discharge_temperature": 0.22,
        "vibration": 0.21,
        "discharge_pressure": 0.19,
        "oil_temperature": 0.16,
        "current": 0.12,
        "suction_pressure": 0.10,
    },
}


# Failure mode signatures
FAILURE_SIGNATURES = {
    FailureMode.BEARING_FAILURE: {
        "indicators": ["vibration_increase", "temperature_rise", "noise_increase"],
        "vibration_frequencies": ["BPFO", "BPFI", "BSF", "FTF"],
        "progression_days": 30,
    },
    FailureMode.CAVITATION: {
        "indicators": ["pressure_fluctuation", "flow_instability", "noise_increase"],
        "typical_frequency_range": "1-10 kHz",
        "progression_days": 14,
    },
    FailureMode.MISALIGNMENT: {
        "indicators": ["2x_vibration", "axial_vibration", "temperature_coupling"],
        "vibration_pattern": "2x running speed dominant",
        "progression_days": 60,
    },
    FailureMode.IMBALANCE: {
        "indicators": ["1x_vibration", "phase_shift"],
        "vibration_pattern": "1x running speed dominant",
        "progression_days": 90,
    },
    FailureMode.OVERHEATING: {
        "indicators": ["temperature_rise", "efficiency_drop", "current_increase"],
        "critical_temp_delta": 20,  # °C above normal
        "progression_days": 7,
    },
}
