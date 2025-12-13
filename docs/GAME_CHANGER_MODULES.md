# OOVMTEL Game-Changer Modules

## Overview

OOVMTEL includes 5 advanced modules that differentiate it from traditional industrial observability platforms:

1. **NLP/Conversational Interface** - Natural language queries in French/English
2. **Auto-RCA Engine** - Automated Root Cause Analysis with causal graphs
3. **Predictive Maintenance** - Anomaly detection and RUL estimation
4. **Auto-Remediation** - Runbook-based automated remediation
5. **Edge Computing** - Distributed edge processing architecture

---

## 1. NLP/Conversational Interface

### Description
Query your industrial data using natural language in French or English. No need to learn PromQL or complex query syntax.

### API Endpoint

```
POST /api/chat
```

### Request Body
```json
{
  "query": "Quelle est la température du moteur principal?",
  "language": "fr",
  "context": {
    "equipment": "Motor-001",
    "timeRange": "1h"
  }
}
```

### Response
```json
{
  "response": "La température du moteur principal est actuellement de 65°C, ce qui est dans les limites normales.",
  "data": {
    "current_value": 65,
    "unit": "°C",
    "status": "normal"
  },
  "query_generated": "industrial_temperature{equipment=\"Motor-001\"}",
  "visualizations": [
    {
      "type": "gauge",
      "config": {}
    }
  ]
}
```

### Supported Query Types
- **Status queries**: "Quel est l'état de la ligne de production?"
- **Metric queries**: "Quelle est la température du four 3?"
- **Trend analysis**: "Comment évolue la pression depuis 24h?"
- **Comparisons**: "Compare les performances des équipements de la zone A"
- **Alerts**: "Y a-t-il des alertes actives?"
- **Predictions**: "Quand faut-il planifier la maintenance du compresseur?"

---

## 2. Auto-RCA Engine

### Description
Automatically analyze incidents and identify root causes using causal graph analysis and temporal correlation.

### API Endpoints

#### Analyze Incident
```
POST /api/rca/analyze
```

**Request Body:**
```json
{
  "incident_id": "INC-2024-001",
  "description": "Production line stopped unexpectedly",
  "affected_equipment": ["Conveyor-A1", "Motor-M3"],
  "start_time": "2024-01-15T10:30:00Z",
  "severity": "high"
}
```

**Response:**
```json
{
  "incident_id": "INC-2024-001",
  "root_causes": [
    {
      "cause": "Motor overheating",
      "probability": 0.85,
      "evidence": [
        "Temperature exceeded 90°C at 10:28",
        "Vibration spike detected at 10:27"
      ]
    }
  ],
  "causal_graph": {
    "nodes": [...],
    "edges": [...]
  },
  "remediation_suggestions": [
    {
      "action": "restart_cooling_system",
      "confidence": 0.9
    }
  ],
  "timeline": [...]
}
```

#### Detect Anomalies
```
POST /api/rca/detect
```

Automatically detects incidents based on metric anomalies.

---

## 3. Predictive Maintenance

### Description
Predict equipment failures before they happen using anomaly detection, trend analysis, and Remaining Useful Life (RUL) estimation.

### API Endpoints

#### Full Predictive Analysis
```
GET /api/predictive/analyze?equipment=Motor-001
```

**Response:**
```json
{
  "equipment": "Motor-001",
  "health_score": 75,
  "rul_prediction": {
    "rul_hours": 720,
    "rul_days": 30,
    "confidence": 0.82,
    "predicted_failure_date": "2024-02-15T00:00:00Z",
    "failure_mode": "bearing_wear",
    "recommended_action": "Schedule preventive maintenance within this week"
  },
  "anomalies": [
    {
      "metric": "vibration",
      "severity": "medium",
      "z_score": 2.5,
      "recommendation": "Increase monitoring frequency"
    }
  ],
  "trends": [
    {
      "metric": "temperature",
      "direction": "increasing",
      "slope": 0.5,
      "is_concerning": true
    }
  ]
}
```

#### Equipment Health Dashboard
```
GET /api/predictive/health
```

Returns health scores for all monitored equipment.

#### Predictive Alerts
```
GET /api/predictive/alerts
```

Returns predictive maintenance alerts sorted by urgency.

