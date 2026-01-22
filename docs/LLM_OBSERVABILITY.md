# LLM Observability Module

## Overview

The LLM Observability module provides comprehensive monitoring, tracing, and metrics for Large Language Model operations in SYNAPSIX. It integrates with OpenTelemetry for distributed tracing and exports metrics to VictoriaMetrics via the OTEL Collector.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SYNAPSIX Application                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         LLM Providers                                    ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ ││
│  │  │   Mistral    │  │    Claude    │  │    OpenAI   │  │    Ollama    │ ││
│  │  │   Provider   │  │   Provider   │  │   Provider   │  │   Provider   │ ││
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ ││
│  │         │                 │                 │                 │          ││
│  │         └────────────────┬┴─────────────────┴─────────────────┘          ││
│  │                          │                                                ││
│  │  ┌───────────────────────▼────────────────────────────────────────────┐  ││
│  │  │                    LLM Observability Module                         │  ││
│  │  │  ┌─────────────────────────────────────────────────────────────┐   │  ││
│  │  │  │                    Data Normalizer                           │   │  ││
│  │  │  │  • Heterogeneous data handling (multi-provider)              │   │  ││
│  │  │  │  • Response format normalization                             │   │  ││
│  │  │  │  • Error categorization                                      │   │  ││
│  │  │  │  • Token usage standardization                               │   │  ││
│  │  │  │  • Cost calculation                                          │   │  ││
│  │  │  └─────────────────────────────────────────────────────────────┘   │  ││
│  │  │                          │                                          │  ││
│  │  │  ┌───────────┬──────────┴──────────┬───────────────┐               │  ││
│  │  │  │           │                     │               │               │  ││
│  │  │  ▼           ▼                     ▼               ▼               │  ││
│  │  │ ┌─────────┐ ┌─────────┐ ┌─────────────────┐ ┌─────────────┐       │  ││
│  │  │ │ Metrics │ │ Tracing │ │ Structured Logs │ │   Alerting  │       │  ││
│  │  │ │         │ │         │ │                 │ │             │       │  ││
│  │  │ │ Counter │ │  Spans  │ │ Correlation IDs │ │ Thresholds  │       │  ││
│  │  │ │Histogram│ │ Context │ │   Event Data    │ │   Checks    │       │  ││
│  │  │ │  Gauge  │ │Propagate│ │                 │ │             │       │  ││
│  │  │ └────┬────┘ └────┬────┘ └────────┬────────┘ └──────┬──────┘       │  ││
│  │  │      │           │               │                 │               │  ││
│  │  └──────┴───────────┴───────────────┴─────────────────┴───────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                          │               │               │                   │
└──────────────────────────┴───────────────┴───────────────┴───────────────────┘
                           │               │               │
                           ▼               ▼               ▼
                    ┌──────────────────────────────────────────────┐
                    │            OTEL Collector (4317/4318)        │
                    │                                              │
                    │  Receivers: OTLP (gRPC/HTTP)                 │
                    │  Processors: Batch, Memory Limiter, Filter   │
                    │  Exporters: VictoriaMetrics, OpenObserve     │
                    └──────────────────────────────────────────────┘
                           │               │               │
              ┌────────────┘               │               └────────────┐
              ▼                            ▼                            ▼
    ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
    │  VictoriaMetrics │     │   OpenObserve    │     │    OpenSearch    │
    │   (Metrics)      │     │  (Logs/Traces)   │     │   (Analytics)    │
    │    :8428         │     │     :5080        │     │      :9200       │
    └────────┬─────────┘     └────────┬─────────┘     └────────┬─────────┘
             │                        │                        │
             └────────────────────────┼────────────────────────┘
                                      │
                                      ▼
                           ┌──────────────────┐
                           │     Grafana      │
                           │    Dashboard     │
                           │      :3000       │
                           │                  │
                           │ LLM Observability│
                           │    Dashboard     │
                           └──────────────────┘
```

## Module Components

### 1. Configuration (`config.py`)

Manages all observability settings via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_SERVICE_NAME` | synapsix-llm | Service identification |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | http://localhost:4318 | OTEL Collector endpoint |
| `LLM_METRICS_ENABLED` | true | Enable metrics collection |
| `LLM_TRACING_ENABLED` | true | Enable distributed tracing |
| `LLM_TRACING_SAMPLE_RATE` | 1.0 | Sampling rate (0.0-1.0) |
| `LLM_TRACING_INCLUDE_PROMPT` | false | Log prompts (privacy concern) |
| `LLM_ALERT_LATENCY_WARNING_MS` | 5000 | Latency warning threshold |
| `LLM_ALERT_LATENCY_CRITICAL_MS` | 15000 | Latency critical threshold |
| `LLM_ALERT_HOURLY_TOKEN_LIMIT` | 100000 | Hourly token limit |
| `LLM_ALERT_HOURLY_COST_LIMIT_USD` | 20.0 | Hourly cost limit |

