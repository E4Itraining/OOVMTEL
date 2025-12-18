import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  ChevronDown,
  ChevronRight,
  Clock,
  Database,
  ExternalLink,
  GitBranch,
  HardDrive,
  Layers,
  MessageSquare,
  Monitor,
  Network,
  RefreshCw,
  Server,
  Settings,
  Workflow,
  Zap
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard, ServiceCard } from '../components/ui/Card'
import { SemiCircleGauge, LinearGauge } from '../components/ui/Gauge'
import { TimeSeriesChart } from '../components/ui/Charts'
import { StatusBadge, HealthIndicator } from '../components/ui/Status'

// Backend services configuration
const BACKEND_SERVICES = [
  {
    id: 'victoriametrics',
    name: 'VictoriaMetrics',
    icon: Database,
    color: 'from-blue-500 to-blue-600',
    status: 'healthy',
    metrics: {
      activeSeries: 2450000,
      storage: '45.2 GB',
      queryLatency: 12,
      ingestRate: 125000
    },
    details: [
      { label: 'Active Series', value: '2.45M', key: 'activeSeries' },
      { label: 'Storage Used', value: '45.2 GB', key: 'storage' },
      { label: 'Query Latency', value: '12ms', key: 'queryLatency' }
    ]
  },
  {
    id: 'opensearch',
    name: 'OpenSearch',
    icon: Database,
    color: 'from-yellow-500 to-orange-500',
    status: 'healthy',
    metrics: {
      documents: 15200000,
      indices: 24,
      nodes: 3,
      health: 'green'
    },
    details: [
      { label: 'Documents', value: '15.2M', key: 'documents' },
      { label: 'Indices', value: '24', key: 'indices' },
      { label: 'Cluster Health', value: 'Green', key: 'health' }
    ]
  },
  {
    id: 'kafka',
    name: 'Apache Kafka',
    icon: MessageSquare,
    color: 'from-green-500 to-green-600',
    status: 'degraded',
    metrics: {
      topics: 12,
      partitions: 48,
      throughput: 45000,
      consumerLag: 1250
    },
    details: [
      { label: 'Topics', value: '12', key: 'topics' },
      { label: 'Throughput', value: '45k/s', key: 'throughput' },
      { label: 'Consumer Lag', value: '1.25k', key: 'consumerLag' }
    ]
  },
  {
    id: 'otel',
    name: 'OTEL Collector',
    icon: Activity,
    color: 'from-purple-500 to-purple-600',
    status: 'healthy',
    metrics: {
      metricsRate: 125000,
      logsRate: 8500,
      tracesRate: 2500,
      pipelines: 4
    },
    details: [
      { label: 'Metrics/s', value: '125k', key: 'metricsRate' },
      { label: 'Logs/s', value: '8.5k', key: 'logsRate' },
      { label: 'Traces/s', value: '2.5k', key: 'tracesRate' }
    ]
  }
]

// Pipeline stages
const PIPELINE_STAGES = [
  { id: 'collectors', name: 'Collectors', icon: Network, count: 8, status: 'healthy' },
  { id: 'processors', name: 'Processors', icon: Workflow, count: 4, status: 'healthy' },
  { id: 'exporters', name: 'Exporters', icon: GitBranch, count: 3, status: 'warning' },
  { id: 'storage', name: 'Storage', icon: HardDrive, count: 2, status: 'healthy' }
]

function BackendServiceCard({ service, isExpanded, onToggle, onDrillDown }) {
  const Icon = service.icon
  const statusColors = {
    healthy: 'border-green-500/30 hover:border-green-500/50',
    degraded: 'border-yellow-500/30 hover:border-yellow-500/50',
    down: 'border-red-500/30 hover:border-red-500/50'
  }

  return (
    <motion.div
      className={`rounded-xl border bg-industrial-card/50 ${statusColors[service.status]} transition-all duration-300`}
      layout
    >
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${service.color} flex items-center justify-center shadow-lg`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-white">{service.name}</h3>
            <StatusBadge status={service.status} />
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-6">
            {service.details.slice(0, 2).map((detail, idx) => (
              <div key={idx} className="text-right">
                <p className="text-lg font-semibold text-white">{detail.value}</p>
                <p className="text-xs text-gray-500">{detail.label}</p>
              </div>
            ))}
          </div>
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
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                {service.details.map((detail, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-industrial-darker/50">
                    <p className="text-lg font-semibold text-white">{detail.value}</p>
                    <p className="text-xs text-gray-500">{detail.label}</p>
                  </div>
                ))}
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <Clock className="w-3 h-3" />
                  <span>Last updated: 5s ago</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onDrillDown(service)
                  }}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-industrial-accent/20 text-cyan-400 hover:bg-industrial-accent/30 transition-colors text-sm"
                >
                  View Details
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

function PipelineStage({ stage, isLast }) {
  const Icon = stage.icon
  const statusColors = {
    healthy: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500'
  }

  return (
    <div className="flex items-center">
      <div className="flex flex-col items-center">
        <div className={`w-14 h-14 rounded-xl bg-industrial-card border border-industrial-border flex items-center justify-center relative`}>
          <Icon className="w-6 h-6 text-gray-300" />
          <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full ${statusColors[stage.status]}`} />
        </div>
        <p className="text-xs text-gray-400 mt-2">{stage.name}</p>
        <p className="text-xs text-gray-500">{stage.count} active</p>
      </div>
      {!isLast && (
        <div className="flex-1 h-px bg-gradient-to-r from-industrial-border to-industrial-accent/30 mx-2 mt-[-20px]">
          <ChevronRight className="w-4 h-4 text-gray-600 ml-auto -mt-2" />
        </div>
      )}
    </div>
  )
}