---

## 4. Auto-Remediation

### Description
Automated incident remediation using pre-defined runbooks with approval workflows.

### API Endpoints

#### List Available Runbooks
```
GET /api/remediation/runbooks?category=infrastructure
```

**Response:**
```json
{
  "runbooks": [
    {
      "id": "restart_service",
      "name": "Restart Service",
      "description": "Safely restart a failed service",
      "category": "infrastructure",
      "risk_level": "low",
      "estimated_duration": 60,
      "success_rate": 0.95,
      "steps": [...]
    }
  ]
}
```

#### Execute Remediation
```
POST /api/remediation/execute
```

**Request Body:**
```json
{
  "runbook_id": "restart_service",
  "target": "worker-node-01",
  "parameters": {
    "service_name": "production-service",
    "wait_time": 30
  },
  "require_approval": true
}
```

#### Pending Approvals
```
GET /api/remediation/pending
```

Lists remediation actions awaiting approval.

#### Approve/Reject Action
```
POST /api/remediation/approve/{action_id}
```

**Request Body:**
```json
{
  "approved": true,
  "comment": "Approved for execution during maintenance window"
}
```

#### Execution History
```
GET /api/remediation/history?limit=50
```

### Built-in Runbooks

| Runbook | Description | Risk Level |
|---------|-------------|------------|
| `restart_service` | Safely restart a service | Low |
| `scale_container` | Scale container replicas | Low |
| `clear_cache` | Clear application caches | Low |
| `failover_database` | Failover to standby database | High |
| `recalibrate_sensor` | Recalibrate industrial sensor | Medium |

---

## 5. Edge Computing

### Description
Distributed edge processing for remote sites with offline capability, local anomaly detection, and bandwidth-optimized sync.

### API Endpoints

#### Register Edge Agent
```
POST /api/edge/register
```

**Request Body:**
```json
{
  "agent_id": "edge-site-paris-01",
  "site_name": "Paris Manufacturing Plant",
  "location": "Paris, France",
  "capabilities": ["metrics", "logs", "local_inference"],
  "config": {
    "processing_mode": "balanced",
    "sync_interval": 60,
    "buffer_size_mb": 100
  }
}
```

#### List Edge Agents
```
GET /api/edge/agents
```

**Response:**
```json
{
  "agents": [
    {
      "agent_id": "edge-site-paris-01",
      "status": "online",
      "last_sync": "2024-01-15T10:30:00Z",
      "metrics": {
        "data_points_processed": 150000,
        "buffer_usage_percent": 15,
        "sync_latency_ms": 250
      }
    }
  ]
}
```

#### Get Agent Status
```
GET /api/edge/agents/{agent_id}
```

#### Receive Edge Data
```
POST /api/edge/data
```

Endpoint for edge agents to push aggregated data.

#### Receive Edge Alerts
```
POST /api/edge/alerts
```

Endpoint for edge agents to push locally detected alerts.

### Edge Processing Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `minimal` | Basic aggregation only | Very low bandwidth |
| `balanced` | Aggregation + anomaly detection | Standard remote sites |
| `full` | Full local processing + ML inference | High-capability edge |

---

## Module Status

Check the status of all game-changer modules:

```
GET /api/modules/status
```

**Response:**
```json
{
  "modules_enabled": true,
  "modules": {
    "nlp": {
      "status": "active",
      "queries_processed": 1250,
      "languages": ["fr", "en"]
    },
    "rca": {
      "status": "active",
      "incidents_analyzed": 45
    },
    "predictive": {
      "status": "active",
      "equipment_monitored": 150,
      "active_predictions": 23
    },
    "remediation": {
      "status": "active",
      "dry_run_mode": true,
      "runbooks_available": 5,
      "actions_executed": 120
    },
    "edge": {
      "status": "active",
      "agents_registered": 8,
      "agents_online": 7
    }
  }
}
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MODULES_ENABLED` | Enable game-changer modules | `true` |
| `NLP_DEFAULT_LANGUAGE` | Default language for NLP | `fr` |
| `REMEDIATION_DRY_RUN` | Execute in dry-run mode | `true` |
| `REMEDIATION_REQUIRE_APPROVAL` | Require approval for actions | `true` |
| `EDGE_SYNC_INTERVAL` | Edge sync interval (seconds) | `60` |
| `PREDICTIVE_ANOMALY_SENSITIVITY` | Z-score threshold for anomalies | `2.0` |

