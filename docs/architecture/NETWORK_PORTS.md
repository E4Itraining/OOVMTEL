# Ports et Configuration Réseau

## Tableau Complet des Ports

| Port | Service | Protocole | Description | Mode |
|------|---------|-----------|-------------|------|
| **3000** | Grafana | HTTP | Dashboards métriques | Tous |
| **4317** | OTEL Collector | gRPC | OTLP gRPC receiver | Tous |
| **4318** | OTEL Collector | HTTP | OTLP HTTP receiver | Tous |
| **4319** | OTEL Collector OT | gRPC | Zone OT receiver | Secure |
| **4320** | OTEL Collector OT | HTTP | Zone OT receiver | Secure |
| **4327** | OTEL Gateway DMZ | gRPC | DMZ gateway | Direct-OTLP |
| **4328** | OTEL Gateway DMZ | HTTP | DMZ gateway | Direct-OTLP |
| **4337** | OTEL Collector OT | gRPC | OT collector | Direct-OTLP |
| **4338** | OTEL Collector OT | HTTP | OT collector | Direct-OTLP |
| **5080** | OpenObserve | HTTP | Logs & Traces UI/API | Tous |
| **5601** | OpenSearch Dashboards | HTTP | Analytics UI | Tous |
| **8080** | SCADA Simulator | HTTP | Prometheus metrics | Tous |
| **8081** | MES Simulator | HTTP | Prometheus metrics | Tous |
| **8082** | PLM Simulator | HTTP | Prometheus metrics | Tous |
| **8083** | OPC-UA Simulator | HTTP | Prometheus metrics | Tous |
| **8085** | Unified View | HTTP | Business-Tech dashboard | Tous |
| **8090** | Kafka UI | HTTP | Kafka management | Standard/Secure |
| **8428** | VictoriaMetrics | HTTP | Time series API | Tous |
| **8429** | vmagent | HTTP | Prometheus scraper | Standard |
| **8480** | vminsert | HTTP | Cluster write endpoint | Secure |
| **8481** | vmselect | HTTP | Cluster read endpoint | Secure |
| **8888** | OTEL Collector | HTTP | Prometheus metrics | Tous |
| **9092** | Kafka | TCP | Bootstrap internal | Standard/Secure |
| **9093** | Kafka | TCP | Bootstrap external | Standard/Secure |
| **9200** | OpenSearch | HTTP | REST API | Tous |
| **13133** | OTEL Collector | HTTP | Health check | Tous |
| **29092** | Kafka OT | TCP | OT zone broker | Secure |
| **55679** | OTEL Collector | HTTP | zPages debug | Tous |

## Architecture Réseau

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          NETWORK ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  MODE STANDARD (docker-compose.yml)                                      │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  oovmtel_network (bridge)                                          │  │
│  │  All services on single network - Internal DNS resolution          │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  MODE DIRECT-OTLP (docker-compose.direct-otlp.yml)                      │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  ot-network  (172.29.0.0/24) │ Simulateurs + OTEL OT              │  │
│  │  dmz-network (172.30.0.0/24) │ OTEL Gateway DMZ                   │  │
│  │  it-network  (172.31.0.0/16) │ Storage + Visualization            │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  MODE SECURE (IEC 62443)                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  ┌─────────────────┐                                              │  │
│  │  │   OT Network    │  172.29.0.0/24                               │  │
│  │  │   internal=true │  No internet access                          │  │
│  │  │   L2/L3         │  Simulators + Kafka-OT + OTEL-OT             │  │
│  │  └────────┬────────┘                                              │  │
│  │           │ Unidirectional                                        │  │
│  │           ▼                                                       │  │
│  │  ┌─────────────────┐                                              │  │
│  │  │   DMZ Network   │  172.30.0.0/24                               │  │
│  │  │   L3/L3.5       │  MirrorMaker + Data Diode + Protocol Break   │  │
│  │  └────────┬────────┘                                              │  │
│  │           │ Validated                                             │  │
│  │           ▼                                                       │  │
│  │  ┌─────────────────┐                                              │  │
│  │  │   IT Network    │  172.31.0.0/16                               │  │
│  │  │   L4/L5         │  Kafka Cluster + Storage + Visualization     │  │
│  │  └─────────────────┘                                              │  │
│  │                                                                    │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Ports par Catégorie

### Ingestion

| Port | Service | Usage |
|------|---------|-------|
| 4317 | OTEL gRPC | Télémétrie OTLP |
| 4318 | OTEL HTTP | Télémétrie OTLP |
| 9092 | Kafka Internal | Messages internes |
| 9093 | Kafka External | Messages externes |

### Storage

| Port | Service | Usage |
|------|---------|-------|
| 8428 | VictoriaMetrics | API métriques |
| 5080 | OpenObserve | Logs/Traces API |
| 9200 | OpenSearch | Full-text search |

### Visualization

| Port | Service | Usage |
|------|---------|-------|
| 3000 | Grafana | Dashboards |
| 5601 | OS Dashboards | Analytics |
| 8085 | Unified View | Business/Tech |
| 8090 | Kafka UI | Management |

### Simulators

| Port | Service | Usage |
|------|---------|-------|
| 8080 | SCADA | Métriques Prometheus |
| 8081 | MES | Métriques Prometheus |
| 8082 | PLM | Métriques Prometheus |
| 8083 | OPC-UA | Métriques Prometheus |

### Health & Debug

| Port | Service | Usage |
|------|---------|-------|
| 13133 | OTEL Health | Health check |
| 8888 | OTEL Metrics | Self-monitoring |
| 55679 | OTEL zPages | Debug pages |

## Configuration Docker Networks

### Mode Standard

```yaml
networks:
  oovmtel_network:
    driver: bridge
```

### Mode Direct-OTLP

```yaml
networks:
  ot-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.29.0.0/24
  dmz-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.30.0.0/24
  it-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.31.0.0/16
```

### Mode Secure

```yaml
networks:
  ot-network:
    driver: bridge
    internal: true  # No internet access
    ipam:
      config:
        - subnet: 172.29.0.0/24
  dmz-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.30.0.0/24
  it-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.31.0.0/16
```

## Références

- [Vue d'ensemble](SYSTEM_OVERVIEW.md)
- [Modes de déploiement](DEPLOYMENT_MODES.md)
- [Pipelines OpenTelemetry](OTEL_PIPELINES.md)
