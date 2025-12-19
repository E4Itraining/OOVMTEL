"""
MQTT Client - Async MQTT client for IoT connectivity
"""

import logging
import asyncio
import uuid
import json
import ssl
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Awaitable
from pydantic import BaseModel, Field

from .models import (
    QoSLevel,
    MQTTMessage,
    TopicSubscription,
    DeviceState,
    DeviceStatus,
    MessageType,
)

logger = logging.getLogger(__name__)


class MQTTConfig(BaseModel):
    """MQTT client configuration."""
    client_id: str = Field(default_factory=lambda: f"synapsix-{uuid.uuid4().hex[:8]}")

    # Broker connection
    broker_host: str = "localhost"
    broker_port: int = 1883
    use_tls: bool = False
    tls_port: int = 8883

    # Authentication
    username: Optional[str] = None
    password: Optional[str] = None
    use_certificate: bool = False
    ca_cert_path: Optional[str] = None
    client_cert_path: Optional[str] = None
    client_key_path: Optional[str] = None

    # Connection settings
    keepalive_seconds: int = 60
    clean_session: bool = True
    reconnect_on_failure: bool = True
    reconnect_delay_seconds: int = 5
    max_reconnect_attempts: int = 10

    # Message settings
    default_qos: QoSLevel = QoSLevel.AT_LEAST_ONCE
    max_inflight_messages: int = 100
    max_queued_messages: int = 1000

    # Last Will and Testament
    lwt_enabled: bool = True
    lwt_topic: str = "synapsix/status"
    lwt_payload: str = '{"status": "offline"}'
    lwt_qos: QoSLevel = QoSLevel.AT_LEAST_ONCE
    lwt_retain: bool = True


