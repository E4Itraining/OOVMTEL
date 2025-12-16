#!/usr/bin/env python3
"""
Industrial Data Simulator for OOVMTEL Platform - Direct OTLP Version
Emits telemetry directly via OpenTelemetry SDK (no Kafka dependency)
"""

import asyncio
import logging
import os
import random
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from enum import Enum

import aiohttp
from aiohttp import web
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

# OpenTelemetry imports
from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import Counter as OTelCounter, UpDownCounter, Histogram as OTelHistogram
from opentelemetry.metrics import Observation, CallbackOptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger('industrial-simulator-otlp')

# Environment configuration
OTEL_ENDPOINT = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://otel-collector-ot:4317')
SIMULATOR_TYPE = os.getenv('SIMULATOR_TYPE', 'scada')
METRICS_PORT = int(os.getenv('METRICS_PORT', '8080'))
DATA_RATE_PER_SEC = int(os.getenv('DATA_RATE_PER_SEC', '100'))
ZONE = os.getenv('ZONE', 'ot')
SERVICE_INSTANCE_ID = os.getenv('SERVICE_INSTANCE_ID', f'{SIMULATOR_TYPE}-001')

# ============================================================================
# Data Models
# ============================================================================

class AlarmSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class EquipmentStatus(Enum):
    RUNNING = "running"
    IDLE = "idle"
    MAINTENANCE = "maintenance"
    FAULT = "fault"
    OFFLINE = "offline"

@dataclass
class SCADADataPoint:
    """SCADA telemetry data point"""
    timestamp: str
    tag_id: str
    tag_name: str
    value: float
    unit: str
    quality: str
    source: str
    area: str
    equipment_id: str

@dataclass
class MESEvent:
    """MES production event"""
    timestamp: str
    event_type: str
    order_id: str
    product_id: str
    workstation_id: str
    operator_id: str
    quantity: int
    status: str
    cycle_time_ms: int
    quality_score: float
    defects: int

@dataclass
class PLMData:
    """PLM engineering data"""
    timestamp: str
    document_id: str
    revision: str
    author: str
    change_type: str
    component_id: str
    bom_level: int
    status: str
    approval_status: str

@dataclass
class OPCUANode:
    """OPC-UA node data"""
    timestamp: str
    node_id: str
    display_name: str
    value: Any
    data_type: str
    status_code: int
    source_timestamp: str
    server_timestamp: str
    namespace: str

# ============================================================================
# OpenTelemetry Setup
# ============================================================================

def setup_opentelemetry():
    """Initialize OpenTelemetry with OTLP exporters"""

    # Create resource with service info
    resource = Resource.create({
        SERVICE_NAME: f"industrial-simulator-{SIMULATOR_TYPE}",
        SERVICE_VERSION: "2.0.0",
        "service.instance.id": SERVICE_INSTANCE_ID,
        "deployment.environment": "industrial",
        "security.zone": ZONE,
        "equipment.type": SIMULATOR_TYPE,
    })

    # Setup Metrics
    metric_exporter = OTLPMetricExporter(
        endpoint=OTEL_ENDPOINT,
        insecure=True,
    )
    metric_reader = PeriodicExportingMetricReader(
        metric_exporter,
        export_interval_millis=10000,  # Export every 10 seconds
    )
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )
    metrics.set_meter_provider(meter_provider)

    # Setup Tracing
    trace_exporter = OTLPSpanExporter(
        endpoint=OTEL_ENDPOINT,
        insecure=True,
    )
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(tracer_provider)

    logger.info(f"OpenTelemetry initialized, exporting to {OTEL_ENDPOINT}")

    return metrics.get_meter("industrial-simulator"), trace.get_tracer("industrial-simulator")


# ============================================================================
# Prometheus Metrics (for local scraping - backwards compatibility)
# ============================================================================

# SCADA Metrics
scada_temperature = Gauge('scada_temperature_celsius', 'Temperature sensor reading', ['equipment', 'area', 'sensor'])
scada_pressure = Gauge('scada_pressure_bar', 'Pressure sensor reading', ['equipment', 'area', 'sensor'])
scada_flow_rate = Gauge('scada_flow_rate_m3h', 'Flow rate sensor reading', ['equipment', 'area', 'sensor'])
scada_level = Gauge('scada_level_percent', 'Tank level reading', ['equipment', 'area', 'tank'])
scada_vibration = Gauge('scada_vibration_mms', 'Vibration sensor reading', ['equipment', 'area', 'sensor'])
scada_power = Gauge('scada_power_kw', 'Power consumption', ['equipment', 'area'])
scada_alarms_total = Counter('scada_alarms_total', 'Total alarms generated', ['severity', 'area'])
scada_data_points = Counter('scada_data_points_total', 'Total SCADA data points generated', ['source'])

