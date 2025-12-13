import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Play,
  Pause,
  RotateCcw,
  Zap,
  Activity,
  Target,
  TrendingUp,
  TrendingDown,
  Server,
  Database,
  Cpu,
  HardDrive,
  RefreshCw,
  ChevronRight,
  ChevronDown,
  FileText,
  Settings,
  Eye,
  XCircle,
  AlertCircle,
  CheckCircle,
  History,
  Wrench,
  PlayCircle,
  Terminal,
  BookOpen,
  ArrowRight,
  Timer,
  BarChart3
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { TimeSeriesChart, DonutChart, AreaChartComponent } from '../components/ui/Charts'
import { StatusBadge, StatusDot, HealthIndicator } from '../components/ui/Status'
import { RadialGauge, LinearGauge } from '../components/ui/Gauge'

// Mock data for SLOs
const sloData = [
  {
    id: 'api-availability',
    name: 'API Availability',
    target: 99.9,
    current: 99.95,
    budget: 43.2,
    budgetUsed: 12.5,
    status: 'healthy',
    service: 'API Gateway',
    window: '30d'
  },
  {
    id: 'latency-p99',
    name: 'Latency P99',
    target: 200,
    current: 185,
    budget: 100,
    budgetUsed: 35,
    status: 'healthy',
    service: 'Backend Services',
    window: '30d',
    unit: 'ms'
  },
  {
    id: 'error-rate',
    name: 'Error Rate',
    target: 0.1,
    current: 0.08,
    budget: 100,
    budgetUsed: 80,
    status: 'warning',
    service: 'All Services',
    window: '30d',
    unit: '%'
  },
  {
    id: 'data-freshness',
    name: 'Data Freshness',
    target: 99.5,
    current: 99.2,
    budget: 50,
    budgetUsed: 60,
    status: 'critical',
    service: 'Data Pipeline',
    window: '7d'
  }
]

// Mock data for active incidents
const activeIncidents = [
  {
    id: 'INC-2024-001',
    title: 'High latency on Kafka consumers',
    severity: 'warning',
    service: 'Kafka',
    startTime: new Date(Date.now() - 25 * 60 * 1000),
    status: 'investigating',
    assignee: 'Auto-remediation',
    runbook: 'kafka-consumer-lag',
    affectedSLOs: ['latency-p99'],
    actions: [
      { time: new Date(Date.now() - 25 * 60 * 1000), action: 'Alert triggered', status: 'completed' },
      { time: new Date(Date.now() - 24 * 60 * 1000), action: 'Auto-scaling initiated', status: 'completed' },
      { time: new Date(Date.now() - 20 * 60 * 1000), action: 'Consumer group rebalance', status: 'in_progress' }
    ]
  },
  {
    id: 'INC-2024-002',
    title: 'VictoriaMetrics storage approaching limit',
    severity: 'critical',
    service: 'VictoriaMetrics',
    startTime: new Date(Date.now() - 2 * 60 * 60 * 1000),
    status: 'mitigating',
    assignee: 'Ops Team',
    runbook: 'vm-storage-cleanup',
    affectedSLOs: ['data-freshness'],
    actions: [
      { time: new Date(Date.now() - 2 * 60 * 60 * 1000), action: 'Alert triggered', status: 'completed' },
      { time: new Date(Date.now() - 1.5 * 60 * 60 * 1000), action: 'Old data retention reduced', status: 'completed' },
      { time: new Date(Date.now() - 30 * 60 * 1000), action: 'Storage expansion requested', status: 'in_progress' }
    ]
  }
]

