#!/usr/bin/env python3
"""
Industrial Data Simulator for OOVMTEL Platform
Generates realistic IT/OT data for SCADA, MES, PLM, and OPC-UA systems
"""

import asyncio
import json
import logging
import os
import random
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum

import aiohttp
from aiohttp import web
from kafka import KafkaProducer
from prometheus_client import Counter, Gauge, Histogram, start_http_server, generate_latest, CONTENT_TYPE_LATEST

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger('industrial-simulator')

# Environment configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
OTEL_ENDPOINT = os.getenv('OTEL_ENDPOINT', 'http://otel-collector:4318')
SIMULATOR_TYPE = os.getenv('SIMULATOR_TYPE', 'scada')
METRICS_PORT = int(os.getenv('METRICS_PORT', '8080'))
DATA_RATE_PER_SEC = int(os.getenv('DATA_RATE_PER_SEC', '100'))

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
# Prometheus Metrics
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
mes_downtime_seconds = Counter('mes_downtime_seconds_total', 'Total downtime', ['workstation', 'reason'])

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
# Data Generators
# ============================================================================

class SCADASimulator:
    """Simulates SCADA system data"""

    AREAS = ['zone_a', 'zone_b', 'zone_c', 'utilities', 'packaging']
    EQUIPMENT = {
        'zone_a': ['reactor_001', 'reactor_002', 'mixer_001', 'pump_001', 'pump_002'],
        'zone_b': ['furnace_001', 'conveyor_001', 'press_001', 'robot_001'],
        'zone_c': ['tank_001', 'tank_002', 'compressor_001', 'filter_001'],
        'utilities': ['boiler_001', 'chiller_001', 'air_handler_001'],
        'packaging': ['filler_001', 'labeler_001', 'palletizer_001']
    }

    def __init__(self):
        self.base_values: Dict[str, float] = {}
        self.kafka_producer: Optional[KafkaProducer] = None
        self._init_base_values()

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

    def _drift_value(self, key: str, drift_range: float = 0.05) -> float:
        """Apply realistic drift to sensor value"""
        base = self.base_values[key]
        drift = base * random.uniform(-drift_range, drift_range)
        new_value = base + drift

        # Occasionally have larger changes (process events)
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
            'temp': '°C',
            'pressure': 'bar',
            'flow': 'm³/h',
            'level': '%',
            'vibration': 'mm/s',
            'power': 'kW'
        }

        # Determine quality (occasionally bad)
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

    def update_prometheus_metrics(self, data: SCADADataPoint):
        """Update Prometheus metrics with SCADA data"""
        labels = {'equipment': data.equipment_id, 'area': data.area, 'sensor': data.tag_name}

        if 'temp' in data.tag_name:
            scada_temperature.labels(**labels).set(data.value)
        elif 'pressure' in data.tag_name:
            scada_pressure.labels(**labels).set(data.value)
        elif 'flow' in data.tag_name:
            scada_flow_rate.labels(**labels).set(data.value)
        elif 'level' in data.tag_name:
            scada_level.labels(equipment=data.equipment_id, area=data.area, tank=data.tag_name).set(data.value)
        elif 'vibration' in data.tag_name:
            scada_vibration.labels(**labels).set(data.value)
        elif 'power' in data.tag_name:
            scada_power.labels(equipment=data.equipment_id, area=data.area).set(data.value)

        scada_data_points.labels(source=data.source).inc()

        # Generate occasional alarms
        if data.value > self.base_values.get(f"{data.equipment_id}_{data.tag_name.split('_')[-1]}", 50) * 1.3:
            severity = 'warning' if random.random() > 0.3 else 'critical'
            scada_alarms_total.labels(severity=severity, area=data.area).inc()


