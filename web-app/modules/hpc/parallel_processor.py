"""
Parallel Processor - Distributed batch processing and ML training
"""

import uuid
import time
import logging
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

from .models import (
    HPCJob,
    ComputeTask,
    JobStatus,
    JobPriority,
    ComputeBackend,
)

logger = logging.getLogger(__name__)


class ParallelProcessor:
    """
    Parallel Processing Engine for distributed batch operations.

    Features:
    - Multi-threaded/multi-process execution
    - GPU-accelerated processing (when available)
    - Batch optimization for time-series data
    - Distributed ML model training
    - Real-time stream processing
    """

    def __init__(
        self,
        max_workers: int = None,
        use_gpu: bool = True
    ):
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.use_gpu = use_gpu

        # Executors
        self.thread_executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=self.max_workers)

        # Active jobs
        self.active_jobs: Dict[str, HPCJob] = {}
        self.job_results: Dict[str, Dict[str, Any]] = {}

        # Statistics
        self.stats = {
            "jobs_completed": 0,
            "jobs_failed": 0,
            "total_processing_time_seconds": 0,
            "total_data_points_processed": 0
        }

        # GPU availability (simulated)
        self.gpu_available = use_gpu
        self.gpu_memory_gb = 16 if use_gpu else 0

        logger.info(f"Parallel Processor initialized with {self.max_workers} workers")

    async def submit_batch_job(
        self,
        name: str,
        data: List[Dict[str, Any]],
        processor_func: str,
        batch_size: int = 1000,
        priority: JobPriority = JobPriority.NORMAL,
        use_gpu: bool = False
    ) -> HPCJob:
        """Submit a batch processing job."""
        job_id = f"JOB-{uuid.uuid4().hex[:8].upper()}"

        # Create tasks for each batch
        tasks = []
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            task = ComputeTask(
                id=f"TASK-{uuid.uuid4().hex[:6].upper()}",
                name=f"Batch {i // batch_size + 1}",
                type="batch_processing",
                cpu_cores=1,
                memory_gb=2,
                gpu_count=1 if use_gpu else 0,
                input_data={"batch": batch, "processor": processor_func}
            )
            tasks.append(task)

        job = HPCJob(
            id=job_id,
            name=name,
            description=f"Batch processing job with {len(tasks)} tasks",
            priority=priority,
            backend=ComputeBackend.CUDA if use_gpu else ComputeBackend.CPU,
            tasks=tasks,
            parallel_tasks=min(len(tasks), self.max_workers),
            total_cpu_cores=len(tasks),
            total_memory_gb=len(tasks) * 2,
            total_gpu_count=len(tasks) if use_gpu else 0
        )

        self.active_jobs[job_id] = job
        logger.info(f"Submitted batch job {job_id} with {len(tasks)} tasks")

        return job

    async def execute_job(self, job_id: str) -> HPCJob:
        """Execute a submitted job."""
        job = self.active_jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        start_time = time.time()

        try:
            # Execute tasks in parallel
            results = await self._execute_tasks_parallel(job)

            # Aggregate results
            job.output = {
                "task_results": results,
                "total_processed": sum(r.get("processed", 0) for r in results),
                "total_errors": sum(r.get("errors", 0) for r in results)
            }

            job.status = JobStatus.COMPLETED
            job.tasks_completed = len(job.tasks)
            self.stats["jobs_completed"] += 1

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            self.stats["jobs_failed"] += 1
            logger.error(f"Job {job_id} failed: {e}")

        finally:
            job.completed_at = datetime.utcnow()
            job.progress_percent = 100

            processing_time = time.time() - start_time
            self.stats["total_processing_time_seconds"] += processing_time

        self.job_results[job_id] = job.output

        return job

    async def _execute_tasks_parallel(
        self,
        job: HPCJob
    ) -> List[Dict[str, Any]]:
        """Execute tasks in parallel."""
        results = []
        semaphore = asyncio.Semaphore(job.parallel_tasks)

        async def execute_with_semaphore(task: ComputeTask):
            async with semaphore:
                return await self._execute_single_task(task)

        # Execute all tasks
        task_coroutines = [
            execute_with_semaphore(task) for task in job.tasks
        ]

        completed = 0
        for coro in asyncio.as_completed(task_coroutines):
            result = await coro
            results.append(result)
            completed += 1
            job.progress_percent = (completed / len(job.tasks)) * 100

        return results

    async def _execute_single_task(
        self,
        task: ComputeTask
    ) -> Dict[str, Any]:
        """Execute a single compute task."""
        task.status = JobStatus.RUNNING
        task.started_at = datetime.utcnow()

        try:
            # Simulate processing
            batch = task.input_data.get("batch", [])
            processor = task.input_data.get("processor", "default")

            # Simulate different processing types
            if processor == "anomaly_detection":
                result = await self._process_anomaly_detection(batch)
            elif processor == "trend_analysis":
                result = await self._process_trend_analysis(batch)
            elif processor == "ml_inference":
                result = await self._process_ml_inference(batch)
            elif processor == "aggregation":
                result = await self._process_aggregation(batch)
            else:
                result = await self._process_default(batch)

            task.status = JobStatus.COMPLETED
            task.result = result
            task.progress_percent = 100

            self.stats["total_data_points_processed"] += len(batch)

            return result

        except Exception as e:
            task.status = JobStatus.FAILED
            task.error_message = str(e)
            return {"error": str(e), "processed": 0}

        finally:
            task.completed_at = datetime.utcnow()

    async def _process_anomaly_detection(
        self,
        batch: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process batch for anomaly detection."""
        # Simulate GPU-accelerated anomaly detection
        await asyncio.sleep(0.1)  # Simulate processing time

        anomalies = []
        for i, item in enumerate(batch):
            if random.random() < 0.05:  # 5% anomaly rate
                anomalies.append({
                    "index": i,
                    "value": item.get("value", 0),
                    "score": random.uniform(0.8, 1.0)
                })

        return {
            "processed": len(batch),
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies[:10],  # Return top 10
            "errors": 0
        }

    async def _process_trend_analysis(
        self,
        batch: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process batch for trend analysis."""
        await asyncio.sleep(0.08)

        values = [item.get("value", 0) for item in batch if "value" in item]

        if values:
            trend = "increasing" if values[-1] > values[0] else "decreasing"
            avg = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)
        else:
            trend = "stable"
            avg = min_val = max_val = 0

        return {
            "processed": len(batch),
            "trend": trend,
            "average": avg,
            "min": min_val,
            "max": max_val,
            "errors": 0
        }

    async def _process_ml_inference(
        self,
        batch: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process batch through ML model inference."""
        await asyncio.sleep(0.15)  # ML inference takes longer

        predictions = []
        for item in batch:
            # Simulate model prediction
            prediction = {
                "input": item.get("features", {}),
                "prediction": random.uniform(0, 1),
                "confidence": random.uniform(0.7, 0.99)
            }
            predictions.append(prediction)

        return {
            "processed": len(batch),
            "predictions": len(predictions),
            "avg_confidence": sum(p["confidence"] for p in predictions) / len(predictions) if predictions else 0,
            "errors": 0
        }

    async def _process_aggregation(
        self,
        batch: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process batch for metric aggregation."""
        await asyncio.sleep(0.05)

        # Group by metric
        aggregations = {}
        for item in batch:
            metric = item.get("metric", "default")
            value = item.get("value", 0)

            if metric not in aggregations:
                aggregations[metric] = {
                    "count": 0,
                    "sum": 0,
                    "min": float('inf'),
                    "max": float('-inf')
                }

            aggregations[metric]["count"] += 1
            aggregations[metric]["sum"] += value
            aggregations[metric]["min"] = min(aggregations[metric]["min"], value)
            aggregations[metric]["max"] = max(aggregations[metric]["max"], value)

        # Calculate averages
        for metric in aggregations:
            count = aggregations[metric]["count"]
            if count > 0:
                aggregations[metric]["avg"] = aggregations[metric]["sum"] / count

        return {
            "processed": len(batch),
            "aggregations": aggregations,
            "metrics_count": len(aggregations),
            "errors": 0
        }

    async def _process_default(
        self,
        batch: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Default batch processing."""
        await asyncio.sleep(0.05)

        return {
            "processed": len(batch),
            "errors": 0
        }

    async def submit_ml_training_job(
        self,
        name: str,
        model_type: str,
        training_data: Dict[str, Any],
        hyperparameters: Dict[str, Any],
        epochs: int = 100,
        distributed: bool = True
    ) -> HPCJob:
        """Submit a distributed ML training job."""
        job_id = f"ML-{uuid.uuid4().hex[:8].upper()}"

        # Determine number of training tasks based on data size
        data_size = training_data.get("size", 10000)
        num_workers = min(self.max_workers, max(1, data_size // 10000))

        tasks = []
        for i in range(num_workers):
            task = ComputeTask(
                id=f"TRAIN-{uuid.uuid4().hex[:6].upper()}",
                name=f"Worker {i + 1}",
                type="ml_training",
                cpu_cores=4,
                memory_gb=16,
                gpu_count=1,
                gpu_memory_gb=8,
                input_data={
                    "model_type": model_type,
                    "worker_id": i,
                    "total_workers": num_workers,
                    "epochs": epochs,
                    "hyperparameters": hyperparameters,
                    "data_shard": i
                }
            )
            tasks.append(task)

        job = HPCJob(
            id=job_id,
            name=name,
            description=f"Distributed ML training: {model_type} with {num_workers} workers",
            priority=JobPriority.HIGH,
            backend=ComputeBackend.CUDA,
            tasks=tasks,
            parallel_tasks=num_workers,
            total_cpu_cores=num_workers * 4,
            total_memory_gb=num_workers * 16,
            total_gpu_count=num_workers,
            metadata={
                "model_type": model_type,
                "epochs": epochs,
                "distributed": distributed,
                "hyperparameters": hyperparameters
            }
        )

        self.active_jobs[job_id] = job
        logger.info(f"Submitted ML training job {job_id}")

        return job

    async def execute_ml_training(self, job_id: str) -> HPCJob:
        """Execute ML training job."""
        job = self.active_jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()

        epochs = job.metadata.get("epochs", 100)

        try:
            # Simulate distributed training
            training_metrics = {
                "loss": [],
                "accuracy": [],
                "val_loss": [],
                "val_accuracy": []
            }

            for epoch in range(epochs):
                # Simulate epoch processing
                await asyncio.sleep(0.02)  # Simulate training time

                # Generate realistic training curves
                epoch_metrics = {
                    "loss": max(0.1, 2.0 * (0.95 ** epoch) + random.uniform(-0.05, 0.05)),
                    "accuracy": min(0.99, 0.5 + 0.4 * (1 - 0.95 ** epoch) + random.uniform(-0.02, 0.02)),
                    "val_loss": max(0.15, 2.1 * (0.94 ** epoch) + random.uniform(-0.08, 0.08)),
                    "val_accuracy": min(0.98, 0.48 + 0.38 * (1 - 0.94 ** epoch) + random.uniform(-0.03, 0.03))
                }

                for key in training_metrics:
                    training_metrics[key].append(epoch_metrics[key])

                job.progress_percent = ((epoch + 1) / epochs) * 100

            # Final model metrics
            final_metrics = {
                "final_loss": training_metrics["loss"][-1],
                "final_accuracy": training_metrics["accuracy"][-1],
                "final_val_loss": training_metrics["val_loss"][-1],
                "final_val_accuracy": training_metrics["val_accuracy"][-1],
                "best_epoch": training_metrics["val_accuracy"].index(max(training_metrics["val_accuracy"])) + 1,
                "total_epochs": epochs
            }

            job.output = {
                "model_id": f"MODEL-{uuid.uuid4().hex[:8].upper()}",
                "training_metrics": training_metrics,
                "final_metrics": final_metrics,
                "model_size_mb": random.uniform(50, 500),
                "training_time_seconds": (datetime.utcnow() - job.started_at).total_seconds()
            }

            job.status = JobStatus.COMPLETED
            job.tasks_completed = len(job.tasks)
            self.stats["jobs_completed"] += 1

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            self.stats["jobs_failed"] += 1

        finally:
            job.completed_at = datetime.utcnow()

        self.job_results[job_id] = job.output

        return job

    def get_job(self, job_id: str) -> Optional[HPCJob]:
        """Get job by ID."""
        return self.active_jobs.get(job_id)

    def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job result."""
        return self.job_results.get(job_id)

    def list_jobs(
        self,
        status: Optional[JobStatus] = None
    ) -> List[HPCJob]:
        """List jobs, optionally filtered by status."""
        jobs = list(self.active_jobs.values())
        if status:
            jobs = [j for j in jobs if j.status == status]
        return jobs

    def get_statistics(self) -> Dict[str, Any]:
        """Get processor statistics."""
        return {
            **self.stats,
            "active_jobs": len([j for j in self.active_jobs.values() if j.status == JobStatus.RUNNING]),
            "queued_jobs": len([j for j in self.active_jobs.values() if j.status == JobStatus.QUEUED]),
            "max_workers": self.max_workers,
            "gpu_available": self.gpu_available,
            "gpu_memory_gb": self.gpu_memory_gb
        }

    def shutdown(self):
        """Shutdown executors."""
        self.thread_executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True)
        logger.info("Parallel Processor shutdown complete")