// Mock data for remediation runbooks
const runbooks = [
  {
    id: 'kafka-consumer-lag',
    name: 'Kafka Consumer Lag Remediation',
    service: 'Kafka',
    triggers: ['consumer_lag > 10000', 'consumer_lag_rate > 500/s'],
    steps: [
      { name: 'Scale consumers', automated: true, avgDuration: '2m' },
      { name: 'Rebalance partitions', automated: true, avgDuration: '5m' },
      { name: 'Check producer rate', automated: false, avgDuration: '10m' },
      { name: 'Notify team if persists', automated: true, avgDuration: '1m' }
    ],
    executions: 45,
    successRate: 92,
    avgMTTR: '8m'
  },
  {
    id: 'vm-storage-cleanup',
    name: 'VictoriaMetrics Storage Cleanup',
    service: 'VictoriaMetrics',
    triggers: ['storage_usage > 85%', 'storage_growth_rate > 2GB/day'],
    steps: [
      { name: 'Reduce retention period', automated: true, avgDuration: '1m' },
      { name: 'Delete old backups', automated: true, avgDuration: '5m' },
      { name: 'Request storage expansion', automated: false, avgDuration: '30m' },
      { name: 'Archive cold data', automated: true, avgDuration: '15m' }
    ],
    executions: 12,
    successRate: 83,
    avgMTTR: '45m'
  },
  {
    id: 'opensearch-health',
    name: 'OpenSearch Cluster Health',
    service: 'OpenSearch',
    triggers: ['cluster_health != green', 'unassigned_shards > 0'],
    steps: [
      { name: 'Check node status', automated: true, avgDuration: '30s' },
      { name: 'Reallocate shards', automated: true, avgDuration: '10m' },
      { name: 'Restart unhealthy nodes', automated: false, avgDuration: '5m' },
      { name: 'Verify cluster recovery', automated: true, avgDuration: '2m' }
    ],
    executions: 28,
    successRate: 96,
    avgMTTR: '12m'
  },
  {
    id: 'otel-collector-restart',
    name: 'OTEL Collector Recovery',
    service: 'OTEL Collector',
    triggers: ['collector_health != healthy', 'dropped_spans > 100/s'],
    steps: [
      { name: 'Check collector logs', automated: true, avgDuration: '1m' },
      { name: 'Restart collector pods', automated: true, avgDuration: '2m' },
      { name: 'Verify pipeline flow', automated: true, avgDuration: '3m' },
      { name: 'Scale if needed', automated: true, avgDuration: '5m' }
    ],
    executions: 67,
    successRate: 98,
    avgMTTR: '6m'
  }
]

// Mock data for recent remediation history
const remediationHistory = [
  {
    id: 'REM-001',
    runbook: 'kafka-consumer-lag',
    service: 'Kafka',
    startTime: new Date(Date.now() - 4 * 60 * 60 * 1000),
    endTime: new Date(Date.now() - 3.8 * 60 * 60 * 1000),
    status: 'success',
    trigger: 'consumer_lag > 10000',
    stepsCompleted: 4,
    stepsTotal: 4
  },
  {
    id: 'REM-002',
    runbook: 'opensearch-health',
    service: 'OpenSearch',
    startTime: new Date(Date.now() - 8 * 60 * 60 * 1000),
    endTime: new Date(Date.now() - 7.5 * 60 * 60 * 1000),
    status: 'success',
    trigger: 'unassigned_shards > 0',
    stepsCompleted: 4,
    stepsTotal: 4
  },
  {
    id: 'REM-003',
    runbook: 'otel-collector-restart',
    service: 'OTEL Collector',
    startTime: new Date(Date.now() - 12 * 60 * 60 * 1000),
    endTime: new Date(Date.now() - 11.9 * 60 * 60 * 1000),
    status: 'success',
    trigger: 'dropped_spans > 100/s',
    stepsCompleted: 4,
    stepsTotal: 4
  },
  {
    id: 'REM-004',
    runbook: 'vm-storage-cleanup',
    service: 'VictoriaMetrics',
    startTime: new Date(Date.now() - 24 * 60 * 60 * 1000),
    endTime: new Date(Date.now() - 23 * 60 * 60 * 1000),
    status: 'partial',
    trigger: 'storage_usage > 85%',
    stepsCompleted: 3,
    stepsTotal: 4
  }
]

// Generate chart data
const generateMTTRTrendData = () => {
  const data = []
  for (let i = 30; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    data.push({
      time: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      mttr: Math.max(5, 15 + Math.random() * 10 - i * 0.3),
      mttd: Math.max(2, 5 + Math.random() * 5 - i * 0.1)
    })
  }
  return data
}

const generateIncidentTrendData = () => {
  const data = []
  for (let i = 7; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    data.push({
      time: date.toLocaleDateString('en-US', { weekday: 'short' }),
      incidents: Math.floor(Math.random() * 5) + 1,
      autoResolved: Math.floor(Math.random() * 4),
      manualResolved: Math.floor(Math.random() * 2)
    })
  }
  return data
}

