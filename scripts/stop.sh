#!/bin/bash
# =============================================================================
# OOVMTEL Platform Stop Script
# Automatically detects and stops the running architecture
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

# =============================================================================
# Detect Architecture
# =============================================================================

detect_architecture() {
    # First check if architecture file exists
    if [ -f "$ARCHITECTURE_FILE" ]; then
        ARCHITECTURE=$(cat "$ARCHITECTURE_FILE")
        echo -e "${BLUE}Detected architecture from file: $ARCHITECTURE${NC}"
        return
    fi

    # Otherwise, detect based on running containers
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "oovmtel-kafka-ot"; then
        ARCHITECTURE="secure"
    elif docker ps --format '{{.Names}}' 2>/dev/null | grep -q "oovmtel-otel-ot-gateway"; then
        ARCHITECTURE="direct-otlp"
    elif docker ps --format '{{.Names}}' 2>/dev/null | grep -q "oovmtel-kafka\$"; then
        ARCHITECTURE="simple"
    else
        # Check for any oovmtel containers
        if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^oovmtel-"; then
            echo -e "${YELLOW}Could not determine architecture, stopping all OOVMTEL containers${NC}"
            ARCHITECTURE="all"
        else
            echo -e "${YELLOW}No OOVMTEL containers found${NC}"
            exit 0
        fi
    fi
    echo -e "${BLUE}Detected architecture: $ARCHITECTURE${NC}"
}

# =============================================================================
# Stop Functions
# =============================================================================

stop_simple() {
    echo -e "${YELLOW}Stopping Simple architecture...${NC}"
    docker compose down --remove-orphans 2>/dev/null || true
    echo -e "${GREEN}Simple architecture stopped${NC}"
}

stop_secure() {
    echo -e "${YELLOW}Stopping Secure IT/OT/DMZ architecture...${NC}"

    echo -e "${YELLOW}Stopping DMZ services...${NC}"
    docker compose -f docker-compose.dmz.yml down --remove-orphans 2>/dev/null || true

    echo -e "${YELLOW}Stopping IT services...${NC}"
    docker compose -f docker-compose.it.yml down --remove-orphans 2>/dev/null || true

    echo -e "${YELLOW}Stopping OT services...${NC}"
    docker compose -f docker-compose.ot.yml down --remove-orphans 2>/dev/null || true

    echo -e "${YELLOW}Removing DMZ network...${NC}"
    docker network rm oovmtel_dmz-network 2>/dev/null || true

    echo -e "${GREEN}Secure architecture stopped${NC}"
}

stop_direct_otlp() {
    echo -e "${YELLOW}Stopping Direct OTLP architecture...${NC}"
    docker compose -f docker-compose.direct-otlp.yml down --remove-orphans 2>/dev/null || true
    echo -e "${GREEN}Direct OTLP architecture stopped${NC}"
}

stop_all() {
    echo -e "${YELLOW}Stopping all OOVMTEL architectures...${NC}"

    # Stop all compose projects
    docker compose down --remove-orphans 2>/dev/null || true
    docker compose -f docker-compose.dmz.yml down --remove-orphans 2>/dev/null || true
    docker compose -f docker-compose.it.yml down --remove-orphans 2>/dev/null || true
    docker compose -f docker-compose.ot.yml down --remove-orphans 2>/dev/null || true
    docker compose -f docker-compose.direct-otlp.yml down --remove-orphans 2>/dev/null || true

    # Remove DMZ network if exists
    docker network rm oovmtel_dmz-network 2>/dev/null || true

    echo -e "${GREEN}All OOVMTEL services stopped${NC}"
}

# =============================================================================
# Main
# =============================================================================

echo -e "${BLUE}"
echo "=============================================="
echo "  OOVMTEL Platform Stop"
echo "=============================================="
echo -e "${NC}"

# Allow override via argument
if [ -n "$1" ]; then
    ARCHITECTURE="$1"
    echo -e "${BLUE}Using architecture from argument: $ARCHITECTURE${NC}"
else
    detect_architecture
fi

case "$ARCHITECTURE" in
    simple)
        stop_simple
        ;;
    secure)
        stop_secure
        ;;
    direct-otlp)
        stop_direct_otlp
        ;;
    all)
        stop_all
        ;;
    *)
        echo -e "${RED}Unknown architecture: $ARCHITECTURE${NC}"
        echo "Usage: $0 [simple|secure|direct-otlp|all]"
        exit 1
        ;;
esac

# Remove architecture file
rm -f "$ARCHITECTURE_FILE"

echo -e "${GREEN}OOVMTEL Platform stopped.${NC}"