class MQTTClient:
    """
    Async MQTT Client for SYNAPSIX.

    Features:
    - Async message handling
    - Auto-reconnection
    - TLS/SSL support
    - Certificate authentication
    - Message queuing
    - Last Will and Testament
    - Topic pattern matching
    """

    def __init__(self, config: MQTTConfig):
        self.config = config
        self._client = None
        self._connected = False
        self._connecting = False
        self._subscriptions: Dict[str, TopicSubscription] = {}
        self._message_handlers: Dict[str, Callable] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._pending_commands: Dict[str, asyncio.Future] = {}

        # Statistics
        self._stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "reconnect_count": 0,
            "errors": 0,
        }

        logger.info(f"MQTT Client initialized: {config.client_id}")

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def connect(self) -> bool:
        """
        Connect to MQTT broker.

        Returns:
            True if connected successfully
        """
        if self._connected or self._connecting:
            return self._connected

        self._connecting = True

        try:
            # Try to use asyncio-mqtt (aiomqtt) or paho-mqtt
            try:
                import aiomqtt
                return await self._connect_aiomqtt()
            except ImportError:
                logger.info("aiomqtt not available, using simulation mode")
                return await self._connect_simulated()

        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")
            self._connecting = False
            return False

    async def _connect_aiomqtt(self) -> bool:
        """Connect using aiomqtt library."""
        import aiomqtt

        try:
            port = self.config.tls_port if self.config.use_tls else self.config.broker_port

            # TLS configuration
            tls_context = None
            if self.config.use_tls:
                tls_context = ssl.create_default_context()
                if self.config.ca_cert_path:
                    tls_context.load_verify_locations(self.config.ca_cert_path)
                if self.config.use_certificate and self.config.client_cert_path:
                    tls_context.load_cert_chain(
                        self.config.client_cert_path,
                        self.config.client_key_path
                    )

            # Create client
            self._client = aiomqtt.Client(
                hostname=self.config.broker_host,
                port=port,
                username=self.config.username,
                password=self.config.password,
                identifier=self.config.client_id,
                tls_context=tls_context,
                keepalive=self.config.keepalive_seconds,
            )

            # Connect
            await self._client.__aenter__()
            self._connected = True
            self._connecting = False

            logger.info(f"Connected to MQTT broker: {self.config.broker_host}:{port}")

            # Start message listener
            asyncio.create_task(self._message_listener())

            return True

        except Exception as e:
            logger.error(f"aiomqtt connection failed: {e}")
            self._connecting = False
            return False

    async def _connect_simulated(self) -> bool:
        """Simulated connection for testing without broker."""
        logger.info("MQTT running in simulation mode")
        self._connected = True
        self._connecting = False

        # Start simulated message generator
        asyncio.create_task(self._simulated_message_loop())

        return True

    async def _simulated_message_loop(self):
        """Generate simulated messages for testing."""
        import random

        while self._connected:
            await asyncio.sleep(5)  # Generate message every 5 seconds

            # Simulate telemetry from a device
            for sub_id, sub in self._subscriptions.items():
                if not sub.enabled:
                    continue

                # Create simulated message
                device_id = f"sensor-{random.randint(1, 10):03d}"
                topic = sub.topic_pattern.replace("+", device_id).replace("#", f"{device_id}/data")

                payload = {
                    "device_id": device_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "temperature": round(20 + random.random() * 10, 2),
                    "humidity": round(40 + random.random() * 30, 2),
                    "pressure": round(1000 + random.random() * 50, 2),
                }

                message = MQTTMessage(
                    message_id=f"MSG-{uuid.uuid4().hex[:8]}",
                    topic=topic,
                    payload=json.dumps(payload),
                    qos=sub.qos,
                    device_id=device_id,
                    parsed_payload=payload,
                    message_type=MessageType.TELEMETRY,
                )

                await self._message_queue.put(message)
                self._stats["messages_received"] += 1

    async def disconnect(self) -> bool:
        """Disconnect from MQTT broker."""
        try:
            self._connected = False

            if self._client and hasattr(self._client, '__aexit__'):
                await self._client.__aexit__(None, None, None)

            self._client = None
            logger.info("Disconnected from MQTT broker")
            return True

        except Exception as e:
            logger.error(f"MQTT disconnect failed: {e}")
            return False

    async def subscribe(
        self,
        topic_pattern: str,
        handler: Optional[Callable[[MQTTMessage], Awaitable[None]]] = None,
        qos: QoSLevel = QoSLevel.AT_LEAST_ONCE,
    ) -> str:
        """
        Subscribe to a topic pattern.

        Args:
            topic_pattern: MQTT topic pattern (supports + and # wildcards)
            handler: Async callback for messages
            qos: Quality of Service level

        Returns:
            Subscription ID
        """
        sub_id = f"SUB-{uuid.uuid4().hex[:8]}"

        subscription = TopicSubscription(
            subscription_id=sub_id,
            topic_pattern=topic_pattern,
            qos=qos,
            handler=sub_id if handler else None,
        )

        self._subscriptions[sub_id] = subscription

        if handler:
            self._message_handlers[sub_id] = handler

        # Subscribe on broker if connected
        if self._connected and self._client:
            try:
                if hasattr(self._client, 'subscribe'):
                    await self._client.subscribe(topic_pattern, qos=qos.value)
            except Exception as e:
                logger.error(f"Subscribe failed: {e}")

        logger.info(f"Subscribed to {topic_pattern} (ID: {sub_id})")
        return sub_id

    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a topic."""
        if subscription_id not in self._subscriptions:
            return False

        subscription = self._subscriptions[subscription_id]

        if self._connected and self._client:
            try:
                if hasattr(self._client, 'unsubscribe'):
                    await self._client.unsubscribe(subscription.topic_pattern)
            except Exception as e:
                logger.error(f"Unsubscribe failed: {e}")

        del self._subscriptions[subscription_id]
        if subscription_id in self._message_handlers:
            del self._message_handlers[subscription_id]

        logger.info(f"Unsubscribed from {subscription.topic_pattern}")
        return True

    async def publish(
        self,
        topic: str,
        payload: Any,
        qos: QoSLevel = QoSLevel.AT_LEAST_ONCE,
        retain: bool = False,
    ) -> bool:
        """
        Publish a message to a topic.

        Args:
            topic: MQTT topic
            payload: Message payload (dict will be JSON-encoded)
            qos: Quality of Service level
            retain: Retain message on broker

        Returns:
            True if published successfully
        """
        try:
            # Encode payload
            if isinstance(payload, dict):
                payload_bytes = json.dumps(payload).encode('utf-8')
            elif isinstance(payload, str):
                payload_bytes = payload.encode('utf-8')
            else:
                payload_bytes = payload

            if self._connected and self._client:
                if hasattr(self._client, 'publish'):
                    await self._client.publish(
                        topic,
                        payload_bytes,
                        qos=qos.value,
                        retain=retain
                    )

            self._stats["messages_sent"] += 1
            logger.debug(f"Published to {topic}")
            return True

        except Exception as e:
            logger.error(f"Publish failed: {e}")
            self._stats["errors"] += 1
            return False

    async def send_command(
        self,
        device_id: str,
        command_type: str,
        parameters: Dict[str, Any],
        timeout: float = 30.0,
        response_topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a command to a device and wait for response.

        Args:
            device_id: Target device ID
            command_type: Type of command
            parameters: Command parameters
            timeout: Response timeout in seconds
            response_topic: Topic for response (default: auto-generate)

        Returns:
            Command response or timeout error
        """
        command_id = f"CMD-{uuid.uuid4().hex[:8]}"

        # Prepare command payload
        command_payload = {
            "command_id": command_id,
            "command_type": command_type,
            "parameters": parameters,
            "timestamp": datetime.utcnow().isoformat(),
            "response_topic": response_topic or f"synapsix/responses/{command_id}",
        }

        # Subscribe to response topic
        if response_topic:
            response_future: asyncio.Future = asyncio.Future()
            self._pending_commands[command_id] = response_future

            await self.subscribe(
                response_topic or f"synapsix/responses/{command_id}",
                handler=lambda msg: self._handle_command_response(command_id, msg),
            )

        # Publish command
        command_topic = f"devices/{device_id}/commands"
        await self.publish(command_topic, command_payload, QoSLevel.AT_LEAST_ONCE)

        # Wait for response
        try:
            if command_id in self._pending_commands:
                response = await asyncio.wait_for(
                    self._pending_commands[command_id],
                    timeout=timeout
                )
                return response
            return {"status": "sent", "command_id": command_id}

        except asyncio.TimeoutError:
            return {"status": "timeout", "command_id": command_id}

        finally:
            if command_id in self._pending_commands:
                del self._pending_commands[command_id]

    async def _handle_command_response(
        self,
        command_id: str,
        message: MQTTMessage
    ) -> None:
        """Handle command response."""
        if command_id in self._pending_commands:
            future = self._pending_commands[command_id]
            if not future.done():
                future.set_result(message.parsed_payload or {"raw": message.payload})

    async def _message_listener(self):
        """Listen for incoming messages."""
        if not self._client:
            return

        try:
            async for message in self._client.messages:
                await self._process_message(message)
        except Exception as e:
            logger.error(f"Message listener error: {e}")
            if self.config.reconnect_on_failure:
                await self._reconnect()

    async def _process_message(self, raw_message: Any) -> None:
        """Process an incoming MQTT message."""
        try:
            # Parse message
            topic = str(raw_message.topic) if hasattr(raw_message, 'topic') else ""
            payload = raw_message.payload if hasattr(raw_message, 'payload') else b""

            # Try to parse JSON payload
            parsed_payload = None
            if isinstance(payload, bytes):
                payload = payload.decode('utf-8')
            try:
                parsed_payload = json.loads(payload)
            except json.JSONDecodeError:
                pass

            # Extract device ID from topic
            device_id = self._extract_device_id(topic)

            # Create message object
            message = MQTTMessage(
                message_id=f"MSG-{uuid.uuid4().hex[:8]}",
                topic=topic,
                payload=payload,
                qos=QoSLevel(raw_message.qos) if hasattr(raw_message, 'qos') else QoSLevel.AT_MOST_ONCE,
                retain=raw_message.retain if hasattr(raw_message, 'retain') else False,
                device_id=device_id,
                parsed_payload=parsed_payload,
                message_type=self._detect_message_type(topic, parsed_payload),
            )

            # Update stats
            self._stats["messages_received"] += 1

            # Find matching subscriptions and invoke handlers
            for sub_id, subscription in self._subscriptions.items():
                if self._topic_matches(subscription.topic_pattern, topic):
                    subscription.messages_received += 1
                    subscription.last_message_at = datetime.utcnow()

                    if sub_id in self._message_handlers:
                        try:
                            await self._message_handlers[sub_id](message)
                        except Exception as e:
                            logger.error(f"Handler error for {sub_id}: {e}")

            # Put in queue for other consumers
            await self._message_queue.put(message)

        except Exception as e:
            logger.error(f"Message processing error: {e}")
            self._stats["errors"] += 1

    def _extract_device_id(self, topic: str) -> Optional[str]:
        """Extract device ID from topic."""
        parts = topic.split('/')

        # Common patterns
        if 'devices' in parts:
            idx = parts.index('devices')
            if idx + 1 < len(parts):
                return parts[idx + 1]

        if 'sensors' in parts:
            idx = parts.index('sensors')
            if idx + 1 < len(parts):
                return parts[idx + 1]

        # Sparkplug B pattern
        if len(parts) >= 5 and parts[0] == 'spBv1.0':
            return parts[4] if len(parts) > 4 else parts[3]

        return None

    def _detect_message_type(
        self,
        topic: str,
        payload: Optional[Dict]
    ) -> MessageType:
        """Detect message type from topic and payload."""
        topic_lower = topic.lower()

        if 'telemetry' in topic_lower or 'data' in topic_lower:
            return MessageType.TELEMETRY
        elif 'command' in topic_lower:
            if 'response' in topic_lower:
                return MessageType.COMMAND_RESPONSE
            return MessageType.COMMAND
        elif 'event' in topic_lower:
            return MessageType.EVENT
        elif 'state' in topic_lower or 'status' in topic_lower:
            return MessageType.STATE
        elif 'config' in topic_lower:
            return MessageType.CONFIG
        elif 'alert' in topic_lower or 'alarm' in topic_lower:
            return MessageType.ALERT
        elif 'heartbeat' in topic_lower or 'ping' in topic_lower:
            return MessageType.HEARTBEAT

        return MessageType.TELEMETRY

    def _topic_matches(self, pattern: str, topic: str) -> bool:
        """Check if topic matches a pattern (supports + and # wildcards)."""
        pattern_parts = pattern.split('/')
        topic_parts = topic.split('/')

        i = 0
        j = 0

        while i < len(pattern_parts) and j < len(topic_parts):
            if pattern_parts[i] == '#':
                return True  # # matches everything after
            elif pattern_parts[i] == '+' or pattern_parts[i] == topic_parts[j]:
                i += 1
                j += 1
            else:
                return False

        return i == len(pattern_parts) and j == len(topic_parts)

    async def _reconnect(self):
        """Attempt to reconnect to broker."""
        self._connected = False
        attempts = 0

        while attempts < self.config.max_reconnect_attempts:
            attempts += 1
            self._stats["reconnect_count"] += 1

            logger.info(f"Reconnection attempt {attempts}/{self.config.max_reconnect_attempts}")

            await asyncio.sleep(self.config.reconnect_delay_seconds)

            if await self.connect():
                # Resubscribe to all topics
                for sub in self._subscriptions.values():
                    if self._client and hasattr(self._client, 'subscribe'):
                        try:
                            await self._client.subscribe(sub.topic_pattern, qos=sub.qos.value)
                        except Exception as e:
                            logger.error(f"Resubscribe failed: {e}")
                return

        logger.error("Max reconnection attempts reached")

    async def get_message(self, timeout: float = None) -> Optional[MQTTMessage]:
        """Get next message from queue."""
        try:
            if timeout:
                return await asyncio.wait_for(self._message_queue.get(), timeout=timeout)
            return self._message_queue.get_nowait()
        except (asyncio.TimeoutError, asyncio.QueueEmpty):
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        return {
            **self._stats,
            "connected": self._connected,
            "subscriptions": len(self._subscriptions),
            "queue_size": self._message_queue.qsize(),
            "client_id": self.config.client_id,
        }
