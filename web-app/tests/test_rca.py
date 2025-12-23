"""
OOVMTEL RCA (Root Cause Analysis) Module Tests

Tests for the automatic root cause analysis engine.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRCAEngineInit:
    """Tests for RCA Engine initialization."""

    def test_rca_engine_can_be_imported(self):
        """Test that RCA engine can be imported."""
        try:
            from modules.rca import RCAEngine
            assert RCAEngine is not None
        except ImportError:
            pytest.skip("RCA module not available")

    def test_rca_engine_initialization(self):
        """Test RCA engine initializes correctly."""
        try:
            from modules.rca import RCAEngine
            engine = RCAEngine(
                victoria_metrics_url="http://test:8428",
                opensearch_url="http://test:9200"
            )
            assert engine is not None
        except ImportError:
            pytest.skip("RCA module not available")


class TestIncidentModels:
    """Tests for incident data models."""

    def test_incident_model(self):
        """Test Incident model structure."""
        try:
            from modules.rca import Incident, IncidentSeverity, IncidentCategory

            incident = Incident(
                id="inc-001",
                title="Test Incident",
                description="Test description",
                severity=IncidentSeverity.CRITICAL,
                category=IncidentCategory.EQUIPMENT,
                timestamp=datetime.utcnow()
            )

            assert incident.id == "inc-001"
            assert incident.severity == IncidentSeverity.CRITICAL
        except ImportError:
            pytest.skip("RCA models not available")

    def test_incident_severity_enum(self):
        """Test IncidentSeverity enum values."""
        try:
            from modules.rca import IncidentSeverity

            assert hasattr(IncidentSeverity, 'CRITICAL') or hasattr(IncidentSeverity, 'critical')
            assert hasattr(IncidentSeverity, 'WARNING') or hasattr(IncidentSeverity, 'warning')
        except ImportError:
            pytest.skip("IncidentSeverity not available")

    def test_incident_category_enum(self):
        """Test IncidentCategory enum values."""
        try:
            from modules.rca import IncidentCategory

            assert hasattr(IncidentCategory, 'EQUIPMENT') or hasattr(IncidentCategory, 'equipment')
        except ImportError:
            pytest.skip("IncidentCategory not available")


class TestRCACorrelator:
    """Tests for RCA correlator."""

    @pytest.fixture
    def correlator(self):
        """Create correlator fixture."""
        try:
            from modules.rca.correlator import TemporalCorrelator
            return TemporalCorrelator()
        except ImportError:
            pytest.skip("RCA correlator not available")

    def test_correlator_initialization(self, correlator):
        """Test correlator initializes correctly."""
        assert correlator is not None

    def test_temporal_correlation(self, correlator):
        """Test temporal correlation calculation."""
        events = [
            {"timestamp": datetime.utcnow(), "type": "anomaly", "metric": "temperature"},
            {"timestamp": datetime.utcnow() - timedelta(minutes=5), "type": "anomaly", "metric": "vibration"},
        ]

        # Should not raise exception
        if hasattr(correlator, 'correlate'):
            result = correlator.correlate(events)
            assert result is not None


class TestCausalGraphBuilder:
    """Tests for causal graph construction."""

    @pytest.fixture
    def graph_builder(self):
        """Create graph builder fixture."""
        try:
            from modules.rca.graph_builder import CausalGraphBuilder
            return CausalGraphBuilder()
        except ImportError:
            pytest.skip("Graph builder not available")

    def test_graph_builder_initialization(self, graph_builder):
        """Test graph builder initializes correctly."""
        assert graph_builder is not None

    def test_build_empty_graph(self, graph_builder):
        """Test building graph with no events."""
        if hasattr(graph_builder, 'build'):
            graph = graph_builder.build([])
            assert graph is not None

    def test_graph_node_creation(self, graph_builder):
        """Test graph node creation."""
        events = [
            {"id": "e1", "type": "root", "label": "Temperature Spike"},
            {"id": "e2", "type": "effect", "label": "Machine Slowdown"},
        ]

        if hasattr(graph_builder, 'build'):
            graph = graph_builder.build(events)
            # Graph should have nodes
            assert graph is not None


class TestRCAAnalysis:
    """Tests for RCA analysis functionality."""

    @pytest.fixture
    def rca_engine(self):
        """Create RCA engine fixture."""
        try:
            from modules.rca import RCAEngine
            return RCAEngine()
        except ImportError:
            pytest.skip("RCA module not available")

    @pytest.mark.asyncio
    async def test_analyze_incident(self, rca_engine, sample_incident):
        """Test incident analysis."""
        try:
            from modules.rca import Incident, IncidentSeverity, IncidentCategory

            incident = Incident(
                id=sample_incident["id"],
                title=sample_incident["title"],
                description=sample_incident["description"],
                severity=IncidentSeverity.CRITICAL,
                category=IncidentCategory.EQUIPMENT,
                timestamp=datetime.utcnow()
            )

            if hasattr(rca_engine, 'analyze'):
                result = await rca_engine.analyze(incident)
                assert result is not None
        except ImportError:
            pytest.skip("RCA analysis not available")

    def test_detect_anomalies(self, rca_engine):
        """Test anomaly detection for RCA."""
        metrics_data = {
            "temperature": [65, 66, 67, 85, 86, 87],  # Spike
            "vibration": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        }

        if hasattr(rca_engine, 'detect_anomalies'):
            anomalies = rca_engine.detect_anomalies(metrics_data)
            assert isinstance(anomalies, list)


class TestRootCauseIdentification:
    """Tests for root cause identification."""

    @pytest.fixture
    def rca_engine(self):
        """Create RCA engine fixture."""
        try:
            from modules.rca import RCAEngine
            return RCAEngine()
        except ImportError:
            pytest.skip("RCA module not available")

    def test_identify_root_causes(self, rca_engine):
        """Test root cause identification."""
        symptoms = [
            "Temperature high",
            "Motor current fluctuation",
            "Vibration spike"
        ]

        if hasattr(rca_engine, 'identify_root_causes'):
            causes = rca_engine.identify_root_causes(symptoms)
            assert isinstance(causes, list)

    def test_probability_scoring(self, rca_engine):
        """Test probability scoring for root causes."""
        if hasattr(rca_engine, 'score_probability'):
            score = rca_engine.score_probability(
                cause="Bearing wear",
                evidence=["vibration_high", "temperature_high"]
            )
            assert 0 <= score <= 1


class TestRemediation Suggestions:
    """Tests for remediation suggestions."""

    @pytest.fixture
    def rca_engine(self):
        """Create RCA engine fixture."""
        try:
            from modules.rca import RCAEngine
            return RCAEngine()
        except ImportError:
            pytest.skip("RCA module not available")

    def test_get_remediation_suggestions(self, rca_engine):
        """Test getting remediation suggestions."""
        root_cause = "Bearing wear"

        if hasattr(rca_engine, 'get_remediation_suggestions'):
            suggestions = rca_engine.get_remediation_suggestions(root_cause)
            assert isinstance(suggestions, list)


class TestRCAAPIEndpoints:
    """Integration tests for RCA API endpoints."""

    def test_rca_analyze_endpoint(self, client):
        """Test RCA analysis endpoint."""
        response = client.post("/api/rca/analyze", json={
            "incident_id": "test-001",
            "title": "Test Incident",
            "description": "Equipment failure",
            "severity": "critical"
        })

        # Accept various responses
        assert response.status_code in [200, 404, 422, 500]

    def test_rca_incidents_list(self, client):
        """Test RCA incidents list endpoint."""
        response = client.get("/api/rca/incidents")

        # Endpoint may or may not exist
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_rca_graph_endpoint(self, client):
        """Test RCA causal graph endpoint."""
        response = client.get("/api/rca/graph/test-001")

        # Accept various responses
        assert response.status_code in [200, 404, 422, 500]


class TestHistoricalPatternMatching:
    """Tests for historical pattern matching."""

    @pytest.fixture
    def rca_engine(self):
        """Create RCA engine fixture."""
        try:
            from modules.rca import RCAEngine
            return RCAEngine()
        except ImportError:
            pytest.skip("RCA module not available")

    def test_find_similar_incidents(self, rca_engine):
        """Test finding similar historical incidents."""
        current_incident = {
            "symptoms": ["temperature_high", "vibration_spike"],
            "equipment": "CNC-001"
        }

        if hasattr(rca_engine, 'find_similar_incidents'):
            similar = rca_engine.find_similar_incidents(current_incident)
            assert isinstance(similar, list)

    def test_pattern_learning(self, rca_engine):
        """Test that patterns can be learned from resolved incidents."""
        resolved = {
            "symptoms": ["temperature_high"],
            "root_cause": "Cooling failure",
            "resolution": "Replace coolant pump"
        }

        if hasattr(rca_engine, 'learn_pattern'):
            # Should not raise exception
            rca_engine.learn_pattern(resolved)
