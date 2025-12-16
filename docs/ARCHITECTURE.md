# OOVMTEL - Architecture Technique Complète

## Vue d'Ensemble

OOVMTEL (**O**penObserve + **V**ictoria**M**etrics + Open**TEL**emetry + OpenSearch + Kafka) est une plateforme d'observabilité industrielle haute performance conçue pour les environnements IT/OT critiques.

---

## Architecture Globale

```mermaid
flowchart TB
    subgraph SOURCES["📊 SOURCES DE DONNÉES"]
        direction LR
        SCADA["🏭 SCADA<br/>500 pts/sec"]
        MES["⚙️ MES<br/>100 evt/sec"]
        PLM["📐 PLM<br/>20 evt/sec"]
        OPCUA["🔌 OPC-UA<br/>200 nodes/sec"]
        IT["💻 IT Systems"]
    end

    subgraph INGESTION["📥 INGESTION LAYER"]
        direction TB
        KAFKA["📨 Kafka Cluster<br/>KRaft Mode"]
        OTEL["📡 OpenTelemetry Collector<br/>Ports: 4317/4318"]
    end

    subgraph STORAGE["💾 STORAGE LAYER"]
        direction LR
        VM["📈 VictoriaMetrics<br/>Time Series DB<br/>Port: 8428"]
        OO["📋 OpenObserve<br/>Logs & Traces<br/>Port: 5080"]
        OS["🔍 OpenSearch<br/>Analytics & Compliance<br/>Port: 9200"]
    end

    subgraph VISUALIZATION["📊 VISUALIZATION"]
        direction LR
        GRAFANA["📉 Grafana<br/>Port: 3000"]
        OSDASH["📊 OpenSearch<br/>Dashboards<br/>Port: 5601"]
        UNIFIED["🖥️ Unified View<br/>Port: 8085"]
        KAFKAUI["📨 Kafka UI<br/>Port: 8090"]
    end

    subgraph MODULES["🚀 GAME-CHANGER MODULES"]
        direction LR
        NLP["💬 NLP<br/>Chat Interface"]
        RCA["🔎 Auto-RCA<br/>Root Cause Analysis"]
        PRED["📊 Predictive<br/>Maintenance"]
        REMED["🔧 Auto<br/>Remediation"]
        EDGE["🌐 Edge<br/>Computing"]
    end

    SOURCES --> KAFKA
    SOURCES --> OTEL
    KAFKA --> OTEL
    OTEL --> STORAGE
    STORAGE --> VISUALIZATION
    STORAGE --> MODULES
    MODULES --> UNIFIED
```

---

## Flux de Données Détaillé

```mermaid
flowchart LR
    subgraph OT["🏭 Zone OT"]
        SIM["Simulateurs<br/>Industriels"]
        PROM["Prometheus<br/>Metrics"]
    end

    subgraph KAFKA_LAYER["📨 Message Queue"]
        K1["scada-metrics<br/>12 partitions"]
        K2["mes-events<br/>8 partitions"]
        K3["plm-data<br/>4 partitions"]
        K4["opcua-nodes<br/>8 partitions"]
    end

    subgraph OTEL_LAYER["📡 Processing Pipeline"]
        RECV["Receivers<br/>OTLP, Kafka, Prometheus"]
        PROC["Processors<br/>Batch, Memory Limiter<br/>Cardinality Control"]
        EXP["Exporters<br/>VM, OO, OS"]
    end

    subgraph STORAGE_LAYER["💾 Storage"]
        VM2["VictoriaMetrics<br/>1M séries<br/>90j rétention"]
        OO2["OpenObserve<br/>7j logs<br/>30j traces"]
        OS2["OpenSearch<br/>365j compliance"]
    end

    SIM --> PROM
    PROM --> K1 & K2 & K3 & K4
    K1 & K2 & K3 & K4 --> RECV
    RECV --> PROC
    PROC --> EXP
    EXP --> VM2 & OO2 & OS2

    style OT fill:#e1f5fe
    style KAFKA_LAYER fill:#fff3e0
    style OTEL_LAYER fill:#f3e5f5
    style STORAGE_LAYER fill:#e8f5e9
```

---

## Modes de Déploiement

### Mode 1: Architecture Kafka (Standard)

