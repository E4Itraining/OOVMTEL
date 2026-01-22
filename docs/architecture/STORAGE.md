# Stockage et Persistance

## Volumes Docker

```
Docker Volumes:
├── victoria_metrics_data/     # Time-series data (90j)
│   └── ~50GB typical
│
├── vmagent_data/              # Scraper queue & buffer
│   └── ~1GB max
│
├── openobserve_data/          # Logs, traces, cache
│   └── ~20GB typical
│
├── opensearch_data/           # Full-text index (365j)
│   └── ~100GB+ typical
│
├── grafana_data/              # Dashboards, plugins
│   └── ~500MB typical
│
├── industrial_logs/           # Raw application logs
│   └── ~10GB typical
│
├── [MODE SECURE - OT]
├── kafka_ot_data/             # OT zone Kafka (4h)
│   └── ~2GB max
│
├── [MODE SECURE - IT]
├── kafka_it_1_data/           # IT Kafka broker 1
├── kafka_it_2_data/           # IT Kafka broker 2
├── kafka_it_3_data/           # IT Kafka broker 3
│   └── ~30GB each
│
├── vmstorage_1_data/          # VM cluster node 1
├── vmstorage_2_data/          # VM cluster node 2
│   └── ~50GB each
│
├── [MODE DIRECT-OTLP]
├── otel_ot_buffer/            # OT file-based queue
├── otel_dmz_buffer/           # DMZ file-based queue
├── otel_it_buffer/            # IT file-based queue
│   └── ~5GB each
```

## Politique de Rétention

| Stockage | Rétention | Taille Typique | Usage |
|----------|-----------|----------------|-------|
| VictoriaMetrics | 90 jours | 50 GB | Métriques opérationnelles |
| OpenObserve | 7 jours | 20 GB | Logs temps réel, traces |
| OpenSearch | 365 jours | 100+ GB | Audit, compliance, analytics |
| Kafka | 24h / 10GB | Variable | Buffer de messages |

## Configuration VictoriaMetrics

```yaml
victoria-metrics:
  image: victoriametrics/victoria-metrics:v1.96.0
  command:
    - "-storageDataPath=/storage"
    - "-retentionPeriod=90d"
    - "-maxLabelsPerTimeseries=30"
    - "-search.maxUniqueTimeseries=1000000"
  volumes:
    - victoria_metrics_data:/storage
```

### Capacités

| Métrique | Valeur |
|----------|--------|
| Séries temporelles max | 1M actives |
| Ingestion | 100k+ points/sec |
| Rétention | 90 jours |
| Compression | ~10x |

## Configuration OpenObserve

```yaml
openobserve:
  image: public.ecr.aws/zinclabs/openobserve:v0.10.1
  environment:
    ZO_DATA_DIR: /data
    ZO_DATA_CACHE_DIR: /data/cache
    ZO_MAX_FILE_SIZE_ON_DISK: 512
  volumes:
    - openobserve_data:/data
```

### Capacités

| Métrique | Valeur |
|----------|--------|
| Ingestion logs | 50k+ events/sec |
| Rétention par défaut | 7 jours |
| Cache | 512 MB |

## Configuration OpenSearch

```yaml
opensearch:
  image: opensearchproject/opensearch:2.11.1
  environment:
    OPENSEARCH_JAVA_OPTS: "-Xms4g -Xmx4g"
  volumes:
    - opensearch_data:/usr/share/opensearch/data
```

### Capacités

| Métrique | Valeur |
|----------|--------|
| Rétention compliance | 365 jours |
| JVM Heap | 4-8 GB |
| Indexation | Full-text search |

## Configuration Kafka

```yaml
kafka:
  image: confluentinc/cp-kafka:7.5.3
  environment:
    KAFKA_LOG_RETENTION_HOURS: 24
    KAFKA_LOG_RETENTION_BYTES: 10737418240  # 10GB
  volumes:
    - kafka_data:/var/lib/kafka/data
```

### Topics et Partitions

| Topic | Partitions | Rétention |
|-------|------------|-----------|
| scada-metrics | 12 | 24h |
| mes-events | 8 | 24h |
| plm-data | 4 | 24h |
| opcua-nodes | 8 | 24h |
| industrial-telemetry | 12 | 24h |

## Métriques Industrielles Stockées

### SCADA (500 pts/sec)

```prometheus
scada_temperature_celsius{equipment_id, zone, source}
scada_pressure_bar{equipment_id, zone}
scada_flow_rate_m3h{equipment_id, fluid}
scada_level_percent{tank_id, product}
scada_vibration_mms{equipment_id, axis}
scada_power_kw{equipment_id, phase}
scada_alarms_total{severity, area}
```

### MES (100 evt/sec)

```prometheus
mes_production_count_total{product_id, line_id}
mes_cycle_time_seconds{line_id, operation}
mes_oee_percent{equipment_id}
mes_quality_rate_percent{product_id, shift}
mes_defects_total{defect_type, product_id}
```

### PLM (20 evt/sec)

```prometheus
plm_changes_total{document_type, status}
plm_approval_time_hours{change_id, workflow}
plm_active_revisions{document_id, version}
```

## Estimation d'Espace Disque

### Mode Standard

| Composant | 30 jours | 90 jours | 1 an |
|-----------|----------|----------|------|
| VictoriaMetrics | 15 GB | 50 GB | - |
| OpenObserve | 20 GB | - | - |
| OpenSearch | - | - | 100 GB |
| Kafka | 5 GB | - | - |
| **Total** | ~40 GB | ~75 GB | ~175 GB |

### Mode Secure (HA)

| Composant | 30 jours | 90 jours | 1 an |
|-----------|----------|----------|------|
| VM Cluster (x2) | 30 GB | 100 GB | - |
| OpenObserve | 20 GB | - | - |
| OpenSearch | - | - | 100 GB |
| Kafka IT (x3) | 30 GB | - | - |
| Kafka OT | 2 GB | - | - |
| **Total** | ~82 GB | ~152 GB | ~252 GB |

## Sauvegarde et Restauration

### VictoriaMetrics

```bash
# Snapshot
curl -X POST http://localhost:8428/snapshot/create

# Backup
vmbackup -storageDataPath=/storage -snapshot.createURL=http://localhost:8428/snapshot/create -dst=s3://bucket/backup
```

### OpenSearch

```bash
# Register repository
curl -X PUT "localhost:9200/_snapshot/backup" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/backup"
  }
}'

# Create snapshot
curl -X PUT "localhost:9200/_snapshot/backup/snapshot_1?wait_for_completion=true"
```

## Références

- [Vue d'ensemble](SYSTEM_OVERVIEW.md)
- [Modes de déploiement](DEPLOYMENT_MODES.md)
- [VictoriaMetrics Docs](https://docs.victoriametrics.com/)
- [OpenSearch Documentation](https://opensearch.org/docs/)
