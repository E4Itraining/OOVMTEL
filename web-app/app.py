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
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    logging.warning(f"Advanced modules not available: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    VICTORIA_METRICS_URL = os.getenv('VICTORIA_METRICS_URL', 'http://victoria-metrics:8428')
    OPENSEARCH_URL = os.getenv('OPENSEARCH_URL', 'http://opensearch:9200')
    KAFKA_URL = os.getenv('KAFKA_URL', 'http://kafka:9092')
    OPENOBSERVE_URL = os.getenv('OPENOBSERVE_URL', 'http://openobserve:5080')
    OTEL_COLLECTOR_URL = os.getenv('OTEL_COLLECTOR_URL', 'http://otel-collector:8888')
    GRAFANA_URL = os.getenv('GRAFANA_URL', 'http://grafana:3000')
    REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', '10'))
    USE_SIMULATED_DATA = os.getenv('USE_SIMULATED_DATA', 'true').lower() == 'true'

config = Config()

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
    kafka_throughput: int
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    vm_active_series: int
    vm_storage_size: int
    vm_query_latency: float
    os_documents: int
    os_health: str
    os_nodes: int
    kafka_topics: int
    kafka_partitions: int
    kafka_lag: int

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

@app.on_event("startup")
async def startup_event():
    global http_client, nlp_engine, rca_engine, predictive_engine, remediation_engine, edge_manager

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
            logger.info("Game-changer modules initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize modules: {e}")

    logger.info("OOVMTEL Unified View API started")
    # Start background task for metrics refresh
    asyncio.create_task(metrics_refresh_loop())

@app.on_event("shutdown")
async def shutdown_event():
    global http_client
    if http_client:
        await http_client.aclose()
    logger.info("OOVMTEL Unified View API stopped")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Serve the main dashboard HTML page."""
    return FileResponse("static/index.html")

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
        "kafka_throughput": 2500000,
        "cpu_usage": 35.0,
        "memory_usage": 62.0,
        "disk_usage": 45.0,
        "vm_active_series": int(results.get("vm_active_series", 250000)),
        "vm_storage_size": int(results.get("vm_storage_size", 5000000000)),
        "vm_query_latency": 15.0,
        "os_documents": 125000,
        "os_health": "green",
        "os_nodes": 1,
        "kafka_topics": 6,
        "kafka_partitions": 72,
        "kafka_lag": 50
    }

async def check_all_services() -> List[Dict[str, Any]]:
    """Check health of all services."""
    services = [
        ("VictoriaMetrics", config.VICTORIA_METRICS_URL + "/health", 8428),
        ("OTEL Collector", config.OTEL_COLLECTOR_URL + "/health", 4317),
        ("Kafka", config.KAFKA_URL, 9092),
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
        "kafka_throughput": random.randint(2000000, 3000000),
        "cpu_usage": random.uniform(25, 50),
        "memory_usage": random.uniform(55, 75),
        "disk_usage": random.uniform(40, 60),
        "vm_active_series": random.randint(200000, 300000),
        "vm_storage_size": random.randint(4000000000, 6000000000),
        "vm_query_latency": random.uniform(10, 25),
        "os_documents": random.randint(100000, 150000),
        "os_health": "green",
        "os_nodes": 1,
        "kafka_topics": 6,
        "kafka_partitions": 72,
        "kafka_lag": random.randint(0, 100)
    }

def generate_simulated_services() -> List[Dict[str, Any]]:
    """Generate simulated service status."""
    return [
        {"name": "VictoriaMetrics", "status": "up", "port": 8428, "latency_ms": random.uniform(1, 5)},
        {"name": "OTEL Collector", "status": "up", "port": 4317, "latency_ms": random.uniform(1, 3)},
        {"name": "Kafka", "status": "up", "port": 9092, "latency_ms": random.uniform(2, 8)},
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
        }
    }

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
                for ws in websocket_connections:
                    try:
                        await ws.send_json(metrics.dict())
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
