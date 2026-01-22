# Architecture OOVMTEL

> **Note :** Cette documentation a été réorganisée en documents plus ciblés pour une meilleure lisibilité.

## Documentation Réorganisée

La documentation d'architecture a été divisée en plusieurs fichiers :

| Document | Description |
|----------|-------------|
| [Index Architecture](architecture/README.md) | Vue d'ensemble et liens |
| [Vue d'ensemble système](architecture/SYSTEM_OVERVIEW.md) | Architecture globale et capacités |
| [Modes de déploiement](architecture/DEPLOYMENT_MODES.md) | Standard, Direct-OTLP, Sécurisé |
| [Pipelines OpenTelemetry](architecture/OTEL_PIPELINES.md) | Configuration collectors |
| [Ports et réseau](architecture/NETWORK_PORTS.md) | Tableau des ports |
| [Stockage](architecture/STORAGE.md) | Volumes et persistance |

---

## Résumé

**OOVMTEL** = **O**penObserve + **V**ictoria**M**etrics + Open**TEL**emetry + OpenSearch + Kafka

Plateforme d'observabilité industrielle haute performance pour environnements IT/OT critiques.

### Capacités

| Capacité | Valeur |
|----------|--------|
| Ingestion métriques | 100k+ points/sec |
| Ingestion logs | 50k+ events/sec |
| Rétention métriques | 90 jours |
| Rétention compliance | 365 jours |
| Latence ingestion (p99) | < 100ms |
| Séries temporelles max | 1M actives |

### Architecture Simplifiée

```
SOURCES → KAFKA → OTEL COLLECTOR → STORAGE → VISUALIZATION
                                      │
                      ┌───────────────┼───────────────┐
                      ▼               ▼               ▼
              VictoriaMetrics   OpenObserve     OpenSearch
                 (Metrics)     (Logs/Traces)   (Analytics)
```

### Modes de Déploiement

| Mode | Fichier | RAM | Usage |
|------|---------|-----|-------|
| Standard | `docker-compose.yml` | 15 GB | Dev/Test |
| Direct-OTLP | `docker-compose.direct-otlp.yml` | 5 GB | POC |
| Secure | `docker-compose.*.yml` | 25 GB | Production |

### Services Principaux

| Service | Port | Rôle |
|---------|------|------|
| Grafana | 3000 | Dashboards |
| OTEL Collector | 4317/4318 | Telemetry |
| OpenObserve | 5080 | Logs/Traces |
| Unified View | 8085 | Business-Tech |
| VictoriaMetrics | 8428 | Metrics |
| Kafka | 9092 | Messages |
| OpenSearch | 9200 | Analytics |

---

## Liens

- [Documentation complète](architecture/README.md)
- [README principal](../README.md)
- [Architecture sécurisée](SECURE_ARCHITECTURE.md)
- [Modules Game-Changer](GAME_CHANGER_MODULES.md)
