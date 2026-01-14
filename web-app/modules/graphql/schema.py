"""
GraphQL Schema for OOVMTEL Unified View
Provides flexible querying for metrics, services, and modules
"""

import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional
from datetime import datetime
import random


# =============================================
# GraphQL Types
# =============================================

@strawberry.type
class BusinessMetrics:
    """Business/Production metrics."""
    oee: float
    quality_rate: float
    production_today: int
    cycle_time: float
    defects_today: int
    critical_alarms: int
    availability: float
    performance: float


@strawberry.type
class TechMetrics:
    """Technical/Infrastructure metrics."""
    metrics_rate: int
    logs_rate: int
    traces_rate: int
    latency_p95: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    vm_active_series: int
    vm_storage_size: int
    os_documents: int
    os_health: str


@strawberry.type
class ServiceStatus:
    """Service health status."""
    name: str
    status: str
    port: int
    latency_ms: Optional[float]


@strawberry.type
class Equipment:
    """Equipment/Asset information."""
    name: str
    status: str
    temp: float
    pressure: float
    power: float


@strawberry.type
class Alert:
    """Alert/Alarm information."""
    id: str
    severity: str
    message: str
    timestamp: str
    service: Optional[str]
    acknowledged: bool


@strawberry.type
class Event:
    """Event record."""
    time: str
    type: str
    title: str
    description: str


@strawberry.type
class PredictiveHealth:
    """Equipment predictive health."""
    equipment: str
    health_score: float
    rul_days: Optional[int]
    status: str
    trend: str
    anomalies_count: int


@strawberry.type
class RCAResult:
    """Root Cause Analysis result."""
    incident_id: str
    root_causes: List[str]
    probability: float
    summary: str


@strawberry.type
class ModuleStatus:
    """Game-changer module status."""
    name: str
    enabled: bool
    description: str


@strawberry.type
class ExternalDataSource:
    """External data source status."""
    name: str
    type: str
    status: str
    last_fetch: Optional[str]


@strawberry.type
class WeatherData:
    """Weather information."""
    temperature: float
    humidity: int
    pressure: int
    conditions: str
    wind_speed: float
    location: str


@strawberry.type
class EnergyData:
    """Energy consumption data."""
    total_power_kw: float
    power_factor: float
    energy_today_kwh: int
    cost_estimate_today: float


@strawberry.type
class UnifiedMetrics:
    """Complete unified metrics."""
    business: BusinessMetrics
    tech: TechMetrics
    services: List[ServiceStatus]
    equipment: List[Equipment]
    alerts: List[Alert]
    timestamp: str


# =============================================
# Query Resolvers
# =============================================

def get_business_metrics() -> BusinessMetrics:
    """Generate business metrics."""
    return BusinessMetrics(
        oee=random.uniform(72, 88),
        quality_rate=random.uniform(94, 99),
        production_today=random.randint(1100, 1400),
        cycle_time=random.uniform(22, 30),
        defects_today=random.randint(5, 20),
        critical_alarms=random.randint(0, 5),
        availability=random.uniform(85, 98),
        performance=random.uniform(80, 95)
    )


def get_tech_metrics() -> TechMetrics:
    """Generate tech metrics."""
    return TechMetrics(
        metrics_rate=random.randint(75000, 95000),
        logs_rate=random.randint(40000, 55000),
        traces_rate=random.randint(10000, 15000),
        latency_p95=random.uniform(30, 60),
        error_rate=random.uniform(0.01, 0.1),
        cpu_usage=random.uniform(25, 50),
        memory_usage=random.uniform(55, 75),
        disk_usage=random.uniform(40, 60),
        vm_active_series=random.randint(200000, 300000),
        vm_storage_size=random.randint(4000000000, 6000000000),
        os_documents=random.randint(100000, 150000),
        os_health="green"
    )


