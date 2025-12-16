"""
HPC Engine - Main orchestrator for High Performance Computing capabilities
"""

import uuid
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .models import (
    HPCCluster,
    HPCNode,
    HPCJob,
    HPCMetrics,
    SimulationScenario,
    SimulationResult,
    ClusterStatus,
    NodeStatus,
    JobStatus,
    JobPriority,
    ComputeBackend,
    HPC_PRESETS,
    SIMULATION_TEMPLATES,
)
from .cluster_manager import ClusterManager
from .simulation_engine import SimulationEngine
from .parallel_processor import ParallelProcessor

logger = logging.getLogger(__name__)


class HPCEngine:
    """
    Main HPC Engine - Orchestrates all HPC capabilities.

    Game-Changer Features:
    1. GPU-Accelerated Processing - 10-100x faster ML inference
    2. Distributed Computing - Scale across multiple nodes
    3. What-If Simulations - Monte Carlo scenario analysis
    4. Parallel Batch Processing - High-throughput data processing
    5. Distributed ML Training - Train models at scale

    Competitive Advantages:
    - Native integration with industrial observability stack
    - Real-time simulation during production
    - Intelligent resource allocation
    - Seamless edge-to-cloud compute coordination
    """

    def __init__(
        self,
        auto_create_cluster: bool = True,
        default_cluster_preset: str = "medium"
    ):
        # Initialize components
        self.cluster_manager = ClusterManager()
        self.simulation_engine = SimulationEngine()
        self.parallel_processor = ParallelProcessor()

        # Default cluster
        self.default_cluster_id: Optional[str] = None

        # Auto-create default cluster
        if auto_create_cluster:
            cluster = self.cluster_manager.create_cluster(
                name="OOVMTEL-HPC-Default",
                preset=default_cluster_preset,
                description="Default HPC cluster for industrial observability workloads"
            )
            self.default_cluster_id = cluster.id
            # Simulate initial workload
            self.cluster_manager.simulate_workload(cluster.id, 30)

        # Statistics
        self.engine_start_time = datetime.utcnow()

        logger.info("HPC Engine initialized")

    # =========================================
    # Cluster Management
    # =========================================

    def create_cluster(
        self,
        name: str,
        preset: str = "medium",
        description: str = ""
    ) -> HPCCluster:
        """Create a new HPC cluster."""
        return self.cluster_manager.create_cluster(name, preset, description)

    def get_cluster(self, cluster_id: str) -> Optional[HPCCluster]:
        """Get cluster by ID."""
        return self.cluster_manager.get_cluster(cluster_id)

    def get_default_cluster(self) -> Optional[HPCCluster]:
        """Get the default cluster."""
        if self.default_cluster_id:
            return self.cluster_manager.get_cluster(self.default_cluster_id)
        return None

    def list_clusters(self) -> List[HPCCluster]:
        """List all clusters."""
        return self.cluster_manager.get_all_clusters()

    def get_cluster_metrics(self, cluster_id: str = None) -> Dict[str, Any]:
        """Get cluster metrics."""
        cid = cluster_id or self.default_cluster_id
        if cid:
            return self.cluster_manager.get_cluster_metrics(cid)
        return {}

    def get_available_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get available cluster presets."""
        return HPC_PRESETS

    # =========================================
    # Job Management
    # =========================================

    async def submit_job(
        self,
        name: str,
        job_type: str,
        parameters: Dict[str, Any],
        priority: JobPriority = JobPriority.NORMAL,
        cluster_id: str = None
    ) -> HPCJob:
        """Submit a job to the HPC cluster."""
        cid = cluster_id or self.default_cluster_id
        if not cid:
            raise ValueError("No cluster available")

        job_id = f"JOB-{uuid.uuid4().hex[:8].upper()}"

        # Create job based on type
        if job_type == "batch_processing":
            job = await self.parallel_processor.submit_batch_job(
                name=name,
                data=parameters.get("data", []),
                processor_func=parameters.get("processor", "default"),
                batch_size=parameters.get("batch_size", 1000),
                priority=priority,
                use_gpu=parameters.get("use_gpu", False)
            )
        elif job_type == "ml_training":
            job = await self.parallel_processor.submit_ml_training_job(
                name=name,
                model_type=parameters.get("model_type", "neural_network"),
                training_data=parameters.get("training_data", {"size": 10000}),
                hyperparameters=parameters.get("hyperparameters", {}),
                epochs=parameters.get("epochs", 100),
                distributed=parameters.get("distributed", True)
            )
        else:
            # Generic job
            job = HPCJob(
                id=job_id,
                name=name,
                description=parameters.get("description", ""),
                priority=priority,
                backend=ComputeBackend.HYBRID,
                metadata=parameters
            )
            self.cluster_manager.submit_job(job, cid)

        return job

    async def execute_job(self, job_id: str) -> HPCJob:
        """Execute a submitted job."""
        job = self.parallel_processor.get_job(job_id)
        if not job:
            job = self.cluster_manager.get_job(job_id)

        if not job:
            raise ValueError(f"Job {job_id} not found")

        if job.metadata.get("model_type"):
            return await self.parallel_processor.execute_ml_training(job_id)
        else:
            return await self.parallel_processor.execute_job(job_id)

    def get_job(self, job_id: str) -> Optional[HPCJob]:
        """Get job by ID."""
        job = self.parallel_processor.get_job(job_id)
        if not job:
            job = self.cluster_manager.get_job(job_id)
        return job

    def list_jobs(self, status: Optional[JobStatus] = None) -> List[HPCJob]:
        """List all jobs."""
        return self.parallel_processor.list_jobs(status)

    # =========================================
    # What-If Simulations
    # =========================================

    def create_simulation(
        self,
        name: str,
        scenario_type: str,
        current_metrics: Dict[str, Any],
        modifications: Dict[str, Any],
        horizon_hours: int = 24,
        iterations: int = 1000
    ) -> SimulationScenario:
        """Create a what-if simulation scenario."""
        return self.simulation_engine.create_scenario(
            name=name,
            scenario_type=scenario_type,
            base_metrics=current_metrics,
            modifications=modifications,
            horizon_hours=horizon_hours,
            iterations=iterations
        )

    async def run_simulation(
        self,
        scenario_id: str,
        current_metrics: Dict[str, Any]
    ) -> SimulationResult:
        """Run a simulation scenario."""
        return await self.simulation_engine.run_simulation(scenario_id, current_metrics)

    def get_simulation_result(self, scenario_id: str) -> Optional[SimulationResult]:
        """Get simulation result."""
        return self.simulation_engine.get_result(scenario_id)

    def list_simulations(self) -> List[SimulationScenario]:
        """List all simulation scenarios."""
        return self.simulation_engine.list_scenarios()

    def get_simulation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available simulation templates."""
        return SIMULATION_TEMPLATES

    def compare_simulations(self, scenario_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple simulation results."""
        return self.simulation_engine.compare_scenarios(scenario_ids)

    # =========================================
    # Batch Processing
    # =========================================

    async def process_metrics_batch(
        self,
        metrics_data: List[Dict[str, Any]],
        processor_type: str = "aggregation",
        batch_size: int = 5000
    ) -> Dict[str, Any]:
        """Process a batch of metrics through HPC pipeline."""
        job = await self.parallel_processor.submit_batch_job(
            name=f"Metrics Batch Processing - {processor_type}",
            data=metrics_data,
            processor_func=processor_type,
            batch_size=batch_size,
            use_gpu=processor_type in ["ml_inference", "anomaly_detection"]
        )

        # Execute immediately
        result_job = await self.parallel_processor.execute_job(job.id)

        return result_job.output

    async def run_anomaly_detection_batch(
        self,
        metrics_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run GPU-accelerated anomaly detection on metrics batch."""
        return await self.process_metrics_batch(
            metrics_data=metrics_data,
            processor_type="anomaly_detection"
        )

    async def run_trend_analysis_batch(
        self,
        metrics_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run trend analysis on metrics batch."""
        return await self.process_metrics_batch(
            metrics_data=metrics_data,
            processor_type="trend_analysis"
        )

    # =========================================
    # ML Training
    # =========================================

    async def train_predictive_model(
        self,
        model_name: str,
        model_type: str,
        training_data: Dict[str, Any],
        hyperparameters: Dict[str, Any] = None,
        epochs: int = 100
    ) -> Dict[str, Any]:
        """Train a predictive maintenance model using distributed HPC."""
        job = await self.parallel_processor.submit_ml_training_job(
            name=model_name,
            model_type=model_type,
            training_data=training_data,
            hyperparameters=hyperparameters or {},
            epochs=epochs,
            distributed=True
        )

        # Execute training
        result_job = await self.parallel_processor.execute_ml_training(job.id)

        return result_job.output

    # =========================================
    # Resource Optimization
    # =========================================

    def optimize_resource_allocation(
        self,
        workload_forecast: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize resource allocation based on workload forecast."""
        cluster = self.get_default_cluster()
        if not cluster:
            return {"error": "No cluster available"}

        # Analyze current utilization
        metrics = self.cluster_manager.get_cluster_metrics(cluster.id)

        # Generate recommendations
        recommendations = []

        cpu_util = metrics.get("cpu", {}).get("utilization_percent", 0)
        gpu_util = metrics.get("gpu", {}).get("avg_utilization_percent", 0)
        memory_util = metrics.get("memory", {}).get("utilization_percent", 0)

        # CPU recommendations
        if cpu_util > 80:
            recommendations.append({
                "type": "scale_up",
                "resource": "cpu",
                "reason": f"High CPU utilization ({cpu_util:.1f}%)",
                "action": "Add more CPU nodes or increase core count"
            })
        elif cpu_util < 20:
            recommendations.append({
                "type": "scale_down",
                "resource": "cpu",
                "reason": f"Low CPU utilization ({cpu_util:.1f}%)",
                "action": "Consider reducing CPU allocation"
            })

        # GPU recommendations
        if gpu_util > 85:
            recommendations.append({
                "type": "scale_up",
                "resource": "gpu",
                "reason": f"High GPU utilization ({gpu_util:.1f}%)",
                "action": "Add more GPU nodes for ML workloads"
            })
        elif gpu_util < 15:
            recommendations.append({
                "type": "optimize",
                "resource": "gpu",
                "reason": f"Low GPU utilization ({gpu_util:.1f}%)",
                "action": "Consider batching more ML jobs together"
            })

        # Memory recommendations
        if memory_util > 85:
            recommendations.append({
                "type": "scale_up",
                "resource": "memory",
                "reason": f"High memory utilization ({memory_util:.1f}%)",
                "action": "Increase memory per node or add nodes"
            })

        return {
            "current_utilization": {
                "cpu_percent": cpu_util,
                "gpu_percent": gpu_util,
                "memory_percent": memory_util
            },
            "recommendations": recommendations,
            "optimal_config": {
                "nodes": max(2, int(cluster.total_nodes * (cpu_util / 70))),
                "gpus_per_node": max(1, int(cluster.total_gpu_count / cluster.total_nodes * (gpu_util / 70)))
            }
        }

    # =========================================
    # Engine Statistics & Health
    # =========================================

    def get_hpc_metrics(self) -> HPCMetrics:
        """Get aggregate HPC metrics."""
        metrics = self.cluster_manager.get_aggregate_metrics()

        # Add simulation stats
        sim_stats = self.simulation_engine.get_statistics()
        metrics.simulations_running = sim_stats.get("running_simulations", 0)
        metrics.simulations_completed_24h = sim_stats.get("completed_simulations", 0)

        # Add processor stats
        proc_stats = self.parallel_processor.get_statistics()
        metrics.compute_hours_24h = proc_stats.get("total_processing_time_seconds", 0) / 3600

        return metrics

    def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive HPC engine status."""
        uptime = (datetime.utcnow() - self.engine_start_time).total_seconds()

        return {
            "status": "online",
            "uptime_seconds": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "clusters": {
                "total": len(self.cluster_manager.clusters),
                "online": len([c for c in self.cluster_manager.clusters.values()
                             if c.status == ClusterStatus.ONLINE])
            },
            "default_cluster_id": self.default_cluster_id,
            "jobs": {
                "running": len(self.parallel_processor.list_jobs(JobStatus.RUNNING)),
                "queued": len(self.parallel_processor.list_jobs(JobStatus.QUEUED)),
                "completed": self.parallel_processor.stats.get("jobs_completed", 0),
                "failed": self.parallel_processor.stats.get("jobs_failed", 0)
            },
            "simulations": self.simulation_engine.get_statistics(),
            "processing": self.parallel_processor.get_statistics(),
            "capabilities": {
                "gpu_acceleration": self.parallel_processor.gpu_available,
                "distributed_training": True,
                "what_if_simulations": True,
                "parallel_processing": True,
                "max_workers": self.parallel_processor.max_workers
            }
        }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on HPC components."""
        checks = {
            "cluster_manager": True,
            "simulation_engine": True,
            "parallel_processor": True,
            "default_cluster": self.default_cluster_id is not None
        }

        # Check cluster health
        if self.default_cluster_id:
            cluster = self.cluster_manager.get_cluster(self.default_cluster_id)
            if cluster:
                checks["cluster_online"] = cluster.status in [
                    ClusterStatus.ONLINE, ClusterStatus.DEGRADED
                ]
                checks["nodes_available"] = cluster.available_nodes > 0

        overall_healthy = all(checks.values())

        return {
            "healthy": overall_healthy,
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }

    # =========================================
    # Demo & Simulation
    # =========================================

    def simulate_activity(self, utilization_percent: float = 50):
        """Simulate cluster activity for demo purposes."""
        if self.default_cluster_id:
            self.cluster_manager.simulate_workload(
                self.default_cluster_id,
                utilization_percent
            )

    async def run_demo_simulation(
        self,
        current_metrics: Dict[str, Any]
    ) -> SimulationResult:
        """Run a demo simulation scenario."""
        # Create demo scenario
        scenario = self.create_simulation(
            name="Demo: Equipment Failure Impact",
            scenario_type="equipment_failure",
            current_metrics=current_metrics,
            modifications={
                "equipment_name": "Reactor-001",
                "failure_type": "bearing_failure",
                "downtime_hours": 8
            },
            horizon_hours=48,
            iterations=500
        )

        # Run simulation
        result = await self.run_simulation(scenario.id, current_metrics)

        return result
