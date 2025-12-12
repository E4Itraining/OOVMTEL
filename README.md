# OOVMTEL - Industrial Observability Platform

**O**penObserve + **V**ictoria**M**etrics + Open**TEL**emetry

Plateforme d'observabilité haute performance optimisée pour les environnements industriels (SCADA, MES, PLM, OPC-UA) avec support du streaming continu IT/OT à grande échelle.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           OOVMTEL - Industrial Observability Platform                    │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DATA SOURCES (IT/OT)                                  │
├─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┤
│     SCADA       │      MES        │      PLM        │    OPC-UA       │   IT Systems    │
│   Controllers   │  Manufacturing  │   Engineering   │    Gateway      │   Applications  │
│   500 pts/sec   │   100 evt/sec   │   20 evt/sec    │   200 nodes/sec │                 │
└────────┬────────┴────────┬────────┴────────┬────────┴────────┬────────┴────────┬────────┘
         │                 │                 │                 │                 │
         ▼                 ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              KAFKA CLUSTER (Message Buffer)                              │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐           │
│  │scada-metrics │  mes-events  │   plm-data   │ opcua-nodes  │ industrial-  │           │
│  │  12 parts    │   8 parts    │   4 parts    │   8 parts    │  telemetry   │           │
│  │  LZ4 comp    │  LZ4 comp    │              │   LZ4 comp   │  12 parts    │           │
│  └──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘           │
│                     Retention: 24h │ Compression: LZ4 │ Max: 10GB                        │
└─────────────────────────────────────────────┬───────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         OPENTELEMETRY COLLECTOR (Central Pipeline)                       │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │  RECEIVERS              │  PROCESSORS           │  EXPORTERS                    │    │
│  │  ├─ OTLP (gRPC/HTTP)    │  ├─ Batch (10k/5s)    │  ├─ VictoriaMetrics (metrics) │    │
│  │  ├─ Kafka (IT/OT)       │  ├─ Memory Limiter    │  ├─ OpenObserve (logs/traces) │    │
│  │  ├─ Prometheus          │  ├─ Resource Detection│  ├─ OpenSearch (analytics)    │    │
│  │  ├─ Host Metrics        │  ├─ Attributes/Industrial                             │    │
│  │  └─ Filelog             │  └─ Transform         │  └─ Kafka (processed)         │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                   Ports: 4317 (gRPC) │ 4318 (HTTP) │ 8888 (Metrics)                      │
└────────────┬──────────────────────────────┬──────────────────────────────┬──────────────┘
             │                              │                              │
             ▼                              ▼                              ▼
┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────────────┐
│   VICTORIA METRICS     │  │      OPENOBSERVE       │  │         OPENSEARCH             │
│   (Time Series DB)     │  │   (Logs & Traces)      │  │    (Full-Text Analytics)       │
├────────────────────────┤  ├────────────────────────┤  ├────────────────────────────────┤
│ • Retention: 90 days   │  │ • Logs ingestion       │  │ • Log analytics                │
│ • 1M unique series     │  │ • Trace storage        │  │ • Trace correlation            │
│ • Remote Write API     │  │ • OTEL native          │  │ • Full-text search             │
│ • High cardinality     │  │ • Built-in dashboards  │  │ • Index State Management       │
│ • Deduplication        │  │ • Memory cache: 1GB    │  │ • ISM policies                 │
│ Port: 8428             │  │ Port: 5080             │  │ Port: 9200                     │
└────────────┬───────────┘  └────────────┬───────────┘  └──────────────┬─────────────────┘
             │                           │                             │
             └───────────────────────────┼─────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              VISUALIZATION & DASHBOARDS                                  │
