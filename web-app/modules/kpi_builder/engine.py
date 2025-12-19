"""
KPI Builder Engine - Main engine for custom KPI management
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from .models import (
    KPIDefinition,
    KPIResult,
    KPIFormula,
    KPIDataSource,
    KPIThreshold,
    KPIVisualization,
    Benchmark,
    BenchmarkComparison,
    KPICategory,
    AggregationType,
    STANDARD_KPI_TEMPLATES,
)
from .calculator import KPICalculator
from .benchmarking import BenchmarkManager

logger = logging.getLogger(__name__)


class KPIBuilderEngine:
    """
    Main KPI Builder Engine for SYNAPSIX.

    Features:
    - Custom KPI definition via UI
    - Formula builder
    - Template library
    - Benchmark comparison
    - Historical tracking
    - Scheduled calculation
    """

    def __init__(self):
        self.calculator = KPICalculator()
        self.benchmark_manager = BenchmarkManager()

        self._kpis: Dict[str, KPIDefinition] = {}
        self._results_history: Dict[str, List[KPIResult]] = {}

        # Load standard templates
        for kpi_id, kpi_def in STANDARD_KPI_TEMPLATES.items():
            self._kpis[kpi_id] = kpi_def

        logger.info("KPI Builder Engine initialized")

    # KPI Management

    def create_kpi(
        self,
        name: str,
        formula_expression: str,
        variables: Dict[str, Dict[str, Any]],
        category: KPICategory = KPICategory.CUSTOM,
        unit: str = "",
        target_value: Optional[float] = None,
        thresholds: Optional[List[Dict[str, Any]]] = None,
        created_by: Optional[str] = None,
    ) -> KPIDefinition:
        """
        Create a custom KPI.

        Args:
            name: KPI name
            formula_expression: Formula (e.g., "a / b * 100")
            variables: Variable definitions
            category: KPI category
            unit: Unit of measure
            target_value: Target value
            thresholds: Threshold definitions
            created_by: Creator username

        Returns:
            Created KPI definition
        """
        kpi_id = f"custom_{uuid.uuid4().hex[:8]}"

        # Build variables
        var_sources = {}
        for var_name, var_config in variables.items():
            var_sources[var_name] = KPIDataSource(
                source_id=f"{kpi_id}_{var_name}",
                metric_name=var_config.get("metric"),
                aggregation=AggregationType(var_config.get("aggregation", "avg")),
                equipment_filter=var_config.get("equipment_filter"),
                constant_value=var_config.get("constant_value"),
            )

        # Build thresholds
        kpi_thresholds = []
        if thresholds:
            for th in thresholds:
                kpi_thresholds.append(KPIThreshold(
                    name=th.get("name", "threshold"),
                    value=th.get("value", 0),
                    color=th.get("color", "#808080"),
                    comparison=th.get("comparison", "gte"),
                ))

        kpi = KPIDefinition(
            kpi_id=kpi_id,
            name=name,
            category=category,
            formula=KPIFormula(
                expression=formula_expression,
                variables=var_sources,
            ),
            unit=unit,
            target_value=target_value,
            thresholds=kpi_thresholds,
            created_by=created_by,
        )

        self._kpis[kpi_id] = kpi
        logger.info(f"Created KPI: {name} ({kpi_id})")

        return kpi

    def create_from_template(
        self,
        template_id: str,
        name: Optional[str] = None,
        **overrides
    ) -> Optional[KPIDefinition]:
        """Create KPI from template."""
        template = STANDARD_KPI_TEMPLATES.get(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return None

        # Create copy with new ID
        new_kpi = template.model_copy()
        new_kpi.kpi_id = f"{template_id}_{uuid.uuid4().hex[:8]}"

        if name:
            new_kpi.name = name

        # Apply overrides
        for key, value in overrides.items():
            if hasattr(new_kpi, key):
                setattr(new_kpi, key, value)

        self._kpis[new_kpi.kpi_id] = new_kpi
        logger.info(f"Created KPI from template: {new_kpi.name}")

        return new_kpi

    def update_kpi(
        self,
        kpi_id: str,
        **updates
    ) -> Optional[KPIDefinition]:
        """Update a KPI definition."""
        if kpi_id not in self._kpis:
            return None

        kpi = self._kpis[kpi_id]

        for key, value in updates.items():
            if hasattr(kpi, key):
                setattr(kpi, key, value)

        kpi.updated_at = datetime.utcnow()

        return kpi

    def delete_kpi(self, kpi_id: str) -> bool:
        """Delete a KPI."""
        if kpi_id in self._kpis:
            del self._kpis[kpi_id]
            if kpi_id in self._results_history:
                del self._results_history[kpi_id]
            return True
        return False

    def get_kpi(self, kpi_id: str) -> Optional[KPIDefinition]:
        """Get KPI by ID."""
        return self._kpis.get(kpi_id)

    def list_kpis(
        self,
        category: Optional[KPICategory] = None,
        enabled_only: bool = True
    ) -> List[KPIDefinition]:
        """List all KPIs."""
        kpis = list(self._kpis.values())

        if category:
            kpis = [k for k in kpis if k.category == category]

        if enabled_only:
            kpis = [k for k in kpis if k.enabled]

        return kpis

    def get_templates(self) -> List[Dict[str, Any]]:
        """Get available KPI templates."""
        return [
            {
                "template_id": tid,
                "name": template.name,
                "description": template.description,
                "category": template.category.value,
                "unit": template.unit,
            }
            for tid, template in STANDARD_KPI_TEMPLATES.items()
        ]

    # Calculation

    def calculate_kpi(
        self,
        kpi_id: str,
        metrics_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[KPIResult]:
        """Calculate a single KPI."""
        kpi = self._kpis.get(kpi_id)
        if not kpi:
            return None

        result = self.calculator.calculate(kpi, metrics_data)

        # Store in history
        if kpi_id not in self._results_history:
            self._results_history[kpi_id] = []
        self._results_history[kpi_id].append(result)

        # Trim history
        max_history = 1000
        if len(self._results_history[kpi_id]) > max_history:
            self._results_history[kpi_id] = self._results_history[kpi_id][-max_history:]

        return result

    def calculate_all(
        self,
        metrics_data: Dict[str, Any],
        category: Optional[KPICategory] = None
    ) -> List[KPIResult]:
        """Calculate all enabled KPIs."""
        results = []

        for kpi_id, kpi in self._kpis.items():
            if not kpi.enabled:
                continue
            if category and kpi.category != category:
                continue

            result = self.calculate_kpi(kpi_id, metrics_data)
            if result:
                results.append(result)

        return results

    # Benchmarking

    def compare_to_benchmark(
        self,
        kpi_id: str,
        benchmark_id: Optional[str] = None
    ) -> Optional[BenchmarkComparison]:
        """Compare KPI to benchmark."""
        kpi = self._kpis.get(kpi_id)
        if not kpi:
            return None

        # Get latest result
        history = self._results_history.get(kpi_id, [])
        if not history:
            return None

        latest_result = history[-1]

        return self.benchmark_manager.compare(
            latest_result, kpi, benchmark_id
        )

    def get_benchmark_report(
        self,
        category: Optional[KPICategory] = None
    ) -> Dict[str, Any]:
        """Get benchmark comparison report for all KPIs."""
        comparisons = []

        for kpi_id, kpi in self._kpis.items():
            if category and kpi.category != category:
                continue

            comparison = self.compare_to_benchmark(kpi_id)
            if comparison:
                comparisons.append(comparison)

        return self.benchmark_manager.get_improvement_roadmap(comparisons)

    # History

    def get_kpi_history(
        self,
        kpi_id: str,
        limit: int = 100
    ) -> List[KPIResult]:
        """Get KPI calculation history."""
        history = self._results_history.get(kpi_id, [])
        return history[-limit:]

    def get_kpi_trend(
        self,
        kpi_id: str,
        periods: int = 10
    ) -> Dict[str, Any]:
        """Get KPI trend analysis."""
        history = self.get_kpi_history(kpi_id, periods)

        if not history:
            return {"trend": "unknown", "values": []}

        values = [r.value for r in history]
        timestamps = [r.timestamp.isoformat() for r in history]

        # Calculate trend
        if len(values) >= 2:
            first_half = sum(values[:len(values)//2]) / (len(values)//2)
            second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)

            if second_half > first_half * 1.05:
                trend = "improving"
            elif second_half < first_half * 0.95:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "trend": trend,
            "values": values,
            "timestamps": timestamps,
            "current": values[-1] if values else None,
            "average": sum(values) / len(values) if values else None,
            "min": min(values) if values else None,
            "max": max(values) if values else None,
        }

    # Dashboard Data

    def get_dashboard_data(
        self,
        kpi_ids: Optional[List[str]] = None,
        category: Optional[KPICategory] = None
    ) -> List[Dict[str, Any]]:
        """Get KPI data formatted for dashboard display."""
        dashboard_data = []

        kpis_to_process = kpi_ids or list(self._kpis.keys())

        for kpi_id in kpis_to_process:
            kpi = self._kpis.get(kpi_id)
            if not kpi or not kpi.enabled:
                continue
            if category and kpi.category != category:
                continue

            history = self._results_history.get(kpi_id, [])
            latest = history[-1] if history else None

            dashboard_data.append({
                "kpi_id": kpi_id,
                "name": kpi.name,
                "category": kpi.category.value,
                "value": latest.value if latest else None,
                "unit": kpi.unit,
                "target": kpi.target_value,
                "status": latest.threshold_status if latest else "unknown",
                "color": latest.threshold_color if latest else "#808080",
                "trend": latest.trend if latest else "stable",
                "change_percent": latest.change_percent if latest else None,
                "visualization": kpi.visualization.model_dump(),
                "last_updated": latest.timestamp.isoformat() if latest else None,
            })

        return dashboard_data

    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            "total_kpis": len(self._kpis),
            "enabled_kpis": len([k for k in self._kpis.values() if k.enabled]),
            "custom_kpis": len([k for k in self._kpis.values() if k.kpi_id.startswith("custom_")]),
            "categories": {
                cat.value: len([k for k in self._kpis.values() if k.category == cat])
                for cat in KPICategory
            },
            "total_calculations": sum(len(h) for h in self._results_history.values()),
        }