// SLO Card Component
function SLOCard({ slo }) {
  const { t } = useI18n()
  const budgetRemaining = 100 - slo.budgetUsed

  const statusColors = {
    healthy: 'text-green-400',
    warning: 'text-yellow-400',
    critical: 'text-red-400'
  }

  const statusBgColors = {
    healthy: 'bg-green-500/20 border-green-500/30',
    warning: 'bg-yellow-500/20 border-yellow-500/30',
    critical: 'bg-red-500/20 border-red-500/30'
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className={`p-4 rounded-xl border ${statusBgColors[slo.status]} transition-all`}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="font-semibold text-white">{slo.name}</h4>
          <p className="text-xs text-gray-400">{slo.service}</p>
        </div>
        <StatusBadge status={slo.status} size="sm" />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-3">
        <div>
          <p className="text-xs text-gray-500 mb-1">{t('observability.current')}</p>
          <p className={`text-xl font-bold ${statusColors[slo.status]}`}>
            {slo.current}{slo.unit || '%'}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">{t('observability.target')}</p>
          <p className="text-xl font-bold text-gray-300">
            {slo.target}{slo.unit || '%'}
          </p>
        </div>
      </div>

      <div>
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-400">{t('observability.errorBudget')}</span>
          <span className={budgetRemaining < 20 ? 'text-red-400' : 'text-gray-400'}>
            {budgetRemaining.toFixed(1)}% {t('observability.remaining')}
          </span>
        </div>
        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${slo.budgetUsed}%` }}
            className={`h-full rounded-full ${
              slo.budgetUsed > 80 ? 'bg-red-500' :
              slo.budgetUsed > 60 ? 'bg-yellow-500' : 'bg-green-500'
            }`}
          />
        </div>
      </div>
    </motion.div>
  )
}

// Incident Card Component
function IncidentCard({ incident, expanded, onToggle }) {
  const { t, formatTime } = useI18n()
  const duration = Math.round((Date.now() - incident.startTime.getTime()) / 60000)

  const severityColors = {
    critical: 'border-red-500/50 bg-red-500/10',
    warning: 'border-yellow-500/50 bg-yellow-500/10',
    info: 'border-blue-500/50 bg-blue-500/10'
  }

  const severityIcons = {
    critical: <XCircle className="w-5 h-5 text-red-400" />,
    warning: <AlertTriangle className="w-5 h-5 text-yellow-400" />,
    info: <AlertCircle className="w-5 h-5 text-blue-400" />
  }

  return (
    <motion.div
      layout
      className={`rounded-xl border ${severityColors[incident.severity]} overflow-hidden`}
    >
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center gap-4 hover:bg-white/5 transition-colors"
      >
        {severityIcons[incident.severity]}

        <div className="flex-1 text-left">
          <div className="flex items-center gap-2">
            <span className="font-medium text-white">{incident.title}</span>
            <span className="text-xs px-2 py-0.5 rounded bg-white/10 text-gray-400">
              {incident.id}
            </span>
          </div>
          <div className="flex items-center gap-4 mt-1 text-sm text-gray-400">
            <span>{incident.service}</span>
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {duration}m
            </span>
            <span className="capitalize">{incident.status}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="px-3 py-1.5 rounded-lg bg-industrial-accent/20 text-industrial-accent hover:bg-industrial-accent/30 transition-colors text-sm">
            {t('observability.viewRunbook')}
          </button>
          <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${expanded ? 'rotate-180' : ''}`} />
        </div>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-white/10"
          >
            <div className="p-4 space-y-4">
              <div>
                <h5 className="text-sm font-medium text-gray-300 mb-2">{t('observability.remediationActions')}</h5>
                <div className="space-y-2">
                  {incident.actions.map((action, idx) => (
                    <div key={idx} className="flex items-center gap-3 text-sm">
                      {action.status === 'completed' ? (
                        <CheckCircle className="w-4 h-4 text-green-400" />
                      ) : action.status === 'in_progress' ? (
                        <RefreshCw className="w-4 h-4 text-yellow-400 animate-spin" />
                      ) : (
                        <Clock className="w-4 h-4 text-gray-500" />
                      )}
                      <span className="text-gray-400">{formatTime(action.time)}</span>
                      <span className="text-white">{action.action}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors">
                  <Play className="w-4 h-4" />
                  {t('observability.runNextStep')}
                </button>
                <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30 transition-colors">
                  <Pause className="w-4 h-4" />
                  {t('observability.pauseRemediation')}
                </button>
                <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors">
                  <RotateCcw className="w-4 h-4" />
                  {t('observability.escalate')}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Runbook Card Component
function RunbookCard({ runbook }) {
  const { t } = useI18n()
  const [expanded, setExpanded] = useState(false)

  return (
    <motion.div
      layout
      className="rounded-xl border border-industrial-border bg-industrial-card/50 overflow-hidden"
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center gap-4 hover:bg-white/5 transition-colors"
      >
        <div className="w-10 h-10 rounded-lg bg-industrial-accent/20 flex items-center justify-center">
          <BookOpen className="w-5 h-5 text-industrial-accent" />
        </div>

        <div className="flex-1 text-left">
          <h4 className="font-medium text-white">{runbook.name}</h4>
          <div className="flex items-center gap-4 mt-1 text-sm text-gray-400">
            <span>{runbook.service}</span>
            <span className="flex items-center gap-1">
              <PlayCircle className="w-3 h-3" />
              {runbook.executions} {t('observability.executions')}
            </span>
            <span className="flex items-center gap-1 text-green-400">
              <CheckCircle className="w-3 h-3" />
              {runbook.successRate}%
            </span>
          </div>
        </div>

        <div className="text-right">
          <p className="text-sm text-gray-400">{t('observability.avgMTTR')}</p>
          <p className="font-bold text-white">{runbook.avgMTTR}</p>
        </div>

        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${expanded ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-white/10"
          >
            <div className="p-4 space-y-4">
              <div>
                <h5 className="text-sm font-medium text-gray-300 mb-2">{t('observability.triggers')}</h5>
                <div className="flex flex-wrap gap-2">
                  {runbook.triggers.map((trigger, idx) => (
                    <span key={idx} className="px-3 py-1 rounded-lg bg-red-500/20 text-red-300 text-sm font-mono">
                      {trigger}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h5 className="text-sm font-medium text-gray-300 mb-2">{t('observability.steps')}</h5>
                <div className="space-y-2">
                  {runbook.steps.map((step, idx) => (
                    <div key={idx} className="flex items-center gap-3 p-2 rounded-lg bg-white/5">
                      <span className="w-6 h-6 rounded-full bg-industrial-accent/20 flex items-center justify-center text-sm text-industrial-accent">
                        {idx + 1}
                      </span>
                      <span className="flex-1 text-white">{step.name}</span>
                      {step.automated ? (
                        <span className="px-2 py-0.5 rounded text-xs bg-green-500/20 text-green-400">
                          {t('observability.automated')}
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-xs bg-yellow-500/20 text-yellow-400">
                          {t('observability.manual')}
                        </span>
                      )}
                      <span className="text-sm text-gray-400">{step.avgDuration}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-industrial-accent text-white hover:bg-industrial-accent/80 transition-colors">
                  <Play className="w-4 h-4" />
                  {t('observability.executeRunbook')}
                </button>
                <button className="px-4 py-2 rounded-lg bg-white/10 text-gray-300 hover:bg-white/20 transition-colors">
                  <Settings className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

function ObservabilityRemediationView() {
  const { metrics, userMode } = useDashboard()
  const { t, formatTime } = useI18n()
  const [expandedIncident, setExpandedIncident] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

  const mttrTrendData = useMemo(() => generateMTTRTrendData(), [])
  const incidentTrendData = useMemo(() => generateIncidentTrendData(), [])

  // Calculate summary metrics
  const summaryMetrics = useMemo(() => {
    const healthySLOs = sloData.filter(s => s.status === 'healthy').length
    const totalSLOs = sloData.length
    const avgMTTR = 12 // minutes
    const avgMTTD = 4 // minutes
    const automationRate = 78 // percentage

    return { healthySLOs, totalSLOs, avgMTTR, avgMTTD, automationRate }
  }, [])

  const tabs = [
    { id: 'overview', label: t('observability.tabs.overview'), icon: Eye },
    { id: 'incidents', label: t('observability.tabs.incidents'), icon: AlertTriangle },
    { id: 'runbooks', label: t('observability.tabs.runbooks'), icon: BookOpen },
    { id: 'history', label: t('observability.tabs.history'), icon: History }
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">{t('observability.title')}</h1>
          <p className="text-gray-400 mt-1">{t('observability.description')}</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-industrial-accent text-white hover:bg-industrial-accent/80 transition-colors">
            <Zap className="w-4 h-4" />
            {t('observability.quickActions')}
          </button>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-5 gap-4">
        <MetricCard
          label={t('observability.sloCompliance')}
          value={`${summaryMetrics.healthySLOs}/${summaryMetrics.totalSLOs}`}
          icon={Target}
          color="cyan"
          trend={{ value: 2, direction: 'up' }}
        />
        <MetricCard
          label={t('observability.activeIncidents')}
          value={activeIncidents.length}
          icon={AlertTriangle}
          color={activeIncidents.length > 0 ? 'red' : 'green'}
        />
        <MetricCard
          label={t('observability.mttr')}
          value={`${summaryMetrics.avgMTTR}m`}
          icon={Timer}
          color="purple"
          trend={{ value: 15, direction: 'down' }}
        />
        <MetricCard
          label={t('observability.mttd')}
          value={`${summaryMetrics.avgMTTD}m`}
          icon={Eye}
          color="blue"
          trend={{ value: 8, direction: 'down' }}
        />
        <MetricCard
          label={t('observability.automationRate')}
          value={`${summaryMetrics.automationRate}%`}
          icon={Zap}
          color="green"
          trend={{ value: 5, direction: 'up' }}
        />
      </div>

      {/* Tabs Navigation */}
      <div className="flex gap-2 border-b border-industrial-border pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors ${
              activeTab === tab.id
                ? 'bg-industrial-accent/20 text-industrial-accent border-b-2 border-industrial-accent'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* SLO Status Grid */}
            <Card>
              <CardHeader
                title={t('observability.sloStatus')}
                icon={Target}
                action={
                  <button className="text-sm text-industrial-accent hover:underline">
                    {t('common.viewAll')}
                  </button>
                }
              />
              <CardBody>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {sloData.map((slo) => (
                    <SLOCard key={slo.id} slo={slo} />
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Charts Row */}
            <div className="grid grid-cols-2 gap-6">
              <Card>
                <CardHeader title={t('observability.mttrTrend')} icon={TrendingDown} />
                <CardBody>
                  <TimeSeriesChart
                    data={mttrTrendData}
                    lines={[
                      { dataKey: 'mttr', name: 'MTTR', color: '#06b6d4' },
                      { dataKey: 'mttd', name: 'MTTD', color: '#8b5cf6' }
                    ]}
                    yAxisLabel={t('observability.minutes')}
                    height={250}
                  />
                </CardBody>
              </Card>

              <Card>
                <CardHeader title={t('observability.incidentTrend')} icon={BarChart3} />
                <CardBody>
                  <AreaChartComponent
                    data={incidentTrendData}
                    areas={[
                      { dataKey: 'autoResolved', name: t('observability.autoResolved'), color: '#22c55e', stackId: '1' },
                      { dataKey: 'manualResolved', name: t('observability.manualResolved'), color: '#f59e0b', stackId: '1' }
                    ]}
                    height={250}
                    stacked
                  />
                </CardBody>
              </Card>
            </div>

            {/* Active Incidents Preview */}
            {activeIncidents.length > 0 && (
              <Card>
                <CardHeader
                  title={t('observability.activeIncidents')}
                  icon={AlertTriangle}
                  action={
                    <button
                      onClick={() => setActiveTab('incidents')}
                      className="text-sm text-industrial-accent hover:underline flex items-center gap-1"
                    >
                      {t('common.viewAll')}
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  }
                />
                <CardBody>
                  <div className="space-y-3">
                    {activeIncidents.slice(0, 2).map((incident) => (
                      <IncidentCard
                        key={incident.id}
                        incident={incident}
                        expanded={expandedIncident === incident.id}
                        onToggle={() => setExpandedIncident(
                          expandedIncident === incident.id ? null : incident.id
                        )}
                      />
                    ))}
                  </div>
                </CardBody>
              </Card>
            )}
          </motion.div>
        )}

        {activeTab === 'incidents' && (
          <motion.div
            key="incidents"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader
                title={t('observability.allActiveIncidents')}
                icon={AlertTriangle}
                action={
                  <div className="flex gap-2">
                    <select className="px-3 py-1.5 rounded-lg bg-industrial-card border border-industrial-border text-sm text-white">
                      <option>{t('observability.allSeverities')}</option>
                      <option>{t('observability.critical')}</option>
                      <option>{t('observability.warning')}</option>
                    </select>
                    <select className="px-3 py-1.5 rounded-lg bg-industrial-card border border-industrial-border text-sm text-white">
                      <option>{t('observability.allServices')}</option>
                      <option>Kafka</option>
                      <option>VictoriaMetrics</option>
                      <option>OpenSearch</option>
                    </select>
                  </div>
                }
              />
              <CardBody>
                {activeIncidents.length > 0 ? (
                  <div className="space-y-3">
                    {activeIncidents.map((incident) => (
                      <IncidentCard
                        key={incident.id}
                        incident={incident}
                        expanded={expandedIncident === incident.id}
                        onToggle={() => setExpandedIncident(
                          expandedIncident === incident.id ? null : incident.id
                        )}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">{t('observability.noActiveIncidents')}</h3>
                    <p className="text-gray-400">{t('observability.allSystemsOperational')}</p>
                  </div>
                )}
              </CardBody>
            </Card>
          </motion.div>
        )}

        {activeTab === 'runbooks' && (
          <motion.div
            key="runbooks"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader
                title={t('observability.remediationRunbooks')}
                icon={BookOpen}
                action={
                  <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-industrial-accent text-white hover:bg-industrial-accent/80 transition-colors text-sm">
                    <FileText className="w-4 h-4" />
                    {t('observability.createRunbook')}
                  </button>
                }
              />
              <CardBody>
                <div className="grid gap-4">
                  {runbooks.map((runbook) => (
                    <RunbookCard key={runbook.id} runbook={runbook} />
                  ))}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {activeTab === 'history' && (
          <motion.div
            key="history"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader
                title={t('observability.remediationHistory')}
                icon={History}
                action={
                  <div className="flex gap-2">
                    <select className="px-3 py-1.5 rounded-lg bg-industrial-card border border-industrial-border text-sm text-white">
                      <option>{t('observability.last24h')}</option>
                      <option>{t('observability.last7d')}</option>
                      <option>{t('observability.last30d')}</option>
                    </select>
                    <button className="px-3 py-1.5 rounded-lg bg-white/10 text-gray-300 hover:bg-white/20 transition-colors text-sm">
                      {t('common.export')}
                    </button>
                  </div>
                }
              />
              <CardBody>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-industrial-border">
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">ID</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">{t('observability.runbook')}</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">{t('observability.service')}</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">{t('observability.trigger')}</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">{t('observability.duration')}</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">{t('observability.status')}</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">{t('observability.progress')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {remediationHistory.map((item) => {
                        const duration = Math.round((item.endTime - item.startTime) / 60000)
                        return (
                          <tr key={item.id} className="border-b border-industrial-border/50 hover:bg-white/5">
                            <td className="py-3 px-4 text-sm font-mono text-gray-300">{item.id}</td>
                            <td className="py-3 px-4 text-sm text-white">{item.runbook}</td>
                            <td className="py-3 px-4 text-sm text-gray-400">{item.service}</td>
                            <td className="py-3 px-4 text-sm font-mono text-yellow-400">{item.trigger}</td>
                            <td className="py-3 px-4 text-sm text-gray-300">{duration}m</td>
                            <td className="py-3 px-4">
                              <StatusBadge
                                status={item.status === 'success' ? 'healthy' : item.status === 'partial' ? 'warning' : 'down'}
                                label={item.status}
                                size="sm"
                              />
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex items-center gap-2">
                                <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden max-w-[100px]">
                                  <div
                                    className={`h-full rounded-full ${
                                      item.status === 'success' ? 'bg-green-500' : 'bg-yellow-500'
                                    }`}
                                    style={{ width: `${(item.stepsCompleted / item.stepsTotal) * 100}%` }}
                                  />
                                </div>
                                <span className="text-xs text-gray-400">
                                  {item.stepsCompleted}/{item.stepsTotal}
                                </span>
                              </div>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default ObservabilityRemediationView
