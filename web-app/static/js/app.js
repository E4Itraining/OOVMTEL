/**
 * OOVMTEL Unified Business-Tech View
 * Industrial Observability Platform
 *
 * Enhanced application JavaScript with real-time updates,
 * problems & impacts tracking, and smooth animations
 */

// Configuration
const CONFIG = {
    apiBaseUrl: '/api',
    wsUrl: `ws://${window.location.host}/ws`,
    refreshInterval: 10000, // 10 seconds fallback
    toastDuration: 5000,
    maxToasts: 5,
    sparklinePoints: 20,
    animations: true
};

// =========================================
// Multilingual Translations (FR/EN/NL)
// =========================================
const TRANSLATIONS = {
    fr: {
        // Navigation
        unifiedView: 'Vue Unifiée',
        businessView: 'Vue Business',
        techView: 'Vue Tech',
        tagline: "Plateforme d'Observabilité Industrielle",
        lastUpdate: 'Mise à jour:',

        // Business KPIs
        businessKPIs: 'KPIs Business',
        oee: 'Efficacité Globale des Équipements',
        target85: 'Objectif: 85%',
        qualityRate: 'Taux de Qualité',
        productionToday: 'Production du Jour',
        activeAlarms: 'Alarmes Actives',
        units: 'unités',
        critical: 'critiques',

        // Infrastructure
        infrastructureHealth: 'Santé Infrastructure',
        metricsIngestion: 'Ingestion Métriques',
        logsIngestion: 'Ingestion Logs',
        pipelineLatency: 'Latence Pipeline',
        errorRate: "Taux d'Erreur",

        // Sections
        problemsImpacts: 'Problèmes & Impacts',
        crossDomainInsights: 'Analyses Transversales',
        businessTechCorrelation: 'Corrélation Business-Tech',
        eventTimeline: 'Chronologie des Événements',

        // Business View
        productionQualityKPIs: 'KPIs Production & Qualité',
        oeeLabel: 'Efficacité Globale des Équipements (OEE)',
        worldClass: 'World Class: 85%+',
        availability: 'Disponibilité',
        performance: 'Performance',
        quality: 'Qualité',
        productionByProduct: 'Production par Produit',
        equipmentMonitoring: 'Surveillance des Équipements',
        processParameters: 'Paramètres Process',
        temperatureTrends: 'Tendances Température',
        pressureMonitoring: 'Surveillance Pression',
        powerConsumption: 'Consommation Électrique',
        vibrationAnalysis: 'Analyse Vibration',

        // Tech View
        serviceHealthOverview: 'Vue d\'Ensemble des Services',
        resourceUtilization: 'Utilisation Ressources',
        cpuUsage: 'Utilisation CPU',
        memoryUsage: 'Utilisation Mémoire',
        dataPipelineMetrics: 'Métriques Pipeline de Données',
        otelReceiverThroughput: 'Débit OTEL Receiver',
        otelExporterThroughput: 'Débit OTEL Exporter',
        kafkaMessagesPerSec: 'Messages Kafka/sec',
        vmWriteRate: 'Taux Écriture VictoriaMetrics',
        storageMetrics: 'Métriques Stockage',
        activeSeries: 'Séries Actives',
        storageSize: 'Taille Stockage',
        queryLatency: 'Latence Requêtes (P99)',
        documents: 'Documents',
        clusterHealth: 'Santé Cluster',
        nodes: 'Nœuds',
        topics: 'Topics',
        partitions: 'Partitions',
        consumerLag: 'Lag Consommateurs',

        // Time
        justNow: "à l'instant",
        secondsAgo: 'il y a {n}s',
        minutesAgo: 'il y a {n}min',
        hoursAgo: 'il y a {n}h',

        // Toast
        systemInitialized: 'Système initialisé',
        dashboardReady: 'Dashboard OOVMTEL prêt'
    },
    en: {
        // Navigation
        unifiedView: 'Unified View',
        businessView: 'Business View',
        techView: 'Tech View',
        tagline: 'Industrial Observability Platform',
        lastUpdate: 'Last update:',

        // Business KPIs
        businessKPIs: 'Business KPIs',
        oee: 'Overall Equipment Effectiveness',
        target85: 'Target: 85%',
        qualityRate: 'Quality Rate',
        productionToday: "Today's Production",
        activeAlarms: 'Active Alarms',
        units: 'units',
        critical: 'critical',

        // Infrastructure
        infrastructureHealth: 'Infrastructure Health',
        metricsIngestion: 'Metrics Ingestion',
        logsIngestion: 'Logs Ingestion',
        pipelineLatency: 'Pipeline Latency',
        errorRate: 'Error Rate',

        // Sections
        problemsImpacts: 'Problems & Impacts',
        crossDomainInsights: 'Cross-Domain Insights',
        businessTechCorrelation: 'Business-Tech Correlation',
        eventTimeline: 'Event Timeline',

        // Business View
        productionQualityKPIs: 'Production & Quality KPIs',
        oeeLabel: 'Overall Equipment Effectiveness (OEE)',
        worldClass: 'World Class: 85%+',
        availability: 'Availability',
        performance: 'Performance',
        quality: 'Quality',
        productionByProduct: 'Production by Product',
        equipmentMonitoring: 'Equipment Monitoring',
        processParameters: 'Process Parameters',
        temperatureTrends: 'Temperature Trends',
        pressureMonitoring: 'Pressure Monitoring',
        powerConsumption: 'Power Consumption',
        vibrationAnalysis: 'Vibration Analysis',

        // Tech View
        serviceHealthOverview: 'Service Health Overview',
        resourceUtilization: 'Resource Utilization',
        cpuUsage: 'CPU Usage',
        memoryUsage: 'Memory Usage',
        dataPipelineMetrics: 'Data Pipeline Metrics',
        otelReceiverThroughput: 'OTEL Receiver Throughput',
        otelExporterThroughput: 'OTEL Exporter Throughput',
        kafkaMessagesPerSec: 'Kafka Messages/sec',
        vmWriteRate: 'VictoriaMetrics Write Rate',
        storageMetrics: 'Storage Metrics',
        activeSeries: 'Active Series',
        storageSize: 'Storage Size',
        queryLatency: 'Query Latency (P99)',
        documents: 'Documents',
        clusterHealth: 'Cluster Health',
        nodes: 'Nodes',
        topics: 'Topics',
        partitions: 'Partitions',
        consumerLag: 'Consumer Lag',

        // Time
        justNow: 'just now',
        secondsAgo: '{n}s ago',
        minutesAgo: '{n}min ago',
        hoursAgo: '{n}h ago',

        // Toast
        systemInitialized: 'System initialized',
        dashboardReady: 'OOVMTEL Dashboard ready'
    },
    nl: {
        // Navigation
        unifiedView: 'Uniforme Weergave',
        businessView: 'Business Weergave',
        techView: 'Tech Weergave',
        tagline: 'Industrieel Observabiliteitsplatform',
        lastUpdate: 'Laatste update:',

        // Business KPIs
        businessKPIs: 'Business KPIs',
        oee: 'Algehele Apparatuur Effectiviteit',
        target85: 'Doel: 85%',
        qualityRate: 'Kwaliteitspercentage',
        productionToday: 'Productie Vandaag',
        activeAlarms: 'Actieve Alarmen',
        units: 'eenheden',
        critical: 'kritiek',

        // Infrastructure
        infrastructureHealth: 'Infrastructuur Gezondheid',
        metricsIngestion: 'Metriek Opname',
        logsIngestion: 'Log Opname',
        pipelineLatency: 'Pipeline Latentie',
        errorRate: 'Foutpercentage',

        // Sections
        problemsImpacts: 'Problemen & Impacts',
        crossDomainInsights: 'Cross-Domein Inzichten',
        businessTechCorrelation: 'Business-Tech Correlatie',
        eventTimeline: 'Gebeurtenis Tijdlijn',

        // Business View
        productionQualityKPIs: 'Productie & Kwaliteit KPIs',
        oeeLabel: 'Algehele Apparatuur Effectiviteit (OEE)',
        worldClass: 'World Class: 85%+',
        availability: 'Beschikbaarheid',
        performance: 'Prestatie',
        quality: 'Kwaliteit',
        productionByProduct: 'Productie per Product',
        equipmentMonitoring: 'Apparatuur Monitoring',
        processParameters: 'Proces Parameters',
        temperatureTrends: 'Temperatuur Trends',
        pressureMonitoring: 'Druk Monitoring',
        powerConsumption: 'Stroomverbruik',
        vibrationAnalysis: 'Trillingsanalyse',

        // Tech View
        serviceHealthOverview: 'Service Gezondheidsoverzicht',
        resourceUtilization: 'Resource Gebruik',
        cpuUsage: 'CPU Gebruik',
        memoryUsage: 'Geheugen Gebruik',
        dataPipelineMetrics: 'Data Pipeline Metrieken',
        otelReceiverThroughput: 'OTEL Ontvanger Doorvoer',
        otelExporterThroughput: 'OTEL Exporteur Doorvoer',
        kafkaMessagesPerSec: 'Kafka Berichten/sec',
        vmWriteRate: 'VictoriaMetrics Schrijfsnelheid',
        storageMetrics: 'Opslag Metrieken',
        activeSeries: 'Actieve Series',
        storageSize: 'Opslag Grootte',
        queryLatency: 'Query Latentie (P99)',
        documents: 'Documenten',
        clusterHealth: 'Cluster Gezondheid',
        nodes: 'Nodes',
        topics: 'Topics',
        partitions: 'Partities',
        consumerLag: 'Consumer Lag',

        // Time
        justNow: 'zojuist',
        secondsAgo: '{n}s geleden',
        minutesAgo: '{n}min geleden',
        hoursAgo: '{n}u geleden',

        // Toast
        systemInitialized: 'Systeem geinitialiseerd',
        dashboardReady: 'OOVMTEL Dashboard klaar'
    }
};

