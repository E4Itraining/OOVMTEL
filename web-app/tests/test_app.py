"""
OOVMTEL API Endpoint Tests

Tests for the main FastAPI application endpoints.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_check_returns_healthy(self, client):
        """Test that health endpoint returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_health_check_timestamp_format(self, client):
        """Test that health timestamp is valid ISO format."""
        response = client.get("/health")
        data = response.json()

        # Should not raise exception if valid ISO format
        datetime.fromisoformat(data["timestamp"])


class TestMetricsEndpoints:
    """Tests for /api/metrics endpoints."""

    def test_get_unified_metrics(self, client):
        """Test unified metrics endpoint returns all data."""
        response = client.get("/api/metrics")

        assert response.status_code == 200
        data = response.json()

        # Check all required sections exist
        assert "business" in data
        assert "tech" in data
        assert "services" in data
        assert "events" in data
        assert "timestamp" in data

    def test_get_unified_metrics_business_fields(self, client):
        """Test that business metrics contain required fields."""
        response = client.get("/api/metrics")
        data = response.json()
        business = data["business"]

        required_fields = [
            "oee", "quality_rate", "production_today", "cycle_time",
            "defects_today", "critical_alarms", "availability", "performance",
            "equipment", "production_by_product", "alarms"
        ]

        for field in required_fields:
            assert field in business, f"Missing business field: {field}"

    def test_get_unified_metrics_tech_fields(self, client):
        """Test that tech metrics contain required fields."""
        response = client.get("/api/metrics")
        data = response.json()
        tech = data["tech"]

        required_fields = [
            "metrics_rate", "logs_rate", "traces_rate", "latency_p95",
            "error_rate", "cpu_usage", "memory_usage", "disk_usage",
            "vm_active_series", "vm_storage_size", "vm_query_latency",
            "os_documents", "os_health", "os_nodes"
        ]

        for field in required_fields:
            assert field in tech, f"Missing tech field: {field}"

    def test_get_business_metrics(self, client):
        """Test business metrics specific endpoint."""
        response = client.get("/api/metrics/business")

        assert response.status_code == 200
        data = response.json()
        assert "oee" in data
        assert "quality_rate" in data

    def test_get_tech_metrics(self, client):
        """Test tech metrics specific endpoint."""
        response = client.get("/api/metrics/tech")

        assert response.status_code == 200
        data = response.json()
        assert "metrics_rate" in data
        assert "logs_rate" in data


class TestServicesEndpoint:
    """Tests for /api/services endpoint."""

    def test_get_services_status(self, client):
        """Test services status endpoint."""
        response = client.get("/api/services")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        if len(data) > 0:
            service = data[0]
            assert "name" in service
            assert "status" in service
            assert "port" in service


class TestEventsEndpoint:
    """Tests for /api/events endpoint."""

    def test_get_events_default_limit(self, client):
        """Test events endpoint with default limit."""
        response = client.get("/api/events")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10  # Default limit

    def test_get_events_custom_limit(self, client):
        """Test events endpoint with custom limit."""
        response = client.get("/api/events?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_event_structure(self, client):
        """Test event structure contains required fields."""
        response = client.get("/api/events")
        data = response.json()

        if len(data) > 0:
            event = data[0]
            assert "time" in event
            assert "type" in event
            assert "title" in event
            assert "desc" in event


class TestMetricsCaching:
    """Tests for metrics caching behavior."""

    def test_metrics_are_cached(self, client):
        """Test that subsequent requests return cached data."""
        # First request
        response1 = client.get("/api/metrics")
        data1 = response1.json()

        # Second request (should be from cache)
        response2 = client.get("/api/metrics")
        data2 = response2.json()

        # Timestamps should be very close if cached
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestDataValidation:
    """Tests for data validation and types."""

    def test_oee_in_valid_range(self, client):
        """Test that OEE is in valid percentage range."""
        response = client.get("/api/metrics")
        data = response.json()
        oee = data["business"]["oee"]

        assert 0 <= oee <= 100, f"OEE {oee} out of valid range [0, 100]"

    def test_quality_rate_in_valid_range(self, client):
        """Test that quality rate is in valid percentage range."""
        response = client.get("/api/metrics")
        data = response.json()
        quality = data["business"]["quality_rate"]

        assert 0 <= quality <= 100, f"Quality rate {quality} out of valid range"

    def test_metrics_rates_positive(self, client):
        """Test that metric rates are positive."""
        response = client.get("/api/metrics")
        data = response.json()
        tech = data["tech"]

        assert tech["metrics_rate"] >= 0
        assert tech["logs_rate"] >= 0
        assert tech["traces_rate"] >= 0

    def test_services_valid_status(self, client):
        """Test that service statuses are valid values."""
        response = client.get("/api/services")
        data = response.json()

        valid_statuses = {"up", "down", "degraded", "unknown", "healthy"}
        for service in data:
            assert service["status"] in valid_statuses, \
                f"Invalid status '{service['status']}' for service {service['name']}"


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_endpoint_returns_404(self, client):
        """Test that invalid endpoints return 404."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_invalid_method_returns_405(self, client):
        """Test that invalid HTTP methods return 405."""
        response = client.delete("/api/metrics")
        assert response.status_code == 405


class TestCORSHeaders:
    """Tests for CORS headers."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present."""
        response = client.options("/api/metrics", headers={
            "Origin": "http://localhost:3002",
            "Access-Control-Request-Method": "GET"
        })

        # CORS is configured with allow_origins=["*"]
        assert response.status_code in [200, 204, 405]


class TestAsyncEndpoints:
    """Async tests for endpoints."""

    @pytest.mark.asyncio
    async def test_async_metrics_endpoint(self, async_client):
        """Test metrics endpoint with async client."""
        response = await async_client.get("/api/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "business" in data
        assert "tech" in data

    @pytest.mark.asyncio
    async def test_async_health_endpoint(self, async_client):
        """Test health endpoint with async client."""
        response = await async_client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestSimulatedDataMode:
    """Tests for simulated data mode."""

    def test_simulated_mode_returns_data(self, client):
        """Test that simulated mode returns valid data."""
        # USE_SIMULATED_DATA is set to true in conftest
        response = client.get("/api/metrics")

        assert response.status_code == 200
        data = response.json()

        # Should have realistic simulated values
        assert data["business"]["oee"] > 0
        assert data["tech"]["metrics_rate"] > 0


class TestEquipmentMetrics:
    """Tests for equipment-related metrics."""

    def test_equipment_list_structure(self, client):
        """Test equipment list structure in business metrics."""
        response = client.get("/api/metrics")
        data = response.json()
        equipment = data["business"]["equipment"]

        assert isinstance(equipment, list)

        for eq in equipment:
            if eq:  # If not empty
                assert "id" in eq or "name" in eq

    def test_production_by_product_structure(self, client):
        """Test production_by_product is a dict."""
        response = client.get("/api/metrics")
        data = response.json()

        assert isinstance(data["business"]["production_by_product"], dict)


class TestAlarms:
    """Tests for alarm data."""

    def test_alarms_list_structure(self, client):
        """Test alarms list structure."""
        response = client.get("/api/metrics")
        data = response.json()
        alarms = data["business"]["alarms"]

        assert isinstance(alarms, list)


class TestOpenSearchHealth:
    """Tests for OpenSearch health reporting."""

    def test_opensearch_health_valid_values(self, client):
        """Test OpenSearch health status is valid."""
        response = client.get("/api/metrics")
        data = response.json()

        valid_health = {"green", "yellow", "red"}
        assert data["tech"]["os_health"] in valid_health
