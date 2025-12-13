#!/bin/bash
# =============================================================================
# OOVMTEL Platform Stop Script
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Stopping OOVMTEL Platform..."

# Stop all services and remove orphan containers
docker compose down --remove-orphans

echo "OOVMTEL Platform stopped."
