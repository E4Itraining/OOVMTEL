# Diagrammes d'Architecture OOVMTEL

Collection de diagrammes Mermaid pour visualiser l'architecture de la plateforme.

> **Tip:** Ces diagrammes sont au format Mermaid et peuvent être rendus par GitHub, GitLab, et la plupart des outils de documentation modernes.

---

## 1. Architecture Globale

```mermaid
flowchart TB
    subgraph SOURCES["🏭 DATA SOURCES"]
        direction LR
        SCADA["SCADA<br/>500 pts/sec"]
        MES["MES<br/>100 evt/sec"]
        PLM["PLM<br/>20 evt/sec"]
        OPCUA["OPC-UA<br/>200 nodes/sec"]
    end

    subgraph INGESTION["📥 INGESTION"]
        direction TB
        KAFKA["Kafka<br/>KRaft Mode"]
        OTEL["OTEL Collector"]
    end

    subgraph STORAGE["💾 STORAGE"]
        direction LR
        VM["VictoriaMetrics<br/>Metrics 90j"]
        OO["OpenObserve<br/>Logs/Traces 7j"]
        OS["OpenSearch<br/>Compliance 365j"]
    end

    subgraph VIZ["📊 VISUALIZATION"]
        direction LR
        GRAFANA["Grafana"]
        UNIFIED["Unified View"]
        OSDASH["OS Dashboards"]
    end

    subgraph MODULES["🧠 AI MODULES"]
        direction LR
        NLP["NLP Chat"]
        RCA["Auto-RCA"]
        PRED["Predictive"]
        REMED["Remediation"]
    end

    SOURCES --> KAFKA --> OTEL
    SOURCES --> OTEL
    OTEL --> STORAGE
    STORAGE --> VIZ
    STORAGE --> MODULES
    MODULES --> UNIFIED
```

---

## 2. Flux de Données

```mermaid
sequenceDiagram
    participant SIM as Simulateurs
    participant KAFKA as Kafka
    participant OTEL as OTEL Collector
    participant VM as VictoriaMetrics
    participant OO as OpenObserve
    participant OS as OpenSearch
    participant UI as Grafana/Unified

    Note over SIM,UI: Phase 1: Collecte
    SIM->>KAFKA: Publish JSON events
    SIM->>OTEL: Prometheus /metrics
    KAFKA->>OTEL: Consume from topics

    Note over SIM,UI: Phase 2: Processing
    OTEL->>OTEL: Batch (10k items)
    OTEL->>OTEL: Filter & Transform

    Note over SIM,UI: Phase 3: Distribution
    par Parallel Export
        OTEL->>VM: Remote Write (metrics)
        OTEL->>OO: OTLP HTTP (logs/traces)
        OTEL->>OS: Bulk API (compliance)
    end

    Note over SIM,UI: Phase 4: Visualization
    UI->>VM: PromQL queries
    UI->>OO: Log queries
    UI->>OS: Analytics
```

---

## 3. Modes de Déploiement

### Mode Standard

```mermaid
flowchart LR
    subgraph SIMS["Simulateurs"]
        S1["SCADA"]
        S2["MES"]
        S3["PLM"]
        S4["OPC-UA"]
    end

    KAFKA["Kafka<br/>:9092"]
    OTEL["OTEL<br/>:4317/4318"]

    subgraph STORAGE["Storage"]
        VM["VM :8428"]
        OO["OO :5080"]
        OS["OS :9200"]
    end

    GRAFANA["Grafana :3000"]

    SIMS --> KAFKA --> OTEL --> STORAGE --> GRAFANA
```

### Mode Direct-OTLP

```mermaid
flowchart TB
    subgraph OT["Zone OT"]
        SIM["Simulateurs"]
        OTEL_OT["OTEL OT<br/>:4337/4338"]
    end

    subgraph DMZ["Zone DMZ"]
        GW["OTEL Gateway<br/>:4327/4328"]
    end

    subgraph IT["Zone IT"]
        OTEL_IT["OTEL IT<br/>:4317/4318"]
        STORE["Storage"]
        VIZ["Visualization"]
    end

    SIM --> OTEL_OT --> GW --> OTEL_IT --> STORE --> VIZ

    style OT fill:#ffcdd2
    style DMZ fill:#ffe0b2
    style IT fill:#c8e6c9
```

### Mode Sécurisé (IEC 62443)

