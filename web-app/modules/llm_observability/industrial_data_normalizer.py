"""
Industrial Data Normalizer.

Handles heterogeneous data from multiple industrial sources (SCADA, MES, PLM, OPC-UA)
and normalizes them into a unified format for LLM context enrichment and observability.

This module provides:
- Multi-source data ingestion (SCADA, MES, PLM, OPC-UA)
- Schema normalization and validation
- Data coherence and correlation
- Time-series alignment
- Contextual enrichment for LLM queries
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Constants
# =============================================================================

class IndustrialDataSource(str, Enum):
    """Industrial data source types."""
    SCADA = "scada"
    MES = "mes"
    PLM = "plm"
    OPCUA = "opcua"
    ERP = "erp"
    CMMS = "cmms"  # Computerized Maintenance Management System
    HISTORIAN = "historian"
    CUSTOM = "custom"


class DataQuality(str, Enum):
    """Data quality indicators."""
    GOOD = "good"
    UNCERTAIN = "uncertain"
    BAD = "bad"
    INTERPOLATED = "interpolated"
    STALE = "stale"


class AlarmSeverity(str, Enum):
    """Alarm severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class EventType(str, Enum):
    """Industrial event types."""
    # SCADA events
    MEASUREMENT = "measurement"
    ALARM = "alarm"
    STATE_CHANGE = "state_change"

    # MES events
    PRODUCTION_START = "production_start"
    PRODUCTION_END = "production_end"
    QUALITY_CHECK = "quality_check"
    DOWNTIME = "downtime"
    MATERIAL_CONSUMED = "material_consumed"

    # PLM events
    DOCUMENT_CHANGE = "document_change"
    REVISION = "revision"
    APPROVAL = "approval"
    BOM_UPDATE = "bom_update"

    # OPC-UA events
    NODE_UPDATE = "node_update"
    SUBSCRIPTION_DATA = "subscription_data"

    # Generic
    CUSTOM = "custom"


# =============================================================================
# Normalized Data Models
# =============================================================================

@dataclass
class NormalizedTimestamp:
    """Normalized timestamp with source and server times."""
    utc: datetime
    source_time: Optional[datetime] = None
    server_time: Optional[datetime] = None
    timezone: str = "UTC"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "utc": self.utc.isoformat(),
            "source_time": self.source_time.isoformat() if self.source_time else None,
            "server_time": self.server_time.isoformat() if self.server_time else None,
            "timezone": self.timezone,
        }


@dataclass
class NormalizedLocation:
    """Normalized location/hierarchy information."""
    site: Optional[str] = None
    area: Optional[str] = None
    line: Optional[str] = None
    equipment: Optional[str] = None
    component: Optional[str] = None

    # ISA-95 hierarchy
    enterprise: Optional[str] = None
    site_isa95: Optional[str] = None
    area_isa95: Optional[str] = None
    work_center: Optional[str] = None
    work_unit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "site": self.site,
            "area": self.area,
            "line": self.line,
            "equipment": self.equipment,
            "component": self.component,
            "hierarchy": f"{self.site or ''}/{self.area or ''}/{self.equipment or ''}".strip("/"),
        }

    @property
    def full_path(self) -> str:
        """Get full hierarchical path."""
        parts = [p for p in [self.site, self.area, self.line, self.equipment, self.component] if p]
        return "/".join(parts)


@dataclass
class NormalizedValue:
    """Normalized value with metadata."""
    value: Any
    unit: Optional[str] = None
    data_type: str = "float"
    quality: DataQuality = DataQuality.GOOD

    # Range information
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    engineering_units: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "unit": self.unit,
            "data_type": self.data_type,
            "quality": self.quality.value,
        }

    @property
    def is_numeric(self) -> bool:
        return self.data_type in ("float", "int", "double", "decimal")


