"""
OOVMTEL Unified Business-Tech View
Backend API Service v2.0

This service provides a unified API for aggregating business and technical metrics
from various data sources (VictoriaMetrics, OpenSearch, Kafka) and serves the
web application for the unified dashboard.

Game-Changer Modules:
- NLP/Conversational Analytics: Natural language queries for industrial data
- Auto-RCA: Automatic root cause analysis with causal graphs
- Predictive Maintenance: Anomaly detection and RUL prediction
- Auto-Remediation: Runbook-based automatic incident remediation
- Edge Computing: Edge agent management and data aggregation
- HPC: High-performance computing for simulations
- AI Observability: Model monitoring and drift detection

Security & Infrastructure:
- JWT Authentication with OAuth2
- Rate Limiting
- Redis Caching
- Prometheus Metrics
- GraphQL API
- Workflow Automation
- External Data Sources Integration
"""

import os
import asyncio
import logging
import uuid
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import random

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query, Body, Depends, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import httpx
from pydantic import BaseModel

# Rate Limiting
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    logging.warning("Rate limiting not available (slowapi not installed)")

# Import new security modules
try:
    from modules.auth import (
        JWTHandler, Token, TokenData, User, get_current_user,
        get_current_active_user, get_jwt_handler, require_roles
    )
    from modules.auth.config import get_auth_config
    AUTH_MODULE_AVAILABLE = True
except ImportError as e:
    AUTH_MODULE_AVAILABLE = False
    logging.warning(f"Auth module not available: {e}")

# Import caching module
try:
    from modules.cache import CacheManager, get_cache_manager
    CACHE_MODULE_AVAILABLE = True
except ImportError as e:
    CACHE_MODULE_AVAILABLE = False
    logging.warning(f"Cache module not available: {e}")

# Import metrics module
try:
    from modules.metrics import (
        MetricsManager, get_metrics_manager, setup_instrumentator,
        WEBSOCKET_CONNECTIONS, NLP_QUERIES
    )
    METRICS_MODULE_AVAILABLE = True
except ImportError as e:
    METRICS_MODULE_AVAILABLE = False
    logging.warning(f"Metrics module not available: {e}")

# Import workflow module
try:
    from modules.workflow import WorkflowEngine, get_workflow_engine
    WORKFLOW_MODULE_AVAILABLE = True
except ImportError as e:
    WORKFLOW_MODULE_AVAILABLE = False
    logging.warning(f"Workflow module not available: {e}")

# Import external data sources module
try:
    from modules.external import get_external_data_manager
    EXTERNAL_MODULE_AVAILABLE = True
except ImportError as e:
    EXTERNAL_MODULE_AVAILABLE = False
    logging.warning(f"External data module not available: {e}")

# Import GraphQL module
try:
    from modules.graphql import get_graphql_router
    GRAPHQL_MODULE_AVAILABLE = True
except ImportError as e:
    GRAPHQL_MODULE_AVAILABLE = False
    logging.warning(f"GraphQL module not available: {e}")

# Import voice/multimodal NLP
try:
    from modules.nlp.voice import get_voice_processor, AudioFormat
    VOICE_MODULE_AVAILABLE = True
except ImportError as e:
    VOICE_MODULE_AVAILABLE = False
    logging.warning(f"Voice module not available: {e}")

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

# =========================================
# Rate Limiter Setup
# =========================================

limiter = None
if RATE_LIMITING_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)