# MES Metrics
mes_production_count = Counter('mes_production_count_total', 'Total production count', ['workstation', 'product'])
mes_cycle_time = Histogram('mes_cycle_time_seconds', 'Production cycle time', ['workstation', 'product'],
                          buckets=[1, 2, 5, 10, 20, 30, 60, 120, 300])
mes_oee = Gauge('mes_oee_percent', 'Overall Equipment Effectiveness', ['workstation'])
mes_quality_rate = Gauge('mes_quality_rate_percent', 'Quality rate', ['workstation', 'product'])
mes_defects_total = Counter('mes_defects_total', 'Total defects detected', ['workstation', 'defect_type'])

# PLM Metrics
plm_changes_total = Counter('plm_changes_total', 'Total PLM changes', ['change_type', 'component_type'])
plm_approval_time = Histogram('plm_approval_time_hours', 'Time to approval', ['document_type'],
                             buckets=[1, 4, 8, 24, 48, 72, 168])
plm_active_revisions = Gauge('plm_active_revisions', 'Active document revisions', ['status'])

# OPC-UA Metrics
opcua_nodes_total = Gauge('opcua_nodes_total', 'Total OPC-UA nodes', ['namespace', 'status'])
opcua_read_latency = Histogram('opcua_read_latency_ms', 'OPC-UA read latency', ['namespace'],
                               buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000])
opcua_subscription_count = Gauge('opcua_subscription_count', 'Active subscriptions', ['namespace'])


# ============================================================================
# Data Generators with OTLP
# ============================================================================

