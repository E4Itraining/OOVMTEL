# Kafka Alternatives Analysis for OOVMTEL

## Executive Summary

Kafka introduces significant complexity in the OOVMTEL architecture:
- **3 separate Kafka clusters** (OT, DMZ, IT)
- **MirrorMaker 2** for data diode pattern
- **Format incompatibilities** (JSON producers vs OTLP consumers)
- **KRaft configuration challenges** (cluster ID issues, metadata conflicts)
- **High operational overhead** for an observability stack

This document analyzes alternatives that could simplify the architecture while maintaining security and performance requirements.

---

## Current Kafka Pain Points

### 1. Operational Complexity
| Issue | Impact |
|-------|--------|
| 3 separate Kafka clusters | Triple the monitoring, configuration, troubleshooting |
| MirrorMaker 2 | Additional failure point, lag management, offset sync |
| KRaft cluster IDs | Multiple commits to fix invalid UUIDs and metadata conflicts |
| Consumer group management | Offset tracking across 3 clusters |

### 2. Format Mismatch
- Simulators produce **JSON** to Kafka
- OTel Collectors expect **OTLP protobuf**
- Current workaround: Prometheus scraping bypasses Kafka entirely
- Creates dual ingestion paths (Kafka + HTTP)

### 3. Resource Overhead
- Each Kafka broker: 2GB heap minimum
- 3-broker IT cluster: 6GB+ RAM just for Kafka
- Plus MirrorMaker, Kafka UI, topic management

### 4. Data Diode Complexity
- Software-based data diode via MirrorMaker 2
- Validator service running every 60s
- Not a true airgap (hardware diode mentioned as future work)

---

## Alternative Solutions

### Option 1: NATS JetStream (Recommended)

**What is it?** Lightweight, high-performance messaging system with built-in persistence.

**Why it's better for OOVMTEL:**

| Feature | Kafka | NATS JetStream |
|---------|-------|----------------|
| Memory footprint | 2GB+ per broker | 50-100MB |
| Configuration | Complex (KRaft, cluster IDs) | Simple YAML |
| Native OTLP support | No (needs conversion) | OTel exporter available |
| Deployment | Heavy (JVM-based) | Single binary (Go) |
| Data replication | MirrorMaker 2 | Built-in leafnodes |
| Latency | milliseconds | microseconds |

**Architecture with NATS:**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   OT Zone   │    │  DMZ Zone   │    │   IT Zone   │
│  NATS Leaf  │───▶│  NATS Hub   │───▶│  NATS Leaf  │
│  (edge)     │    │  (gateway)  │    │  (storage)  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
  OTel Collector    Security Filter    OTel Collector
       │                  │                  │
   Simulators         Validation      OpenSearch/VM
```

**Data Diode with NATS:**
- Use **leafnode** connections (unidirectional by design)
- Gateway can filter/sanitize messages
- No separate replication tool needed

**Sample NATS configuration:**
```yaml
# nats-server.conf (DMZ Hub)
jetstream: {
  store_dir: /data/jetstream
  max_memory_store: 1GB
  max_file_store: 10GB
}

leafnodes: {
  port: 7422
  authorization: {
    users: [
      {user: ot-zone, password: $OT_NATS_PASS, permissions: {publish: "ot.>"}}
      {user: it-zone, password: $IT_NATS_PASS, permissions: {subscribe: "it.>"}}
    ]
  }
}

