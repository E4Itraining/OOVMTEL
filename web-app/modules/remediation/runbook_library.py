"""
Runbook Library - Manages collection of runbooks
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from .models import Runbook, RUNBOOK_TEMPLATES

logger = logging.getLogger(__name__)


class RunbookLibrary:
    """
    Manages the collection of available runbooks.

    Features:
    - Load/save runbooks
    - Search runbooks by condition
    - Runbook versioning
    - Usage statistics
    """

    def __init__(self):
        self.runbooks: Dict[str, Runbook] = {}
        self._load_templates()

    def _load_templates(self):
        """Load built-in runbook templates."""
        for runbook_id, runbook in RUNBOOK_TEMPLATES.items():
            self.runbooks[runbook.id] = runbook

        logger.info(f"Loaded {len(self.runbooks)} runbook templates")

    def get_runbook(self, runbook_id: str) -> Optional[Runbook]:
        """Get a runbook by ID."""
        return self.runbooks.get(runbook_id)

    def list_runbooks(
        self,
        category: Optional[str] = None,
        target_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Runbook]:
        """List runbooks with optional filters."""
        results = list(self.runbooks.values())

        if category:
            results = [r for r in results if r.category == category]

        if target_type:
            results = [r for r in results if r.target_type == target_type]

        if tags:
            results = [r for r in results
                      if any(t in r.tags for t in tags)]

        return results

    def find_runbooks_for_condition(
        self,
        condition: str,
        target_type: Optional[str] = None
    ) -> List[Runbook]:
        """Find runbooks that can handle a given condition."""
        condition_lower = condition.lower()
        matching = []

        # Condition to runbook mapping
        condition_mappings = {
            "high_cpu": ["restart_service", "scale_container"],
            "memory_leak": ["restart_service", "clear_cache"],
            "high_memory": ["clear_cache", "restart_service"],
            "service_unresponsive": ["restart_service"],
            "sensor_drift": ["recalibrate_sensor"],
            "database_failure": ["failover_database"],
            "high_load": ["scale_container"],
            "cache_overflow": ["clear_cache"],
            "temperature": ["recalibrate_sensor"],
            "vibration": ["recalibrate_sensor"],
        }

        # Find matching runbooks
        for keyword, runbook_names in condition_mappings.items():
            if keyword in condition_lower:
                for name in runbook_names:
                    for runbook in self.runbooks.values():
                        if name in runbook.id.lower() or name in runbook.name.lower():
                            if runbook not in matching:
                                matching.append(runbook)

        # Also check trigger conditions
        for runbook in self.runbooks.values():
            for trigger in runbook.trigger_conditions:
                if trigger in condition_lower or condition_lower in trigger:
                    if runbook not in matching:
                        matching.append(runbook)

        # Filter by target type if specified
        if target_type:
            matching = [r for r in matching if r.target_type == target_type]

        # Sort by success rate
        matching.sort(key=lambda r: r.success_rate, reverse=True)

        return matching

    def add_runbook(self, runbook: Runbook) -> Runbook:
        """Add a new runbook to the library."""
        if runbook.id in self.runbooks:
            raise ValueError(f"Runbook {runbook.id} already exists")

        runbook.created_at = datetime.utcnow()
        self.runbooks[runbook.id] = runbook

        logger.info(f"Added runbook: {runbook.id}")
        return runbook

    def update_runbook(self, runbook: Runbook) -> Runbook:
        """Update an existing runbook."""
        if runbook.id not in self.runbooks:
            raise ValueError(f"Runbook {runbook.id} not found")

        runbook.updated_at = datetime.utcnow()

        # Increment version
        parts = runbook.version.split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        runbook.version = ".".join(parts)

        self.runbooks[runbook.id] = runbook

        logger.info(f"Updated runbook: {runbook.id} to version {runbook.version}")
        return runbook

    def delete_runbook(self, runbook_id: str) -> bool:
        """Delete a runbook."""
        if runbook_id in self.runbooks:
            del self.runbooks[runbook_id]
            logger.info(f"Deleted runbook: {runbook_id}")
            return True
        return False

    def count(self) -> int:
        """Get total number of runbooks."""
        return len(self.runbooks)

    def get_categories(self) -> List[str]:
        """Get list of unique categories."""
        return list(set(r.category for r in self.runbooks.values()))

    def get_statistics(self) -> Dict[str, any]:
        """Get library statistics."""
        runbooks = list(self.runbooks.values())

        return {
            "total_runbooks": len(runbooks),
            "categories": self.get_categories(),
            "by_category": {
                cat: len([r for r in runbooks if r.category == cat])
                for cat in self.get_categories()
            },
            "by_risk_level": {
                "low": len([r for r in runbooks if r.risk_level == "low"]),
                "medium": len([r for r in runbooks if r.risk_level == "medium"]),
                "high": len([r for r in runbooks if r.risk_level == "high"]),
            },
            "average_success_rate": sum(r.success_rate for r in runbooks) / len(runbooks) if runbooks else 0,
            "total_executions": sum(r.execution_count for r in runbooks),
        }

    def record_execution(
        self,
        runbook_id: str,
        success: bool
    ):
        """Record a runbook execution for statistics."""
        runbook = self.runbooks.get(runbook_id)
        if runbook:
            runbook.execution_count += 1

            # Update success rate (exponential moving average)
            alpha = 0.1
            new_success = 1.0 if success else 0.0
            runbook.success_rate = (
                alpha * new_success +
                (1 - alpha) * runbook.success_rate
            )