@dataclass
class NormalizedIndustrialEvent:
    """
    Unified industrial event representation.

    This is the core normalized format that all industrial data sources
    are converted to for consistent processing and LLM context.
    """
    # Identification
    event_id: str
    timestamp: NormalizedTimestamp
    source: IndustrialDataSource
    event_type: EventType

    # Location
    location: NormalizedLocation

    # Data
    tag_id: Optional[str] = None
    tag_name: Optional[str] = None
    value: Optional[NormalizedValue] = None

    # Context
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None

    # Relationships
    related_events: List[str] = field(default_factory=list)
    parent_event: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_data: Optional[Dict[str, Any]] = None

    # Tracing
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.to_dict(),
            "source": self.source.value,
            "event_type": self.event_type.value,
            "location": self.location.to_dict(),
            "tag_id": self.tag_id,
            "tag_name": self.tag_name,
            "value": self.value.to_dict() if self.value else None,
            "description": self.description,
            "category": self.category,
            "subcategory": self.subcategory,
            "metadata": self.metadata,
            "correlation_id": self.correlation_id,
        }

    def to_llm_context(self) -> str:
        """Convert to human-readable string for LLM context."""
        parts = [f"[{self.source.value.upper()}]"]

        if self.location.full_path:
            parts.append(f"Location: {self.location.full_path}")

        if self.tag_name:
            parts.append(f"Tag: {self.tag_name}")

        if self.value:
            val_str = f"{self.value.value}"
            if self.value.unit:
                val_str += f" {self.value.unit}"
            if self.value.quality != DataQuality.GOOD:
                val_str += f" ({self.value.quality.value})"
            parts.append(f"Value: {val_str}")

        if self.description:
            parts.append(f"Description: {self.description}")

        parts.append(f"Time: {self.timestamp.utc.strftime('%Y-%m-%d %H:%M:%S')}")

        return " | ".join(parts)


# =============================================================================
# Source-Specific Normalizers
# =============================================================================

class SCADANormalizer:
    """Normalizes SCADA data to unified format."""

    # Unit standardization mapping
    UNIT_MAP = {
        "°c": "°C", "celsius": "°C", "deg_c": "°C",
        "°f": "°F", "fahrenheit": "°F",
        "bar": "bar", "psi": "psi", "kpa": "kPa", "mpa": "MPa",
        "m3/h": "m³/h", "m3h": "m³/h", "l/min": "L/min", "gpm": "gal/min",
        "%": "%", "percent": "%",
        "mm/s": "mm/s", "in/s": "in/s",
        "kw": "kW", "mw": "MW", "w": "W",
        "a": "A", "ma": "mA", "v": "V", "mv": "mV",
    }

    def normalize(self, data: Dict[str, Any]) -> NormalizedIndustrialEvent:
        """
        Normalize SCADA data point.

        Expected input format:
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "tag_id": "SCADA.ZONE_A.REACTOR_001.TEMP",
            "tag_name": "reactor_001_temp",
            "value": 75.5,
            "unit": "°C",
            "quality": "good",
            "source": "plc_main",
            "area": "zone_a",
            "equipment_id": "reactor_001"
        }
        """
        import uuid

        # Parse timestamp
        ts_str = data.get("timestamp", datetime.utcnow().isoformat())
        if isinstance(ts_str, str):
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        else:
            ts = ts_str

        timestamp = NormalizedTimestamp(utc=ts)

        # Parse location
        location = NormalizedLocation(
            area=data.get("area"),
            equipment=data.get("equipment_id"),
        )

        # Parse tag_id for additional location info
        tag_id = data.get("tag_id", "")
        if tag_id:
            parts = tag_id.split(".")
            if len(parts) >= 2:
                location.site = parts[0] if parts[0] != "SCADA" else None
                if len(parts) >= 3:
                    location.area = location.area or parts[1].lower()
                if len(parts) >= 4:
                    location.equipment = location.equipment or parts[2].lower()

        # Normalize unit
        raw_unit = data.get("unit", "")
        unit = self.UNIT_MAP.get(raw_unit.lower(), raw_unit)

        # Parse quality
        quality_str = data.get("quality", "good").lower()
        quality_map = {
            "good": DataQuality.GOOD,
            "uncertain": DataQuality.UNCERTAIN,
            "bad": DataQuality.BAD,
        }
        quality = quality_map.get(quality_str, DataQuality.UNCERTAIN)

        # Create normalized value
        value = NormalizedValue(
            value=data.get("value"),
            unit=unit,
            data_type="float" if isinstance(data.get("value"), (int, float)) else "string",
            quality=quality,
        )

        # Determine event type
        tag_name = data.get("tag_name", "").lower()
        if "alarm" in tag_name:
            event_type = EventType.ALARM
        elif "status" in tag_name or "state" in tag_name:
            event_type = EventType.STATE_CHANGE
        else:
            event_type = EventType.MEASUREMENT

        return NormalizedIndustrialEvent(
            event_id=str(uuid.uuid4()),
            timestamp=timestamp,
            source=IndustrialDataSource.SCADA,
            event_type=event_type,
            location=location,
            tag_id=tag_id,
            tag_name=data.get("tag_name"),
            value=value,
            category="process_data",
            metadata={"plc_source": data.get("source")},
            raw_data=data,
        )


