"""
Tests for LLM Observability Configuration.

Tests configuration loading from environment variables.
"""

import pytest
import os
from unittest.mock import patch

from modules.llm_observability.config import (
    LLMObservabilityConfig,
    OTLPExporterConfig,
    MetricsConfig,
    TracingConfig,
    LoggingConfig,
    AlertingConfig,
    ExportProtocol,
    LogLevel,
    get_observability_config,
    reload_config,
)


class TestExportProtocol:
    """Tests for ExportProtocol enum."""

    def test_values(self):
        assert ExportProtocol.OTLP_GRPC == "otlp_grpc"
        assert ExportProtocol.OTLP_HTTP == "otlp_http"
        assert ExportProtocol.PROMETHEUS == "prometheus"
        assert ExportProtocol.CONSOLE == "console"


class TestLogLevel:
    """Tests for LogLevel enum."""

    def test_values(self):
        assert LogLevel.DEBUG == "debug"
        assert LogLevel.INFO == "info"
        assert LogLevel.WARNING == "warning"
        assert LogLevel.ERROR == "error"


class TestOTLPExporterConfig:
    """Tests for OTLPExporterConfig dataclass."""

    def test_default_values(self):
        config = OTLPExporterConfig()

        assert config.traces_endpoint == "http://localhost:4318/v1/traces"
        assert config.metrics_endpoint == "http://localhost:4318/v1/metrics"
        assert config.logs_endpoint == "http://localhost:4318/v1/logs"
        assert config.timeout_seconds == 10.0
        assert config.compression == "gzip"
        assert config.max_retries == 3

    def test_from_env(self):
        env_vars = {
            "OTEL_EXPORTER_OTLP_ENDPOINT": "http://custom-collector:4318",
            "OTEL_EXPORTER_OTLP_TIMEOUT": "20",
            "OTEL_EXPORTER_OTLP_COMPRESSION": "none"
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = OTLPExporterConfig.from_env()

            assert "custom-collector" in config.traces_endpoint
            assert config.timeout_seconds == 20.0
            assert config.compression == "none"


class TestMetricsConfig:
    """Tests for MetricsConfig dataclass."""

    def test_default_values(self):
        config = MetricsConfig()

        assert config.enabled is True
        assert config.export_interval_seconds == 60.0
        assert len(config.latency_buckets) > 0
        assert "mistral" in config.cost_per_million_prompt_tokens

    def test_from_env_disabled(self):
        with patch.dict(os.environ, {"LLM_METRICS_ENABLED": "false"}, clear=False):
            config = MetricsConfig.from_env()
            assert config.enabled is False

    def test_from_env_custom_interval(self):
        with patch.dict(os.environ, {"LLM_METRICS_EXPORT_INTERVAL": "30"}, clear=False):
            config = MetricsConfig.from_env()
            assert config.export_interval_seconds == 30.0


class TestTracingConfig:
    """Tests for TracingConfig dataclass."""

    def test_default_values(self):
        config = TracingConfig()

        assert config.enabled is True
        assert config.sample_rate == 1.0
        assert config.include_prompt is False  # Privacy default
        assert config.include_response is False  # Privacy default
        assert config.max_prompt_length == 1000

    def test_from_env(self):
        env_vars = {
            "LLM_TRACING_ENABLED": "true",
            "LLM_TRACING_SAMPLE_RATE": "0.5",
            "LLM_TRACING_INCLUDE_PROMPT": "true"
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = TracingConfig.from_env()

            assert config.enabled is True
            assert config.sample_rate == 0.5
            assert config.include_prompt is True


class TestLoggingConfig:
    """Tests for LoggingConfig dataclass."""

    def test_default_values(self):
        config = LoggingConfig()

        assert config.enabled is True
        assert config.level == LogLevel.INFO
        assert config.include_trace_id is True
        assert config.include_user_id is False  # Privacy default

    def test_from_env(self):
        env_vars = {
            "LLM_LOGGING_ENABLED": "true",
            "LLM_LOG_LEVEL": "debug"
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = LoggingConfig.from_env()

            assert config.enabled is True
            assert config.level == LogLevel.DEBUG


class TestAlertingConfig:
    """Tests for AlertingConfig dataclass."""

    def test_default_values(self):
        config = AlertingConfig()

        assert config.latency_warning_ms == 5000
        assert config.latency_critical_ms == 15000
        assert config.error_rate_warning_pct == 5.0
        assert config.error_rate_critical_pct == 10.0
        assert config.daily_token_limit == 1000000
        assert config.hourly_token_limit == 100000
        assert config.daily_cost_limit_usd == 100.0
        assert config.hourly_cost_limit_usd == 20.0

    def test_from_env(self):
        env_vars = {
            "LLM_ALERT_LATENCY_WARNING_MS": "3000",
            "LLM_ALERT_LATENCY_CRITICAL_MS": "10000",
            "LLM_ALERT_HOURLY_TOKEN_LIMIT": "50000"
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = AlertingConfig.from_env()

            assert config.latency_warning_ms == 3000
            assert config.latency_critical_ms == 10000
            assert config.hourly_token_limit == 50000


class TestLLMObservabilityConfig:
    """Tests for main LLMObservabilityConfig dataclass."""

    def test_default_values(self):
        config = LLMObservabilityConfig()

        assert config.service_name == "synapsix-llm"
        assert config.service_version == "1.0.0"
        assert config.environment == "production"
        assert isinstance(config.otlp, OTLPExporterConfig)
        assert isinstance(config.metrics, MetricsConfig)
        assert isinstance(config.tracing, TracingConfig)
        assert isinstance(config.logging, LoggingConfig)
        assert isinstance(config.alerting, AlertingConfig)

    def test_from_env(self):
        env_vars = {
            "OTEL_SERVICE_NAME": "custom-service",
            "SERVICE_VERSION": "2.0.0",
            "DEPLOYMENT_ENVIRONMENT": "staging"
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = LLMObservabilityConfig.from_env()

            assert config.service_name == "custom-service"
            assert config.service_version == "2.0.0"
            assert config.environment == "staging"

    def test_to_dict(self):
        config = LLMObservabilityConfig()
        result = config.to_dict()

        assert "service_name" in result
        assert "service_version" in result
        assert "environment" in result
        assert "metrics_enabled" in result
        assert "tracing_enabled" in result
        assert "alerting" in result


class TestConfigSingleton:
    """Tests for configuration singleton pattern."""

    def test_get_observability_config_singleton(self):
        # Reset first
        from modules.llm_observability import config as config_module
        config_module._config = None

        config1 = get_observability_config()
        config2 = get_observability_config()

        assert config1 is config2

    def test_reload_config(self):
        from modules.llm_observability import config as config_module
        config_module._config = None

        config1 = get_observability_config()

        with patch.dict(os.environ, {"OTEL_SERVICE_NAME": "reloaded-service"}, clear=False):
            config2 = reload_config()

            assert config2.service_name == "reloaded-service"
            # New instance after reload
            config3 = get_observability_config()
            assert config3 is config2