class SCADASimulator:
    """Simulates SCADA system data with OTLP export"""

    AREAS = ['zone_a', 'zone_b', 'zone_c', 'utilities', 'packaging']
    EQUIPMENT = {
        'zone_a': ['reactor_001', 'reactor_002', 'mixer_001', 'pump_001', 'pump_002'],
        'zone_b': ['furnace_001', 'conveyor_001', 'press_001', 'robot_001'],
        'zone_c': ['tank_001', 'tank_002', 'compressor_001', 'filter_001'],
        'utilities': ['boiler_001', 'chiller_001', 'air_handler_001'],
        'packaging': ['filler_001', 'labeler_001', 'palletizer_001']
    }

    def __init__(self, meter, tracer):
        self.meter = meter
        self.tracer = tracer
        self.base_values: Dict[str, float] = {}
        self._init_base_values()
        self._init_otel_metrics()

    def _init_base_values(self):
        """Initialize base values for sensors"""
        for area, equipment_list in self.EQUIPMENT.items():
            for eq in equipment_list:
                self.base_values[f"{eq}_temp"] = random.uniform(20, 80)
                self.base_values[f"{eq}_pressure"] = random.uniform(1, 10)
                self.base_values[f"{eq}_flow"] = random.uniform(10, 100)
                self.base_values[f"{eq}_level"] = random.uniform(20, 80)
                self.base_values[f"{eq}_vibration"] = random.uniform(0.1, 2.0)
                self.base_values[f"{eq}_power"] = random.uniform(10, 500)

    def _init_otel_metrics(self):
        """Initialize OpenTelemetry metrics"""
        self.otel_temperature = self.meter.create_gauge(
            "scada.temperature",
            unit="Cel",
            description="Temperature sensor reading"
        )
        self.otel_pressure = self.meter.create_gauge(
            "scada.pressure",
            unit="bar",
            description="Pressure sensor reading"
        )
        self.otel_flow_rate = self.meter.create_gauge(
            "scada.flow_rate",
            unit="m3/h",
            description="Flow rate sensor reading"
        )
        self.otel_level = self.meter.create_gauge(
            "scada.level",
            unit="%",
            description="Tank level reading"
        )
        self.otel_vibration = self.meter.create_gauge(
            "scada.vibration",
            unit="mm/s",
            description="Vibration sensor reading"
        )
        self.otel_power = self.meter.create_gauge(
            "scada.power",
            unit="kW",
            description="Power consumption"
        )
        self.otel_data_points = self.meter.create_counter(
            "scada.data_points",
            unit="1",
            description="Total SCADA data points generated"
        )
        self.otel_alarms = self.meter.create_counter(
            "scada.alarms",
            unit="1",
            description="Total alarms generated"
        )

    def _drift_value(self, key: str, drift_range: float = 0.05) -> float:
        """Apply realistic drift to sensor value"""
        base = self.base_values[key]
        drift = base * random.uniform(-drift_range, drift_range)
        new_value = base + drift
        if random.random() < 0.01:
            new_value *= random.uniform(0.8, 1.2)
        self.base_values[key] = new_value
        return new_value

    def generate_data_point(self) -> SCADADataPoint:
        """Generate a single SCADA data point"""
        area = random.choice(self.AREAS)
        equipment = random.choice(self.EQUIPMENT[area])
        sensor_type = random.choice(['temp', 'pressure', 'flow', 'level', 'vibration', 'power'])

        key = f"{equipment}_{sensor_type}"
        value = self._drift_value(key)

        units = {
            'temp': '°C', 'pressure': 'bar', 'flow': 'm³/h',
            'level': '%', 'vibration': 'mm/s', 'power': 'kW'
        }

        quality = 'good' if random.random() > 0.02 else random.choice(['uncertain', 'bad'])

        return SCADADataPoint(
            timestamp=datetime.now(timezone.utc).isoformat(),
            tag_id=f"SCADA.{area.upper()}.{equipment.upper()}.{sensor_type.upper()}",
            tag_name=f"{equipment}_{sensor_type}",
            value=round(value, 3),
            unit=units[sensor_type],
            quality=quality,
            source='plc_main',
            area=area,
            equipment_id=equipment
        )

    def update_metrics(self, data: SCADADataPoint):
        """Update both Prometheus and OpenTelemetry metrics"""
        labels = {'equipment': data.equipment_id, 'area': data.area, 'sensor': data.tag_name}
        otel_attrs = {"equipment": data.equipment_id, "area": data.area, "sensor": data.tag_name, "quality": data.quality}

        # Update Prometheus (for backwards compatibility)
        if 'temp' in data.tag_name:
            scada_temperature.labels(**labels).set(data.value)
            self.otel_temperature.set(data.value, otel_attrs)
        elif 'pressure' in data.tag_name:
            scada_pressure.labels(**labels).set(data.value)
            self.otel_pressure.set(data.value, otel_attrs)
        elif 'flow' in data.tag_name:
            scada_flow_rate.labels(**labels).set(data.value)
            self.otel_flow_rate.set(data.value, otel_attrs)
        elif 'level' in data.tag_name:
            scada_level.labels(equipment=data.equipment_id, area=data.area, tank=data.tag_name).set(data.value)
            self.otel_level.set(data.value, otel_attrs)
        elif 'vibration' in data.tag_name:
            scada_vibration.labels(**labels).set(data.value)
            self.otel_vibration.set(data.value, otel_attrs)
        elif 'power' in data.tag_name:
            scada_power.labels(equipment=data.equipment_id, area=data.area).set(data.value)
            self.otel_power.set(data.value, otel_attrs)

        scada_data_points.labels(source=data.source).inc()
        self.otel_data_points.add(1, {"source": data.source})

        # Generate occasional alarms
        base_key = f"{data.equipment_id}_{data.tag_name.split('_')[-1]}"
        if data.value > self.base_values.get(base_key, 50) * 1.3:
            severity = 'warning' if random.random() > 0.3 else 'critical'
            scada_alarms_total.labels(severity=severity, area=data.area).inc()
            self.otel_alarms.add(1, {"severity": severity, "area": data.area})


