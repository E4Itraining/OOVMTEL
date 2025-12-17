#!/bin/bash
# =============================================================================
# OOVMTEL Platform Startup Script
# Industrial Observability Platform
# =============================================================================
# Usage: ./start.sh [simple|secure|direct-otlp]
#   simple      - Single network, Kafka-based (default)
#   secure      - IT/OT/DMZ zones with MirrorMaker 2 (IEC 62443 compliant)
#   direct-otlp - Direct OTLP pipeline without Kafka
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ARCHITECTURE="${1:-simple}"
ARCHITECTURE_FILE="$PROJECT_DIR/.oovmtel-architecture"

cd "$PROJECT_DIR"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Common Functions
# =============================================================================

check_prerequisites() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed${NC}"
        exit 1
    fi

    if ! command -v docker compose &> /dev/null; then
        echo -e "${RED}Error: Docker Compose is not installed${NC}"
        exit 1
    fi
}

create_directories() {
    echo -e "${BLUE}Creating directories...${NC}"
    mkdir -p config/grafana/provisioning/dashboards/json
    mkdir -p data
    chmod -R 755 config/
}

wait_for_service() {
    local service=$1
    local port=$2
    local max_attempts=${3:-30}
    local attempt=1

    echo -e "${YELLOW}Waiting for $service on port $port...${NC}"
    while ! nc -z localhost $port 2>/dev/null; do
        if [ $attempt -ge $max_attempts ]; then
            echo -e "${RED}Timeout waiting for $service${NC}"
            return 1
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    echo -e "${GREEN}$service is ready${NC}"
}

save_architecture() {
    echo "$ARCHITECTURE" > "$ARCHITECTURE_FILE"
}

# =============================================================================
# Simple Architecture (docker-compose.yml)
# =============================================================================

start_simple() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "  OOVMTEL - Simple Architecture"
    echo "  (Single network, Kafka-based)"
    echo "=============================================="
    echo -e "${NC}"

    # Start Kafka (KRaft mode)
    echo -e "${YELLOW}Starting Kafka (KRaft mode)...${NC}"
    docker compose up -d kafka
    sleep 15

    # Wait for Kafka
    echo -e "${YELLOW}Waiting for Kafka to be ready...${NC}"
    MAX_RETRIES=30
    RETRY_COUNT=0
    until docker compose exec -T kafka kafka-topics --bootstrap-server localhost:9092 --list &> /dev/null; do
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
            echo -e "${RED}Kafka failed to start in time${NC}"
            exit 1
        fi
        echo "Waiting for Kafka... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    done
    echo -e "${GREEN}Kafka is ready!${NC}"

    # Initialize Kafka topics
    echo -e "${YELLOW}Creating Kafka topics...${NC}"
    docker compose up kafka-init

    # Start storage services
    echo -e "${YELLOW}Starting storage services...${NC}"
    docker compose up -d victoria-metrics opensearch openobserve
    sleep 15

    # Start OTEL Collector
    echo -e "${YELLOW}Starting OpenTelemetry Collector...${NC}"
    docker compose up -d otel-collector
    sleep 5

    # Start Grafana and UI services
    echo -e "${YELLOW}Starting visualization services...${NC}"
    docker compose up -d grafana kafka-ui opensearch-dashboards vmagent

    # Wait for OTEL Collector
    echo -e "${YELLOW}Waiting for OTEL Collector to be ready...${NC}"
    RETRY_COUNT=0
    MAX_RETRIES=30
    until docker compose exec -T otel-collector wget -qO- http://localhost:13133/health 2>/dev/null | grep -q "Server available"; do
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
            echo -e "${YELLOW}OTEL Collector health check timed out, continuing...${NC}"
            break
        fi
        echo "Waiting for OTEL Collector... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    done
    echo -e "${GREEN}OTEL Collector is ready!${NC}"

    # Launch data ingestion
    echo -e "${YELLOW}Initializing data ingestion...${NC}"
    docker compose up data-ingestion-launcher
    echo -e "${GREEN}Data ingestion initialized!${NC}"

    # Build and start simulators
    echo -e "${YELLOW}Building and starting industrial simulators...${NC}"
    docker compose build scada-simulator mes-simulator plm-simulator opcua-simulator
    docker compose up -d scada-simulator mes-simulator plm-simulator opcua-simulator
    sleep 10

    print_simple_summary
}