# Unidirectional: OT can only publish, IT can only subscribe
```

**Migration effort:** Medium (2-3 days)
- Replace KafkaProducer with NATS client in simulators
- Configure OTel NATS exporter
- Simplify docker-compose significantly

---

### Option 2: Direct OTLP over gRPC (Simplest)

**Concept:** Eliminate the message queue entirely for this observability use case.

**Why consider this:**
- OpenTelemetry has built-in **retry, batching, and backpressure**
- OTel Collector can buffer data during downstream outages
- For observability data, "at-least-once" delivery is typically sufficient

**Architecture:**
```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   OT Zone   │  OTLP   │  DMZ Zone   │  OTLP   │   IT Zone   │
│ OTel Agent  │────────▶│ OTel Gateway│────────▶│OTel Collector│
│ (buffered)  │  gRPC   │ (sanitizer) │  gRPC   │  (router)   │
└─────────────┘         └─────────────┘         └─────────────┘
       ▲                                              │
  Simulators                              ┌───────────┼───────────┐
  (native OTLP)                           ▼           ▼           ▼
                                    VictoriaMetrics OpenObserve OpenSearch
```

**Benefits:**
- **Zero message queue** infrastructure
- Native OTLP format end-to-end
- OTel Collector handles batching/retry
- File-based buffer for disconnected scenarios

**OTel Collector as buffer:**
```yaml
# OT Zone OTel Collector with file storage buffer
extensions:
  file_storage:
    directory: /var/lib/otelcol/buffer
    timeout: 10s
    compaction:
      on_start: true
      on_rebound: true

exporters:
  otlp:
    endpoint: dmz-otel:4317
    sending_queue:
      enabled: true
      storage: file_storage
      num_consumers: 10
      queue_size: 10000
    retry_on_failure:
      enabled: true
      initial_interval: 5s
      max_interval: 300s
```

**Data Diode consideration:**
- Use **network firewall rules** to enforce unidirectional flow
- OT zone only has outbound rules to DMZ
- DMZ cannot initiate connections back to OT

**Migration effort:** Low (1-2 days)
- Modify simulators to use OTLP SDK
- Remove all Kafka services
- Configure OTel file-based queuing

---

### Option 3: Apache Pulsar

**What is it?** Multi-tenant, geo-replicated messaging with built-in tiered storage.

**Why consider it:**
- Native **geo-replication** (replaces MirrorMaker)
- Built-in **topic compaction** and **tiered storage**
- Better multi-tenancy than Kafka

| Feature | Kafka | Pulsar |
|---------|-------|--------|
| Geo-replication | MirrorMaker 2 | Native async replication |
| Multi-zone | Separate clusters | Single logical cluster |
| Storage tiering | Requires Tiered Storage plugin | Built-in |
| Kubernetes native | Strimzi (complex) | Pulsar Operator |

**However:** Pulsar is still complex and heavy. Only recommended if you need:
- True multi-datacenter deployment
- Millions of topics
- Long-term message retention with tiered storage

**Migration effort:** High (1 week+)

---

### Option 4: Redis Streams

**What is it?** Lightweight stream processing built into Redis.

**Good for:**
- Simpler use cases with moderate throughput
- When you already have Redis in your stack
- Real-time processing with minimal infrastructure

**Limitations:**
- Memory-bound (no native disk persistence for streams)
- Less mature ecosystem than Kafka/NATS
- Not ideal for high-throughput industrial telemetry

**Migration effort:** Medium (2-3 days)

---

### Option 5: Keep Kafka but Simplify

If Kafka must stay, here's how to reduce complexity:

#### 5a. Single Kafka Cluster + Network Segmentation
```
┌─────────────────────────────────────────────────────────┐
│                   Single Kafka Cluster                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                  │
│  │Broker 1 │  │Broker 2 │  │Broker 3 │                  │
│  └─────────┘  └─────────┘  └─────────┘                  │
│                      │                                   │
│  Topics: ot.*, dmz.*, it.*                              │
│  ACLs: OT can only write ot.*, IT can only read it.*    │
└─────────────────────────────────────────────────────────┘
         │                                    │
    OT Network                           IT Network
    (write only)                         (read only)