function TechnicalView() {
  const navigate = useNavigate()
  const { t } = useI18n()
  const { metrics } = useDashboard()
  const [expandedService, setExpandedService] = useState(null)

  const handleToggleService = (serviceId) => {
    setExpandedService(expandedService === serviceId ? null : serviceId)
  }

  const handleDrillDown = (service) => {
    navigate(`/details/${service.id}`)
  }

  // Mock time series data
  const timeSeriesData = Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    metrics: 100000 + Math.random() * 50000,
    logs: 7000 + Math.random() * 3000,
    traces: 2000 + Math.random() * 1000
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">
            {t('technicalView.title')}
          </h1>
          <p className="text-gray-400 mt-1">
            {t('technicalView.subtitle')}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn btn-ghost flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            {t('common.refresh')}
          </button>
          <button className="btn btn-ghost flex items-center gap-2">
            <Settings className="w-4 h-4" />
            {t('common.settings')}
          </button>
        </div>
      </div>

      {/* Key Infrastructure Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <MetricCard
          label={t('metrics.tech.metricsRate')}
          value={metrics.tech?.metricsRate?.toLocaleString() || '125,000'}
          unit="/s"
          icon={Activity}
          color="cyan"
        />
        <MetricCard
          label={t('metrics.tech.logsRate')}
          value={metrics.tech?.logsRate?.toLocaleString() || '8,500'}
          unit="/s"
          icon={Layers}
          color="yellow"
        />
        <MetricCard
          label={t('metrics.tech.tracesRate')}
          value={metrics.tech?.tracesRate?.toLocaleString() || '2,500'}
          unit="/s"
          icon={GitBranch}
          color="purple"
        />
        <MetricCard
          label={t('metrics.tech.cpu')}
          value={metrics.tech?.cpu?.toFixed(1) || '45'}
          unit="%"
          icon={Monitor}
          color="green"
        />
        <MetricCard
          label={t('metrics.tech.memory')}
          value={metrics.tech?.memory?.toFixed(1) || '67'}
          unit="%"
          icon={HardDrive}
          color="blue"
        />
        <MetricCard
          label={t('metrics.tech.errorRate')}
          value={metrics.tech?.errorRate?.toFixed(2) || '0.12'}
          unit="%"
          icon={AlertTriangle}
          color={metrics.tech?.errorRate > 1 ? 'red' : 'green'}
        />
      </div>

      {/* Data Pipeline Visualization */}
      <Card>
        <CardHeader
          title={t('technicalView.pipeline.title')}
          subtitle={t('technicalView.pipeline.subtitle')}
          icon={Workflow}
        />
        <CardBody>
          <div className="flex items-center justify-between overflow-x-auto pb-4">
            {PIPELINE_STAGES.map((stage, idx) => (
              <PipelineStage
                key={stage.id}
                stage={stage}
                isLast={idx === PIPELINE_STAGES.length - 1}
              />
            ))}
          </div>
        </CardBody>
      </Card>

      {/* Backend Services */}
      <div>
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">
          {t('technicalView.backends.title')}
        </h2>
        <div className="space-y-3">
          {BACKEND_SERVICES.map((service) => (
            <BackendServiceCard
              key={service.id}
              service={service}
              isExpanded={expandedService === service.id}
              onToggle={() => handleToggleService(service.id)}
              onDrillDown={handleDrillDown}
            />
          ))}
        </div>
      </div>

      {/* Throughput Chart */}
      <Card>
        <CardHeader
          title={t('technicalView.throughput.title')}
          subtitle={t('technicalView.throughput.subtitle')}
          icon={Zap}
        />
        <CardBody>
          <div className="h-64">
            <TimeSeriesChart
              data={timeSeriesData}
              lines={[
                { key: 'metrics', color: '#06b6d4', name: 'Metrics' },
                { key: 'logs', color: '#eab308', name: 'Logs' },
                { key: 'traces', color: '#a855f7', name: 'Traces' }
              ]}
            />
          </div>
        </CardBody>
      </Card>

      {/* Quick Links to Service UIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => navigate('/grafana')}
          className="p-4 rounded-xl border border-industrial-border bg-industrial-card/50 hover:border-orange-500/50 transition-all flex items-center justify-between group"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
              <Activity className="w-5 h-5 text-orange-400" />
            </div>
            <div className="text-left">
              <p className="font-medium text-white">Grafana</p>
              <p className="text-xs text-gray-400">Dashboards & Visualization</p>
            </div>
          </div>
          <ExternalLink className="w-5 h-5 text-gray-500 group-hover:text-orange-400 transition-colors" />
        </button>

        <button
          onClick={() => navigate('/opensearch')}
          className="p-4 rounded-xl border border-industrial-border bg-industrial-card/50 hover:border-yellow-500/50 transition-all flex items-center justify-between group"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-yellow-500/20 flex items-center justify-center">
              <Database className="w-5 h-5 text-yellow-400" />
            </div>
            <div className="text-left">
              <p className="font-medium text-white">OpenSearch</p>
              <p className="text-xs text-gray-400">Log Analysis & Search</p>
            </div>
          </div>
          <ExternalLink className="w-5 h-5 text-gray-500 group-hover:text-yellow-400 transition-colors" />
        </button>

        <button
          onClick={() => navigate('/kafka')}
          className="p-4 rounded-xl border border-industrial-border bg-industrial-card/50 hover:border-green-500/50 transition-all flex items-center justify-between group"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-green-400" />
            </div>
            <div className="text-left">
              <p className="font-medium text-white">Kafka</p>
              <p className="text-xs text-gray-400">Streaming & Topics</p>
            </div>
          </div>
          <ExternalLink className="w-5 h-5 text-gray-500 group-hover:text-green-400 transition-colors" />
        </button>
      </div>
    </div>
  )
}

export default TechnicalView
