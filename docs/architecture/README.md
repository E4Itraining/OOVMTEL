# Architecture OOVMTEL

Documentation technique de l'architecture de la plateforme d'observabilité industrielle.

## Documents

| Document | Description | Taille |
|----------|-------------|--------|
| [Vue d'ensemble](SYSTEM_OVERVIEW.md) | Architecture globale et capacités | ~15K |
| [Modes de déploiement](DEPLOYMENT_MODES.md) | Standard, Direct-OTLP, Sécurisé | ~12K |
| [Pipelines OpenTelemetry](OTEL_PIPELINES.md) | Configuration collectors et processeurs | ~8K |
| [Ports et réseau](NETWORK_PORTS.md) | Tableau des ports et configuration réseau | ~6K |
| [Stockage](STORAGE.md) | Volumes, rétention et persistance | ~5K |
| [Diagrammes](DIAGRAMS.md) | Diagrammes Mermaid d'architecture | ~8K |

## Architecture Simplifiée

```
┌─────────────────────────────────────────────────────────────┐
│                      OOVMTEL PLATFORM                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SOURCES          INGESTION         STORAGE      VISUALIZATION
│  ┌──────┐        ┌─────────┐       ┌──────┐      ┌──────────┐
│  │SCADA │───────►│  Kafka  │──────►│  VM  │─────►│ Grafana  │
│  │ MES  │        │  OTEL   │       │  OO  │      │ Unified  │
│  │ PLM  │        │Collector│       │  OS  │      │  View    │
│  │OPC-UA│        └─────────┘       └──────┘      └──────────┘
│  └──────┘                                                    │
│                                                              │
│  VM = VictoriaMetrics | OO = OpenObserve | OS = OpenSearch   │
└─────────────────────────────────────────────────────────────┘
```

## Capacités Clés

| Capacité | Valeur |
|----------|--------|
| Ingestion métriques | 100k+ points/sec |
| Ingestion logs | 50k+ events/sec |
| Rétention métriques | 90 jours |
| Rétention compliance | 365 jours |
| Latence ingestion (p99) | < 100ms |

## Stack Technologique

| Catégorie | Technologie | Version |
|-----------|-------------|---------|
| Container | Docker | 24.0+ |
| Message Queue | Kafka (KRaft) | 7.5.3 |
| Time Series | VictoriaMetrics | v1.96.0 |
| Logs/Traces | OpenObserve | v0.10.1 |
| Analytics | OpenSearch | 2.11.1 |
| Telemetry | OpenTelemetry | 0.91.0 |
| Visualization | Grafana | 10.2.3 |
| Backend | FastAPI | 0.108.0 |

## Liens Rapides

- [README principal](../../README.md)
- [Documentation complète](../README.md)
- [Modules Game-Changer](../GAME_CHANGER_MODULES.md)
- [Architecture sécurisée IEC 62443](../SECURE_ARCHITECTURE.md)