```

**Benefits:**
- Eliminate MirrorMaker 2
- Use Kafka ACLs for unidirectional access
- Single cluster to manage

#### 5b. Use Kafka Schema Registry
- Enforce OTLP protobuf schema
- Simulators serialize to protobuf directly
- Eliminates JSON/OTLP format mismatch

#### 5c. Managed Kafka (Confluent Cloud, AWS MSK, Redpanda Cloud)
- Offload operational burden
- Built-in replication across regions
- **Redpanda** is Kafka-API compatible but much lighter

---

## Recommendation Matrix

| Priority | Solution | Complexity Reduction | Migration Effort | Best For |
|----------|----------|---------------------|------------------|----------|
| ⭐⭐⭐ | **Direct OTLP** | 90% (no MQ) | Low | Pure observability |
| ⭐⭐⭐ | **NATS JetStream** | 70% | Medium | Event streaming + obs |
| ⭐⭐ | **Simplified Kafka** | 40% | Low | Keep existing skills |
| ⭐ | **Pulsar** | 20% | High | Enterprise multi-DC |
| ⭐ | **Redis Streams** | 60% | Medium | Low-volume use cases |

---

## Recommended Approach for OOVMTEL

### Primary Recommendation: Direct OTLP with File-Based Buffering

**Rationale:**
1. OOVMTEL is an **observability platform**, not a general event streaming system
2. OpenTelemetry has mature **buffering and retry** capabilities
3. Eliminates 3 Kafka clusters, MirrorMaker 2, and format conversion
4. Reduces container count by 8-10 services
5. Security zones can be enforced via **network firewall rules**

**Implementation Steps:**
1. Modify simulators to emit OTLP directly (SDK available for Python)
2. Configure OTel Collector in OT zone with file-based sending queue
3. Deploy OTel Gateway in DMZ for sanitization
4. Route to IT zone OTel Collector → backends
5. Remove all Kafka-related services

### Secondary Recommendation: NATS JetStream

**When to choose NATS instead:**
- You need message **replay** capabilities
- Multiple consumers need the same data stream
- You want **exactly-once** processing semantics
- Future plans include non-observability event streaming

---

## Migration Path (Direct OTLP)

### Phase 1: Parallel Deployment (Week 1)
- Add OTLP endpoints to simulators alongside Kafka
- Deploy OTel Collectors with file-based queue
- Verify data reaches backends via OTLP path

### Phase 2: Validation (Week 2)
- Compare metrics between Kafka and OTLP paths
- Test failure scenarios (network outage, backend down)
- Validate file buffer recovery

### Phase 3: Cutover (Week 3)
- Disable Kafka producers in simulators
- Remove Kafka services from docker-compose
- Update documentation

### Phase 4: Cleanup
- Remove Kafka configurations
- Archive MirrorMaker configs
- Update monitoring dashboards

---

## Resource Comparison

### Current Architecture (with Kafka)
| Service | Memory | CPU |
|---------|--------|-----|
| kafka (main) | 2GB | 1 core |
| kafka-ot | 1GB | 0.5 core |
| kafka-it (x3) | 6GB | 2 cores |
| mirrormaker2 | 1GB | 0.5 core |
| kafka-ui | 512MB | 0.25 core |
| **Total Kafka** | **10.5GB** | **4.25 cores** |

### Proposed Architecture (Direct OTLP)
| Service | Memory | CPU |
|---------|--------|-----|
| otel-collector-ot | 256MB | 0.25 core |
| otel-gateway-dmz | 256MB | 0.25 core |
| otel-collector-it | 512MB | 0.5 core |
| **Total** | **1GB** | **1 core** |

**Savings:** ~90% memory, ~75% CPU reduction

---

## Conclusion

For an industrial observability platform like OOVMTEL, **Kafka is over-engineered**. The data diode requirement can be achieved more simply with:

1. **Network-level enforcement** (firewall rules)
2. **OTel Gateway** for sanitization
3. **File-based buffering** for reliability

Kafka excels at:
- Multi-consumer event streaming
- Long-term message retention
- Complex stream processing (KStreams, ksqlDB)

None of these are primary requirements for OOVMTEL's observability use case.

**Recommended action:** Implement Direct OTLP with file-based buffering, achieving 90% reduction in message queue infrastructure while maintaining security and reliability.