├─────────────────────────────┬─────────────────────────────┬─────────────────────────────┤
│         GRAFANA             │    OPENSEARCH DASHBOARDS    │         KAFKA UI            │
│    (Unified Dashboards)     │     (Log Analytics)         │    (Cluster Monitoring)     │
│    Port: 3000               │     Port: 5601              │    Port: 8090               │
└─────────────────────────────┴─────────────────────────────┴─────────────────────────────┘
```

## Composants

| Composant | Rôle | Port | Capacité |
|-----------|------|------|----------|
| **Kafka** | Buffer de messages pour streaming haute volumétrie | 9092, 9093 | 10GB, 24h retention |
| **Victoria Metrics** | Base de données time-series haute performance | 8428 | 1M séries, 90j retention |
| **OpenObserve** | Logs et traces (alternative légère à Elasticsearch) | 5080 | Cache 1GB |
| **OpenSearch** | Analytics full-text et corrélation | 9200 | Cluster scalable |
| **OTEL Collector** | Pipeline de télémétrie central | 4317, 4318 | 10k batch, 2GB memory |
| **Grafana** | Visualisation unifiée | 3000 | Multi-datasource |

## Flux de Données IT/OT

```
                    ┌──────────────────────────────────────────────┐
                    │           Industrial Data Flow               │
                    └──────────────────────────────────────────────┘

    OT (Operational Technology)              IT (Information Technology)
    ═══════════════════════════              ═══════════════════════════

    ┌─────────────┐                          ┌─────────────┐
    │    PLC      │──┐                       │   App       │──┐
    └─────────────┘  │                       │   Server    │  │
    ┌─────────────┐  │   ┌─────────────┐     └─────────────┘  │   ┌─────────────┐
    │   SCADA     │──┼──▶│   Kafka     │◀────────────────────┼──▶│   OTEL      │
    │   RTU       │  │   │   Buffer    │     ┌─────────────┐ │   │  Collector  │
    └─────────────┘  │   └─────────────┘     │   Database  │ │   └─────────────┘
    ┌─────────────┐  │          │            │   Server    │─┘          │
    │   OPC-UA    │──┘          │            └─────────────┘            │
    │   Server    │             │            ┌─────────────┐            │
    └─────────────┘             │            │   Cloud     │            │
                                │            │   Services  │────────────┘
                                ▼            └─────────────┘
                    ┌──────────────────────────────────────────────┐
                    │          Unified Observability Stack          │
                    │  ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
                    │  │ Victoria │ │OpenObserve│ │  OpenSearch  │  │
                    │  │ Metrics  │ │          │ │              │  │
                    │  └──────────┘ └──────────┘ └──────────────┘  │
                    └──────────────────────────────────────────────┘
```

## Démarrage Rapide

### Prérequis

- Docker 24.0+
- Docker Compose v2.20+
- 16GB RAM minimum (32GB recommandé pour production)
- 50GB d'espace disque

### Installation

```bash
# Cloner le repository
git clone <repository-url>
cd OOVMTEL

# Démarrer la plateforme
./scripts/start.sh

# Vérifier le statut
./scripts/status.sh
```

### Arrêt

```bash
# Arrêter tous les services
./scripts/stop.sh

# Nettoyage complet (supprime les données)
./scripts/cleanup.sh
```

## Accès aux Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Unified Business-Tech View** | http://localhost:8085 | - |
| **Grafana** | http://localhost:3000 | admin / admin123 |
| **OpenObserve** | http://localhost:5080 | root@example.com / Complexpass#123 |
| **OpenSearch Dashboards** | http://localhost:5601 | - |
| **Kafka UI** | http://localhost:8090 | - |
| **Victoria Metrics** | http://localhost:8428 | - |
| **OTEL Collector Health** | http://localhost:13133 | - |
| **OTEL zPages** | http://localhost:55679 | - |

## Unified Business-Tech View

The platform includes a comprehensive **Unified Business-Tech View** that provides a single-pane-of-glass experience for both business stakeholders and technical teams.

### Features

**Business View:**
- Overall Equipment Effectiveness (OEE) monitoring
- Production KPIs (quality rate, cycle time, defects)
- Equipment status and health monitoring
- Real-time alarm tracking
- Process parameters visualization (temperature, pressure, power, vibration)

**Tech View:**
- Service health status for all platform components
- Resource utilization (CPU, memory, disk)
- Data pipeline metrics (ingestion rates, latency, error rates)
- Storage metrics (VictoriaMetrics, OpenSearch, Kafka)
- OTEL Collector throughput monitoring

**Unified Insights:**
- Cross-domain correlation between business and tech events
- Real-time event timeline combining both domains
- Automatic metric aggregation and visualization

### Access

The Unified View is available at: **http://localhost:8085**

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Unified Business-Tech View                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │  Business View  │     │   Unified View  │     │    Tech View    │       │
│  │  - OEE/KPIs     │     │  - Cross-domain │     │  - Services     │       │
│  │  - Production   │     │  - Timeline     │     │  - Resources    │       │
│  │  - Equipment    │     │  - Correlation  │     │  - Pipeline     │       │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘       │
│                                   │                                         │
│                          ┌────────┴────────┐                               │
│                          │   FastAPI API   │                               │
│                          │   Port: 8085    │                               │
│                          └────────┬────────┘                               │
│                                   │                                         │
│        ┌──────────────────────────┼──────────────────────────┐             │
│        │                          │                          │             │
│        ▼                          ▼                          ▼             │
│  ┌───────────────┐        ┌───────────────┐        ┌───────────────┐       │
│  │VictoriaMetrics│        │   OpenSearch  │        │     Kafka     │       │
│  │   (metrics)   │        │    (logs)     │        │   (events)    │       │
│  └───────────────┘        └───────────────┘        └───────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Grafana Dashboard

A pre-configured Grafana dashboard is also available at **http://localhost:3000** under:
- **Folder:** Industrial
- **Dashboard:** Unified Business-Tech View

## Injection de Données

### Via OTLP (Recommandé)

```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Configuration
OTEL_ENDPOINT = "localhost:4317"

# Traces
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True))
)