def get_services() -> List[ServiceStatus]:
    """Get service statuses."""
    return [
        ServiceStatus(name="VictoriaMetrics", status="up", port=8428, latency_ms=random.uniform(1, 5)),
        ServiceStatus(name="OTEL Collector", status="up", port=4317, latency_ms=random.uniform(1, 3)),
        ServiceStatus(name="OpenSearch", status="up", port=9200, latency_ms=random.uniform(5, 15)),
        ServiceStatus(name="OpenObserve", status="up", port=5080, latency_ms=random.uniform(2, 6)),
        ServiceStatus(name="Grafana", status="up", port=3000, latency_ms=random.uniform(1, 4)),
    ]


def get_equipment() -> List[Equipment]:
    """Get equipment list."""
    return [
        Equipment(name="Reactor-001", status="running", temp=random.uniform(60, 80), pressure=random.uniform(4, 6), power=random.uniform(100, 150)),
        Equipment(name="Mixer-002", status="running", temp=random.uniform(40, 60), pressure=random.uniform(2, 4), power=random.uniform(50, 80)),
        Equipment(name="Pump-003", status="warning", temp=random.uniform(30, 50), pressure=random.uniform(3, 5), power=random.uniform(20, 40)),
        Equipment(name="Furnace-004", status="running", temp=random.uniform(200, 300), pressure=random.uniform(1, 2), power=random.uniform(200, 300)),
        Equipment(name="Conveyor-005", status="running", temp=random.uniform(25, 35), pressure=random.uniform(1, 2), power=random.uniform(30, 50)),
    ]


def get_alerts() -> List[Alert]:
    """Get active alerts."""
    return [
        Alert(id="ALT-001", severity="warning", message="High temperature on Reactor-001", timestamp=datetime.utcnow().isoformat(), service="SCADA", acknowledged=False),
        Alert(id="ALT-002", severity="warning", message="Vibration alert on Pump-003", timestamp=datetime.utcnow().isoformat(), service="Predictive", acknowledged=False),
        Alert(id="ALT-003", severity="info", message="Scheduled maintenance in 2 hours", timestamp=datetime.utcnow().isoformat(), service="CMMS", acknowledged=True),
    ]


# =============================================
# GraphQL Query
# =============================================

