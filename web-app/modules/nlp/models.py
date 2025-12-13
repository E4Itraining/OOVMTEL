"""
NLP Module Data Models
Pydantic models for conversational analytics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class QueryIntent(str, Enum):
    """Types of user intents detected from natural language queries."""
    METRICS_QUERY = "metrics_query"          # Get specific metrics
    COMPARISON = "comparison"                  # Compare equipment/periods
    TROUBLESHOOTING = "troubleshooting"       # Diagnose issues
    TREND_ANALYSIS = "trend_analysis"         # Analyze trends over time
    ALERT_STATUS = "alert_status"             # Check alerts/alarms
    ROOT_CAUSE = "root_cause"                 # Find root cause of incident
    PREDICTION = "prediction"                  # Predict future values
    SUMMARY = "summary"                        # Get summary/overview
    EQUIPMENT_STATUS = "equipment_status"     # Check equipment status
    PRODUCTION_STATUS = "production_status"   # Check production metrics
    UNKNOWN = "unknown"                        # Could not determine intent


class TimeRange(BaseModel):
    """Time range for queries."""
    start: datetime
    end: datetime
    duration_description: str = ""  # e.g., "yesterday afternoon", "last 24h"

    @classmethod
    def last_hours(cls, hours: int) -> "TimeRange":
        end = datetime.utcnow()
        start = end - timedelta(hours=hours)
        return cls(start=start, end=end, duration_description=f"last {hours}h")

    @classmethod
    def last_days(cls, days: int) -> "TimeRange":
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        return cls(start=start, end=end, duration_description=f"last {days} days")


class ExtractedEntities(BaseModel):
    """Entities extracted from natural language query."""
    equipment: List[str] = Field(default_factory=list)
    equipment_types: List[str] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=list)
    kpis: List[str] = Field(default_factory=list)
    time_range: Optional[TimeRange] = None
    production_lines: List[str] = Field(default_factory=list)
    products: List[str] = Field(default_factory=list)
    severity_levels: List[str] = Field(default_factory=list)
    comparison_targets: List[str] = Field(default_factory=list)
    thresholds: Dict[str, float] = Field(default_factory=dict)


class ConversationalQuery(BaseModel):
    """Input model for conversational queries."""
    query: str
    language: str = "auto"  # auto, fr, en
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class VisualizationType(str, Enum):
    """Types of visualizations that can be suggested."""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    GAUGE = "gauge"
    TABLE = "table"
    HEATMAP = "heatmap"
    PIE_CHART = "pie_chart"
    TIMELINE = "timeline"
    TREEMAP = "treemap"
    STAT_CARD = "stat_card"


class SuggestedVisualization(BaseModel):
    """Suggested visualization for query results."""
    type: VisualizationType
    title: str
    config: Dict[str, Any] = Field(default_factory=dict)
    data: List[Dict[str, Any]] = Field(default_factory=list)
    description: str = ""


class DataPoint(BaseModel):
    """Single data point in query results."""
    timestamp: Optional[datetime] = None
    value: Union[float, int, str]
    metric: str
    labels: Dict[str, str] = Field(default_factory=dict)


class QueryResult(BaseModel):
    """Result from executing a query."""
    success: bool
    data: List[DataPoint] = Field(default_factory=list)
    aggregations: Dict[str, Any] = Field(default_factory=dict)
    raw_query: str = ""
    query_type: str = ""  # promql, opensearch, etc.
    execution_time_ms: float = 0
    error: Optional[str] = None


class ConversationContext(BaseModel):
    """Context maintained across conversation turns."""
    session_id: str
    history: List[Dict[str, str]] = Field(default_factory=list)
    last_entities: Optional[ExtractedEntities] = None
    last_intent: Optional[QueryIntent] = None
    last_results: Optional[QueryResult] = None
    equipment_context: List[str] = Field(default_factory=list)
    time_context: Optional[TimeRange] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NLPResponse(BaseModel):
    """Full response from NLP engine."""
    answer: str
    answer_html: str = ""
    intent: QueryIntent
    entities: ExtractedEntities
    query_results: List[QueryResult] = Field(default_factory=list)
    visualizations: List[SuggestedVisualization] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)  # Follow-up questions
    confidence: float = 0.0
    processing_time_ms: float = 0
    language: str = "fr"


# Keyword mappings for entity extraction
EQUIPMENT_KEYWORDS = {
    "fr": {
        "ligne": "line",
        "lignes": "line",
        "machine": "machine",
        "machines": "machine",
        "réacteur": "reactor",
        "réacteurs": "reactor",
        "pompe": "pump",
        "pompes": "pump",
        "mélangeur": "mixer",
        "mixeur": "mixer",
        "four": "furnace",
        "fours": "furnace",
        "convoyeur": "conveyor",
        "convoyeurs": "conveyor",
        "cuve": "tank",
        "cuves": "tank",
        "capteur": "sensor",
        "capteurs": "sensor",
    },
    "en": {
        "line": "line",
        "lines": "line",
        "machine": "machine",
        "machines": "machine",
        "reactor": "reactor",
        "reactors": "reactor",
        "pump": "pump",
        "pumps": "pump",
        "mixer": "mixer",
        "mixers": "mixer",
        "furnace": "furnace",
        "furnaces": "furnace",
        "conveyor": "conveyor",
        "conveyors": "conveyor",
        "tank": "tank",
        "tanks": "tank",
        "sensor": "sensor",
        "sensors": "sensor",
    }
}

METRIC_KEYWORDS = {
    "fr": {
        "oee": "oee",
        "trs": "oee",  # Taux de Rendement Synthétique
        "qualité": "quality_rate",
        "disponibilité": "availability",
        "performance": "performance",
        "production": "production_count",
        "défauts": "defects",
        "rebuts": "defects",
        "température": "temperature",
        "pression": "pressure",
        "vibration": "vibration",
        "consommation": "power_consumption",
        "débit": "flow_rate",
        "temps de cycle": "cycle_time",
        "cadence": "cycle_time",
        "arrêts": "downtime",
        "pannes": "failures",
    },
    "en": {
        "oee": "oee",
        "quality": "quality_rate",
        "availability": "availability",
        "performance": "performance",
        "production": "production_count",
        "defects": "defects",
        "scrap": "defects",
        "temperature": "temperature",
        "pressure": "pressure",
        "vibration": "vibration",
        "consumption": "power_consumption",
        "power": "power_consumption",
        "flow": "flow_rate",
        "cycle time": "cycle_time",
        "downtime": "downtime",
        "failures": "failures",
    }
}

TIME_KEYWORDS = {
    "fr": {
        "aujourd'hui": ("today", 0),
        "hier": ("yesterday", 1),
        "cette semaine": ("this_week", 7),
        "ce mois": ("this_month", 30),
        "dernière heure": ("last_hour", 1/24),
        "dernières 24h": ("last_24h", 1),
        "dernières 24 heures": ("last_24h", 1),
        "cette nuit": ("tonight", 0.5),
        "ce matin": ("this_morning", 0.5),
        "cet après-midi": ("this_afternoon", 0.5),
    },
    "en": {
        "today": ("today", 0),
        "yesterday": ("yesterday", 1),
        "this week": ("this_week", 7),
        "this month": ("this_month", 30),
        "last hour": ("last_hour", 1/24),
        "last 24h": ("last_24h", 1),
        "last 24 hours": ("last_24h", 1),
        "tonight": ("tonight", 0.5),
        "this morning": ("this_morning", 0.5),
        "this afternoon": ("this_afternoon", 0.5),
    }
}

INTENT_PATTERNS = {
    "fr": {
        QueryIntent.TROUBLESHOOTING: [
            "pourquoi", "problème", "problèmes", "cause", "défaillance",
            "erreur", "bug", "incident", "panne", "dysfonctionnement"
        ],
        QueryIntent.COMPARISON: [
            "compare", "comparer", "comparaison", "différence", "versus",
            "vs", "par rapport", "meilleur", "pire"
        ],
        QueryIntent.TREND_ANALYSIS: [
            "tendance", "évolution", "progression", "historique",
            "au fil du temps", "sur la période"
        ],
        QueryIntent.ALERT_STATUS: [
            "alerte", "alertes", "alarme", "alarmes", "notification",
            "critique", "warning", "urgence"
        ],
        QueryIntent.ROOT_CAUSE: [
            "cause racine", "origine", "source du problème",
            "à l'origine", "responsable"
        ],
        QueryIntent.PREDICTION: [
            "prédire", "prédiction", "prévoir", "anticipé",
            "va se passer", "risque de"
        ],
        QueryIntent.SUMMARY: [
            "résumé", "synthèse", "overview", "bilan", "état général",
            "comment ça va", "situation"
        ],
        QueryIntent.EQUIPMENT_STATUS: [
            "état", "statut", "fonctionne", "marche", "arrêté",
            "en panne", "opérationnel"
        ],
        QueryIntent.PRODUCTION_STATUS: [
            "production", "produit", "fabriqué", "unités",
            "rendement", "objectif"
        ],
    },
    "en": {
        QueryIntent.TROUBLESHOOTING: [
            "why", "problem", "problems", "cause", "failure",
            "error", "bug", "incident", "breakdown", "malfunction"
        ],
        QueryIntent.COMPARISON: [
            "compare", "comparison", "difference", "versus",
            "vs", "against", "better", "worse"
        ],
        QueryIntent.TREND_ANALYSIS: [
            "trend", "evolution", "progression", "history",
            "over time", "during period"
        ],
        QueryIntent.ALERT_STATUS: [
            "alert", "alerts", "alarm", "alarms", "notification",
            "critical", "warning", "urgent"
        ],
        QueryIntent.ROOT_CAUSE: [
            "root cause", "origin", "source of problem",
            "responsible", "underlying"
        ],
        QueryIntent.PREDICTION: [
            "predict", "prediction", "forecast", "anticipated",
            "will happen", "risk of"
        ],
        QueryIntent.SUMMARY: [
            "summary", "overview", "status", "general state",
            "how is", "situation"
        ],
        QueryIntent.EQUIPMENT_STATUS: [
            "status", "state", "running", "working", "stopped",
            "down", "operational"
        ],
        QueryIntent.PRODUCTION_STATUS: [
            "production", "produced", "manufactured", "units",
            "yield", "target"
        ],
    }
}