# =========================================
# Application Lifespan (replaces deprecated @app.on_event)
# =========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    global http_client, nlp_engine, rca_engine, predictive_engine
    global remediation_engine, edge_manager, hpc_engine, llm_nlp
    global ai_observability_engine, cache_manager, workflow_engine
    global external_data_manager, voice_processor

    # ===== STARTUP =====
    logger.info("Starting OOVMTEL Unified View API v2.0...")

    # Initialize HTTP client
    http_client = httpx.AsyncClient(timeout=10.0)

    # Initialize cache
    if CACHE_MODULE_AVAILABLE:
        try:
            cache_manager = await get_cache_manager()
            logger.info("Cache manager initialized")
        except Exception as e:
            logger.warning(f"Cache initialization failed: {e}")

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
            remediation_engine = RemediationEngine(dry_run=True)
            edge_manager = EdgeAgentManager()
            hpc_engine = HPCEngine(
                auto_create_cluster=True,
                default_cluster_preset="medium"
            )
            logger.info("Game-changer modules initialized")
        except Exception as e:
            logger.error(f"Failed to initialize modules: {e}")

    # Initialize LLM-enhanced NLP
    if LLM_MODULE_AVAILABLE:
        try:
            llm_nlp = LLMEnhancedNLP()
            initialized = await llm_nlp.initialize()
            if initialized:
                logger.info("LLM-enhanced NLP initialized")
            else:
                logger.info("LLM not configured - using rule-based NLP fallback")
        except Exception as e:
            logger.warning(f"LLM initialization failed: {e}")

    # Initialize AI Observability Engine
    if AI_OBSERVABILITY_AVAILABLE:
        try:
            ai_observability_engine = AIObservabilityEngine(
                victoria_metrics_url=config.VICTORIA_METRICS_URL
            )
            await ai_observability_engine.initialize()
            logger.info("AI Observability Engine initialized")
        except Exception as e:
            logger.warning(f"AI Observability initialization failed: {e}")

    # Initialize workflow engine
    if WORKFLOW_MODULE_AVAILABLE:
        try:
            workflow_engine = get_workflow_engine()
            logger.info("Workflow engine initialized")
        except Exception as e:
            logger.warning(f"Workflow initialization failed: {e}")

    # Initialize external data sources
    if EXTERNAL_MODULE_AVAILABLE:
        try:
            external_data_manager = await get_external_data_manager()
            logger.info("External data sources initialized")
        except Exception as e:
            logger.warning(f"External data initialization failed: {e}")

    # Initialize voice processor
    if VOICE_MODULE_AVAILABLE:
        try:
            voice_processor = await get_voice_processor()
            logger.info("Voice processor initialized")
        except Exception as e:
            logger.warning(f"Voice processor initialization failed: {e}")

    logger.info("OOVMTEL Unified View API v2.0 started successfully")

    # Start background tasks
    asyncio.create_task(metrics_refresh_loop())

    yield  # Application runs here

    # ===== SHUTDOWN =====
    logger.info("Shutting down OOVMTEL Unified View API...")

    if http_client:
        await http_client.aclose()

    if CACHE_MODULE_AVAILABLE and cache_manager:
        await cache_manager.close()

    if EXTERNAL_MODULE_AVAILABLE and external_data_manager:
        await external_data_manager.close()

    logger.info("OOVMTEL Unified View API stopped")


# =========================================
# Initialize FastAPI app with lifespan
# =========================================

