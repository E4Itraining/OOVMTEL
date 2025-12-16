"""
Simulation Engine - What-if scenario simulations using HPC resources
"""

import uuid
import time
import logging
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from statistics import mean, stdev, median

from .models import (
    SimulationScenario,
    SimulationResult,
    HPCJob,
    ComputeTask,
    JobStatus,
    JobPriority,
    ComputeBackend,
    SIMULATION_TEMPLATES,
)

logger = logging.getLogger(__name__)


class SimulationEngine:
    """
    Simulation Engine for What-If Scenario Analysis.

    Features:
    - Monte Carlo simulations
    - Equipment failure impact analysis
    - Production optimization scenarios
    - Supply chain disruption modeling
    - Energy cost impact analysis
    """

    def __init__(self):
        self.scenarios: Dict[str, SimulationScenario] = {}
        self.results: Dict[str, SimulationResult] = {}
        self.running_simulations: Dict[str, bool] = {}

        logger.info("Simulation Engine initialized")

    def create_scenario(
        self,
        name: str,
        scenario_type: str,
        base_metrics: Dict[str, Any],
        modifications: Dict[str, Any],
        horizon_hours: int = 24,
        iterations: int = 1000
    ) -> SimulationScenario:
        """Create a new simulation scenario."""
        scenario_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"

        template = SIMULATION_TEMPLATES.get(scenario_type)
        if not template:
            raise ValueError(f"Unknown scenario type: {scenario_type}")

        scenario = SimulationScenario(
            id=scenario_id,
            name=name,
            description=template["description"],
            type=scenario_type,
            base_metrics=base_metrics,
            modifications=modifications,
            simulation_horizon_hours=horizon_hours,
            monte_carlo_iterations=iterations
        )

        self.scenarios[scenario_id] = scenario
        logger.info(f"Created simulation scenario {scenario_id}: {name}")

        return scenario

    async def run_simulation(
        self,
        scenario_id: str,
        current_metrics: Dict[str, Any]
    ) -> SimulationResult:
        """Run a simulation scenario."""
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        start_time = datetime.utcnow()
        scenario.status = JobStatus.RUNNING
        self.running_simulations[scenario_id] = True

        try:
            # Run Monte Carlo simulation
            simulation_results = self._run_monte_carlo(
                scenario=scenario,
                current_metrics=current_metrics
            )

            # Analyze results
            result = self._analyze_results(
                scenario=scenario,
                raw_results=simulation_results,
                start_time=start_time
            )

            self.results[scenario_id] = result
            scenario.status = JobStatus.COMPLETED

            return result

        except Exception as e:
            scenario.status = JobStatus.FAILED
            logger.error(f"Simulation {scenario_id} failed: {e}")
            raise

        finally:
            self.running_simulations.pop(scenario_id, None)

    def _run_monte_carlo(
        self,
        scenario: SimulationScenario,
        current_metrics: Dict[str, Any]
    ) -> Dict[str, List[float]]:
        """Run Monte Carlo simulation iterations."""
        results = {
            "oee": [],
            "production": [],
            "quality": [],
            "cost": [],
            "downtime_hours": [],
            "risk_score": []
        }

        business = current_metrics.get("business", {})
        base_oee = business.get("oee", 75)
        base_production = business.get("production_today", 1000)
        base_quality = business.get("quality_rate", 95)

        for i in range(scenario.monte_carlo_iterations):
            # Apply modifications with random variations
            iteration_result = self._simulate_iteration(
                scenario=scenario,
                base_oee=base_oee,
                base_production=base_production,
                base_quality=base_quality,
                iteration=i
            )

            for key in results:
                if key in iteration_result:
                    results[key].append(iteration_result[key])

        return results

    def _simulate_iteration(
        self,
        scenario: SimulationScenario,
        base_oee: float,
        base_production: int,
        base_quality: float,
        iteration: int
    ) -> Dict[str, float]:
        """Simulate a single iteration with stochastic variations."""
        result = {}

        # Add random noise to simulate uncertainty
        noise_factor = random.gauss(1.0, 0.1)

        if scenario.type == "equipment_failure":
            # Simulate equipment failure impact
            downtime_hours = scenario.modifications.get("downtime_hours", 4)
            downtime_variation = random.gauss(downtime_hours, downtime_hours * 0.2)

            # Impact on OEE (availability component affected)
            availability_impact = (downtime_variation / scenario.simulation_horizon_hours) * 100
            result["oee"] = max(0, base_oee - availability_impact * noise_factor)

            # Impact on production
            production_loss = (downtime_variation / 24) * base_production
            result["production"] = int(max(0, base_production - production_loss))

            # Quality may be affected during restart
            quality_impact = random.uniform(0, 3) if downtime_variation > 2 else 0
            result["quality"] = max(0, base_quality - quality_impact)

            # Cost impact (lost production + repair)
            repair_cost = random.uniform(5000, 20000)
            lost_production_cost = production_loss * 50  # $50 per unit
            result["cost"] = repair_cost + lost_production_cost

            result["downtime_hours"] = downtime_variation
            result["risk_score"] = min(100, availability_impact * 2 + random.uniform(0, 20))

        elif scenario.type == "production_change":
            # Simulate production increase
            increase_percent = scenario.modifications.get("increase_percent", 20)
            ramp_up_hours = scenario.modifications.get("ramp_up_hours", 24)

            # OEE may decrease with higher production
            oee_pressure = increase_percent * 0.15 * noise_factor
            result["oee"] = max(50, base_oee - oee_pressure)

            # Production increase
            actual_increase = increase_percent * random.uniform(0.7, 1.1)
            result["production"] = int(base_production * (1 + actual_increase / 100))

            # Quality pressure
            quality_pressure = increase_percent * 0.1 * noise_factor
            result["quality"] = max(85, base_quality - quality_pressure)

            # Cost (overtime, additional materials)
            overtime_cost = increase_percent * 100 * noise_factor
            result["cost"] = overtime_cost

            result["downtime_hours"] = 0
            result["risk_score"] = min(100, oee_pressure * 3)

        elif scenario.type == "maintenance_delay":
            # Simulate delayed maintenance impact
            delay_days = scenario.modifications.get("delay_days", 7)
            current_health = scenario.modifications.get("current_health_score", 80)

            # Health degrades over time
            daily_degradation = (100 - current_health) * 0.05
            degraded_health = current_health - (delay_days * daily_degradation * noise_factor)

            # Failure probability increases
            failure_prob = max(0, min(1, (100 - degraded_health) / 100))

            # Random failure occurrence
            if random.random() < failure_prob:
                result["downtime_hours"] = random.uniform(4, 24)
                result["oee"] = max(40, base_oee - result["downtime_hours"] * 2)
                result["cost"] = random.uniform(10000, 50000)
            else:
                result["downtime_hours"] = 0
                result["oee"] = base_oee - delay_days * 0.5
                result["cost"] = 0

            result["production"] = int(base_production * (result["oee"] / base_oee))
            result["quality"] = base_quality - random.uniform(0, 2)
            result["risk_score"] = min(100, failure_prob * 100 + 20)

        elif scenario.type == "supply_chain":
            # Simulate supply chain disruption
            severity = scenario.modifications.get("disruption_severity", 50)

            # Impact scales with severity
            severity_factor = severity / 100 * noise_factor

            # Production heavily impacted
            result["production"] = int(base_production * (1 - severity_factor * 0.6))

            # OEE drops due to stoppages
            result["oee"] = max(30, base_oee - severity_factor * 30)

            # Quality may improve (slower production)
            result["quality"] = min(99, base_quality + random.uniform(0, 2))

            # Cost impact (express shipping, alternative suppliers)
            result["cost"] = severity * 500 * noise_factor

            result["downtime_hours"] = severity_factor * 8
            result["risk_score"] = min(100, severity + random.uniform(0, 20))

        elif scenario.type == "cost_change":
            # Simulate energy cost increase
            cost_increase = scenario.modifications.get("cost_increase_percent", 20)

            # Production unchanged
            result["production"] = base_production

            # OEE unchanged
            result["oee"] = base_oee

            # Quality unchanged
            result["quality"] = base_quality

            # Cost impact
            base_energy_cost = base_production * 5  # $5 per unit energy cost
            result["cost"] = base_energy_cost * (cost_increase / 100) * noise_factor

            result["downtime_hours"] = 0
            result["risk_score"] = min(100, cost_increase * 0.5)

        else:
            # Default case
            result = {
                "oee": base_oee * noise_factor,
                "production": int(base_production * noise_factor),
                "quality": base_quality * noise_factor,
                "cost": 0,
                "downtime_hours": 0,
                "risk_score": 0
            }

        return result

    def _analyze_results(
        self,
        scenario: SimulationScenario,
        raw_results: Dict[str, List[float]],
        start_time: datetime
    ) -> SimulationResult:
        """Analyze Monte Carlo results and generate insights."""
        end_time = datetime.utcnow()

        # Calculate statistics for each metric
        statistics = {}
        probability_distribution = {}
        confidence_lower = {}
        confidence_upper = {}

        for metric, values in raw_results.items():
            if not values:
                continue

            sorted_values = sorted(values)
            n = len(sorted_values)

            statistics[metric] = {
                "mean": mean(values),
                "median": median(values),
                "std_dev": stdev(values) if n > 1 else 0,
                "min": min(values),
                "max": max(values),
                "p5": sorted_values[int(n * 0.05)],
                "p25": sorted_values[int(n * 0.25)],
                "p75": sorted_values[int(n * 0.75)],
                "p95": sorted_values[int(n * 0.95)]
            }

            # Confidence intervals
            ci_index = int(n * (1 - scenario.confidence_level) / 2)
            confidence_lower[metric] = sorted_values[ci_index]
            confidence_upper[metric] = sorted_values[n - ci_index - 1]

            # Create distribution buckets for visualization
            bucket_count = 20
            bucket_size = (max(values) - min(values)) / bucket_count if max(values) != min(values) else 1
            distribution = [0] * bucket_count
            for v in values:
                bucket_idx = min(bucket_count - 1, int((v - min(values)) / bucket_size))
                distribution[bucket_idx] += 1
            probability_distribution[metric] = distribution

        # Calculate impacts
        base_oee = scenario.base_metrics.get("business", {}).get("oee", 75)
        base_production = scenario.base_metrics.get("business", {}).get("production_today", 1000)
        base_quality = scenario.base_metrics.get("business", {}).get("quality_rate", 95)

        oee_impact = statistics.get("oee", {}).get("mean", base_oee) - base_oee
        production_impact = int(statistics.get("production", {}).get("mean", base_production) - base_production)
        quality_impact = statistics.get("quality", {}).get("mean", base_quality) - base_quality
        cost_impact = statistics.get("cost", {}).get("mean", 0)

        # Risk factors and mitigations
        risk_factors = []
        mitigations = []

        risk_score = statistics.get("risk_score", {}).get("mean", 0)

        if risk_score > 70:
            risk_factors.append("High probability of significant operational impact")
            mitigations.append("Consider implementing contingency plans immediately")
        elif risk_score > 40:
            risk_factors.append("Moderate risk of operational disruption")
            mitigations.append("Monitor key indicators closely")

        if oee_impact < -5:
            risk_factors.append(f"Expected OEE drop of {abs(oee_impact):.1f}%")
            mitigations.append("Prepare backup equipment or overtime capacity")

        if production_impact < -100:
            risk_factors.append(f"Expected production loss of {abs(production_impact)} units")
            mitigations.append("Consider pre-building inventory buffer")

        if cost_impact > 10000:
            risk_factors.append(f"Expected additional costs of ${cost_impact:,.0f}")
            mitigations.append("Review budget allocation and cost optimization")

        # Generate visualization data
        charts = [
            {
                "type": "histogram",
                "title": "OEE Distribution",
                "data": probability_distribution.get("oee", []),
                "metric": "oee"
            },
            {
                "type": "histogram",
                "title": "Production Distribution",
                "data": probability_distribution.get("production", []),
                "metric": "production"
            },
            {
                "type": "box_plot",
                "title": "Risk Score Analysis",
                "data": statistics.get("risk_score", {}),
                "metric": "risk_score"
            }
        ]

        result = SimulationResult(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            started_at=start_time,
            completed_at=end_time,
            duration_seconds=(end_time - start_time).total_seconds(),
            iterations_completed=scenario.monte_carlo_iterations,
            predicted_outcomes={
                "oee": statistics.get("oee", {}).get("mean", 0),
                "production": statistics.get("production", {}).get("mean", 0),
                "quality": statistics.get("quality", {}).get("mean", 0),
                "downtime_hours": statistics.get("downtime_hours", {}).get("mean", 0)
            },
            probability_distribution=probability_distribution,
            oee_impact=oee_impact,
            production_impact=production_impact,
            quality_impact=quality_impact,
            cost_impact=cost_impact,
            risk_score=risk_score,
            risk_factors=risk_factors,
            mitigation_suggestions=mitigations,
            confidence_interval_lower=confidence_lower,
            confidence_interval_upper=confidence_upper,
            confidence_level=scenario.confidence_level,
            statistics=statistics,
            charts=charts
        )

        return result

    def get_scenario(self, scenario_id: str) -> Optional[SimulationScenario]:
        """Get scenario by ID."""
        return self.scenarios.get(scenario_id)

    def get_result(self, scenario_id: str) -> Optional[SimulationResult]:
        """Get simulation result."""
        return self.results.get(scenario_id)

    def list_scenarios(self) -> List[SimulationScenario]:
        """List all scenarios."""
        return list(self.scenarios.values())

    def list_templates(self) -> Dict[str, Dict[str, Any]]:
        """List available simulation templates."""
        return SIMULATION_TEMPLATES

    def get_statistics(self) -> Dict[str, Any]:
        """Get simulation statistics."""
        return {
            "total_scenarios": len(self.scenarios),
            "completed_simulations": len(self.results),
            "running_simulations": len(self.running_simulations),
            "templates_available": len(SIMULATION_TEMPLATES)
        }

    def compare_scenarios(
        self,
        scenario_ids: List[str]
    ) -> Dict[str, Any]:
        """Compare results from multiple scenarios."""
        comparison = {
            "scenarios": [],
            "metrics_comparison": {
                "oee": [],
                "production": [],
                "quality": [],
                "cost": [],
                "risk_score": []
            }
        }

        for sid in scenario_ids:
            result = self.results.get(sid)
            if result:
                comparison["scenarios"].append({
                    "id": sid,
                    "name": result.scenario_name,
                    "oee_impact": result.oee_impact,
                    "production_impact": result.production_impact,
                    "cost_impact": result.cost_impact,
                    "risk_score": result.risk_score
                })

                for metric in comparison["metrics_comparison"]:
                    if metric in result.statistics:
                        comparison["metrics_comparison"][metric].append({
                            "scenario": result.scenario_name,
                            "mean": result.statistics[metric].get("mean", 0),
                            "std_dev": result.statistics[metric].get("std_dev", 0)
                        })

        return comparison
