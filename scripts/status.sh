#!/bin/bash
# =============================================================================
# OOVMTEL Platform Status Script
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=============================================="
echo "  OOVMTEL Platform Status"
echo "=============================================="
echo ""

# Function to check service health
check_service() {
    local name=$1
    local url=$2
    local status

    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|204"; then
        echo -e "  ${GREEN}✓${NC} $name"
        return 0
    else
        echo -e "  ${RED}✗${NC} $name"
        return 1
    fi
}

echo "Container Status:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "Service Health Checks:"

check_service "Kafka" "http://localhost:9093" 2>/dev/null || true
check_service "Victoria Metrics" "http://localhost:8428/health" 2>/dev/null || true
check_service "OpenObserve" "http://localhost:5080/healthz" 2>/dev/null || true
check_service "OpenSearch" "http://localhost:9200/_cluster/health" 2>/dev/null || true
check_service "Grafana" "http://localhost:3000/api/health" 2>/dev/null || true
check_service "OTEL Collector" "http://localhost:13133/health" 2>/dev/null || true

echo ""
echo "Kafka Topics:"
docker compose exec -T kafka kafka-topics --bootstrap-server localhost:9092 --list 2>/dev/null || echo "  Kafka not available"

echo ""
echo "Disk Usage:"
docker system df --format "table {{.Type}}\t{{.Size}}\t{{.Active}}"
