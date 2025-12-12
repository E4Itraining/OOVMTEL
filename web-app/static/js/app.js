/**
 * OOVMTEL Unified Business-Tech View
 * Industrial Observability Platform
 *
 * Main application JavaScript
 */

// Configuration
const CONFIG = {
    apiBaseUrl: '/api',
    refreshInterval: 10000, // 10 seconds
    victoriaMetricsUrl: 'http://localhost:8428',
    animations: true
};

// Application State
const state = {
    currentView: 'unified',
    lastUpdate: null,
    data: {
        business: {},
        tech: {},
        services: []
    }
};

// =========================================
// Utility Functions
// =========================================

function formatNumber(num, decimals = 0) {
    if (num === null || num === undefined || isNaN(num)) return '--';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toFixed(decimals);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
}

function randomInRange(min, max) {
    return Math.random() * (max - min) + min;
}

// =========================================
// View Toggle
// =========================================

function initViewToggle() {
    const toggleBtns = document.querySelectorAll('.toggle-btn');

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            switchView(view);
        });
    });
}

function switchView(view) {
    state.currentView = view;

    // Update toggle buttons
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });

    // Update view panels
    document.querySelectorAll('.view-panel').forEach(panel => {
        panel.classList.remove('active');
    });

    const viewMap = {
        'unified': 'unifiedView',
        'business': 'businessView',
        'tech': 'techView'
    };

    document.getElementById(viewMap[view]).classList.add('active');
}

// =========================================
// Data Fetching
// =========================================

