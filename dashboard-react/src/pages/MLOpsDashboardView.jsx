import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  CircuitBoard,
  Database,
  Activity,
  Cpu,
  GitBranch,
  Layers,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ChevronRight,
  ChevronDown,
  RefreshCw,
  Download,
  Eye,
  Target,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Zap,
  Server,
  HardDrive,
  Network,
  Play,
  Pause,
  RotateCcw,
  LineChart,
  Brain,
  Sparkles,
  Gauge,
  Timer,
  AlertCircle,
  Info,
  Box,
  Workflow,
  Binary,
  Sigma,
  FileCode,
  TestTube,
  Shield
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { TimeSeriesChart, DonutChart, BarChartComponent, AreaChartComponent } from '../components/ui/Charts'
import { StatusBadge, HealthIndicator } from '../components/ui/Status'
import { RadialGauge, LinearGauge, SemiCircleGauge } from '../components/ui/Gauge'

// ML Models inventory
const mlModels = [
  {
    id: 'model-001',
    name: 'Maintenance Prédictive v2.3',
    type: 'Time Series Forecasting',
    framework: 'TensorFlow',
    status: 'production',
    version: '2.3.1',
    accuracy: 94.2,
    latencyP50: 45,
    latencyP99: 120,
    throughput: 1250,
    drift: 'none',
    lastTrained: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    dataQuality: 98
  },
  {
    id: 'model-002',
    name: 'Contrôle Qualité Vision',
    type: 'Image Classification',
    framework: 'PyTorch',
    status: 'production',
    version: '1.8.0',
    accuracy: 97.8,
    latencyP50: 85,
    latencyP99: 180,
    throughput: 450,
    drift: 'low',
    lastTrained: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000),
    dataQuality: 95
  },
  {
    id: 'model-003',
    name: 'Détection Anomalies Réseau',
    type: 'Anomaly Detection',
    framework: 'Scikit-learn',
    status: 'production',
    version: '3.1.2',
    accuracy: 92.5,
    latencyP50: 15,
    latencyP99: 45,
    throughput: 5200,
    drift: 'medium',
    lastTrained: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    dataQuality: 88
  },
  {
    id: 'model-004',
    name: 'Optimisation Énergie',
    type: 'Reinforcement Learning',
    framework: 'TensorFlow',
    status: 'staging',
    version: '0.9.5',
    accuracy: 89.3,
    latencyP50: 220,
    latencyP99: 450,
    throughput: 120,
    drift: 'none',
    lastTrained: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    dataQuality: 96
  }
]

// Data pipelines
const dataPipelines = [
  {
    id: 'pipeline-001',
    name: 'ETL Production Metrics',
    status: 'running',
    frequency: '5min',
    lastRun: new Date(Date.now() - 3 * 60 * 1000),
    nextRun: new Date(Date.now() + 2 * 60 * 1000),
    successRate: 99.8,
    avgDuration: 45,
    recordsProcessed: 125000
  },
  {
    id: 'pipeline-002',
    name: 'Feature Store Update',
    status: 'running',
    frequency: '1h',
    lastRun: new Date(Date.now() - 25 * 60 * 1000),
    nextRun: new Date(Date.now() + 35 * 60 * 1000),
    successRate: 99.5,
    avgDuration: 180,
    recordsProcessed: 450000
  },
  {
    id: 'pipeline-003',
    name: 'Training Data Prep',
    status: 'idle',
    frequency: 'daily',
    lastRun: new Date(Date.now() - 8 * 60 * 60 * 1000),
    nextRun: new Date(Date.now() + 16 * 60 * 60 * 1000),
    successRate: 98.2,
    avgDuration: 3600,
    recordsProcessed: 2500000
  },
  {
    id: 'pipeline-004',
    name: 'Real-time Inference Log',
    status: 'running',
    frequency: 'continuous',
    lastRun: new Date(Date.now() - 1000),
    nextRun: null,
    successRate: 99.9,
    avgDuration: 5,
    recordsProcessed: 85000000
  }
]

