"""
SAP Connector - Integration with SAP ERP/S4HANA
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from .base import BaseConnector, ConnectorConfig, ConnectionStatus
from .models import (
    ConnectorType,
    SyncResult,
    ERPData,
    SAP_STANDARD_MAPPINGS,
)

logger = logging.getLogger(__name__)


class SAPConfig(ConnectorConfig):
    """SAP-specific configuration."""
    connector_type: ConnectorType = ConnectorType.SAP

    # SAP specific settings
    client: str = "100"                    # SAP Client
    system_id: str = ""                    # SAP System ID (SID)
    system_number: str = "00"              # SAP System Number
    language: str = "EN"

    # RFC Connection settings (for direct RFC)
    use_rfc: bool = False
    rfc_destination: str = ""

    # REST/OData settings (for S/4HANA)
    use_odata: bool = True
    odata_version: str = "v4"              # v2 or v4
    odata_service_path: str = "/sap/opu/odata/sap/"

    # BAPI settings
    bapis: Dict[str, str] = Field(default_factory=lambda: {
        "equipment": "BAPI_EQUI_GETLIST",
        "maintenance_orders": "BAPI_ALM_ORDER_GET_LIST",
        "production_orders": "BAPI_PRODORD_GET_LIST",
        "materials": "BAPI_MATERIAL_GET_LIST",
    })

    # OData services
    odata_services: Dict[str, str] = Field(default_factory=lambda: {
        "equipment": "API_EQUIPMENT_SRV",
        "maintenance_orders": "API_MAINTENANCEORDER_SRV",
        "production_orders": "API_PRODUCTION_ORDER_SRV",
        "materials": "API_PRODUCT_SRV",
        "plants": "API_PLANT_SRV",
    })


class SAPConnector(BaseConnector):
    """
    SAP ERP/S/4HANA Connector.

    Supports:
    - OData API (recommended for S/4HANA)
    - RFC/BAPI calls (for ECC)
    - Equipment master data
    - Maintenance orders
    - Production orders
    - Material master
    - Plant data
    """

    def __init__(self, config: SAPConfig):
        super().__init__(config)
        self.sap_config = config
        self._session = None
        self._token = None
        self._token_expiry: Optional[datetime] = None

    async def connect(self) -> bool:
        """Establish connection to SAP system."""
        self.status = ConnectionStatus.CONNECTING

        try:
            if self.sap_config.use_odata:
                success = await self._connect_odata()
            else:
                success = await self._connect_rfc()

            if success:
                self.status = ConnectionStatus.CONNECTED
                logger.info(f"Connected to SAP: {self.sap_config.system_id}")
            else:
                self.status = ConnectionStatus.ERROR

            return success

        except Exception as e:
            logger.error(f"SAP connection failed: {e}")
            self.status = ConnectionStatus.ERROR
            return False

    async def _connect_odata(self) -> bool:
        """Connect via OData API."""
        import httpx

        base_url = f"{'https' if self.config.use_ssl else 'http'}://{self.config.host}:{self.config.port}"

        try:
            self._session = httpx.AsyncClient(
                base_url=base_url,
                verify=self.config.verify_ssl,
                timeout=self.config.connection_timeout_seconds,
            )

            # Authenticate
            if self.config.auth_type == "basic":
                self._session.auth = (self.config.username, self.config.password)
            elif self.config.auth_type == "oauth2":
                await self._oauth2_authenticate()

            # Test connection with metadata request
            test_service = list(self.sap_config.odata_services.values())[0]
            response = await self._session.get(
                f"{self.sap_config.odata_service_path}{test_service}/$metadata"
            )

            return response.status_code in [200, 401]  # 401 means auth issue but connection works

        except Exception as e:
            logger.error(f"OData connection failed: {e}")
            return False

    async def _connect_rfc(self) -> bool:
        """Connect via RFC (requires pyrfc library)."""
        # RFC connection would require pyrfc library
        # This is a placeholder for the RFC implementation
        logger.warning("RFC connection not implemented - use OData instead")
        return False

    async def _oauth2_authenticate(self) -> None:
        """Perform OAuth2 authentication."""
        token_url = f"{'https' if self.config.use_ssl else 'http'}://{self.config.host}:{self.config.port}/sap/bc/sec/oauth2/token"

        response = await self._session.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            }
        )

        if response.status_code == 200:
            data = response.json()
            self._token = data.get("access_token")
            self._session.headers["Authorization"] = f"Bearer {self._token}"

    async def disconnect(self) -> bool:
        """Close SAP connection."""
        try:
            if self._session:
                await self._session.aclose()
                self._session = None

            self.status = ConnectionStatus.DISCONNECTED
            logger.info(f"Disconnected from SAP: {self.sap_config.system_id}")
            return True

        except Exception as e:
            logger.error(f"SAP disconnect failed: {e}")
            return False

    async def test_connection(self) -> Dict[str, Any]:
        """Test SAP connection."""
        result = {
            "success": False,
            "system_id": self.sap_config.system_id,
            "client": self.sap_config.client,
            "connection_type": "odata" if self.sap_config.use_odata else "rfc",
            "timestamp": datetime.utcnow().isoformat(),
            "details": {}
        }

        try:
            was_connected = self.is_connected

            if not was_connected:
                await self.connect()

            if self.is_connected:
                # Try to fetch system info
                info = await self._get_system_info()
                result["success"] = True
                result["details"] = info

            if not was_connected:
                await self.disconnect()

        except Exception as e:
            result["error"] = str(e)

        return result

    async def _get_system_info(self) -> Dict[str, Any]:
        """Get SAP system information."""
        return {
            "system_id": self.sap_config.system_id,
            "client": self.sap_config.client,
            "odata_version": self.sap_config.odata_version,
            "available_services": list(self.sap_config.odata_services.keys()),
        }

    async def fetch_data(
        self,
        data_type: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch data from SAP.

        Args:
            data_type: equipment, maintenance_orders, production_orders, materials
            filters: OData filter expressions
            limit: Maximum records ($top)
        """
        if not self.is_connected:
            await self.connect()

        service = self.sap_config.odata_services.get(data_type)
        if not service:
            raise ValueError(f"Unknown data type: {data_type}")

        # Build OData URL
        url = f"{self.sap_config.odata_service_path}{service}/{self._get_entity_set(data_type)}"

        params = {}
        if filters:
            filter_parts = [f"{k} eq '{v}'" for k, v in filters.items()]
            params["$filter"] = " and ".join(filter_parts)
        if limit:
            params["$top"] = str(limit)

        params["$format"] = "json"

        try:
            response = await self._session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            records = data.get("d", {}).get("results", data.get("value", []))

            return {
                "data_type": data_type,
                "records": records,
                "count": len(records),
                "fetched_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"SAP fetch failed for {data_type}: {e}")
            raise

    def _get_entity_set(self, data_type: str) -> str:
        """Get OData entity set name for a data type."""
        entity_sets = {
            "equipment": "A_Equipment",
            "maintenance_orders": "A_MaintenanceOrder",
            "production_orders": "A_ProductionOrder_2",
            "materials": "A_Product",
            "plants": "A_Plant",
        }
        return entity_sets.get(data_type, data_type)

    async def push_data(
        self,
        data_type: str,
        data: Dict[str, Any]
    ) -> SyncResult:
        """Push data to SAP."""
        sync_id = f"SAP-PUSH-{uuid.uuid4().hex[:8].upper()}"
        started_at = datetime.utcnow()

        result = SyncResult(
            sync_id=sync_id,
            connector_type=ConnectorType.SAP,
            started_at=started_at,
            status="in_progress"
        )

        try:
            if not self.is_connected:
                await self.connect()

            records = data.get("records", [])
            result.records_processed = len(records)

            service = self.sap_config.odata_services.get(data_type)
            if not service:
                raise ValueError(f"Unknown data type: {data_type}")

            url = f"{self.sap_config.odata_service_path}{service}/{self._get_entity_set(data_type)}"

            for record in records:
                try:
                    response = await self._session.post(url, json=record)
                    if response.status_code in [200, 201, 204]:
                        result.records_success += 1
                    else:
                        result.records_failed += 1
                        result.errors.append(f"HTTP {response.status_code}: {response.text[:200]}")
                except Exception as e:
                    result.records_failed += 1
                    result.errors.append(str(e))

            result.status = "success" if result.records_failed == 0 else "partial"

        except Exception as e:
            logger.error(f"SAP push failed: {e}")
            result.status = "failed"
            result.errors.append(str(e))

        result.completed_at = datetime.utcnow()
        result.duration_ms = (result.completed_at - started_at).total_seconds() * 1000

        return result

    async def fetch_equipment(
        self,
        plant: Optional[str] = None,
        equipment_type: Optional[str] = None,
        limit: int = 1000
    ) -> ERPData:
        """Fetch equipment master data."""
        filters = {}
        if plant:
            filters["Plant"] = plant
        if equipment_type:
            filters["EquipmentType"] = equipment_type

        data = await self.fetch_data("equipment", filters, limit)

        return ERPData(
            equipment=data["records"],
            source_system=f"SAP:{self.sap_config.system_id}",
            extracted_at=datetime.utcnow(),
            record_count=data["count"]
        )

    async def fetch_maintenance_orders(
        self,
        plant: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 1000
    ) -> ERPData:
        """Fetch maintenance orders."""
        filters = {}
        if plant:
            filters["MaintenancePlanningPlant"] = plant
        if status:
            filters["MaintenanceOrderType"] = status

        data = await self.fetch_data("maintenance_orders", filters, limit)

        return ERPData(
            work_orders=data["records"],
            source_system=f"SAP:{self.sap_config.system_id}",
            extracted_at=datetime.utcnow(),
            record_count=data["count"]
        )

    async def create_maintenance_notification(
        self,
        equipment_id: str,
        notification_type: str,
        description: str,
        priority: str = "3"
    ) -> Dict[str, Any]:
        """Create a maintenance notification in SAP."""
        notification_data = {
            "Equipment": equipment_id,
            "NotificationType": notification_type,
            "NotificationText": description,
            "Priority": priority,
            "ReportedByUser": self.config.username,
        }

        result = await self.push_data("maintenance_notifications", {"records": [notification_data]})

        return {
            "success": result.status == "success",
            "sync_result": result,
        }

    def _get_supported_data_types(self) -> List[str]:
        """Get supported SAP data types."""
        return list(self.sap_config.odata_services.keys())