### Docker Compose Configuration

The modules are automatically enabled when using the standard docker-compose configuration:

```yaml
unified-view:
  environment:
    MODULES_ENABLED: "true"
    NLP_DEFAULT_LANGUAGE: "fr"
    REMEDIATION_DRY_RUN: "true"
    REMEDIATION_REQUIRE_APPROVAL: "true"
```

---

## Architecture

```
+------------------+     +------------------+     +------------------+
|   NLP Module     |     |   RCA Module     |     | Predictive Module|
|                  |     |                  |     |                  |
| - Query Parser   |     | - Correlator     |     | - Anomaly Detect |
| - Intent Detect  |     | - Graph Builder  |     | - Trend Analysis |
| - Query Gen      |     | - Root Cause     |     | - RUL Estimator  |
| - Response Build |     |   Analysis       |     | - Forecaster     |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         +------------------------+------------------------+
                                  |
                    +-------------+-------------+
                    |     Main Application      |
                    |        (FastAPI)          |
                    +-------------+-------------+
                                  |
         +------------------------+------------------------+
         |                        |                        |
+--------+---------+     +--------+---------+     +--------+---------+
| Remediation      |     |   Edge Module    |     | Data Sources     |
| Module           |     |                  |     |                  |
| - Runbook Lib    |     | - Agent Manager  |     | - VictoriaMetrics|
| - Executor       |     | - Processor      |     | - OpenSearch     |
| - Approval Flow  |     | - Buffer Manager |     | - OpenObserve    |
+------------------+     | - Sync Manager   |     +------------------+
                         +------------------+
```

---

## Best Practices

### NLP Queries
- Be specific about equipment names and time ranges
- Use natural language, no need for technical syntax
- Available in both French and English

### RCA Analysis
- Provide as much context as possible about the incident
- Include all affected equipment for better correlation
- Review causal graphs to understand failure chains

### Predictive Maintenance
- Monitor equipment with historical data for better predictions
- Set appropriate anomaly sensitivity for your environment
- Review RUL predictions regularly and adjust maintenance schedules

### Auto-Remediation
- Always start with `dry_run: true` to validate runbooks
- Require approval for production environments
- Create custom runbooks for your specific equipment

### Edge Computing
- Choose processing mode based on bandwidth constraints
- Monitor buffer usage to avoid data loss
- Configure appropriate sync intervals for your network

---

## Troubleshooting

### Modules Not Loading
```bash
# Check module status
curl http://localhost:8085/api/modules/status

# Check logs
docker logs oovmtel-unified-view
```

### NLP Not Understanding Queries
- Check language parameter matches your query language
- Be more specific about equipment names
- Use simpler sentence structure

### RCA Not Finding Root Cause
- Ensure sufficient historical data is available
- Check that metric names are correctly mapped
- Increase analysis time window

### Predictions Not Accurate
- Verify equipment has enough historical data (minimum 7 days)
- Adjust anomaly sensitivity threshold
- Check for data gaps in time series

---

## API Reference Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Natural language query |
| `/api/rca/analyze` | POST | Analyze incident root cause |
| `/api/rca/detect` | POST | Detect anomalies |
| `/api/predictive/analyze` | GET | Full predictive analysis |
| `/api/predictive/health` | GET | Equipment health scores |
| `/api/predictive/alerts` | GET | Predictive alerts |
| `/api/remediation/runbooks` | GET | List runbooks |
| `/api/remediation/execute` | POST | Execute remediation |
| `/api/remediation/pending` | GET | Pending approvals |
| `/api/remediation/approve/{id}` | POST | Approve/reject action |
| `/api/remediation/history` | GET | Execution history |
| `/api/remediation/stats` | GET | Remediation statistics |
| `/api/edge/register` | POST | Register edge agent |
| `/api/edge/agents` | GET | List edge agents |
| `/api/edge/agents/{id}` | GET | Get agent status |
| `/api/edge/data` | POST | Receive edge data |
| `/api/edge/alerts` | POST | Receive edge alerts |
| `/api/modules/status` | GET | Module status |