@strawberry.type
class Query:
    """Root GraphQL Query."""

    @strawberry.field
    def metrics(self) -> UnifiedMetrics:
        """Get all unified metrics."""
        return UnifiedMetrics(
            business=get_business_metrics(),
            tech=get_tech_metrics(),
            services=get_services(),
            equipment=get_equipment(),
            alerts=get_alerts(),
            timestamp=datetime.utcnow().isoformat()
        )

    @strawberry.field
    def business_metrics(self) -> BusinessMetrics:
        """Get business metrics only."""
        return get_business_metrics()

    @strawberry.field
    def tech_metrics(self) -> TechMetrics:
        """Get technical metrics only."""
        return get_tech_metrics()

    @strawberry.field
    def services(self) -> List[ServiceStatus]:
        """Get all service statuses."""
        return get_services()

    @strawberry.field
    def service(self, name: str) -> Optional[ServiceStatus]:
        """Get specific service status."""
        for svc in get_services():
            if svc.name.lower() == name.lower():
                return svc
        return None

    @strawberry.field
    def equipment(self, status: Optional[str] = None) -> List[Equipment]:
        """Get equipment list, optionally filtered by status."""
        all_equipment = get_equipment()
        if status:
            return [e for e in all_equipment if e.status == status]
        return all_equipment

    @strawberry.field
    def equipment_by_name(self, name: str) -> Optional[Equipment]:
        """Get specific equipment by name."""
        for eq in get_equipment():
            if eq.name.lower() == name.lower():
                return eq
        return None

    @strawberry.field
    def alerts(
        self,
        severity: Optional[str] = None,
        acknowledged: Optional[bool] = None
    ) -> List[Alert]:
        """Get alerts, optionally filtered."""
        all_alerts = get_alerts()
        if severity:
            all_alerts = [a for a in all_alerts if a.severity == severity]
        if acknowledged is not None:
            all_alerts = [a for a in all_alerts if a.acknowledged == acknowledged]
        return all_alerts

    @strawberry.field
    def predictive_health(self) -> List[PredictiveHealth]:
        """Get predictive health for all equipment."""
        equipment_names = ["Reactor-001", "Mixer-002", "Pump-003", "Furnace-004", "Conveyor-005"]
        return [
            PredictiveHealth(
                equipment=name,
                health_score=random.uniform(60, 100),
                rul_days=random.randint(10, 180),
                status=random.choice(["healthy", "warning", "critical"]),
                trend=random.choice(["stable", "improving", "degrading"]),
                anomalies_count=random.randint(0, 5)
            )
            for name in equipment_names
        ]

    @strawberry.field
    def modules(self) -> List[ModuleStatus]:
        """Get game-changer modules status."""
        return [
            ModuleStatus(name="NLP", enabled=True, description="Natural language queries"),
            ModuleStatus(name="RCA", enabled=True, description="Root cause analysis"),
            ModuleStatus(name="Predictive", enabled=True, description="Predictive maintenance"),
            ModuleStatus(name="Remediation", enabled=True, description="Auto-remediation"),
            ModuleStatus(name="Edge", enabled=True, description="Edge computing"),
            ModuleStatus(name="HPC", enabled=True, description="High performance computing"),
            ModuleStatus(name="LLM", enabled=True, description="LLM-enhanced NLP"),
            ModuleStatus(name="AI Observability", enabled=True, description="AI model monitoring"),
        ]

    @strawberry.field
    def external_sources(self) -> List[ExternalDataSource]:
        """Get external data sources status."""
        return [
            ExternalDataSource(name="Weather", type="weather", status="connected", last_fetch=datetime.utcnow().isoformat()),
            ExternalDataSource(name="ERP", type="erp", status="connected", last_fetch=datetime.utcnow().isoformat()),
            ExternalDataSource(name="CMMS", type="cmms", status="connected", last_fetch=datetime.utcnow().isoformat()),
            ExternalDataSource(name="Energy", type="energy", status="connected", last_fetch=datetime.utcnow().isoformat()),
        ]

    @strawberry.field
    def weather(self) -> WeatherData:
        """Get current weather data."""
        return WeatherData(
            temperature=random.uniform(15, 30),
            humidity=random.randint(40, 80),
            pressure=random.randint(1010, 1025),
            conditions=random.choice(["Clear", "Cloudy", "Partly Cloudy"]),
            wind_speed=random.uniform(0, 20),
            location="Paris, France"
        )

    @strawberry.field
    def energy(self) -> EnergyData:
        """Get current energy consumption."""
        return EnergyData(
            total_power_kw=random.uniform(800, 1200),
            power_factor=random.uniform(0.85, 0.98),
            energy_today_kwh=random.randint(15000, 25000),
            cost_estimate_today=random.uniform(2000, 4000)
        )


# =============================================
# GraphQL Mutation
# =============================================

@strawberry.type
class Mutation:
    """Root GraphQL Mutation."""

    @strawberry.mutation
    def acknowledge_alert(self, alert_id: str, user: str) -> Alert:
        """Acknowledge an alert."""
        return Alert(
            id=alert_id,
            severity="warning",
            message="Alert acknowledged",
            timestamp=datetime.utcnow().isoformat(),
            service="System",
            acknowledged=True
        )

    @strawberry.mutation
    def trigger_rca(self, incident_description: str) -> RCAResult:
        """Trigger root cause analysis."""
        return RCAResult(
            incident_id=f"INC-{random.randint(1000, 9999)}",
            root_causes=["High temperature", "Vibration anomaly"],
            probability=random.uniform(0.7, 0.95),
            summary="Analysis complete. Primary root cause identified as high temperature."
        )


# =============================================
# Schema and Router
# =============================================

schema = strawberry.Schema(query=Query, mutation=Mutation)


def get_graphql_router() -> GraphQLRouter:
    """Get GraphQL router for FastAPI."""
    return GraphQLRouter(schema, path="/graphql")
