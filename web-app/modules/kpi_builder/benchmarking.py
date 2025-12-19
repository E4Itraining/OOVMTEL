"""
Benchmarking Manager - Compare KPIs against industry benchmarks
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from .models import (
    KPIDefinition,
    KPIResult,
    Benchmark,
    BenchmarkComparison,
    KPICategory,
    INDUSTRY_BENCHMARKS,
)

logger = logging.getLogger(__name__)


class BenchmarkManager:
    """
    Compare KPIs against industry benchmarks.

    Features:
    - Multiple benchmark sources
    - Percentile ranking
    - Gap analysis
    - Improvement recommendations
    """

    def __init__(self):
        self._benchmarks: Dict[str, Benchmark] = dict(INDUSTRY_BENCHMARKS)

        logger.info("Benchmark Manager initialized")

    def add_benchmark(self, benchmark: Benchmark) -> str:
        """Add a benchmark."""
        self._benchmarks[benchmark.benchmark_id] = benchmark
        logger.info(f"Added benchmark: {benchmark.name}")
        return benchmark.benchmark_id

    def get_benchmark(self, benchmark_id: str) -> Optional[Benchmark]:
        """Get benchmark by ID."""
        return self._benchmarks.get(benchmark_id)

    def list_benchmarks(
        self,
        category: Optional[KPICategory] = None,
        industry: Optional[str] = None
    ) -> List[Benchmark]:
        """List available benchmarks."""
        benchmarks = list(self._benchmarks.values())

        if category:
            benchmarks = [b for b in benchmarks if b.kpi_category == category]

        if industry:
            benchmarks = [b for b in benchmarks if b.industry == industry]

        return benchmarks

    def compare(
        self,
        kpi_result: KPIResult,
        kpi_definition: KPIDefinition,
        benchmark_id: Optional[str] = None
    ) -> Optional[BenchmarkComparison]:
        """
        Compare KPI result against benchmark.

        Args:
            kpi_result: KPI calculation result
            kpi_definition: KPI definition
            benchmark_id: Specific benchmark ID (or auto-select)

        Returns:
            Benchmark comparison or None
        """
        # Find appropriate benchmark
        if benchmark_id:
            benchmark = self._benchmarks.get(benchmark_id)
        else:
            benchmark = self._find_benchmark(kpi_definition)

        if not benchmark:
            return None

        value = kpi_result.value

        # Calculate percentile rank
        percentile_rank = self._calculate_percentile_rank(value, benchmark)

        # Calculate gaps
        gap_to_median = value - benchmark.percentile_50
        gap_to_world_class = benchmark.world_class - value

        # Determine rating
        rating, rating_description = self._determine_rating(value, benchmark)

        # Calculate improvement potential
        improvement_potential = 0.0
        if value < benchmark.world_class and value > 0:
            improvement_potential = ((benchmark.world_class - value) / value) * 100

        # Generate recommendations
        recommendations = self._generate_recommendations(
            kpi_result, kpi_definition, benchmark, rating
        )

        return BenchmarkComparison(
            kpi_id=kpi_result.kpi_id,
            kpi_name=kpi_result.kpi_name,
            current_value=value,
            benchmark_id=benchmark.benchmark_id,
            benchmark_name=benchmark.name,
            percentile_rank=percentile_rank,
            gap_to_median=gap_to_median,
            gap_to_world_class=gap_to_world_class,
            rating=rating,
            rating_description=rating_description,
            improvement_potential_percent=improvement_potential,
            recommendations=recommendations,
        )

    def _find_benchmark(
        self,
        kpi_definition: KPIDefinition
    ) -> Optional[Benchmark]:
        """Find appropriate benchmark for KPI."""
        # Look for matching category
        for benchmark in self._benchmarks.values():
            if benchmark.kpi_category == kpi_definition.category:
                return benchmark

        # Look by KPI ID
        for bid, benchmark in self._benchmarks.items():
            if kpi_definition.kpi_id in bid:
                return benchmark

        return None

    def _calculate_percentile_rank(
        self,
        value: float,
        benchmark: Benchmark
    ) -> float:
        """Calculate what percentile the value falls into."""
        if value <= benchmark.percentile_25:
            # Below 25th percentile
            return (value / benchmark.percentile_25) * 25 if benchmark.percentile_25 > 0 else 0

        elif value <= benchmark.percentile_50:
            # Between 25th and 50th
            range_size = benchmark.percentile_50 - benchmark.percentile_25
            if range_size > 0:
                return 25 + ((value - benchmark.percentile_25) / range_size) * 25
            return 37.5

        elif value <= benchmark.percentile_75:
            # Between 50th and 75th
            range_size = benchmark.percentile_75 - benchmark.percentile_50
            if range_size > 0:
                return 50 + ((value - benchmark.percentile_50) / range_size) * 25
            return 62.5

        elif value <= benchmark.percentile_90:
            # Between 75th and 90th
            range_size = benchmark.percentile_90 - benchmark.percentile_75
            if range_size > 0:
                return 75 + ((value - benchmark.percentile_75) / range_size) * 15
            return 82.5

        else:
            # Above 90th percentile
            range_size = benchmark.world_class - benchmark.percentile_90
            if range_size > 0:
                extra = ((value - benchmark.percentile_90) / range_size) * 10
                return min(100, 90 + extra)
            return 95

    def _determine_rating(
        self,
        value: float,
        benchmark: Benchmark
    ) -> tuple:
        """Determine rating based on value and benchmark."""
        if value >= benchmark.world_class:
            return ("world_class", "Performance de classe mondiale")
        elif value >= benchmark.percentile_90:
            return ("top_decile", "Top 10% de l'industrie")
        elif value >= benchmark.percentile_75:
            return ("top_quartile", "Top 25% de l'industrie")
        elif value >= benchmark.percentile_50:
            return ("above_average", "Au-dessus de la moyenne")
        elif value >= benchmark.percentile_25:
            return ("below_average", "En dessous de la moyenne")
        else:
            return ("bottom_quartile", "Quartile inférieur - amélioration urgente")

    def _generate_recommendations(
        self,
        kpi_result: KPIResult,
        kpi_definition: KPIDefinition,
        benchmark: Benchmark,
        rating: str
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if rating in ["bottom_quartile", "below_average"]:
            recommendations.append(
                f"Objectif à court terme: atteindre la médiane de l'industrie ({benchmark.percentile_50})"
            )
            recommendations.append(
                "Identifier et éliminer les principales sources de pertes"
            )
            recommendations.append(
                "Mettre en place un suivi quotidien des indicateurs clés"
            )

        elif rating == "above_average":
            recommendations.append(
                f"Objectif: atteindre le top quartile ({benchmark.percentile_75})"
            )
            recommendations.append(
                "Analyser les meilleures pratiques des équipements les plus performants"
            )

        elif rating == "top_quartile":
            recommendations.append(
                f"Objectif: atteindre le top 10% ({benchmark.percentile_90})"
            )
            recommendations.append(
                "Implémenter des techniques d'amélioration continue avancées"
            )

        elif rating == "top_decile":
            recommendations.append(
                f"Objectif: atteindre la classe mondiale ({benchmark.world_class})"
            )
            recommendations.append(
                "Partager les meilleures pratiques avec les autres équipements"
            )

        # Category-specific recommendations
        if kpi_definition.category == KPICategory.EFFICIENCY:
            if rating in ["bottom_quartile", "below_average"]:
                recommendations.append(
                    "Focus sur la réduction des micro-arrêts et des temps de changement"
                )

        elif kpi_definition.category == KPICategory.QUALITY:
            if rating in ["bottom_quartile", "below_average"]:
                recommendations.append(
                    "Analyser les causes racines des défauts récurrents"
                )

        elif kpi_definition.category == KPICategory.MAINTENANCE:
            recommendations.append(
                "Évaluer la transition vers une maintenance prédictive"
            )

        return recommendations[:5]

    def get_improvement_roadmap(
        self,
        comparisons: List[BenchmarkComparison]
    ) -> Dict[str, Any]:
        """Generate improvement roadmap from multiple comparisons."""
        if not comparisons:
            return {}

        # Sort by improvement potential
        sorted_comparisons = sorted(
            comparisons,
            key=lambda c: c.improvement_potential_percent,
            reverse=True
        )

        # Group into priority levels
        high_priority = []
        medium_priority = []
        low_priority = []

        for comp in sorted_comparisons:
            if comp.rating in ["bottom_quartile", "below_average"]:
                high_priority.append(comp)
            elif comp.rating == "above_average":
                medium_priority.append(comp)
            else:
                low_priority.append(comp)

        return {
            "summary": {
                "total_kpis": len(comparisons),
                "high_priority_count": len(high_priority),
                "medium_priority_count": len(medium_priority),
                "low_priority_count": len(low_priority),
                "total_improvement_potential": sum(c.improvement_potential_percent for c in comparisons),
            },
            "high_priority": [
                {
                    "kpi": c.kpi_name,
                    "current": c.current_value,
                    "target": c.current_value + c.gap_to_median,
                    "rating": c.rating,
                    "recommendations": c.recommendations[:2],
                }
                for c in high_priority[:3]
            ],
            "medium_priority": [
                {
                    "kpi": c.kpi_name,
                    "current": c.current_value,
                    "target": c.current_value + c.gap_to_world_class,
                    "rating": c.rating,
                }
                for c in medium_priority[:3]
            ],
            "already_good": [c.kpi_name for c in low_priority],
        }
