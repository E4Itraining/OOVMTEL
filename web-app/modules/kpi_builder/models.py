"""
KPI Builder - Data Models
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class AggregationType(str, Enum):
    """Aggregation types for KPI calculation."""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    FIRST = "first"
    LAST = "last"
    MEDIAN = "median"
    STDDEV = "stddev"
    PERCENTILE = "percentile"


class KPICategory(str, Enum):
    """KPI categories."""
    EFFICIENCY = "efficiency"
    QUALITY = "quality"
    AVAILABILITY = "availability"
    PERFORMANCE = "performance"
    SAFETY = "safety"
    ENVIRONMENTAL = "environmental"
    FINANCIAL = "financial"
    MAINTENANCE = "maintenance"
    CUSTOM = "custom"


class DataSourceType(str, Enum):
    """Data source types."""
    METRIC = "metric"
    FORMULA = "formula"
    CONSTANT = "constant"
    EXTERNAL = "external"


class FormulaOperator(str, Enum):
    """Formula operators."""
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    POWER = "^"
    PERCENT = "%"
    MIN = "min"
    MAX = "max"
    AVG = "avg"
    IF = "if"
    AND = "and"
    OR = "or"
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    EQ = "=="
    NEQ = "!="


class KPIDataSource(BaseModel):
    """Data source for KPI calculation."""
    source_id: str
    source_type: DataSourceType = DataSourceType.METRIC
    metric_name: Optional[str] = None
    equipment_filter: Optional[str] = None
    aggregation: AggregationType = AggregationType.AVG
    time_range_minutes: int = 60
    constant_value: Optional[float] = None
    external_source: Optional[str] = None


class KPIFormula(BaseModel):
    """Formula for KPI calculation."""
    expression: str
    # e.g., "(good_units / total_units) * 100"
    # e.g., "availability * performance * quality"

    variables: Dict[str, KPIDataSource] = Field(default_factory=dict)
    # Maps variable names to data sources

    # For complex formulas
    sub_formulas: Dict[str, 'KPIFormula'] = Field(default_factory=dict)

    # Validation
    min_result: Optional[float] = None
    max_result: Optional[float] = None


class KPIThreshold(BaseModel):
    """Threshold configuration for KPI."""
    name: str
    value: float
    color: str = "#808080"
    comparison: str = "gte"  # gt, gte, lt, lte, eq
    action: Optional[str] = None  # Optional action on threshold breach


class KPIVisualization(BaseModel):
    """Visualization settings for KPI."""
    chart_type: str = "gauge"  # gauge, line, bar, number, sparkline
    color_scheme: str = "default"
    show_trend: bool = True
    show_target: bool = True
    decimal_places: int = 2
    prefix: str = ""
    suffix: str = ""
    icon: Optional[str] = None


class KPIDefinition(BaseModel):
    """Custom KPI definition."""
    kpi_id: str
    name: str
    description: str = ""
    category: KPICategory = KPICategory.CUSTOM

    # Calculation
    formula: KPIFormula
    unit: str = ""

    # Thresholds
    thresholds: List[KPIThreshold] = Field(default_factory=list)
    target_value: Optional[float] = None
    baseline_value: Optional[float] = None

    # Time settings
    calculation_interval_seconds: int = 60
    historical_retention_days: int = 90

    # Grouping
    group_by: List[str] = Field(default_factory=list)  # e.g., ["equipment", "shift"]

    # Visualization
    visualization: KPIVisualization = Field(default_factory=KPIVisualization)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    enabled: bool = True


class KPIResult(BaseModel):
    """Result of KPI calculation."""
    kpi_id: str
    kpi_name: str
    value: float
    unit: str = ""

    # Context
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

    # Grouping
    group_values: Dict[str, str] = Field(default_factory=dict)

    # Status
    threshold_status: str = "normal"  # normal, warning, critical, excellent
    threshold_color: str = "#808080"
    target_deviation: Optional[float] = None  # % deviation from target
    trend: str = "stable"  # up, down, stable

    # Calculation details
    input_values: Dict[str, float] = Field(default_factory=dict)
    formula_used: str = ""
    calculation_time_ms: float = 0.0

    # Historical comparison
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None


class Benchmark(BaseModel):
    """Industry benchmark for KPI comparison."""
    benchmark_id: str
    name: str
    description: str = ""

    # Applicability
    kpi_category: KPICategory
    industry: str = "manufacturing"
    sub_industry: Optional[str] = None

    # Values
    percentile_25: float
    percentile_50: float  # Median
    percentile_75: float
    percentile_90: float
    world_class: float

    # Metadata
    source: str = ""
    year: int = 2024
    region: str = "global"


class BenchmarkComparison(BaseModel):
    """Comparison of KPI against benchmarks."""
    kpi_id: str
    kpi_name: str
    current_value: float
    benchmark_id: str
    benchmark_name: str

    # Comparison
    percentile_rank: float  # Where current value falls (0-100)
    gap_to_median: float
    gap_to_world_class: float

    # Rating
    rating: str  # "below_average", "average", "above_average", "top_quartile", "world_class"
    rating_description: str = ""

    # Improvement potential
    improvement_potential_percent: float
    recommendations: List[str] = Field(default_factory=list)


# Standard industrial KPI templates
STANDARD_KPI_TEMPLATES = {
    "oee": KPIDefinition(
        kpi_id="oee",
        name="Overall Equipment Effectiveness (OEE)",
        description="Mesure globale de l'efficacité des équipements",
        category=KPICategory.EFFICIENCY,
        formula=KPIFormula(
            expression="availability * performance * quality / 10000",
            variables={
                "availability": KPIDataSource(source_id="avail", metric_name="availability"),
                "performance": KPIDataSource(source_id="perf", metric_name="performance"),
                "quality": KPIDataSource(source_id="qual", metric_name="quality_rate"),
            }
        ),
        unit="%",
        thresholds=[
            KPIThreshold(name="Critique", value=40, color="#dc3545", comparison="lt"),
            KPIThreshold(name="Faible", value=60, color="#ffc107", comparison="lt"),
            KPIThreshold(name="Bon", value=85, color="#28a745", comparison="gte"),
        ],
        target_value=85.0,
    ),
    "availability": KPIDefinition(
        kpi_id="availability",
        name="Disponibilité",
        description="Temps de fonctionnement effectif / Temps planifié",
        category=KPICategory.AVAILABILITY,
        formula=KPIFormula(
            expression="(planned_time - downtime) / planned_time * 100",
            variables={
                "planned_time": KPIDataSource(source_id="pt", metric_name="planned_production_time"),
                "downtime": KPIDataSource(source_id="dt", metric_name="unplanned_downtime"),
            }
        ),
        unit="%",
        target_value=95.0,
    ),
    "mtbf": KPIDefinition(
        kpi_id="mtbf",
        name="Mean Time Between Failures (MTBF)",
        description="Temps moyen entre pannes",
        category=KPICategory.MAINTENANCE,
        formula=KPIFormula(
            expression="operating_time / failure_count",
            variables={
                "operating_time": KPIDataSource(source_id="ot", metric_name="operating_hours"),
                "failure_count": KPIDataSource(source_id="fc", metric_name="failure_count"),
            }
        ),
        unit="heures",
    ),
    "mttr": KPIDefinition(
        kpi_id="mttr",
        name="Mean Time To Repair (MTTR)",
        description="Temps moyen de réparation",
        category=KPICategory.MAINTENANCE,
        formula=KPIFormula(
            expression="total_repair_time / repair_count",
            variables={
                "total_repair_time": KPIDataSource(source_id="trt", metric_name="total_repair_time"),
                "repair_count": KPIDataSource(source_id="rc", metric_name="repair_count"),
            }
        ),
        unit="heures",
    ),
    "scrap_rate": KPIDefinition(
        kpi_id="scrap_rate",
        name="Taux de rebut",
        description="Pourcentage de produits défectueux",
        category=KPICategory.QUALITY,
        formula=KPIFormula(
            expression="defect_count / total_produced * 100",
            variables={
                "defect_count": KPIDataSource(source_id="dc", metric_name="defect_count"),
                "total_produced": KPIDataSource(source_id="tp", metric_name="total_produced"),
            }
        ),
        unit="%",
        target_value=2.0,
    ),
    "energy_efficiency": KPIDefinition(
        kpi_id="energy_efficiency",
        name="Efficacité énergétique",
        description="Production par unité d'énergie consommée",
        category=KPICategory.ENVIRONMENTAL,
        formula=KPIFormula(
            expression="production_units / energy_consumed",
            variables={
                "production_units": KPIDataSource(source_id="pu", metric_name="production_count"),
                "energy_consumed": KPIDataSource(source_id="ec", metric_name="energy_kwh"),
            }
        ),
        unit="unités/kWh",
    ),
}


# Industry benchmarks
INDUSTRY_BENCHMARKS = {
    "oee_manufacturing": Benchmark(
        benchmark_id="oee_mfg",
        name="OEE Manufacturing Benchmark",
        kpi_category=KPICategory.EFFICIENCY,
        industry="manufacturing",
        percentile_25=45.0,
        percentile_50=60.0,
        percentile_75=75.0,
        percentile_90=85.0,
        world_class=90.0,
        source="Industry Standard",
    ),
    "availability_manufacturing": Benchmark(
        benchmark_id="avail_mfg",
        name="Availability Manufacturing Benchmark",
        kpi_category=KPICategory.AVAILABILITY,
        industry="manufacturing",
        percentile_25=80.0,
        percentile_50=88.0,
        percentile_75=94.0,
        percentile_90=97.0,
        world_class=99.0,
        source="Industry Standard",
    ),
}