print_simple_summary() {
    echo ""
    echo -e "${GREEN}=============================================="
    echo "  OOVMTEL Platform Started Successfully!"
    echo "==============================================${NC}"
    echo ""
    echo "Access the following services:"
    echo ""
    echo -e "  ${BLUE}Grafana:${NC}              http://localhost:3000"
    echo "                        (admin / admin123)"
    echo ""
    echo -e "  ${BLUE}Victoria Metrics:${NC}     http://localhost:8428"
    echo ""
    echo -e "  ${BLUE}OpenObserve:${NC}          http://localhost:5080"
    echo "                        (root@example.com / Complexpass#123)"
    echo ""
    echo -e "  ${BLUE}OpenSearch Dashboards:${NC} http://localhost:5601"
    echo ""
    echo -e "  ${BLUE}Kafka UI:${NC}             http://localhost:8090"
    echo ""
    echo "To view logs: docker compose logs -f"
    echo "To stop:      ./scripts/stop.sh"
    echo ""
}

# =============================================================================
# Secure IT/OT/DMZ Architecture
# =============================================================================

start_secure() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "  OOVMTEL - Secure IT/OT Architecture"
    echo "  IEC 62443 / NIS2 Compliant"
    echo "=============================================="
    echo -e "${NC}"

    # Phase 1: Start Zone OT
    echo -e "\n${BLUE}--- PHASE 1: Starting Zone OT ---${NC}"
    echo -e "${YELLOW}Building OT simulators...${NC}"
    docker compose -f docker-compose.ot.yml build --quiet

    echo -e "${YELLOW}Starting OT services...${NC}"
    docker compose -f docker-compose.ot.yml up -d --remove-orphans

    echo -e "${YELLOW}Waiting for Kafka OT...${NC}"
    sleep 10
    wait_for_service "Kafka OT" 29092 60

    echo -e "${GREEN}Zone OT started successfully${NC}"

    # Phase 2: Create DMZ Network
    echo -e "\n${BLUE}--- PHASE 2: Setting up DMZ Network ---${NC}"
    if ! docker network ls | grep -q "oovmtel_dmz-network"; then
        echo -e "${YELLOW}Creating DMZ network...${NC}"
        docker network create --driver bridge --subnet 172.30.0.0/24 oovmtel_dmz-network
    fi

    echo -e "${YELLOW}Connecting OT Kafka to DMZ network...${NC}"
    docker network connect oovmtel_dmz-network oovmtel-kafka-ot 2>/dev/null || true
    echo -e "${GREEN}DMZ network ready${NC}"

    # Phase 3: Start Zone IT
    echo -e "\n${BLUE}--- PHASE 3: Starting Zone IT ---${NC}"
    echo -e "${YELLOW}Starting IT services...${NC}"
    docker compose -f docker-compose.it.yml up -d --remove-orphans
    sleep 15

    wait_for_service "Kafka IT" 9092 60
    wait_for_service "VictoriaMetrics" 8428 60
    wait_for_service "OpenSearch" 9200 90
    wait_for_service "Grafana" 3000 60

    echo -e "${GREEN}Zone IT started successfully${NC}"

    # Phase 4: Start DMZ Services
    echo -e "\n${BLUE}--- PHASE 4: Starting DMZ Services ---${NC}"
    echo -e "${YELLOW}Connecting IT Kafka to DMZ network...${NC}"
    docker network connect oovmtel_dmz-network oovmtel-kafka-it-1 2>/dev/null || true

    echo -e "${YELLOW}Starting DMZ services (MirrorMaker 2)...${NC}"
    docker compose -f docker-compose.dmz.yml up -d --remove-orphans

    echo -e "${GREEN}DMZ services started${NC}"

    # Verification
    echo -e "\n${BLUE}--- VERIFICATION ---${NC}"
    sleep 5
    OT_TOPICS_IN_IT=$(docker exec oovmtel-kafka-it-1 kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null | grep -c "^ot-" || echo "0")

    if [ "$OT_TOPICS_IN_IT" -eq 0 ]; then
        echo -e "${GREEN}Data diode integrity verified - No raw OT topics in IT zone${NC}"
    else
        echo -e "${YELLOW}Warning: Found $OT_TOPICS_IN_IT OT topics in IT zone${NC}"
    fi

    print_secure_summary
}

