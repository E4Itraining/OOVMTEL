"""
MQTT Message Processor - Advanced message processing and routing
"""

import logging
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Awaitable, Pattern
import re

from .models import (
    MQTTMessage,
    TelemetryData,
    DeviceAlert,
    MessageType,
    QoSLevel,
)

logger = logging.getLogger(__name__)


class MessageHandler:
    """
    Configurable message handler with filtering and transformation.
    """

    def __init__(
        self,
        handler_id: str,
        name: str,
        topic_patterns: List[str],
        callback: Callable[[MQTTMessage], Awaitable[None]],
        message_types: Optional[List[MessageType]] = None,
        device_filter: Optional[Pattern] = None,
        transform: Optional[Callable[[Dict], Dict]] = None,
        enabled: bool = True,
    ):
        self.handler_id = handler_id
        self.name = name
        self.topic_patterns = topic_patterns
        self.callback = callback
        self.message_types = message_types
        self.device_filter = device_filter
        self.transform = transform
        self.enabled = enabled

        # Statistics
        self.messages_processed = 0
        self.messages_filtered = 0
        self.errors = 0

    def matches(self, message: MQTTMessage) -> bool:
        """Check if message matches this handler's criteria."""
        if not self.enabled:
            return False

        # Check message type
        if self.message_types and message.message_type not in self.message_types:
            return False

        # Check device filter
        if self.device_filter and message.device_id:
            if not self.device_filter.match(message.device_id):
                return False

        # Check topic patterns
        for pattern in self.topic_patterns:
            if self._topic_matches(pattern, message.topic):
                return True

        return False

    def _topic_matches(self, pattern: str, topic: str) -> bool:
        """Check if topic matches pattern."""
        pattern_parts = pattern.split('/')
        topic_parts = topic.split('/')

        i = 0
        j = 0

        while i < len(pattern_parts) and j < len(topic_parts):
            if pattern_parts[i] == '#':
                return True
            elif pattern_parts[i] == '+' or pattern_parts[i] == topic_parts[j]:
                i += 1
                j += 1
            else:
                return False

        return i == len(pattern_parts) and j == len(topic_parts)

    async def process(self, message: MQTTMessage) -> None:
        """Process a message."""
        try:
            # Apply transformation if configured
            if self.transform and message.parsed_payload:
                message.parsed_payload = self.transform(message.parsed_payload)

            await self.callback(message)
            self.messages_processed += 1

        except Exception as e:
            self.errors += 1
            logger.error(f"Handler {self.name} error: {e}")
            raise


