# Pipelines OpenTelemetry

Configuration des collectors et processeurs OpenTelemetry.

## Architecture du Collector

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    OPENTELEMETRY COLLECTOR PIPELINE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                          RECEIVERS                                 │  │
│  │  ┌─────────┐  ┌─────────────┐  ┌─────────┐  ┌─────────────────┐   │  │
│  │  │  OTLP   │  │ PROMETHEUS  │  │  KAFKA  │  │   HOSTMETRICS   │   │  │
│  │  │gRPC:4317│  │ Scrape 15s  │  │Consumer │  │ CPU, Mem, Disk  │   │  │
│  │  │HTTP:4318│  │ 4 targets   │  │ 5 topics│  │ Interval: 60s   │   │  │
│  │  └────┬────┘  └──────┬──────┘  └────┬────┘  └────────┬────────┘   │  │
│  └───────┼──────────────┼──────────────┼────────────────┼────────────┘  │
│          └──────────────┴──────────────┴────────────────┘               │
│                                    │                                     │
│                                    ▼                                     │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                         PROCESSORS                                 │  │
│  │  ┌───────────────┐  ┌─────────┐  ┌─────────────────────────────┐  │  │
│  │  │MEMORY_LIMITER │  │  BATCH  │  │    RESOURCEDETECTION        │  │  │
│  │  │ Limit: 2GB    │  │ 10k/5s  │  │ env, system, docker         │  │  │
│  │  │ Spike: 512MB  │  │ Max:20k │  └─────────────────────────────┘  │  │
│  │  └───────────────┘  └─────────┘                                    │  │
│  │  ┌─────────────┐  ┌─────────┐  ┌─────────────┐                    │  │
│  │  │ ATTRIBUTES  │  │ FILTER  │  │  TRANSFORM  │                    │  │
│  │  │ +platform   │  │ Drop:   │  │ Normalize   │                    │  │
│  │  │ +environment│  │ go_*    │  │ Map attrs   │                    │  │
│  │  └─────────────┘  └─────────┘  └─────────────┘                    │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│                                    ▼                                     │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                          EXPORTERS                                 │  │
│  │  ┌─────────────────────┐  ┌─────────────────┐  ┌───────────────┐  │  │
│  │  │PROMETHEUSREMOTEWRITE│  │    OTLPHTTP     │  │  OPENSEARCH   │  │  │
│  │  │ → VictoriaMetrics   │  │ → OpenObserve   │  │ → OpenSearch  │  │  │
│  │  │   :8428             │  │   :5080         │  │   :9200       │  │  │
│  │  │   Metrics only      │  │   Logs + Traces │  │   Logs + Audit│  │  │
│  │  └─────────────────────┘  └─────────────────┘  └───────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Extensions: Health :13133 | pprof :1777 | zPages :55679                │
└─────────────────────────────────────────────────────────────────────────┘
```

## Configuration des Pipelines

```yaml
pipelines:
  metrics:
    receivers: [otlp, hostmetrics, prometheus]
    processors: [memory_limiter, resourcedetection, batch]
    exporters: [prometheusremotewrite, debug]

  logs:
    receivers: [otlp, filelog]
    processors: [memory_limiter, batch]
    exporters: [otlphttp, opensearch]

  traces:
    receivers: [otlp]
    processors: [memory_limiter, batch]
    exporters: [otlphttp, opensearch]
```

## Receivers

### OTLP Receiver

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
```

### Prometheus Receiver

```yaml
receivers:
  prometheus:
    config:
      scrape_configs:
        - job_name: 'scada-simulator'
          scrape_interval: 15s
          static_configs:
            - targets: ['scada-simulator:8080']
        - job_name: 'mes-simulator'
          static_configs:
            - targets: ['mes-simulator:8081']
        - job_name: 'plm-simulator'
          static_configs:
            - targets: ['plm-simulator:8082']
        - job_name: 'opcua-simulator'
          static_configs:
            - targets: ['opcua-simulator:8083']
```

### Kafka Receiver

```yaml
receivers:
  kafka:
    protocol_version: 3.5.0
    brokers:
      - kafka:9092
    topic: industrial-telemetry
    group_id: otel-collector
    encoding: otlp_proto
```

### Hostmetrics Receiver

```yaml
receivers:
  hostmetrics:
    collection_interval: 60s
    scrapers:
      cpu:
      memory:
      disk:
      network:
      filesystem:
```

## Processors

### Memory Limiter

```yaml
processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 2048
    spike_limit_mib: 512
```

### Batch Processor

```yaml
processors:
  batch:
    send_batch_size: 10000
    send_batch_max_size: 20000
    timeout: 5s
```

### Resource Detection

```yaml
processors:
  resourcedetection:
    detectors:
      - env
      - system
      - docker
    timeout: 5s
```

### Attributes Processor

```yaml
processors:
  attributes:
    actions:
      - key: platform
        value: oovmtel
        action: insert
      - key: environment
        value: production
        action: insert
```

### Filter Processor

```yaml
processors:
  filter:
    metrics:
      exclude:
        match_type: regexp
        metric_names:
          - go_.*
          - process_.*
```

## Exporters

### Prometheus Remote Write

```yaml
exporters:
  prometheusremotewrite:
    endpoint: http://victoria-metrics:8428/api/v1/write
    tls:
      insecure: true
```

### OTLP HTTP (OpenObserve)

```yaml
exporters:
  otlphttp:
    endpoint: http://openobserve:5080/api/default
    headers:
      Authorization: "Basic cm9vdEBleGFtcGxlLmNvbTpDb21wbGV4cGFzcyMxMjM="
```

### OpenSearch Exporter

```yaml
exporters:
  opensearch:
    http:
      endpoint: http://opensearch:9200
    logs_index: otel-logs
    traces_index: otel-traces
```

## Extensions

```yaml
extensions:
  health_check:
    endpoint: 0.0.0.0:13133
  pprof:
    endpoint: 0.0.0.0:1777
  zpages:
    endpoint: 0.0.0.0:55679
```

## Endpoints de Debug

| Endpoint | Port | Description |
|----------|------|-------------|
| Health check | :13133 | /health |
| pprof | :1777 | Profiling Go |
| zPages servicez | :55679/debug/servicez | Services |
| zPages pipelinez | :55679/debug/pipelinez | Pipelines |
| zPages tracez | :55679/debug/tracez | Traces |

## Fichiers de Configuration

| Mode | Fichier |
|------|---------|
| Standard | `config/otel/otel-collector-config.yaml` |
| IT Zone | `config/otel/otel-collector-it-config.yaml` |
| OT Zone | `config/otel/otel-collector-ot-config.yaml` |
| DMZ Gateway | `config/otel/otel-gateway-dmz-direct.yaml` |

## Références

- [OpenTelemetry Collector Documentation](https://opentelemetry.io/docs/collector/)
- [Vue d'ensemble](SYSTEM_OVERVIEW.md)
- [Ports et réseau](NETWORK_PORTS.md)