async function fetchMetrics() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/metrics`);
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.warn('API not available, using simulated data');
    }

    // Return simulated data if API is not available
    return generateSimulatedData();
}

function generateSimulatedData() {
    return {
        business: {
            oee: randomInRange(72, 88),
            qualityRate: randomInRange(94, 99),
            productionToday: Math.floor(randomInRange(1100, 1400)),
            cycleTime: randomInRange(22, 30),
            defectsToday: Math.floor(randomInRange(5, 20)),
            criticalAlarms: Math.floor(randomInRange(0, 5)),
            availability: randomInRange(85, 98),
            performance: randomInRange(80, 95),
            equipment: [
                { name: 'Reactor-001', status: 'running', temp: randomInRange(60, 80), pressure: randomInRange(4, 6), power: randomInRange(100, 150) },
                { name: 'Mixer-002', status: 'running', temp: randomInRange(40, 60), pressure: randomInRange(2, 4), power: randomInRange(50, 80) },
                { name: 'Pump-003', status: 'warning', temp: randomInRange(30, 50), pressure: randomInRange(3, 5), power: randomInRange(20, 40) },
                { name: 'Furnace-004', status: 'running', temp: randomInRange(200, 300), pressure: randomInRange(1, 2), power: randomInRange(200, 300) },
                { name: 'Conveyor-005', status: 'running', temp: randomInRange(25, 35), pressure: randomInRange(1, 2), power: randomInRange(30, 50) },
                { name: 'Tank-006', status: 'stopped', temp: randomInRange(20, 30), pressure: randomInRange(1, 2), power: 0 }
            ],
            productionByProduct: {
                'Product A': Math.floor(randomInRange(250, 350)),
                'Product B': Math.floor(randomInRange(200, 300)),
                'Product C': Math.floor(randomInRange(350, 450)),
                'Product D': Math.floor(randomInRange(280, 380))
            },
            alarms: [
                { severity: 'critical', message: 'High temperature on Reactor-001' },
                { severity: 'warning', message: 'Vibration alert on Pump-003' },
                { severity: 'warning', message: 'Maintenance due on Mixer-002' }
            ]
        },
        tech: {
            metricsRate: Math.floor(randomInRange(75000, 95000)),
            logsRate: Math.floor(randomInRange(40000, 55000)),
            tracesRate: Math.floor(randomInRange(10000, 15000)),
            latencyP95: randomInRange(30, 60),
            errorRate: randomInRange(0.01, 0.1),
            kafkaThroughput: Math.floor(randomInRange(2000000, 3000000)),
            cpuUsage: randomInRange(25, 50),
            memoryUsage: randomInRange(55, 75),
            diskUsage: randomInRange(40, 60),
            vmActiveSeries: Math.floor(randomInRange(200000, 300000)),
            vmStorageSize: Math.floor(randomInRange(4000000000, 6000000000)),
            vmQueryLatency: randomInRange(10, 25),
            osDocuments: Math.floor(randomInRange(100000, 150000)),
            osHealth: 'green',
            osNodes: 1,
            kafkaTopics: 6,
            kafkaPartitions: 72,
            kafkaLag: Math.floor(randomInRange(0, 100))
        },
        services: [
            { name: 'VictoriaMetrics', status: 'up', port: 8428 },
            { name: 'OTEL Collector', status: 'up', port: 4317 },
            { name: 'Kafka', status: 'up', port: 9092 },
            { name: 'OpenSearch', status: 'up', port: 9200 },
            { name: 'OpenObserve', status: 'up', port: 5080 },
            { name: 'Grafana', status: 'up', port: 3000 }
        ],
        events: [
            { time: new Date(Date.now() - 120000), type: 'business', title: 'Production batch completed', desc: 'Batch #4521 - 150 units' },
            { time: new Date(Date.now() - 300000), type: 'tech', title: 'OTEL pipeline spike', desc: '120K metrics/sec processed' },
            { time: new Date(Date.now() - 480000), type: 'business', title: 'Quality check passed', desc: 'Product A - 99.2% quality' },
            { time: new Date(Date.now() - 600000), type: 'tech', title: 'Memory optimization', desc: 'VM GC completed - 2GB freed' },
            { time: new Date(Date.now() - 900000), type: 'business', title: 'Equipment maintenance', desc: 'Pump-003 scheduled check' }
        ]
    };
}

// =========================================
// UI Rendering
// =========================================

function updateUI(data) {
    state.data = data;
    state.lastUpdate = new Date();

    // Update timestamp
    document.getElementById('lastUpdateTime').textContent = formatTime(state.lastUpdate);

    // Update all views
    updateUnifiedView(data);
    updateBusinessView(data);
    updateTechView(data);
}

function updateUnifiedView(data) {
    // Business KPIs
    updateElement('oeeValue', data.business.oee.toFixed(1));
    updateElement('qualityValue', data.business.qualityRate.toFixed(1));
    updateElement('productionValue', formatNumber(data.business.productionToday));
    updateElement('alarmsValue', data.business.criticalAlarms);

    // Tech KPIs
    updateElement('metricsRateValue', formatNumber(data.tech.metricsRate));
    updateElement('logsRateValue', formatNumber(data.tech.logsRate));
    updateElement('latencyValue', data.tech.latencyP95.toFixed(0));
    updateElement('errorRateValue', data.tech.errorRate.toFixed(3));

    // Services Status
    renderServicesStatus(data.services);

    // Alarms
    renderAlarmList(data.business.alarms);

    // Event Timeline
    renderEventTimeline(data.events);
}

function updateBusinessView(data) {
    // OEE Components
    updateElement('availabilityValue', data.business.availability.toFixed(1) + '%');
    updateElement('performanceValue', data.business.performance.toFixed(1) + '%');
    updateElement('qualityBarValue', data.business.qualityRate.toFixed(1) + '%');

    document.getElementById('availabilityBar').style.width = data.business.availability + '%';
    document.getElementById('performanceBar').style.width = data.business.performance + '%';
    document.getElementById('qualityBar').style.width = data.business.qualityRate + '%';

    // Equipment Grid
    renderEquipmentGrid(data.business.equipment);
}

function updateTechView(data) {
    // Services Detail Grid
    renderServicesDetailGrid(data.services);

    // Storage Metrics
    updateElement('vmActiveSeries', formatNumber(data.tech.vmActiveSeries));
    updateElement('vmStorageSize', formatBytes(data.tech.vmStorageSize));
    updateElement('vmQueryLatency', data.tech.vmQueryLatency.toFixed(1) + ' ms');
    updateElement('osDocuments', formatNumber(data.tech.osDocuments));
    updateElement('osNodes', data.tech.osNodes);
    updateElement('kafkaTopics', data.tech.kafkaTopics);
    updateElement('kafkaPartitions', data.tech.kafkaPartitions);
    updateElement('kafkaLag', formatNumber(data.tech.kafkaLag));

    // Pipeline Stats
    renderPipelineStats(data);
}

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function renderServicesStatus(services) {
    const container = document.getElementById('servicesStatus');
    if (!container) return;

    container.innerHTML = services.map(service => `
        <div class="service-badge">
            <span class="status-dot ${service.status}"></span>
            <span class="service-name">${service.name}</span>
        </div>
    `).join('');
}

function renderServicesDetailGrid(services) {
    const container = document.getElementById('servicesDetailGrid');
    if (!container) return;

    const serviceIcons = {
        'VictoriaMetrics': 'VM',
        'OTEL Collector': 'OT',
        'Kafka': 'K',
        'OpenSearch': 'OS',
        'OpenObserve': 'OO',
        'Grafana': 'G'
    };

    container.innerHTML = services.map(service => `
        <div class="service-card ${service.status}">
            <div class="service-icon">${serviceIcons[service.name] || service.name[0]}</div>
            <div class="service-name">${service.name}</div>
            <div class="service-status">${service.status === 'up' ? 'Running' : 'Down'}</div>
            <div class="service-port">Port: ${service.port}</div>
        </div>
    `).join('');
}

function renderEquipmentGrid(equipment) {
    const container = document.getElementById('equipmentGrid');
    if (!container) return;

    container.innerHTML = equipment.map(eq => `
        <div class="equipment-card">
            <div class="equipment-header">
                <span class="equipment-name">${eq.name}</span>
                <span class="equipment-status ${eq.status}">${eq.status.toUpperCase()}</span>
            </div>
            <div class="equipment-metrics">
                <div class="equipment-metric">
                    <span class="label">Temperature</span>
                    <span class="value">${eq.temp.toFixed(1)}°C</span>
                </div>
                <div class="equipment-metric">
                    <span class="label">Pressure</span>
                    <span class="value">${eq.pressure.toFixed(2)} bar</span>
                </div>
                <div class="equipment-metric">
                    <span class="label">Power</span>
                    <span class="value">${eq.power.toFixed(0)} kW</span>
                </div>
                <div class="equipment-metric">
                    <span class="label">Vibration</span>
                    <span class="value">${randomInRange(0.5, 3).toFixed(1)} mm/s</span>
                </div>
            </div>
        </div>
    `).join('');
}

function renderAlarmList(alarms) {
    const container = document.getElementById('alarmList');
    if (!container) return;

    container.innerHTML = alarms.slice(0, 3).map(alarm => `
        <div class="alarm-item">
            <span class="alarm-severity ${alarm.severity}"></span>
            <span class="alarm-message">${alarm.message}</span>
        </div>
    `).join('');
}

function renderEventTimeline(events) {
    const container = document.getElementById('eventTimeline');
    if (!container) return;

    container.innerHTML = events.map(event => `
        <div class="timeline-event">
            <span class="event-time">${formatTime(event.time)}</span>
            <span class="event-icon ${event.type}">${event.type === 'business' ? 'B' : 'T'}</span>
            <div class="event-content">
                <div class="event-title">${event.title}</div>
                <div class="event-desc">${event.desc}</div>
            </div>
        </div>
    `).join('');
}

function renderPipelineStats(data) {
    const container = document.getElementById('pipelineStats');
    if (!container) return;

    container.innerHTML = `
        <div class="pipeline-stat">
            <div class="stat-value">${formatNumber(data.tech.metricsRate)}</div>
            <div class="stat-label">Metrics/sec</div>
        </div>
        <div class="pipeline-stat">
            <div class="stat-value">${formatNumber(data.tech.logsRate)}</div>
            <div class="stat-label">Logs/sec</div>
        </div>
        <div class="pipeline-stat">
            <div class="stat-value">${formatNumber(data.tech.tracesRate)}</div>
            <div class="stat-label">Traces/sec</div>
        </div>
        <div class="pipeline-stat">
            <div class="stat-value">${data.tech.latencyP95.toFixed(0)}ms</div>
            <div class="stat-label">P95 Latency</div>
        </div>
        <div class="pipeline-stat">
            <div class="stat-value">${formatBytes(data.tech.kafkaThroughput)}/s</div>
            <div class="stat-label">Kafka Throughput</div>
        </div>
        <div class="pipeline-stat">
            <div class="stat-value">${data.tech.errorRate.toFixed(3)}%</div>
            <div class="stat-label">Error Rate</div>
        </div>
    `;
}

// =========================================
// Simple Chart Rendering
// =========================================

function renderSimpleChart(containerId, data, color) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const width = container.offsetWidth;
    const height = container.offsetHeight;
    const points = data.length;
    const maxValue = Math.max(...data);
    const minValue = Math.min(...data);
    const range = maxValue - minValue || 1;

    const pathData = data.map((value, index) => {
        const x = (index / (points - 1)) * width;
        const y = height - ((value - minValue) / range) * (height * 0.8) - height * 0.1;
        return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
    }).join(' ');

    container.innerHTML = `
        <svg width="100%" height="100%" viewBox="0 0 ${width} ${height}">
            <defs>
                <linearGradient id="gradient-${containerId}" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:${color};stop-opacity:0.3" />
                    <stop offset="100%" style="stop-color:${color};stop-opacity:0" />
                </linearGradient>
            </defs>
            <path d="${pathData} L ${width} ${height} L 0 ${height} Z" fill="url(#gradient-${containerId})" />
            <path d="${pathData}" fill="none" stroke="${color}" stroke-width="2" />
        </svg>
    `;
}

// =========================================
// Initialization
// =========================================

async function init() {
    console.log('OOVMTEL Unified View initializing...');

    // Initialize view toggle
    initViewToggle();

    // Initial data fetch
    const data = await fetchMetrics();
    updateUI(data);

    // Set up auto-refresh
    setInterval(async () => {
        const data = await fetchMetrics();
        updateUI(data);
    }, CONFIG.refreshInterval);

    console.log('OOVMTEL Unified View initialized');
}

// Start the application
document.addEventListener('DOMContentLoaded', init);
