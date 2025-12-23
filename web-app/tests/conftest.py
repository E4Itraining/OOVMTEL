"""
OOVMTEL Backend Test Configuration and Fixtures

This module provides shared fixtures for all tests.
"""

import os
import sys
import pytest
import asyncio
from datetime import datetime
from typing import AsyncGenerator, Generator, Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient


# =========================================
# Environment Setup
# =========================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ["USE_SIMULATED_DATA"] = "true"
    os.environ["VICTORIA_METRICS_URL"] = "http://test-victoria:8428"
    os.environ["OPENSEARCH_URL"] = "http://test-opensearch:9200"
    os.environ["OPENOBSERVE_URL"] = "http://test-openobserve:5080"
    os.environ["OTEL_COLLECTOR_URL"] = "http://test-otel:8888"
    os.environ["GRAFANA_URL"] = "http://test-grafana:3000"
    os.environ["REFRESH_INTERVAL"] = "1"
    yield


# =========================================
# FastAPI App Fixtures
# =========================================

@pytest.fixture(scope="module")
def app():
    """Create FastAPI application for testing."""
    from app import app as fastapi_app
    return fastapi_app


@pytest.fixture
def client(app) -> Generator:
    """Create synchronous test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client(app) -> AsyncGenerator:
    """Create async test client for testing async endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# =========================================
# Mock Data Fixtures
# =========================================

@pytest.fixture
def sample_business_metrics() -> Dict[str, Any]:
    """Sample business metrics for testing."""
    return {
        "oee": 85.5,
        "quality_rate": 96.2,
        "production_today": 1250,
        "cycle_time": 25.3,
        "defects_today": 12,
        "critical_alarms": 3,
        "availability": 94.0,
        "performance": 91.2,
        "equipment": [
            {"id": "eq1", "name": "CNC-001", "status": "running", "health": 95},
            {"id": "eq2", "name": "ROBOT-001", "status": "idle", "health": 88},
            {"id": "eq3", "name": "PRESS-001", "status": "maintenance", "health": 72},
        ],
        "production_by_product": {
            "ProductA": 450,
            "ProductB": 380,
            "ProductC": 420,
        },
        "alarms": [
            {"id": "a1", "severity": "warning", "message": "Temperature high on CNC-001"},
            {"id": "a2", "severity": "critical", "message": "Vibration alert on PRESS-001"},
        ]
    }


@pytest.fixture
def sample_tech_metrics() -> Dict[str, Any]:
    """Sample technical metrics for testing."""
    return {
        "metrics_rate": 85000,
        "logs_rate": 45000,
        "traces_rate": 12000,
        "latency_p95": 45.0,
        "error_rate": 0.05,
        "cpu_usage": 35.0,
        "memory_usage": 62.0,
        "disk_usage": 45.0,
        "vm_active_series": 250000,
        "vm_storage_size": 5000000000,
        "vm_query_latency": 15.0,
        "os_documents": 125000,
        "os_health": "green",
        "os_nodes": 1
    }


@pytest.fixture
def sample_services_status() -> list:
    """Sample services status for testing."""
    return [
        {"name": "VictoriaMetrics", "status": "up", "port": 8428, "latency_ms": 5.2},
        {"name": "OTEL Collector", "status": "up", "port": 4317, "latency_ms": 3.1},
        {"name": "OpenSearch", "status": "up", "port": 9200, "latency_ms": 12.4},
        {"name": "OpenObserve", "status": "up", "port": 5080, "latency_ms": 8.7},
        {"name": "Grafana", "status": "up", "port": 3000, "latency_ms": 6.3},
    ]


@pytest.fixture
def sample_events() -> list:
    """Sample events for testing."""
    return [
        {
            "time": datetime.utcnow().isoformat(),
            "type": "alert",
            "title": "High Temperature",
            "desc": "Temperature exceeded threshold on CNC-001"
        },
        {
            "time": datetime.utcnow().isoformat(),
            "type": "production",
            "title": "Batch Complete",
            "desc": "Batch #1234 completed successfully"
        },
    ]