```mermaid
flowchart TB
    subgraph SIMULATORS["🏭 Simulateurs"]
        S1["SCADA"]
        S2["MES"]
        S3["PLM"]
        S4["OPC-UA"]
    end

    subgraph KAFKA["📨 Kafka Cluster"]
        direction TB
        BROKER["Kafka Broker<br/>KRaft Mode<br/>Port: 9092/9093"]
        TOPICS["Topics:<br/>scada-metrics, mes-events<br/>plm-data, opcua-nodes<br/>industrial-telemetry"]
    end

    subgraph OTEL["📡 OTEL Collector"]
        RX["Receivers:<br/>• OTLP gRPC/HTTP<br/>• Kafka Consumer<br/>• Prometheus"]
        PX["Processors:<br/>• Batch 10k/5s<br/>• Memory 2GB<br/>• Cardinality"]
        TX["Exporters:<br/>• prometheusremotewrite<br/>• otlphttp"]
    end

    subgraph BACKENDS["💾 Backends"]
        VM["VictoriaMetrics<br/>:8428"]
        OO["OpenObserve<br/>:5080"]
        OS["OpenSearch<br/>:9200"]
    end

    SIMULATORS --> |Prometheus| OTEL
    SIMULATORS --> |JSON| KAFKA
    KAFKA --> OTEL
    OTEL --> BACKENDS

    style KAFKA fill:#fff3e0
```

### Mode 2: Architecture Direct OTLP (Kafka-Free)

```mermaid
flowchart TB
    subgraph OT_ZONE["🏭 Zone OT (L2/3)"]
        SIM["Simulateurs OTLP<br/>(SDK natif)"]
        OTEL_OT["OTEL Collector OT<br/>:4337/4338<br/>File Buffer"]
    end

    subgraph DMZ_ZONE["🛡️ Zone DMZ (L3)"]
        GW["OTEL Gateway DMZ<br/>:4327/4328<br/>• Sanitization<br/>• Validation<br/>• File Buffer"]
    end

    subgraph IT_ZONE["💼 Zone IT (L4/5)"]
        OTEL_IT["OTEL Collector IT<br/>:4317/4318<br/>Full Processing"]

        subgraph BACKENDS["💾 Storage"]
            VM["VictoriaMetrics"]
            OO["OpenObserve"]
            OS["OpenSearch"]
        end

        GRAFANA["Grafana"]
    end

    SIM --> |OTLP gRPC| OTEL_OT
    OTEL_OT --> |OTLP gRPC| GW
    GW --> |OTLP gRPC| OTEL_IT
    OTEL_IT --> BACKENDS
    BACKENDS --> GRAFANA

    style OT_ZONE fill:#ffebee
    style DMZ_ZONE fill:#fff3e0
    style IT_ZONE fill:#e8f5e9
```

### Mode 3: Architecture Sécurisée (IEC 62443)

```mermaid
flowchart TB
    subgraph OT["🔴 Zone OT - IEC 62443 L2/3<br/>Réseau: 172.29.0.0/24"]
        SIM_OT["Simulateurs<br/>SCADA/MES/PLM/OPC-UA"]
        OTEL_OT["OTEL Collector OT<br/>:4319/4320"]
        KAFKA_OT["Kafka Edge OT<br/>Rétention: 4h"]
    end

    subgraph DMZ["🟡 Zone DMZ - IEC 62443 L3/3.5<br/>Réseau: 172.30.0.0/24"]
        MM["Kafka MirrorMaker 2<br/>OT→IT: ✅ ENABLED<br/>IT→OT: ❌ DISABLED"]
        DIODE["Data Diode Validator<br/>Monitoring flux inverse"]
        PROTO["Protocol Break<br/>Sanitization"]
    end

    subgraph IT["🟢 Zone IT - IEC 62443 L4/5<br/>Réseau: 172.31.0.0/16"]
        KAFKA_IT["Kafka Cluster IT<br/>3 brokers KRaft<br/>RF=3"]
        OTEL_IT["OTEL Collectors IT<br/>x2 + Nginx LB"]

        subgraph HA["Haute Disponibilité"]
            VM_HA["VictoriaMetrics<br/>Cluster HA"]
            OO_IT["OpenObserve"]
            OS_IT["OpenSearch<br/>Compliance 365j"]
        end

        GRAFANA_IT["Grafana"]
    end

    SIM_OT --> OTEL_OT
    OTEL_OT --> KAFKA_OT
    KAFKA_OT --> |UNIDIRECTIONNEL| MM
    MM --> DIODE
    DIODE --> PROTO
    PROTO --> KAFKA_IT
    KAFKA_IT --> OTEL_IT
    OTEL_IT --> HA
    HA --> GRAFANA_IT

    style OT fill:#ffcdd2
    style DMZ fill:#ffe0b2
    style IT fill:#c8e6c9
```

---

## Composants OpenTelemetry

