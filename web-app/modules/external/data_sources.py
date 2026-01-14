"""
External Data Sources for OOVMTEL
Weather, ERP, CMMS, and Energy integrations
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


class DataSourceType(str, Enum):
    """Types of external data sources."""
    WEATHER = "weather"
    ERP = "erp"
    CMMS = "cmms"
    ENERGY = "energy"
    MES = "mes"
    CUSTOM = "custom"


class DataSourceStatus(str, Enum):
    """Status of data source connection."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class DataSourceConfig:
    """Configuration for an external data source."""
    type: DataSourceType
    name: str
    url: str
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    poll_interval_seconds: int = 60
    enabled: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class DataSourceResult:
    """Result from external data source query."""
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    status: DataSourceStatus
    error: Optional[str] = None
    latency_ms: float = 0


class BaseDataSource(ABC):
    """Base class for external data sources."""

    def __init__(self, config: DataSourceConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
        self._status = DataSourceStatus.UNKNOWN
        self._last_fetch: Optional[datetime] = None
        self._cached_data: Optional[Dict[str, Any]] = None

    async def initialize(self):
        """Initialize the data source connection."""
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the data source connection."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    async def fetch_data(self) -> DataSourceResult:
        """Fetch data from the external source."""
        pass

    async def get_cached_or_fetch(self) -> DataSourceResult:
        """Get cached data or fetch if expired."""
        now = datetime.utcnow()
        if (
            self._cached_data
            and self._last_fetch
            and (now - self._last_fetch).seconds < self.config.poll_interval_seconds
        ):
            return DataSourceResult(
                source=self.config.name,
                timestamp=self._last_fetch,
                data=self._cached_data,
                status=self._status
            )

        result = await self.fetch_data()
        if result.status == DataSourceStatus.CONNECTED:
            self._cached_data = result.data
            self._last_fetch = result.timestamp
            self._status = DataSourceStatus.CONNECTED
        return result


class WeatherProvider(BaseDataSource):
    """
    Weather data provider.
    Supports OpenWeatherMap and similar APIs.
    """

    def __init__(self, config: Optional[DataSourceConfig] = None):
        if config is None:
            config = DataSourceConfig(
                type=DataSourceType.WEATHER,
                name="OpenWeatherMap",
                url=os.getenv("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5"),
                api_key=os.getenv("WEATHER_API_KEY", "demo-key"),
                poll_interval_seconds=300  # 5 minutes
            )
        super().__init__(config)
        self.location = os.getenv("WEATHER_LOCATION", "48.8566,2.3522")  # Paris default

    async def fetch_data(self) -> DataSourceResult:
        """Fetch weather data."""
        start_time = datetime.utcnow()

        try:
            if not self._client:
                await self.initialize()

            # Demo mode - return simulated weather data
            if self.config.api_key == "demo-key":
                import random
                data = self._generate_demo_weather()
            else:
                lat, lon = self.location.split(",")
                response = await self._client.get(
                    f"{self.config.url}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.config.api_key,
                        "units": "metric"
                    }
                )
                response.raise_for_status()
                data = self._parse_weather_response(response.json())

            latency = (datetime.utcnow() - start_time).total_seconds() * 1000

            return DataSourceResult(
                source=self.config.name,
                timestamp=datetime.utcnow(),
                data=data,
                status=DataSourceStatus.CONNECTED,
                latency_ms=latency
            )

        except Exception as e:
            logger.error(f"Weather fetch error: {e}")
            return DataSourceResult(
                source=self.config.name,
                timestamp=datetime.utcnow(),
                data={},
                status=DataSourceStatus.ERROR,
                error=str(e)
            )

    def _generate_demo_weather(self) -> Dict[str, Any]:
        """Generate demo weather data."""
        import random
        return {
            "temperature": round(random.uniform(15, 30), 1),
            "humidity": random.randint(40, 80),
            "pressure": random.randint(1010, 1025),
            "wind_speed": round(random.uniform(0, 20), 1),
            "wind_direction": random.randint(0, 360),
            "conditions": random.choice(["Clear", "Cloudy", "Partly Cloudy", "Rain"]),
            "visibility": random.randint(5, 10),
            "uv_index": random.randint(1, 10),
            "location": "Paris, France",
            "demo_mode": True
        }

    def _parse_weather_response(self, response: dict) -> Dict[str, Any]:
        """Parse OpenWeatherMap response."""
        return {
            "temperature": response.get("main", {}).get("temp"),
            "humidity": response.get("main", {}).get("humidity"),
            "pressure": response.get("main", {}).get("pressure"),
            "wind_speed": response.get("wind", {}).get("speed"),
            "wind_direction": response.get("wind", {}).get("deg"),
            "conditions": response.get("weather", [{}])[0].get("description"),
            "visibility": response.get("visibility", 0) / 1000,
            "location": response.get("name"),
            "demo_mode": False
        }


