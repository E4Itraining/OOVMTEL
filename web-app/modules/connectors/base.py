"""
ERP/MES Connectors - Base Connector Class
"""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

from .models import (
    ConnectorType,
    SyncConfig,
    SyncResult,
    DataMapping,
    ERPData,
    MESData,
    HistorianData,
)

logger = logging.getLogger(__name__)


class ConnectionStatus(str, Enum):
    """Connection status states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


class ConnectorConfig(BaseModel):
    """Base configuration for all connectors."""
    connector_id: str = Field(default_factory=lambda: f"CONN-{uuid.uuid4().hex[:8].upper()}")
    connector_type: ConnectorType
    name: str
    description: str = ""
    enabled: bool = True

    # Connection settings
    host: str
    port: int
    use_ssl: bool = True
    verify_ssl: bool = True

    # Authentication
    auth_type: str = "basic"  # basic, oauth2, api_key, certificate
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    certificate_path: Optional[str] = None

    # Sync configuration
    sync_config: SyncConfig = Field(default_factory=SyncConfig)

    # Retry settings
    max_retries: int = 3
    retry_delay_seconds: int = 5
    connection_timeout_seconds: int = 30

    # Rate limiting
    rate_limit_requests_per_minute: int = 60

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)


class BaseConnector(ABC):
    """
    Abstract base class for all ERP/MES connectors.

    Provides common functionality for:
    - Connection management
    - Data synchronization
    - Error handling
    - Logging and monitoring
    """

    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.status = ConnectionStatus.DISCONNECTED
        self._connection = None
        self._last_sync: Optional[datetime] = None
        self._sync_history: List[SyncResult] = []

        logger.info(f"Initialized {config.connector_type.value} connector: {config.name}")

    @property
    def connector_id(self) -> str:
        return self.config.connector_id

    @property
    def connector_type(self) -> ConnectorType:
        return self.config.connector_type

    @property
    def is_connected(self) -> bool:
        return self.status == ConnectionStatus.CONNECTED

    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the external system.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Close connection to the external system.

        Returns:
            True if disconnection successful, False otherwise
        """
        pass

    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to the external system.

        Returns:
            Dict with connection test results
        """
        pass

    @abstractmethod
    async def fetch_data(
        self,
        data_type: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch data from the external system.

        Args:
            data_type: Type of data to fetch (equipment, orders, etc.)
            filters: Optional filters to apply
            limit: Maximum number of records

        Returns:
            Fetched data
        """
        pass

    @abstractmethod
    async def push_data(
        self,
        data_type: str,
        data: Dict[str, Any]
    ) -> SyncResult:
        """
        Push data to the external system.

        Args:
            data_type: Type of data to push
            data: Data to push

        Returns:
            Sync result
        """
        pass

    async def sync(
        self,
        direction: str = "inbound",
        data_types: Optional[List[str]] = None
    ) -> SyncResult:
        """
        Perform data synchronization.

        Args:
            direction: inbound, outbound, or bidirectional
            data_types: Specific data types to sync (None = all)

        Returns:
            Sync result
        """
        sync_id = f"SYNC-{uuid.uuid4().hex[:8].upper()}"
        started_at = datetime.utcnow()

        result = SyncResult(
            sync_id=sync_id,
            connector_type=self.connector_type,
            started_at=started_at,
            status="in_progress"
        )

        try:
            if not self.is_connected:
                await self.connect()

            if direction in ["inbound", "bidirectional"]:
                inbound_result = await self._sync_inbound(data_types)
                result.records_processed += inbound_result.get("processed", 0)
                result.records_success += inbound_result.get("success", 0)
                result.records_failed += inbound_result.get("failed", 0)
                result.errors.extend(inbound_result.get("errors", []))

            if direction in ["outbound", "bidirectional"]:
                outbound_result = await self._sync_outbound(data_types)
                result.records_processed += outbound_result.get("processed", 0)
                result.records_success += outbound_result.get("success", 0)
                result.records_failed += outbound_result.get("failed", 0)
                result.errors.extend(outbound_result.get("errors", []))

            result.status = "success" if not result.errors else "partial"

        except Exception as e:
            logger.error(f"Sync failed for {self.connector_id}: {e}")
            result.status = "failed"
            result.errors.append(str(e))

        result.completed_at = datetime.utcnow()
        result.duration_ms = (result.completed_at - started_at).total_seconds() * 1000

        self._last_sync = result.completed_at
        self._sync_history.append(result)

        return result

    async def _sync_inbound(self, data_types: Optional[List[str]]) -> Dict[str, Any]:
        """Perform inbound synchronization (external -> SYNAPSIX)."""
        result = {"processed": 0, "success": 0, "failed": 0, "errors": []}

        types_to_sync = data_types or self._get_supported_data_types()

        for data_type in types_to_sync:
            try:
                data = await self.fetch_data(data_type)
                records = data.get("records", [])
                result["processed"] += len(records)

                # Transform and store data
                transformed = self._transform_data(records, data_type, "inbound")
                stored = await self._store_data(transformed, data_type)

                result["success"] += stored.get("success", 0)
                result["failed"] += stored.get("failed", 0)

            except Exception as e:
                logger.error(f"Inbound sync failed for {data_type}: {e}")
                result["errors"].append(f"{data_type}: {str(e)}")

        return result

    async def _sync_outbound(self, data_types: Optional[List[str]]) -> Dict[str, Any]:
        """Perform outbound synchronization (SYNAPSIX -> external)."""
        result = {"processed": 0, "success": 0, "failed": 0, "errors": []}

        types_to_sync = data_types or self._get_supported_data_types()

        for data_type in types_to_sync:
            try:
                # Get pending outbound data
                pending = await self._get_pending_outbound(data_type)
                result["processed"] += len(pending)

                if pending:
                    # Transform and push data
                    transformed = self._transform_data(pending, data_type, "outbound")
                    push_result = await self.push_data(data_type, {"records": transformed})

                    result["success"] += push_result.records_success
                    result["failed"] += push_result.records_failed
                    result["errors"].extend(push_result.errors)

            except Exception as e:
                logger.error(f"Outbound sync failed for {data_type}: {e}")
                result["errors"].append(f"{data_type}: {str(e)}")

        return result

    def _transform_data(
        self,
        records: List[Dict[str, Any]],
        data_type: str,
        direction: str
    ) -> List[Dict[str, Any]]:
        """Transform data using configured mappings."""
        mappings = self._get_mappings(data_type)
        if not mappings:
            return records

        transformed = []
        for record in records:
            new_record = {}
            for mapping in mappings:
                source_field = mapping.external_field if direction == "inbound" else mapping.internal_field
                target_field = mapping.internal_field if direction == "inbound" else mapping.external_field

                value = record.get(source_field, mapping.default_value)

                # Apply transformation if specified
                if mapping.transform and value is not None:
                    value = self._apply_transform(value, mapping.transform)

                # Apply unit conversion if specified
                if mapping.unit_conversion and value is not None:
                    value = self._convert_unit(value, mapping.unit_conversion)

                if value is not None or mapping.required:
                    new_record[target_field] = value

            transformed.append(new_record)

        return transformed

    def _apply_transform(self, value: Any, transform: str) -> Any:
        """Apply transformation expression to a value."""
        try:
            # Simple transformations
            if transform == "uppercase":
                return str(value).upper()
            elif transform == "lowercase":
                return str(value).lower()
            elif transform == "strip":
                return str(value).strip()
            elif transform.startswith("multiply:"):
                factor = float(transform.split(":")[1])
                return float(value) * factor
            elif transform.startswith("divide:"):
                divisor = float(transform.split(":")[1])
                return float(value) / divisor if divisor != 0 else None
            elif transform.startswith("add:"):
                addend = float(transform.split(":")[1])
                return float(value) + addend
            else:
                return value
        except Exception as e:
            logger.warning(f"Transform failed: {e}")
            return value

    def _convert_unit(self, value: float, conversion: Dict[str, Any]) -> float:
        """Convert value between units."""
        try:
            factor = conversion.get("factor", 1.0)
            offset = conversion.get("offset", 0.0)
            return (float(value) * factor) + offset
        except Exception as e:
            logger.warning(f"Unit conversion failed: {e}")
            return value

    def _get_mappings(self, data_type: str) -> List[DataMapping]:
        """Get field mappings for a data type."""
        return self.config.sync_config.mappings

    def _get_supported_data_types(self) -> List[str]:
        """Get list of supported data types for this connector."""
        return []

    async def _store_data(self, data: List[Dict], data_type: str) -> Dict[str, Any]:
        """Store transformed data in SYNAPSIX."""
        # Override in subclasses for actual storage
        return {"success": len(data), "failed": 0}

    async def _get_pending_outbound(self, data_type: str) -> List[Dict]:
        """Get pending outbound data for sync."""
        # Override in subclasses for actual retrieval
        return []

    def get_status(self) -> Dict[str, Any]:
        """Get current connector status."""
        return {
            "connector_id": self.connector_id,
            "connector_type": self.connector_type.value,
            "name": self.config.name,
            "status": self.status.value,
            "is_connected": self.is_connected,
            "last_sync": self._last_sync.isoformat() if self._last_sync else None,
            "sync_count": len(self._sync_history),
            "enabled": self.config.enabled,
        }

    def get_sync_history(self, limit: int = 10) -> List[SyncResult]:
        """Get recent sync history."""
        return self._sync_history[-limit:]
