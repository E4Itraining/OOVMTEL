#!/bin/bash
# =============================================================================
# OOVMTEL Platform Stop Script
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Stopping OOVMTEL Platform..."

# Stop all services
docker compose down

echo "OOVMTEL Platform stopped."