class ERPConnector(BaseDataSource):
    """
    ERP system connector.
    Supports SAP, Oracle, and custom ERP APIs.
    """

    def __init__(self, config: Optional[DataSourceConfig] = None):
        if config is None:
            config = DataSourceConfig(
                type=DataSourceType.ERP,
                name="ERP System",
                url=os.getenv("ERP_API_URL", "http://erp-api:8080"),
                api_key=os.getenv("ERP_API_KEY"),
                poll_interval_seconds=60
            )
        super().__init__(config)

    async def fetch_data(self) -> DataSourceResult:
        """Fetch ERP data (production orders, inventory, etc.)."""
        start_time = datetime.utcnow()

        try:
            # Demo mode - return simulated ERP data
            data = self._generate_demo_erp_data()
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000

            return DataSourceResult(
                source=self.config.name,
                timestamp=datetime.utcnow(),
                data=data,
                status=DataSourceStatus.CONNECTED,
                latency_ms=latency
            )

        except Exception as e:
            logger.error(f"ERP fetch error: {e}")
            return DataSourceResult(
                source=self.config.name,
                timestamp=datetime.utcnow(),
                data={},
                status=DataSourceStatus.ERROR,
                error=str(e)
            )

    def _generate_demo_erp_data(self) -> Dict[str, Any]:
        """Generate demo ERP data."""
        import random
        return {
            "production_orders": [
                {
                    "id": f"PO-{random.randint(10000, 99999)}",
                    "product": random.choice(["Product A", "Product B", "Product C"]),
                    "quantity": random.randint(100, 1000),
                    "status": random.choice(["planned", "in_progress", "completed"]),
                    "due_date": (datetime.utcnow() + timedelta(days=random.randint(1, 14))).isoformat()
                }
                for _ in range(5)
            ],
            "inventory": {
                "raw_materials": random.randint(5000, 10000),
                "work_in_progress": random.randint(1000, 3000),
                "finished_goods": random.randint(2000, 5000)
            },
            "kpis": {
                "on_time_delivery": round(random.uniform(92, 99), 1),
                "inventory_turnover": round(random.uniform(8, 15), 1),
                "order_fulfillment_rate": round(random.uniform(95, 100), 1)
            },
            "demo_mode": True
        }


class CMMSConnector(BaseDataSource):
    """
    CMMS (Computerized Maintenance Management System) connector.
    """

    def __init__(self, config: Optional[DataSourceConfig] = None):
        if config is None:
            config = DataSourceConfig(
                type=DataSourceType.CMMS,
                name="CMMS System",
                url=os.getenv("CMMS_API_URL", "http://cmms-api:8080"),
                api_key=os.getenv("CMMS_API_KEY"),
                poll_interval_seconds=120
            )
        super().__init__(config)

    async def fetch_data(self) -> DataSourceResult:
        """Fetch CMMS data (work orders, maintenance history)."""
        start_time = datetime.utcnow()

        try:
            data = self._generate_demo_cmms_data()
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000

            return DataSourceResult(
                source=self.config.name,
                timestamp=datetime.utcnow(),
                data=data,
                status=DataSourceStatus.CONNECTED,
                latency_ms=latency
            )

        except Exception as e:
            logger.error(f"CMMS fetch error: {e}")
            return DataSourceResult(
                source=self.config.name,
                timestamp=datetime.utcnow(),
                data={},
                status=DataSourceStatus.ERROR,
                error=str(e)
            )

    def _generate_demo_cmms_data(self) -> Dict[str, Any]:
        """Generate demo CMMS data."""
        import random
        equipment = ["Reactor-001", "Mixer-002", "Pump-003", "Furnace-004", "Conveyor-005"]

        return {
            "work_orders": [
                {
                    "id": f"WO-{random.randint(10000, 99999)}",
                    "equipment": random.choice(equipment),
                    "type": random.choice(["preventive", "corrective", "inspection"]),
                    "priority": random.choice(["low", "medium", "high", "critical"]),
                    "status": random.choice(["open", "in_progress", "completed"]),
                    "scheduled_date": (datetime.utcnow() + timedelta(days=random.randint(-7, 14))).isoformat()
                }
                for _ in range(8)
            ],
            "maintenance_history": [
                {
                    "equipment": eq,
                    "last_maintenance": (datetime.utcnow() - timedelta(days=random.randint(10, 90))).isoformat(),
                    "maintenance_count_year": random.randint(2, 12),
                    "mtbf_hours": random.randint(500, 2000),
                    "mttr_hours": round(random.uniform(1, 8), 1)
                }
                for eq in equipment
            ],
            "spare_parts": {
                "total_items": random.randint(500, 1000),
                "low_stock_items": random.randint(5, 20),
                "pending_orders": random.randint(3, 10)
            },
            "demo_mode": True
        }