class MESSimulator:
    """Simulates MES (Manufacturing Execution System) data"""

    WORKSTATIONS = ['ws_assembly_01', 'ws_assembly_02', 'ws_welding_01', 'ws_paint_01', 'ws_qc_01']
    PRODUCTS = ['product_a', 'product_b', 'product_c', 'product_d']
    OPERATORS = [f'operator_{i:03d}' for i in range(1, 21)]
    EVENT_TYPES = ['production_start', 'production_end', 'quality_check', 'material_consumed', 'downtime_start', 'downtime_end']
    DEFECT_TYPES = ['scratch', 'dimension_error', 'color_mismatch', 'assembly_fault', 'missing_component']

    def __init__(self):
        self.active_orders: Dict[str, Dict] = {}
        self.workstation_status: Dict[str, EquipmentStatus] = {
            ws: EquipmentStatus.RUNNING for ws in self.WORKSTATIONS
        }
        self.kafka_producer: Optional[KafkaProducer] = None

    def generate_event(self) -> MESEvent:
        """Generate a MES production event"""
        workstation = random.choice(self.WORKSTATIONS)
        product = random.choice(self.PRODUCTS)
        event_type = random.choice(self.EVENT_TYPES)

        # Realistic cycle times per product (ms)
        base_cycle_times = {
            'product_a': 15000,
            'product_b': 25000,
            'product_c': 45000,
            'product_d': 8000
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

    def update_prometheus_metrics(self, event: MESEvent):
        """Update Prometheus metrics with MES data"""
        if event.event_type == 'production_end':
            mes_production_count.labels(workstation=event.workstation_id, product=event.product_id).inc(event.quantity)
            mes_cycle_time.labels(workstation=event.workstation_id, product=event.product_id).observe(event.cycle_time_ms / 1000)
            mes_quality_rate.labels(workstation=event.workstation_id, product=event.product_id).set(event.quality_score)

            if event.defects > 0:
                defect_type = random.choice(self.DEFECT_TYPES)
                mes_defects_total.labels(workstation=event.workstation_id, defect_type=defect_type).inc(event.defects)

        # Update OEE (simplified calculation)
        oee = random.gauss(85, 10)
        mes_oee.labels(workstation=event.workstation_id).set(max(0, min(100, oee)))


class PLMSimulator:
    """Simulates PLM (Product Lifecycle Management) data"""

    DOCUMENT_TYPES = ['cad_model', 'drawing', 'specification', 'bom', 'work_instruction', 'test_plan']
    CHANGE_TYPES = ['create', 'modify', 'review', 'approve', 'release', 'obsolete']
    COMPONENT_TYPES = ['mechanical', 'electrical', 'software', 'assembly', 'raw_material']
    AUTHORS = [f'engineer_{i:03d}' for i in range(1, 16)]

    def __init__(self):
        self.kafka_producer: Optional[KafkaProducer] = None

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

    def update_prometheus_metrics(self, data: PLMData):
        """Update Prometheus metrics with PLM data"""
        component_type = random.choice(self.COMPONENT_TYPES)
        plm_changes_total.labels(change_type=data.change_type, component_type=component_type).inc()

        if data.change_type == 'approve':
            # Simulate approval time (hours)
            approval_time = random.expovariate(1/24)  # Mean 24 hours
            plm_approval_time.labels(document_type=random.choice(self.DOCUMENT_TYPES)).observe(approval_time)

        # Update active revisions gauge
        plm_active_revisions.labels(status=data.status).set(random.randint(10, 100))


class OPCUASimulator:
    """Simulates OPC-UA server data"""

    NAMESPACES = ['urn:industrial:plc', 'urn:industrial:sensors', 'urn:industrial:drives']
    NODE_TYPES = ['analog', 'digital', 'string', 'array']

    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.kafka_producer: Optional[KafkaProducer] = None
        self._init_nodes()

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

    def generate_node_data(self) -> OPCUANode:
        """Generate OPC-UA node data"""
        node_id = random.choice(list(self.nodes.keys()))
        node_info = self.nodes[node_id]

        # Generate value based on type
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

    def update_prometheus_metrics(self, data: OPCUANode):
        """Update Prometheus metrics with OPC-UA data"""
        status = 'good' if data.status_code == 0 else 'bad'
        opcua_nodes_total.labels(namespace=data.namespace, status=status).set(
            len([n for n in self.nodes.values() if n['namespace'] == data.namespace])
        )

        # Simulate read latency
        latency = random.expovariate(1/10)  # Mean 10ms
        opcua_read_latency.labels(namespace=data.namespace).observe(latency)

        opcua_subscription_count.labels(namespace=data.namespace).set(random.randint(5, 20))


# ============================================================================
# Kafka Producer
# ============================================================================

def create_kafka_producer() -> Optional[KafkaProducer]:
    """Create Kafka producer with retry logic"""
    max_retries = 5
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                compression_type='lz4',
                batch_size=65536,
                linger_ms=10,
                acks='all',
                retries=3
            )
            logger.info(f"Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
            return producer
        except Exception as e:
            logger.warning(f"Kafka connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

    logger.error("Failed to connect to Kafka after all retries")
    return None


# ============================================================================
# HTTP Server for Metrics
# ============================================================================

async def metrics_handler(request):
    """Handle Prometheus metrics endpoint"""
    return web.Response(
        body=generate_latest(),
        content_type=CONTENT_TYPE_LATEST
    )

async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({'status': 'healthy', 'simulator': SIMULATOR_TYPE})

async def ready_handler(request):
    """Readiness check endpoint"""
    return web.json_response({'status': 'ready', 'simulator': SIMULATOR_TYPE})


# ============================================================================
# Main Simulation Loop
# ============================================================================

async def run_simulator():
    """Main simulation loop"""
    logger.info(f"Starting {SIMULATOR_TYPE} simulator")
    logger.info(f"Data rate: {DATA_RATE_PER_SEC} points/second")
    logger.info(f"Metrics port: {METRICS_PORT}")

    # Initialize simulator based on type
    simulators = {
        'scada': SCADASimulator,
        'mes': MESSimulator,
        'plm': PLMSimulator,
        'opcua': OPCUASimulator
    }

    kafka_topics = {
        'scada': 'scada-metrics',
        'mes': 'mes-events',
        'plm': 'plm-data',
        'opcua': 'opcua-nodes'
    }

    if SIMULATOR_TYPE not in simulators:
        logger.error(f"Unknown simulator type: {SIMULATOR_TYPE}")
        return

    simulator = simulators[SIMULATOR_TYPE]()
    kafka_topic = kafka_topics[SIMULATOR_TYPE]

    # Calculate interval between data points
    interval = 1.0 / DATA_RATE_PER_SEC

    # IMPORTANT: Start HTTP server FIRST before Kafka connection
    # This ensures healthchecks pass while waiting for Kafka
    app = web.Application()
    app.router.add_get('/metrics', metrics_handler)
    app.router.add_get('/health', health_handler)
    app.router.add_get('/ready', ready_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', METRICS_PORT)
    await site.start()
    logger.info(f"Metrics server started on port {METRICS_PORT}")

    # Now connect to Kafka (this can block for up to 25s)
    # HTTP server is already running, so healthchecks will pass
    kafka_producer = await asyncio.get_event_loop().run_in_executor(
        None, create_kafka_producer
    )

    # Main loop
    data_count = 0
    last_log_time = time.time()

    while True:
        try:
            start_time = time.time()

            # Generate data based on simulator type
            if SIMULATOR_TYPE == 'scada':
                data = simulator.generate_data_point()
            elif SIMULATOR_TYPE == 'mes':
                data = simulator.generate_event()
            elif SIMULATOR_TYPE == 'plm':
                data = simulator.generate_data()
            else:
                data = simulator.generate_node_data()

            # Update Prometheus metrics
            simulator.update_prometheus_metrics(data)

            # Send to Kafka
            if kafka_producer:
                try:
                    kafka_producer.send(
                        kafka_topic,
                        key=getattr(data, 'tag_id', None) or getattr(data, 'node_id', None) or str(data_count),
                        value=asdict(data)
                    )
                except Exception as e:
                    logger.error(f"Kafka send error: {e}")

            data_count += 1

            # Log statistics every 10 seconds
            if time.time() - last_log_time >= 10:
                rate = data_count / (time.time() - last_log_time)
                logger.info(f"Generated {data_count} data points, rate: {rate:.2f}/s")
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