class MESNormalizer:
    """Normalizes MES data to unified format."""

    EVENT_TYPE_MAP = {
        "production_start": EventType.PRODUCTION_START,
        "production_end": EventType.PRODUCTION_END,
        "quality_check": EventType.QUALITY_CHECK,
        "downtime_start": EventType.DOWNTIME,
        "downtime_end": EventType.DOWNTIME,
        "material_consumed": EventType.MATERIAL_CONSUMED,
    }

    def normalize(self, data: Dict[str, Any]) -> NormalizedIndustrialEvent:
        """
        Normalize MES production event.

        Expected input format:
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "event_type": "production_end",
            "order_id": "ORD-12345",
            "product_id": "product_a",
            "workstation_id": "ws_assembly_01",
            "operator_id": "operator_001",
            "quantity": 5,
            "status": "completed",
            "cycle_time_ms": 15000,
            "quality_score": 98.5,
            "defects": 0
        }
        """
        import uuid

        # Parse timestamp
        ts_str = data.get("timestamp", datetime.utcnow().isoformat())
        if isinstance(ts_str, str):
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        else:
            ts = ts_str

        timestamp = NormalizedTimestamp(utc=ts)

        # Parse location from workstation
        workstation = data.get("workstation_id", "")
        location = NormalizedLocation(
            work_center=workstation,
            equipment=workstation,
        )

        # Parse event type
        event_type_str = data.get("event_type", "custom")
        event_type = self.EVENT_TYPE_MAP.get(event_type_str, EventType.CUSTOM)

        # Build description
        product = data.get("product_id", "unknown")
        quantity = data.get("quantity", 0)
        description = f"{event_type_str}: {quantity}x {product} at {workstation}"

        # Create normalized value (using quality_score as primary metric)
        value = NormalizedValue(
            value=data.get("quality_score", data.get("quantity")),
            unit="%" if "quality" in str(data.get("quality_score")) else "units",
            data_type="float",
            quality=DataQuality.GOOD,
        )

        return NormalizedIndustrialEvent(
            event_id=str(uuid.uuid4()),
            timestamp=timestamp,
            source=IndustrialDataSource.MES,
            event_type=event_type,
            location=location,
            tag_id=data.get("order_id"),
            tag_name=f"{workstation}_{event_type_str}",
            value=value,
            description=description,
            category="production",
            subcategory=event_type_str,
            metadata={
                "order_id": data.get("order_id"),
                "product_id": data.get("product_id"),
                "operator_id": data.get("operator_id"),
                "cycle_time_ms": data.get("cycle_time_ms"),
                "defects": data.get("defects"),
                "status": data.get("status"),
            },
            raw_data=data,
        )