# Metrics
metrics.set_meter_provider(MeterProvider(
    metric_readers=[PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=OTEL_ENDPOINT, insecure=True)
    )]
))
```

### Via Kafka (Haute Volumétrie)

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9093'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    compression_type='lz4'
)

# Envoyer des données SCADA
producer.send('scada-metrics', {
    'timestamp': '2024-01-15T10:30:00Z',
    'tag_id': 'SCADA.ZONE_A.REACTOR_001.TEMP',
    'value': 75.5,
    'unit': '°C',
    'quality': 'good'
})
```

### Via Prometheus Remote Write

```yaml
# prometheus.yml
remote_write:
  - url: http://localhost:8428/api/v1/write
```

### Via API OpenObserve

```bash
# Envoyer des logs
curl -X POST "http://localhost:5080/api/default/industrial/_json" \
  -H "Content-Type: application/json" \
  -u "root@example.com:Complexpass#123" \
  -d '[{
    "timestamp": "2024-01-15T10:30:00Z",
    "level": "INFO",
    "source": "scada",
    "message": "Temperature reading normal",
    "equipment_id": "reactor_001"
  }]'
```

## Simulateurs Industriels

La plateforme inclut des simulateurs réalistes pour les tests :

| Simulateur | Type | Débit | Topics Kafka |
|------------|------|-------|--------------|
| SCADA | Capteurs temps réel | 500 pts/sec | scada-metrics |
| MES | Événements production | 100 evt/sec | mes-events |
| PLM | Données engineering | 20 evt/sec | plm-data |
| OPC-UA | Nœuds OPC-UA | 200 nodes/sec | opcua-nodes |

### Métriques Générées

**SCADA:**
- `scada_temperature_celsius` - Température
- `scada_pressure_bar` - Pression
- `scada_flow_rate_m3h` - Débit
- `scada_level_percent` - Niveau de cuve
- `scada_vibration_mms` - Vibration
- `scada_power_kw` - Consommation électrique
- `scada_alarms_total` - Alarmes

**MES:**
- `mes_production_count_total` - Production
- `mes_cycle_time_seconds` - Temps de cycle
- `mes_oee_percent` - OEE (Overall Equipment Effectiveness)
- `mes_quality_rate_percent` - Taux qualité
- `mes_defects_total` - Défauts

**PLM:**
- `plm_changes_total` - Modifications
- `plm_approval_time_hours` - Temps d'approbation
- `plm_active_revisions` - Révisions actives

## Configuration Avancée

### Scaling Kafka

```yaml
# docker-compose.override.yml
services:
  kafka:
    environment:
      KAFKA_NUM_PARTITIONS: 24
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
```

### Haute Disponibilité Victoria Metrics

```yaml
# Pour cluster Victoria Metrics
services:
  vmselect:
    image: victoriametrics/vmselect
  vminsert:
    image: victoriametrics/vminsert
  vmstorage:
    image: victoriametrics/vmstorage
```

### Optimisation OTEL Collector

```yaml
# config/otel/otel-collector-config.yaml
processors:
  batch:
    send_batch_size: 20000  # Augmenter pour haute volumétrie
    timeout: 2s
  memory_limiter:
    limit_mib: 4096  # Augmenter pour plus de buffer
```

## Monitoring de la Plateforme

### Métriques Internes

- **OTEL Collector:** http://localhost:8888/metrics
- **Victoria Metrics:** http://localhost:8428/metrics
- **Kafka JMX:** Port 7071 (si activé)

### Dashboards Grafana Recommandés

1. **Industrial Overview** - Vue globale IT/OT
2. **SCADA Real-Time** - Monitoring temps réel
3. **MES Production** - KPIs production
4. **OEE Dashboard** - Efficacité équipements
5. **Kafka Throughput** - Débit des topics

## Troubleshooting

### Kafka ne démarre pas

```bash
# Vérifier les logs
docker compose logs kafka

# Augmenter la mémoire si nécessaire
# Dans docker-compose.yml, modifier KAFKA_HEAP_OPTS
```

### OTEL Collector en erreur

```bash
# Vérifier la configuration
docker compose exec otel-collector cat /etc/otel/config.yaml

# Voir les erreurs
docker compose logs otel-collector --tail 100
```

### Victoria Metrics surchargé

```bash
# Vérifier les métriques
curl http://localhost:8428/api/v1/status/tsdb

# Augmenter les limites si nécessaire
```

## Performance Attendue

| Métrique | Valeur |
|----------|--------|
| Ingestion métriques | 100k+ points/sec |
| Ingestion logs | 50k+ events/sec |
| Rétention métriques | 90 jours |
| Rétention logs | 30 jours |
| Latence requête (p99) | < 500ms |
| Latence ingestion (p99) | < 100ms |

## Sécurité (Production)

Pour un déploiement en production, activer :

1. **TLS/SSL** sur tous les endpoints
2. **Authentification** Kafka (SASL)
3. **RBAC** OpenSearch
4. **Network Policies** Kubernetes
5. **Encryption at rest**

## Licence

MIT License

## Support

Pour les questions ou problèmes, ouvrir une issue sur le repository.