class MESSimulator:
    """Simulates MES data with OTLP export"""

    WORKSTATIONS = ['ws_assembly_01', 'ws_assembly_02', 'ws_welding_01', 'ws_paint_01', 'ws_qc_01']
    PRODUCTS = ['product_a', 'product_b', 'product_c', 'product_d']
    OPERATORS = [f'operator_{i:03d}' for i in range(1, 21)]
    EVENT_TYPES = ['production_start', 'production_end', 'quality_check', 'material_consumed', 'downtime_start', 'downtime_end']
    DEFECT_TYPES = ['scratch', 'dimension_error', 'color_mismatch', 'assembly_fault', 'missing_component']

    def __init__(self, meter, tracer):
        self.meter = meter
        self.tracer = tracer
        self._init_otel_metrics()

    def _init_otel_metrics(self):
        """Initialize OpenTelemetry metrics"""
        self.otel_production = self.meter.create_counter(
            "mes.production_count",
            unit="1",
            description="Total production count"
        )
        self.otel_cycle_time = self.meter.create_histogram(
            "mes.cycle_time",
            unit="s",
            description="Production cycle time"
        )
        self.otel_oee = self.meter.create_gauge(
            "mes.oee",
            unit="%",
            description="Overall Equipment Effectiveness"
        )
        self.otel_quality_rate = self.meter.create_gauge(
            "mes.quality_rate",
            unit="%",
            description="Quality rate"
        )
        self.otel_defects = self.meter.create_counter(
            "mes.defects",
            unit="1",
            description="Total defects detected"
        )

    def generate_event(self) -> MESEvent:
        """Generate a MES production event"""
        workstation = random.choice(self.WORKSTATIONS)
        product = random.choice(self.PRODUCTS)
        event_type = random.choice(self.EVENT_TYPES)

        base_cycle_times = {
            'product_a': 15000, 'product_b': 25000,
            'product_c': 45000, 'product_d': 8000
        }

        cycle_time = int(base_cycle_times[product] * random.uniform(0.8, 1.3))
        quality_score = min(100, max(0, random.gauss(95, 5)))
        defects = 0 if quality_score > 90 else random.randint(1, 3)

        return MESEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            order_id=f"ORD-{random.randint(10000, 99999)}",
            product_id=product,
            workstation_id=workstation,
            operator_id=random.choice(self.OPERATORS),
            quantity=random.randint(1, 10),
            status='completed' if event_type == 'production_end' else 'in_progress',
            cycle_time_ms=cycle_time,
            quality_score=round(quality_score, 2),
            defects=defects
        )

    def update_metrics(self, event: MESEvent):
        """Update both Prometheus and OpenTelemetry metrics"""
        attrs = {"workstation": event.workstation_id, "product": event.product_id}

        if event.event_type == 'production_end':
            mes_production_count.labels(**attrs).inc(event.quantity)
            self.otel_production.add(event.quantity, attrs)

            mes_cycle_time.labels(**attrs).observe(event.cycle_time_ms / 1000)
            self.otel_cycle_time.record(event.cycle_time_ms / 1000, attrs)

            mes_quality_rate.labels(**attrs).set(event.quality_score)
            self.otel_quality_rate.set(event.quality_score, attrs)

            if event.defects > 0:
                defect_type = random.choice(self.DEFECT_TYPES)
                mes_defects_total.labels(workstation=event.workstation_id, defect_type=defect_type).inc(event.defects)
                self.otel_defects.add(event.defects, {"workstation": event.workstation_id, "defect_type": defect_type})

        oee = random.gauss(85, 10)
        mes_oee.labels(workstation=event.workstation_id).set(max(0, min(100, oee)))
        self.otel_oee.set(max(0, min(100, oee)), {"workstation": event.workstation_id})