```mermaid
flowchart TB
    subgraph OT["Zone OT - L2/L3"]
        SIM_OT["Simulateurs"]
        KAFKA_OT["Kafka OT"]
    end

    subgraph DMZ["Zone DMZ - L3/L3.5"]
        MM["MirrorMaker 2"]
        DIODE["Data Diode"]
    end

    subgraph IT["Zone IT - L4/L5"]
        KAFKA_HA["Kafka HA x3"]
        VM_HA["VM Cluster"]
        GRAFANA["Grafana"]
    end

    SIM_OT --> KAFKA_OT
    KAFKA_OT --> |"Unidirectionnel"| MM
    MM --> DIODE --> KAFKA_HA --> VM_HA --> GRAFANA

    style OT fill:#ffcdd2
    style DMZ fill:#ffe0b2
    style IT fill:#c8e6c9
```

---

## 4. Pipeline OTEL

```mermaid
flowchart LR
    subgraph RX["Receivers"]
        OTLP["OTLP<br/>:4317/4318"]
        PROM["Prometheus<br/>scrape"]
        KAFKA["Kafka<br/>consumer"]
        HOST["Hostmetrics"]
    end

    subgraph PX["Processors"]
        MEM["Memory<br/>Limiter"]
        BATCH["Batch<br/>10k/5s"]
        RES["Resource<br/>Detection"]
        ATTR["Attributes"]
        FILT["Filter"]
    end

    subgraph EX["Exporters"]
        PRW["Remote Write<br/>→ VM"]
        OTLPH["OTLP HTTP<br/>→ OO"]
        OSE["OpenSearch<br/>→ OS"]
    end

    RX --> MEM --> BATCH --> RES --> ATTR --> FILT --> EX
```

---

## 5. Modules Game-Changer

```mermaid
flowchart TB
    subgraph API["FastAPI Backend :8085"]
        ROUTER["API Router"]
    end

    subgraph MODULES["Modules"]
        NLP["NLP Module<br/>FR/EN Query"]
        RCA["RCA Module<br/>Root Cause"]
        PRED["Predictive<br/>Anomaly/RUL"]
        REMED["Remediation<br/>Runbooks"]
        HPC["HPC<br/>Parallel"]
    end

    subgraph DATA["Data Sources"]
        VM["VictoriaMetrics<br/>PromQL"]
        OS["OpenSearch<br/>Query DSL"]
        OO["OpenObserve<br/>SQL"]
    end

    ROUTER --> MODULES
    MODULES --> DATA
```

---

## 6. Architecture des Personas

```mermaid
mindmap
  root((OOVMTEL))
    Business
      Dirigeant
        Command Center
        KPIs
      CFO
        Vue Financière
        ROI
      Dir. Production
        OEE
        Équipements
    Tech
      DSI
        Infrastructure
        Gouvernance
      Data/MLOps
        Pipelines
        ML Models
      DevOps/SRE
        SLOs
        Incidents
    Sécurité
      RSSI
        Posture
        Vulnérabilités
      Analyste SOC
        Alertes
        Investigation
    Juridique
      DPO
        RGPD
        Audit Trail
      Conformité
        Régulations EU
    GreenOps
      Resp. RSE
        Impact Carbone
      Green IT
        PUE
        Énergie
```

---

## 7. Réseau et Ports

```mermaid
flowchart TB
    subgraph INGESTION["Ingestion Layer"]
        OTEL_G["OTEL gRPC :4317"]
        OTEL_H["OTEL HTTP :4318"]
        KAFKA_I["Kafka :9092"]
        KAFKA_E["Kafka :9093"]
    end

    subgraph STORAGE["Storage Layer"]
        VM_P["VictoriaMetrics :8428"]
        OO_P["OpenObserve :5080"]
        OS_P["OpenSearch :9200"]
    end

    subgraph VIZ["Visualization"]
        GRAFANA_P["Grafana :3000"]
        UNIFIED_P["Unified View :8085"]
        OSDASH_P["OS Dashboards :5601"]
        KAFKAUI_P["Kafka UI :8090"]
    end

    subgraph SIMS["Simulators"]
        SCADA_P["SCADA :8080"]
        MES_P["MES :8081"]
        PLM_P["PLM :8082"]
        OPCUA_P["OPC-UA :8083"]
    end

    SIMS --> INGESTION --> STORAGE --> VIZ
```

---

## Utilisation des Diagrammes

Ces diagrammes peuvent être :

1. **Rendus par GitHub/GitLab** - Visualisation directe dans le repository
2. **Exportés en images** - Via [Mermaid Live Editor](https://mermaid.live/)
3. **Intégrés dans des présentations** - Export PNG/SVG
4. **Utilisés dans la documentation** - MkDocs, Docusaurus, etc.

## Outils Recommandés

- [Mermaid Live Editor](https://mermaid.live/) - Éditeur en ligne
- [VS Code Mermaid Extension](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) - Preview dans VS Code
- [mermaid-cli](https://github.com/mermaid-js/mermaid-cli) - Génération d'images en ligne de commande
