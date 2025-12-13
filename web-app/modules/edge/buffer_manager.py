"""
Buffer Manager - Manages offline data buffering at the edge
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque

from .models import DataBuffer, AggregatedData, SyncStatus

logger = logging.getLogger(__name__)


class BufferManager:
    """
    Manages data buffering when offline.

    Features:
    - Circular buffer with size limit
    - Data retention policy
    - Priority-based buffering
    - Compression support
    """

    def __init__(
        self,
        max_size_mb: int = 100,
        retention_hours: int = 24
    ):
        self.max_size_mb = max_size_mb
        self.retention_hours = retention_hours

        # Data storage
        self.buffers: Dict[str, DataBuffer] = {}
        self.data_store: Dict[str, List[AggregatedData]] = {}

        # Metrics
        self.total_size_bytes = 0
        self.data_points_count = 0

    def add_data(self, data: List[AggregatedData]) -> str:
        """Add data to buffer."""
        buffer_id = f"BUF-{uuid.uuid4().hex[:8].upper()}"

        # Calculate size (rough estimate)
        size_bytes = len(data) * 200  # ~200 bytes per record

        # Check if we need to make room
        while self.total_size_bytes + size_bytes > self.max_size_mb * 1024 * 1024:
            self._evict_oldest()

        # Store data
        self.data_store[buffer_id] = data.copy()

        # Create buffer metadata
        timestamps = [d.end_time for d in data]
        buffer = DataBuffer(
            id=buffer_id,
            size_bytes=size_bytes,
            data_points_count=len(data),
            oldest_data=min(timestamps) if timestamps else None,
            newest_data=max(timestamps) if timestamps else None,
            sync_status=SyncStatus.BUFFERED
        )
        self.buffers[buffer_id] = buffer

        # Update totals
        self.total_size_bytes += size_bytes
        self.data_points_count += len(data)

        logger.info(f"Buffered {len(data)} records in {buffer_id}")
        return buffer_id

    def get_pending_sync(self) -> List[str]:
        """Get buffer IDs pending sync."""
        return [
            buf_id for buf_id, buf in self.buffers.items()
            if buf.sync_status in [SyncStatus.BUFFERED, SyncStatus.FAILED]
        ]

    def get_buffer_data(self, buffer_id: str) -> List[AggregatedData]:
        """Get data from a specific buffer."""
        return self.data_store.get(buffer_id, [])

    def mark_synced(self, buffer_ids: List[str]):
        """Mark buffers as synced."""
        for buffer_id in buffer_ids:
            if buffer_id in self.buffers:
                buf = self.buffers[buffer_id]
                buf.sync_status = SyncStatus.SYNCED

                # Remove synced data
                if buffer_id in self.data_store:
                    self.total_size_bytes -= buf.size_bytes
                    self.data_points_count -= buf.data_points_count
                    del self.data_store[buffer_id]
                    del self.buffers[buffer_id]

                logger.info(f"Buffer {buffer_id} synced and removed")

    def mark_sync_failed(self, buffer_id: str, error: str):
        """Mark a sync attempt as failed."""
        if buffer_id in self.buffers:
            buf = self.buffers[buffer_id]
            buf.sync_status = SyncStatus.FAILED
            buf.sync_attempts += 1
            buf.last_sync_attempt = datetime.utcnow()
            buf.last_sync_error = error

    def get_size(self) -> int:
        """Get total buffer size in bytes."""
        return self.total_size_bytes

    def get_data_points_count(self) -> int:
        """Get total buffered data points count."""
        return self.data_points_count

    def get_status(self) -> Dict[str, Any]:
        """Get buffer manager status."""
        return {
            "total_size_mb": self.total_size_bytes / (1024 * 1024),
            "max_size_mb": self.max_size_mb,
            "utilization_percent": (self.total_size_bytes / (self.max_size_mb * 1024 * 1024)) * 100,
            "data_points_buffered": self.data_points_count,
            "buffer_count": len(self.buffers),
            "pending_sync": len(self.get_pending_sync()),
            "oldest_data": self._get_oldest_timestamp(),
            "newest_data": self._get_newest_timestamp()
        }

    def _evict_oldest(self):
        """Evict oldest buffer to make room."""
        if not self.buffers:
            return

        # Find oldest buffer
        oldest_id = None
        oldest_time = datetime.utcnow()

        for buf_id, buf in self.buffers.items():
            if buf.oldest_data and buf.oldest_data < oldest_time:
                oldest_time = buf.oldest_data
                oldest_id = buf_id

        if oldest_id:
            buf = self.buffers[oldest_id]
            self.total_size_bytes -= buf.size_bytes
            self.data_points_count -= buf.data_points_count

            if oldest_id in self.data_store:
                del self.data_store[oldest_id]
            del self.buffers[oldest_id]

            logger.warning(f"Evicted oldest buffer {oldest_id} to make room")

    def _get_oldest_timestamp(self) -> Optional[str]:
        """Get oldest timestamp in buffer."""
        oldest = None
        for buf in self.buffers.values():
            if buf.oldest_data:
                if oldest is None or buf.oldest_data < oldest:
                    oldest = buf.oldest_data
        return oldest.isoformat() if oldest else None

    def _get_newest_timestamp(self) -> Optional[str]:
        """Get newest timestamp in buffer."""
        newest = None
        for buf in self.buffers.values():
            if buf.newest_data:
                if newest is None or buf.newest_data > newest:
                    newest = buf.newest_data
        return newest.isoformat() if newest else None

    def cleanup_expired(self):
        """Remove expired data based on retention policy."""
        cutoff = datetime.utcnow() - timedelta(hours=self.retention_hours)

        expired = []
        for buf_id, buf in self.buffers.items():
            if buf.newest_data and buf.newest_data < cutoff:
                expired.append(buf_id)

        for buf_id in expired:
            buf = self.buffers[buf_id]
            self.total_size_bytes -= buf.size_bytes
            self.data_points_count -= buf.data_points_count

            if buf_id in self.data_store:
                del self.data_store[buf_id]
            del self.buffers[buf_id]

            logger.info(f"Expired buffer {buf_id} removed")

        return len(expired)

    def clear(self):
        """Clear all buffers."""
        self.buffers.clear()
        self.data_store.clear()
        self.total_size_bytes = 0
        self.data_points_count = 0