```mermaid
flowchart LR
    subgraph RECEIVERS["📥 Receivers"]
        R1["otlp<br/>gRPC :4317<br/>HTTP :4318"]
        R2["kafka<br/>industrial-telemetry"]
        R3["prometheus<br/>:9090/metrics"]
        R4["hostmetrics<br/>CPU, Memory, Disk"]
        R5["filelog<br/>/var/log/*.log"]
    end

    subgraph PROCESSORS["⚙️ Processors"]
        P1["batch<br/>10000 items<br/>5s timeout"]
        P2["memory_limiter<br/>2GB limit<br/>1.8GB spike"]
        P3["resourcedetection<br/>docker, system"]
        P4["attributes<br/>add: environment<br/>hash: device_id"]
        P5["transform<br/>context manipulation"]
    end

    subgraph EXPORTERS["📤 Exporters"]
        E1["prometheusremotewrite<br/>→ VictoriaMetrics"]
        E2["otlphttp<br/>→ OpenObserve"]
        E3["opensearch<br/>→ OpenSearch"]
        E4["kafka<br/>→ processed-telemetry"]
    end

    RECEIVERS --> PROCESSORS
    PROCESSORS --> EXPORTERS
```

---

## Architecture des Modules Game-Changer

```mermaid
flowchart TB
    subgraph API["🌐 FastAPI Backend - Port 8085"]
        ROUTER["API Router"]
    end

    subgraph MODULES["🚀 Game-Changer Modules"]
        subgraph NLP_MOD["💬 NLP Module"]
            NLP_PARSER["Query Parser<br/>FR/EN"]
            NLP_INTENT["Intent Detection"]
            NLP_GEN["PromQL Generator"]
        end

        subgraph RCA_MOD["🔎 Auto-RCA Module"]
            RCA_CORR["Temporal Correlator"]
            RCA_GRAPH["Causal Graph Builder"]
            RCA_ANALYZE["Root Cause Analyzer"]
        end

        subgraph PRED_MOD["📊 Predictive Module"]
            PRED_ANOM["Anomaly Detection<br/>Z-Score Analysis"]
            PRED_TREND["Trend Analysis"]
            PRED_RUL["RUL Estimator"]
        end

        subgraph REMED_MOD["🔧 Remediation Module"]
            REMED_LIB["Runbook Library"]
            REMED_EXEC["Executor"]
            REMED_APPROVE["Approval Workflow"]
        end

        subgraph EDGE_MOD["🌐 Edge Module"]
            EDGE_MGR["Agent Manager"]
            EDGE_PROC["Local Processor"]
            EDGE_SYNC["Sync Manager"]
        end
    end

    subgraph DATA["💾 Data Sources"]
        VM_DATA["VictoriaMetrics"]
        OS_DATA["OpenSearch"]
        OO_DATA["OpenObserve"]
    end

    ROUTER --> NLP_MOD & RCA_MOD & PRED_MOD & REMED_MOD & EDGE_MOD
    NLP_MOD --> VM_DATA
    RCA_MOD --> VM_DATA & OS_DATA
    PRED_MOD --> VM_DATA
    EDGE_MOD --> ROUTER
```

---

## Tableau des Ports et Services

| Service | Port | Protocole | Description |
|---------|------|-----------|-------------|
| **Kafka** | 9092 | TCP | Bootstrap (interne) |
| **Kafka** | 9093 | TCP | Bootstrap (externe) |
| **OTEL Collector** | 4317 | gRPC | OTLP gRPC receiver |
| **OTEL Collector** | 4318 | HTTP | OTLP HTTP receiver |
| **OTEL Collector** | 8888 | HTTP | Prometheus metrics |
| **OTEL Collector** | 13133 | HTTP | Health check |
| **VictoriaMetrics** | 8428 | HTTP | Query & Ingest API |
| **OpenObserve** | 5080 | HTTP | Web UI & API |
| **OpenSearch** | 9200 | HTTP | REST API |
| **OpenSearch Dashboards** | 5601 | HTTP | Web UI |
| **Grafana** | 3000 | HTTP | Web UI |
| **Kafka UI** | 8090 | HTTP | Web UI |
| **Unified View** | 8085 | HTTP | FastAPI + React |

---

## Configuration des Topics Kafka

```mermaid
flowchart LR
    subgraph TOPICS["📨 Kafka Topics Configuration"]
        T1["scada-metrics<br/>Partitions: 12<br/>Retention: 24h<br/>Compression: LZ4"]
        T2["mes-events<br/>Partitions: 8<br/>Retention: 24h<br/>Compression: LZ4"]
        T3["plm-data<br/>Partitions: 4<br/>Retention: 24h"]
        T4["opcua-nodes<br/>Partitions: 8<br/>Retention: 24h<br/>Compression: LZ4"]
        T5["industrial-telemetry<br/>Partitions: 12<br/>Retention: 24h<br/>Compression: LZ4"]
    end

    subgraph CONSUMERS["📥 Consumers"]
        C1["OTEL Collector<br/>Group: otel-consumer"]
    end

    TOPICS --> CONSUMERS
```