// Current language state
let currentLanguage = localStorage.getItem('oovmtel_language') || 'fr';

// =========================================
// Language Switcher Functions
// =========================================

function t(key) {
    return TRANSLATIONS[currentLanguage][key] || TRANSLATIONS['en'][key] || key;
}

function setLanguage(lang) {
    if (!TRANSLATIONS[lang]) return;

    currentLanguage = lang;
    localStorage.setItem('oovmtel_language', lang);
    document.documentElement.lang = lang;

    // Update all translatable elements
    updateTranslations();

    // Update language switcher UI
    updateLanguageSwitcherUI();
}

function updateTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const translation = t(key);
        if (translation) {
            el.textContent = translation;
        }
    });
}

function updateLanguageSwitcherUI() {
    const currentLangEl = document.getElementById('currentLang');
    if (currentLangEl) {
        currentLangEl.textContent = currentLanguage.toUpperCase();
    }

    document.querySelectorAll('.lang-option').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === currentLanguage);
    });
}

function initLanguageSwitcher() {
    const switcher = document.getElementById('languageSwitcher');
    const toggle = document.getElementById('langToggle');
    const dropdown = document.getElementById('langDropdown');

    if (!switcher || !toggle) return;

    // Toggle dropdown
    toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        switcher.classList.toggle('open');
    });

    // Language selection
    document.querySelectorAll('.lang-option').forEach(btn => {
        btn.addEventListener('click', () => {
            setLanguage(btn.dataset.lang);
            switcher.classList.remove('open');
        });
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!switcher.contains(e.target)) {
            switcher.classList.remove('open');
        }
    });

    // Initialize with current language
    setLanguage(currentLanguage);
}

