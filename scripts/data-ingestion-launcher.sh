#!/bin/bash
# =============================================================================
# OOVMTEL Data Ingestion Launcher
# Ensures all services are ready and initializes data flow at launch
# =============================================================================

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
MAX_RETRIES=${MAX_RETRIES:-60}
RETRY_INTERVAL=${RETRY_INTERVAL:-5}
KAFKA_ENABLED=${KAFKA_ENABLED:-false}
KAFKA_BOOTSTRAP=${KAFKA_BOOTSTRAP_SERVERS:-kafka:9092}
VICTORIA_METRICS_URL=${VICTORIA_METRICS_URL:-http://victoria-metrics:8428}
OPENSEARCH_URL=${OPENSEARCH_URL:-http://opensearch:9200}
OPENOBSERVE_URL=${OPENOBSERVE_URL:-http://openobserve:5080}
OTEL_COLLECTOR_URL=${OTEL_COLLECTOR_URL:-http://otel-collector:13133}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_header() {
    echo ""
    echo -e "${CYAN}=============================================="
    echo "  $1"
    echo -e "==============================================${NC}"
    echo ""
}

# =============================================================================
# Service Health Checks
# =============================================================================

wait_for_kafka() {
    log_info "Waiting for Kafka to be ready..."
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        if kafka-topics --bootstrap-server "$KAFKA_BOOTSTRAP" --list &>/dev/null; then
            log_success "Kafka is ready!"
            return 0
        fi
        retries=$((retries + 1))
        log_info "Kafka not ready yet... ($retries/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
    done

    log_error "Kafka failed to become ready"
    return 1
}

wait_for_victoria_metrics() {
    log_info "Waiting for VictoriaMetrics to be ready..."
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -sf "${VICTORIA_METRICS_URL}/health" &>/dev/null; then
            log_success "VictoriaMetrics is ready!"
            return 0
        fi
        retries=$((retries + 1))
        log_info "VictoriaMetrics not ready yet... ($retries/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
    done

    log_error "VictoriaMetrics failed to become ready"
    return 1
}

wait_for_opensearch() {
    log_info "Waiting for OpenSearch to be ready..."
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -sf "${OPENSEARCH_URL}/_cluster/health" | grep -q '"status":"green"\|"status":"yellow"'; then
            log_success "OpenSearch is ready!"
            return 0
        fi
        retries=$((retries + 1))
        log_info "OpenSearch not ready yet... ($retries/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
    done

    log_error "OpenSearch failed to become ready"
    return 1
}

wait_for_openobserve() {
    log_info "Waiting for OpenObserve to be ready..."
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -sf "${OPENOBSERVE_URL}/healthz" &>/dev/null; then
            log_success "OpenObserve is ready!"
            return 0
        fi
        retries=$((retries + 1))
        log_info "OpenObserve not ready yet... ($retries/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
    done

    log_error "OpenObserve failed to become ready"
    return 1
}

wait_for_otel_collector() {
    log_info "Waiting for OTEL Collector to be ready..."
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -sf "${OTEL_COLLECTOR_URL}/health" | grep -q "Server available"; then
            log_success "OTEL Collector is ready!"
            return 0
        fi
        retries=$((retries + 1))
        log_info "OTEL Collector not ready yet... ($retries/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
    done

    log_error "OTEL Collector failed to become ready"
    return 1
}

# =============================================================================
# Kafka Topics Verification
# =============================================================================

verify_kafka_topics() {
    log_info "Verifying Kafka topics..."

    local required_topics=(
        "scada-metrics"
        "mes-events"
        "plm-data"
        "opcua-nodes"
        "industrial-telemetry"
        "processed-telemetry"
    )

    local existing_topics
    existing_topics=$(kafka-topics --bootstrap-server "$KAFKA_BOOTSTRAP" --list 2>/dev/null)

    local all_present=true
    for topic in "${required_topics[@]}"; do
        if echo "$existing_topics" | grep -q "^${topic}$"; then
            log_success "Topic '$topic' exists"
        else
            log_warn "Topic '$topic' not found - creating..."
            create_kafka_topic "$topic"
        fi
    done

    log_success "All Kafka topics verified!"
    return 0
}

create_kafka_topic() {
    local topic=$1
    local partitions=8
    local retention_ms=86400000

    # Set partitions based on topic
    case $topic in
        "scada-metrics"|"industrial-telemetry")
            partitions=12
            ;;
        "plm-data"|"processed-telemetry")
            partitions=6
            retention_ms=172800000
            ;;
    esac

    kafka-topics --create --if-not-exists \
        --topic "$topic" \
        --bootstrap-server "$KAFKA_BOOTSTRAP" \
        --partitions "$partitions" \
        --replication-factor 1 \
        --config retention.ms=$retention_ms \
        --config compression.type=lz4 2>/dev/null

    if [ $? -eq 0 ]; then
        log_success "Created topic '$topic'"
    else
        log_error "Failed to create topic '$topic'"
    fi
}

# =============================================================================
# Data Flow Initialization
# =============================================================================

initialize_opensearch_indices() {
    log_info "Initializing OpenSearch indices..."

    # Create industrial logs index template
    curl -sf -X PUT "${OPENSEARCH_URL}/_index_template/industrial-logs" \
        -H 'Content-Type: application/json' \
        -d '{
            "index_patterns": ["industrial-logs-*"],
            "template": {
                "settings": {
                    "number_of_shards": 3,
                    "number_of_replicas": 0,
                    "index.refresh_interval": "5s"
                },
                "mappings": {
                    "properties": {
                        "@timestamp": { "type": "date" },
                        "level": { "type": "keyword" },
                        "source": { "type": "keyword" },
                        "area": { "type": "keyword" },
                        "equipment_id": { "type": "keyword" },
                        "message": { "type": "text" }
                    }
                }
            }
        }' &>/dev/null

    # Create industrial traces index template
    curl -sf -X PUT "${OPENSEARCH_URL}/_index_template/industrial-traces" \
        -H 'Content-Type: application/json' \
        -d '{
            "index_patterns": ["industrial-traces-*"],
            "template": {
                "settings": {
                    "number_of_shards": 3,
                    "number_of_replicas": 0
                },
                "mappings": {
                    "properties": {
                        "@timestamp": { "type": "date" },
                        "traceId": { "type": "keyword" },
                        "spanId": { "type": "keyword" },
                        "parentSpanId": { "type": "keyword" },
                        "serviceName": { "type": "keyword" },
                        "operationName": { "type": "keyword" },
                        "duration": { "type": "long" }
                    }
                }
            }
        }' &>/dev/null

    log_success "OpenSearch indices initialized!"
}

