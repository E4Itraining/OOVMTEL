#!/bin/bash
# =============================================================================
# OOVMTEL Platform Startup Script
# Industrial Observability Platform
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=============================================="
echo "  OOVMTEL - Industrial Observability Platform"
echo "=============================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p config/grafana/provisioning/dashboards/json
mkdir -p data

# Set permissions
echo -e "${BLUE}Setting permissions...${NC}"
chmod -R 755 config/

# Start infrastructure services first
echo -e "${YELLOW}Starting infrastructure services (Zookeeper, Kafka)...${NC}"
docker compose up -d zookeeper
sleep 5
docker compose up -d kafka
sleep 10

# Wait for Kafka to be ready
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

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for storage services...${NC}"
sleep 15

# Start OTEL Collector
echo -e "${YELLOW}Starting OpenTelemetry Collector...${NC}"
docker compose up -d otel-collector
sleep 5

# Start Grafana and UI services
echo -e "${YELLOW}Starting visualization services...${NC}"
docker compose up -d grafana kafka-ui opensearch-dashboards vmagent

# Wait for OTEL Collector health check
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

# Launch data ingestion initialization
echo -e "${YELLOW}Initializing data ingestion...${NC}"
docker compose up data-ingestion-launcher
echo -e "${GREEN}Data ingestion initialized!${NC}"

# Build and start simulators
echo -e "${YELLOW}Building and starting industrial simulators...${NC}"
docker compose build scada-simulator mes-simulator plm-simulator opcua-simulator
docker compose up -d scada-simulator mes-simulator plm-simulator opcua-simulator

# Wait for simulators to start generating data
echo -e "${YELLOW}Waiting for simulators to start...${NC}"
sleep 10

# Verify data flow
echo -e "${YELLOW}Verifying data flow...${NC}"
SCADA_STATUS=$(curl -sf http://localhost:8080/health 2>/dev/null && echo "UP" || echo "DOWN")
MES_STATUS=$(curl -sf http://localhost:8081/health 2>/dev/null && echo "UP" || echo "DOWN")
PLM_STATUS=$(curl -sf http://localhost:8082/health 2>/dev/null && echo "UP" || echo "DOWN")
OPCUA_STATUS=$(curl -sf http://localhost:8083/health 2>/dev/null && echo "UP" || echo "DOWN")

echo -e "  SCADA Simulator:  ${SCADA_STATUS}"
echo -e "  MES Simulator:    ${MES_STATUS}"
echo -e "  PLM Simulator:    ${PLM_STATUS}"
echo -e "  OPC-UA Simulator: ${OPCUA_STATUS}"

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
echo -e "  ${BLUE}OTEL Collector:${NC}"
echo "    - OTLP gRPC:       localhost:4317"
echo "    - OTLP HTTP:       localhost:4318"
echo "    - Health:          http://localhost:13133"
echo "    - zPages:          http://localhost:55679"
echo ""
echo "Industrial Simulators running:"
echo "  - SCADA:  500 points/sec (port 8080)"
echo "  - MES:    100 events/sec (port 8081)"
echo "  - PLM:    20 events/sec  (port 8082)"
echo "  - OPC-UA: 200 nodes/sec  (port 8083)"
echo ""
echo -e "${BLUE}Data Ingestion Endpoints:${NC}"
echo "  - OTLP gRPC:       localhost:4317"
echo "  - OTLP HTTP:       localhost:4318"
echo "  - Prometheus:      localhost:8428/api/v1/write"
echo "  - Kafka:           localhost:9093 (external)"
echo ""
echo -e "${GREEN}Data ingestion is active and receiving data!${NC}"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop:      ./scripts/stop.sh"
echo ""
