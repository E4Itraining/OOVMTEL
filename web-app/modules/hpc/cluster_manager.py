"""
Cluster Manager - Manages HPC cluster resources and nodes
"""

import uuid
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .models import (
    HPCCluster,
    HPCNode,
    HPCJob,
    GPUDevice,
    HPCMetrics,
    ClusterStatus,
    NodeStatus,
    JobStatus,
    JobPriority,
    ComputeBackend,
    HPC_PRESETS,
)

logger = logging.getLogger(__name__)


class ClusterManager:
    """
    Manages HPC cluster resources including nodes, GPUs, and job scheduling.

    Features:
    - Dynamic cluster provisioning
    - Node health monitoring
    - Resource allocation
    - Job queue management
    - Load balancing
    """

    def __init__(self):
        self.clusters: Dict[str, HPCCluster] = {}
        self.jobs: Dict[str, HPCJob] = {}
        self.job_queue: List[str] = []  # Job IDs in queue order

        # Statistics
        self.total_jobs_completed = 0
        self.total_compute_hours = 0

        logger.info("Cluster Manager initialized")

    def create_cluster(
        self,
        name: str,
        preset: str = "medium",
        description: str = ""
    ) -> HPCCluster:
        """Create a new HPC cluster from a preset."""
        cluster_id = f"HPC-{uuid.uuid4().hex[:8].upper()}"

        preset_config = HPC_PRESETS.get(preset, HPC_PRESETS["medium"])

        # Create nodes
        nodes = []
        for i in range(preset_config["nodes"]):
            node = self._create_node(
                node_index=i,
                cpu_cores=preset_config["cpu_cores_per_node"],
                memory_gb=preset_config["memory_gb_per_node"],
                gpu_count=preset_config["gpus_per_node"],
                gpu_memory_gb=preset_config["gpu_memory_gb"]
            )
            nodes.append(node)

        # Calculate totals
        total_cpus = sum(n.cpu_cores for n in nodes)
        total_memory = sum(n.memory_total_gb for n in nodes)
        total_gpus = sum(len(n.gpus) for n in nodes)
        total_gpu_memory = sum(n.total_gpu_memory_gb for n in nodes)

        cluster = HPCCluster(
            id=cluster_id,
            name=name,
            description=description or preset_config["description"],
            status=ClusterStatus.ONLINE,
            nodes=nodes,
            total_nodes=len(nodes),
            available_nodes=len(nodes),
            total_cpu_cores=total_cpus,
            total_memory_gb=total_memory,
            total_gpu_count=total_gpus,
            total_gpu_memory_gb=total_gpu_memory
        )

        self.clusters[cluster_id] = cluster
        logger.info(f"Created cluster {cluster_id} with {len(nodes)} nodes")

        return cluster

    def _create_node(
        self,
        node_index: int,
        cpu_cores: int,
        memory_gb: float,
        gpu_count: int,
        gpu_memory_gb: float
    ) -> HPCNode:
        """Create a compute node with GPUs."""
        node_id = f"NODE-{uuid.uuid4().hex[:8].upper()}"

        # Create GPUs
        gpus = []
        gpu_vendors = ["NVIDIA", "AMD"]
        gpu_models = {
            "NVIDIA": ["A100", "H100", "V100", "RTX 4090"],
            "AMD": ["MI250X", "MI300X", "Instinct"]
        }

        for g in range(gpu_count):
            vendor = random.choice(gpu_vendors)
            model = random.choice(gpu_models[vendor])

            gpu = GPUDevice(
                id=f"GPU-{uuid.uuid4().hex[:6].upper()}",
                name=f"{vendor} {model}",
                vendor=vendor,
                memory_total_gb=gpu_memory_gb,
                memory_available_gb=gpu_memory_gb,
                compute_capability="8.0" if vendor == "NVIDIA" else "N/A",
                driver_version="535.104.05" if vendor == "NVIDIA" else "6.1.0",
                temperature_celsius=random.uniform(35, 55),
                utilization_percent=0,
                power_watts=random.uniform(50, 100),
                power_limit_watts=400 if "A100" in model or "H100" in model else 350,
                clock_speed_mhz=random.randint(1200, 1800)
            )
            gpus.append(gpu)

        node = HPCNode(
            id=node_id,
            hostname=f"compute-{node_index:03d}",
            ip_address=f"10.0.{node_index // 256}.{node_index % 256}",
            status=NodeStatus.AVAILABLE,
            cpu_cores=cpu_cores,
            cpu_threads=cpu_cores * 2,
            cpu_model="AMD EPYC 7763" if random.random() > 0.5 else "Intel Xeon Platinum 8380",
            memory_total_gb=memory_gb,
            memory_available_gb=memory_gb,
            gpus=gpus,
            total_gpu_memory_gb=gpu_count * gpu_memory_gb,
            storage_total_gb=2000,
            storage_used_gb=random.uniform(100, 500),
            network_bandwidth_gbps=100,
            infiniband_enabled=True,
            tags=["production", f"rack-{node_index // 4}"],
            location="datacenter-1",
            rack=f"rack-{node_index // 4}",
            last_heartbeat=datetime.utcnow()
        )

        return node

    def get_cluster(self, cluster_id: str) -> Optional[HPCCluster]:
        """Get cluster by ID."""
        return self.clusters.get(cluster_id)

    def get_all_clusters(self) -> List[HPCCluster]:
        """Get all clusters."""
        return list(self.clusters.values())

    def delete_cluster(self, cluster_id: str) -> bool:
        """Delete a cluster."""
        if cluster_id in self.clusters:
            del self.clusters[cluster_id]
            logger.info(f"Deleted cluster {cluster_id}")
            return True
        return False

    def get_node(self, cluster_id: str, node_id: str) -> Optional[HPCNode]:
        """Get a specific node."""
        cluster = self.clusters.get(cluster_id)
        if cluster:
            for node in cluster.nodes:
                if node.id == node_id:
                    return node
        return None

    def update_node_status(
        self,
        cluster_id: str,
        node_id: str,
        status: NodeStatus
    ) -> bool:
        """Update node status."""
        node = self.get_node(cluster_id, node_id)
        if node:
            node.status = status
            node.last_heartbeat = datetime.utcnow()
            self._update_cluster_availability(cluster_id)
            return True
        return False

    def _update_cluster_availability(self, cluster_id: str):
        """Update cluster availability counts."""
        cluster = self.clusters.get(cluster_id)
        if cluster:
            cluster.available_nodes = len([
                n for n in cluster.nodes
                if n.status == NodeStatus.AVAILABLE
            ])

            # Update cluster status based on node availability
            if cluster.available_nodes == 0:
                cluster.status = ClusterStatus.OFFLINE
            elif cluster.available_nodes < cluster.total_nodes * 0.5:
                cluster.status = ClusterStatus.DEGRADED
            else:
                cluster.status = ClusterStatus.ONLINE

    def submit_job(self, job: HPCJob, cluster_id: str) -> HPCJob:
        """Submit a job to the cluster queue."""
        cluster = self.clusters.get(cluster_id)
        if not cluster:
            raise ValueError(f"Cluster {cluster_id} not found")

        # Validate resource requirements
        if job.total_gpu_count > cluster.total_gpu_count:
            raise ValueError("Job requires more GPUs than available in cluster")

        if job.total_memory_gb > cluster.total_memory_gb:
            raise ValueError("Job requires more memory than available in cluster")

        # Add to queue
        self.jobs[job.id] = job
        self.job_queue.append(job.id)
        cluster.jobs_queued += 1

        logger.info(f"Submitted job {job.id} to cluster {cluster_id}")

        return job

    def get_job(self, job_id: str) -> Optional[HPCJob]:
        """Get job by ID."""
        return self.jobs.get(job_id)

    def get_job_queue(self, cluster_id: str) -> List[HPCJob]:
        """Get jobs in queue for a cluster."""
        return [
            self.jobs[jid] for jid in self.job_queue
            if jid in self.jobs and self.jobs[jid].status == JobStatus.QUEUED
        ]

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        job = self.jobs.get(job_id)
        if job and job.status in [JobStatus.QUEUED, JobStatus.PENDING]:
            job.status = JobStatus.CANCELLED
            if job_id in self.job_queue:
                self.job_queue.remove(job_id)
            return True
        return False

    def allocate_resources(
        self,
        cluster_id: str,
        cpu_cores: int,
        memory_gb: float,
        gpu_count: int = 0
    ) -> List[HPCNode]:
        """Allocate resources from available nodes."""
        cluster = self.clusters.get(cluster_id)
        if not cluster:
            return []

        allocated_nodes = []
        remaining_cpus = cpu_cores
        remaining_memory = memory_gb
        remaining_gpus = gpu_count

        for node in cluster.nodes:
            if node.status != NodeStatus.AVAILABLE:
                continue

            # Check if node can contribute
            available_cpus = node.cpu_cores - int(node.cpu_usage_percent / 100 * node.cpu_cores)
            available_memory = node.memory_available_gb
            available_gpus = len([g for g in node.gpus if g.status == NodeStatus.AVAILABLE])

            if available_cpus > 0 or available_memory > 0 or available_gpus > 0:
                allocated_nodes.append(node)
                remaining_cpus -= available_cpus
                remaining_memory -= available_memory
                remaining_gpus -= available_gpus

                # Mark node as busy
                node.status = NodeStatus.BUSY

                if remaining_cpus <= 0 and remaining_memory <= 0 and remaining_gpus <= 0:
                    break

        return allocated_nodes

    def release_resources(self, nodes: List[HPCNode]):
        """Release allocated resources."""
        for node in nodes:
            node.status = NodeStatus.AVAILABLE
            for gpu in node.gpus:
                gpu.status = NodeStatus.AVAILABLE

    def get_cluster_metrics(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed metrics for a cluster."""
        cluster = self.clusters.get(cluster_id)
        if not cluster:
            return None

        # Calculate utilization
        total_cpu_used = sum(n.cpu_usage_percent * n.cpu_cores / 100 for n in cluster.nodes)
        total_memory_used = sum(n.memory_used_gb for n in cluster.nodes)
        total_gpu_util = 0
        gpu_count = 0
        for node in cluster.nodes:
            for gpu in node.gpus:
                total_gpu_util += gpu.utilization_percent
                gpu_count += 1

        return {
            "cluster_id": cluster_id,
            "status": cluster.status.value,
            "nodes": {
                "total": cluster.total_nodes,
                "available": cluster.available_nodes,
                "busy": len([n for n in cluster.nodes if n.status == NodeStatus.BUSY]),
                "offline": len([n for n in cluster.nodes if n.status == NodeStatus.OFFLINE])
            },
            "cpu": {
                "total_cores": cluster.total_cpu_cores,
                "used_cores": int(total_cpu_used),
                "utilization_percent": (total_cpu_used / cluster.total_cpu_cores * 100) if cluster.total_cpu_cores > 0 else 0
            },
            "memory": {
                "total_gb": cluster.total_memory_gb,
                "used_gb": total_memory_used,
                "utilization_percent": (total_memory_used / cluster.total_memory_gb * 100) if cluster.total_memory_gb > 0 else 0
            },
            "gpu": {
                "total_count": cluster.total_gpu_count,
                "total_memory_gb": cluster.total_gpu_memory_gb,
                "avg_utilization_percent": (total_gpu_util / gpu_count) if gpu_count > 0 else 0
            },
            "jobs": {
                "queued": cluster.jobs_queued,
                "running": cluster.jobs_running,
                "completed_24h": cluster.jobs_completed_24h
            },
            "performance": {
                "avg_queue_time_seconds": cluster.avg_queue_time_seconds,
                "avg_execution_time_seconds": cluster.avg_execution_time_seconds,
                "throughput_jobs_per_hour": cluster.throughput_jobs_per_hour
            }
        }

    def get_aggregate_metrics(self) -> HPCMetrics:
        """Get aggregate metrics across all clusters."""
        metrics = HPCMetrics()

        metrics.total_clusters = len(self.clusters)

        for cluster in self.clusters.values():
            metrics.total_nodes += cluster.total_nodes
            metrics.total_gpus += cluster.total_gpu_count
            metrics.jobs_queued += cluster.jobs_queued
            metrics.jobs_running += cluster.jobs_running
            metrics.jobs_completed_24h += cluster.jobs_completed_24h

            # Aggregate utilization (weighted average)
            if cluster.total_nodes > 0:
                weight = cluster.total_nodes / max(1, metrics.total_nodes)
                metrics.cpu_utilization_avg += cluster.cpu_utilization_percent * weight
                metrics.memory_utilization_avg += cluster.memory_utilization_percent * weight
                metrics.gpu_utilization_avg += cluster.gpu_utilization_percent * weight

        # Node health
        for cluster in self.clusters.values():
            for node in cluster.nodes:
                if node.status == NodeStatus.AVAILABLE or node.status == NodeStatus.BUSY:
                    metrics.nodes_healthy += 1
                elif node.status == NodeStatus.DRAINING:
                    metrics.nodes_warning += 1
                else:
                    metrics.nodes_error += 1

        metrics.collected_at = datetime.utcnow()

        return metrics

    def simulate_workload(self, cluster_id: str, utilization_percent: float = 50):
        """Simulate cluster workload for demo purposes."""
        cluster = self.clusters.get(cluster_id)
        if not cluster:
            return

        for node in cluster.nodes:
            # Simulate CPU usage
            node.cpu_usage_percent = random.uniform(
                utilization_percent * 0.5,
                min(utilization_percent * 1.5, 100)
            )

            # Simulate memory usage
            node.memory_used_gb = node.memory_total_gb * random.uniform(0.3, 0.8)
            node.memory_available_gb = node.memory_total_gb - node.memory_used_gb

            # Simulate GPU usage
            for gpu in node.gpus:
                gpu.utilization_percent = random.uniform(
                    utilization_percent * 0.6,
                    min(utilization_percent * 1.4, 100)
                )
                gpu.memory_used_gb = gpu.memory_total_gb * (gpu.utilization_percent / 100)
                gpu.memory_available_gb = gpu.memory_total_gb - gpu.memory_used_gb
                gpu.temperature_celsius = 40 + (gpu.utilization_percent * 0.4)
                gpu.power_watts = 100 + (gpu.utilization_percent * 2.5)

            node.last_heartbeat = datetime.utcnow()

        # Update cluster-level metrics
        cluster.cpu_utilization_percent = sum(
            n.cpu_usage_percent for n in cluster.nodes
        ) / len(cluster.nodes)

        cluster.memory_utilization_percent = sum(
            n.memory_used_gb / n.memory_total_gb * 100 for n in cluster.nodes
        ) / len(cluster.nodes)

        total_gpu_util = 0
        gpu_count = 0
        for node in cluster.nodes:
            for gpu in node.gpus:
                total_gpu_util += gpu.utilization_percent
                gpu_count += 1

        cluster.gpu_utilization_percent = total_gpu_util / gpu_count if gpu_count > 0 else 0

        # Simulate job activity
        cluster.jobs_running = int(utilization_percent / 10)
        cluster.jobs_queued = random.randint(0, 20)
        cluster.jobs_completed_24h = random.randint(50, 200)
        cluster.throughput_jobs_per_hour = cluster.jobs_completed_24h / 24
        cluster.avg_queue_time_seconds = random.uniform(30, 300)
        cluster.avg_execution_time_seconds = random.uniform(600, 3600)

        cluster.updated_at = datetime.utcnow()
