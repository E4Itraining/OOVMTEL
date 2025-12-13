"""
Edge Agent - Main edge computing agent
"""

import uuid
import time
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque

from .models import (
    EdgeConfig,
    EdgeMetrics,
    EdgeStatus,
    DataBuffer,
    AggregatedData,
    EdgeAlert,
    SyncStatus,
    ModelDeployment,
    DataPoint,
    AggregationType,
)
from .processor import EdgeProcessor
from .buffer_manager import BufferManager
from .sync_manager import SyncManager

logger = logging.getLogger(__name__)


class EdgeAgent:
    """
    Main Edge Computing Agent.

    Features:
    - Local data collection and aggregation
    - Offline buffering
    - Edge-based anomaly detection
    - Model inference at edge
    - Sync with central platform
    """

    def __init__(self, config: EdgeConfig):
        self.config = config
        self.status = EdgeStatus.OFFLINE
        self.start_time = datetime.utcnow()

        # Components
        self.processor = EdgeProcessor(
            anomaly_threshold=config.anomaly_threshold,
            local_alerting=config.local_alerting
        )
        self.buffer_manager = BufferManager(
            max_size_mb=config.buffer_size_mb,
            retention_hours=config.buffer_retention_hours
        )
        self.sync_manager = SyncManager(
            central_url=config.central_url,
            api_key=config.api_key,
            batch_size=config.sync_batch_size,
            compression=config.compression_enabled
        )

        # Data queues
        self.raw_data_queue: deque = deque(maxlen=10000)
        self.aggregated_data: List[AggregatedData] = []
        self.pending_alerts: List[EdgeAlert] = []

        # Metrics
        self.metrics = EdgeMetrics()
        self.metrics.uptime_seconds = 0

        # Model deployments
        self.deployed_models: Dict[str, ModelDeployment] = {}

        # State
        self.last_sync_time: Optional[datetime] = None
        self.is_offline = False
        self.running = False

        logger.info(f"Edge Agent {config.agent_id} initialized for site {config.site_name}")

    async def start(self):
        """Start the edge agent."""
        self.running = True
        self.status = EdgeStatus.ONLINE

        logger.info(f"Starting edge agent {self.config.agent_id}")

        # Start background tasks
        asyncio.create_task(self._collection_loop())
        asyncio.create_task(self._aggregation_loop())
        asyncio.create_task(self._sync_loop())
        asyncio.create_task(self._metrics_loop())

    async def stop(self):
        """Stop the edge agent."""
        self.running = False
        self.status = EdgeStatus.OFFLINE

        # Flush remaining data
        await self._flush_buffer()

        logger.info(f"Edge agent {self.config.agent_id} stopped")

    async def collect_data(self, data_points: List[DataPoint]):
        """Collect data points from sensors/sources."""
        for dp in data_points:
            self.raw_data_queue.append(dp)
            self.metrics.data_points_collected += 1

        # Immediate anomaly detection if enabled
        if self.config.local_anomaly_detection:
            alerts = self.processor.detect_anomalies(data_points)
            self.pending_alerts.extend(alerts)
            self.metrics.anomalies_detected += len(alerts)

    def get_metrics(self) -> EdgeMetrics:
        """Get current agent metrics."""
        self.metrics.uptime_seconds = int(
            (datetime.utcnow() - self.start_time).total_seconds()
        )
        return self.metrics

    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "agent_id": self.config.agent_id,
            "site_name": self.config.site_name,
            "status": self.status.value,
            "is_offline": self.is_offline,
            "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "buffer_size": self.buffer_manager.get_size(),
            "pending_data": len(self.aggregated_data),
            "pending_alerts": len(self.pending_alerts),
            "deployed_models": len(self.deployed_models),
            "metrics": self.get_metrics().model_dump()
        }

    def get_alerts(self, unsynced_only: bool = False) -> List[EdgeAlert]:
        """Get alerts generated at edge."""
        if unsynced_only:
            return [a for a in self.pending_alerts if not a.synced]
        return self.pending_alerts

    async def deploy_model(self, model: ModelDeployment) -> bool:
        """Deploy a model to the edge."""
        if not self.config.models_enabled:
            logger.warning("Models are disabled on this agent")
            return False

        self.deployed_models[model.id] = model
        self.metrics.models_deployed = len(self.deployed_models)

        logger.info(f"Deployed model {model.id} ({model.name} v{model.version})")
        return True

    async def run_inference(
        self,
        model_id: str,
        input_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Run inference on a deployed model."""
        model = self.deployed_models.get(model_id)
        if not model:
            logger.warning(f"Model {model_id} not found")
            return None

        # Simulate model inference
        # In production, this would load and run actual ML model
        result = self.processor.run_model_inference(model, input_data)
        model.predictions_made += 1

        return result

    async def _collection_loop(self):
        """Background loop for data collection."""
        while self.running:
            await asyncio.sleep(self.config.collection_interval_seconds)

            # In production, this would collect from actual sensors
            # For now, we process any data in the queue
            self._process_raw_data()

    async def _aggregation_loop(self):
        """Background loop for data aggregation."""
        while self.running:
            await asyncio.sleep(self.config.aggregation_interval_seconds)

            # Aggregate collected data
            aggregated = self._aggregate_data()
            self.aggregated_data.extend(aggregated)
            self.metrics.data_points_aggregated += len(aggregated)

    async def _sync_loop(self):
        """Background loop for syncing with central."""
        while self.running:
            await asyncio.sleep(self.config.sync_interval_seconds)

            if self.aggregated_data or self.pending_alerts:
                success = await self._sync_data()

                if success:
                    self.last_sync_time = datetime.utcnow()
                    self.is_offline = False
                    self.status = EdgeStatus.ONLINE
                else:
                    # Buffer data for later sync
                    await self._buffer_data()

                    # Check if we've been offline too long
                    if self.last_sync_time:
                        offline_seconds = (
                            datetime.utcnow() - self.last_sync_time
                        ).total_seconds()
                        if offline_seconds > self.config.offline_mode_threshold_seconds:
                            self.is_offline = True
                            self.status = EdgeStatus.OFFLINE

    async def _metrics_loop(self):
        """Background loop for collecting agent metrics."""
        while self.running:
            await asyncio.sleep(60)  # Every minute

            # Update metrics
            self.metrics.data_points_buffered = self.buffer_manager.get_data_points_count()
            # In production, would collect actual CPU/memory usage

    def _process_raw_data(self):
        """Process raw data from queue."""
        # Process up to 1000 points at a time
        processed = 0
        while self.raw_data_queue and processed < 1000:
            dp = self.raw_data_queue.popleft()
            # Data point is already collected, just counting
            processed += 1

    def _aggregate_data(self) -> List[AggregatedData]:
        """Aggregate collected data points."""
        if not self.raw_data_queue:
            return []

        aggregated = []
        now = datetime.utcnow()
        interval = timedelta(seconds=self.config.aggregation_interval_seconds)

        # Group by metric and equipment
        groups: Dict[str, List[DataPoint]] = {}
        while self.raw_data_queue:
            dp = self.raw_data_queue.popleft()
            key = f"{dp.metric}:{dp.equipment or 'none'}"
            if key not in groups:
                groups[key] = []
            groups[key].append(dp)

        # Aggregate each group
        for key, points in groups.items():
            if not points:
                continue

            values = [p.value for p in points]
            metric, equipment = key.split(":", 1)
            equipment = None if equipment == "none" else equipment

            agg = AggregatedData(
                start_time=now - interval,
                end_time=now,
                metric=metric,
                equipment=equipment,
                count=len(values),
                sum=sum(values),
                min=min(values),
                max=max(values),
                avg=sum(values) / len(values),
                source_agent=self.config.agent_id,
                labels=points[0].labels if points else {}
            )

            # Calculate percentiles if enough data
            if len(values) >= 10:
                sorted_values = sorted(values)
                agg.p50 = sorted_values[len(sorted_values) // 2]
                agg.p95 = sorted_values[int(len(sorted_values) * 0.95)]
                agg.p99 = sorted_values[int(len(sorted_values) * 0.99)]

            aggregated.append(agg)

        return aggregated

    async def _sync_data(self) -> bool:
        """Sync data with central platform."""
        self.status = EdgeStatus.SYNCING

        try:
            # Sync aggregated data
            if self.aggregated_data:
                success = await self.sync_manager.sync_data(self.aggregated_data)
                if success:
                    synced_count = len(self.aggregated_data)
                    self.metrics.data_points_synced += synced_count
                    self.aggregated_data.clear()

            # Sync alerts
            if self.pending_alerts:
                unsynced = [a for a in self.pending_alerts if not a.synced]
                if unsynced:
                    success = await self.sync_manager.sync_alerts(unsynced)
                    if success:
                        for alert in unsynced:
                            alert.synced = True
                        self.metrics.alerts_generated += len(unsynced)

            # Sync buffered data
            buffered = self.buffer_manager.get_pending_sync()
            if buffered:
                success = await self.sync_manager.sync_buffered(buffered)
                if success:
                    self.buffer_manager.mark_synced(buffered)

            return True

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            self.metrics.errors_count += 1
            return False

    async def _buffer_data(self):
        """Buffer data when offline."""
        if self.aggregated_data:
            self.buffer_manager.add_data(self.aggregated_data)
            self.aggregated_data.clear()

    async def _flush_buffer(self):
        """Flush remaining buffer before shutdown."""
        # Try one final sync
        await self._sync_data()

        # Buffer any remaining data
        await self._buffer_data()


class EdgeAgentManager:
    """
    Manages multiple edge agents from central platform.
    """

    def __init__(self):
        self.agents: Dict[str, EdgeSite] = {}

    def register_agent(
        self,
        agent_id: str,
        site_name: str,
        config: EdgeConfig
    ) -> Dict[str, Any]:
        """Register a new edge agent."""
        from .models import EdgeSite

        site = EdgeSite(
            agent_id=agent_id,
            site_name=site_name,
            location=config.location,
            config=config
        )
        self.agents[agent_id] = site

        return {
            "agent_id": agent_id,
            "status": "registered",
            "config": config.model_dump()
        }

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent."""
        site = self.agents.get(agent_id)
        if not site:
            return None

        return {
            "agent_id": site.agent_id,
            "site_name": site.site_name,
            "status": site.status.value,
            "last_seen": site.last_seen.isoformat() if site.last_seen else None,
            "alerts": len(site.active_alerts),
            "models": len(site.deployed_models)
        }

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get status of all agents."""
        return [
            self.get_agent_status(agent_id)
            for agent_id in self.agents
        ]

    def update_agent_heartbeat(
        self,
        agent_id: str,
        metrics: EdgeMetrics
    ):
        """Update agent heartbeat and metrics."""
        site = self.agents.get(agent_id)
        if site:
            site.last_seen = datetime.utcnow()
            site.status = EdgeStatus.ONLINE
            site.metrics = metrics

    def push_model_to_agent(
        self,
        agent_id: str,
        model: ModelDeployment
    ) -> bool:
        """Push a model deployment to an agent."""
        site = self.agents.get(agent_id)
        if not site:
            return False

        site.deployed_models.append(model)
        return True

    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics from all agents."""
        online_count = len([
            a for a in self.agents.values()
            if a.status == EdgeStatus.ONLINE
        ])

        total_data_points = sum(
            a.metrics.data_points_collected if a.metrics else 0
            for a in self.agents.values()
        )

        total_alerts = sum(
            len(a.active_alerts)
            for a in self.agents.values()
        )

        return {
            "total_agents": len(self.agents),
            "online_agents": online_count,
            "offline_agents": len(self.agents) - online_count,
            "total_data_points": total_data_points,
            "total_alerts": total_alerts
        }