### 2. Data Normalizer (`normalizer.py`)

Handles heterogeneous data from multiple LLM providers:

**Supported Providers:**
- **Mistral AI**: `choices[].message`, `usage.{prompt,completion,total}_tokens`
- **Anthropic Claude**: `content[]`, `usage.{input,output}_tokens`
- **OpenAI**: `choices[].message`, `usage.{prompt,completion,total}_tokens`
- **Ollama**: `message`, `{prompt_eval_count,eval_count}`

**Normalized Event (`NormalizedLLMEvent`):**
```python
@dataclass
class NormalizedLLMEvent:
    event_id: str
    timestamp: datetime
    provider: ProviderDataFormat
    model: str
    operation: str  # chat, completion, embedding

    # Token usage
    token_usage: NormalizedTokenUsage

    # Performance
    latency_ms: float
    time_to_first_token_ms: Optional[float]  # Streaming
    tokens_per_second: Optional[float]

    # Status
    status: CompletionStatus
    error: Optional[NormalizedError]

    # Tracing
    trace_id: Optional[str]
    span_id: Optional[str]
```

**Error Categorization:**
- `AUTHENTICATION`: API key issues
- `RATE_LIMIT`: Rate limiting hit
- `QUOTA_EXCEEDED`: Token/cost quota exceeded
- `TIMEOUT`: Request timeout
- `CONTENT_POLICY`: Safety filter triggered
- `MODEL_UNAVAILABLE`: Model not accessible

### 3. Metrics (`metrics.py`)

OpenTelemetry metrics exported to VictoriaMetrics:

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `llm.request.count` | Counter | provider, model, status | Total requests |
| `llm.request.duration` | Histogram | provider, model | Latency (ms) |
| `llm.token.usage` | Counter | provider, model, token_type | Token consumption |
| `llm.cost.usd` | Counter | provider, model | Estimated costs |
| `llm.error.count` | Counter | provider, error_category | Error counts |
| `llm.request.active` | Gauge | - | Active requests |

**Aggregated Metrics API:**
```json
{
  "window_start": "2024-01-01T00:00:00Z",
  "window_end": "2024-01-01T01:00:00Z",
  "requests": {
    "total": 1000,
    "successful": 985,
    "failed": 15,
    "success_rate_pct": 98.5,
    "requests_per_minute": 16.67
  },
  "tokens": {
    "prompt": 50000,
    "completion": 25000,
    "total": 75000,
    "avg_per_request": 75
  },
  "cost": {
    "total_usd": 0.45,
    "by_provider": {"mistral": 0.45}
  },
  "latency_ms": {
    "avg": 2500,
    "p50": 2000,
    "p95": 5000,
    "p99": 8000
  }
}
```

### 4. Telemetry (`telemetry.py`)

Distributed tracing with OpenTelemetry:

**Span Attributes (GenAI Semantic Conventions):**
```python
{
    "gen_ai.system": "mistral",
    "gen_ai.request.model": "mistral-large-latest",
    "gen_ai.operation.name": "chat",
    "gen_ai.usage.prompt_tokens": 100,
    "gen_ai.usage.completion_tokens": 50,
    "gen_ai.response.finish_reasons": ["stop"],

    # Custom SYNAPSIX attributes
    "synapsix.llm.event_id": "uuid",
    "synapsix.llm.latency_ms": 2500,
    "synapsix.llm.estimated_cost_usd": 0.0006
}
```

**Context Propagation:**
- W3C Trace Context format
- Automatic trace/span ID injection
- Request correlation across services

### 5. Decorators (`decorators.py`)

Easy instrumentation for LLM calls:

```python
from modules.llm_observability import trace_llm_call, LLMCallContext

# Decorator approach
@trace_llm_call(provider="mistral", model="mistral-large")
async def generate_response(messages):
    response = await client.chat(messages)
    return response

# Context manager approach
async with LLMCallContext(provider="mistral", model="mistral-large") as ctx:
    ctx.set_request(request_data)
    response = await client.chat(messages)
    ctx.set_response(response)
```

## API Endpoints

### Status & Configuration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/llm/observability/status` | GET | Module status and config |
| `/api/llm/observability/config` | POST | Update alerting thresholds |

### Metrics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/llm/observability/metrics` | GET | Aggregated metrics (customizable window) |
| `/api/llm/observability/metrics/realtime` | GET | Last 5 minutes metrics |
| `/api/llm/observability/alerts` | GET | Active alerts |
| `/api/llm/observability/dashboard` | GET | Complete dashboard data |

**Query Parameters for `/api/llm/observability/metrics`:**
- `window_minutes`: Time window (1-1440, default: 60)
- `provider`: Filter by provider (mistral, claude, openai, ollama)
- `model`: Filter by model name