send_test_metric() {
    log_info "Sending test metric to VictoriaMetrics..."

    local timestamp=$(date +%s)000
    local test_data="data_ingestion_status,service=launcher,status=initialized value=1 ${timestamp}"

    if curl -sf -X POST "${VICTORIA_METRICS_URL}/api/v1/import/prometheus" \
        --data-binary "$test_data" &>/dev/null; then
        log_success "Test metric sent to VictoriaMetrics"
        return 0
    else
        log_warn "Could not send test metric to VictoriaMetrics"
        return 1
    fi
}

send_test_kafka_message() {
    log_info "Sending test message to Kafka..."

    local test_message='{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","source":"data-ingestion-launcher","status":"initialized","message":"Data ingestion launcher test"}'

    if echo "$test_message" | kafka-console-producer \
        --bootstrap-server "$KAFKA_BOOTSTRAP" \
        --topic "industrial-telemetry" &>/dev/null; then
        log_success "Test message sent to Kafka"
        return 0
    else
        log_warn "Could not send test message to Kafka"
        return 1
    fi
}

# =============================================================================
# Data Flow Verification
# =============================================================================

verify_data_flow() {
    log_info "Verifying data flow..."

    local check_count=0
    local success_count=0

    # Check VictoriaMetrics metrics count
    check_count=$((check_count + 1))
    local vm_series
    vm_series=$(curl -sf "${VICTORIA_METRICS_URL}/api/v1/status/tsdb" 2>/dev/null | grep -o '"totalSeries":[0-9]*' | grep -o '[0-9]*' || echo "0")
    if [ "${vm_series:-0}" -gt 0 ]; then
        log_success "VictoriaMetrics has $vm_series time series"
        success_count=$((success_count + 1))
    else
        log_info "VictoriaMetrics has no series yet (will populate after simulators start)"
    fi

    # Check OpenSearch cluster status
    check_count=$((check_count + 1))
    local os_status
    os_status=$(curl -sf "${OPENSEARCH_URL}/_cluster/health" 2>/dev/null | grep -o '"status":"[a-z]*"' | cut -d'"' -f4 || echo "unknown")
    if [ "$os_status" = "green" ] || [ "$os_status" = "yellow" ]; then
        log_success "OpenSearch cluster status: $os_status"
        success_count=$((success_count + 1))
    else
        log_warn "OpenSearch cluster status: $os_status"
    fi

    # Check Kafka consumer groups (only if Kafka is enabled)
    if [ "$KAFKA_ENABLED" = "true" ]; then
        check_count=$((check_count + 1))
        if kafka-consumer-groups --bootstrap-server "$KAFKA_BOOTSTRAP" --list &>/dev/null; then
            log_success "Kafka consumer groups accessible"
            success_count=$((success_count + 1))
        else
            log_warn "Could not list Kafka consumer groups"
        fi
    fi

    # Check OTEL Collector pipelines
    check_count=$((check_count + 1))
    if curl -sf "http://otel-collector:8888/metrics" 2>/dev/null | grep -q "otelcol_receiver"; then
        log_success "OTEL Collector receivers are active"
        success_count=$((success_count + 1))
    else
        log_info "OTEL Collector receivers not yet reporting metrics"
    fi

    log_info "Data flow verification: $success_count/$check_count checks passed"
    return 0
}

# =============================================================================
# Status Report
# =============================================================================