print_secure_summary() {
    echo -e "\n${GREEN}"
    echo "=============================================="
    echo "  OOVMTEL Secure Architecture Started"
    echo "=============================================="
    echo -e "${NC}"
    echo ""
    echo "Zone OT (172.29.0.0/24):"
    echo "  - Kafka OT:        localhost:29093 (external)"
    echo "  - OTel Collector:  localhost:4319 (gRPC), 4320 (HTTP)"
    echo "  - Simulators:      localhost:8080-8083"
    echo ""
    echo "Zone DMZ (172.30.0.0/24):"
    echo "  - MirrorMaker 2:   OT->IT replication (UNIDIRECTIONAL)"
    echo ""
    echo "Zone IT (172.31.0.0/16):"
    echo "  - Kafka IT:        localhost:9092"
    echo "  - VictoriaMetrics: localhost:8428"
    echo "  - OpenObserve:     localhost:5080"
    echo "  - OpenSearch:      localhost:9200"
    echo "  - Grafana:         localhost:3000"
    echo ""
    echo "To view logs:"
    echo "  docker compose -f docker-compose.ot.yml logs -f"
    echo "  docker compose -f docker-compose.it.yml logs -f"
    echo "  docker compose -f docker-compose.dmz.yml logs -f"
    echo ""
    echo "To stop: ./scripts/stop.sh"
    echo ""
}

# =============================================================================
# Direct OTLP Architecture (without Kafka)
# =============================================================================

start_direct_otlp() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "  OOVMTEL - Direct OTLP Architecture"
    echo "  (File-based buffering, no Kafka)"
    echo "=============================================="
    echo -e "${NC}"

    # Build simulators
    echo -e "${YELLOW}Building simulators...${NC}"
    docker compose -f docker-compose.direct-otlp.yml build --quiet

    # Start all services
    echo -e "${YELLOW}Starting all services...${NC}"
    docker compose -f docker-compose.direct-otlp.yml up -d --remove-orphans

    # Wait for services
    sleep 15
    wait_for_service "VictoriaMetrics" 8428 60
    wait_for_service "OpenSearch" 9200 90
    wait_for_service "Grafana" 3000 60

    echo -e "${GREEN}Direct OTLP architecture started${NC}"

    print_direct_otlp_summary
}

print_direct_otlp_summary() {
    echo -e "\n${GREEN}"
    echo "=============================================="
    echo "  OOVMTEL Direct OTLP Architecture Started"
    echo "=============================================="
    echo -e "${NC}"
    echo ""
    echo "Services:"
    echo "  - VictoriaMetrics: localhost:8428"
    echo "  - OpenObserve:     localhost:5080"
    echo "  - OpenSearch:      localhost:9200"
    echo "  - Grafana:         localhost:3000"
    echo "  - OTel Collector:  localhost:4317 (gRPC), 4318 (HTTP)"
    echo ""
    echo "To view logs: docker compose -f docker-compose.direct-otlp.yml logs -f"
    echo "To stop:      ./scripts/stop.sh"
    echo ""
}

# =============================================================================
# Main
# =============================================================================

show_usage() {
    echo "Usage: $0 [simple|secure|direct-otlp]"
    echo ""
    echo "Architectures:"
    echo "  simple      - Single network with Kafka (default)"
    echo "  secure      - IT/OT/DMZ zones with MirrorMaker 2"
    echo "  direct-otlp - Direct OTLP pipeline without Kafka"
    echo ""
}

# Validate architecture argument
case "$ARCHITECTURE" in
    simple|secure|direct-otlp)
        ;;
    -h|--help)
        show_usage
        exit 0
        ;;
    *)
        echo -e "${RED}Error: Unknown architecture '$ARCHITECTURE'${NC}"
        show_usage
        exit 1
        ;;
esac

# Check prerequisites
check_prerequisites

# Create directories
create_directories

# Save architecture choice
save_architecture

# Start selected architecture
case "$ARCHITECTURE" in
    simple)
        start_simple
        ;;
    secure)
        start_secure
        ;;
    direct-otlp)
        start_direct_otlp
        ;;
esac

echo -e "${GREEN}Architecture '$ARCHITECTURE' is running.${NC}"
echo -e "Run ${BLUE}./scripts/status.sh${NC} to check service status."
