#!/bin/bash
# =============================================================================
# OOVMTEL - Secure IT/OT Architecture Stop Script
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║           OOVMTEL - Stopping Secure IT/OT Architecture                ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

cd "$PROJECT_DIR"

echo -e "${YELLOW}🛑 Stopping DMZ services...${NC}"
docker-compose -f docker-compose.dmz.yml down --remove-orphans 2>/dev/null || true

echo -e "${YELLOW}🛑 Stopping IT services...${NC}"
docker-compose -f docker-compose.it.yml down --remove-orphans 2>/dev/null || true

echo -e "${YELLOW}🛑 Stopping OT services...${NC}"
docker-compose -f docker-compose.ot.yml down --remove-orphans 2>/dev/null || true

echo -e "${YELLOW}🔗 Removing DMZ network...${NC}"
docker network rm oovmtel_dmz-network 2>/dev/null || true

echo -e "${GREEN}✅ All secure architecture services stopped${NC}"