class PLMSimulator:
    """Simulates PLM data with OTLP export"""

    DOCUMENT_TYPES = ['cad_model', 'drawing', 'specification', 'bom', 'work_instruction', 'test_plan']
    CHANGE_TYPES = ['create', 'modify', 'review', 'approve', 'release', 'obsolete']
    COMPONENT_TYPES = ['mechanical', 'electrical', 'software', 'assembly', 'raw_material']
    AUTHORS = [f'engineer_{i:03d}' for i in range(1, 16)]

    def __init__(self, meter, tracer):
        self.meter = meter
        self.tracer = tracer
        self._init_otel_metrics()

    def _init_otel_metrics(self):
        """Initialize OpenTelemetry metrics"""
        self.otel_changes = self.meter.create_counter(
            "plm.changes",
            unit="1",
            description="Total PLM changes"
        )
        self.otel_approval_time = self.meter.create_histogram(
            "plm.approval_time",
            unit="h",
            description="Time to approval"
        )
        self.otel_active_revisions = self.meter.create_gauge(
            "plm.active_revisions",
            unit="1",
            description="Active document revisions"
        )

    def generate_data(self) -> PLMData:
        """Generate PLM engineering data"""
        change_type = random.choice(self.CHANGE_TYPES)

        approval_status = 'pending'
        if change_type in ['approve', 'release']:
            approval_status = 'approved'
        elif change_type == 'obsolete':
            approval_status = 'obsolete'

        return PLMData(
            timestamp=datetime.now(timezone.utc).isoformat(),
            document_id=f"DOC-{random.randint(100000, 999999)}",
            revision=f"{random.randint(1, 20)}.{random.randint(0, 9)}",
            author=random.choice(self.AUTHORS),
            change_type=change_type,
            component_id=f"CMP-{random.randint(10000, 99999)}",
            bom_level=random.randint(0, 5),
            status=random.choice(['draft', 'in_review', 'approved', 'released']),
            approval_status=approval_status
        )

    def update_metrics(self, data: PLMData):
        """Update both Prometheus and OpenTelemetry metrics"""
        component_type = random.choice(self.COMPONENT_TYPES)
        attrs = {"change_type": data.change_type, "component_type": component_type}

        plm_changes_total.labels(**attrs).inc()
        self.otel_changes.add(1, attrs)

        if data.change_type == 'approve':
            approval_time = random.expovariate(1/24)
            doc_type = random.choice(self.DOCUMENT_TYPES)
            plm_approval_time.labels(document_type=doc_type).observe(approval_time)
            self.otel_approval_time.record(approval_time, {"document_type": doc_type})

        revisions = random.randint(10, 100)
        plm_active_revisions.labels(status=data.status).set(revisions)
        self.otel_active_revisions.set(revisions, {"status": data.status})


class OPCUASimulator:
    """Simulates OPC-UA data with OTLP export"""

    NAMESPACES = ['urn:industrial:plc', 'urn:industrial:sensors', 'urn:industrial:drives']
    NODE_TYPES = ['analog', 'digital', 'string', 'array']

    def __init__(self, meter, tracer):
        self.meter = meter
        self.tracer = tracer
        self.nodes: Dict[str, Dict] = {}
        self._init_nodes()
        self._init_otel_metrics()

    def _init_nodes(self):
        """Initialize OPC-UA node structure"""
        for ns in self.NAMESPACES:
            for i in range(50):
                node_id = f"ns={self.NAMESPACES.index(ns)+2};s=Node_{i:04d}"
                self.nodes[node_id] = {
                    'namespace': ns,
                    'display_name': f"Industrial_Node_{i:04d}",
                    'data_type': random.choice(self.NODE_TYPES),
                    'base_value': random.uniform(0, 100)
                }

    def _init_otel_metrics(self):
        """Initialize OpenTelemetry metrics"""
        self.otel_nodes = self.meter.create_gauge(
            "opcua.nodes",
            unit="1",
            description="Total OPC-UA nodes"
        )
        self.otel_read_latency = self.meter.create_histogram(
            "opcua.read_latency",
            unit="ms",
            description="OPC-UA read latency"
        )
        self.otel_subscriptions = self.meter.create_gauge(
            "opcua.subscriptions",
            unit="1",
            description="Active subscriptions"
        )

    def generate_node_data(self) -> OPCUANode:
        """Generate OPC-UA node data"""
        node_id = random.choice(list(self.nodes.keys()))
        node_info = self.nodes[node_id]

        if node_info['data_type'] == 'analog':
            value = node_info['base_value'] * random.uniform(0.9, 1.1)
        elif node_info['data_type'] == 'digital':
            value = random.choice([True, False])
        elif node_info['data_type'] == 'string':
            value = f"STATUS_{random.choice(['OK', 'WARN', 'ERR'])}"
        else:
            value = [random.uniform(0, 100) for _ in range(5)]

        now = datetime.now(timezone.utc)

        return OPCUANode(
            timestamp=now.isoformat(),
            node_id=node_id,
            display_name=node_info['display_name'],
            value=value if not isinstance(value, float) else round(value, 3),
            data_type=node_info['data_type'],
            status_code=0 if random.random() > 0.01 else random.choice([0x80000000, 0x80010000]),
            source_timestamp=now.isoformat(),
            server_timestamp=now.isoformat(),
            namespace=node_info['namespace']
        )

    def update_metrics(self, data: OPCUANode):
        """Update both Prometheus and OpenTelemetry metrics"""
        status = 'good' if data.status_code == 0 else 'bad'
        attrs = {"namespace": data.namespace, "status": status}

        node_count = len([n for n in self.nodes.values() if n['namespace'] == data.namespace])
        opcua_nodes_total.labels(**attrs).set(node_count)
        self.otel_nodes.set(node_count, attrs)

        latency = random.expovariate(1/10)
        opcua_read_latency.labels(namespace=data.namespace).observe(latency)
        self.otel_read_latency.record(latency, {"namespace": data.namespace})

        subs = random.randint(5, 20)
        opcua_subscription_count.labels(namespace=data.namespace).set(subs)
        self.otel_subscriptions.set(subs, {"namespace": data.namespace})