---

## Métriques de Performance

| Métrique | Valeur Cible | Description |
|----------|--------------|-------------|
| **Ingestion Rate** | 100k+ pts/sec | Métriques time-series |
| **Log Ingestion** | 50k+ evt/sec | Événements de log |
| **Query Latency (p99)** | < 500ms | Requêtes VictoriaMetrics |
| **Ingestion Latency (p99)** | < 100ms | Pipeline OTEL |
| **Active Time Series** | 1M max | Cardinalité VictoriaMetrics |
| **Metrics Retention** | 90 jours | VictoriaMetrics |
| **Logs Retention** | 7 jours | OpenObserve (temps réel) |
| **Compliance Retention** | 365 jours | OpenSearch |

---

## Comparaison des Modes de Déploiement

| Critère | Kafka Mode | Direct OTLP | Secure (IEC 62443) |
|---------|------------|-------------|---------------------|
| **Complexité** | Moyenne | Faible | Élevée |
| **Mémoire Kafka** | 10.5 GB | 0 GB | 12+ GB |
| **Mémoire OTEL** | 2 GB | 2.75 GB | 4+ GB |
| **Replay des données** | ✅ Oui | ❌ Non | ✅ Oui |
| **Multi-consumer** | ✅ Oui | ❌ Non | ✅ Oui |
| **Sécurité IT/OT** | Moyenne | Moyenne | Très élevée |
| **Conformité IEC 62443** | ❌ Non | ❌ Non | ✅ Oui |
| **Data Diode** | ❌ Non | ❌ Non | ✅ Oui |
| **Cas d'usage** | Standard | POC/Dev | Production critique |

---

## Diagramme de Séquence: Flux de Données

```mermaid
sequenceDiagram
    participant SIM as Simulateur
    participant KAFKA as Kafka
    participant OTEL as OTEL Collector
    participant VM as VictoriaMetrics
    participant OO as OpenObserve
    participant OS as OpenSearch
    participant GRAFANA as Grafana

    SIM->>KAFKA: Publish metrics (JSON)
    SIM->>OTEL: Expose /metrics (Prometheus)

    loop Every 15s
        OTEL->>SIM: Scrape Prometheus metrics
    end

    KAFKA->>OTEL: Consume from topics

    OTEL->>OTEL: Process (batch, filter, transform)

    par Export to backends
        OTEL->>VM: Remote Write (metrics)
        OTEL->>OO: OTLP HTTP (logs/traces)
        OTEL->>OS: Bulk API (compliance)
    end

    GRAFANA->>VM: Query metrics
    GRAFANA->>OO: Query logs
    GRAFANA->>OS: Query analytics
```

---

## Architecture Unified Business-Tech View

```mermaid
flowchart TB
    subgraph FRONTEND["🖥️ React Dashboard - Port 3001"]
        BV["📊 Business View<br/>OEE, Production KPIs"]
        TV["⚙️ Tech View<br/>Services, Resources"]
        UV["🔗 Unified View<br/>Cross-domain Correlation"]
    end

    subgraph BACKEND["🌐 FastAPI Backend - Port 8085"]
        API["REST API<br/>/api/metrics<br/>/api/services<br/>/api/events"]
        WS["WebSocket<br/>/ws"]
        MODULES_API["Modules API<br/>/api/chat<br/>/api/rca<br/>/api/predictive"]
    end

    subgraph DATA_SOURCES["💾 Data Sources"]
        VM_SRC["VictoriaMetrics<br/>Business Metrics"]
        OS_SRC["OpenSearch<br/>Event Logs"]
        KAFKA_SRC["Kafka<br/>Real-time Events"]
    end

    FRONTEND <--> |HTTP/WS| BACKEND
    BACKEND <--> DATA_SOURCES
```

---

## Prochaines Étapes

1. **Kubernetes Deployment** - Helm charts pour production
2. **Hardware Data Diode** - Pour installations critiques
3. **TLS/mTLS** - Chiffrement inter-services
4. **Multi-Datacenter** - Réplication cross-site
5. **GPU Acceleration** - Pour modules AI/ML

---

## Références

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [VictoriaMetrics Docs](https://docs.victoriametrics.com/)
- [OpenObserve Docs](https://openobserve.ai/docs/)
- [OpenSearch Documentation](https://opensearch.org/docs/)
- [IEC 62443 Standard](https://www.iec.ch/cyber-security)
