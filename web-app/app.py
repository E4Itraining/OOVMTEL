"""
OOVMTEL Unified Business-Tech View
Backend API Service

This service provides a unified API for aggregating business and technical metrics
from various data sources (VictoriaMetrics, OpenSearch, Kafka) and serves the
web application for the unified dashboard.
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import random

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel

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

@app.on_event("startup")
async def startup_event():
    global http_client
    http_client = httpx.AsyncClient(timeout=10.0)
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