@pytest.fixture
def sample_unified_metrics(sample_business_metrics, sample_tech_metrics, sample_services_status, sample_events):
    """Complete unified metrics for testing."""
    return {
        "business": sample_business_metrics,
        "tech": sample_tech_metrics,
        "services": sample_services_status,
        "events": sample_events,
        "timestamp": datetime.utcnow().isoformat()
    }


# =========================================
# NLP Module Fixtures
# =========================================

@pytest.fixture
def nlp_query_samples() -> list:
    """Sample NLP queries for testing."""
    return [
        {
            "query": "Quel est le taux OEE actuel?",
            "language": "fr",
            "expected_intent": "metrics_query"
        },
        {
            "query": "Show me the temperature of CNC-001",
            "language": "en",
            "expected_intent": "metrics_query"
        },
        {
            "query": "Pourquoi la ligne 3 est-elle en panne?",
            "language": "fr",
            "expected_intent": "troubleshooting"
        },
        {
            "query": "What is the production trend for today?",
            "language": "en",
            "expected_intent": "trend_analysis"
        },
        {
            "query": "Compare production between Line 1 and Line 2",
            "language": "en",
            "expected_intent": "comparison"
        },
    ]


# =========================================
# RCA Module Fixtures
# =========================================

@pytest.fixture
def sample_incident() -> Dict[str, Any]:
    """Sample incident for RCA testing."""
    return {
        "id": "inc-001",
        "title": "Production Line Stoppage",
        "description": "Line 3 stopped unexpectedly",
        "severity": "critical",
        "category": "equipment",
        "timestamp": datetime.utcnow().isoformat(),
        "affected_equipment": ["PRESS-001", "CONV-003"],
        "symptoms": [
            "Vibration spike detected",
            "Temperature anomaly",
            "Motor current fluctuation"
        ]
    }


# =========================================
# Predictive Module Fixtures
# =========================================

@pytest.fixture
def sample_equipment_data() -> Dict[str, Any]:
    """Sample equipment data for predictive testing."""
    return {
        "equipment_id": "CNC-001",
        "metrics": {
            "temperature": [65.2, 66.1, 67.3, 68.5, 69.2, 70.1],
            "vibration": [0.12, 0.13, 0.15, 0.14, 0.16, 0.18],
            "current": [45.2, 45.5, 46.1, 45.8, 46.3, 46.7],
            "rpm": [1200, 1205, 1198, 1202, 1195, 1190]
        },
        "timestamps": [
            datetime.utcnow().isoformat() for _ in range(6)
        ]
    }


# =========================================
# Mock HTTP Client Fixtures
# =========================================

@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient for external API calls."""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        mock.return_value.__aexit__.return_value = None
        yield client


@pytest.fixture
def mock_victoria_response():
    """Mock VictoriaMetrics API response."""
    return {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": [
                {
                    "metric": {"__name__": "test_metric"},
                    "value": [1703356800, "85.5"]
                }
            ]
        }
    }


@pytest.fixture
def mock_opensearch_response():
    """Mock OpenSearch API response."""
    return {
        "took": 5,
        "hits": {
            "total": {"value": 100},
            "hits": [
                {
                    "_source": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "message": "Test log message",
                        "level": "INFO"
                    }
                }
            ]
        }
    }


# =========================================
# WebSocket Fixtures
# =========================================

@pytest.fixture
def websocket_mock():
    """Mock WebSocket connection."""
    ws = AsyncMock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    ws.receive_json = AsyncMock()
    ws.close = AsyncMock()
    return ws


# =========================================
# Helper Functions
# =========================================

def create_mock_response(status_code: int = 200, json_data: dict = None):
    """Create a mock HTTP response."""
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data or {}
    return response


@pytest.fixture
def create_mock_response_fixture():
    """Fixture to create mock responses."""
    return create_mock_response
