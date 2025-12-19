"""
KEPWARE Connector - Integration with Kepware KEPServerEX
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
    HistorianData,
    KEPWARE_STANDARD_MAPPINGS,
)

logger = logging.getLogger(__name__)


class KEPWAREConfig(ConnectorConfig):
    """KEPWARE-specific configuration."""
    connector_type: ConnectorType = ConnectorType.KEPWARE

    # Default port for Kepware Configuration API
    port: int = 57412

    # Kepware specific settings
    project_name: str = ""
    channel_filter: Optional[str] = None   # Filter by channel name
    device_filter: Optional[str] = None    # Filter by device name

    # IoT Gateway settings
    use_iot_gateway: bool = False
    iot_gateway_port: int = 8080
    mqtt_broker: Optional[str] = None

    # REST API settings
    api_version: str = "v1"

    # Subscription settings
    enable_subscriptions: bool = True
    subscription_rate_ms: int = 1000       # Polling rate in milliseconds
    dead_band: float = 0.0                 # Dead band for value changes

    # Tag groups to sync
    tag_groups: List[str] = Field(default_factory=list)

    # OPC UA settings (alternative)
    use_opc_ua: bool = False
    opc_ua_endpoint: str = "opc.tcp://localhost:49320"


class KEPWAREConnector(BaseConnector):
    """
    KEPWARE KEPServerEX Connector.

    Supports:
    - REST Configuration API
    - IoT Gateway REST/MQTT
    - OPC UA endpoint
    - Real-time tag subscriptions
    - Tag browsing and discovery
    """

    def __init__(self, config: KEPWAREConfig):
        super().__init__(config)
        self.kepware_config = config
        self._session = None
        self._subscriptions: Dict[str, Any] = {}
        self._tag_cache: Dict[str, Any] = {}

    async def connect(self) -> bool:
        """Establish connection to Kepware."""
        self.status = ConnectionStatus.CONNECTING

        try:
            import httpx

            base_url = f"{'https' if self.config.use_ssl else 'http'}://{self.config.host}:{self.config.port}"

            self._session = httpx.AsyncClient(
                base_url=base_url,
                verify=self.config.verify_ssl,
                timeout=self.config.connection_timeout_seconds,
            )

            # Set authentication
            if self.config.username and self.config.password:
                self._session.auth = (self.config.username, self.config.password)

            # Test connection
            response = await self._session.get(f"/config/{self.kepware_config.api_version}/project")

            if response.status_code == 200:
                self.status = ConnectionStatus.CONNECTED
                logger.info(f"Connected to Kepware: {self.config.host}")

                # Cache tag list
                await self._refresh_tag_cache()

                return True
            else:
                self.status = ConnectionStatus.ERROR
                logger.error(f"Kepware connection failed: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Kepware connection failed: {e}")
            self.status = ConnectionStatus.ERROR
            return False

    async def disconnect(self) -> bool:
        """Close Kepware connection."""
        try:
            # Cancel all subscriptions
            for sub_id in list(self._subscriptions.keys()):
                await self._cancel_subscription(sub_id)

            if self._session:
                await self._session.aclose()
                self._session = None

            self.status = ConnectionStatus.DISCONNECTED
            logger.info(f"Disconnected from Kepware: {self.config.host}")
            return True

        except Exception as e:
            logger.error(f"Kepware disconnect failed: {e}")
            return False

    async def test_connection(self) -> Dict[str, Any]:
        """Test Kepware connection."""
        result = {
            "success": False,
            "host": self.config.host,
            "port": self.config.port,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {}
        }

        try:
            was_connected = self.is_connected

            if not was_connected:
                await self.connect()

            if self.is_connected:
                # Get project info
                info = await self._get_project_info()
                result["success"] = True
                result["details"] = info

            if not was_connected:
                await self.disconnect()

        except Exception as e:
            result["error"] = str(e)

        return result

    async def _get_project_info(self) -> Dict[str, Any]:
        """Get Kepware project information."""
        try:
            response = await self._session.get(f"/config/{self.kepware_config.api_version}/project")
            if response.status_code == 200:
                project = response.json()

                # Get channel count
                channels_response = await self._session.get(
                    f"/config/{self.kepware_config.api_version}/project/channels"
                )
                channels = channels_response.json() if channels_response.status_code == 200 else []

                return {
                    "project_name": project.get("PROJECT_NAME", ""),
                    "channel_count": len(channels),
                    "tag_count": len(self._tag_cache),
                    "api_version": self.kepware_config.api_version,
                }
        except Exception as e:
            logger.error(f"Failed to get project info: {e}")

        return {}

    async def _refresh_tag_cache(self) -> None:
        """Refresh the tag cache."""
        try:
            tags = await self._browse_all_tags()
            self._tag_cache = {tag["full_path"]: tag for tag in tags}
            logger.info(f"Cached {len(self._tag_cache)} tags from Kepware")
        except Exception as e:
            logger.error(f"Failed to refresh tag cache: {e}")

    async def _browse_all_tags(self) -> List[Dict[str, Any]]:
        """Browse all tags in the Kepware project."""
        all_tags = []

        try:
            # Get all channels
            channels_response = await self._session.get(
                f"/config/{self.kepware_config.api_version}/project/channels"
            )

            if channels_response.status_code != 200:
                return all_tags

            channels = channels_response.json()

            for channel in channels:
                channel_name = channel.get("common.ALLTYPES_NAME", "")

                # Apply channel filter
                if self.kepware_config.channel_filter:
                    if self.kepware_config.channel_filter not in channel_name:
                        continue

                # Get devices in channel
                devices_response = await self._session.get(
                    f"/config/{self.kepware_config.api_version}/project/channels/{channel_name}/devices"
                )

                if devices_response.status_code != 200:
                    continue

                devices = devices_response.json()

                for device in devices:
                    device_name = device.get("common.ALLTYPES_NAME", "")

                    # Apply device filter
                    if self.kepware_config.device_filter:
                        if self.kepware_config.device_filter not in device_name:
                            continue

                    # Get tags in device
                    tags_response = await self._session.get(
                        f"/config/{self.kepware_config.api_version}/project/channels/{channel_name}/devices/{device_name}/tags"
                    )

                    if tags_response.status_code == 200:
                        tags = tags_response.json()

                        for tag in tags:
                            tag_name = tag.get("common.ALLTYPES_NAME", "")
                            full_path = f"{channel_name}.{device_name}.{tag_name}"

                            all_tags.append({
                                "full_path": full_path,
                                "channel": channel_name,
                                "device": device_name,
                                "tag_name": tag_name,
                                "data_type": tag.get("servermain.TAG_DATA_TYPE", ""),
                                "description": tag.get("common.ALLTYPES_DESCRIPTION", ""),
                                "address": tag.get("servermain.TAG_ADDRESS", ""),
                            })

        except Exception as e:
            logger.error(f"Failed to browse tags: {e}")

        return all_tags

    async def fetch_data(
        self,
        data_type: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch data from Kepware.

        Args:
            data_type: tags, channels, devices, or tag_values
            filters: Optional filters (channel, device, tag patterns)
            limit: Maximum records
        """
        if not self.is_connected:
            await self.connect()

        if data_type == "tags":
            return await self._fetch_tags(filters, limit)
        elif data_type == "tag_values":
            return await self._fetch_tag_values(filters, limit)
        elif data_type == "channels":
            return await self._fetch_channels(filters, limit)
        elif data_type == "devices":
            return await self._fetch_devices(filters, limit)
        else:
            raise ValueError(f"Unknown data type: {data_type}")

    async def _fetch_tags(
        self,
        filters: Optional[Dict[str, Any]],
        limit: Optional[int]
    ) -> Dict[str, Any]:
        """Fetch tag definitions."""
        tags = list(self._tag_cache.values())

        if filters:
            if "channel" in filters:
                tags = [t for t in tags if filters["channel"] in t["channel"]]
            if "device" in filters:
                tags = [t for t in tags if filters["device"] in t["device"]]
            if "pattern" in filters:
                import fnmatch
                tags = [t for t in tags if fnmatch.fnmatch(t["full_path"], filters["pattern"])]

        if limit:
            tags = tags[:limit]

        return {
            "data_type": "tags",
            "records": tags,
            "count": len(tags),
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def _fetch_tag_values(
        self,
        filters: Optional[Dict[str, Any]],
        limit: Optional[int]
    ) -> Dict[str, Any]:
        """Fetch current tag values via IoT Gateway."""
        tag_values = []

        # Get tags to read
        tags_data = await self._fetch_tags(filters, limit)
        tags = tags_data["records"]

        if self.kepware_config.use_iot_gateway:
            # Use IoT Gateway REST API
            for tag in tags:
                try:
                    value = await self._read_tag_iot_gateway(tag["full_path"])
                    tag_values.append({
                        "tag_id": tag["full_path"],
                        "value": value.get("value"),
                        "quality": value.get("quality", "Good"),
                        "timestamp": value.get("timestamp", datetime.utcnow().isoformat()),
                    })
                except Exception as e:
                    logger.warning(f"Failed to read tag {tag['full_path']}: {e}")
        else:
            # Use Configuration API (limited value reading)
            logger.warning("IoT Gateway not enabled - tag values may not be available")

        return {
            "data_type": "tag_values",
            "records": tag_values,
            "count": len(tag_values),
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def _read_tag_iot_gateway(self, tag_path: str) -> Dict[str, Any]:
        """Read a tag value via IoT Gateway REST API."""
        import httpx

        iot_url = f"{'https' if self.config.use_ssl else 'http'}://{self.config.host}:{self.kepware_config.iot_gateway_port}"

        async with httpx.AsyncClient(verify=self.config.verify_ssl) as client:
            response = await client.get(
                f"{iot_url}/iotgateway/read",
                params={"ids": tag_path}
            )

            if response.status_code == 200:
                data = response.json()
                if data and "readResults" in data:
                    result = data["readResults"][0]
                    return {
                        "value": result.get("v"),
                        "quality": "Good" if result.get("s") else "Bad",
                        "timestamp": result.get("t"),
                    }

        return {}

    async def _fetch_channels(
        self,
        filters: Optional[Dict[str, Any]],
        limit: Optional[int]
    ) -> Dict[str, Any]:
        """Fetch channel configurations."""
        response = await self._session.get(
            f"/config/{self.kepware_config.api_version}/project/channels"
        )

        channels = response.json() if response.status_code == 200 else []

        if limit:
            channels = channels[:limit]

        return {
            "data_type": "channels",
            "records": channels,
            "count": len(channels),
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def _fetch_devices(
        self,
        filters: Optional[Dict[str, Any]],
        limit: Optional[int]
    ) -> Dict[str, Any]:
        """Fetch device configurations."""
        all_devices = []

        channels_data = await self._fetch_channels(None, None)

        for channel in channels_data["records"]:
            channel_name = channel.get("common.ALLTYPES_NAME", "")

            response = await self._session.get(
                f"/config/{self.kepware_config.api_version}/project/channels/{channel_name}/devices"
            )

            if response.status_code == 200:
                devices = response.json()
                for device in devices:
                    device["_channel"] = channel_name
                all_devices.extend(devices)

        if limit:
            all_devices = all_devices[:limit]

        return {
            "data_type": "devices",
            "records": all_devices,
            "count": len(all_devices),
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def push_data(
        self,
        data_type: str,
        data: Dict[str, Any]
    ) -> SyncResult:
        """Push data to Kepware (write tag values)."""
        sync_id = f"KEP-PUSH-{uuid.uuid4().hex[:8].upper()}"
        started_at = datetime.utcnow()

        result = SyncResult(
            sync_id=sync_id,
            connector_type=ConnectorType.KEPWARE,
            started_at=started_at,
            status="in_progress"
        )

        try:
            if not self.is_connected:
                await self.connect()

            records = data.get("records", [])
            result.records_processed = len(records)

            if data_type == "tag_values":
                for record in records:
                    try:
                        success = await self._write_tag_value(
                            record["tag_id"],
                            record["value"]
                        )
                        if success:
                            result.records_success += 1
                        else:
                            result.records_failed += 1
                    except Exception as e:
                        result.records_failed += 1
                        result.errors.append(str(e))

            result.status = "success" if result.records_failed == 0 else "partial"

        except Exception as e:
            logger.error(f"Kepware push failed: {e}")
            result.status = "failed"
            result.errors.append(str(e))

        result.completed_at = datetime.utcnow()
        result.duration_ms = (result.completed_at - started_at).total_seconds() * 1000

        return result

    async def _write_tag_value(self, tag_path: str, value: Any) -> bool:
        """Write a tag value via IoT Gateway."""
        if not self.kepware_config.use_iot_gateway:
            logger.warning("IoT Gateway not enabled - cannot write tag values")
            return False

        import httpx

        iot_url = f"{'https' if self.config.use_ssl else 'http'}://{self.config.host}:{self.kepware_config.iot_gateway_port}"

        async with httpx.AsyncClient(verify=self.config.verify_ssl) as client:
            response = await client.post(
                f"{iot_url}/iotgateway/write",
                json=[{"id": tag_path, "v": value}]
            )

            return response.status_code == 200

    async def subscribe_tags(
        self,
        tag_patterns: List[str],
        callback: Any,
        rate_ms: int = 1000
    ) -> str:
        """
        Subscribe to tag value changes.

        Args:
            tag_patterns: List of tag patterns to subscribe to
            callback: Async callback function for value changes
            rate_ms: Subscription rate in milliseconds

        Returns:
            Subscription ID
        """
        sub_id = f"SUB-{uuid.uuid4().hex[:8].upper()}"

        self._subscriptions[sub_id] = {
            "patterns": tag_patterns,
            "callback": callback,
            "rate_ms": rate_ms,
            "active": True,
        }

        logger.info(f"Created subscription {sub_id} for {len(tag_patterns)} patterns")
        return sub_id

    async def _cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a tag subscription."""
        if subscription_id in self._subscriptions:
            self._subscriptions[subscription_id]["active"] = False
            del self._subscriptions[subscription_id]
            return True
        return False

    def _get_supported_data_types(self) -> List[str]:
        """Get supported Kepware data types."""
        return ["tags", "tag_values", "channels", "devices"]

    async def get_historian_data(
        self,
        tag_paths: List[str],
        start_time: datetime,
        end_time: datetime,
        aggregate: str = "raw"
    ) -> HistorianData:
        """
        Fetch historical data from Kepware Local Historian.

        Args:
            tag_paths: Tags to retrieve
            start_time: Start of time range
            end_time: End of time range
            aggregate: raw, average, min, max, count
        """
        # This requires Kepware Local Historian add-on
        logger.warning("Local Historian data retrieval - requires Historian add-on")

        return HistorianData(
            tag_values=[],
            start_time=start_time,
            end_time=end_time,
            source_system=f"Kepware:{self.config.host}",
            extracted_at=datetime.utcnow(),
        )
