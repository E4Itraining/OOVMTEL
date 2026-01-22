"""
OOVMTEL Unified Business-Tech View
Backend API Service

This service provides a unified API for aggregating business and technical metrics
from various data sources (VictoriaMetrics, OpenSearch, Kafka) and serves the
web application for the unified dashboard.

Game-Changer Modules:
- NLP/Conversational Analytics: Natural language queries for industrial data
- Auto-RCA: Automatic root cause analysis with causal graphs
- Predictive Maintenance: Anomaly detection and RUL prediction
- Auto-Remediation: Runbook-based automatic incident remediation
- Edge Computing: Edge agent management and data aggregation
"""

import os
import asyncio
import logging
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import random

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel

# Import game-changer modules
try:
    from modules.nlp import NLPEngine, ConversationalQuery
    from modules.rca import RCAEngine, Incident, IncidentSeverity, IncidentCategory
    from modules.predictive import PredictiveEngine
    from modules.remediation import RemediationEngine, RunbookLibrary
    from modules.edge import EdgeAgent, EdgeConfig, EdgeAgentManager
    from modules.hpc import (
        HPCEngine, ClusterManager, SimulationEngine, ParallelProcessor,
        HPCCluster, HPCJob, SimulationScenario, SimulationResult,
        JobStatus, JobPriority, ComputeBackend, HPC_PRESETS
    )
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    logging.warning(f"Advanced modules not available: {e}")

# Import LLM module
try:
    from modules.llm import (
        LLMSettings, get_llm_settings,
        MistralProvider, IndustrialPrompts
    )
    from modules.llm.nlp_integration import LLMEnhancedNLP, get_llm_nlp
    LLM_MODULE_AVAILABLE = True
except ImportError as e:
    LLM_MODULE_AVAILABLE = False
    logging.warning(f"LLM module not available: {e}")

# Import AI Observability module
try:
    from modules.ai_observability import (
        AIObservabilityEngine,
        AIObservabilityConfig,
        ModelType,
        AIRiskLevel,
    )
    AI_OBSERVABILITY_AVAILABLE = True
except ImportError as e:
    AI_OBSERVABILITY_AVAILABLE = False
    logging.warning(f"AI Observability module not available: {e}")

# Import LLM Observability module
try:
    from modules.llm_observability import (
        init_llm_telemetry,
        get_llm_telemetry,
        get_llm_metrics,
        get_observability_config,
        LLMObservabilityConfig,
        # Industrial data normalizer
        get_industrial_normalizer,
        IndustrialDataSource,
        NormalizedIndustrialEvent,
    )
    LLM_OBSERVABILITY_AVAILABLE = True