generate_status_report() {
    log_header "DATA INGESTION STATUS REPORT"

    echo -e "${CYAN}Services Status:${NC}"
    if [ "$KAFKA_ENABLED" = "true" ]; then
        echo "  - Kafka:           $(check_service_status kafka)"
    fi
    echo "  - VictoriaMetrics: $(check_service_status victoria-metrics)"
    echo "  - OpenSearch:      $(check_service_status opensearch)"
    echo "  - OpenObserve:     $(check_service_status openobserve)"
    echo "  - OTEL Collector:  $(check_service_status otel-collector)"
    echo ""

    if [ "$KAFKA_ENABLED" = "true" ]; then
        echo -e "${CYAN}Kafka Topics:${NC}"
        kafka-topics --bootstrap-server "$KAFKA_BOOTSTRAP" --list 2>/dev/null | while read -r topic; do
            local partitions
            partitions=$(kafka-topics --bootstrap-server "$KAFKA_BOOTSTRAP" --describe --topic "$topic" 2>/dev/null | grep -c "Partition:" || echo "?")
            echo "  - $topic (partitions: $partitions)"
        done
        echo ""
    fi

    echo -e "${CYAN}Data Ingestion Endpoints:${NC}"
    echo "  - OTLP gRPC:       otel-collector:4317"
    echo "  - OTLP HTTP:       otel-collector:4318"
    echo "  - Prometheus:      victoria-metrics:8428"
    echo "  - OpenSearch:      opensearch:9200"
    if [ "$KAFKA_ENABLED" = "true" ]; then
        echo "  - Kafka:           kafka:9092"
    fi
    echo ""

    echo -e "${GREEN}Data ingestion is ready to receive data!${NC}"
    echo ""
}

check_service_status() {
    local service=$1
    case $service in
        kafka)
            if kafka-topics --bootstrap-server "$KAFKA_BOOTSTRAP" --list &>/dev/null; then
                echo -e "${GREEN}READY${NC}"
            else
                echo -e "${RED}NOT READY${NC}"
            fi
            ;;
        victoria-metrics)
            if curl -sf "${VICTORIA_METRICS_URL}/health" &>/dev/null; then
                echo -e "${GREEN}READY${NC}"
            else
                echo -e "${RED}NOT READY${NC}"
            fi
            ;;
        opensearch)
            if curl -sf "${OPENSEARCH_URL}/_cluster/health" &>/dev/null; then
                echo -e "${GREEN}READY${NC}"
            else
                echo -e "${RED}NOT READY${NC}"
            fi
            ;;
        openobserve)
            if curl -sf "${OPENOBSERVE_URL}/healthz" &>/dev/null; then
                echo -e "${GREEN}READY${NC}"
            else
                echo -e "${RED}NOT READY${NC}"
            fi
            ;;
        otel-collector)
            if curl -sf "${OTEL_COLLECTOR_URL}/health" &>/dev/null; then
                echo -e "${GREEN}READY${NC}"
            else
                echo -e "${RED}NOT READY${NC}"
            fi
            ;;
    esac
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    log_header "OOVMTEL Data Ingestion Launcher"

    log_info "Starting data ingestion initialization..."
    log_info "Configuration:"
    log_info "  - Kafka Enabled: $KAFKA_ENABLED"
    if [ "$KAFKA_ENABLED" = "true" ]; then
        log_info "  - Kafka: $KAFKA_BOOTSTRAP"
    fi
    log_info "  - VictoriaMetrics: $VICTORIA_METRICS_URL"
    log_info "  - OpenSearch: $OPENSEARCH_URL"
    log_info "  - OpenObserve: $OPENOBSERVE_URL"
    log_info "  - OTEL Collector: $OTEL_COLLECTOR_URL"
    echo ""

    # Phase 1: Wait for all services
    log_header "Phase 1: Service Health Checks"

    if [ "$KAFKA_ENABLED" = "true" ]; then
        wait_for_kafka || exit 1
    else
        log_info "Kafka disabled - skipping Kafka health check"
    fi
    wait_for_victoria_metrics || exit 1
    wait_for_opensearch || exit 1
    wait_for_openobserve || exit 1
    wait_for_otel_collector || exit 1

    log_success "All services are healthy!"

    # Phase 2: Verify/Create Kafka topics (only if Kafka is enabled)
    if [ "$KAFKA_ENABLED" = "true" ]; then
        log_header "Phase 2: Kafka Topics Verification"
        verify_kafka_topics
    else
        log_info "Kafka disabled - skipping topic verification"
    fi

    # Phase 3: Initialize data stores
    log_header "Phase 3: Data Store Initialization"
    initialize_opensearch_indices
    send_test_metric
    if [ "$KAFKA_ENABLED" = "true" ]; then
        send_test_kafka_message
    fi

    # Phase 4: Verify data flow
    log_header "Phase 4: Data Flow Verification"
    verify_data_flow

    # Phase 5: Generate status report
    generate_status_report

    log_success "Data ingestion initialization complete!"
    log_info "Simulators can now start sending data."

    # Keep container running if needed (for health checks)
    if [ "${KEEP_RUNNING:-false}" = "true" ]; then
        log_info "Keeping container running for health checks..."
        while true; do
            sleep 60
            verify_data_flow >/dev/null 2>&1
        done
    fi

    exit 0
}

# Run main function
main "$@"