// Application State
const state = {
    currentView: 'unified',
    lastUpdate: null,
    connectionType: 'polling', // 'websocket' | 'polling' | 'disconnected'
    websocket: null,
    previousData: null,
    data: {
        business: {},
        tech: {},
        services: []
    },
    history: {
        oee: [],
        metricsRate: [],
        logsRate: [],
        latency: [],
        production: [],
        quality: []
    },
    problems: []
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
    const localeMap = { fr: 'fr-FR', en: 'en-GB', nl: 'nl-NL' };
    return date.toLocaleTimeString(localeMap[currentLanguage] || 'fr-FR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
}

function formatTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 5) return t('justNow');
    if (seconds < 60) return t('secondsAgo').replace('{n}', seconds);
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return t('minutesAgo').replace('{n}', minutes);
    const hours = Math.floor(minutes / 60);
    return t('hoursAgo').replace('{n}', hours);
}

function randomInRange(min, max) {
    return Math.random() * (max - min) + min;
}

function getTrendDirection(current, previous) {
    if (!previous || current === previous) return 'neutral';
    return current > previous ? 'up' : 'down';
}

function getTrendPercentage(current, previous) {
    if (!previous || previous === 0) return 0;
    return ((current - previous) / previous * 100).toFixed(1);
}

// =========================================
// Toast Notifications
// =========================================