// Data quality metrics
const dataQualityMetrics = {
  overall: 94.5,
  dimensions: [
    { name: 'Complétude', score: 98, status: 'good' },
    { name: 'Exactitude', score: 95, status: 'good' },
    { name: 'Cohérence', score: 92, status: 'warning' },
    { name: 'Fraîcheur', score: 96, status: 'good' },
    { name: 'Unicité', score: 91, status: 'warning' },
    { name: 'Validité', score: 97, status: 'good' }
  ],
  issues: [
    { type: 'missing_values', count: 1245, severity: 'low', table: 'sensor_readings' },
    { type: 'outliers', count: 87, severity: 'medium', table: 'production_metrics' },
    { type: 'duplicates', count: 23, severity: 'low', table: 'equipment_logs' }
  ]
}

// Model drift alerts
const driftAlerts = [
  {
    id: 'drift-001',
    model: 'Détection Anomalies Réseau',
    type: 'data_drift',
    severity: 'medium',
    feature: 'network_traffic_volume',
    driftScore: 0.42,
    detectedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    status: 'investigating'
  },
  {
    id: 'drift-002',
    model: 'Contrôle Qualité Vision',
    type: 'concept_drift',
    severity: 'low',
    feature: 'image_brightness_distribution',
    driftScore: 0.18,
    detectedAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
    status: 'monitoring'
  }
]

// Feature store stats
const featureStoreStats = {
  totalFeatures: 1247,
  activeFeatures: 892,
  featureGroups: 45,
  freshnessScore: 96,
  topFeatures: [
    { name: 'equipment_temperature_avg_1h', usage: 98, freshness: '5min' },
    { name: 'production_rate_rolling_24h', usage: 95, freshness: '15min' },
    { name: 'defect_rate_by_shift', usage: 92, freshness: '1h' },
    { name: 'energy_consumption_pattern', usage: 88, freshness: '5min' },
    { name: 'maintenance_prediction_score', usage: 85, freshness: '30min' }
  ]
}

// AI Observability metrics
const aiObservability = {
  totalInferences: 12450000,
  avgLatency: 52,
  errorRate: 0.02,
  throughput: 2500,
  costPerInference: 0.0003,
  breakdown: {
    preprocessing: 15,
    inference: 28,
    postprocessing: 9
  }
}

// Generate model performance trend
const generateModelPerformanceTrend = () => {
  const data = []
  for (let i = 29; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    data.push({
      time: date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }),
      accuracy: 92 + Math.random() * 4,
      latency: 45 + Math.random() * 20,
      throughput: 1100 + Math.random() * 300
    })
  }
  return data
}

// Generate inference distribution
const generateInferenceDistribution = () => {
  const data = []
  for (let i = 23; i >= 0; i--) {
    data.push({
      time: `${23 - i}:00`,
      inferences: Math.floor(400000 + Math.random() * 200000)
    })
  }
  return data
}

// Model type distribution
const modelTypeDistribution = [
  { name: 'Classification', value: 35, color: '#3b82f6' },
  { name: 'Regression', value: 25, color: '#22c55e' },
  { name: 'Anomaly Detection', value: 20, color: '#f59e0b' },
  { name: 'Time Series', value: 15, color: '#8b5cf6' },
  { name: 'NLP', value: 5, color: '#ec4899' }
]

