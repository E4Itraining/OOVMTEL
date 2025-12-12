#!/bin/bash
# =============================================================================
# OOVMTEL Platform Cleanup Script
# Removes all containers, volumes, and data
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "WARNING: This will remove all OOVMTEL data including:"
echo "  - All containers"
echo "  - All volumes (Victoria Metrics data, Kafka data, etc.)"
echo "  - All networks"
echo ""
read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping and removing all containers, networks, and volumes..."
    docker compose down -v --remove-orphans

    echo "Removing built images..."
    docker compose down --rmi local

    echo "Cleanup complete!"
else
    echo "Cleanup cancelled."
fi
