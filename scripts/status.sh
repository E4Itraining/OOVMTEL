#!/bin/bash
# =============================================================================
# OOVMTEL Platform Status Script
# Automatically detects and shows status for the running architecture
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ARCHITECTURE_FILE="$PROJECT_DIR/.oovmtel-architecture"

cd "$PROJECT_DIR"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# Detect Architecture
# =============================================================================

detect_architecture() {
    if [ -f "$ARCHITECTURE_FILE" ]; then
        ARCHITECTURE=$(cat "$ARCHITECTURE_FILE")
        return
    fi

    # Detect based on running containers
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "oovmtel-kafka-ot"; then
        ARCHITECTURE="secure"
    elif docker ps --format '{{.Names}}' 2>/dev/null | grep -q "oovmtel-otel-ot-gateway"; then
        ARCHITECTURE="direct-otlp"
    elif docker ps --format '{{.Names}}' 2>/dev/null | grep -q "oovmtel-kafka\$"; then
        ARCHITECTURE="simple"
    else
        ARCHITECTURE="unknown"
    fi
}

# =============================================================================
# Health Check Functions
# =============================================================================

check_service() {
    local name=$1
    local url=$2
    local expected=${3:-"200"}

    local status_code
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [[ "$status_code" =~ ^($expected|204)$ ]]; then
        echo -e "  ${GREEN}[OK]${NC} $name"
        return 0
    else
        echo -e "  ${RED}[FAIL]${NC} $name (HTTP $status_code)"
        return 1
    fi
}

check_port() {
    local name=$1
    local port=$2

    if nc -z localhost $port 2>/dev/null; then
        echo -e "  ${GREEN}[OK]${NC} $name (port $port)"
        return 0
    else
        echo -e "  ${RED}[FAIL]${NC} $name (port $port not responding)"
        return 1
    fi
}

# =============================================================================
# Status Functions by Architecture
# =============================================================================

status_simple() {
    echo -e "\n${BLUE}Container Status:${NC}"
    docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  No containers running"

    echo -e "\n${BLUE}Service Health Checks:${NC}"
    check_port "Kafka" 9092
    check_service "Victoria Metrics" "http://localhost:8428/health"
    check_service "OpenObserve" "http://localhost:5080/healthz"
    check_service "OpenSearch" "http://localhost:9200/_cluster/health"
    check_service "Grafana" "http://localhost:3000/api/health"
    check_service "OTEL Collector" "http://localhost:13133/health"

    echo -e "\n${BLUE}Kafka Topics:${NC}"
    docker compose exec -T kafka kafka-topics --bootstrap-server localhost:9092 --list 2>/dev/null || echo "  Kafka not available"
}

status_secure() {
    echo -e "\n${BLUE}=== Zone OT ===${NC}"
    docker compose -f docker-compose.ot.yml ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || echo "  No OT containers"

    echo -e "\n${BLUE}=== Zone IT ===${NC}"
    docker compose -f docker-compose.it.yml ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || echo "  No IT containers"

    echo -e "\n${BLUE}=== Zone DMZ ===${NC}"
    docker compose -f docker-compose.dmz.yml ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || echo "  No DMZ containers"

    echo -e "\n${BLUE}Service Health Checks:${NC}"
    echo -e "${YELLOW}Zone OT:${NC}"
    check_port "Kafka OT" 29092
    check_service "OTEL Collector OT" "http://localhost:14319/health" || true

    echo -e "${YELLOW}Zone IT:${NC}"
    check_port "Kafka IT" 9092
    check_service "Victoria Metrics" "http://localhost:8428/health"
    check_service "OpenObserve" "http://localhost:5080/healthz"
    check_service "OpenSearch" "http://localhost:9200/_cluster/health"
    check_service "Grafana" "http://localhost:3000/api/health"

    echo -e "\n${BLUE}DMZ Network Status:${NC}"
    if docker network ls | grep -q "oovmtel_dmz-network"; then
        echo -e "  ${GREEN}[OK]${NC} DMZ network exists"
        docker network inspect oovmtel_dmz-network --format '{{range .Containers}}  - {{.Name}}{{"\n"}}{{end}}' 2>/dev/null || true
    else
        echo -e "  ${RED}[FAIL]${NC} DMZ network not found"
    fi

    echo -e "\n${BLUE}Kafka Topics (IT Zone):${NC}"
    docker exec oovmtel-kafka-it-1 kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null || echo "  Kafka IT not available"

    echo -e "\n${BLUE}Data Diode Verification:${NC}"
    OT_TOPICS=$(docker exec oovmtel-kafka-it-1 kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null | grep -c "^ot-" || echo "0")
    IT_TOPICS=$(docker exec oovmtel-kafka-it-1 kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null | grep -c "^it-" || echo "0")
    echo "  OT topics in IT zone: $OT_TOPICS (should be 0)"
    echo "  IT topics (mirrored): $IT_TOPICS"
}

status_direct_otlp() {
    echo -e "\n${BLUE}Container Status:${NC}"
    docker compose -f docker-compose.direct-otlp.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  No containers running"

    echo -e "\n${BLUE}Service Health Checks:${NC}"
    check_service "Victoria Metrics" "http://localhost:8428/health"
    check_service "OpenObserve" "http://localhost:5080/healthz"
    check_service "OpenSearch" "http://localhost:9200/_cluster/health"
    check_service "Grafana" "http://localhost:3000/api/health"
    check_service "OTEL Gateway" "http://localhost:13133/health"
}

# =============================================================================
# Main
# =============================================================================

echo -e "${BLUE}"
echo "=============================================="
echo "  OOVMTEL Platform Status"
echo "=============================================="
echo -e "${NC}"

detect_architecture

echo -e "Architecture: ${GREEN}$ARCHITECTURE${NC}"

case "$ARCHITECTURE" in
    simple)
        status_simple
        ;;
    secure)
        status_secure
        ;;
    direct-otlp)
        status_direct_otlp
        ;;
    unknown)
        echo -e "\n${YELLOW}No OOVMTEL architecture detected.${NC}"
        echo "Run ./scripts/start.sh [simple|secure|direct-otlp] to start the platform."
        ;;
esac

echo -e "\n${BLUE}Disk Usage:${NC}"
docker system df --format "table {{.Type}}\t{{.Size}}\t{{.Active}}" 2>/dev/null || echo "  Unable to get disk usage"