function showToast(type, title, message) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    // Limit number of toasts
    const existingToasts = container.querySelectorAll('.toast');
    if (existingToasts.length >= CONFIG.maxToasts) {
        existingToasts[0].remove();
    }

    const icons = {
        critical: '!',
        warning: '!',
        success: '✓',
        info: 'i'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${icons[type] || 'i'}</div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    // Auto-remove after duration
    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.add('hiding');
            setTimeout(() => toast.remove(), 300);
        }
    }, CONFIG.toastDuration);
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
// WebSocket Connection
// =========================================

function initWebSocket() {
    try {
        state.websocket = new WebSocket(CONFIG.wsUrl);

        state.websocket.onopen = () => {
            console.log('WebSocket connected');
            state.connectionType = 'websocket';
            updateConnectionStatus();
            showToast('success', 'Connexion temps réel', 'WebSocket connecté');
        };

        state.websocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                updateUI(data);
            } catch (error) {
                console.warn('Failed to parse WebSocket message:', error);
            }
        };

        state.websocket.onclose = () => {
            console.log('WebSocket disconnected, falling back to polling');
            state.connectionType = 'polling';
            updateConnectionStatus();
            // Retry connection after 5 seconds
            setTimeout(initWebSocket, 5000);
        };

        state.websocket.onerror = (error) => {
            console.warn('WebSocket error:', error);
            state.connectionType = 'polling';
            updateConnectionStatus();
        };
    } catch (error) {
        console.warn('WebSocket not available, using polling');
        state.connectionType = 'polling';
        updateConnectionStatus();
    }
}

function updateConnectionStatus() {
    const indicator = document.getElementById('refreshIndicator');
    const statusDot = document.getElementById('connectionStatus');
    const refreshText = indicator?.querySelector('.refresh-text');

    if (!indicator || !statusDot) return;

    indicator.classList.remove('disconnected');
    statusDot.classList.remove('websocket', 'polling', 'disconnected');

    switch (state.connectionType) {
        case 'websocket':
            statusDot.classList.add('websocket');
            statusDot.title = 'WebSocket actif';
            break;
        case 'polling':
            statusDot.classList.add('polling');
            statusDot.title = 'Mode polling';
            break;
        case 'disconnected':
            indicator.classList.add('disconnected');
            statusDot.classList.add('disconnected');
            if (refreshText) refreshText.textContent = 'HORS LIGNE';
            statusDot.title = 'Déconnecté';
            break;
    }
}

// =========================================
// Data Fetching
// =========================================

