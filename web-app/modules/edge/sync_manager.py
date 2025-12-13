"""
Sync Manager - Handles data synchronization with central platform
"""

import gzip
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from .models import AggregatedData, EdgeAlert, SyncStatus

logger = logging.getLogger(__name__)


class SyncManager:
    """
    Manages data synchronization between edge and central platform.

    Features:
    - Batched data sync
    - Compression
    - Retry logic
    - Bandwidth optimization
    """

    def __init__(
        self,
        central_url: str,
        api_key: Optional[str] = None,
        batch_size: int = 1000,
        compression: bool = True,
        max_retries: int = 3
    ):
        self.central_url = central_url
        self.api_key = api_key
        self.batch_size = batch_size
        self.compression = compression
        self.max_retries = max_retries

        # Metrics
        self.bytes_sent = 0
        self.bytes_received = 0
        self.sync_count = 0
        self.error_count = 0
        self.last_sync_time: Optional[datetime] = None
        self.last_sync_latency_ms = 0

    async def sync_data(self, data: List[AggregatedData]) -> bool:
        """Sync aggregated data to central platform."""
        if not data:
            return True

        try:
            # Split into batches
            for i in range(0, len(data), self.batch_size):
                batch = data[i:i + self.batch_size]
                success = await self._send_batch(batch, "data")

                if not success:
                    return False

            return True

        except Exception as e:
            logger.error(f"Data sync failed: {e}")
            self.error_count += 1
            return False

    async def sync_alerts(self, alerts: List[EdgeAlert]) -> bool:
        """Sync alerts to central platform."""
        if not alerts:
            return True

        try:
            payload = [alert.model_dump() for alert in alerts]
            success = await self._send_payload(payload, "alerts")
            return success

        except Exception as e:
            logger.error(f"Alert sync failed: {e}")
            self.error_count += 1
            return False

    async def sync_buffered(self, buffer_ids: List[str]) -> bool:
        """Sync buffered data."""
        # In real implementation, would retrieve buffer data
        # and send to central platform
        logger.info(f"Syncing {len(buffer_ids)} buffered batches")
        return True

    async def _send_batch(
        self,
        data: List[AggregatedData],
        data_type: str
    ) -> bool:
        """Send a batch of data."""
        payload = [d.model_dump() for d in data]
        return await self._send_payload(payload, data_type)

    async def _send_payload(
        self,
        payload: Any,
        endpoint: str
    ) -> bool:
        """Send payload to central platform."""
        import httpx

        url = f"{self.central_url}/api/edge/{endpoint}"
        headers = {}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Serialize payload
        json_data = json.dumps(payload, default=str)
        body = json_data.encode()

        # Compress if enabled
        if self.compression:
            body = gzip.compress(body)
            headers["Content-Encoding"] = "gzip"

        headers["Content-Type"] = "application/json"

        start_time = datetime.utcnow()

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        url,
                        content=body,
                        headers=headers
                    )

                    self.last_sync_latency_ms = (
                        datetime.utcnow() - start_time
                    ).total_seconds() * 1000

                    if response.status_code == 200:
                        self.bytes_sent += len(body)
                        self.sync_count += 1
                        self.last_sync_time = datetime.utcnow()
                        return True
                    elif response.status_code >= 500:
                        # Server error, retry
                        logger.warning(
                            f"Server error {response.status_code}, "
                            f"attempt {attempt + 1}/{self.max_retries}"
                        )
                        continue
                    else:
                        # Client error, don't retry
                        logger.error(f"Client error: {response.status_code}")
                        return False

            except httpx.TimeoutException:
                logger.warning(f"Timeout, attempt {attempt + 1}/{self.max_retries}")
            except httpx.NetworkError as e:
                logger.warning(f"Network error: {e}, attempt {attempt + 1}/{self.max_retries}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                break

        return False

    async def check_central_status(self) -> Dict[str, Any]:
        """Check central platform status."""
        import httpx

        url = f"{self.central_url}/health"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)

                if response.status_code == 200:
                    return {
                        "status": "online",
                        "latency_ms": response.elapsed.total_seconds() * 1000
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"HTTP {response.status_code}"
                    }

        except Exception as e:
            return {
                "status": "offline",
                "error": str(e)
            }

    async def fetch_model_updates(self) -> List[Dict[str, Any]]:
        """Fetch model updates from central platform."""
        import httpx

        url = f"{self.central_url}/api/edge/models"
        headers = {}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            logger.error(f"Failed to fetch model updates: {e}")

        return []

    def get_metrics(self) -> Dict[str, Any]:
        """Get sync manager metrics."""
        return {
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "sync_count": self.sync_count,
            "error_count": self.error_count,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "last_sync_latency_ms": self.last_sync_latency_ms,
            "compression_enabled": self.compression
        }

    def reset_metrics(self):
        """Reset sync metrics."""
        self.bytes_sent = 0
        self.bytes_received = 0
        self.sync_count = 0
        self.error_count = 0