except ImportError as e:
    LLM_OBSERVABILITY_AVAILABLE = False
    logging.warning(f"LLM Observability module not available: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base directory for static files (resolve relative paths correctly)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Configuration
class Config:
    VICTORIA_METRICS_URL = os.getenv('VICTORIA_METRICS_URL', 'http://victoria-metrics:8428')
    OPENSEARCH_URL = os.getenv('OPENSEARCH_URL', 'http://opensearch:9200')
    OPENOBSERVE_URL = os.getenv('OPENOBSERVE_URL', 'http://openobserve:5080')
    OTEL_COLLECTOR_URL = os.getenv('OTEL_COLLECTOR_URL', 'http://otel-collector:8888')
    GRAFANA_URL = os.getenv('GRAFANA_URL', 'http://grafana:3000')
    REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', '10'))
    USE_SIMULATED_DATA = os.getenv('USE_SIMULATED_DATA', 'true').lower() == 'true'

config = Config()


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


# Pydantic Models
class ServiceStatus(BaseModel):
    name: str
    status: str
    port: int
    latency_ms: Optional[float] = None

class BusinessMetrics(BaseModel):
    oee: float
    quality_rate: float
    production_today: int
    cycle_time: float
    defects_today: int
    critical_alarms: int
    availability: float
    performance: float
    equipment: List[Dict[str, Any]]
    production_by_product: Dict[str, int]
    alarms: List[Dict[str, str]]

class TechMetrics(BaseModel):
    metrics_rate: int
    logs_rate: int
    traces_rate: int
    latency_p95: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    vm_active_series: int
    vm_storage_size: int
    vm_query_latency: float
    os_documents: int
    os_health: str
    os_nodes: int

class Event(BaseModel):
    time: datetime
    type: str
    title: str
    desc: str

class UnifiedMetrics(BaseModel):
    business: BusinessMetrics
    tech: TechMetrics
    services: List[ServiceStatus]
    events: List[Event]
    timestamp: datetime

# Initialize FastAPI app
app = FastAPI(
    title="OOVMTEL Unified View API",
    description="Unified Business-Tech View for Industrial Observability Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections
websocket_connections: List[WebSocket] = []

# Cache for metrics
metrics_cache: Dict[str, Any] = {}
cache_timestamp: Optional[datetime] = None

# HTTP client
http_client: Optional[httpx.AsyncClient] = None

# Initialize game-changer modules
nlp_engine: Optional[Any] = None
rca_engine: Optional[Any] = None
predictive_engine: Optional[Any] = None
remediation_engine: Optional[Any] = None
edge_manager: Optional[Any] = None
hpc_engine: Optional[Any] = None
llm_nlp: Optional[Any] = None  # LLM-enhanced NLP
ai_observability_engine: Optional[Any] = None  # AI Observability Engine
llm_telemetry: Optional[Any] = None  # LLM Observability Telemetry

@app.on_event("startup")
async def startup_event():
    global http_client, nlp_engine, rca_engine, predictive_engine, remediation_engine, edge_manager, hpc_engine, llm_nlp, ai_observability_engine

    http_client = httpx.AsyncClient(timeout=10.0)

    # Initialize game-changer modules
    if MODULES_AVAILABLE:
        try:
            nlp_engine = NLPEngine(
                victoria_metrics_url=config.VICTORIA_METRICS_URL,
                opensearch_url=config.OPENSEARCH_URL
            )
            rca_engine = RCAEngine(
                victoria_metrics_url=config.VICTORIA_METRICS_URL,
                opensearch_url=config.OPENSEARCH_URL
            )
            predictive_engine = PredictiveEngine(
                victoria_metrics_url=config.VICTORIA_METRICS_URL
            )
            remediation_engine = RemediationEngine(dry_run=True)  # Dry run by default
            edge_manager = EdgeAgentManager()
            hpc_engine = HPCEngine(
                auto_create_cluster=True,
                default_cluster_preset="medium"
            )
            logger.info("Game-changer modules initialized successfully (including HPC)")
        except Exception as e:
            logger.error(f"Failed to initialize modules: {e}")

    # Initialize LLM-enhanced NLP
    if LLM_MODULE_AVAILABLE:
        try:
            llm_nlp = LLMEnhancedNLP()
            initialized = await llm_nlp.initialize()
            if initialized:
                logger.info("LLM-enhanced NLP initialized successfully")
            else:
                logger.info("LLM not configured - using rule-based NLP fallback")
        except Exception as e:
            logger.warning(f"LLM initialization failed: {e}")
            llm_nlp = None

    # Initialize AI Observability Engine
    if AI_OBSERVABILITY_AVAILABLE:
        try:
            ai_observability_engine = AIObservabilityEngine(
                victoria_metrics_url=config.VICTORIA_METRICS_URL
            )
            await ai_observability_engine.initialize()
            logger.info("AI Observability Engine initialized successfully")
        except Exception as e:
            logger.warning(f"AI Observability initialization failed: {e}")
            ai_observability_engine = None

    # Initialize LLM Observability Telemetry
    if LLM_OBSERVABILITY_AVAILABLE:
        try:
            llm_telemetry = init_llm_telemetry()
            logger.info("LLM Observability Telemetry initialized successfully")
        except Exception as e:
            logger.warning(f"LLM Observability initialization failed: {e}")

    logger.info("OOVMTEL Unified View API started")
    # Start background task for metrics refresh
    asyncio.create_task(metrics_refresh_loop())

@app.on_event("shutdown")
async def shutdown_event():
    global http_client
    if http_client:
        await http_client.aclose()
    logger.info("OOVMTEL Unified View API stopped")

# Static files (using absolute path for reliability)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# Mount assets directory at /assets for Vite build compatibility
ASSETS_DIR = os.path.join(STATIC_DIR, "assets")
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

@app.get("/")
async def root():
    """Serve the main dashboard HTML page."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# =========================================
# Metrics Endpoints
# =========================================

@app.get("/api/metrics", response_model=UnifiedMetrics)
async def get_unified_metrics():
    """Get unified metrics from all sources."""
    global metrics_cache, cache_timestamp

    # Use cache if available and fresh
    if cache_timestamp and (datetime.utcnow() - cache_timestamp).seconds < config.REFRESH_INTERVAL:
        if metrics_cache:
            return UnifiedMetrics(**metrics_cache)

    try:
        if config.USE_SIMULATED_DATA:
            metrics = generate_simulated_metrics()
        else:
            metrics = await fetch_real_metrics()

        metrics_cache = metrics
        cache_timestamp = datetime.utcnow()
        return UnifiedMetrics(**metrics)
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        # Return simulated data as fallback
        return UnifiedMetrics(**generate_simulated_metrics())

@app.get("/api/metrics/business")
async def get_business_metrics():
    """Get business-specific metrics."""
    metrics = await get_unified_metrics()
    return metrics.business

@app.get("/api/metrics/tech")
async def get_tech_metrics():
    """Get tech-specific metrics."""
    metrics = await get_unified_metrics()
    return metrics.tech

@app.get("/api/services")
async def get_services_status():
    """Get status of all services."""
    metrics = await get_unified_metrics()
    return metrics.services

@app.get("/api/events")
async def get_recent_events(limit: int = 10):
    """Get recent events from both business and tech domains."""
    metrics = await get_unified_metrics()
    return metrics.events[:limit]

# =========================================
# WebSocket for Real-time Updates
# =========================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics updates."""
    await websocket.accept()
    websocket_connections.append(websocket)
    logger.info(f"WebSocket client connected. Total: {len(websocket_connections)}")

    try:
        while True:
            # Send metrics update every refresh interval
            metrics = await get_unified_metrics()
            await websocket.send_json(metrics.dict())
            await asyncio.sleep(config.REFRESH_INTERVAL)
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(websocket_connections)}")

# =========================================
# Data Fetching Functions
# =========================================

async def fetch_real_metrics() -> Dict[str, Any]:
    """Fetch real metrics from data sources."""
    try:
        # Fetch from VictoriaMetrics
        business_metrics = await fetch_victoria_metrics_business()
        tech_metrics = await fetch_victoria_metrics_tech()

        # Check service health
        services = await check_all_services()

        # Generate events from logs
        events = await fetch_recent_events()

        return {
            "business": business_metrics,
            "tech": tech_metrics,
            "services": services,
            "events": events,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error fetching real metrics: {e}")
        raise

async def fetch_victoria_metrics_business() -> Dict[str, Any]:
    """Fetch business metrics from VictoriaMetrics."""
    queries = {
        "oee": "avg(mes_oee_percent) or vector(75)",
        "quality_rate": "avg(mes_quality_rate_percent) or vector(96)",
        "production_today": "sum(increase(mes_production_count_total[24h])) or vector(1250)",
        "cycle_time": "avg(mes_cycle_time_seconds) or vector(25)",
        "defects_today": "sum(increase(mes_defects_total[24h])) or vector(12)",
        "critical_alarms": "sum(scada_alarms_total{severity=\"critical\"}) or vector(3)"
    }

    results = {}
    for name, query in queries.items():
        try:
            response = await http_client.get(
                f"{config.VICTORIA_METRICS_URL}/api/v1/query",
                params={"query": query}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("data", {}).get("result"):
                    results[name] = float(data["data"]["result"][0]["value"][1])
                else:
                    results[name] = 0
        except Exception as e:
            logger.warning(f"Error fetching {name}: {e}")
            results[name] = 0

    return {
        **results,
        "availability": results.get("oee", 75) * 1.1,
        "performance": results.get("oee", 75) * 0.95,
        "equipment": [],
        "production_by_product": {},
        "alarms": []
    }

async def fetch_victoria_metrics_tech() -> Dict[str, Any]:
    """Fetch tech metrics from VictoriaMetrics."""
    queries = {
        "metrics_rate": "sum(rate(otelcol_receiver_accepted_metric_points[5m])) or vector(85000)",
        "logs_rate": "sum(rate(otelcol_receiver_accepted_log_records[5m])) or vector(45000)",
        "traces_rate": "sum(rate(otelcol_receiver_accepted_spans[5m])) or vector(12000)",
        "vm_active_series": "vm_rows{type=\"indexdb\"} or vector(250000)",
        "vm_storage_size": "vm_data_size_bytes{type=\"indexdb\"} + vm_data_size_bytes{type=\"storage\"} or vector(5000000000)"
    }

    results = {}
    for name, query in queries.items():
        try:
            response = await http_client.get(
                f"{config.VICTORIA_METRICS_URL}/api/v1/query",
                params={"query": query}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("data", {}).get("result"):
                    results[name] = float(data["data"]["result"][0]["value"][1])
                else:
                    results[name] = 0
        except Exception as e:
            logger.warning(f"Error fetching {name}: {e}")
            results[name] = 0

    return {
        "metrics_rate": int(results.get("metrics_rate", 85000)),
        "logs_rate": int(results.get("logs_rate", 45000)),
        "traces_rate": int(results.get("traces_rate", 12000)),
        "latency_p95": 45.0,
        "error_rate": 0.05,
        "cpu_usage": 35.0,
        "memory_usage": 62.0,
        "disk_usage": 45.0,
        "vm_active_series": int(results.get("vm_active_series", 250000)),
        "vm_storage_size": int(results.get("vm_storage_size", 5000000000)),
        "vm_query_latency": 15.0,
        "os_documents": 125000,
        "os_health": "green",
        "os_nodes": 1
    }

async def check_all_services() -> List[Dict[str, Any]]:
    """Check health of all services."""
    services = [
        ("VictoriaMetrics", config.VICTORIA_METRICS_URL + "/health", 8428),
        ("OTEL Collector", config.OTEL_COLLECTOR_URL + "/health", 4317),
        ("OpenSearch", config.OPENSEARCH_URL + "/_cluster/health", 9200),
        ("OpenObserve", config.OPENOBSERVE_URL + "/healthz", 5080),
        ("Grafana", config.GRAFANA_URL + "/api/health", 3000)
    ]

    results = []
    for name, url, port in services:
        try:
            start = datetime.utcnow()
            response = await http_client.get(url)
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            status = "up" if response.status_code < 400 else "down"
        except Exception:
            status = "down"
            latency = None

        results.append({
            "name": name,
            "status": status,
            "port": port,
            "latency_ms": latency
        })

    return results

async def fetch_recent_events() -> List[Dict[str, Any]]:
    """Fetch recent events from logs/traces."""
    # For now, return simulated events
    return generate_simulated_events()

# =========================================
# Simulated Data Generation
# =========================================

def generate_simulated_metrics() -> Dict[str, Any]:
    """Generate simulated metrics for demo/testing."""
    return {
        "business": generate_simulated_business_metrics(),
        "tech": generate_simulated_tech_metrics(),
        "services": generate_simulated_services(),
        "events": generate_simulated_events(),
        "timestamp": datetime.utcnow()
    }

def generate_simulated_business_metrics() -> Dict[str, Any]:
    """Generate simulated business metrics."""
    oee = random.uniform(72, 88)
    return {
        "oee": oee,
        "quality_rate": random.uniform(94, 99),
        "production_today": random.randint(1100, 1400),
        "cycle_time": random.uniform(22, 30),
        "defects_today": random.randint(5, 20),
        "critical_alarms": random.randint(0, 5),
        "availability": random.uniform(85, 98),
        "performance": random.uniform(80, 95),
        "equipment": [
            {"name": "Reactor-001", "status": "running", "temp": random.uniform(60, 80), "pressure": random.uniform(4, 6), "power": random.uniform(100, 150)},
            {"name": "Mixer-002", "status": "running", "temp": random.uniform(40, 60), "pressure": random.uniform(2, 4), "power": random.uniform(50, 80)},
            {"name": "Pump-003", "status": "warning", "temp": random.uniform(30, 50), "pressure": random.uniform(3, 5), "power": random.uniform(20, 40)},
            {"name": "Furnace-004", "status": "running", "temp": random.uniform(200, 300), "pressure": random.uniform(1, 2), "power": random.uniform(200, 300)},
            {"name": "Conveyor-005", "status": "running", "temp": random.uniform(25, 35), "pressure": random.uniform(1, 2), "power": random.uniform(30, 50)},
            {"name": "Tank-006", "status": "stopped", "temp": random.uniform(20, 30), "pressure": random.uniform(1, 2), "power": 0}
        ],
        "production_by_product": {
            "Product A": random.randint(250, 350),
            "Product B": random.randint(200, 300),
            "Product C": random.randint(350, 450),
            "Product D": random.randint(280, 380)
        },
        "alarms": [
            {"severity": "critical", "message": "High temperature on Reactor-001"},
            {"severity": "warning", "message": "Vibration alert on Pump-003"},
            {"severity": "warning", "message": "Maintenance due on Mixer-002"}
        ]
    }

def generate_simulated_tech_metrics() -> Dict[str, Any]:
    """Generate simulated tech metrics."""
    return {
        "metrics_rate": random.randint(75000, 95000),
        "logs_rate": random.randint(40000, 55000),
        "traces_rate": random.randint(10000, 15000),
        "latency_p95": random.uniform(30, 60),
        "error_rate": random.uniform(0.01, 0.1),
        "cpu_usage": random.uniform(25, 50),
        "memory_usage": random.uniform(55, 75),
        "disk_usage": random.uniform(40, 60),
        "vm_active_series": random.randint(200000, 300000),
        "vm_storage_size": random.randint(4000000000, 6000000000),
        "vm_query_latency": random.uniform(10, 25),
        "os_documents": random.randint(100000, 150000),
        "os_health": "green",
        "os_nodes": 1
    }

def generate_simulated_services() -> List[Dict[str, Any]]:
    """Generate simulated service status."""
    return [
        {"name": "VictoriaMetrics", "status": "up", "port": 8428, "latency_ms": random.uniform(1, 5)},
        {"name": "OTEL Collector", "status": "up", "port": 4317, "latency_ms": random.uniform(1, 3)},
        {"name": "OpenSearch", "status": "up", "port": 9200, "latency_ms": random.uniform(5, 15)},
        {"name": "OpenObserve", "status": "up", "port": 5080, "latency_ms": random.uniform(2, 6)},
        {"name": "Grafana", "status": "up", "port": 3000, "latency_ms": random.uniform(1, 4)}
    ]

def generate_simulated_events() -> List[Dict[str, Any]]:
    """Generate simulated events."""
    events = [
        {"type": "business", "title": "Production batch completed", "desc": f"Batch #{random.randint(4000, 5000)} - {random.randint(100, 200)} units"},
        {"type": "tech", "title": "OTEL pipeline spike", "desc": f"{random.randint(100, 150)}K metrics/sec processed"},
        {"type": "business", "title": "Quality check passed", "desc": f"Product A - {random.uniform(98, 99.9):.1f}% quality"},
        {"type": "tech", "title": "Memory optimization", "desc": f"VM GC completed - {random.randint(1, 3)}GB freed"},
        {"type": "business", "title": "Equipment maintenance", "desc": "Pump-003 scheduled check"}
    ]

    now = datetime.utcnow()
    for i, event in enumerate(events):
        event["time"] = (now - timedelta(minutes=i * 3 + random.randint(1, 5))).isoformat()

    return events

# =========================================
# NLP/Conversational Analytics Endpoints
# =========================================

class ChatRequest(BaseModel):
    query: str
    language: str = "auto"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    intent: str
    confidence: float
    visualizations: List[Dict[str, Any]] = []
    suggestions: List[str] = []
    processing_time_ms: float = 0

@app.post("/api/chat", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """Process a natural language query about industrial data."""
    if not MODULES_AVAILABLE or not nlp_engine:
        raise HTTPException(status_code=503, detail="NLP module not available")

    try:
        # Get current metrics for context
        metrics = generate_simulated_metrics() if config.USE_SIMULATED_DATA else await fetch_real_metrics()

        conv_query = ConversationalQuery(
            query=request.query,
            language=request.language,
            session_id=request.session_id
        )

        response = await nlp_engine.process_query(conv_query, metrics)

        return ChatResponse(
            answer=response.answer,
            intent=response.intent.value,
            confidence=response.confidence,
            visualizations=[v.model_dump() for v in response.visualizations],
            suggestions=response.suggestions,
            processing_time_ms=response.processing_time_ms
        )
    except Exception as e:
        logger.error(f"Chat query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =========================================
# Root Cause Analysis Endpoints
# =========================================

class RCARequest(BaseModel):
    incident_id: Optional[str] = None
    title: str
    description: str
    severity: str = "medium"
    category: str = "performance"

@app.post("/api/rca/analyze")
async def analyze_root_cause(request: RCARequest):
    """Perform root cause analysis on an incident."""
    if not MODULES_AVAILABLE or not rca_engine:
        raise HTTPException(status_code=503, detail="RCA module not available")

    try:
        # Create incident
        incident = Incident(
            id=request.incident_id or f"INC-{uuid.uuid4().hex[:8].upper()}",
            title=request.title,
            description=request.description,
            severity=IncidentSeverity(request.severity),
            category=IncidentCategory(request.category),
            detected_at=datetime.utcnow()
        )

        # Get current metrics
        metrics = generate_simulated_metrics() if config.USE_SIMULATED_DATA else await fetch_real_metrics()

        # Perform analysis
        analysis = await rca_engine.analyze_incident(incident, metrics)

        return {
            "incident_id": analysis.incident.id,
            "root_causes": [
                {
                    "name": rc.node.name,
                    "probability": rc.probability,
                    "evidence": rc.evidence,
                    "remediation": rc.remediation.model_dump() if rc.remediation else None
                }
                for rc in analysis.root_causes
            ],
            "causal_graph": analysis.causal_graph.to_d3_format(),
            "timeline": analysis.timeline,
            "summary": analysis.summary,
            "analysis_duration_ms": analysis.analysis_duration_ms
        }
    except Exception as e:
        logger.error(f"RCA error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rca/detect")
async def detect_incidents():
    """Automatically detect incidents from current metrics."""
    if not MODULES_AVAILABLE or not rca_engine:
        raise HTTPException(status_code=503, detail="RCA module not available")

    try:
        metrics = generate_simulated_metrics() if config.USE_SIMULATED_DATA else await fetch_real_metrics()
        incidents = await rca_engine.detect_incidents(metrics)

        return {
            "incidents": [inc.model_dump() for inc in incidents],
            "count": len(incidents)
        }
    except Exception as e:
        logger.error(f"Incident detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =========================================
# Predictive Maintenance Endpoints
# =========================================

@app.get("/api/predictive/analyze")
async def predictive_analysis(equipment: Optional[str] = Query(None)):
    """Perform predictive maintenance analysis."""
    if not MODULES_AVAILABLE or not predictive_engine:
        raise HTTPException(status_code=503, detail="Predictive module not available")

    try:
        metrics = generate_simulated_metrics() if config.USE_SIMULATED_DATA else await fetch_real_metrics()

        equipment_filter = [equipment] if equipment else None
        analysis = await predictive_engine.analyze(metrics, equipment_filter)

        return {
            "analysis_id": analysis.analysis_id,
            "equipment_health": [eh.model_dump() for eh in analysis.equipment_health],
            "anomalies": [a.model_dump() for a in analysis.anomalies],
            "trends": [t.model_dump() for t in analysis.trends],
            "rul_predictions": [r.model_dump() for r in analysis.rul_predictions],
            "failure_predictions": [f.model_dump() for f in analysis.failure_predictions],
            "maintenance_recommendations": [m.model_dump() for m in analysis.maintenance_recommendations],
            "alerts": analysis.alerts,
            "summary": analysis.summary,
            "analysis_duration_ms": analysis.analysis_duration_ms
        }
    except Exception as e:
        logger.error(f"Predictive analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predictive/health")
async def equipment_health():
    """Get equipment health scores."""
    if not MODULES_AVAILABLE or not predictive_engine:
        raise HTTPException(status_code=503, detail="Predictive module not available")

    try:
        metrics = generate_simulated_metrics() if config.USE_SIMULATED_DATA else await fetch_real_metrics()
        analysis = await predictive_engine.analyze(metrics)

        return {
            "equipment": [
                {
                    "name": eh.equipment,
                    "overall_score": eh.overall_score,
                    "status": eh.status,
                    "trend": eh.trend.value,
                    "anomalies": eh.anomalies_count,
                    "warnings": eh.active_warnings
                }
                for eh in analysis.equipment_health
            ]
        }
    except Exception as e:
        logger.error(f"Equipment health error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predictive/alerts")
async def predictive_alerts():
    """Get predictive maintenance alerts."""
    if not MODULES_AVAILABLE or not predictive_engine:
        raise HTTPException(status_code=503, detail="Predictive module not available")

    try:
        metrics = generate_simulated_metrics() if config.USE_SIMULATED_DATA else await fetch_real_metrics()
        analysis = await predictive_engine.analyze(metrics)

        return {"alerts": analysis.alerts}
    except Exception as e:
        logger.error(f"Predictive alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =========================================
# Auto-Remediation Endpoints
# =========================================

@app.get("/api/remediation/runbooks")
async def list_runbooks(category: Optional[str] = Query(None)):
    """List available runbooks."""
    if not MODULES_AVAILABLE or not remediation_engine:
        raise HTTPException(status_code=503, detail="Remediation module not available")

    try:
        runbooks = remediation_engine.runbook_library.list_runbooks(category=category)
        return {
            "runbooks": [
                {
                    "id": rb.id,
                    "name": rb.name,
                    "description": rb.description,
                    "category": rb.category,
                    "risk_level": rb.risk_level,
                    "estimated_duration": rb.estimated_duration_minutes,
                    "requires_downtime": rb.requires_downtime,
                    "success_rate": rb.success_rate
                }
                for rb in runbooks
            ]
        }
    except Exception as e:
        logger.error(f"List runbooks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class RemediationRequest(BaseModel):
    runbook_id: str
    target: str
    incident_id: Optional[str] = None

@app.post("/api/remediation/execute")
async def execute_remediation(request: RemediationRequest):
    """Execute a remediation runbook."""
    if not MODULES_AVAILABLE or not remediation_engine:
        raise HTTPException(status_code=503, detail="Remediation module not available")

    try:
        action = await remediation_engine.create_action(
            runbook_id=request.runbook_id,
            target=request.target,
            incident_id=request.incident_id
        )

        # For auto-approved actions, execute immediately
        if action.status.value == "approved":
            action = await remediation_engine.execute_action(action)

        return {
            "action_id": action.id,
            "status": action.status.value,
            "runbook": action.runbook_name,
            "target": action.target,
            "requires_approval": action.approval_request is not None,
            "approval_id": action.approval_request.id if action.approval_request else None
        }
    except Exception as e:
        logger.error(f"Execute remediation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/remediation/pending")
async def pending_approvals():
    """Get pending approval requests."""
    if not MODULES_AVAILABLE or not remediation_engine:
        raise HTTPException(status_code=503, detail="Remediation module not available")

    try:
        pending = remediation_engine.get_pending_approvals()
        return {
            "pending": [
                {
                    "id": p.id,
                    "action_id": p.action_id,
                    "runbook": p.runbook_name,
                    "reason": p.reason,
                    "risk_summary": p.risk_summary,
                    "requested_at": p.requested_at.isoformat(),
                    "expires_at": p.expires_at.isoformat()
                }
                for p in pending
            ]
        }
    except Exception as e:
        logger.error(f"Pending approvals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ApprovalRequest(BaseModel):
    approval_id: str
    approver: str
    approved: bool
    notes: str = ""

@app.post("/api/remediation/approve")
async def approve_remediation(request: ApprovalRequest):
    """Approve or reject a remediation action."""
    if not MODULES_AVAILABLE or not remediation_engine:
        raise HTTPException(status_code=503, detail="Remediation module not available")

    try:
        if request.approved:
            approval = await remediation_engine.approve_action(
                request.approval_id,
                request.approver,
                request.notes
            )
        else:
            approval = await remediation_engine.reject_action(
                request.approval_id,
                request.approver,
                request.notes
            )

        return {
            "approval_id": approval.id,
            "status": approval.status,
            "approved_by": approval.approved_by
        }
    except Exception as e:
        logger.error(f"Approval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/remediation/history")
async def remediation_history(limit: int = Query(20)):
    """Get remediation action history."""
    if not MODULES_AVAILABLE or not remediation_engine:
        raise HTTPException(status_code=503, detail="Remediation module not available")

    try:
        history = remediation_engine.get_action_history(limit=limit)
        return {
            "actions": [
                {
                    "id": a.id,
                    "runbook": a.runbook_name,
                    "target": a.target,
                    "status": a.status.value,
                    "success": a.overall_success,
                    "created_at": a.created_at.isoformat(),
                    "completed_at": a.completed_at.isoformat() if a.completed_at else None
                }
                for a in history
            ]
        }
    except Exception as e:
        logger.error(f"History error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/remediation/stats")
async def remediation_stats():
    """Get remediation statistics."""
    if not MODULES_AVAILABLE or not remediation_engine:
        raise HTTPException(status_code=503, detail="Remediation module not available")

    try:
        return remediation_engine.get_statistics()
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =========================================
# Edge Computing Endpoints
# =========================================

class EdgeRegistration(BaseModel):
    site_name: str
    location: str = ""
    preset: str = "high_volume"

@app.post("/api/edge/register")
async def register_edge_agent(registration: EdgeRegistration):
    """Register a new edge agent."""
    if not MODULES_AVAILABLE or not edge_manager:
        raise HTTPException(status_code=503, detail="Edge module not available")

    try:
        from modules.edge.models import EDGE_PRESETS

        agent_id = f"EDGE-{uuid.uuid4().hex[:8].upper()}"
        preset = EDGE_PRESETS.get(registration.preset, EDGE_PRESETS["high_volume"])

        config = EdgeConfig(
            agent_id=agent_id,
            site_name=registration.site_name,
            location=registration.location,
            central_url="http://localhost:8080"
        )

        result = edge_manager.register_agent(agent_id, registration.site_name, config)
        return result
    except Exception as e:
        logger.error(f"Edge registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/edge/agents")
async def list_edge_agents():
    """List all registered edge agents."""
    if not MODULES_AVAILABLE or not edge_manager:
        raise HTTPException(status_code=503, detail="Edge module not available")

    try:
        return {
            "agents": edge_manager.get_all_agents(),
            "aggregated": edge_manager.get_aggregated_metrics()
        }
    except Exception as e:
        logger.error(f"List agents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/edge/agents/{agent_id}")
async def get_edge_agent(agent_id: str):
    """Get specific edge agent status."""
    if not MODULES_AVAILABLE or not edge_manager:
        raise HTTPException(status_code=503, detail="Edge module not available")

    try:
        status = edge_manager.get_agent_status(agent_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/edge/data")
async def receive_edge_data(data: Dict[str, Any] = Body(...)):
    """Receive data from edge agents."""
    # This endpoint would receive aggregated data from edge agents
    logger.info(f"Received edge data: {len(data.get('data', []))} records")
    return {"status": "received", "count": len(data.get("data", []))}

@app.post("/api/edge/alerts")
async def receive_edge_alerts(alerts: List[Dict[str, Any]] = Body(...)):
    """Receive alerts from edge agents."""
    logger.info(f"Received {len(alerts)} edge alerts")
    return {"status": "received", "count": len(alerts)}

# =========================================
# Game-Changer Modules Status
# =========================================

@app.get("/api/modules/status")
async def modules_status():
    """Get status of all game-changer modules."""
    return {
        "modules_available": MODULES_AVAILABLE,
        "nlp": {
            "enabled": nlp_engine is not None,
            "description": "Natural language queries for industrial data"
        },
        "rca": {
            "enabled": rca_engine is not None,
            "description": "Automatic root cause analysis with causal graphs"
        },
        "predictive": {
            "enabled": predictive_engine is not None,
            "description": "Anomaly detection and failure prediction"
        },
        "remediation": {
            "enabled": remediation_engine is not None,
            "description": "Automatic incident remediation with runbooks",
            "runbooks_count": remediation_engine.runbook_library.count() if remediation_engine else 0
        },
        "edge": {
            "enabled": edge_manager is not None,
            "description": "Edge computing agent management",
            "agents_count": len(edge_manager.agents) if edge_manager else 0
        },
        "hpc": {
            "enabled": hpc_engine is not None,
            "description": "High Performance Computing for simulations and ML",
            "clusters_count": len(hpc_engine.list_clusters()) if hpc_engine else 0,
            "capabilities": ["gpu_acceleration", "distributed_training", "what_if_simulations", "parallel_processing"] if hpc_engine else []
        },
        "llm": {
            "enabled": llm_nlp is not None and llm_nlp.is_llm_available if llm_nlp else False,
            "module_available": LLM_MODULE_AVAILABLE,
            "description": "LLM-enhanced NLP for natural language understanding",
            "provider": get_llm_settings().active_provider.value if LLM_MODULE_AVAILABLE else None,
            "fallback_enabled": get_llm_settings().fallback_to_rules if LLM_MODULE_AVAILABLE else True
        },
        "ai_observability": {
            "enabled": ai_observability_engine is not None,
            "module_available": AI_OBSERVABILITY_AVAILABLE,
            "description": "AI/ML model monitoring, drift detection, and explainability",
            "models_count": len(ai_observability_engine.get_all_models()) if ai_observability_engine else 0,
            "capabilities": [
                "model_registry",
                "drift_detection",
                "performance_tracking",
                "explainability",
                "eu_ai_act_compliance"
            ] if ai_observability_engine else []
        }
    }

# =========================================
# LLM - Large Language Model Endpoints
# =========================================

@app.get("/api/llm/status")
async def llm_status():
    """Get LLM module status and configuration."""
    if not LLM_MODULE_AVAILABLE:
        return {
            "available": False,
            "reason": "LLM module not installed"
        }

    settings = get_llm_settings()
    return {
        "available": True,
        "enabled": settings.llm_enabled,
        "configured": settings.is_configured(),
        "provider": settings.active_provider.value,
        "model": settings.mistral.model if settings.active_provider.value == "mistral" else None,
        "fallback_enabled": settings.fallback_to_rules,
        "llm_active": llm_nlp.is_llm_available if llm_nlp else False
    }

@app.get("/api/llm/health")
async def llm_health():
    """Health check for LLM provider."""
    if not LLM_MODULE_AVAILABLE or not llm_nlp:
        return {
            "status": "unavailable",
            "reason": "LLM module not available"
        }

    try:
        health = await llm_nlp.health_check()
        return health
    except Exception as e:
        logger.error(f"LLM health check error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/api/llm/models")
async def list_llm_models():
    """List available LLM models."""
    if not LLM_MODULE_AVAILABLE:
        raise HTTPException(status_code=503, detail="LLM module not available")

    settings = get_llm_settings()
    return {
        "active_provider": settings.active_provider.value,
        "mistral_models": settings.mistral.AVAILABLE_MODELS,
        "current_model": settings.mistral.model
    }

class LLMChatRequest(BaseModel):
    """Request model for LLM-enhanced chat."""
    query: str
    language: str = "fr"
    session_id: Optional[str] = None
    use_llm: bool = True  # Set to False to force rule-based response

@app.post("/api/llm/chat")
async def llm_chat(request: LLMChatRequest):
    """
    LLM-enhanced chat endpoint.

    Uses Mistral or other configured LLM for natural language understanding
    and response generation. Falls back to rule-based NLP if LLM unavailable.
    """
    if not MODULES_AVAILABLE or not nlp_engine:
        raise HTTPException(status_code=503, detail="NLP module not available")

    try:
        # Get current metrics for context
        metrics = generate_simulated_metrics() if config.USE_SIMULATED_DATA else await fetch_real_metrics()

        # First, use rule-based NLP for intent and entity extraction
        conv_query = ConversationalQuery(
            query=request.query,
            language=request.language,
            session_id=request.session_id
        )
        nlp_response = await nlp_engine.process_query(conv_query, metrics)

        # If LLM is available and requested, enhance the response
        llm_enhanced = False
        llm_response_data = None

        if request.use_llm and LLM_MODULE_AVAILABLE and llm_nlp and llm_nlp.is_llm_available:
            try:
                # Extract entities as dict
                entities_dict = {
                    "equipment": nlp_response.entities.equipment,
                    "metrics": nlp_response.entities.metrics,
                    "time_range": str(nlp_response.entities.time_range) if nlp_response.entities.time_range else None
                }

                llm_response_data = await llm_nlp.generate_response(
                    query=request.query,
                    intent=nlp_response.intent.value,
                    entities=entities_dict,
                    metrics_context=metrics,
                    language=request.language,
                    session_id=request.session_id
                )
                llm_enhanced = llm_response_data.get("llm_enhanced", False)
            except Exception as e:
                logger.warning(f"LLM enhancement failed: {e}")

        # Build response
        if llm_enhanced and llm_response_data:
            return {
                "answer": llm_response_data["content"],
                "intent": nlp_response.intent.value,
                "confidence": nlp_response.confidence,
                "visualizations": [v.model_dump() for v in nlp_response.visualizations],
                "suggestions": nlp_response.suggestions,
                "processing_time_ms": nlp_response.processing_time_ms,
                "llm_enhanced": True,
                "llm_model": llm_response_data.get("model"),
                "llm_tokens": llm_response_data.get("tokens_used", 0),
                "llm_latency_ms": llm_response_data.get("latency_ms", 0)
            }
        else:
            return {
                "answer": nlp_response.answer,
                "intent": nlp_response.intent.value,
                "confidence": nlp_response.confidence,
                "visualizations": [v.model_dump() for v in nlp_response.visualizations],
                "suggestions": nlp_response.suggestions,
                "processing_time_ms": nlp_response.processing_time_ms,
                "llm_enhanced": False
            }

    except Exception as e:
        logger.error(f"LLM chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================================
# LLM Observability Endpoints
# =========================================

@app.get("/api/llm/observability/status")
async def llm_observability_status():
    """
    Get LLM observability module status.

    Returns configuration, telemetry status, and availability information.
    """
    if not LLM_OBSERVABILITY_AVAILABLE:
        return {
            "available": False,
            "reason": "LLM Observability module not installed"
        }

    try:
        config = get_observability_config()
        telemetry = get_llm_telemetry()
        metrics = get_llm_metrics()

        return {
            "available": True,
            "config": config.to_dict(),
            "telemetry": telemetry.get_status(),
            "metrics": metrics.get_status(),
        }
    except Exception as e:
        logger.error(f"LLM observability status error: {e}")
        return {
            "available": True,
            "error": str(e)
        }


@app.get("/api/llm/observability/metrics")
async def llm_observability_metrics(
    window_minutes: int = Query(default=60, ge=1, le=1440, description="Time window in minutes"),
    provider: Optional[str] = Query(default=None, description="Filter by provider"),
    model: Optional[str] = Query(default=None, description="Filter by model"),
):
    """
    Get aggregated LLM metrics.

    Returns request counts, token usage, latency statistics, costs, and error rates.
    """
    if not LLM_OBSERVABILITY_AVAILABLE:
        raise HTTPException(status_code=503, detail="LLM Observability module not available")

    try:
        metrics = get_llm_metrics()
        aggregated = metrics.get_aggregated_metrics(
            window_minutes=window_minutes,
            provider=provider,
            model=model,
        )
        return aggregated.to_dict()
    except Exception as e:
        logger.error(f"LLM observability metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/llm/observability/metrics/realtime")
async def llm_observability_realtime_metrics():
    """
    Get real-time LLM metrics for last 5 minutes.

    Provides quick access to current operational state.
    """
    if not LLM_OBSERVABILITY_AVAILABLE:
        raise HTTPException(status_code=503, detail="LLM Observability module not available")

    try:
        metrics = get_llm_metrics()
        realtime = metrics.get_aggregated_metrics(window_minutes=5)
        hourly = metrics.get_current_hour_usage()

        return {
            "realtime_5min": realtime.to_dict(),
            "hourly_usage": hourly,
            "active_requests": metrics._active_requests,
        }
    except Exception as e:
        logger.error(f"LLM realtime metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/llm/observability/alerts")
async def llm_observability_alerts():
    """
    Get active LLM observability alerts.

    Checks for threshold violations (latency, error rate, token limits, costs).
    """
    if not LLM_OBSERVABILITY_AVAILABLE:
        raise HTTPException(status_code=503, detail="LLM Observability module not available")

    try:
        metrics = get_llm_metrics()
        alerts = metrics.check_alerts()

        return {
            "alerts": alerts,
            "alert_count": len(alerts),
            "has_critical": any(a["severity"] == "critical" for a in alerts),
            "has_warning": any(a["severity"] == "warning" for a in alerts),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"LLM alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/llm/observability/dashboard")
async def llm_observability_dashboard():
    """
    Get comprehensive dashboard data for LLM observability.

    Combines metrics, alerts, and configuration for dashboard rendering.
    """
    if not LLM_OBSERVABILITY_AVAILABLE:
        raise HTTPException(status_code=503, detail="LLM Observability module not available")

    try:
        config = get_observability_config()
        metrics = get_llm_metrics()
        telemetry = get_llm_telemetry()

        # Get metrics for different windows
        metrics_5m = metrics.get_aggregated_metrics(window_minutes=5)
        metrics_1h = metrics.get_aggregated_metrics(window_minutes=60)
        metrics_24h = metrics.get_aggregated_metrics(window_minutes=1440)
        hourly = metrics.get_current_hour_usage()
        alerts = metrics.check_alerts()

        # Determine overall health
        if any(a["severity"] == "critical" for a in alerts):
            health_status = "critical"
        elif any(a["severity"] == "warning" for a in alerts):
            health_status = "warning"
        else:
            health_status = "healthy"

        return {
            "health_status": health_status,
            "metrics": {
                "last_5_minutes": metrics_5m.to_dict(),
                "last_hour": metrics_1h.to_dict(),
                "last_24_hours": metrics_24h.to_dict(),
            },
            "hourly_usage": hourly,
            "alerts": alerts,
            "config": {
                "service_name": config.service_name,
                "environment": config.environment,
                "tracing_enabled": config.tracing.enabled,
                "metrics_enabled": config.metrics.enabled,
                "sample_rate": config.tracing.sample_rate,
            },
            "thresholds": {
                "latency_warning_ms": config.alerting.latency_warning_ms,
                "latency_critical_ms": config.alerting.latency_critical_ms,
                "error_rate_warning_pct": config.alerting.error_rate_warning_pct,
                "error_rate_critical_pct": config.alerting.error_rate_critical_pct,
                "hourly_token_limit": config.alerting.hourly_token_limit,
                "hourly_cost_limit_usd": config.alerting.hourly_cost_limit_usd,
            },
            "telemetry_status": telemetry.get_status(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"LLM dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class LLMObservabilityConfigUpdate(BaseModel):
    """Request model for updating observability config."""
    latency_warning_ms: Optional[float] = None
    latency_critical_ms: Optional[float] = None
    error_rate_warning_pct: Optional[float] = None
    error_rate_critical_pct: Optional[float] = None
    hourly_token_limit: Optional[int] = None
    hourly_cost_limit_usd: Optional[float] = None


@app.post("/api/llm/observability/config")
async def update_llm_observability_config(update: LLMObservabilityConfigUpdate):
    """
    Update LLM observability alerting thresholds.

    Note: Changes are applied at runtime but not persisted to env vars.
    """
    if not LLM_OBSERVABILITY_AVAILABLE:
        raise HTTPException(status_code=503, detail="LLM Observability module not available")

    try:
        config = get_observability_config()

        # Update alerting config
        if update.latency_warning_ms is not None:
            config.alerting.latency_warning_ms = update.latency_warning_ms
        if update.latency_critical_ms is not None:
            config.alerting.latency_critical_ms = update.latency_critical_ms
        if update.error_rate_warning_pct is not None:
            config.alerting.error_rate_warning_pct = update.error_rate_warning_pct
        if update.error_rate_critical_pct is not None:
            config.alerting.error_rate_critical_pct = update.error_rate_critical_pct
        if update.hourly_token_limit is not None:
            config.alerting.hourly_token_limit = update.hourly_token_limit
        if update.hourly_cost_limit_usd is not None:
            config.alerting.hourly_cost_limit_usd = update.hourly_cost_limit_usd

        return {
            "message": "Configuration updated successfully",
            "config": config.to_dict(),
        }
    except Exception as e:
        logger.error(f"LLM config update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================================
# Industrial Data Normalization Endpoints
# =========================================

class IndustrialDataInput(BaseModel):
    """Input model for industrial data normalization."""
    source: str  # scada, mes, plm, opcua
    data: Dict[str, Any]
    correlation_id: Optional[str] = None


class IndustrialDataBatchInput(BaseModel):
    """Input model for batch industrial data normalization."""
    source: str
    data_list: List[Dict[str, Any]]
    correlation_id: Optional[str] = None


@app.post("/api/industrial/normalize")
async def normalize_industrial_data_endpoint(input_data: IndustrialDataInput):
    """
    Normalize a single industrial data point.

    Supports sources: scada, mes, plm, opcua
    """
    if not LLM_OBSERVABILITY_AVAILABLE:
        raise HTTPException(status_code=503, detail="LLM Observability module not available")

    try:
        normalizer = get_industrial_normalizer()
        event = normalizer.normalize(
            source=input_data.source,
            data=input_data.data,
            correlation_id=input_data.correlation_id,
        )
        return event.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Industrial data normalization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/industrial/normalize/batch")
async def normalize_industrial_data_batch(input_data: IndustrialDataBatchInput):
    """
    Normalize a batch of industrial data points.

    All data points must be from the same source.
    """
    if not LLM_OBSERVABILITY_AVAILABLE:
        raise HTTPException(status_code=503, detail="LLM Observability module not available")

    try:
        normalizer = get_industrial_normalizer()
        events = normalizer.normalize_batch(
            source=input_data.source,
            data_list=input_data.data_list,
            correlation_id=input_data.correlation_id,
        )
        return {
            "count": len(events),
            "events": [e.to_dict() for e in events],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Industrial data batch normalization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/industrial/events")
async def get_industrial_events(
    source: Optional[str] = Query(default=None, description="Filter by source (scada, mes, plm, opcua)"),
    minutes: int = Query(default=5, ge=1, le=60, description="Time window in minutes"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max events to return"),
):
    """
    Get recent normalized industrial events from buffer.
    """
    if not LLM_OBSERVABILITY_AVAILABLE:
        raise HTTPException(status_code=503, detail="LLM Observability module not available")

    try:
        normalizer = get_industrial_normalizer()

        source_enum = None
        if source:
            try:
                source_enum = IndustrialDataSource(source.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid source: {source}")

        events = normalizer.get_recent_events(
            source=source_enum,
            minutes=minutes,
            limit=limit,
        )

        return {
            "count": len(events),
            "events": [e.to_dict() for e in events],
            "filters": {
                "source": source,
                "minutes": minutes,
                "limit": limit,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Industrial events retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/industrial/context")
async def get_industrial_context_for_llm(
    equipment: Optional[str] = Query(default=None, description="Filter by equipment ID"),
    area: Optional[str] = Query(default=None, description="Filter by area"),
    sources: Optional[str] = Query(default=None, description="Comma-separated sources (scada,mes,plm,opcua)"),
    minutes: int = Query(default=15, ge=1, le=60, description="Time window in minutes"),
    max_events: int = Query(default=50, ge=1, le=200, description="Max events to include"),
):
    """
    Get industrial context formatted for LLM queries.

    Returns a human-readable summary of recent industrial data
    that can be used to enrich LLM responses.
    """
    if not LLM_OBSERVABILITY_AVAILABLE:
        raise HTTPException(status_code=503, detail="LLM Observability module not available")

    try:
        normalizer = get_industrial_normalizer()

        # Parse sources
        source_list = None
        if sources:
            source_list = []
            for s in sources.split(","):
                try:
                    source_list.append(IndustrialDataSource(s.strip().lower()))
                except ValueError:
                    pass

        context = normalizer.get_context_for_llm(
            equipment=equipment,
            area=area,
            sources=source_list,
            minutes=minutes,
            max_events=max_events,
        )

        return {
            "context": context,
            "filters": {
                "equipment": equipment,
                "area": area,
                "sources": sources,
                "minutes": minutes,
                "max_events": max_events,
            },
        }
    except Exception as e:
        logger.error(f"Industrial context generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/industrial/correlations")
async def get_industrial_correlations(
    time_window_seconds: int = Query(default=60, ge=1, le=300, description="Correlation time window"),
    equipment: Optional[str] = Query(default=None, description="Filter by equipment ID"),
):
    """
    Find correlated events across industrial sources.

    Groups events that occurred within the time window
    and may be related (e.g., SCADA alarm followed by MES downtime).
    """
    if not LLM_OBSERVABILITY_AVAILABLE:
        raise HTTPException(status_code=503, detail="LLM Observability module not available")

    try:
        normalizer = get_industrial_normalizer()

        groups = normalizer.correlate_events(
            time_window_seconds=time_window_seconds,
            equipment=equipment,
        )

        return {
            "correlation_groups": [
                {
                    "count": len(group),
                    "time_span_seconds": (group[-1].timestamp.utc - group[0].timestamp.utc).total_seconds(),
                    "sources": list(set(e.source.value for e in group)),
                    "events": [e.to_dict() for e in group],
                }
                for group in groups
            ],
            "total_groups": len(groups),
        }
    except Exception as e:
        logger.error(f"Industrial correlation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/industrial/statistics")
async def get_industrial_statistics():
    """
    Get industrial data normalizer statistics.
    """
    if not LLM_OBSERVABILITY_AVAILABLE:
        raise HTTPException(status_code=503, detail="LLM Observability module not available")

    try:
        normalizer = get_industrial_normalizer()
        return normalizer.get_statistics()
    except Exception as e:
        logger.error(f"Industrial statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/industrial/sources")
async def list_industrial_sources():
    """
    List supported industrial data sources and their schemas.
    """
    return {
        "sources": [
            {
                "id": "scada",
                "name": "SCADA",
                "description": "Supervisory Control and Data Acquisition",
                "schema": {
                    "timestamp": "ISO 8601 timestamp",
                    "tag_id": "Unique tag identifier (e.g., SCADA.ZONE_A.REACTOR_001.TEMP)",
                    "tag_name": "Human-readable tag name",
                    "value": "Numeric or string value",
                    "unit": "Engineering unit (e.g., °C, bar, m³/h)",
                    "quality": "Data quality (good, uncertain, bad)",
                    "source": "PLC/RTU source identifier",
                    "area": "Plant area",
                    "equipment_id": "Equipment identifier",
                },
            },
            {
                "id": "mes",
                "name": "MES",
                "description": "Manufacturing Execution System",
                "schema": {
                    "timestamp": "ISO 8601 timestamp",
                    "event_type": "Event type (production_start, production_end, quality_check, etc.)",
                    "order_id": "Production order ID",
                    "product_id": "Product identifier",
                    "workstation_id": "Workstation identifier",
                    "operator_id": "Operator identifier",
                    "quantity": "Produced quantity",
                    "status": "Event status",
                    "cycle_time_ms": "Cycle time in milliseconds",
                    "quality_score": "Quality score (0-100)",
                    "defects": "Number of defects",
                },
            },
            {
                "id": "plm",
                "name": "PLM",
                "description": "Product Lifecycle Management",
                "schema": {
                    "timestamp": "ISO 8601 timestamp",
                    "document_id": "Document identifier",
                    "revision": "Document revision",
                    "author": "Author identifier",
                    "change_type": "Change type (create, modify, revision, approve, etc.)",
                    "component_id": "Component identifier",
                    "bom_level": "BOM hierarchy level",
                    "status": "Document status",
                    "approval_status": "Approval status",
                },
            },
            {
                "id": "opcua",
                "name": "OPC-UA",
                "description": "Open Platform Communications Unified Architecture",
                "schema": {
                    "timestamp": "ISO 8601 timestamp",
                    "node_id": "OPC-UA node identifier (e.g., ns=2;s=Device1.Temperature)",
                    "display_name": "Human-readable node name",
                    "value": "Node value",
                    "data_type": "OPC-UA data type (Double, Int32, Boolean, String, etc.)",
                    "status_code": "OPC-UA status code",
                    "source_timestamp": "Source timestamp",
                    "server_timestamp": "Server timestamp",
                    "namespace": "OPC-UA namespace",
                },
            },
        ],
    }


# =========================================
# HPC - High Performance Computing Endpoints
# =========================================

@app.get("/api/hpc/status")
async def hpc_status():
    """Get HPC engine status and capabilities."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        return hpc_engine.get_engine_status()
    except Exception as e:
        logger.error(f"HPC status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hpc/health")
async def hpc_health():
    """Health check for HPC components."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        return hpc_engine.health_check()
    except Exception as e:
        logger.error(f"HPC health error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hpc/metrics")
async def hpc_metrics():
    """Get aggregate HPC metrics."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        metrics = hpc_engine.get_hpc_metrics()
        return metrics.model_dump()
    except Exception as e:
        logger.error(f"HPC metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Cluster Management
@app.get("/api/hpc/clusters")
async def list_hpc_clusters():
    """List all HPC clusters."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        clusters = hpc_engine.list_clusters()
        return {
            "clusters": [c.model_dump() for c in clusters],
            "count": len(clusters)
        }
    except Exception as e:
        logger.error(f"List clusters error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ClusterCreateRequest(BaseModel):
    name: str
    preset: str = "medium"
    description: str = ""

@app.post("/api/hpc/clusters")
async def create_hpc_cluster(request: ClusterCreateRequest):
    """Create a new HPC cluster."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        cluster = hpc_engine.create_cluster(
            name=request.name,
            preset=request.preset,
            description=request.description
        )
        return cluster.model_dump()
    except Exception as e:
        logger.error(f"Create cluster error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hpc/clusters/{cluster_id}")
async def get_hpc_cluster(cluster_id: str):
    """Get specific HPC cluster details."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        cluster = hpc_engine.get_cluster(cluster_id)
        if not cluster:
            raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} not found")
        return cluster.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get cluster error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hpc/clusters/{cluster_id}/metrics")
async def get_cluster_metrics(cluster_id: str):
    """Get metrics for a specific cluster."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        metrics = hpc_engine.get_cluster_metrics(cluster_id)
        if not metrics:
            raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} not found")
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cluster metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hpc/presets")
async def get_hpc_presets():
    """Get available HPC cluster presets."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    return hpc_engine.get_available_presets()

# Job Management
class JobSubmitRequest(BaseModel):
    name: str
    job_type: str  # batch_processing, ml_training
    parameters: Dict[str, Any] = {}
    priority: str = "normal"
    cluster_id: Optional[str] = None

@app.post("/api/hpc/jobs")
async def submit_hpc_job(request: JobSubmitRequest):
    """Submit a job to the HPC cluster."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        priority_map = {
            "critical": JobPriority.CRITICAL,
            "high": JobPriority.HIGH,
            "normal": JobPriority.NORMAL,
            "low": JobPriority.LOW,
            "background": JobPriority.BACKGROUND
        }

        job = await hpc_engine.submit_job(
            name=request.name,
            job_type=request.job_type,
            parameters=request.parameters,
            priority=priority_map.get(request.priority, JobPriority.NORMAL),
            cluster_id=request.cluster_id
        )

        return {
            "job_id": job.id,
            "name": job.name,
            "status": job.status.value,
            "tasks_count": len(job.tasks)
        }
    except Exception as e:
        logger.error(f"Submit job error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/hpc/jobs/{job_id}/execute")
async def execute_hpc_job(job_id: str):
    """Execute a submitted HPC job."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        job = await hpc_engine.execute_job(job_id)
        return {
            "job_id": job.id,
            "status": job.status.value,
            "progress_percent": job.progress_percent,
            "output": job.output
        }
    except Exception as e:
        logger.error(f"Execute job error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hpc/jobs")
async def list_hpc_jobs(status: Optional[str] = Query(None)):
    """List HPC jobs."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        status_filter = None
        if status:
            status_map = {
                "queued": JobStatus.QUEUED,
                "running": JobStatus.RUNNING,
                "completed": JobStatus.COMPLETED,
                "failed": JobStatus.FAILED
            }
            status_filter = status_map.get(status)

        jobs = hpc_engine.list_jobs(status_filter)
        return {
            "jobs": [{
                "id": j.id,
                "name": j.name,
                "status": j.status.value,
                "progress_percent": j.progress_percent,
                "submitted_at": j.submitted_at.isoformat(),
                "completed_at": j.completed_at.isoformat() if j.completed_at else None
            } for j in jobs],
            "count": len(jobs)
        }
    except Exception as e:
        logger.error(f"List jobs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hpc/jobs/{job_id}")
async def get_hpc_job(job_id: str):
    """Get HPC job details."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        job = hpc_engine.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        return job.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get job error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# What-If Simulations
class SimulationRequest(BaseModel):
    name: str
    scenario_type: str  # equipment_failure, production_change, maintenance_delay, supply_chain, cost_change
    modifications: Dict[str, Any]
    horizon_hours: int = 24
    iterations: int = 1000

@app.post("/api/hpc/simulations")
async def create_simulation(request: SimulationRequest):
    """Create a what-if simulation scenario."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        # Get current metrics as base
        metrics = generate_simulated_metrics() if config.USE_SIMULATED_DATA else await fetch_real_metrics()

        scenario = hpc_engine.create_simulation(
            name=request.name,
            scenario_type=request.scenario_type,
            current_metrics=metrics,
            modifications=request.modifications,
            horizon_hours=request.horizon_hours,
            iterations=request.iterations
        )

        return {
            "scenario_id": scenario.id,
            "name": scenario.name,
            "type": scenario.type,
            "status": scenario.status.value
        }
    except Exception as e:
        logger.error(f"Create simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/hpc/simulations/{scenario_id}/run")
async def run_simulation(scenario_id: str):
    """Run a simulation scenario."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        # Get current metrics
        metrics = generate_simulated_metrics() if config.USE_SIMULATED_DATA else await fetch_real_metrics()

        result = await hpc_engine.run_simulation(scenario_id, metrics)

        return {
            "scenario_id": result.scenario_id,
            "scenario_name": result.scenario_name,
            "duration_seconds": result.duration_seconds,
            "iterations_completed": result.iterations_completed,
            "predicted_outcomes": result.predicted_outcomes,
            "oee_impact": result.oee_impact,
            "production_impact": result.production_impact,
            "quality_impact": result.quality_impact,
            "cost_impact": result.cost_impact,
            "risk_score": result.risk_score,
            "risk_factors": result.risk_factors,
            "mitigation_suggestions": result.mitigation_suggestions,
            "confidence_level": result.confidence_level,
            "statistics": result.statistics,
            "charts": result.charts
        }
    except Exception as e:
        logger.error(f"Run simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hpc/simulations")
async def list_simulations():
    """List all simulation scenarios."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        scenarios = hpc_engine.list_simulations()
        return {
            "scenarios": [{
                "id": s.id,
                "name": s.name,
                "type": s.type,
                "status": s.status.value,
                "created_at": s.created_at.isoformat()
            } for s in scenarios],
            "count": len(scenarios)
        }
    except Exception as e:
        logger.error(f"List simulations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hpc/simulations/{scenario_id}/result")
async def get_simulation_result(scenario_id: str):
    """Get simulation result."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        result = hpc_engine.get_simulation_result(scenario_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"No result for scenario {scenario_id}")
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get simulation result error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hpc/simulation-templates")
async def get_simulation_templates():
    """Get available simulation templates."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    return hpc_engine.get_simulation_templates()

@app.post("/api/hpc/simulations/compare")
async def compare_simulations(scenario_ids: List[str] = Body(...)):
    """Compare multiple simulation results."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        comparison = hpc_engine.compare_simulations(scenario_ids)
        return comparison
    except Exception as e:
        logger.error(f"Compare simulations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch Processing
class BatchProcessRequest(BaseModel):
    data: List[Dict[str, Any]]
    processor_type: str = "aggregation"  # aggregation, anomaly_detection, trend_analysis, ml_inference
    batch_size: int = 5000

@app.post("/api/hpc/batch/process")
async def process_batch(request: BatchProcessRequest):
    """Process a batch of data through HPC pipeline."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        result = await hpc_engine.process_metrics_batch(
            metrics_data=request.data,
            processor_type=request.processor_type,
            batch_size=request.batch_size
        )
        return result
    except Exception as e:
        logger.error(f"Batch process error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ML Training
class MLTrainRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    model_name: str
    model_type: str  # neural_network, random_forest, xgboost, lstm
    training_data: Dict[str, Any] = {"size": 10000}
    hyperparameters: Dict[str, Any] = {}
    epochs: int = 100

@app.post("/api/hpc/ml/train")
async def train_ml_model(request: MLTrainRequest):
    """Train a predictive model using distributed HPC."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        result = await hpc_engine.train_predictive_model(
            model_name=request.model_name,
            model_type=request.model_type,
            training_data=request.training_data,
            hyperparameters=request.hyperparameters,
            epochs=request.epochs
        )
        return result
    except Exception as e:
        logger.error(f"ML training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Resource Optimization
@app.post("/api/hpc/optimize")
async def optimize_resources(workload_forecast: Dict[str, Any] = Body(...)):
    """Get resource optimization recommendations."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        recommendations = hpc_engine.optimize_resource_allocation(workload_forecast)
        return recommendations
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Demo endpoint
@app.post("/api/hpc/demo/simulation")
async def run_demo_simulation():
    """Run a demo simulation for showcasing capabilities."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        metrics = generate_simulated_metrics() if config.USE_SIMULATED_DATA else await fetch_real_metrics()
        result = await hpc_engine.run_demo_simulation(metrics)
        return {
            "scenario_id": result.scenario_id,
            "scenario_name": result.scenario_name,
            "oee_impact": result.oee_impact,
            "production_impact": result.production_impact,
            "cost_impact": result.cost_impact,
            "risk_score": result.risk_score,
            "risk_factors": result.risk_factors,
            "mitigation_suggestions": result.mitigation_suggestions
        }
    except Exception as e:
        logger.error(f"Demo simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/hpc/demo/activity")
async def simulate_cluster_activity(utilization: float = Query(50, ge=0, le=100)):
    """Simulate cluster activity for demo purposes."""
    if not MODULES_AVAILABLE or not hpc_engine:
        raise HTTPException(status_code=503, detail="HPC module not available")

    try:
        hpc_engine.simulate_activity(utilization)
        return {"status": "simulated", "utilization_percent": utilization}
    except Exception as e:
        logger.error(f"Simulate activity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =========================================
# AI Observability Endpoints
# =========================================

@app.get("/api/ai-observability/dashboard")
async def get_ai_observability_dashboard():
    """Get comprehensive AI observability dashboard data."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        return ai_observability_engine.get_dashboard_data()
    except Exception as e:
        logger.error(f"AI Observability dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/models")
async def list_ai_models():
    """List all registered AI/ML models."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        models = ai_observability_engine.get_all_models()
        return {
            "models": [
                {
                    "model_id": m.model_id,
                    "name": m.name,
                    "version": m.version,
                    "type": m.model_type.value,
                    "status": m.status.value,
                    "risk_level": m.risk_level.value,
                    "deployment_target": m.deployment_target,
                    "description": m.description,
                    "tags": m.tags,
                    "deployed_at": m.deployed_at.isoformat() if m.deployed_at else None,
                }
                for m in models
            ],
            "count": len(models)
        }
    except Exception as e:
        logger.error(f"List AI models error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/models/{model_id}")
async def get_ai_model_detail(model_id: str):
    """Get detailed information for a specific AI model."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        detail = ai_observability_engine.get_model_detail(model_id)
        if not detail:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        return detail
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get AI model detail error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/models/{model_id}/health")
async def get_ai_model_health(model_id: str):
    """Get health score for a specific AI model."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        health = ai_observability_engine.get_health_score(model_id)
        return {
            "model_id": health.model_id,
            "timestamp": health.timestamp.isoformat(),
            "overall_score": health.overall_score,
            "status": health.status,
            "performance_score": health.performance_score,
            "accuracy_score": health.accuracy_score,
            "drift_score": health.drift_score,
            "availability_score": health.availability_score,
            "resource_score": health.resource_score,
            "compliance_score": health.compliance_score,
            "slo_violations": health.slo_violations,
            "slo_compliance_pct": health.slo_compliance_pct,
            "recommendations": health.recommendations,
            "score_trend": health.score_trend,
        }
    except Exception as e:
        logger.error(f"Get AI model health error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/models/{model_id}/metrics")
async def get_ai_model_metrics(model_id: str, window_minutes: int = Query(5)):
    """Get performance metrics for a specific AI model."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        metrics = ai_observability_engine.get_performance_metrics(model_id, window_minutes)
        return {
            "model_id": metrics.model_id,
            "timestamp": metrics.timestamp.isoformat(),
            "latency_p50": metrics.latency_p50,
            "latency_p95": metrics.latency_p95,
            "latency_p99": metrics.latency_p99,
            "latency_avg": metrics.latency_avg,
            "latency_max": metrics.latency_max,
            "requests_total": metrics.requests_total,
            "requests_per_second": metrics.requests_per_second,
            "errors_total": metrics.errors_total,
            "error_rate_pct": metrics.error_rate_pct,
        }
    except Exception as e:
        logger.error(f"Get AI model metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/health-scores")
async def get_all_health_scores():
    """Get health scores for all active AI models."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        scores = ai_observability_engine.get_all_health_scores()
        return {
            "health_scores": {
                model_id: {
                    "overall_score": score.overall_score,
                    "status": score.status,
                    "score_trend": score.score_trend,
                }
                for model_id, score in scores.items()
            },
            "summary": {
                "total_models": len(scores),
                "healthy": len([s for s in scores.values() if s.status == "healthy"]),
                "warning": len([s for s in scores.values() if s.status == "warning"]),
                "critical": len([s for s in scores.values() if s.status == "critical"]),
                "avg_score": round(sum(s.overall_score for s in scores.values()) / len(scores), 1) if scores else 0,
            }
        }
    except Exception as e:
        logger.error(f"Get all health scores error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/drift")
async def get_drift_summary():
    """Get drift detection summary."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        return ai_observability_engine.get_drift_summary()
    except Exception as e:
        logger.error(f"Get drift summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/drift/{model_id}")
async def get_model_drift_history(model_id: str, hours: int = Query(24)):
    """Get drift detection history for a specific model."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        history = ai_observability_engine.get_drift_history(model_id, hours)
        return {
            "model_id": model_id,
            "history": [
                {
                    "timestamp": d.timestamp.isoformat(),
                    "drift_type": d.drift_type.value,
                    "severity": d.severity.value,
                    "drift_score": d.drift_score,
                    "affected_features": d.affected_features,
                    "recommendation": d.recommendation,
                    "requires_retraining": d.requires_retraining,
                }
                for d in history
            ],
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Get model drift history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class DriftDetectionRequest(BaseModel):
    feature_id: str
    current_data: List[float]


@app.post("/api/ai-observability/drift/{model_id}/detect")
async def detect_drift(model_id: str, request: DriftDetectionRequest):
    """Detect drift for a specific feature."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        result = await ai_observability_engine.detect_drift(
            model_id=model_id,
            feature_id=request.feature_id,
            current_data=request.current_data
        )
        return {
            "model_id": result.model_id,
            "timestamp": result.timestamp.isoformat(),
            "drift_type": result.drift_type.value,
            "severity": result.severity.value,
            "drift_score": result.drift_score,
            "statistical_distance": result.statistical_distance,
            "affected_features": result.affected_features,
            "recommendation": result.recommendation,
            "requires_retraining": result.requires_retraining,
            "details": result.details,
        }
    except Exception as e:
        logger.error(f"Detect drift error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/explainability")
async def get_explainability_summary():
    """Get explainability and audit logging summary."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        return ai_observability_engine.explainability.get_explainability_summary()
    except Exception as e:
        logger.error(f"Get explainability summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/audit-logs")
async def get_audit_logs(
    model_id: Optional[str] = Query(None),
    hours: int = Query(24),
    limit: int = Query(100)
):
    """Get prediction audit logs."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        logs = ai_observability_engine.get_audit_logs(model_id, hours, limit)
        return {
            "audit_logs": [
                {
                    "prediction_id": log.prediction_id,
                    "model_id": log.model_id,
                    "timestamp": log.timestamp.isoformat(),
                    "confidence": log.confidence,
                    "latency_ms": log.latency_ms,
                    "top_contributing_features": log.top_contributing_features[:3],
                    "decision_path": log.decision_path,
                    "human_feedback": log.human_feedback,
                }
                for log in logs
            ],
            "count": len(logs)
        }
    except Exception as e:
        logger.error(f"Get audit logs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/explain/{prediction_id}")
async def explain_prediction(prediction_id: str):
    """Get detailed explanation for a prediction."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        explanation = ai_observability_engine.explain_prediction(prediction_id)
        if not explanation:
            raise HTTPException(status_code=404, detail=f"Prediction {prediction_id} not found")
        return explanation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Explain prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class FeedbackRequest(BaseModel):
    feedback: str
    score: Optional[float] = None


@app.post("/api/ai-observability/feedback/{prediction_id}")
async def record_prediction_feedback(prediction_id: str, request: FeedbackRequest):
    """Record human feedback on a prediction."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        success = ai_observability_engine.record_feedback(
            prediction_id=prediction_id,
            feedback=request.feedback,
            score=request.score
        )
        if not success:
            raise HTTPException(status_code=404, detail=f"Prediction {prediction_id} not found")
        return {"status": "recorded", "prediction_id": prediction_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Record feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/alerts")
async def get_ai_alerts(model_id: Optional[str] = Query(None)):
    """Get active AI-related alerts."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        alerts = ai_observability_engine.get_active_alerts(model_id)
        return {
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "model_id": a.model_id,
                    "timestamp": a.timestamp.isoformat(),
                    "severity": a.severity,
                    "category": a.category,
                    "title": a.title,
                    "description": a.description,
                    "metric_name": a.metric_name,
                    "metric_value": a.metric_value,
                    "threshold_value": a.threshold_value,
                    "state": a.state,
                    "acknowledged": a.acknowledged,
                    "suggested_actions": a.suggested_actions,
                }
                for a in alerts
            ],
            "count": len(alerts)
        }
    except Exception as e:
        logger.error(f"Get AI alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai-observability/alerts/{alert_id}/acknowledge")
async def acknowledge_ai_alert(alert_id: str, user: str = Query(...)):
    """Acknowledge an AI alert."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        success = ai_observability_engine.acknowledge_alert(alert_id, user)
        if not success:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        return {"status": "acknowledged", "alert_id": alert_id, "acknowledged_by": user}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Acknowledge alert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/inventory")
async def get_ai_inventory():
    """Get AI model inventory for compliance reporting."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        return ai_observability_engine.get_model_inventory()
    except Exception as e:
        logger.error(f"Get AI inventory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/compliance")
async def get_ai_compliance_report():
    """Get EU AI Act compliance report."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        return ai_observability_engine.get_compliance_report()
    except Exception as e:
        logger.error(f"Get compliance report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-observability/transparency/{model_id}")
async def get_ai_transparency_report(model_id: str):
    """Get AI Act transparency report for a specific model."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        return ai_observability_engine.get_transparency_report(model_id)
    except Exception as e:
        logger.error(f"Get transparency report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ModelRegistrationRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    name: str
    version: str
    model_type: str
    description: str = ""
    risk_level: str = "minimal"
    deployment_target: str = "central"
    tags: List[str] = []


@app.post("/api/ai-observability/models/register")
async def register_ai_model(request: ModelRegistrationRequest):
    """Register a new AI model."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        # Map string to enums
        type_map = {
            "anomaly_detection": ModelType.ANOMALY_DETECTION,
            "predictive_maintenance": ModelType.PREDICTIVE_MAINTENANCE,
            "root_cause_analysis": ModelType.ROOT_CAUSE_ANALYSIS,
            "nlp_query": ModelType.NLP_QUERY,
            "time_series_forecast": ModelType.TIME_SERIES_FORECAST,
            "classification": ModelType.CLASSIFICATION,
            "regression": ModelType.REGRESSION,
            "recommendation": ModelType.RECOMMENDATION,
            "llm_assistant": ModelType.LLM_ASSISTANT,
            "edge_inference": ModelType.EDGE_INFERENCE,
            "custom": ModelType.CUSTOM,
        }
        risk_map = {
            "unacceptable": AIRiskLevel.UNACCEPTABLE,
            "high": AIRiskLevel.HIGH,
            "limited": AIRiskLevel.LIMITED,
            "minimal": AIRiskLevel.MINIMAL,
        }

        model = ai_observability_engine.register_model(
            name=request.name,
            version=request.version,
            model_type=type_map.get(request.model_type, ModelType.CUSTOM),
            description=request.description,
            risk_level=risk_map.get(request.risk_level, AIRiskLevel.MINIMAL),
            deployment_target=request.deployment_target,
            tags=request.tags,
        )

        return {
            "status": "registered",
            "model_id": model.model_id,
            "name": model.name,
            "version": model.version,
        }
    except Exception as e:
        logger.error(f"Register AI model error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class InferenceRecordRequest(BaseModel):
    latency_ms: float
    success: bool = True
    input_data: Optional[Dict[str, Any]] = None
    output: Optional[Any] = None
    confidence: float = 0.0


@app.post("/api/ai-observability/models/{model_id}/inference")
async def record_model_inference(model_id: str, request: InferenceRecordRequest):
    """Record a model inference for observability tracking."""
    if not AI_OBSERVABILITY_AVAILABLE or not ai_observability_engine:
        raise HTTPException(status_code=503, detail="AI Observability module not available")

    try:
        ai_observability_engine.record_inference(
            model_id=model_id,
            latency_ms=request.latency_ms,
            success=request.success,
            input_data=request.input_data,
            output=request.output,
            confidence=request.confidence,
        )
        return {"status": "recorded", "model_id": model_id}
    except Exception as e:
        logger.error(f"Record inference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================================
# Simulator Management API
# =========================================

# In-memory simulator state (in production, use Redis or similar)
simulator_states = {}

class SimulatorConfig(BaseModel):
    rate: Optional[int] = 100
    zones: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    anomalyRate: Optional[float] = 0.0

class SimulatorStatus(BaseModel):
    id: str
    running: bool
    config: SimulatorConfig
    metrics: dict = {}
    startedAt: Optional[str] = None

@app.get("/api/simulators")
async def get_simulators():
    """Get status of all simulators."""
    simulators = [
        {"id": "scada", "name": "SCADA Simulator", "description": "Industrial SCADA data"},
        {"id": "mes", "name": "MES Simulator", "description": "Manufacturing execution data"},
        {"id": "plm", "name": "PLM Simulator", "description": "Product lifecycle data"},
        {"id": "opcua", "name": "OPC-UA Simulator", "description": "OPC-UA node data"},
        {"id": "it_infra", "name": "IT Infrastructure", "description": "IT metrics"},
        {"id": "security", "name": "Security Events", "description": "Security events"}
    ]

    result = []
    for sim in simulators:
        state = simulator_states.get(sim["id"], {"running": False, "config": {}, "metrics": {}})
        result.append({
            **sim,
            "running": state.get("running", False),
            "config": state.get("config", {}),
            "metrics": state.get("metrics", {}),
            "startedAt": state.get("startedAt")
        })

    return {"simulators": result}

@app.post("/api/simulators/{simulator_id}/start")
async def start_simulator(simulator_id: str, config: SimulatorConfig = None):
    """Start a simulator with optional configuration."""
    import datetime

    if config is None:
        config = SimulatorConfig()

    simulator_states[simulator_id] = {
        "running": True,
        "config": config.dict(),
        "metrics": {"totalMessages": 0, "rate": config.rate},
        "startedAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    logger.info(f"Started simulator: {simulator_id} with config: {config}")

    return {
        "status": "started",
        "simulator_id": simulator_id,
        "config": config.dict()
    }

@app.post("/api/simulators/{simulator_id}/stop")
async def stop_simulator(simulator_id: str):
    """Stop a simulator."""
    if simulator_id in simulator_states:
        simulator_states[simulator_id]["running"] = False
        simulator_states[simulator_id]["stoppedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    logger.info(f"Stopped simulator: {simulator_id}")

    return {"status": "stopped", "simulator_id": simulator_id}

@app.get("/api/simulators/{simulator_id}/status")
async def get_simulator_status(simulator_id: str):
    """Get status of a specific simulator."""
    state = simulator_states.get(simulator_id, {"running": False, "config": {}, "metrics": {}})
    return {
        "simulator_id": simulator_id,
        **state
    }

class ScenarioConfig(BaseModel):
    type: Optional[str] = None
    duration: Optional[int] = None
    anomalyRate: Optional[float] = 0.0
    scenario: Optional[dict] = None

@app.post("/api/scenarios/{scenario_id}/activate")
async def activate_scenario(scenario_id: str, config: ScenarioConfig = None):
    """Activate a predefined scenario."""
    logger.info(f"Activating scenario: {scenario_id} with config: {config}")

    return {
        "status": "activated",
        "scenario_id": scenario_id,
        "config": config.dict() if config else {}
    }

@app.post("/api/scenarios/{scenario_id}/deactivate")
async def deactivate_scenario(scenario_id: str):
    """Deactivate a scenario."""
    logger.info(f"Deactivating scenario: {scenario_id}")
    return {"status": "deactivated", "scenario_id": scenario_id}


# =========================================
# Industrial Observability API
# =========================================

@app.get("/api/industrial/equipment")
async def get_industrial_equipment():
    """Get list of industrial equipment with health status."""
    import random

    equipment_types = ["MOTOR", "PUMP", "CONVEYOR", "ROBOT", "FURNACE", "PRESS", "CNC", "COMPRESSOR"]
    zones = ["Production-Line-1", "Production-Line-2", "Assembly", "Utilities", "Packaging", "Welding"]

    equipments = []
    for i in range(12):
        eq_type = equipment_types[i % len(equipment_types)]
        health = 70 + random.random() * 30

        equipments.append({
            "id": f"{eq_type[:3]}-{str(i+1).zfill(3)}",
            "type": eq_type,
            "name": f"{eq_type.title()} {i+1}",
            "zone": zones[i % len(zones)],
            "level": i % 3,
            "health": round(health, 1),
            "status": "optimal" if health > 90 else "normal" if health > 70 else "degraded" if health > 50 else "critical",
            "rul": random.randint(100, 900),
            "alerts": [] if random.random() > 0.15 else [{"type": "warning", "message": "Value near threshold"}]
        })

    return {"equipment": equipments}

@app.get("/api/industrial/zones")
async def get_industrial_zones():
    """Get ISA-95 zone information."""
    zones = [
        {"id": "zone-0", "name": "Zone 0 - Process", "level": 0, "securityLevel": "SL1"},
        {"id": "zone-1", "name": "Zone 1 - Basic Control", "level": 1, "securityLevel": "SL2"},
        {"id": "zone-2", "name": "Zone 2 - Area Control", "level": 2, "securityLevel": "SL3"},
        {"id": "zone-3", "name": "Zone 3 - Site Operations", "level": 3, "securityLevel": "SL3"},
        {"id": "zone-35", "name": "Zone 3.5 - DMZ", "level": 3.5, "securityLevel": "SL3"},
        {"id": "zone-4", "name": "Zone 4 - Business Planning", "level": 4, "securityLevel": "SL2"},
        {"id": "zone-5", "name": "Zone 5 - Enterprise", "level": 5, "securityLevel": "SL2"}
    ]
    return {"zones": zones}


# =========================================
# Correlation API (IT-OT-AI)
# =========================================

@app.get("/api/correlation/patterns")
async def get_correlation_patterns():
    """Get known correlation patterns between IT, OT, and AI domains."""
    patterns = [
        {
            "id": "it_database_ot_mes",
            "name": "Database -> MES",
            "description": "Database latency impacts MES cycle time",
            "source": {"domain": "it", "metric": "response_time", "component": "PostgreSQL"},
            "target": {"domain": "ot", "metric": "cycle_time", "component": "MES-Server"},
            "correlation": 0.87,
            "lag": 30,
            "impact": "high",
            "causality": "confirmed"
        },
        {
            "id": "ot_temp_ai_drift",
            "name": "Temperature -> AI Drift",
            "description": "Temperature variations cause predictive model drift",
            "source": {"domain": "ot", "metric": "temperature", "component": "Main-Motor"},
            "target": {"domain": "ai", "metric": "prediction_drift", "component": "RUL-Model"},
            "correlation": 0.72,
            "lag": 120,
            "impact": "medium",
            "causality": "probable"
        },
        {
            "id": "ai_anomaly_it_alert",
            "name": "AI Anomaly -> IT Alert",
            "description": "Anomaly detection triggers monitoring alerts",
            "source": {"domain": "ai", "metric": "anomaly_score", "component": "AnomalyDetector"},
            "target": {"domain": "it", "metric": "alert_count", "component": "Prometheus"},
            "correlation": 0.95,
            "lag": 5,
            "impact": "high",
            "causality": "confirmed"
        }
    ]
    return {"patterns": patterns}

@app.get("/api/correlation/events")
async def get_correlated_events():
    """Get recent correlated events across domains."""
    import random
    from datetime import datetime, timedelta

    now = datetime.now(datetime.timezone.utc)
    events = []

    event_types = [
        {"type": "spike", "domain": "it", "metric": "cpu_usage", "severity": "warning"},
        {"type": "degradation", "domain": "ot", "metric": "refresh_rate", "severity": "warning"},
        {"type": "alert", "domain": "ot", "metric": "cycle_time", "severity": "high"},
        {"type": "anomaly_detected", "domain": "ai", "metric": "anomaly_score", "severity": "info"},
        {"type": "threshold", "domain": "ot", "metric": "temperature", "severity": "warning"},
        {"type": "drift_detected", "domain": "ai", "metric": "prediction_drift", "severity": "low"}
    ]

    for i, evt in enumerate(event_types):
        events.append({
            "id": f"evt-{i}",
            "timestamp": (now - timedelta(minutes=i*3)).isoformat(),
            "correlatedWith": [f"evt-{j}" for j in range(i) if random.random() > 0.5],
            **evt
        })

    return {"events": events}


# =========================================
# Cybersecurity OT API
# =========================================

@app.get("/api/security/ot/overview")
async def get_ot_security_overview():
    """Get OT security overview."""
    import random

    return {
        "securityScore": 76,
        "complianceScore": 82,
        "totalThreats": 19,
        "criticalVulnerabilities": 1,
        "openVulnerabilities": 4,
        "zonesProtected": 7,
        "lastScan": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

@app.get("/api/security/ot/events")
async def get_security_events():
    """Get recent security events."""
    import random
    from datetime import datetime, timedelta

    now = datetime.now(datetime.timezone.utc)
    event_types = ["auth_failure", "port_scan", "modbus_anomaly", "firmware_change", "new_device"]
    severities = ["critical", "high", "warning", "medium", "low"]
    zones = ["Zone 5", "Zone 4", "Zone 3.5", "Zone 3", "Zone 2"]

    events = []
    for i in range(10):
        events.append({
            "id": f"sec-evt-{i}",
            "type": random.choice(event_types),
            "severity": random.choice(severities),
            "zone": random.choice(zones),
            "source": f"192.168.{random.randint(1,10)}.{random.randint(1,255)}",
            "timestamp": (now - timedelta(minutes=i*5)).isoformat(),
            "details": f"Security event detected"
        })

    return {"events": events}

@app.get("/api/security/ot/vulnerabilities")
async def get_ot_vulnerabilities():
    """Get OT vulnerabilities."""
    vulnerabilities = [
        {"id": "CVE-2024-1234", "severity": "critical", "cvss": 9.8, "asset": "PLC Siemens S7-1500", "zone": "Zone 2", "status": "open", "age": 5},
        {"id": "CVE-2024-5678", "severity": "high", "cvss": 8.2, "asset": "SCADA Server", "zone": "Zone 3", "status": "mitigated", "age": 12},
        {"id": "CVE-2023-9012", "severity": "high", "cvss": 7.5, "asset": "Historian DB", "zone": "Zone 4", "status": "open", "age": 45},
        {"id": "CVE-2024-3456", "severity": "medium", "cvss": 5.3, "asset": "HMI Panel", "zone": "Zone 3", "status": "patched", "age": 3}
    ]
    return {"vulnerabilities": vulnerabilities}

@app.get("/api/security/ot/compliance")
async def get_ot_compliance():
    """Get OT compliance status across frameworks."""
    compliance = {
        "frameworks": [
            {"name": "IEC 62443", "score": 78, "status": "partial"},
            {"name": "NIS 2", "score": 85, "status": "compliant"},
            {"name": "ISO 27001", "score": 92, "status": "compliant"},
            {"name": "NIST CSF", "score": 70, "status": "partial"},
            {"name": "CIS Controls", "score": 65, "status": "partial"},
            {"name": "SOC 2", "score": 88, "status": "compliant"}
        ],
        "overallScore": 82,
        "lastAudit": "2024-01-15",
        "nextAudit": "2024-07-15"
    }
    return compliance


# =========================================
# Background Tasks
# =========================================

async def metrics_refresh_loop():
    """Background task to refresh metrics and push to WebSocket clients."""
    while True:
        await asyncio.sleep(config.REFRESH_INTERVAL)
        if websocket_connections:
            try:
                metrics = await get_unified_metrics()
                metrics_json = json.dumps(metrics.dict(), default=json_serial)
                for ws in websocket_connections:
                    try:
                        await ws.send_text(metrics_json)
                    except Exception as e:
                        logger.warning(f"Error sending to WebSocket: {e}")
            except Exception as e:
                logger.error(f"Error in metrics refresh loop: {e}")

# =========================================
# Main Entry Point
# =========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