async function fetchMetrics() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/metrics`);
        if (response.ok) {
            state.connectionType = state.websocket?.readyState === 1 ? 'websocket' : 'polling';
            updateConnectionStatus();
            return await response.json();
        }
    } catch (error) {
        console.warn('API not available, using simulated data');
        state.connectionType = 'polling';
        updateConnectionStatus();
    }

    // Return simulated data if API is not available
    return generateSimulatedData();
}

function generateSimulatedData() {
    const now = new Date();
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
                { name: 'Reactor-001', status: 'running', temp: randomInRange(60, 80), pressure: randomInRange(4, 6), power: randomInRange(100, 150), vibration: randomInRange(0.5, 2) },
                { name: 'Mixer-002', status: 'running', temp: randomInRange(40, 60), pressure: randomInRange(2, 4), power: randomInRange(50, 80), vibration: randomInRange(0.3, 1.5) },
                { name: 'Pump-003', status: 'warning', temp: randomInRange(30, 50), pressure: randomInRange(3, 5), power: randomInRange(20, 40), vibration: randomInRange(2, 4) },
                { name: 'Furnace-004', status: 'running', temp: randomInRange(200, 300), pressure: randomInRange(1, 2), power: randomInRange(200, 300), vibration: randomInRange(0.2, 1) },
                { name: 'Conveyor-005', status: 'running', temp: randomInRange(25, 35), pressure: randomInRange(1, 2), power: randomInRange(30, 50), vibration: randomInRange(0.5, 1.5) },
                { name: 'Tank-006', status: 'stopped', temp: randomInRange(20, 30), pressure: randomInRange(1, 2), power: 0, vibration: 0 }
            ],
            productionByProduct: {
                'Product A': Math.floor(randomInRange(250, 350)),
                'Product B': Math.floor(randomInRange(200, 300)),
                'Product C': Math.floor(randomInRange(350, 450)),
                'Product D': Math.floor(randomInRange(280, 380))
            },
            alarms: [
                { severity: 'critical', message: 'Température élevée sur Reactor-001', time: new Date(now - 60000), source: 'SCADA' },
                { severity: 'warning', message: 'Alerte vibration sur Pump-003', time: new Date(now - 180000), source: 'MES' },
                { severity: 'warning', message: 'Maintenance prévue sur Mixer-002', time: new Date(now - 300000), source: 'PLM' }
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
            { name: 'VictoriaMetrics', status: 'up', port: 8428, latency: randomInRange(5, 15) },
            { name: 'OTEL Collector', status: 'up', port: 4317, latency: randomInRange(2, 8) },
            { name: 'Kafka', status: 'up', port: 9092, latency: randomInRange(3, 10) },
            { name: 'OpenSearch', status: 'up', port: 9200, latency: randomInRange(10, 25) },
            { name: 'OpenObserve', status: 'up', port: 5080, latency: randomInRange(5, 15) },
            { name: 'Grafana', status: 'up', port: 3000, latency: randomInRange(8, 20) }
        ],
        events: [
            { time: new Date(now - 120000), type: 'business', title: 'Batch de production terminé', desc: 'Batch #4521 - 150 unités' },
            { time: new Date(now - 300000), type: 'tech', title: 'Pic pipeline OTEL', desc: '120K métriques/sec traitées' },
            { time: new Date(now - 480000), type: 'business', title: 'Contrôle qualité réussi', desc: 'Product A - 99.2% qualité' },
            { time: new Date(now - 600000), type: 'tech', title: 'Optimisation mémoire', desc: 'VM GC terminé - 2GB libérés' },
            { time: new Date(now - 900000), type: 'business', title: 'Maintenance équipement', desc: 'Contrôle planifié Pump-003' }
        ]
    };
}

// =========================================
// Problems & Impacts Analysis
// =========================================

function analyzeProblemsAndImpacts(data) {
    const problems = [];

    // Check equipment with issues
    data.business.equipment?.forEach(eq => {
        if (eq.status === 'warning' || eq.status === 'stopped') {
            const impacts = [];

            if (eq.status === 'warning') {
                impacts.push({
                    type: 'business',
                    description: 'Risque de dégradation de la production',
                    value: '-5% à -10% OEE potentiel',
                    severity: 'negative'
                });
                impacts.push({
                    type: 'tech',
                    description: 'Augmentation des logs d\'alerte',
                    value: '+15% volume logs',
                    severity: 'negative'
                });
            }

            if (eq.status === 'stopped') {
                impacts.push({
                    type: 'business',
                    description: 'Arrêt de production sur la ligne',
                    value: `0 unités/heure`,
                    severity: 'negative'
                });
                impacts.push({
                    type: 'business',
                    description: 'Impact sur la disponibilité OEE',
                    value: '-3% à -8% disponibilité',
                    severity: 'negative'
                });
            }

            if (eq.vibration > 2.5) {
                impacts.push({
                    type: 'tech',
                    description: 'Vibrations anormales détectées',
                    value: `${eq.vibration.toFixed(1)} mm/s`,
                    severity: 'negative'
                });
            }

            if (eq.temp > 100) {
                impacts.push({
                    type: 'business',
                    description: 'Surchauffe nécessitant ralentissement',
                    value: `${eq.temp.toFixed(0)}°C`,
                    severity: 'negative'
                });
            }

            problems.push({
                id: `eq-${eq.name}`,
                severity: eq.status === 'stopped' ? 'critical' : 'warning',
                title: `${eq.name} - ${eq.status === 'stopped' ? 'Arrêté' : 'En alerte'}`,
                time: new Date(),
                source: 'SCADA',
                impacts
            });
        }
    });

    // Check alarms
    data.business.alarms?.forEach((alarm, idx) => {
        const impacts = [];

        if (alarm.severity === 'critical') {
            impacts.push({
                type: 'business',
                description: 'Intervention immédiate requise',
                value: 'Priorité haute',
                severity: 'negative'
            });
            impacts.push({
                type: 'tech',
                description: 'Génération d\'alertes système',
                value: 'Escalade automatique',
                severity: 'negative'
            });
        }

        problems.push({
            id: `alarm-${idx}`,
            severity: alarm.severity,
            title: alarm.message,
            time: alarm.time || new Date(),
            source: alarm.source || 'Système',
            impacts
        });
    });

    // Check tech issues
    if (data.tech.errorRate > 0.05) {
        problems.push({
            id: 'error-rate',
            severity: data.tech.errorRate > 0.1 ? 'critical' : 'warning',
            title: `Taux d'erreur élevé: ${(data.tech.errorRate * 100).toFixed(2)}%`,
            time: new Date(),
            source: 'OTEL',
            impacts: [
                {
                    type: 'tech',
                    description: 'Perte potentielle de données télémétriques',
                    value: `~${Math.floor(data.tech.metricsRate * data.tech.errorRate)} métriques/sec`,
                    severity: 'negative'
                },
                {
                    type: 'business',
                    description: 'Risque de données manquantes pour analyse',
                    value: 'Dégradation visibilité',
                    severity: 'negative'
                }
            ]
        });
    }

    if (data.tech.latencyP95 > 50) {
        problems.push({
            id: 'latency',
            severity: 'warning',
            title: `Latence élevée: ${data.tech.latencyP95.toFixed(0)}ms P95`,
            time: new Date(),
            source: 'Infrastructure',
            impacts: [
                {
                    type: 'tech',
                    description: 'Délai dans la collecte des métriques',
                    value: `+${(data.tech.latencyP95 - 30).toFixed(0)}ms vs normal`,
                    severity: 'negative'
                },
                {
                    type: 'business',
                    description: 'Décalage temps réel des dashboards',
                    value: 'Rafraîchissement retardé',
                    severity: 'negative'
                }
            ]
        });
    }

    // Sort by severity
    problems.sort((a, b) => {
        const order = { critical: 0, warning: 1, info: 2 };
        return order[a.severity] - order[b.severity];
    });

    return problems;
}

