#!/bin/bash
# =============================================================================
# OOVMTEL Platform Cleanup Script
# Removes all containers, volumes, networks, and images for all architectures
# =============================================================================

set -e

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

echo -e "${BLUE}"
echo "=============================================="
echo "  OOVMTEL Platform Cleanup"
echo "=============================================="
echo -e "${NC}"

echo -e "${YELLOW}WARNING: This will remove all OOVMTEL data including:${NC}"
echo "  - All containers (all architectures)"
echo "  - All volumes (Victoria Metrics data, Kafka data, etc.)"
echo "  - All networks (including DMZ network)"
echo "  - All locally built images"
echo ""

read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cleanup cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Stopping and removing all containers...${NC}"

# Stop all compose projects
echo "  Stopping simple architecture..."
docker compose down -v --remove-orphans 2>/dev/null || true

echo "  Stopping secure architecture (DMZ)..."
docker compose -f docker-compose.dmz.yml down -v --remove-orphans 2>/dev/null || true

echo "  Stopping secure architecture (IT)..."
docker compose -f docker-compose.it.yml down -v --remove-orphans 2>/dev/null || true

echo "  Stopping secure architecture (OT)..."
docker compose -f docker-compose.ot.yml down -v --remove-orphans 2>/dev/null || true

echo "  Stopping direct-otlp architecture..."
docker compose -f docker-compose.direct-otlp.yml down -v --remove-orphans 2>/dev/null || true

echo -e "${YELLOW}Removing DMZ network...${NC}"
docker network rm oovmtel_dmz-network 2>/dev/null || true

echo -e "${YELLOW}Removing locally built images...${NC}"
docker compose down --rmi local 2>/dev/null || true
docker compose -f docker-compose.ot.yml down --rmi local 2>/dev/null || true
docker compose -f docker-compose.it.yml down --rmi local 2>/dev/null || true
docker compose -f docker-compose.direct-otlp.yml down --rmi local 2>/dev/null || true

echo -e "${YELLOW}Cleaning up orphan volumes...${NC}"
# Remove any remaining oovmtel volumes
docker volume ls -q | grep "^oovmtel" | xargs -r docker volume rm 2>/dev/null || true

echo -e "${YELLOW}Removing architecture file...${NC}"
rm -f "$ARCHITECTURE_FILE"

echo -e "${YELLOW}Cleaning up data directory...${NC}"
rm -rf "$PROJECT_DIR/data" 2>/dev/null || true

echo ""
echo -e "${GREEN}=============================================="
echo "  Cleanup complete!"
echo "==============================================${NC}"
echo ""
echo "To start fresh, run: ./scripts/start.sh [simple|secure|direct-otlp]"