class EnergyMeterConnector(BaseDataSource):
    """
    Energy meter data connector.
    """

    def __init__(self, config: Optional[DataSourceConfig] = None):
        if config is None:
            config = DataSourceConfig(
                type=DataSourceType.ENERGY,
                name="Energy Meters",
                url=os.getenv("ENERGY_API_URL", "http://energy-gateway:8080"),
                poll_interval_seconds=30
            )
        super().__init__(config)

    async def fetch_data(self) -> DataSourceResult:
        """Fetch energy consumption data."""
        start_time = datetime.utcnow()

        try:
            data = self._generate_demo_energy_data()
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000

            return DataSourceResult(
                source=self.config.name,
                timestamp=datetime.utcnow(),
                data=data,
                status=DataSourceStatus.CONNECTED,
                latency_ms=latency
            )

        except Exception as e:
            logger.error(f"Energy fetch error: {e}")
            return DataSourceResult(
                source=self.config.name,
                timestamp=datetime.utcnow(),
                data={},
                status=DataSourceStatus.ERROR,
                error=str(e)
            )

    def _generate_demo_energy_data(self) -> Dict[str, Any]:
        """Generate demo energy data."""
        import random
        return {
            "total_power_kw": round(random.uniform(800, 1200), 1),
            "power_factor": round(random.uniform(0.85, 0.98), 2),
            "voltage_v": round(random.uniform(395, 405), 1),
            "current_a": round(random.uniform(1500, 2000), 1),
            "energy_today_kwh": random.randint(15000, 25000),
            "energy_month_kwh": random.randint(400000, 600000),
            "peak_demand_kw": round(random.uniform(1100, 1400), 1),
            "by_zone": {
                "Production Line A": round(random.uniform(200, 400), 1),
                "Production Line B": round(random.uniform(150, 300), 1),
                "HVAC": round(random.uniform(100, 200), 1),
                "Lighting": round(random.uniform(50, 100), 1),
                "Utilities": round(random.uniform(100, 200), 1)
            },
            "cost_estimate_today": round(random.uniform(2000, 4000), 2),
            "demo_mode": True
        }


class ExternalDataManager:
    """
    Manager for all external data sources.
    """

    def __init__(self):
        self.sources: Dict[str, BaseDataSource] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize all data sources."""
        if self._initialized:
            return

        # Initialize default sources
        self.sources["weather"] = WeatherProvider()
        self.sources["erp"] = ERPConnector()
        self.sources["cmms"] = CMMSConnector()
        self.sources["energy"] = EnergyMeterConnector()

        for source in self.sources.values():
            await source.initialize()

        self._initialized = True
        logger.info(f"Initialized {len(self.sources)} external data sources")

    async def close(self):
        """Close all data source connections."""
        for source in self.sources.values():
            await source.close()
        self._initialized = False

    def add_source(self, name: str, source: BaseDataSource):
        """Add a custom data source."""
        self.sources[name] = source

    async def fetch_all(self) -> Dict[str, DataSourceResult]:
        """Fetch data from all sources concurrently."""
        if not self._initialized:
            await self.initialize()

        tasks = {
            name: source.get_cached_or_fetch()
            for name, source in self.sources.items()
            if source.config.enabled
        }

        results = {}
        for name, task in tasks.items():
            results[name] = await task

        return results

    async def fetch_source(self, source_name: str) -> Optional[DataSourceResult]:
        """Fetch data from a specific source."""
        if source_name not in self.sources:
            return None
        return await self.sources[source_name].get_cached_or_fetch()

    def get_source_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all data sources."""
        return {
            name: {
                "type": source.config.type.value,
                "status": source._status.value,
                "enabled": source.config.enabled,
                "last_fetch": source._last_fetch.isoformat() if source._last_fetch else None,
                "poll_interval": source.config.poll_interval_seconds
            }
            for name, source in self.sources.items()
        }


# Global external data manager
_external_manager: Optional[ExternalDataManager] = None


async def get_external_data_manager() -> ExternalDataManager:
    """Get or create external data manager instance."""
    global _external_manager
    if _external_manager is None:
        _external_manager = ExternalDataManager()
        await _external_manager.initialize()
    return _external_manager