# ============================================================================
# HTTP Server for Metrics (Prometheus compatibility)
# ============================================================================

async def metrics_handler(request):
    """Handle Prometheus metrics endpoint"""
    return web.Response(body=generate_latest(), content_type=CONTENT_TYPE_LATEST)

async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({'status': 'healthy', 'simulator': SIMULATOR_TYPE, 'mode': 'otlp'})

async def ready_handler(request):
    """Readiness check endpoint"""
    return web.json_response({'status': 'ready', 'simulator': SIMULATOR_TYPE, 'mode': 'otlp'})


# ============================================================================
# Main Simulation Loop
# ============================================================================

async def run_simulator():
    """Main simulation loop with Direct OTLP"""
    logger.info(f"Starting {SIMULATOR_TYPE} simulator (Direct OTLP mode)")
    logger.info(f"OTLP endpoint: {OTEL_ENDPOINT}")
    logger.info(f"Zone: {ZONE}")
    logger.info(f"Data rate: {DATA_RATE_PER_SEC} points/second")
    logger.info(f"Metrics port: {METRICS_PORT}")

    # Initialize OpenTelemetry
    meter, tracer = setup_opentelemetry()

    # Initialize simulator based on type
    simulators = {
        'scada': SCADASimulator,
        'mes': MESSimulator,
        'plm': PLMSimulator,
        'opcua': OPCUASimulator
    }

    if SIMULATOR_TYPE not in simulators:
        logger.error(f"Unknown simulator type: {SIMULATOR_TYPE}")
        return

    simulator = simulators[SIMULATOR_TYPE](meter, tracer)
    logger.info(f"Simulator initialized: {SIMULATOR_TYPE}")

    # Calculate interval between data points
    interval = 1.0 / DATA_RATE_PER_SEC

    # Start HTTP server
    app = web.Application()
    app.router.add_get('/metrics', metrics_handler)
    app.router.add_get('/health', health_handler)
    app.router.add_get('/ready', ready_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', METRICS_PORT)
    await site.start()
    logger.info(f"Metrics server started on port {METRICS_PORT}")

    # Main loop
    data_count = 0
    last_log_time = time.time()

    while True:
        try:
            start_time = time.time()

            # Generate data based on simulator type
            with tracer.start_as_current_span(f"{SIMULATOR_TYPE}_generate") as span:
                if SIMULATOR_TYPE == 'scada':
                    data = simulator.generate_data_point()
                    span.set_attribute("tag_id", data.tag_id)
                elif SIMULATOR_TYPE == 'mes':
                    data = simulator.generate_event()
                    span.set_attribute("event_type", data.event_type)
                elif SIMULATOR_TYPE == 'plm':
                    data = simulator.generate_data()
                    span.set_attribute("change_type", data.change_type)
                else:
                    data = simulator.generate_node_data()
                    span.set_attribute("node_id", data.node_id)

                # Update metrics (Prometheus + OTLP)
                simulator.update_metrics(data)

            data_count += 1

            # Log statistics every 10 seconds
            if time.time() - last_log_time >= 10:
                rate = data_count / (time.time() - last_log_time)
                logger.info(f"Generated {data_count} data points, rate: {rate:.2f}/s (OTLP mode)")
                data_count = 0
                last_log_time = time.time()

            # Sleep to maintain target rate
            elapsed = time.time() - start_time
            if elapsed < interval:
                await asyncio.sleep(interval - elapsed)

        except Exception as e:
            logger.error(f"Simulation error: {e}")
            await asyncio.sleep(1)


def main():
    """Entry point"""
    asyncio.run(run_simulator())


if __name__ == '__main__':
    main()
