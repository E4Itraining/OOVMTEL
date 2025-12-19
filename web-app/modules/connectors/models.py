"""
ERP/MES Connectors - Data Models
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ConnectorType(str, Enum):
    """Types of industrial connectors."""
    SAP = "sap"
    SAP_HANA = "sap_hana"
    ORACLE_ERP = "oracle_erp"
    KEPWARE = "kepware"
    FACTORYTALK = "factorytalk"
    IGNITION = "ignition"
    OSISOFT_PI = "osisoft_pi"
    WONDERWARE = "wonderware"
    GENERIC_OPC_UA = "generic_opc_ua"
    GENERIC_REST = "generic_rest"


class DataDirection(str, Enum):
    """Direction of data flow."""
    INBOUND = "inbound"      # From external system to SYNAPSIX
    OUTBOUND = "outbound"    # From SYNAPSIX to external system
    BIDIRECTIONAL = "bidirectional"


class SyncMode(str, Enum):
    """Synchronization mode."""
    REAL_TIME = "real_time"      # Push-based, immediate
    POLLING = "polling"          # Pull-based, scheduled
    BATCH = "batch"              # Scheduled batch transfers
    ON_DEMAND = "on_demand"      # Manual trigger only


class DataMapping(BaseModel):
    """Mapping between external and internal data fields."""
    external_field: str
    internal_field: str
    transform: Optional[str] = None  # Transformation expression
    data_type: str = "string"
    unit_conversion: Optional[Dict[str, Any]] = None
    default_value: Optional[Any] = None
    required: bool = False
    description: str = ""


class SyncConfig(BaseModel):
    """Synchronization configuration."""
    mode: SyncMode = SyncMode.POLLING
    interval_seconds: int = 60
    batch_size: int = 1000
    retry_attempts: int = 3
    retry_delay_seconds: int = 5
    timeout_seconds: int = 30
    enable_compression: bool = True
    enable_encryption: bool = True
    mappings: List[DataMapping] = Field(default_factory=list)


class SyncResult(BaseModel):
    """Result of a synchronization operation."""
    sync_id: str
    connector_type: ConnectorType
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str  # success, partial, failed
    records_processed: int = 0
    records_success: int = 0
    records_failed: int = 0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    duration_ms: float = 0
    next_sync_at: Optional[datetime] = None


class ERPData(BaseModel):
    """ERP system data structure."""
    # Production Orders
    production_orders: List[Dict[str, Any]] = Field(default_factory=list)
    # Work Orders
    work_orders: List[Dict[str, Any]] = Field(default_factory=list)
    # Material Master
    materials: List[Dict[str, Any]] = Field(default_factory=list)
    # Bill of Materials
    bom: List[Dict[str, Any]] = Field(default_factory=list)
    # Equipment/Asset Master
    equipment: List[Dict[str, Any]] = Field(default_factory=list)
    # Maintenance Plans
    maintenance_plans: List[Dict[str, Any]] = Field(default_factory=list)
    # Cost Centers
    cost_centers: List[Dict[str, Any]] = Field(default_factory=list)
    # Inventory
    inventory: List[Dict[str, Any]] = Field(default_factory=list)

    # Metadata
    source_system: str = ""
    extracted_at: Optional[datetime] = None
    record_count: int = 0


class MESData(BaseModel):
    """MES system data structure."""
    # Production Data
    production_counts: List[Dict[str, Any]] = Field(default_factory=list)
    # Quality Data
    quality_events: List[Dict[str, Any]] = Field(default_factory=list)
    # Downtime Events
    downtime_events: List[Dict[str, Any]] = Field(default_factory=list)
    # OEE Metrics
    oee_data: List[Dict[str, Any]] = Field(default_factory=list)
    # Batch/Lot Data
    batch_data: List[Dict[str, Any]] = Field(default_factory=list)
    # Process Parameters
    process_params: List[Dict[str, Any]] = Field(default_factory=list)
    # Alarms
    alarms: List[Dict[str, Any]] = Field(default_factory=list)
    # Operator Actions
    operator_actions: List[Dict[str, Any]] = Field(default_factory=list)

    # Metadata
    source_system: str = ""
    extracted_at: Optional[datetime] = None
    record_count: int = 0


class HistorianData(BaseModel):
    """Process Historian data structure."""
    # Tag values (time-series)
    tag_values: List[Dict[str, Any]] = Field(default_factory=list)
    # Tag metadata
    tag_definitions: List[Dict[str, Any]] = Field(default_factory=list)
    # Calculated values
    calculated_values: List[Dict[str, Any]] = Field(default_factory=list)
    # Events
    events: List[Dict[str, Any]] = Field(default_factory=list)

    # Time range
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    # Metadata
    source_system: str = ""
    extracted_at: Optional[datetime] = None
    record_count: int = 0


# Standard field mappings for common systems
SAP_STANDARD_MAPPINGS = {
    "equipment": [
        DataMapping(external_field="EQUNR", internal_field="equipment_id", description="Equipment Number"),
        DataMapping(external_field="EQKTX", internal_field="equipment_name", description="Equipment Description"),
        DataMapping(external_field="EQART", internal_field="equipment_type", description="Equipment Type"),
        DataMapping(external_field="WERK", internal_field="plant", description="Plant"),
        DataMapping(external_field="KOSTL", internal_field="cost_center", description="Cost Center"),
        DataMapping(external_field="INBDT", internal_field="install_date", data_type="date", description="Installation Date"),
    ],
    "maintenance_orders": [
        DataMapping(external_field="AUFNR", internal_field="order_id", description="Order Number"),
        DataMapping(external_field="AUART", internal_field="order_type", description="Order Type"),
        DataMapping(external_field="EQUNR", internal_field="equipment_id", description="Equipment"),
        DataMapping(external_field="PRIOK", internal_field="priority", description="Priority"),
        DataMapping(external_field="GSTRP", internal_field="scheduled_start", data_type="date", description="Scheduled Start"),
        DataMapping(external_field="GLTRP", internal_field="scheduled_end", data_type="date", description="Scheduled End"),
    ],
    "production_orders": [
        DataMapping(external_field="AUFNR", internal_field="order_id", description="Production Order"),
        DataMapping(external_field="MATNR", internal_field="material_id", description="Material Number"),
        DataMapping(external_field="GAMNG", internal_field="target_quantity", data_type="float", description="Target Quantity"),
        DataMapping(external_field="GMEIN", internal_field="unit", description="Unit of Measure"),
        DataMapping(external_field="GSTRP", internal_field="start_date", data_type="date", description="Start Date"),
    ],
}


KEPWARE_STANDARD_MAPPINGS = {
    "tags": [
        DataMapping(external_field="TagName", internal_field="tag_id", description="Tag Name"),
        DataMapping(external_field="Value", internal_field="value", data_type="float", description="Current Value"),
        DataMapping(external_field="Quality", internal_field="quality", description="Data Quality"),
        DataMapping(external_field="Timestamp", internal_field="timestamp", data_type="datetime", description="Timestamp"),
        DataMapping(external_field="DataType", internal_field="data_type", description="Data Type"),
        DataMapping(external_field="EngineeringUnits", internal_field="unit", description="Engineering Units"),
    ],
}


FACTORYTALK_STANDARD_MAPPINGS = {
    "tags": [
        DataMapping(external_field="Name", internal_field="tag_id", description="Tag Name"),
        DataMapping(external_field="Value", internal_field="value", data_type="float", description="Value"),
        DataMapping(external_field="Status", internal_field="quality", description="Status"),
        DataMapping(external_field="TimeStamp", internal_field="timestamp", data_type="datetime", description="Timestamp"),
        DataMapping(external_field="Description", internal_field="description", description="Description"),
    ],
    "alarms": [
        DataMapping(external_field="AlarmName", internal_field="alarm_id", description="Alarm Name"),
        DataMapping(external_field="Severity", internal_field="severity", description="Severity"),
        DataMapping(external_field="Message", internal_field="message", description="Message"),
        DataMapping(external_field="AckRequired", internal_field="ack_required", data_type="bool", description="Acknowledgment Required"),
    ],
}
