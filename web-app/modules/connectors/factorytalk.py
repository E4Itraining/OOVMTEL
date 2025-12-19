"""
FactoryTalk Connector - Integration with Rockwell Automation FactoryTalk
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
    MESData,
    HistorianData,
    FACTORYTALK_STANDARD_MAPPINGS,
)

logger = logging.getLogger(__name__)


class FactoryTalkConfig(ConnectorConfig):
    """FactoryTalk-specific configuration."""
    connector_type: ConnectorType = ConnectorType.FACTORYTALK

    # FactoryTalk component type
    component: str = "historian"  # historian, optix, metrics, alarms

    # Default port
    port: int = 443

    # FactoryTalk Historian settings
    historian_server: str = ""
    historian_port: int = 3014
    max_points_per_query: int = 100000

    # FactoryTalk Optix settings
    optix_project: str = ""

    # FactoryTalk Metrics & Scoreboard settings
    metrics_url: str = ""

    # REST API settings
    api_base_path: str = "/ftapi"

    # Tag retrieval settings
    tag_filter: Optional[str] = None
    area_filter: Optional[str] = None

    # Subscription settings
    enable_live_data: bool = True
    live_data_rate_ms: int = 1000

    # VantagePoint settings (for analytics)
    vantagepoint_enabled: bool = False
    vantagepoint_server: str = ""


class FactoryTalkConnector(BaseConnector):
    """
    FactoryTalk Connector for Rockwell Automation systems.

    Supports:
    - FactoryTalk Historian (time-series data)
    - FactoryTalk Optix (HMI/SCADA)
    - FactoryTalk Metrics & Scoreboard (OEE/KPIs)
    - FactoryTalk Alarms & Events
    - VantagePoint (analytics)
    """

    def __init__(self, config: FactoryTalkConfig):
        super().__init__(config)
        self.ft_config = config
        self._session = None
        self._tag_cache: Dict[str, Any] = {}

    async def connect(self) -> bool:
        """Establish connection to FactoryTalk."""
        self.status = ConnectionStatus.CONNECTING

        try:
            import httpx

            base_url = f"https://{self.config.host}:{self.config.port}"

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

            # Test connection based on component
            if self.ft_config.component == "historian":
                success = await self._test_historian_connection()
            elif self.ft_config.component == "metrics":
                success = await self._test_metrics_connection()
            else:
                success = await self._test_api_connection()

            if success:
                self.status = ConnectionStatus.CONNECTED
                logger.info(f"Connected to FactoryTalk {self.ft_config.component}: {self.config.host}")
                return True
            else:
                self.status = ConnectionStatus.ERROR
                return False

        except Exception as e:
            logger.error(f"FactoryTalk connection failed: {e}")
            self.status = ConnectionStatus.ERROR
            return False

    async def _oauth2_authenticate(self) -> None:
        """Perform OAuth2 authentication with FactoryTalk Hub."""
        token_url = f"https://{self.config.host}/identity/connect/token"

        response = await self._session.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "scope": "factorytalk-api",
            }
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            self._session.headers["Authorization"] = f"Bearer {token}"

    async def _test_historian_connection(self) -> bool:
        """Test Historian connection."""
        try:
            response = await self._session.get(
                f"{self.ft_config.api_base_path}/historian/v1/servers"
            )
            return response.status_code in [200, 401]
        except Exception:
            return False

    async def _test_metrics_connection(self) -> bool:
        """Test Metrics & Scoreboard connection."""
        try:
            response = await self._session.get(
                f"{self.ft_config.api_base_path}/metrics/v1/health"
            )
            return response.status_code in [200, 401]
        except Exception:
            return False

    async def _test_api_connection(self) -> bool:
        """Test generic API connection."""
        try:
            response = await self._session.get(f"{self.ft_config.api_base_path}/health")
            return response.status_code in [200, 401]
        except Exception:
            return False

    async def disconnect(self) -> bool:
        """Close FactoryTalk connection."""
        try:
            if self._session:
                await self._session.aclose()
                self._session = None

            self.status = ConnectionStatus.DISCONNECTED
            logger.info(f"Disconnected from FactoryTalk: {self.config.host}")
            return True

        except Exception as e:
            logger.error(f"FactoryTalk disconnect failed: {e}")
            return False

    async def test_connection(self) -> Dict[str, Any]:
        """Test FactoryTalk connection."""
        result = {
            "success": False,
            "host": self.config.host,
            "component": self.ft_config.component,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {}
        }

        try:
            was_connected = self.is_connected

            if not was_connected:
                await self.connect()

            if self.is_connected:
                info = await self._get_system_info()
                result["success"] = True
                result["details"] = info

            if not was_connected:
                await self.disconnect()

        except Exception as e:
            result["error"] = str(e)

        return result

    async def _get_system_info(self) -> Dict[str, Any]:
        """Get FactoryTalk system information."""
        info = {
            "component": self.ft_config.component,
            "host": self.config.host,
        }

        if self.ft_config.component == "historian":
            try:
                response = await self._session.get(
                    f"{self.ft_config.api_base_path}/historian/v1/servers"
                )
                if response.status_code == 200:
                    servers = response.json()
                    info["historian_servers"] = len(servers)
            except Exception:
                pass

        return info

    async def fetch_data(
        self,
        data_type: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch data from FactoryTalk.

        Args:
            data_type: tags, tag_values, historical, oee, alarms, production
            filters: Optional filters
            limit: Maximum records
        """
        if not self.is_connected:
            await self.connect()

        if data_type == "tags":
            return await self._fetch_tags(filters, limit)
        elif data_type == "tag_values":
            return await self._fetch_tag_values(filters, limit)
        elif data_type == "historical":
            return await self._fetch_historical(filters, limit)
        elif data_type == "oee":
            return await self._fetch_oee(filters, limit)
        elif data_type == "alarms":
            return await self._fetch_alarms(filters, limit)
        elif data_type == "production":
            return await self._fetch_production(filters, limit)
        else:
            raise ValueError(f"Unknown data type: {data_type}")

    async def _fetch_tags(
        self,
        filters: Optional[Dict[str, Any]],
        limit: Optional[int]
    ) -> Dict[str, Any]:
        """Fetch tag definitions from Historian."""
        params = {}

        if filters:
            if "pattern" in filters:
                params["nameFilter"] = filters["pattern"]
            if "area" in filters:
                params["areaFilter"] = filters["area"]

        if limit:
            params["maxCount"] = str(limit)

        try:
            response = await self._session.get(
                f"{self.ft_config.api_base_path}/historian/v1/tags",
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                tags = data.get("tags", [])

                # Cache tags
                for tag in tags:
                    self._tag_cache[tag.get("name", "")] = tag

                return {
                    "data_type": "tags",
                    "records": tags,
                    "count": len(tags),
                    "fetched_at": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Failed to fetch tags: {e}")

        return {"data_type": "tags", "records": [], "count": 0}

    async def _fetch_tag_values(
        self,
        filters: Optional[Dict[str, Any]],
        limit: Optional[int]
    ) -> Dict[str, Any]:
        """Fetch current tag values."""
        tag_names = filters.get("tags", []) if filters else list(self._tag_cache.keys())

        if limit:
            tag_names = tag_names[:limit]

        values = []

        try:
            # Batch request for current values
            response = await self._session.post(
                f"{self.ft_config.api_base_path}/historian/v1/tags/current",
                json={"tagNames": tag_names}
            )

            if response.status_code == 200:
                data = response.json()
                values = data.get("values", [])
        except Exception as e:
            logger.error(f"Failed to fetch tag values: {e}")

        return {
            "data_type": "tag_values",
            "records": values,
            "count": len(values),
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def _fetch_historical(
        self,
        filters: Optional[Dict[str, Any]],
        limit: Optional[int]
    ) -> Dict[str, Any]:
        """Fetch historical data from Historian."""
        if not filters:
            filters = {}

        tag_names = filters.get("tags", list(self._tag_cache.keys())[:10])
        start_time = filters.get("start_time", datetime.utcnow().isoformat())
        end_time = filters.get("end_time", datetime.utcnow().isoformat())
        resolution = filters.get("resolution", "raw")  # raw, 1min, 5min, 1hour

        try:
            response = await self._session.post(
                f"{self.ft_config.api_base_path}/historian/v1/tags/history",
                json={
                    "tagNames": tag_names,
                    "startTime": start_time,
                    "endTime": end_time,
                    "resolution": resolution,
                    "maxPoints": limit or self.ft_config.max_points_per_query,
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "data_type": "historical",
                    "records": data.get("series", []),
                    "count": len(data.get("series", [])),
                    "fetched_at": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")

        return {"data_type": "historical", "records": [], "count": 0}

    async def _fetch_oee(
        self,
        filters: Optional[Dict[str, Any]],
        limit: Optional[int]
    ) -> Dict[str, Any]:
        """Fetch OEE data from Metrics & Scoreboard."""
        if self.ft_config.component != "metrics":
            logger.warning("OEE data requires Metrics & Scoreboard component")
            return {"data_type": "oee", "records": [], "count": 0}

        params = {}
        if filters:
            if "line" in filters:
                params["lineId"] = filters["line"]
            if "shift" in filters:
                params["shiftId"] = filters["shift"]
            if "start_time" in filters:
                params["startTime"] = filters["start_time"]
            if "end_time" in filters:
                params["endTime"] = filters["end_time"]

        try:
            response = await self._session.get(
                f"{self.ft_config.api_base_path}/metrics/v1/oee",
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "data_type": "oee",
                    "records": data.get("oeeData", []),
                    "count": len(data.get("oeeData", [])),
                    "fetched_at": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Failed to fetch OEE data: {e}")

        return {"data_type": "oee", "records": [], "count": 0}

    async def _fetch_alarms(
        self,
        filters: Optional[Dict[str, Any]],
        limit: Optional[int]
    ) -> Dict[str, Any]:
        """Fetch alarms from FactoryTalk Alarms & Events."""
        params = {"maxCount": str(limit or 1000)}

        if filters:
            if "severity" in filters:
                params["severity"] = filters["severity"]
            if "state" in filters:
                params["state"] = filters["state"]  # active, acknowledged, cleared
            if "start_time" in filters:
                params["startTime"] = filters["start_time"]

        try:
            response = await self._session.get(
                f"{self.ft_config.api_base_path}/alarms/v1/events",
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "data_type": "alarms",
                    "records": data.get("alarms", []),
                    "count": len(data.get("alarms", [])),
                    "fetched_at": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Failed to fetch alarms: {e}")

        return {"data_type": "alarms", "records": [], "count": 0}

    async def _fetch_production(
        self,
        filters: Optional[Dict[str, Any]],
        limit: Optional[int]
    ) -> Dict[str, Any]:
        """Fetch production data from Metrics & Scoreboard."""
        params = {}
        if filters:
            if "line" in filters:
                params["lineId"] = filters["line"]
            if "product" in filters:
                params["productId"] = filters["product"]

        if limit:
            params["maxCount"] = str(limit)

        try:
            response = await self._session.get(
                f"{self.ft_config.api_base_path}/metrics/v1/production",
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "data_type": "production",
                    "records": data.get("productionData", []),
                    "count": len(data.get("productionData", [])),
                    "fetched_at": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Failed to fetch production data: {e}")

        return {"data_type": "production", "records": [], "count": 0}

    async def push_data(
        self,
        data_type: str,
        data: Dict[str, Any]
    ) -> SyncResult:
        """Push data to FactoryTalk."""
        sync_id = f"FT-PUSH-{uuid.uuid4().hex[:8].upper()}"
        started_at = datetime.utcnow()

        result = SyncResult(
            sync_id=sync_id,
            connector_type=ConnectorType.FACTORYTALK,
            started_at=started_at,
            status="in_progress"
        )

        try:
            if not self.is_connected:
                await self.connect()

            records = data.get("records", [])
            result.records_processed = len(records)

            if data_type == "tag_values":
                # Write tag values
                response = await self._session.post(
                    f"{self.ft_config.api_base_path}/historian/v1/tags/write",
                    json={"values": records}
                )

                if response.status_code == 200:
                    result.records_success = len(records)
                else:
                    result.records_failed = len(records)
                    result.errors.append(f"HTTP {response.status_code}")

            elif data_type == "production":
                # Write production data
                response = await self._session.post(
                    f"{self.ft_config.api_base_path}/metrics/v1/production",
                    json={"productionData": records}
                )

                if response.status_code in [200, 201]:
                    result.records_success = len(records)
                else:
                    result.records_failed = len(records)
                    result.errors.append(f"HTTP {response.status_code}")

            result.status = "success" if result.records_failed == 0 else "partial"

        except Exception as e:
            logger.error(f"FactoryTalk push failed: {e}")
            result.status = "failed"
            result.errors.append(str(e))

        result.completed_at = datetime.utcnow()
        result.duration_ms = (result.completed_at - started_at).total_seconds() * 1000

        return result

    async def get_historian_data(
        self,
        tag_names: List[str],
        start_time: datetime,
        end_time: datetime,
        resolution: str = "raw"
    ) -> HistorianData:
        """
        Fetch historical data from FactoryTalk Historian.

        Args:
            tag_names: Tags to retrieve
            start_time: Start of time range
            end_time: End of time range
            resolution: raw, 1min, 5min, 1hour, 1day
        """
        data = await self._fetch_historical({
            "tags": tag_names,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "resolution": resolution,
        }, None)

        return HistorianData(
            tag_values=data["records"],
            start_time=start_time,
            end_time=end_time,
            source_system=f"FactoryTalk:{self.config.host}",
            extracted_at=datetime.utcnow(),
            record_count=data["count"]
        )

    async def get_oee_data(
        self,
        line_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> MESData:
        """Fetch OEE data from FactoryTalk Metrics."""
        filters = {}
        if line_id:
            filters["line"] = line_id
        if start_time:
            filters["start_time"] = start_time.isoformat()
        if end_time:
            filters["end_time"] = end_time.isoformat()

        data = await self._fetch_oee(filters, None)

        return MESData(
            oee_data=data["records"],
            source_system=f"FactoryTalk:{self.config.host}",
            extracted_at=datetime.utcnow(),
            record_count=data["count"]
        )

    def _get_supported_data_types(self) -> List[str]:
        """Get supported FactoryTalk data types."""
        return ["tags", "tag_values", "historical", "oee", "alarms", "production"]