## Grafana Dashboard

The LLM Observability dashboard (`llm-observability.json`) provides:

**Overview Row:**
- Avg LLM Latency (stat)
- Requests per Minute (stat)
- Error Rate (stat)
- Active Requests (stat)
- Tokens (Last Hour) (stat)
- Cost (Last Hour) (stat)

**Latency Analysis Row:**
- LLM Latency Percentiles (p50, p95, p99)
- Latency by Provider

**Token Usage & Costs Row:**
- Token Usage (Prompt vs Completion)
- LLM Costs Over Time

**Requests & Errors Row:**
- Request Rate (total and by provider)
- Errors by Category

**Provider Breakdown Row:**
- Requests by Provider (pie chart)
- Cost by Provider (pie chart)
- Tokens by Model (pie chart)

## Alerting

### Built-in Alerts

| Alert | Warning | Critical | Description |
|-------|---------|----------|-------------|
| Latency | 5000ms | 15000ms | P95 latency threshold |
| Error Rate | 5% | 10% | Error percentage |
| Token Usage | - | 100k/hour | Hourly token limit |
| Cost | - | $20/hour | Hourly cost limit |
| Rate Limit | 50 req/min | 55 req/min | Rate limiting warning |

### Alert Response Format

```json
{
  "alerts": [
    {
      "type": "latency_warning",
      "severity": "warning",
      "message": "P95 latency (6000ms) exceeds warning threshold (5000ms)",
      "value": 6000,
      "threshold": 5000
    }
  ],
  "alert_count": 1,
  "has_critical": false,
  "has_warning": true
}
```

## Integration with Existing Providers

### Mistral Provider Integration

The Mistral provider (`mistral_client.py`) is automatically instrumented:

```python
# In MistralProvider.generate():
if OBSERVABILITY_AVAILABLE:
    async with LLMCallContext(
        provider="mistral",
        model=model,
        request_id=request_id,
        session_id=session_id,
    ) as ctx:
        ctx.set_request(request_body)
        response, latency_ms = await self._execute_request(...)
        ctx.set_response(response.raw_response)
```

### Adding Observability to Custom Providers

```python
from modules.llm_observability import (
    get_llm_telemetry,
    get_llm_metrics,
    LLMCallContext
)

class CustomProvider(BaseLLMProvider):
    async def generate(self, messages, **kwargs):
        request_id = kwargs.pop("request_id", str(uuid.uuid4()))

        async with LLMCallContext(
            provider="custom",
            model=self.config.model,
            request_id=request_id,
        ) as ctx:
            ctx.set_request({"messages": messages, **kwargs})
            response = await self._call_api(messages)
            ctx.set_response(response)
            return response
```

## Data Privacy

### Privacy-Preserving Features

1. **Prompt/Response Hashing**: Content is SHA256-hashed (first 16 chars) for tracking without storing actual content
2. **Configurable Logging**: `LLM_TRACING_INCLUDE_PROMPT=false` (default)
3. **Content Truncation**: Max 1000 chars if logging enabled
4. **No PII Storage**: Only operational metrics stored

### Sensitive Data Handling

```python
# In normalizer.py
def _hash_content(self, content: Optional[str]) -> Optional[str]:
    """Generate SHA256 hash of content for privacy-preserving tracking."""
    if not content:
        return None
    return hashlib.sha256(content.encode()).hexdigest()[:16]
```

## Performance Considerations

### Minimal Overhead

- Async metrics emission (non-blocking)
- Batch span processing
- Local aggregation before export
- Configurable sampling rate

### Resource Limits

- Max 10,000 events in memory (rolling window)
- 60s export interval (configurable)
- Memory limiter in OTEL Collector

## Troubleshooting

### Common Issues

1. **Metrics not appearing in Grafana**
   - Check OTEL Collector is running
   - Verify endpoint configuration
   - Check VictoriaMetrics connectivity

2. **High latency in metrics**
   - Increase batch size
   - Check network to OTEL Collector
   - Consider sampling for high-volume

3. **Missing traces**
   - Verify `LLM_TRACING_ENABLED=true`
   - Check sample rate configuration
   - Ensure OTLP exporter is configured

### Debug Mode

```bash
# Enable debug logging
export LLM_LOG_LEVEL=debug
export LLM_TRACING_INCLUDE_PROMPT=true  # Development only!
export LLM_TRACING_INCLUDE_RESPONSE=true  # Development only!
```

## Future Enhancements

- [ ] Claude provider integration
- [ ] OpenAI provider integration
- [ ] Ollama provider integration
- [ ] Token efficiency metrics
- [ ] Cost allocation by user/team
- [ ] Prompt caching analytics
- [ ] Model comparison dashboards
- [ ] SLA compliance reporting