function renderProblemsAndImpacts(problems) {
    const container = document.getElementById('problemsImpactsContainer');
    const countBadge = document.getElementById('problemsCount');

    if (!container) return;

    // Update count badge
    const criticalCount = problems.filter(p => p.severity === 'critical').length;
    if (countBadge) {
        countBadge.textContent = problems.length;
        countBadge.className = `section-badge ${criticalCount > 0 ? 'critical' : 'warning'}`;
    }

    if (problems.length === 0) {
        container.innerHTML = `
            <div class="no-problems">
                <div class="no-problems-icon">✓</div>
                <div class="no-problems-text">Aucun problème détecté</div>
                <div class="no-problems-subtext">Tous les systèmes fonctionnent normalement</div>
            </div>
        `;
        return;
    }

    container.innerHTML = problems.map(problem => `
        <div class="problem-impact-card ${problem.severity}">
            <div class="problem-header">
                <div class="problem-icon ${problem.severity}">
                    ${problem.severity === 'critical' ? '!' : '⚠'}
                </div>
                <div class="problem-info">
                    <div class="problem-title">${problem.title}</div>
                    <div class="problem-meta">
                        <span class="problem-time">⏱ ${formatTimeAgo(problem.time)}</span>
                        <span class="problem-source">${problem.source}</span>
                    </div>
                </div>
            </div>
            <div class="impacts-container">
                <div class="impacts-grid">
                    ${problem.impacts.map(impact => `
                        <div class="impact-item">
                            <span class="impact-arrow">→</span>
                            <div class="impact-content">
                                <span class="impact-type ${impact.type}">${impact.type === 'business' ? 'BUSINESS' : 'TECH'}</span>
                                <div class="impact-description">${impact.description}</div>
                                <div class="impact-value ${impact.severity}">${impact.value}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

// =========================================
// Sparkline Charts
// =========================================

function updateHistory(key, value) {
    if (!state.history[key]) state.history[key] = [];
    state.history[key].push(value);
    if (state.history[key].length > CONFIG.sparklinePoints) {
        state.history[key].shift();
    }
}

function renderSparkline(containerId, data, color) {
    const container = document.getElementById(containerId);
    if (!container || data.length < 2) return;

    const width = 100;
    const height = 30;
    const maxValue = Math.max(...data);
    const minValue = Math.min(...data);
    const range = maxValue - minValue || 1;

    const points = data.map((value, index) => {
        const x = (index / (data.length - 1)) * width;
        const y = height - ((value - minValue) / range) * (height * 0.8) - height * 0.1;
        return `${x},${y}`;
    }).join(' ');

    container.innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
            <defs>
                <linearGradient id="grad-${containerId}" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:${color};stop-opacity:0.3"/>
                    <stop offset="100%" style="stop-color:${color};stop-opacity:0"/>
                </linearGradient>
            </defs>
            <polygon points="0,${height} ${points} ${width},${height}" fill="url(#grad-${containerId})"/>
            <polyline points="${points}" fill="none" stroke="${color}" stroke-width="1.5"/>
        </svg>
    `;
}

// =========================================
// UI Rendering
// =========================================

function updateUI(data) {
    const previousData = state.previousData;
    state.previousData = JSON.parse(JSON.stringify(data));
    state.data = data;
    state.lastUpdate = new Date();

    // Update timestamp
    document.getElementById('lastUpdateTime').textContent = formatTime(state.lastUpdate);

    // Update history for sparklines
    updateHistory('oee', data.business.oee);
    updateHistory('metricsRate', data.tech.metricsRate);
    updateHistory('logsRate', data.tech.logsRate);
    updateHistory('latency', data.tech.latencyP95);
    updateHistory('production', data.business.productionToday);
    updateHistory('quality', data.business.qualityRate);

    // Analyze problems and impacts
    const problems = analyzeProblemsAndImpacts(data);
    state.problems = problems;

    // Check for new critical problems
    if (previousData) {
        const prevProblems = analyzeProblemsAndImpacts(previousData);
        const newCritical = problems.filter(p =>
            p.severity === 'critical' &&
            !prevProblems.some(pp => pp.id === p.id)
        );
        newCritical.forEach(p => {
            showToast('critical', 'Nouveau problème critique', p.title);
        });
    }

    // Update all views
    updateUnifiedView(data, previousData);
    updateBusinessView(data, previousData);
    updateTechView(data, previousData);

    // Render problems and impacts
    renderProblemsAndImpacts(problems);
}

function updateUnifiedView(data, previousData) {
    // Business KPIs with trends
    updateElementWithTrend('oeeValue', data.business.oee.toFixed(1),
        previousData?.business?.oee, true);
    updateElementWithTrend('qualityValue', data.business.qualityRate.toFixed(1),
        previousData?.business?.qualityRate, true);
    updateElementWithTrend('productionValue', formatNumber(data.business.productionToday),
        previousData?.business?.productionToday, true);
    updateElement('alarmsValue', data.business.criticalAlarms);

    // Tech KPIs with trends
    updateElementWithTrend('metricsRateValue', formatNumber(data.tech.metricsRate),
        previousData?.tech?.metricsRate, true);
    updateElementWithTrend('logsRateValue', formatNumber(data.tech.logsRate),
        previousData?.tech?.logsRate, true);
    updateElementWithTrend('latencyValue', data.tech.latencyP95.toFixed(0),
        previousData?.tech?.latencyP95, false); // Lower is better for latency
    updateElementWithTrend('errorRateValue', data.tech.errorRate.toFixed(3),
        previousData?.tech?.errorRate, false);

    // Services Status
    renderServicesStatus(data.services);

    // Alarms
    renderAlarmList(data.business.alarms);

    // Event Timeline
    renderEventTimeline(data.events);

    // Sparklines in trend areas
    renderSparkline('oeeChart', state.history.oee, '#3b82f6');
    renderSparkline('qualityTrend', state.history.quality, '#10b981');
    renderSparkline('productionTrend', state.history.production, '#8b5cf6');
}

function updateBusinessView(data, previousData) {
    // OEE Components
    updateElement('availabilityValue', data.business.availability.toFixed(1) + '%');
    updateElement('performanceValue', data.business.performance.toFixed(1) + '%');
    updateElement('qualityBarValue', data.business.qualityRate.toFixed(1) + '%');

    // Animate progress bars
    animateProgressBar('availabilityBar', data.business.availability);
    animateProgressBar('performanceBar', data.business.performance);
    animateProgressBar('qualityBar', data.business.qualityRate);

    // Equipment Grid
    renderEquipmentGrid(data.business.equipment);
}

function updateTechView(data, previousData) {
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
        if (element.textContent !== String(value)) {
            element.textContent = value;
            element.classList.add('value-changed');
            setTimeout(() => element.classList.remove('value-changed'), 500);
        }
    }
}

function updateElementWithTrend(id, value, previousValue, higherIsBetter = true) {
    const element = document.getElementById(id);
    if (!element) return;

    const numValue = parseFloat(String(value).replace(/[^\d.-]/g, ''));
    const numPrevious = previousValue ? parseFloat(String(previousValue)) : null;

    if (element.textContent !== String(value)) {
        element.textContent = value;

        if (numPrevious !== null && numValue !== numPrevious) {
            const increased = numValue > numPrevious;
            const isGood = higherIsBetter ? increased : !increased;
            element.classList.add(isGood ? 'value-increased' : 'value-decreased');
            setTimeout(() => {
                element.classList.remove('value-increased', 'value-decreased');
            }, 500);
        }
    }
}

function animateProgressBar(id, value) {
    const bar = document.getElementById(id);
    if (bar) {
        bar.style.width = value + '%';
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
            <div class="service-status">${service.status === 'up' ? 'En ligne' : 'Hors ligne'}</div>
            <div class="service-port">Port: ${service.port}</div>
            ${service.latency ? `<div class="service-latency">${service.latency.toFixed(0)}ms</div>` : ''}
        </div>
    `).join('');
}

function renderEquipmentGrid(equipment) {
    const container = document.getElementById('equipmentGrid');
    if (!container) return;

    const statusLabels = {
        running: 'EN MARCHE',
        warning: 'ALERTE',
        stopped: 'ARRÊTÉ'
    };

    container.innerHTML = equipment.map(eq => `
        <div class="equipment-card">
            <div class="equipment-header">
                <span class="equipment-name">${eq.name}</span>
                <span class="equipment-status ${eq.status}">${statusLabels[eq.status] || eq.status.toUpperCase()}</span>
            </div>
            <div class="equipment-metrics">
                <div class="equipment-metric">
                    <span class="label">Température</span>
                    <span class="value ${eq.temp > 100 ? 'text-danger' : ''}">${eq.temp.toFixed(1)}°C</span>
                </div>
                <div class="equipment-metric">
                    <span class="label">Pression</span>
                    <span class="value">${eq.pressure.toFixed(2)} bar</span>
                </div>
                <div class="equipment-metric">
                    <span class="label">Puissance</span>
                    <span class="value">${eq.power.toFixed(0)} kW</span>
                </div>
                <div class="equipment-metric">
                    <span class="label">Vibration</span>
                    <span class="value ${eq.vibration > 2.5 ? 'text-warning' : ''}">${eq.vibration.toFixed(1)} mm/s</span>
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
            <div class="stat-label">Métriques/sec</div>
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
            <div class="stat-label">Latence P95</div>
        </div>
        <div class="pipeline-stat">
            <div class="stat-value">${formatBytes(data.tech.kafkaThroughput)}/s</div>
            <div class="stat-label">Débit Kafka</div>
        </div>
        <div class="pipeline-stat">
            <div class="stat-value">${data.tech.errorRate.toFixed(3)}%</div>
            <div class="stat-label">Taux d'erreur</div>
        </div>
    `;
}

// =========================================
// Time Ago Updater
// =========================================

function startTimeAgoUpdater() {
    setInterval(() => {
        const updateAgoEl = document.getElementById('updateAgo');
        if (updateAgoEl && state.lastUpdate) {
            updateAgoEl.textContent = formatTimeAgo(state.lastUpdate);
        }
    }, 1000);
}

// =========================================
// Initialization
// =========================================

async function init() {
    console.log('OOVMTEL Unified View initializing...');

    // Initialize language switcher
    initLanguageSwitcher();

    // Initialize view toggle
    initViewToggle();

    // Initialize WebSocket for real-time updates
    initWebSocket();

    // Start time ago updater
    startTimeAgoUpdater();

    // Initial data fetch
    const data = await fetchMetrics();
    updateUI(data);

    // Set up auto-refresh as fallback
    setInterval(async () => {
        // Only poll if WebSocket is not connected
        if (state.connectionType !== 'websocket') {
            const data = await fetchMetrics();
            updateUI(data);
        }
    }, CONFIG.refreshInterval);

    console.log('OOVMTEL Unified View initialized');
    showToast('info', t('systemInitialized'), t('dashboardReady'));
}

// Start the application
document.addEventListener('DOMContentLoaded', init);