app = FastAPI(
    title="OOVMTEL Unified View API",
    description="Unified Business-Tech View for Industrial Observability Platform",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add rate limiter if available
if RATE_LIMITING_AVAILABLE and limiter:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup Prometheus metrics if available
if METRICS_MODULE_AVAILABLE:
    setup_instrumentator(app)

# Add GraphQL router if available
if GRAPHQL_MODULE_AVAILABLE:
    try:
        graphql_router = get_graphql_router()
        app.include_router(graphql_router)
        logger.info("GraphQL endpoint available at /graphql")
    except Exception as e:
        logger.warning(f"GraphQL setup failed: {e}")

# CORS middleware - configurable origins
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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

# New infrastructure modules
cache_manager: Optional[Any] = None
workflow_engine: Optional[Any] = None
external_data_manager: Optional[Any] = None
voice_processor: Optional[Any] = None

# Note: Startup and shutdown are now handled by the lifespan context manager above

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
# Authentication Endpoints (v1 API)
# =========================================

class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/v1/auth/token", response_model=Token if AUTH_MODULE_AVAILABLE else dict, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login.
    Returns JWT access and refresh tokens.
    """
    if not AUTH_MODULE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Authentication module not available")

    jwt_handler = get_jwt_handler()
    user = jwt_handler.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = jwt_handler.create_access_token(
        data={"sub": user.username, "roles": user.roles}
    )
    refresh_token = jwt_handler.create_refresh_token(
        data={"sub": user.username, "roles": user.roles}
    )

    config = get_auth_config()
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=config.access_token_expire_minutes * 60,
        refresh_token=refresh_token
    )


@app.get("/api/v1/auth/me", tags=["Authentication"])
async def get_current_user_info(
    current_user: User = Depends(get_current_user) if AUTH_MODULE_AVAILABLE else None
):
    """Get current authenticated user information."""
    if not AUTH_MODULE_AVAILABLE:
        return {"username": "anonymous", "roles": ["admin"]}
    return {
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "roles": current_user.roles
    }


@app.post("/api/v1/auth/refresh", tags=["Authentication"])
async def refresh_token(refresh_token: str = Body(..., embed=True)):
    """Refresh an access token using a refresh token."""
    if not AUTH_MODULE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Authentication module not available")

    jwt_handler = get_jwt_handler()
    token_data = jwt_handler.verify_token(refresh_token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user = jwt_handler.get_user(token_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access_token = jwt_handler.create_access_token(
        data={"sub": user.username, "roles": user.roles}
    )

    return {"access_token": new_access_token, "token_type": "bearer"}


# =========================================
# Workflow Automation Endpoints
# =========================================

@app.get("/api/v1/workflows/rules", tags=["Workflow"])
async def list_workflow_rules(enabled_only: bool = False):
    """List all workflow automation rules."""
    if not WORKFLOW_MODULE_AVAILABLE or not workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow module not available")

    rules = workflow_engine.list_rules(enabled_only=enabled_only)
    return {
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "enabled": r.enabled,
                "trigger_count": len(r.triggers),
                "action_count": len(r.actions),
                "last_triggered": r.last_triggered.isoformat() if r.last_triggered else None,
                "execution_count": r.execution_count
            }
            for r in rules
        ],
        "total": len(rules)
    }


@app.get("/api/v1/workflows/rules/{rule_id}", tags=["Workflow"])
async def get_workflow_rule(rule_id: str):
    """Get a specific workflow rule."""
    if not WORKFLOW_MODULE_AVAILABLE or not workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow module not available")

    rule = workflow_engine.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")

    return {
        "id": rule.id,
        "name": rule.name,
        "description": rule.description,
        "enabled": rule.enabled,
        "triggers": [{"type": t.type.value, "condition": t.condition} for t in rule.triggers],
        "actions": [{"type": a.type.value, "config": a.config} for a in rule.actions],
        "created_at": rule.created_at.isoformat(),
        "updated_at": rule.updated_at.isoformat(),
        "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None,
        "execution_count": rule.execution_count
    }


@app.post("/api/v1/workflows/trigger", tags=["Workflow"])
async def trigger_workflow_event(
    event_type: str = Body(...),
    event_data: dict = Body(...)
):
    """Manually trigger a workflow event."""
    if not WORKFLOW_MODULE_AVAILABLE or not workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow module not available")

    try:
        executions = await workflow_engine.trigger_event(event_type, event_data)
        return {
            "triggered": len(executions),
            "executions": [
                {
                    "id": e.id,
                    "rule_id": e.rule_id,
                    "rule_name": e.rule_name,
                    "status": e.status.value,
                    "started_at": e.started_at.isoformat()
                }
                for e in executions
            ]
        }
    except Exception as e:
        logger.error(f"Workflow trigger error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/workflows/executions", tags=["Workflow"])
async def get_workflow_executions(limit: int = 100, rule_id: Optional[str] = None):
    """Get workflow execution history."""
    if not WORKFLOW_MODULE_AVAILABLE or not workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow module not available")

    executions = workflow_engine.get_execution_history(limit=limit, rule_id=rule_id)
    return {
        "executions": [
            {
                "id": e.id,
                "rule_id": e.rule_id,
                "rule_name": e.rule_name,
                "trigger_type": e.trigger_type.value,
                "status": e.status.value,
                "started_at": e.started_at.isoformat(),
                "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                "error": e.error
            }
            for e in executions
        ],
        "count": len(executions)
    }


@app.get("/api/v1/workflows/stats", tags=["Workflow"])
async def get_workflow_statistics():
    """Get workflow statistics."""
    if not WORKFLOW_MODULE_AVAILABLE or not workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow module not available")

    return workflow_engine.get_statistics()


# =========================================
# External Data Sources Endpoints
# =========================================

@app.get("/api/v1/external/sources", tags=["External Data"])
async def list_external_sources():
    """List all external data sources and their status."""
    if not EXTERNAL_MODULE_AVAILABLE or not external_data_manager:
        raise HTTPException(status_code=503, detail="External data module not available")

    return {
        "sources": external_data_manager.get_source_status()
    }


@app.get("/api/v1/external/fetch", tags=["External Data"])
async def fetch_all_external_data():
    """Fetch data from all external sources."""
    if not EXTERNAL_MODULE_AVAILABLE or not external_data_manager:
        raise HTTPException(status_code=503, detail="External data module not available")

    try:
        results = await external_data_manager.fetch_all()
        return {
            "data": {
                name: {
                    "status": result.status.value,
                    "data": result.data,
                    "timestamp": result.timestamp.isoformat(),
                    "latency_ms": result.latency_ms,
                    "error": result.error
                }
                for name, result in results.items()
            }
        }
    except Exception as e:
        logger.error(f"External data fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/external/{source_name}", tags=["External Data"])
async def fetch_external_source(source_name: str):
    """Fetch data from a specific external source."""
    if not EXTERNAL_MODULE_AVAILABLE or not external_data_manager:
        raise HTTPException(status_code=503, detail="External data module not available")

    result = await external_data_manager.fetch_source(source_name)
    if not result:
        raise HTTPException(status_code=404, detail=f"Source {source_name} not found")

    return {
        "source": source_name,
        "status": result.status.value,
        "data": result.data,
        "timestamp": result.timestamp.isoformat(),
        "latency_ms": result.latency_ms,
        "error": result.error
    }


@app.get("/api/v1/external/weather/current", tags=["External Data"])
async def get_weather_data():
    """Get current weather data."""
    if not EXTERNAL_MODULE_AVAILABLE or not external_data_manager:
        raise HTTPException(status_code=503, detail="External data module not available")

    result = await external_data_manager.fetch_source("weather")
    if not result or result.error:
        raise HTTPException(status_code=500, detail="Weather data unavailable")

    return result.data


@app.get("/api/v1/external/energy/current", tags=["External Data"])
async def get_energy_data():
    """Get current energy consumption data."""
    if not EXTERNAL_MODULE_AVAILABLE or not external_data_manager:
        raise HTTPException(status_code=503, detail="External data module not available")

    result = await external_data_manager.fetch_source("energy")
    if not result or result.error:
        raise HTTPException(status_code=500, detail="Energy data unavailable")

    return result.data


# =========================================
# Voice / Multimodal NLP Endpoints
# =========================================

class VoiceTranscriptionRequest(BaseModel):
    audio_base64: str
    audio_format: str = "wav"
    language: Optional[str] = None


@app.post("/api/v1/voice/transcribe", tags=["Voice"])
async def transcribe_voice(request: VoiceTranscriptionRequest):
    """
    Transcribe voice input to text.
    Supports WAV, MP3, OGG, WEBM, M4A formats.
    """
    if not VOICE_MODULE_AVAILABLE or not voice_processor:
        raise HTTPException(status_code=503, detail="Voice module not available")

    try:
        # Parse audio format
        try:
            audio_format = AudioFormat(request.audio_format.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format: {request.audio_format}"
            )

        result = await voice_processor.transcribe_base64(
            audio_base64=request.audio_base64,
            audio_format=audio_format,
            language=request.language
        )

        return {
            "id": result.id,
            "status": result.status.value,
            "text": result.text,
            "confidence": result.confidence,
            "language": result.language,
            "duration_seconds": result.duration_seconds,
            "processing_time_ms": result.processing_time_ms,
            "error": result.error
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/voice/query", tags=["Voice"])
async def voice_nlp_query(request: VoiceTranscriptionRequest):
    """
    Voice-to-query pipeline: transcribe voice and process as NLP query.
    """
    if not VOICE_MODULE_AVAILABLE or not voice_processor:
        raise HTTPException(status_code=503, detail="Voice module not available")

    try:
        # Parse audio format
        try:
            audio_format = AudioFormat(request.audio_format.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format: {request.audio_format}"
            )

        # Transcribe voice
        transcription = await voice_processor.transcribe_base64(
            audio_base64=request.audio_base64,
            audio_format=audio_format,
            language=request.language
        )

        if transcription.status.value != "completed" or not transcription.text:
            return {
                "transcription": {
                    "status": transcription.status.value,
                    "error": transcription.error or "Could not transcribe audio"
                },
                "nlp_response": None
            }

        # Process with NLP
        nlp_result = None
        if LLM_MODULE_AVAILABLE and llm_nlp:
            nlp_result = await llm_nlp.process_query(
                query=transcription.text,
                language=transcription.language[:2] if transcription.language else "en"
            )
        elif MODULES_AVAILABLE and nlp_engine:
            nlp_result = await nlp_engine.process_query(
                query=ConversationalQuery(
                    query=transcription.text,
                    language=transcription.language[:2] if transcription.language else "en"
                )
            )

        return {
            "transcription": {
                "text": transcription.text,
                "confidence": transcription.confidence,
                "language": transcription.language,
                "processing_time_ms": transcription.processing_time_ms
            },
            "nlp_response": nlp_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/voice/languages", tags=["Voice"])
async def get_supported_languages():
    """Get list of supported voice recognition languages."""
    if not VOICE_MODULE_AVAILABLE or not voice_processor:
        raise HTTPException(status_code=503, detail="Voice module not available")

    return {
        "languages": voice_processor.get_supported_languages(),
        "default": voice_processor.config.default_language
    }


@app.get("/api/v1/voice/config", tags=["Voice"])
async def get_voice_config():
    """Get voice processor configuration."""
    if not VOICE_MODULE_AVAILABLE or not voice_processor:
        raise HTTPException(status_code=503, detail="Voice module not available")

    return voice_processor.get_config()


# =========================================
# Cache Management Endpoints
# =========================================

@app.get("/api/v1/cache/stats", tags=["Cache"])
async def get_cache_stats():
    """Get cache statistics."""
    if not CACHE_MODULE_AVAILABLE or not cache_manager:
        return {"status": "disabled", "message": "Cache module not available"}

    return cache_manager.get_stats()


@app.delete("/api/v1/cache/clear", tags=["Cache"])
async def clear_cache(pattern: str = "*"):
    """Clear cache entries matching pattern."""
    if not CACHE_MODULE_AVAILABLE or not cache_manager:
        raise HTTPException(status_code=503, detail="Cache module not available")

    try:
        count = await cache_manager.clear_pattern(pattern)
        return {"cleared": count, "pattern": pattern}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================
# System Status Endpoint (Enhanced)
# =========================================

@app.get("/api/v1/system/status", tags=["System"])
async def get_system_status():
    """Get comprehensive system status including all modules."""
    return {
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "modules": {
            "auth": AUTH_MODULE_AVAILABLE,
            "cache": CACHE_MODULE_AVAILABLE,
            "metrics": METRICS_MODULE_AVAILABLE,
            "workflow": WORKFLOW_MODULE_AVAILABLE,
            "external_data": EXTERNAL_MODULE_AVAILABLE,
            "graphql": GRAPHQL_MODULE_AVAILABLE,
            "voice": VOICE_MODULE_AVAILABLE,
            "nlp": MODULES_AVAILABLE,
            "rca": MODULES_AVAILABLE,
            "predictive": MODULES_AVAILABLE,
            "remediation": MODULES_AVAILABLE,
            "edge": MODULES_AVAILABLE,
            "hpc": MODULES_AVAILABLE,
            "llm": LLM_MODULE_AVAILABLE,
            "ai_observability": AI_OBSERVABILITY_AVAILABLE,
        },
        "endpoints": {
            "rest_api": "/api/v1/",
            "graphql": "/graphql" if GRAPHQL_MODULE_AVAILABLE else None,
            "websocket": "/ws",
            "metrics": "/metrics" if METRICS_MODULE_AVAILABLE else None,
            "docs": "/api/docs",
            "redoc": "/api/redoc"
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