// Model Card Component
function ModelCard({ model, isExpanded, onToggle }) {
  const statusColors = {
    production: 'border-green-500/30 hover:border-green-500/50',
    staging: 'border-blue-500/30 hover:border-blue-500/50',
    development: 'border-yellow-500/30 hover:border-yellow-500/50',
    deprecated: 'border-gray-500/30 hover:border-gray-500/50'
  }

  const driftColors = {
    none: 'text-green-400',
    low: 'text-yellow-400',
    medium: 'text-orange-400',
    high: 'text-red-400'
  }

  return (
    <motion.div
      className={`rounded-xl border bg-industrial-card/50 ${statusColors[model.status]} transition-all duration-300`}
      layout
    >
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center">
            <Brain className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-white">{model.name}</h3>
              <span className="px-2 py-0.5 rounded text-xs bg-white/10 text-gray-400">
                v{model.version}
              </span>
            </div>
            <p className="text-sm text-gray-400">{model.type} • {model.framework}</p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="hidden md:flex items-center gap-6">
            <div className="text-center">
              <p className="text-lg font-semibold text-white">{model.accuracy}%</p>
              <p className="text-xs text-gray-500">Accuracy</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-semibold text-white">{model.latencyP50}ms</p>
              <p className="text-xs text-gray-500">Latence P50</p>
            </div>
            <div className="text-center">
              <p className={`text-sm font-semibold ${driftColors[model.drift]}`}>
                {model.drift === 'none' ? 'Stable' : model.drift.charAt(0).toUpperCase() + model.drift.slice(1) + ' drift'}
              </p>
              <p className="text-xs text-gray-500">Drift</p>
            </div>
          </div>
          <span className={`px-2 py-1 rounded text-xs ${
            model.status === 'production' ? 'bg-green-500/20 text-green-400' :
            model.status === 'staging' ? 'bg-blue-500/20 text-blue-400' :
            'bg-yellow-500/20 text-yellow-400'
          }`}>
            {model.status}
          </span>
          <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
        </div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 pt-2 border-t border-industrial-border/50">
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                <div className="p-3 rounded-lg bg-industrial-darker/50">
                  <p className="text-xs text-gray-500">Accuracy</p>
                  <p className="text-lg font-semibold text-green-400">{model.accuracy}%</p>
                </div>
                <div className="p-3 rounded-lg bg-industrial-darker/50">
                  <p className="text-xs text-gray-500">Latence P50</p>
                  <p className="text-lg font-semibold text-white">{model.latencyP50}ms</p>
                </div>
                <div className="p-3 rounded-lg bg-industrial-darker/50">
                  <p className="text-xs text-gray-500">Latence P99</p>
                  <p className="text-lg font-semibold text-white">{model.latencyP99}ms</p>
                </div>
                <div className="p-3 rounded-lg bg-industrial-darker/50">
                  <p className="text-xs text-gray-500">Throughput</p>
                  <p className="text-lg font-semibold text-white">{model.throughput}/s</p>
                </div>
                <div className="p-3 rounded-lg bg-industrial-darker/50">
                  <p className="text-xs text-gray-500">Data Quality</p>
                  <p className="text-lg font-semibold text-cyan-400">{model.dataQuality}%</p>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Entraîné: {model.lastTrained.toLocaleDateString('fr-FR')}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button className="px-3 py-1.5 rounded-lg bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 transition-colors text-sm flex items-center gap-1">
                    <Eye className="w-4 h-4" />
                    Monitoring
                  </button>
                  <button className="px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 transition-colors text-sm flex items-center gap-1">
                    <RotateCcw className="w-4 h-4" />
                    Retrain
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Pipeline Card Component
function PipelineCard({ pipeline }) {
  const statusColors = {
    running: 'bg-green-500',
    idle: 'bg-gray-500',
    failed: 'bg-red-500',
    paused: 'bg-yellow-500'
  }

  return (
    <div className="p-4 rounded-xl border border-industrial-border bg-industrial-card/50">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`w-2 h-2 rounded-full ${statusColors[pipeline.status]} ${pipeline.status === 'running' ? 'animate-pulse' : ''}`} />
          <div>
            <h4 className="font-medium text-white">{pipeline.name}</h4>
            <p className="text-xs text-gray-500">{pipeline.frequency}</p>
          </div>
        </div>
        <span className={`px-2 py-1 rounded text-xs ${
          pipeline.status === 'running' ? 'bg-green-500/20 text-green-400' :
          pipeline.status === 'idle' ? 'bg-gray-500/20 text-gray-400' :
          pipeline.status === 'failed' ? 'bg-red-500/20 text-red-400' :
          'bg-yellow-500/20 text-yellow-400'
        }`}>
          {pipeline.status}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="p-2 rounded-lg bg-industrial-darker/50">
          <p className="text-sm font-semibold text-white">{pipeline.successRate}%</p>
          <p className="text-[10px] text-gray-500">Success</p>
        </div>
        <div className="p-2 rounded-lg bg-industrial-darker/50">
          <p className="text-sm font-semibold text-white">{pipeline.avgDuration}s</p>
          <p className="text-[10px] text-gray-500">Avg Duration</p>
        </div>
        <div className="p-2 rounded-lg bg-industrial-darker/50">
          <p className="text-sm font-semibold text-white">{(pipeline.recordsProcessed / 1000000).toFixed(1)}M</p>
          <p className="text-[10px] text-gray-500">Records</p>
        </div>
      </div>
    </div>
  )
}

// Drift Alert Card
function DriftAlertCard({ alert }) {
  const severityColors = {
    low: 'border-yellow-500/50 bg-yellow-500/5',
    medium: 'border-orange-500/50 bg-orange-500/5',
    high: 'border-red-500/50 bg-red-500/5'
  }

  return (
    <div className={`p-4 rounded-xl border ${severityColors[alert.severity]}`}>
      <div className="flex items-start justify-between mb-2">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={`px-2 py-0.5 rounded text-xs ${
              alert.type === 'data_drift' ? 'bg-blue-500/20 text-blue-400' :
              'bg-purple-500/20 text-purple-400'
            }`}>
              {alert.type === 'data_drift' ? 'Data Drift' : 'Concept Drift'}
            </span>
            <span className={`px-2 py-0.5 rounded text-xs ${
              alert.severity === 'low' ? 'bg-yellow-500/20 text-yellow-400' :
              alert.severity === 'medium' ? 'bg-orange-500/20 text-orange-400' :
              'bg-red-500/20 text-red-400'
            }`}>
              {alert.severity}
            </span>
          </div>
          <h4 className="font-medium text-white">{alert.model}</h4>
          <p className="text-sm text-gray-400">Feature: {alert.feature}</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-white">{(alert.driftScore * 100).toFixed(0)}%</p>
          <p className="text-xs text-gray-500">Drift Score</p>
        </div>
      </div>
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>Détecté: {alert.detectedAt.toLocaleTimeString('fr-FR')}</span>
        <span className={`px-2 py-0.5 rounded ${
          alert.status === 'investigating' ? 'bg-blue-500/20 text-blue-400' :
          'bg-gray-500/20 text-gray-400'
        }`}>
          {alert.status}
        </span>
      </div>
    </div>
  )
}

function MLOpsDashboardView() {
  const { t } = useI18n()
  const [activeTab, setActiveTab] = useState('overview')
  const [expandedModel, setExpandedModel] = useState(null)

  const performanceTrend = generateModelPerformanceTrend()
  const inferenceDistribution = generateInferenceDistribution()

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: Eye },
    { id: 'models', label: 'Modèles', icon: Brain },
    { id: 'pipelines', label: 'Pipelines', icon: Workflow },
    { id: 'quality', label: 'Data Quality', icon: Shield },
    { id: 'observability', label: 'Observabilité IA', icon: Activity }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center">
              <CircuitBoard className="w-5 h-5 text-white" />
            </div>
            Dashboard Data & MLOps
          </h1>
          <p className="text-gray-400 mt-1">
            Monitoring IA, pipelines de données et observabilité des modèles ML
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn btn-ghost flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Actualiser
          </button>
          <button className="btn btn-ghost flex items-center gap-2">
            <Download className="w-4 h-4" />
            Rapport
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all
                ${activeTab === tab.id
                  ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                  : 'bg-industrial-card/50 text-gray-400 border border-industrial-border hover:text-white'
                }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        <MetricCard
          label="Modèles prod"
          value={mlModels.filter(m => m.status === 'production').length}
          icon={Brain}
          color="purple"
        />
        <MetricCard
          label="Inférences/jour"
          value={`${(aiObservability.totalInferences / 1000000).toFixed(1)}M`}
          icon={Zap}
          color="cyan"
        />
        <MetricCard
          label="Latence P50"
          value={aiObservability.avgLatency}
          unit="ms"
          icon={Timer}
          color="green"
        />
        <MetricCard
          label="Error Rate"
          value={aiObservability.errorRate}
          unit="%"
          icon={AlertTriangle}
          color={aiObservability.errorRate < 0.1 ? 'green' : 'yellow'}
        />
        <MetricCard
          label="Data Quality"
          value={dataQualityMetrics.overall}
          unit="%"
          icon={Shield}
          color={dataQualityMetrics.overall >= 90 ? 'green' : 'yellow'}
        />
        <MetricCard
          label="Drift Alerts"
          value={driftAlerts.length}
          icon={AlertCircle}
          color={driftAlerts.filter(d => d.severity === 'high').length > 0 ? 'red' : 'yellow'}
        />
        <MetricCard
          label="Features"
          value={featureStoreStats.activeFeatures}
          icon={Box}
          color="blue"
        />
      </div>

      {activeTab === 'overview' && (
        <>
          {/* Models & Drift */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader
                title="Modèles en production"
                subtitle="Performance et statut des modèles ML"
                icon={Brain}
              />
              <CardBody>
                <div className="space-y-3">
                  {mlModels.filter(m => m.status === 'production').map((model) => (
                    <ModelCard
                      key={model.id}
                      model={model}
                      isExpanded={expandedModel === model.id}
                      onToggle={() => setExpandedModel(expandedModel === model.id ? null : model.id)}
                    />
                  ))}
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader
                title="Alertes Drift"
                subtitle="Détection de dérive des modèles"
                icon={AlertTriangle}
              />
              <CardBody>
                <div className="space-y-3">
                  {driftAlerts.map((alert) => (
                    <DriftAlertCard key={alert.id} alert={alert} />
                  ))}
                  {driftAlerts.length === 0 && (
                    <div className="p-4 text-center text-gray-500">
                      <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-green-400" />
                      <p>Aucune alerte de drift active</p>
                    </div>
                  )}
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Performance & Pipelines */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader
                title="Performance des modèles"
                subtitle="Évolution sur 30 jours"
                icon={TrendingUp}
              />
              <CardBody>
                <div className="h-64">
                  <TimeSeriesChart
                    data={performanceTrend}
                    lines={[
                      { key: 'accuracy', color: '#22c55e', name: 'Accuracy (%)' },
                      { key: 'latency', color: '#3b82f6', name: 'Latence (ms)' }
                    ]}
                  />
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader
                title="Pipelines de données"
                subtitle="Statut des pipelines actifs"
                icon={Workflow}
              />
              <CardBody>
                <div className="grid grid-cols-2 gap-3">
                  {dataPipelines.map((pipeline) => (
                    <PipelineCard key={pipeline.id} pipeline={pipeline} />
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>
        </>
      )}

      {activeTab === 'models' && (
        <Card>
          <CardHeader
            title="Inventaire des modèles"
            subtitle="Tous les modèles ML déployés"
            icon={Brain}
          />
          <CardBody>
            <div className="space-y-3">
              {mlModels.map((model) => (
                <ModelCard
                  key={model.id}
                  model={model}
                  isExpanded={expandedModel === model.id}
                  onToggle={() => setExpandedModel(expandedModel === model.id ? null : model.id)}
                />
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {activeTab === 'pipelines' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {dataPipelines.map((pipeline) => (
            <Card key={pipeline.id}>
              <CardBody>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      pipeline.status === 'running' ? 'bg-green-500/20' :
                      pipeline.status === 'idle' ? 'bg-gray-500/20' : 'bg-red-500/20'
                    }`}>
                      <Workflow className={`w-5 h-5 ${
                        pipeline.status === 'running' ? 'text-green-400' :
                        pipeline.status === 'idle' ? 'text-gray-400' : 'text-red-400'
                      }`} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white">{pipeline.name}</h3>
                      <p className="text-sm text-gray-400">Fréquence: {pipeline.frequency}</p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-lg text-sm ${
                    pipeline.status === 'running' ? 'bg-green-500/20 text-green-400' :
                    pipeline.status === 'idle' ? 'bg-gray-500/20 text-gray-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {pipeline.status}
                  </span>
                </div>

                <div className="grid grid-cols-4 gap-4">
                  <div className="p-3 rounded-lg bg-industrial-darker/50 text-center">
                    <p className="text-xl font-bold text-white">{pipeline.successRate}%</p>
                    <p className="text-xs text-gray-500">Success Rate</p>
                  </div>
                  <div className="p-3 rounded-lg bg-industrial-darker/50 text-center">
                    <p className="text-xl font-bold text-white">{pipeline.avgDuration}s</p>
                    <p className="text-xs text-gray-500">Durée moy.</p>
                  </div>
                  <div className="p-3 rounded-lg bg-industrial-darker/50 text-center">
                    <p className="text-xl font-bold text-white">{(pipeline.recordsProcessed / 1000000).toFixed(1)}M</p>
                    <p className="text-xs text-gray-500">Records</p>
                  </div>
                  <div className="p-3 rounded-lg bg-industrial-darker/50 text-center">
                    <p className="text-sm font-medium text-white">
                      {pipeline.lastRun.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                    <p className="text-xs text-gray-500">Last Run</p>
                  </div>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      {activeTab === 'quality' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader
              title="Score de qualité des données"
              subtitle="Dimensions de qualité"
              icon={Shield}
            />
            <CardBody>
              <div className="flex flex-col items-center mb-6">
                <SemiCircleGauge
                  value={dataQualityMetrics.overall}
                  max={100}
                  label="Data Quality Score"
                  color={dataQualityMetrics.overall >= 90 ? '#22c55e' : dataQualityMetrics.overall >= 75 ? '#eab308' : '#ef4444'}
                />
              </div>
              <div className="space-y-3">
                {dataQualityMetrics.dimensions.map((dim) => (
                  <div key={dim.name}>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-400">{dim.name}</span>
                      <span className={`text-sm font-medium ${
                        dim.status === 'good' ? 'text-green-400' : 'text-yellow-400'
                      }`}>
                        {dim.score}%
                      </span>
                    </div>
                    <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          dim.status === 'good' ? 'bg-green-500' : 'bg-yellow-500'
                        }`}
                        style={{ width: `${dim.score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="Problèmes détectés"
              subtitle="Issues de qualité à traiter"
              icon={AlertTriangle}
            />
            <CardBody>
              <div className="space-y-3">
                {dataQualityMetrics.issues.map((issue, idx) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-xl border ${
                      issue.severity === 'high' ? 'border-red-500/50 bg-red-500/5' :
                      issue.severity === 'medium' ? 'border-yellow-500/50 bg-yellow-500/5' :
                      'border-gray-500/50 bg-gray-500/5'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-white capitalize">{issue.type.replace('_', ' ')}</p>
                        <p className="text-sm text-gray-400">Table: {issue.table}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xl font-bold text-white">{issue.count}</p>
                        <p className="text-xs text-gray-500">occurrences</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>
      )}

      {activeTab === 'observability' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-1">
            <CardHeader
              title="Métriques d'inférence"
              subtitle="Performance globale IA"
              icon={Zap}
            />
            <CardBody>
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/30">
                  <p className="text-3xl font-bold text-white">{(aiObservability.totalInferences / 1000000).toFixed(1)}M</p>
                  <p className="text-sm text-gray-400">Inférences aujourd'hui</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-industrial-darker/50 text-center">
                    <p className="text-lg font-bold text-white">{aiObservability.avgLatency}ms</p>
                    <p className="text-xs text-gray-500">Latence P50</p>
                  </div>
                  <div className="p-3 rounded-lg bg-industrial-darker/50 text-center">
                    <p className="text-lg font-bold text-white">{aiObservability.throughput}/s</p>
                    <p className="text-xs text-gray-500">Throughput</p>
                  </div>
                  <div className="p-3 rounded-lg bg-industrial-darker/50 text-center">
                    <p className="text-lg font-bold text-green-400">{aiObservability.errorRate}%</p>
                    <p className="text-xs text-gray-500">Error Rate</p>
                  </div>
                  <div className="p-3 rounded-lg bg-industrial-darker/50 text-center">
                    <p className="text-lg font-bold text-white">${aiObservability.costPerInference}</p>
                    <p className="text-xs text-gray-500">Cost/inférence</p>
                  </div>
                </div>

                <div>
                  <p className="text-xs text-gray-500 uppercase mb-2">Breakdown latence</p>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">Preprocessing</span>
                      <span className="text-sm text-white">{aiObservability.breakdown.preprocessing}ms</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">Inference</span>
                      <span className="text-sm text-white">{aiObservability.breakdown.inference}ms</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">Postprocessing</span>
                      <span className="text-sm text-white">{aiObservability.breakdown.postprocessing}ms</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader
              title="Distribution des inférences"
              subtitle="Volume horaire sur 24h"
              icon={BarChart3}
            />
            <CardBody>
              <div className="h-64">
                <TimeSeriesChart
                  data={inferenceDistribution}
                  lines={[
                    { key: 'inferences', color: '#8b5cf6', name: 'Inférences' }
                  ]}
                />
              </div>
            </CardBody>
          </Card>

          <Card className="lg:col-span-3">
            <CardHeader
              title="Feature Store"
              subtitle="Features les plus utilisées"
              icon={Box}
            />
            <CardBody>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="p-4 rounded-xl bg-industrial-darker/50 text-center">
                  <p className="text-2xl font-bold text-white">{featureStoreStats.totalFeatures}</p>
                  <p className="text-sm text-gray-400">Total Features</p>
                </div>
                <div className="p-4 rounded-xl bg-industrial-darker/50 text-center">
                  <p className="text-2xl font-bold text-green-400">{featureStoreStats.activeFeatures}</p>
                  <p className="text-sm text-gray-400">Features Actives</p>
                </div>
                <div className="p-4 rounded-xl bg-industrial-darker/50 text-center">
                  <p className="text-2xl font-bold text-white">{featureStoreStats.featureGroups}</p>
                  <p className="text-sm text-gray-400">Feature Groups</p>
                </div>
                <div className="p-4 rounded-xl bg-industrial-darker/50 text-center">
                  <p className="text-2xl font-bold text-cyan-400">{featureStoreStats.freshnessScore}%</p>
                  <p className="text-sm text-gray-400">Freshness Score</p>
                </div>
              </div>

              <div className="space-y-2">
                {featureStoreStats.topFeatures.map((feature, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-bold text-gray-500 w-6">{idx + 1}</span>
                      <div>
                        <p className="font-mono text-sm text-white">{feature.name}</p>
                        <p className="text-xs text-gray-500">Freshness: {feature.freshness}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="w-24">
                        <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
                            style={{ width: `${feature.usage}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-sm font-medium text-white w-12 text-right">{feature.usage}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>
      )}
    </div>
  )
}

export default MLOpsDashboardView