class PLMNormalizer:
    """Normalizes PLM data to unified format."""

    CHANGE_TYPE_MAP = {
        "create": EventType.DOCUMENT_CHANGE,
        "modify": EventType.DOCUMENT_CHANGE,
        "delete": EventType.DOCUMENT_CHANGE,
        "revision": EventType.REVISION,
        "approve": EventType.APPROVAL,
        "reject": EventType.APPROVAL,
        "bom_add": EventType.BOM_UPDATE,
        "bom_remove": EventType.BOM_UPDATE,
    }

    def normalize(self, data: Dict[str, Any]) -> NormalizedIndustrialEvent:
        """
        Normalize PLM engineering data.

        Expected input format:
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "document_id": "DOC-001",
            "revision": "A.2",
            "author": "engineer_001",
            "change_type": "revision",
            "component_id": "COMP-123",
            "bom_level": 2,
            "status": "released",
            "approval_status": "approved"
        }
        """
        import uuid

        # Parse timestamp
        ts_str = data.get("timestamp", datetime.utcnow().isoformat())
        if isinstance(ts_str, str):
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        else:
            ts = ts_str

        timestamp = NormalizedTimestamp(utc=ts)

        # Location from component
        location = NormalizedLocation(
            component=data.get("component_id"),
        )

        # Event type
        change_type = data.get("change_type", "custom")
        event_type = self.CHANGE_TYPE_MAP.get(change_type, EventType.CUSTOM)

        # Description
        doc_id = data.get("document_id", "unknown")
        revision = data.get("revision", "")
        description = f"PLM {change_type}: {doc_id} rev {revision}"

        return NormalizedIndustrialEvent(
            event_id=str(uuid.uuid4()),
            timestamp=timestamp,
            source=IndustrialDataSource.PLM,
            event_type=event_type,
            location=location,
            tag_id=data.get("document_id"),
            tag_name=f"{data.get('component_id')}_{change_type}",
            description=description,
            category="engineering",
            subcategory=change_type,
            metadata={
                "document_id": data.get("document_id"),
                "revision": data.get("revision"),
                "author": data.get("author"),
                "bom_level": data.get("bom_level"),
                "status": data.get("status"),
                "approval_status": data.get("approval_status"),
            },
            raw_data=data,
        )


class OPCUANormalizer:
    """Normalizes OPC-UA data to unified format."""

    # OPC-UA status codes
    STATUS_CODE_MAP = {
        0: DataQuality.GOOD,
        0x40000000: DataQuality.UNCERTAIN,
        0x80000000: DataQuality.BAD,
    }

    def normalize(self, data: Dict[str, Any]) -> NormalizedIndustrialEvent:
        """
        Normalize OPC-UA node data.

        Expected input format:
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "node_id": "ns=2;s=Device1.Temperature",
            "display_name": "Temperature Sensor 1",
            "value": 25.5,
            "data_type": "Double",
            "status_code": 0,
            "source_timestamp": "2024-01-01T00:00:00Z",
            "server_timestamp": "2024-01-01T00:00:01Z",
            "namespace": "Device1"
        }
        """
        import uuid

        # Parse timestamps
        ts_str = data.get("timestamp", datetime.utcnow().isoformat())
        if isinstance(ts_str, str):
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        else:
            ts = ts_str

        source_ts = None
        if data.get("source_timestamp"):
            source_ts = datetime.fromisoformat(data["source_timestamp"].replace("Z", "+00:00"))

        server_ts = None
        if data.get("server_timestamp"):
            server_ts = datetime.fromisoformat(data["server_timestamp"].replace("Z", "+00:00"))

        timestamp = NormalizedTimestamp(
            utc=ts,
            source_time=source_ts,
            server_time=server_ts,
        )

        # Parse node_id for location
        node_id = data.get("node_id", "")
        namespace = data.get("namespace", "")
        location = NormalizedLocation(
            site=namespace,
        )

        # Parse node path
        if ";" in node_id:
            _, node_path = node_id.split(";", 1)
            if "=" in node_path:
                _, node_path = node_path.split("=", 1)
            parts = node_path.split(".")
            if len(parts) >= 1:
                location.equipment = parts[0]
            if len(parts) >= 2:
                location.component = parts[1]

        # Quality from status code
        status_code = data.get("status_code", 0)
        quality = DataQuality.GOOD
        for code, qual in self.STATUS_CODE_MAP.items():
            if status_code & code:
                quality = qual
                break

        # Data type mapping
        opc_type = data.get("data_type", "").lower()
        type_map = {
            "double": "float", "float": "float",
            "int32": "int", "int64": "int", "uint32": "int", "uint16": "int",
            "boolean": "bool", "bool": "bool",
            "string": "string",
        }
        data_type = type_map.get(opc_type, "string")

        value = NormalizedValue(
            value=data.get("value"),
            data_type=data_type,
            quality=quality,
        )

        return NormalizedIndustrialEvent(
            event_id=str(uuid.uuid4()),
            timestamp=timestamp,
            source=IndustrialDataSource.OPCUA,
            event_type=EventType.NODE_UPDATE,
            location=location,
            tag_id=node_id,
            tag_name=data.get("display_name"),
            value=value,
            category="opcua",
            metadata={
                "namespace": namespace,
                "status_code": status_code,
                "opc_data_type": data.get("data_type"),
            },
            raw_data=data,
        )


