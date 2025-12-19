"""
MQTT Module - Data Models
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from pydantic import BaseModel, Field


class QoSLevel(int, Enum):
    """MQTT Quality of Service levels."""
    AT_MOST_ONCE = 0    # Fire and forget
    AT_LEAST_ONCE = 1   # Acknowledged delivery
    EXACTLY_ONCE = 2    # Assured delivery


class DeviceStatus(str, Enum):
    """IoT device connection status."""
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    ERROR = "error"
    SLEEPING = "sleeping"


class MessageType(str, Enum):
    """Types of MQTT messages."""
    TELEMETRY = "telemetry"         # Sensor data
    EVENT = "event"                  # Device events
    COMMAND = "command"              # Commands to devices
    COMMAND_RESPONSE = "command_response"
    STATE = "state"                  # Device state updates
    CONFIG = "config"                # Configuration updates
    ALERT = "alert"                  # Device alerts
    HEARTBEAT = "heartbeat"          # Keep-alive
    LWT = "lwt"                      # Last Will and Testament


class MQTTMessage(BaseModel):
    """MQTT message structure."""
    message_id: str
    topic: str
    payload: Union[str, bytes, Dict[str, Any]]
    qos: QoSLevel = QoSLevel.AT_LEAST_ONCE
    retain: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Parsed content
    message_type: MessageType = MessageType.TELEMETRY
    device_id: Optional[str] = None
    parsed_payload: Optional[Dict[str, Any]] = None

    # Processing metadata
    received_at: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False
    processing_error: Optional[str] = None


class TopicSubscription(BaseModel):
    """Topic subscription configuration."""
    subscription_id: str
    topic_pattern: str              # e.g., "sensors/+/temperature", "devices/#"
    qos: QoSLevel = QoSLevel.AT_LEAST_ONCE
    handler: Optional[str] = None   # Handler function name
    enabled: bool = True

    # Parsing configuration
    extract_device_id: bool = True
    device_id_position: int = 1     # Position in topic path
    payload_format: str = "json"    # json, raw, csv

    # Filtering
    include_patterns: List[str] = Field(default_factory=list)
    exclude_patterns: List[str] = Field(default_factory=list)

    # Stats
    messages_received: int = 0
    last_message_at: Optional[datetime] = None


class DeviceState(BaseModel):
    """Current state of an IoT device."""
    device_id: str
    status: DeviceStatus = DeviceStatus.UNKNOWN
    last_seen: Optional[datetime] = None
    last_telemetry: Optional[datetime] = None

    # Connection info
    connected: bool = False
    connection_count: int = 0
    disconnect_count: int = 0
    last_disconnect_reason: Optional[str] = None

    # Current values
    current_values: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Statistics
    messages_sent: int = 0
    messages_received: int = 0
    errors_count: int = 0
    uptime_percent: float = 100.0


class IoTDevice(BaseModel):
    """IoT device registration."""
    device_id: str
    device_type: str                # sensor, actuator, gateway, controller
    name: str
    description: str = ""

    # MQTT settings
    client_id: Optional[str] = None
    topic_prefix: str = ""          # e.g., "plant1/line2/sensor123"
    telemetry_topic: str = ""
    command_topic: str = ""
    state_topic: str = ""

    # Authentication
    username: Optional[str] = None
    use_certificate: bool = False
    certificate_cn: Optional[str] = None

    # Device capabilities
    capabilities: List[str] = Field(default_factory=list)  # e.g., ["temperature", "humidity"]
    supports_commands: bool = False
    supports_config: bool = False

    # Location and hierarchy
    location: Optional[str] = None
    parent_device_id: Optional[str] = None  # For gateway hierarchy
    equipment_id: Optional[str] = None      # Link to SYNAPSIX equipment

    # State
    state: DeviceState = Field(default_factory=lambda: DeviceState(device_id=""))
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_config_update: Optional[datetime] = None

    # Tags for filtering
    tags: Dict[str, str] = Field(default_factory=dict)


class TelemetryData(BaseModel):
    """Telemetry data from IoT device."""
    device_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Measurements
    measurements: Dict[str, float] = Field(default_factory=dict)
    # e.g., {"temperature": 25.5, "humidity": 60.0, "pressure": 1013.25}

    # Additional fields
    unit_map: Dict[str, str] = Field(default_factory=dict)
    # e.g., {"temperature": "°C", "humidity": "%", "pressure": "hPa"}

    quality: Dict[str, str] = Field(default_factory=dict)
    # e.g., {"temperature": "good", "humidity": "good"}

    # Metadata
    sequence_number: Optional[int] = None
    batch_id: Optional[str] = None
    source_topic: Optional[str] = None


class DeviceCommand(BaseModel):
    """Command to send to IoT device."""
    command_id: str
    device_id: str
    command_type: str               # e.g., "setpoint", "calibrate", "reset"
    parameters: Dict[str, Any] = Field(default_factory=dict)

    # MQTT delivery
    topic: Optional[str] = None
    qos: QoSLevel = QoSLevel.AT_LEAST_ONCE
    retain: bool = False

    # Response handling
    expect_response: bool = True
    response_topic: Optional[str] = None
    timeout_seconds: int = 30

    # Status
    sent: bool = False
    sent_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    priority: int = 1               # 1 = highest


class DeviceAlert(BaseModel):
    """Alert from IoT device."""
    alert_id: str
    device_id: str
    alert_type: str                 # threshold, connectivity, error, warning
    severity: str                   # critical, high, medium, low
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)

    # Timing
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    # Context
    source_topic: Optional[str] = None
    related_measurement: Optional[str] = None
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None


# Topic patterns for industrial IoT
INDUSTRIAL_TOPIC_PATTERNS = {
    "sparkplug_b": {
        "namespace": "spBv1.0",
        "node_birth": "spBv1.0/{group_id}/NBIRTH/{node_id}",
        "node_data": "spBv1.0/{group_id}/NDATA/{node_id}",
        "node_death": "spBv1.0/{group_id}/NDEATH/{node_id}",
        "device_birth": "spBv1.0/{group_id}/DBIRTH/{node_id}/{device_id}",
        "device_data": "spBv1.0/{group_id}/DDATA/{node_id}/{device_id}",
        "device_death": "spBv1.0/{group_id}/DDEATH/{node_id}/{device_id}",
    },
    "unified_namespace": {
        "enterprise": "{enterprise}/{site}/{area}/{line}/{cell}",
        "telemetry": "{enterprise}/{site}/telemetry/{device_type}/{device_id}",
        "commands": "{enterprise}/{site}/commands/{device_type}/{device_id}",
        "events": "{enterprise}/{site}/events/{device_type}/{device_id}",
    },
    "simple": {
        "telemetry": "devices/{device_id}/telemetry",
        "commands": "devices/{device_id}/commands",
        "state": "devices/{device_id}/state",
        "config": "devices/{device_id}/config",
    },
}


# Common payload schemas
PAYLOAD_SCHEMAS = {
    "simple_telemetry": {
        "type": "object",
        "properties": {
            "device_id": {"type": "string"},
            "timestamp": {"type": "string", "format": "date-time"},
            "values": {"type": "object"},
        },
    },
    "sparkplug_metric": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {"type": "number"},
            "timestamp": {"type": "integer"},
            "dataType": {"type": "string"},
        },
    },
}