class MessageProcessor:
    """
    Advanced MQTT message processor.

    Features:
    - Message routing based on topics and content
    - Payload transformation
    - Alert generation
    - Data aggregation
    - Rate limiting
    - Dead letter queue
    """

    def __init__(
        self,
        max_queue_size: int = 10000,
        batch_size: int = 100,
        batch_timeout_seconds: float = 1.0,
    ):
        self._handlers: Dict[str, MessageHandler] = {}
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._dead_letter_queue: asyncio.Queue = asyncio.Queue()
        self._batch_size = batch_size
        self._batch_timeout = batch_timeout_seconds
        self._running = False

        # Aggregation buffers
        self._aggregation_buffers: Dict[str, List[TelemetryData]] = {}
        self._aggregation_callbacks: Dict[str, Callable] = {}

        # Rate limiting
        self._rate_limits: Dict[str, Dict] = {}

        # Statistics
        self._stats = {
            "messages_received": 0,
            "messages_processed": 0,
            "messages_dropped": 0,
            "errors": 0,
        }

        logger.info("Message Processor initialized")

    def add_handler(
        self,
        name: str,
        topic_patterns: List[str],
        callback: Callable[[MQTTMessage], Awaitable[None]],
        message_types: Optional[List[MessageType]] = None,
        device_filter: Optional[str] = None,
        transform: Optional[Callable[[Dict], Dict]] = None,
    ) -> str:
        """
        Add a message handler.

        Args:
            name: Handler name
            topic_patterns: List of topic patterns to match
            callback: Async callback function
            message_types: Filter by message types
            device_filter: Regex pattern for device IDs
            transform: Payload transformation function

        Returns:
            Handler ID
        """
        handler_id = f"HDL-{uuid.uuid4().hex[:8]}"

        device_pattern = re.compile(device_filter) if device_filter else None

        handler = MessageHandler(
            handler_id=handler_id,
            name=name,
            topic_patterns=topic_patterns,
            callback=callback,
            message_types=message_types,
            device_filter=device_pattern,
            transform=transform,
        )

        self._handlers[handler_id] = handler
        logger.info(f"Added handler: {name} (ID: {handler_id})")

        return handler_id

    def remove_handler(self, handler_id: str) -> bool:
        """Remove a handler."""
        if handler_id in self._handlers:
            del self._handlers[handler_id]
            return True
        return False

    async def submit(self, message: MQTTMessage) -> bool:
        """Submit a message for processing."""
        try:
            self._queue.put_nowait(message)
            self._stats["messages_received"] += 1
            return True
        except asyncio.QueueFull:
            self._stats["messages_dropped"] += 1
            logger.warning("Message queue full, dropping message")
            return False

    async def process_message(self, message: MQTTMessage) -> None:
        """Process a single message through all matching handlers."""
        matched_handlers = []

        for handler in self._handlers.values():
            if handler.matches(message):
                matched_handlers.append(handler)
            else:
                handler.messages_filtered += 1

        if not matched_handlers:
            # No handlers matched - send to dead letter queue
            await self._dead_letter_queue.put(message)
            return

        # Process through all matching handlers
        for handler in matched_handlers:
            try:
                await handler.process(message)
            except Exception as e:
                self._stats["errors"] += 1
                logger.error(f"Handler {handler.name} failed: {e}")

        self._stats["messages_processed"] += 1
        message.processed = True

    async def start(self) -> None:
        """Start the message processor."""
        self._running = True
        asyncio.create_task(self._processing_loop())
        asyncio.create_task(self._aggregation_loop())
        logger.info("Message processor started")

    async def stop(self) -> None:
        """Stop the message processor."""
        self._running = False
        logger.info("Message processor stopped")

    async def _processing_loop(self) -> None:
        """Main processing loop."""
        while self._running:
            try:
                # Get message with timeout
                message = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=1.0
                )
                await self.process_message(message)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Processing loop error: {e}")
                self._stats["errors"] += 1

    # Aggregation

    def setup_aggregation(
        self,
        aggregation_id: str,
        callback: Callable[[List[TelemetryData]], Awaitable[None]],
        buffer_size: int = 100,
        flush_interval_seconds: float = 10.0,
    ) -> None:
        """
        Set up data aggregation for batch processing.

        Args:
            aggregation_id: Unique ID for this aggregation
            callback: Callback to receive aggregated data
            buffer_size: Number of records to buffer
            flush_interval_seconds: Maximum time before flushing
        """
        self._aggregation_buffers[aggregation_id] = []
        self._aggregation_callbacks[aggregation_id] = {
            "callback": callback,
            "buffer_size": buffer_size,
            "flush_interval": flush_interval_seconds,
            "last_flush": datetime.utcnow(),
        }

    async def aggregate_telemetry(
        self,
        aggregation_id: str,
        telemetry: TelemetryData
    ) -> None:
        """Add telemetry to aggregation buffer."""
        if aggregation_id not in self._aggregation_buffers:
            return

        self._aggregation_buffers[aggregation_id].append(telemetry)

        config = self._aggregation_callbacks[aggregation_id]
        if len(self._aggregation_buffers[aggregation_id]) >= config["buffer_size"]:
            await self._flush_aggregation(aggregation_id)

    async def _flush_aggregation(self, aggregation_id: str) -> None:
        """Flush aggregation buffer."""
        if aggregation_id not in self._aggregation_buffers:
            return

        buffer = self._aggregation_buffers[aggregation_id]
        if not buffer:
            return

        config = self._aggregation_callbacks[aggregation_id]
        callback = config["callback"]

        try:
            await callback(buffer.copy())
            self._aggregation_buffers[aggregation_id] = []
            config["last_flush"] = datetime.utcnow()
        except Exception as e:
            logger.error(f"Aggregation flush failed for {aggregation_id}: {e}")

    async def _aggregation_loop(self) -> None:
        """Periodic aggregation flush loop."""
        while self._running:
            await asyncio.sleep(1.0)

            now = datetime.utcnow()
            for agg_id, config in self._aggregation_callbacks.items():
                elapsed = (now - config["last_flush"]).total_seconds()
                if elapsed >= config["flush_interval"]:
                    await self._flush_aggregation(agg_id)

    # Alert Generation

    async def check_thresholds(
        self,
        telemetry: TelemetryData,
        thresholds: Dict[str, Dict[str, float]],
    ) -> List[DeviceAlert]:
        """
        Check telemetry against thresholds and generate alerts.

        Args:
            telemetry: Telemetry data to check
            thresholds: Dict of {metric: {warning: value, critical: value}}

        Returns:
            List of generated alerts
        """
        alerts = []

        for metric, value in telemetry.measurements.items():
            if metric not in thresholds:
                continue

            threshold = thresholds[metric]

            if "critical" in threshold and value >= threshold["critical"]:
                alerts.append(DeviceAlert(
                    alert_id=f"ALT-{uuid.uuid4().hex[:8]}",
                    device_id=telemetry.device_id,
                    alert_type="threshold",
                    severity="critical",
                    message=f"{metric} exceeded critical threshold: {value} >= {threshold['critical']}",
                    details={
                        "metric": metric,
                        "value": value,
                        "threshold": threshold["critical"],
                    },
                    related_measurement=metric,
                    threshold_value=threshold["critical"],
                    actual_value=value,
                ))
            elif "warning" in threshold and value >= threshold["warning"]:
                alerts.append(DeviceAlert(
                    alert_id=f"ALT-{uuid.uuid4().hex[:8]}",
                    device_id=telemetry.device_id,
                    alert_type="threshold",
                    severity="warning",
                    message=f"{metric} exceeded warning threshold: {value} >= {threshold['warning']}",
                    details={
                        "metric": metric,
                        "value": value,
                        "threshold": threshold["warning"],
                    },
                    related_measurement=metric,
                    threshold_value=threshold["warning"],
                    actual_value=value,
                ))

        return alerts

    # Rate Limiting

    def set_rate_limit(
        self,
        device_id: str,
        max_messages_per_second: float,
    ) -> None:
        """Set rate limit for a device."""
        self._rate_limits[device_id] = {
            "rate": max_messages_per_second,
            "tokens": max_messages_per_second,
            "last_update": datetime.utcnow(),
        }

    def check_rate_limit(self, device_id: str) -> bool:
        """
        Check if message is within rate limit.

        Returns:
            True if allowed, False if rate limited
        """
        if device_id not in self._rate_limits:
            return True

        limit = self._rate_limits[device_id]
        now = datetime.utcnow()
        elapsed = (now - limit["last_update"]).total_seconds()

        # Refill tokens
        limit["tokens"] = min(
            limit["rate"],
            limit["tokens"] + elapsed * limit["rate"]
        )
        limit["last_update"] = now

        if limit["tokens"] >= 1:
            limit["tokens"] -= 1
            return True

        return False

    # Statistics

    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics."""
        return {
            **self._stats,
            "queue_size": self._queue.qsize(),
            "dead_letter_size": self._dead_letter_queue.qsize(),
            "handlers": {
                h.handler_id: {
                    "name": h.name,
                    "enabled": h.enabled,
                    "processed": h.messages_processed,
                    "filtered": h.messages_filtered,
                    "errors": h.errors,
                }
                for h in self._handlers.values()
            },
            "aggregations": {
                agg_id: len(buffer)
                for agg_id, buffer in self._aggregation_buffers.items()
            },
        }

    async def get_dead_letters(self, limit: int = 100) -> List[MQTTMessage]:
        """Get messages from dead letter queue."""
        messages = []
        while len(messages) < limit and not self._dead_letter_queue.empty():
            try:
                msg = self._dead_letter_queue.get_nowait()
                messages.append(msg)
            except asyncio.QueueEmpty:
                break
        return messages
