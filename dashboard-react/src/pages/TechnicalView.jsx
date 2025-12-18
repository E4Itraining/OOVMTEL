import React, { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Server,
  Database,
  Activity,
  Cpu,
  HardDrive,
  Network,
  Zap,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  ChevronRight,
  ChevronDown,
  ArrowLeft,
  RefreshCw,
  Search,
  Filter,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  ExternalLink,
  Layers,
  Box,
  GitBranch,
  Terminal,
  Eye,
  MoreVertical
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard, ServiceCard } from '../components/ui/Card'
import { RadialGauge, LinearGauge } from '../components/ui/Gauge'
import { TimeSeriesChart } from '../components/ui/Charts'
import { StatusBadge, LoadingSpinner } from '../components/ui/Status'

// Generate mock time series data
const generateTimeSeriesData = (points = 30, baseValue = 50, variance = 20) => {
  return Array.from({ length: points }, (_, i) => ({
    time: `${String(i).padStart(2, '0')}:00`,
    value: Math.max(0, baseValue + (Math.random() - 0.5) * variance)
  }))
}

// Service Detail Panel - Drill Down Component
function ServiceDetailPanel({ service, onClose, onNavigateToSource }) {
  const [activeTab, setActiveTab] = useState('metrics')

  const tabs = [
    { id: 'metrics', label: 'Metrics', icon: Activity },
    { id: 'logs', label: 'Recent Logs', icon: Terminal },
    { id: 'traces', label: 'Traces', icon: GitBranch },
    { id: 'config', label: 'Config', icon: Box }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, x: 300 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 300 }}
      className="fixed right-0 top-0 h-full w-[480px] bg-industrial-dark border-l border-industrial-border z-50 overflow-hidden flex flex-col"
    >
      {/* Header */}
      <div className="p-4 border-b border-industrial-border flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-white/5 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-400" />
          </button>
          <div>
            <h3 className="text-lg font-semibold text-white">{service.name}</h3>
            <div className="flex items-center gap-2">
              <StatusBadge status={service.status} size="sm" />
              <span className="text-xs text-gray-500">Last updated: 30s ago</span>
            </div>
          </div>
        </div>
        <button
          onClick={() => onNavigateToSource(service)}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-industrial-accent/10 text-industrial-accent text-sm hover:bg-industrial-accent/20 transition-colors"
        >
          <ExternalLink className="w-4 h-4" />
          Open in Source
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-industrial-border">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors
              ${activeTab === tab.id
                ? 'text-industrial-accent border-b-2 border-industrial-accent'
                : 'text-gray-400 hover:text-white'
              }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'metrics' && (
          <div className="space-y-4">
            {/* Key Metrics */}
            <div className="grid grid-cols-2 gap-4">
              {service.metrics?.map((metric, i) => (
                <div key={i} className="p-4 rounded-xl bg-industrial-card border border-industrial-border">
                  <p className="text-xs text-gray-500 mb-1">{metric.label}</p>
                  <p className="text-xl font-bold text-white">{metric.value}</p>
                  {metric.trend && (
                    <div className={`flex items-center gap-1 text-xs mt-1 ${metric.trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {metric.trend > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                      {Math.abs(metric.trend)}%
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Performance Chart */}
            <div className="p-4 rounded-xl bg-industrial-card border border-industrial-border">
              <h4 className="text-sm font-medium text-white mb-4">Performance (24h)</h4>
              <TimeSeriesChart
                data={generateTimeSeriesData(24, 80, 30)}
                lines={[{ dataKey: 'value', color: 'cyan', name: 'Performance' }]}
                height={200}
              />
            </div>

            {/* Resource Usage */}
            <div className="p-4 rounded-xl bg-industrial-card border border-industrial-border">
              <h4 className="text-sm font-medium text-white mb-4">Resource Usage</h4>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">CPU</span>
                    <span className="text-white">45%</span>
                  </div>
                  <LinearGauge value={45} color="auto" showValue={false} />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">Memory</span>
                    <span className="text-white">62%</span>
                  </div>
                  <LinearGauge value={62} color="auto" showValue={false} />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">Disk I/O</span>
                    <span className="text-white">28%</span>
                  </div>
                  <LinearGauge value={28} color="auto" showValue={false} />
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="space-y-2">
            {[
              { level: 'INFO', message: 'Request processed successfully', time: '12:34:56' },
              { level: 'WARN', message: 'High latency detected on endpoint /api/metrics', time: '12:34:45' },
              { level: 'INFO', message: 'Connection established with downstream service', time: '12:34:30' },
              { level: 'ERROR', message: 'Failed to connect to database replica-02', time: '12:34:15' },
              { level: 'INFO', message: 'Health check passed', time: '12:34:00' }
            ].map((log, i) => (
              <div key={i} className={`p-3 rounded-lg text-sm font-mono
                ${log.level === 'ERROR' ? 'bg-red-500/10 border border-red-500/30' :
                  log.level === 'WARN' ? 'bg-yellow-500/10 border border-yellow-500/30' :
                  'bg-industrial-card border border-industrial-border'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium
                    ${log.level === 'ERROR' ? 'bg-red-500/20 text-red-400' :
                      log.level === 'WARN' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-blue-500/20 text-blue-400'
                    }`}
                  >
                    {log.level}
                  </span>
                  <span className="text-gray-500 text-xs">{log.time}</span>
                </div>
                <p className="text-gray-300">{log.message}</p>
              </div>
            ))}
            <button className="w-full py-2 text-center text-sm text-industrial-accent hover:underline">
              View all logs in OpenSearch →
            </button>
          </div>
        )}

        {activeTab === 'traces' && (
          <div className="space-y-3">
            {[
              { traceId: 'abc123...def', duration: '145ms', spans: 12, status: 'success' },
              { traceId: 'ghi456...jkl', duration: '892ms', spans: 24, status: 'slow' },
              { traceId: 'mno789...pqr', duration: '23ms', spans: 4, status: 'success' }
            ].map((trace, i) => (
              <div key={i} className="p-3 rounded-lg bg-industrial-card border border-industrial-border">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-mono text-gray-300">{trace.traceId}</span>
                  <span className={`px-2 py-0.5 rounded text-xs
                    ${trace.status === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}
                  `}>
                    {trace.status}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>Duration: {trace.duration}</span>
                  <span>Spans: {trace.spans}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'config' && (
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-industrial-card border border-industrial-border">
              <h4 className="text-sm font-medium text-white mb-3">Service Configuration</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Replicas</span>
                  <span className="text-white">3</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Port</span>
                  <span className="text-white font-mono">{service.port || '8080'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Version</span>
                  <span className="text-white font-mono">v2.4.1</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Last Deploy</span>
                  <span className="text-white">2 days ago</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}

// Aggregated Backend Card
function BackendCard({ backend, onClick, isExpanded, onToggle }) {
  return (
    <motion.div
      className="rounded-xl bg-industrial-card border border-industrial-border overflow-hidden"
      layout
    >
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg bg-${backend.color}-500/10 flex items-center justify-center`}>
            <backend.icon className={`w-5 h-5 text-${backend.color}-400`} />
          </div>
          <div className="text-left">
            <h4 className="font-medium text-white">{backend.name}</h4>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <StatusBadge status={backend.status} size="sm" />
              <span>{backend.endpoint}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-lg font-bold text-white">{backend.primaryMetric}</p>
            <p className="text-xs text-gray-500">{backend.primaryMetricLabel}</p>
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
            className="border-t border-industrial-border"
          >
            <div className="p-4 space-y-4">
              {/* Metrics Grid */}
              <div className="grid grid-cols-3 gap-3">
                {backend.metrics.map((metric, i) => (
                  <div key={i} className="p-3 rounded-lg bg-industrial-darker">
                    <p className="text-xs text-gray-500 mb-1">{metric.label}</p>
                    <p className="text-lg font-semibold text-white">{metric.value}</p>
                  </div>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2">
                <button
                  onClick={() => onClick(backend)}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-industrial-accent/10 text-industrial-accent text-sm hover:bg-industrial-accent/20 transition-colors"
                >
                  <Eye className="w-4 h-4" />
                  View Dashboard
                </button>
                <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-white/5 text-gray-300 text-sm hover:bg-white/10 transition-colors">
                  <ExternalLink className="w-4 h-4" />
                  Open Native UI
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

function TechnicalView() {
  const navigate = useNavigate()
  const { metrics, isLoading } = useDashboard()
  const { t } = useI18n()

  const [selectedService, setSelectedService] = useState(null)
  const [expandedBackends, setExpandedBackends] = useState({})
  const [searchQuery, setSearchQuery] = useState('')

  const backends = useMemo(() => [
    {
      name: 'VictoriaMetrics',
      icon: Database,
      color: 'cyan',
      status: 'healthy',
      endpoint: 'victoria-metrics:8428',
      primaryMetric: '125K',
      primaryMetricLabel: 'Active Series',
      metrics: [
        { label: 'Ingestion Rate', value: '1.2K/s' },
        { label: 'Query Latency', value: '12ms' },
        { label: 'Storage Used', value: '2.4GB' }
      ]
    },
    {
      name: 'OpenSearch',
      icon: Search,
      color: 'purple',
      status: 'healthy',
      endpoint: 'opensearch:9200',
      primaryMetric: '1.2M',
      primaryMetricLabel: 'Documents',
      metrics: [
        { label: 'Indices', value: '12' },
        { label: 'Search Rate', value: '520/s' },
        { label: 'Index Size', value: '8.5GB' }
      ]
    },
    {
      name: 'Kafka',
      icon: Activity,
      color: 'green',
      status: 'warning',
      endpoint: 'kafka:9092',
      primaryMetric: '6',
      primaryMetricLabel: 'Topics',
      metrics: [
        { label: 'Partitions', value: '96' },
        { label: 'Throughput', value: '45K msg/s' },
        { label: 'Consumer Lag', value: '142' }
      ]
    },
    {
      name: 'OTEL Collector',
      icon: Zap,
      color: 'yellow',
      status: 'healthy',
      endpoint: 'otel-collector:8888',
      primaryMetric: '180',
      primaryMetricLabel: 'Spans/s',
      metrics: [
        { label: 'Metrics/s', value: '1.2K' },
        { label: 'Logs/s', value: '520' },
        { label: 'Export Success', value: '99.9%' }
      ]
    }
  ], [])

  const services = useMemo(() => [
    {
      name: 'api-gateway',
      status: 'healthy',
      port: '8080',
      metrics: [
        { label: 'Requests/s', value: '1.2K', trend: 5 },
        { label: 'Latency P95', value: '45ms', trend: -3 },
        { label: 'Error Rate', value: '0.02%', trend: 0 },
        { label: 'Uptime', value: '99.99%', trend: 0 }
      ]
    },
    {
      name: 'data-processor',
      status: 'healthy',
      port: '8081',
      metrics: [
        { label: 'Events/s', value: '5.4K', trend: 12 },
        { label: 'Processing Time', value: '23ms', trend: -8 },
        { label: 'Queue Depth', value: '142', trend: 5 },
        { label: 'Success Rate', value: '99.8%', trend: 0 }
      ]
    },
    {
      name: 'scada-connector',
      status: 'warning',
      port: '8082',
      metrics: [
        { label: 'Signals/s', value: '890', trend: -2 },
        { label: 'Latency', value: '89ms', trend: 15 },
        { label: 'Reconnects', value: '3', trend: 100 },
        { label: 'Buffer Used', value: '45%', trend: 10 }
      ]
    },
    {
      name: 'ml-inference',
      status: 'healthy',
      port: '8083',
      metrics: [
        { label: 'Predictions/s', value: '320', trend: 8 },
        { label: 'Model Latency', value: '12ms', trend: -5 },
        { label: 'Accuracy', value: '94.2%', trend: 1 },
        { label: 'GPU Util', value: '72%', trend: 3 }
      ]
    }
  ], [])

  const pipelineData = useMemo(() => generateTimeSeriesData(30, 1000, 300), [])
  const resourceData = useMemo(() => [
    { name: 'CPU', value: metrics.tech?.cpu || 45, color: 'cyan' },
    { name: 'Memory', value: metrics.tech?.memory || 62, color: 'purple' },
    { name: 'Disk', value: metrics.tech?.disk || 38, color: 'green' },
    { name: 'Network', value: 28, color: 'yellow' }
  ], [metrics.tech])

  const toggleBackend = (name) => {
    setExpandedBackends(prev => ({ ...prev, [name]: !prev[name] }))
  }

  const handleServiceClick = (service) => {
    setSelectedService(service)
  }

  const handleNavigateToSource = (item) => {
    // Navigate to the specific backend/service dashboard
    if (item.endpoint) {
      navigate(`/details/${item.name.toLowerCase().replace(' ', '-')}`)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <LoadingSpinner size="lg" label={t('common.loading')} />
      </div>
    )
  }

  return (
    <div className="relative">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/command-center')}
            className="p-2 rounded-lg hover:bg-white/5 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-400" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white">{t('technicalView.title')}</h1>
            <p className="text-gray-400">{t('technicalView.subtitle')}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search services..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 rounded-lg bg-industrial-card border border-industrial-border text-white placeholder-gray-500 focus:border-industrial-accent focus:outline-none"
            />
          </div>

          <button className="p-2 rounded-lg bg-industrial-card border border-industrial-border hover:border-gray-600 transition-colors">
            <Filter className="w-5 h-5 text-gray-400" />
          </button>

          <button className="p-2 rounded-lg bg-industrial-card border border-industrial-border hover:border-gray-600 transition-colors">
            <RefreshCw className="w-5 h-5 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <MetricCard
          label={t('metrics.tech.metricsRate')}
          value={metrics.tech?.metricsRate?.toLocaleString() || "1,250"}
          unit="pts/s"
          icon={Activity}
          color="cyan"
          trend="up"
          trendValue="+5%"
        />
        <MetricCard
          label={t('metrics.tech.logsRate')}
          value={metrics.tech?.logsRate?.toLocaleString() || "520"}
          unit="rec/s"
          icon={Database}
          color="purple"
        />
        <MetricCard
          label={t('metrics.tech.latencyP95')}
          value={metrics.tech?.latencyP95 || "23"}
          unit="ms"
          icon={Clock}
          color="green"
          trend="down"
          trendValue="-3ms"
        />
        <MetricCard
          label={t('metrics.tech.errorRate')}
          value={metrics.tech?.errorRate || "0.02"}
          unit="%"
          icon={AlertTriangle}
          color="green"
        />
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Data Sources */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-industrial-accent" />
            {t('technicalView.dataSources')}
          </h2>

          {backends.map((backend) => (
            <BackendCard
              key={backend.name}
              backend={backend}
              isExpanded={expandedBackends[backend.name]}
              onToggle={() => toggleBackend(backend.name)}
              onClick={handleNavigateToSource}
            />
          ))}
        </div>

        {/* Right Column - Services & Resources */}
        <div className="space-y-6">
          {/* Resource Usage */}
          <Card>
            <CardHeader title={t('technicalView.resourceUsage')} icon={Cpu} />
            <CardBody>
              <div className="space-y-4">
                {resourceData.map((resource) => (
                  <div key={resource.name}>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-400">{resource.name}</span>
                      <span className="text-sm font-medium text-white">{resource.value}%</span>
                    </div>
                    <LinearGauge value={resource.value} color="auto" showValue={false} />
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          {/* Services */}
          <Card>
            <CardHeader title={t('technicalView.services')} icon={Layers} />
            <CardBody>
              <div className="space-y-2">
                {services.map((service) => (
                  <button
                    key={service.name}
                    onClick={() => handleServiceClick(service)}
                    className="w-full p-3 rounded-lg bg-industrial-darker hover:bg-white/5 transition-colors flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-3">
                      <StatusBadge status={service.status} size="sm" />
                      <div className="text-left">
                        <p className="text-sm font-medium text-white">{service.name}</p>
                        <p className="text-xs text-gray-500">:{service.port}</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-500 group-hover:text-white transition-colors" />
                  </button>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>
      </div>

      {/* Pipeline Chart */}
      <div className="mt-6">
        <Card>
          <CardHeader title={t('technicalView.pipelineThroughput')} icon={Activity} />
          <CardBody>
            <TimeSeriesChart
              data={pipelineData}
              lines={[{ dataKey: 'value', color: 'cyan', name: 'Throughput' }]}
              height={260}
              yAxisLabel="Throughput"
              yAxisUnit="pts/s"
              warningThreshold={1400}
              criticalThreshold={1600}
              referenceLines={[{ y: 1000, color: '#22c55e', label: 'Baseline', dashed: true }]}
              enableBrush
              brushHeight={30}
              tooltipUnit="pts/s"
            />
          </CardBody>
        </Card>
      </div>

      {/* Service Detail Panel */}
      <AnimatePresence>
        {selectedService && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 z-40"
              onClick={() => setSelectedService(null)}
            />
            <ServiceDetailPanel
              service={selectedService}
              onClose={() => setSelectedService(null)}
              onNavigateToSource={handleNavigateToSource}
            />
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

export default TechnicalView
