"""
MQTT Broker Manager - Multi-broker connectivity management
"""

import logging
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Awaitable
from pydantic import BaseModel, Field

from .client import MQTTClient, MQTTConfig
from .models import (
    MQTTMessage,
    IoTDevice,
    DeviceState,
    DeviceStatus,
    TelemetryData,
    QoSLevel,
)

logger = logging.getLogger(__name__)


class BrokerConnection(BaseModel):
    """Configuration for a broker connection."""
    broker_id: str
    name: str
    description: str = ""
    config: MQTTConfig
    enabled: bool = True
    priority: int = 1  # For failover ordering

    # Status
    connected: bool = False
    last_connected: Optional[datetime] = None
    last_error: Optional[str] = None


class MQTTBrokerManager:
    """
    Multi-broker MQTT manager for SYNAPSIX.

    Features:
    - Multiple broker connections
    - Automatic failover
    - Device registry
    - Message routing
    - Telemetry aggregation
    """

    def __init__(self):
        self._brokers: Dict[str, BrokerConnection] = {}
        self._clients: Dict[str, MQTTClient] = {}
        self._devices: Dict[str, IoTDevice] = {}
        self._telemetry_handlers: List[Callable[[TelemetryData], Awaitable[None]]] = []
        self._running = False

        logger.info("MQTT Broker Manager initialized")

    async def add_broker(
        self,
        name: str,
        host: str,
        port: int = 1883,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = False,
        **kwargs
    ) -> str:
        """
        Add a new broker connection.

        Returns:
            Broker ID
        """
        broker_id = f"BROKER-{uuid.uuid4().hex[:8]}"

        config = MQTTConfig(
            broker_host=host,
            broker_port=port,
            username=username,
            password=password,
            use_tls=use_tls,
            client_id=f"synapsix-{broker_id}",
            **kwargs
        )

        connection = BrokerConnection(
            broker_id=broker_id,
            name=name,
            config=config,
        )

        self._brokers[broker_id] = connection

        logger.info(f"Added broker: {name} ({host}:{port})")
        return broker_id

    async def connect_broker(self, broker_id: str) -> bool:
        """Connect to a specific broker."""
        if broker_id not in self._brokers:
            logger.error(f"Unknown broker: {broker_id}")
            return False

        broker = self._brokers[broker_id]

        if not broker.enabled:
            logger.warning(f"Broker {broker.name} is disabled")
            return False

        try:
            client = MQTTClient(broker.config)
            success = await client.connect()

            if success:
                self._clients[broker_id] = client
                broker.connected = True
                broker.last_connected = datetime.utcnow()
                broker.last_error = None

                # Set up default subscriptions
                await self._setup_default_subscriptions(broker_id, client)

                logger.info(f"Connected to broker: {broker.name}")
                return True
            else:
                broker.connected = False
                broker.last_error = "Connection failed"
                return False

        except Exception as e:
            broker.connected = False
            broker.last_error = str(e)
            logger.error(f"Failed to connect to {broker.name}: {e}")
            return False

    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all enabled brokers."""
        results = {}

        for broker_id, broker in self._brokers.items():
            if broker.enabled:
                results[broker_id] = await self.connect_broker(broker_id)

        return results

    async def disconnect_broker(self, broker_id: str) -> bool:
        """Disconnect from a broker."""
        if broker_id not in self._clients:
            return True

        try:
            client = self._clients[broker_id]
            await client.disconnect()
            del self._clients[broker_id]

            if broker_id in self._brokers:
                self._brokers[broker_id].connected = False

            logger.info(f"Disconnected from broker: {broker_id}")
            return True

        except Exception as e:
            logger.error(f"Disconnect failed: {e}")
            return False

    async def disconnect_all(self) -> None:
        """Disconnect from all brokers."""
        for broker_id in list(self._clients.keys()):
            await self.disconnect_broker(broker_id)

    async def _setup_default_subscriptions(
        self,
        broker_id: str,
        client: MQTTClient
    ) -> None:
        """Set up default topic subscriptions."""
        # Subscribe to common patterns
        default_topics = [
            "devices/+/telemetry",
            "devices/+/state",
            "devices/+/events",
            "sensors/#",
            "synapsix/+/data",
        ]

        for topic in default_topics:
            await client.subscribe(
                topic,
                handler=lambda msg: self._handle_message(broker_id, msg),
                qos=QoSLevel.AT_LEAST_ONCE,
            )

    async def _handle_message(
        self,
        broker_id: str,
        message: MQTTMessage
    ) -> None:
        """Handle incoming MQTT message."""
        try:
            # Update device state
            if message.device_id:
                await self._update_device_state(message.device_id, message)

            # Convert to telemetry if applicable
            if message.message_type.value == "telemetry" and message.parsed_payload:
                telemetry = self._parse_telemetry(message)
                if telemetry:
                    # Notify handlers
                    for handler in self._telemetry_handlers:
                        try:
                            await handler(telemetry)
                        except Exception as e:
                            logger.error(f"Telemetry handler error: {e}")

        except Exception as e:
            logger.error(f"Message handling error: {e}")

    async def _update_device_state(
        self,
        device_id: str,
        message: MQTTMessage
    ) -> None:
        """Update device state from message."""
        if device_id not in self._devices:
            # Auto-register device
            self._devices[device_id] = IoTDevice(
                device_id=device_id,
                device_type="auto_detected",
                name=f"Device {device_id}",
                state=DeviceState(device_id=device_id),
            )

        device = self._devices[device_id]
        device.state.last_seen = datetime.utcnow()
        device.state.status = DeviceStatus.ONLINE
        device.state.messages_received += 1

        if message.parsed_payload and isinstance(message.parsed_payload, dict):
            device.state.current_values.update(message.parsed_payload)

    def _parse_telemetry(self, message: MQTTMessage) -> Optional[TelemetryData]:
        """Parse telemetry data from message."""
        if not message.parsed_payload:
            return None

        payload = message.parsed_payload

        # Extract measurements (numeric values)
        measurements = {}
        for key, value in payload.items():
            if isinstance(value, (int, float)) and key not in ['timestamp', 'sequence']:
                measurements[key] = float(value)

        if not measurements:
            return None

        return TelemetryData(
            device_id=message.device_id or "unknown",
            timestamp=message.timestamp,
            measurements=measurements,
            source_topic=message.topic,
        )

    # Device Management

    async def register_device(self, device: IoTDevice) -> str:
        """Register an IoT device."""
        self._devices[device.device_id] = device

        logger.info(f"Registered device: {device.device_id} ({device.device_type})")
        return device.device_id

    async def unregister_device(self, device_id: str) -> bool:
        """Unregister a device."""
        if device_id in self._devices:
            del self._devices[device_id]
            return True
        return False

    def get_device(self, device_id: str) -> Optional[IoTDevice]:
        """Get device by ID."""
        return self._devices.get(device_id)

    def get_all_devices(self) -> List[IoTDevice]:
        """Get all registered devices."""
        return list(self._devices.values())

    def get_online_devices(self) -> List[IoTDevice]:
        """Get all online devices."""
        return [
            d for d in self._devices.values()
            if d.state.status == DeviceStatus.ONLINE
        ]

    # Publishing

    async def publish(
        self,
        topic: str,
        payload: Any,
        broker_id: Optional[str] = None,
        qos: QoSLevel = QoSLevel.AT_LEAST_ONCE,
        retain: bool = False,
    ) -> bool:
        """
        Publish message to broker(s).

        Args:
            topic: MQTT topic
            payload: Message payload
            broker_id: Specific broker (None = all connected)
            qos: Quality of Service
            retain: Retain message
        """
        if broker_id:
            if broker_id in self._clients:
                return await self._clients[broker_id].publish(topic, payload, qos, retain)
            return False

        # Publish to all connected brokers
        results = []
        for client in self._clients.values():
            results.append(await client.publish(topic, payload, qos, retain))

        return any(results)

    async def send_command_to_device(
        self,
        device_id: str,
        command_type: str,
        parameters: Dict[str, Any],
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """Send command to a device."""
        device = self.get_device(device_id)

        if not device:
            return {"error": f"Device {device_id} not found"}

        if not device.supports_commands:
            return {"error": f"Device {device_id} does not support commands"}

        # Find the broker this device is connected through
        for broker_id, client in self._clients.items():
            if client.is_connected:
                return await client.send_command(
                    device_id, command_type, parameters, timeout
                )

        return {"error": "No connected brokers"}

    # Telemetry Handlers

    def add_telemetry_handler(
        self,
        handler: Callable[[TelemetryData], Awaitable[None]]
    ) -> None:
        """Add a telemetry data handler."""
        self._telemetry_handlers.append(handler)

    def remove_telemetry_handler(
        self,
        handler: Callable[[TelemetryData], Awaitable[None]]
    ) -> None:
        """Remove a telemetry handler."""
        if handler in self._telemetry_handlers:
            self._telemetry_handlers.remove(handler)

    # Status

    def get_status(self) -> Dict[str, Any]:
        """Get manager status."""
        return {
            "brokers": {
                bid: {
                    "name": b.name,
                    "connected": b.connected,
                    "last_connected": b.last_connected.isoformat() if b.last_connected else None,
                    "last_error": b.last_error,
                }
                for bid, b in self._brokers.items()
            },
            "devices": {
                "total": len(self._devices),
                "online": len(self.get_online_devices()),
            },
            "clients": {
                bid: client.get_stats()
                for bid, client in self._clients.items()
            },
        }

    async def start(self) -> None:
        """Start the broker manager."""
        self._running = True
        await self.connect_all()

        # Start background tasks
        asyncio.create_task(self._health_check_loop())

    async def stop(self) -> None:
        """Stop the broker manager."""
        self._running = False
        await self.disconnect_all()

    async def _health_check_loop(self) -> None:
        """Periodic health check for connections."""
        while self._running:
            await asyncio.sleep(30)  # Check every 30 seconds

            for broker_id, broker in self._brokers.items():
                if broker.enabled and not broker.connected:
                    logger.info(f"Attempting to reconnect to {broker.name}")
                    await self.connect_broker(broker_id)

                # Check device timeouts
                timeout_threshold = datetime.utcnow()
                for device in self._devices.values():
                    if device.state.last_seen:
                        elapsed = (timeout_threshold - device.state.last_seen).total_seconds()
                        if elapsed > 300:  # 5 minutes timeout
                            device.state.status = DeviceStatus.OFFLINE
