# Modes de Déploiement

OOVMTEL supporte trois modes de déploiement adaptés à différents cas d'usage.

## Vue Comparative

| Critère | Standard (Kafka) | Direct-OTLP | Secure (IEC 62443) |
|---------|------------------|-------------|---------------------|
| **Complexité** | Moyenne | Faible | Élevée |
| **RAM totale** | ~15 GB | ~5 GB | ~25 GB |
| **Replay données** | 24h | Non | 7j+ |
| **Multi-consumer** | Oui | Non | Oui |
| **Séparation IT/OT** | Non | Logique | Physique |
| **Data Diode** | Non | Non | Oui |
| **Conformité** | - | - | IEC 62443 |
| **Cas d'usage** | Dev/Test | POC | Production critique |

## Mode 1: Standard (Kafka)

**Fichier:** `docker-compose.yml`

```mermaid
flowchart TB
    subgraph SIMS["Simulateurs Industriels"]
        S1["SCADA :8080"]
        S2["MES :8081"]
        S3["PLM :8082"]
        S4["OPC-UA :8083"]
    end

    subgraph KAFKA["Kafka Cluster - KRaft Mode"]
        BROKER["Broker :9092/:9093"]
        TOPICS["Topics: scada-metrics, mes-events..."]
    end

    subgraph OTEL["OpenTelemetry Collector"]
        RX["Receivers"] --> PX["Processors"] --> EX["Exporters"]
    end

    subgraph STORE["Storage Backends"]
        VM["VictoriaMetrics :8428"]
        OO["OpenObserve :5080"]
        OS["OpenSearch :9200"]
    end

    SIMS --> |JSON| KAFKA
    SIMS --> |Prometheus| OTEL
    KAFKA --> |Consumer| OTEL
    EX --> STORE
```

### Services (13)

| Service | Port | Rôle |
|---------|------|------|
| kafka | 9092/9093 | Message broker |
| victoria-metrics | 8428 | Time series DB |
| vmagent | 8429 | Prometheus scraper |
| openobserve | 5080 | Logs & traces |
| opensearch | 9200 | Full-text search |
| opensearch-dashboards | 5601 | Analytics UI |
| otel-collector | 4317/4318 | Telemetry pipeline |
| grafana | 3000 | Dashboards |
| unified-view | 8085 | Business-Tech view |
| scada-simulator | 8080 | SCADA data gen |
| mes-simulator | 8081 | MES data gen |
| plm-simulator | 8082 | PLM data gen |
| opcua-simulator | 8083 | OPC-UA data gen |

### Démarrage

```bash
docker compose up -d
# ou
./scripts/start.sh simple
```

---

## Mode 2: Direct-OTLP (Sans Kafka)

**Fichier:** `docker-compose.direct-otlp.yml`

```mermaid
flowchart TB
    subgraph OT["Zone OT - 172.29.0.0/24"]
        SIM["Simulateurs OTLP"]
        OTEL_OT["otel-collector-ot<br/>:4337/4338"]
    end

    subgraph DMZ["Zone DMZ - 172.30.0.0/24"]
        GW["otel-gateway-dmz<br/>:4327/4328<br/>Sanitization"]
    end

    subgraph IT["Zone IT"]
        OTEL_IT["otel-collector-it<br/>:4317/4318"]
        BACKENDS["VictoriaMetrics + OpenObserve + OpenSearch"]
        GRAFANA["Grafana :3000"]
    end

    SIM --> OTEL_OT --> GW --> OTEL_IT --> BACKENDS --> GRAFANA

    style OT fill:#ffcdd2
    style DMZ fill:#ffe0b2
    style IT fill:#c8e6c9
```

### Avantages

- 90% moins de ressources (pas de Kafka)
- OTLP end-to-end
- File-based buffering (persistance)
- Séparation IT/OT/DMZ

### Démarrage

```bash
docker compose -f docker-compose.direct-otlp.yml up -d
# ou
./scripts/start.sh direct-otlp
```

---

## Mode 3: Secure (IEC 62443)

**Fichiers:**
- `docker-compose.ot.yml` - Zone OT
- `docker-compose.dmz.yml` - Zone DMZ
- `docker-compose.it.yml` - Zone IT

```mermaid
flowchart TB
    subgraph OT["Zone OT - IEC 62443 L2/L3"]
        SIM_OT["Simulateurs"]
        KAFKA_OT["kafka-ot :29092"]
    end

    subgraph DMZ["Zone DMZ - IEC 62443 L3/L3.5"]
        MM["MirrorMaker 2<br/>Unidirectionnel"]
        DIODE["Data Diode"]
    end

    subgraph IT["Zone IT - IEC 62443 L4/L5"]
        KAFKA_HA["Kafka Cluster HA x3"]
        VM_HA["VictoriaMetrics Cluster"]
        GRAFANA_IT["Grafana"]
    end

    SIM_OT --> KAFKA_OT --> MM --> DIODE --> KAFKA_HA --> VM_HA --> GRAFANA_IT

    style OT fill:#ffcdd2
    style DMZ fill:#ffe0b2
    style IT fill:#c8e6c9
```

### Conformité IEC 62443

| Zone | Niveau | Réseau | Composants |
|------|--------|--------|------------|
| OT | L2/L3 | 172.29.0.0/24 | Simulateurs, Kafka-OT, OTEL-OT |
| DMZ | L3/L3.5 | 172.30.0.0/24 | MirrorMaker, Data Diode, Protocol Break |
| IT | L4/L5 | 172.31.0.0/16 | Kafka HA, VM Cluster, Grafana |

### Démarrage

```bash
./scripts/start.sh secure
```

---

## Ressources Système

| Mode | RAM Min | RAM Recommandée | CPU | Disque |
|------|---------|-----------------|-----|--------|
| Standard | 16 GB | 32 GB | 4 cores | 100 GB |
| Direct-OTLP | 8 GB | 16 GB | 2 cores | 50 GB |
| Secure | 32 GB | 64 GB | 8 cores | 200 GB |

### Détail par Service

| Service | RAM | CPU |
|---------|-----|-----|
| Kafka | 4-8 GB | 1-2 |
| VictoriaMetrics | 2-4 GB | 0.5-1 |
| OpenObserve | 1-2 GB | 0.5-1 |
| OpenSearch | 4-8 GB | 1-2 |
| OTEL Collector | 2-4 GB | 0.5-1 |
| Grafana | 512 MB | 0.2 |
| Simulators | 256 MB each | 0.1 |

## Références

- [Vue d'ensemble](SYSTEM_OVERVIEW.md)
- [Architecture sécurisée détaillée](../SECURE_ARCHITECTURE.md)
- [Pipelines OpenTelemetry](OTEL_PIPELINES.md)
