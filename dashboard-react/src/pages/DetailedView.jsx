import React, { useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Activity,
  Database,
  Server,
  Cpu,
  HardDrive,
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  ChevronLeft,
  RefreshCw,
  ExternalLink,
  Zap,
  MemoryStick
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { TimeSeriesChart, BarChartComponent, AreaChartComponent } from '../components/ui/Charts'
import { RadialGauge, LinearGauge } from '../components/ui/Gauge'
import { StatusBadge, LoadingSpinner } from '../components/ui/Status'

// Generate realistic time series
const generateTimeSeries = (points = 60, baseValue = 50, variance = 15) => {
  let current = baseValue
  return Array.from({ length: points }, (_, i) => {
    current = Math.max(0, Math.min(100, current + (Math.random() - 0.5) * variance))
    return {
      time: `${String(Math.floor(i / 60)).padStart(2, '0')}:${String(i % 60).padStart(2, '0')}`,
      value: Math.round(current * 10) / 10
    }
  })
}

const serviceConfigs = {
  'victoriametrics': {
    name: 'VictoriaMetrics',
    icon: Database,
    color: 'from-cyan-500 to-blue-600',
    url: 'http://localhost:8428',
    description: 'High-performance time series database',
    metrics: [
      { key: 'activeSeries', label: 'Active Series', value: '125,432', unit: '', trend: 'up', trendValue: '+2.3%' },
      { key: 'storage', label: 'Storage Used', value: '2.4', unit: 'GB', trend: 'up', trendValue: '+120MB' },
      { key: 'queryLatency', label: 'Query Latency P95', value: '12', unit: 'ms', trend: 'down', trendValue: '-3ms' },
      { key: 'ingestionRate', label: 'Ingestion Rate', value: '1,250', unit: 'pts/s', trend: 'stable', trendValue: '' },
    ]
  },
  'opensearch': {
    name: 'OpenSearch',
    icon: Database,
    color: 'from-blue-500 to-purple-600',
    url: 'http://localhost:9200',
    description: 'Distributed search and analytics engine',
    metrics: [
      { key: 'documents', label: 'Total Documents', value: '2.8M', unit: '', trend: 'up', trendValue: '+45K' },
      { key: 'indices', label: 'Indices', value: '5', unit: '', trend: 'stable', trendValue: '' },
      { key: 'shards', label: 'Active Shards', value: '15', unit: '', trend: 'stable', trendValue: '' },
      { key: 'searchRate', label: 'Search Rate', value: '89', unit: 'req/s', trend: 'up', trendValue: '+12%' },
    ]
  },
  'kafka': {
    name: 'Kafka',
    icon: Activity,
    color: 'from-green-500 to-teal-600',
    url: 'http://localhost:8090',
    description: 'Distributed event streaming platform',
    metrics: [
      { key: 'topics', label: 'Topics', value: '6', unit: '', trend: 'stable', trendValue: '' },
      { key: 'partitions', label: 'Partitions', value: '50', unit: '', trend: 'stable', trendValue: '' },
      { key: 'throughput', label: 'Throughput', value: '2,335', unit: 'msg/s', trend: 'up', trendValue: '+8%' },
      { key: 'consumerLag', label: 'Consumer Lag', value: '170', unit: 'msgs', trend: 'down', trendValue: '-45' },
    ]
  },
  'otel-collector': {
    name: 'OTEL Collector',
    icon: Zap,
    color: 'from-purple-500 to-pink-600',
    url: 'http://localhost:8888',
    description: 'OpenTelemetry data collection and processing',
    metrics: [
      { key: 'received', label: 'Received', value: '1,250', unit: 'pts/s', trend: 'up', trendValue: '+5%' },
      { key: 'exported', label: 'Exported', value: '1,225', unit: 'pts/s', trend: 'up', trendValue: '+5%' },
      { key: 'dropped', label: 'Dropped', value: '0', unit: '', trend: 'stable', trendValue: '' },
      { key: 'queueSize', label: 'Queue Size', value: '128', unit: '', trend: 'stable', trendValue: '' },
    ]
  },
  'grafana': {
    name: 'Grafana',
    icon: Activity,
    color: 'from-orange-500 to-red-600',
    url: 'http://localhost:3000',
    description: 'Visualization and analytics platform',
    metrics: [
      { key: 'dashboards', label: 'Dashboards', value: '6', unit: '', trend: 'stable', trendValue: '' },
      { key: 'panels', label: 'Total Panels', value: '63', unit: '', trend: 'stable', trendValue: '' },
      { key: 'alerts', label: 'Active Alerts', value: '2', unit: '', trend: 'down', trendValue: '-1' },
      { key: 'queries', label: 'Queries/min', value: '120', unit: '', trend: 'up', trendValue: '+15%' },
    ]
  },
  'openobserve': {
    name: 'OpenObserve',
    icon: Server,
    color: 'from-indigo-500 to-purple-600',
    url: 'http://localhost:5080',
    description: 'Logs and traces storage',
    metrics: [
      { key: 'logsRate', label: 'Logs Rate', value: '520', unit: 'rec/s', trend: 'up', trendValue: '+8%' },
      { key: 'tracesRate', label: 'Traces Rate', value: '180', unit: 'spans/s', trend: 'stable', trendValue: '' },
      { key: 'storage', label: 'Storage', value: '1.2', unit: 'GB', trend: 'up', trendValue: '+80MB' },
      { key: 'retention', label: 'Retention', value: '7', unit: 'days', trend: 'stable', trendValue: '' },
    ]
  }
}

function DetailedView() {
  const { service } = useParams()
  const navigate = useNavigate()
  const { metrics: globalMetrics } = useDashboard()

  const config = serviceConfigs[service] || serviceConfigs['victoriametrics']
  const Icon = config.icon

  // Generate mock data
  const cpuData = useMemo(() => generateTimeSeries(60, 45, 15), [])
  const memoryData = useMemo(() => generateTimeSeries(60, 62, 10), [])
  const throughputData = useMemo(() => generateTimeSeries(60, 1000, 200), [])
  const latencyData = useMemo(() => generateTimeSeries(60, 25, 10), [])

  const resourceUsage = {
    cpu: 45,
    memory: 62,
    disk: 38,
    network: 28
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 rounded-lg hover:bg-industrial-card transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-gray-400" />
          </button>
          <div className="flex items-center gap-4">
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${config.color} flex items-center justify-center shadow-lg`}>
              <Icon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">{config.name}</h1>
              <p className="text-gray-400">{config.description}</p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status="healthy" size="md" />
          <a
            href={config.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary"
          >
            <ExternalLink className="w-4 h-4" />
            Ouvrir
          </a>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {config.metrics.map((metric, i) => (
          <MetricCard
            key={metric.key}
            label={metric.label}
            value={metric.value}
            unit={metric.unit}
            trend={metric.trend}
            trendValue={metric.trendValue}
            color={['cyan', 'purple', 'green', 'yellow'][i % 4]}
          />
        ))}
      </div>

      {/* Resource Usage */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Gauges */}
        <Card>
          <CardHeader title="Resource Usage" icon={Cpu} />
          <CardBody>
            <div className="grid grid-cols-2 gap-6">
              <div className="text-center">
                <RadialGauge value={resourceUsage.cpu} size={100} color="auto" />
                <p className="text-sm text-gray-400 mt-2">CPU</p>
              </div>
              <div className="text-center">
                <RadialGauge value={resourceUsage.memory} size={100} color="auto" />
                <p className="text-sm text-gray-400 mt-2">Memory</p>
              </div>
              <div className="text-center">
                <RadialGauge value={resourceUsage.disk} size={100} color="auto" />
                <p className="text-sm text-gray-400 mt-2">Disk</p>
              </div>
              <div className="text-center">
                <RadialGauge value={resourceUsage.network} size={100} color="auto" />
                <p className="text-sm text-gray-400 mt-2">Network</p>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* CPU & Memory Chart */}
        <Card className="lg:col-span-2">
          <CardHeader title="CPU & Memory (1h)" icon={Activity} />
          <CardBody>
            <TimeSeriesChart
              data={cpuData.map((d, i) => ({
                ...d,
                memory: memoryData[i]?.value || 0
              }))}
              lines={[
                { dataKey: 'value', color: 'cyan', name: 'CPU %' },
                { dataKey: 'memory', color: 'purple', name: 'Memory %' }
              ]}
              height={220}
              showLegend
            />
          </CardBody>
        </Card>
      </div>

      {/* Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Throughput */}
        <Card>
          <CardHeader title="Throughput (1h)" icon={TrendingUp} />
          <CardBody>
            <AreaChartComponent
              data={throughputData}
              areas={[{ dataKey: 'value', color: 'cyan', name: 'Throughput' }]}
              height={220}
            />
          </CardBody>
        </Card>

        {/* Latency */}
        <Card>
          <CardHeader title="Latency P95 (1h)" icon={Clock} />
          <CardBody>
            <TimeSeriesChart
              data={latencyData}
              lines={[{ dataKey: 'value', color: 'purple', name: 'Latency ms' }]}
              height={220}
            />
          </CardBody>
        </Card>
      </div>

      {/* Detailed Stats */}
      <Card>
        <CardHeader title="Detailed Statistics" icon={Database} />
        <CardBody>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {[
              { label: 'Uptime', value: '7d 14h 32m', icon: Clock },
              { label: 'Requests', value: '1.2M', icon: Activity },
              { label: 'Errors', value: '0.02%', icon: AlertTriangle },
              { label: 'Connections', value: '24', icon: Server },
              { label: 'Cache Hit', value: '94.5%', icon: Zap },
              { label: 'Version', value: 'v1.96.0', icon: CheckCircle },
            ].map((stat) => (
              <div key={stat.label} className="p-4 rounded-lg bg-industrial-dark/50 text-center">
                <stat.icon className="w-5 h-5 text-gray-500 mx-auto mb-2" />
                <p className="text-lg font-semibold text-white">{stat.value}</p>
                <p className="text-xs text-gray-500">{stat.label}</p>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader title="Recent Activity" icon={Activity} />
        <CardBody className="p-0">
          <div className="divide-y divide-industrial-border/50">
            {[
              { time: '2 min ago', event: 'Query completed', details: 'SELECT * FROM metrics WHERE...', status: 'success' },
              { time: '5 min ago', event: 'Data export', details: 'Exported 1,250 points to OpenSearch', status: 'success' },
              { time: '12 min ago', event: 'Config reload', details: 'Configuration reloaded successfully', status: 'success' },
              { time: '1h ago', event: 'Memory warning', details: 'Memory usage reached 85%', status: 'warning' },
              { time: '3h ago', event: 'Service restart', details: 'Scheduled maintenance restart', status: 'info' },
            ].map((activity, i) => (
              <motion.div
                key={i}
                className="p-4 hover:bg-industrial-dark/30"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      activity.status === 'success' ? 'bg-green-500' :
                      activity.status === 'warning' ? 'bg-yellow-500' :
                      activity.status === 'error' ? 'bg-red-500' :
                      'bg-blue-500'
                    }`} />
                    <div>
                      <p className="font-medium text-white">{activity.event}</p>
                      <p className="text-sm text-gray-400">{activity.details}</p>
                    </div>
                  </div>
                  <span className="text-xs text-gray-500">{activity.time}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

export default DetailedView