# =============================================================================
# Main Industrial Data Normalizer
# =============================================================================

class IndustrialDataNormalizer:
    """
    Main normalizer for heterogeneous industrial data.

    Provides unified interface for normalizing data from multiple sources
    and maintaining data coherence.
    """

    def __init__(self):
        """Initialize normalizers for each source."""
        self._normalizers = {
            IndustrialDataSource.SCADA: SCADANormalizer(),
            IndustrialDataSource.MES: MESNormalizer(),
            IndustrialDataSource.PLM: PLMNormalizer(),
            IndustrialDataSource.OPCUA: OPCUANormalizer(),
        }

        # Event buffer for correlation
        self._event_buffer: List[NormalizedIndustrialEvent] = []
        self._buffer_max_size = 10000
        self._buffer_max_age = timedelta(hours=1)

        # Statistics
        self._stats = defaultdict(int)

    def normalize(
        self,
        source: Union[str, IndustrialDataSource],
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> NormalizedIndustrialEvent:
        """
        Normalize data from any supported source.

        Args:
            source: Data source type (scada, mes, plm, opcua)
            data: Raw data dictionary
            correlation_id: Optional correlation ID for tracing

        Returns:
            NormalizedIndustrialEvent
        """
        # Convert string to enum
        if isinstance(source, str):
            source = IndustrialDataSource(source.lower())

        # Get appropriate normalizer
        normalizer = self._normalizers.get(source)
        if not normalizer:
            raise ValueError(f"No normalizer available for source: {source}")

        # Normalize
        event = normalizer.normalize(data)
        event.correlation_id = correlation_id

        # Update stats
        self._stats[f"normalized_{source.value}"] += 1
        self._stats["total_normalized"] += 1

        # Add to buffer
        self._add_to_buffer(event)

        return event

    def normalize_batch(
        self,
        source: Union[str, IndustrialDataSource],
        data_list: List[Dict[str, Any]],
        correlation_id: Optional[str] = None,
    ) -> List[NormalizedIndustrialEvent]:
        """Normalize a batch of data from the same source."""
        return [
            self.normalize(source, data, correlation_id)
            for data in data_list
        ]

    def normalize_mixed(
        self,
        data_list: List[Dict[str, Any]],
        correlation_id: Optional[str] = None,
    ) -> List[NormalizedIndustrialEvent]:
        """
        Normalize a batch of data from mixed sources.

        Each data dict must have a 'source' field indicating the type.
        """
        events = []
        for data in data_list:
            source = data.pop("_source", data.get("source_type", "custom"))
            events.append(self.normalize(source, data, correlation_id))
        return events

    def _add_to_buffer(self, event: NormalizedIndustrialEvent):
        """Add event to buffer and maintain size/age limits."""
        self._event_buffer.append(event)

        # Trim by size
        if len(self._event_buffer) > self._buffer_max_size:
            self._event_buffer = self._event_buffer[-self._buffer_max_size:]

        # Trim by age
        cutoff = datetime.utcnow() - self._buffer_max_age
        self._event_buffer = [
            e for e in self._event_buffer
            if e.timestamp.utc > cutoff
        ]

    def get_recent_events(
        self,
        source: Optional[IndustrialDataSource] = None,
        minutes: int = 5,
        limit: int = 100,
    ) -> List[NormalizedIndustrialEvent]:
        """Get recent normalized events from buffer."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        events = [
            e for e in self._event_buffer
            if e.timestamp.utc > cutoff
            and (source is None or e.source == source)
        ]

        return sorted(events, key=lambda e: e.timestamp.utc, reverse=True)[:limit]

    def get_context_for_llm(
        self,
        equipment: Optional[str] = None,
        area: Optional[str] = None,
        sources: Optional[List[IndustrialDataSource]] = None,
        minutes: int = 15,
        max_events: int = 50,
    ) -> str:
        """
        Generate contextual summary for LLM queries.

        Returns a formatted string with recent industrial data
        that can be used as context for LLM responses.
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        # Filter events
        events = []
        for e in self._event_buffer:
            if e.timestamp.utc < cutoff:
                continue
            if equipment and e.location.equipment != equipment:
                continue
            if area and e.location.area != area:
                continue
            if sources and e.source not in sources:
                continue
            events.append(e)

        # Sort and limit
        events = sorted(events, key=lambda e: e.timestamp.utc, reverse=True)[:max_events]

        if not events:
            return "No recent industrial data available for the specified criteria."

        # Group by source
        by_source = defaultdict(list)
        for e in events:
            by_source[e.source].append(e)

        # Build context string
        lines = [f"=== Industrial Context (last {minutes} minutes) ===\n"]

        for source, source_events in by_source.items():
            lines.append(f"\n--- {source.value.upper()} ({len(source_events)} events) ---")
            for e in source_events[:10]:  # Limit per source
                lines.append(e.to_llm_context())

        # Add summary
        lines.append(f"\n--- Summary ---")
        lines.append(f"Total events: {len(events)}")
        lines.append(f"Sources: {', '.join(s.value for s in by_source.keys())}")

        if equipment:
            lines.append(f"Equipment filter: {equipment}")
        if area:
            lines.append(f"Area filter: {area}")

        return "\n".join(lines)

    def correlate_events(
        self,
        time_window_seconds: int = 60,
        equipment: Optional[str] = None,
    ) -> List[List[NormalizedIndustrialEvent]]:
        """
        Find correlated events across sources.

        Groups events that occurred within the time window
        and are related to the same equipment.
        """
        if not self._event_buffer:
            return []

        # Filter by equipment if specified
        events = self._event_buffer
        if equipment:
            events = [e for e in events if e.location.equipment == equipment]

        # Sort by time
        events = sorted(events, key=lambda e: e.timestamp.utc)

        # Group correlated events
        groups = []
        current_group = [events[0]] if events else []

        for event in events[1:]:
            last_event = current_group[-1]
            time_diff = (event.timestamp.utc - last_event.timestamp.utc).total_seconds()

            if time_diff <= time_window_seconds:
                current_group.append(event)
            else:
                if len(current_group) > 1:
                    groups.append(current_group)
                current_group = [event]

        if len(current_group) > 1:
            groups.append(current_group)

        return groups

    def get_statistics(self) -> Dict[str, Any]:
        """Get normalizer statistics."""
        return {
            "total_normalized": self._stats["total_normalized"],
            "by_source": {
                source.value: self._stats[f"normalized_{source.value}"]
                for source in IndustrialDataSource
                if self._stats[f"normalized_{source.value}"] > 0
            },
            "buffer_size": len(self._event_buffer),
            "buffer_max_size": self._buffer_max_size,
        }


# =============================================================================
# Singleton and Factory
# =============================================================================

_normalizer_instance: Optional[IndustrialDataNormalizer] = None


def get_industrial_normalizer() -> IndustrialDataNormalizer:
    """Get the singleton industrial data normalizer."""
    global _normalizer_instance
    if _normalizer_instance is None:
        _normalizer_instance = IndustrialDataNormalizer()
    return _normalizer_instance


def normalize_industrial_data(
    source: str,
    data: Dict[str, Any],
) -> NormalizedIndustrialEvent:
    """Convenience function for quick normalization."""
    return get_industrial_normalizer().normalize(source, data)
