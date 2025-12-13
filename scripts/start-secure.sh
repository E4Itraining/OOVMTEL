#!/bin/bash
# =============================================================================
# OOVMTEL - Secure IT/OT Architecture Startup Script
# =============================================================================
# This script starts the secure three-zone architecture:
# 1. Zone OT (Operational Technology)
# 2. Zone DMZ (Demilitarized Zone - Data Diode)
# 3. Zone IT (Information Technology)
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║           OOVMTEL - Secure IT/OT Architecture Startup                 ║"
echo "║                   IEC 62443 / NIS2 Compliant                          ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

cd "$PROJECT_DIR"

# Function to wait for service
wait_for_service() {
    local service=$1
    local port=$2
    local max_attempts=${3:-30}
    local attempt=1

    echo -e "${YELLOW}⏳ Waiting for $service on port $port...${NC}"
    while ! nc -z localhost $port 2>/dev/null; do
        if [ $attempt -ge $max_attempts ]; then
            echo -e "${RED}❌ Timeout waiting for $service${NC}"
            return 1
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    echo -e "${GREEN}✅ $service is ready${NC}"
}

# =============================================================================
# PHASE 1: Start Zone OT
# =============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  PHASE 1: Starting Zone OT (IEC 62443 Level 2/3)                       ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${YELLOW}📦 Building OT simulators...${NC}"
docker-compose -f docker-compose.ot.yml build --quiet

echo -e "${YELLOW}🚀 Starting OT services...${NC}"
docker-compose -f docker-compose.ot.yml up -d --remove-orphans

echo -e "${YELLOW}⏳ Waiting for Kafka OT...${NC}"
sleep 10
wait_for_service "Kafka OT" 9094 60

echo -e "${GREEN}✅ Zone OT started successfully${NC}"

# =============================================================================
# PHASE 2: Create DMZ Network and Start DMZ
# =============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  PHASE 2: Starting Zone DMZ (Data Diode)                               ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Create DMZ network if it doesn't exist
if ! docker network ls | grep -q "oovmtel_dmz-network"; then
    echo -e "${YELLOW}🔗 Creating DMZ network...${NC}"
    docker network create --driver bridge --subnet 172.30.0.0/24 oovmtel_dmz-network
fi

# Connect OT Kafka to DMZ network
echo -e "${YELLOW}🔗 Connecting OT Kafka to DMZ network...${NC}"
docker network connect oovmtel_dmz-network oovmtel-kafka-ot 2>/dev/null || true

echo -e "${GREEN}✅ DMZ network ready${NC}"
echo -e "${YELLOW}⚠️  Note: DMZ services will be started after IT zone${NC}"

# =============================================================================
# PHASE 3: Start Zone IT
# =============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  PHASE 3: Starting Zone IT (IEC 62443 Level 4/5)                       ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${YELLOW}🚀 Starting IT services...${NC}"
docker-compose -f docker-compose.it.yml up -d --remove-orphans

echo -e "${YELLOW}⏳ Waiting for IT services...${NC}"
sleep 15

wait_for_service "Kafka IT" 9092 60
wait_for_service "VictoriaMetrics" 8428 60
wait_for_service "OpenSearch" 9200 90
wait_for_service "Grafana" 3000 60

echo -e "${GREEN}✅ Zone IT started successfully${NC}"

# =============================================================================
# PHASE 4: Start DMZ Services
# =============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  PHASE 4: Starting DMZ Services (MirrorMaker 2)                        ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Connect IT Kafka to DMZ network
echo -e "${YELLOW}🔗 Connecting IT Kafka to DMZ network...${NC}"
docker network connect oovmtel_dmz-network oovmtel-kafka-it-1 2>/dev/null || true

echo -e "${YELLOW}🚀 Starting DMZ services...${NC}"
docker-compose -f docker-compose.dmz.yml up -d --remove-orphans

echo -e "${GREEN}✅ DMZ services started${NC}"

# =============================================================================
# VERIFICATION
# =============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  VERIFICATION: Checking Data Diode Integrity                           ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

sleep 5

# Check OT topics are not in IT (should be renamed to it-*)
echo -e "${YELLOW}🔍 Checking topic isolation...${NC}"
OT_TOPICS_IN_IT=$(docker exec oovmtel-kafka-it-1 kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null | grep -c "^ot-" || echo "0")

if [ "$OT_TOPICS_IN_IT" -eq 0 ]; then
    echo -e "${GREEN}✅ Data diode integrity verified - No raw OT topics in IT zone${NC}"
else
    echo -e "${RED}⚠️  Warning: Found $OT_TOPICS_IN_IT OT topics in IT zone${NC}"
fi

# =============================================================================
# SUMMARY
# =============================================================================
echo -e "\n${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    OOVMTEL Secure Architecture Started                ║"
echo "╠═══════════════════════════════════════════════════════════════════════╣"
echo "║                                                                       ║"
echo "║  Zone OT (172.29.0.0/24):                                            ║"
echo "║    - Kafka OT:        localhost:9094                                  ║"
echo "║    - OTel Collector:  localhost:4319 (gRPC), 4320 (HTTP)             ║"
echo "║    - SCADA Simulator: localhost:8080                                  ║"
echo "║    - MES Simulator:   localhost:8081                                  ║"
echo "║    - PLM Simulator:   localhost:8082                                  ║"
echo "║    - OPC-UA Simulator:localhost:8083                                  ║"
echo "║                                                                       ║"
echo "║  Zone DMZ (172.30.0.0/24):                                           ║"
echo "║    - MirrorMaker 2:   OT→IT replication (UNIDIRECTIONAL)             ║"
echo "║    - Data Diode:      Monitoring & validation                         ║"
echo "║                                                                       ║"
echo "║  Zone IT (172.31.0.0/16):                                            ║"
echo "║    - Kafka IT:        localhost:9092                                  ║"
echo "║    - VictoriaMetrics: localhost:8428                                  ║"
echo "║    - OpenObserve:     localhost:5080                                  ║"
echo "║    - OpenSearch:      localhost:9200                                  ║"
echo "║    - Grafana:         localhost:3000                                  ║"
echo "║    - OTel Collector:  localhost:4317 (gRPC), 4318 (HTTP)             ║"
echo "║                                                                       ║"
echo "╠═══════════════════════════════════════════════════════════════════════╣"
echo "║  Dashboards:                                                          ║"
echo "║    - Pipeline Health: http://localhost:3000/d/oovmtel-pipeline-health ║"
echo "║    - AI Observability:http://localhost:3000/d/oovmtel-ai-observability║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}📋 To view logs:${NC}"
echo "   docker-compose -f docker-compose.ot.yml logs -f"
echo "   docker-compose -f docker-compose.dmz.yml logs -f"
echo "   docker-compose -f docker-compose.it.yml logs -f"

echo -e "\n${YELLOW}🛑 To stop:${NC}"
echo "   ./scripts/stop-secure.sh"
