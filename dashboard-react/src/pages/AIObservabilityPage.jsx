import React, { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Brain,
  Activity,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  Eye,
  BarChart3,
  PieChart,
  Target,
  Shield,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  FileText,
  Settings,
  Zap,
  AlertCircle,
  XCircle,
  HelpCircle,
  Layers,
  GitBranch,
  Search,
  Filter,
  Download,
  ExternalLink,
  Gauge,
  Sparkles,
  Scale,
  BookOpen,
  MessageSquare
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { TimeSeriesChart, DonutChart, AreaChartComponent } from '../components/ui/Charts'
import { StatusBadge, StatusDot, HealthIndicator } from '../components/ui/Status'
import { RadialGauge, LinearGauge } from '../components/ui/Gauge'

// API base URL
const API_BASE = '/api/ai-observability'

// Mock data for initial state
const mockDashboardData = {
  overview: {
    total_models: 8,
    active_models: 8,
    avg_health_score: 92.5,
    healthy_count: 6,
    warning_count: 2,
    critical_count: 0
  },
  models: [
    { model_id: 'nlp-query-engine-v1', name: 'NLP Query Engine', version: '1.0.0', type: 'nlp_query', status: 'active', risk_level: 'minimal', deployment_target: 'central', tags: ['nlp', 'query'] },
    { model_id: 'rca-engine-v1', name: 'Root Cause Analysis Engine', version: '1.0.0', type: 'root_cause_analysis', status: 'active', risk_level: 'limited', deployment_target: 'central', tags: ['rca', 'causal'] },
    { model_id: 'predictive-maintenance-v1', name: 'Predictive Maintenance Engine', version: '1.0.0', type: 'predictive_maintenance', status: 'active', risk_level: 'limited', deployment_target: 'central', tags: ['predictive', 'rul'] },
    { model_id: 'anomaly-detector-zscore-v1', name: 'Z-Score Anomaly Detector', version: '1.0.0', type: 'anomaly_detection', status: 'active', risk_level: 'minimal', deployment_target: 'central', tags: ['anomaly', 'zscore'] },
    { model_id: 'time-series-forecaster-v1', name: 'Time Series Forecaster', version: '1.0.0', type: 'time_series_forecast', status: 'active', risk_level: 'minimal', deployment_target: 'central', tags: ['forecast', 'timeseries'] },
    { model_id: 'llm-assistant-mistral-v1', name: 'LLM Industrial Assistant', version: '1.0.0', type: 'llm_assistant', status: 'active', risk_level: 'limited', deployment_target: 'central', tags: ['llm', 'mistral'] },
    { model_id: 'edge-anomaly-detector-v1', name: 'Edge Anomaly Detector', version: '1.0.0', type: 'edge_inference', status: 'active', risk_level: 'minimal', deployment_target: 'edge', tags: ['edge', 'anomaly'] },
    { model_id: 'adaptive-threshold-v1', name: 'Adaptive Threshold Engine', version: '1.0.0', type: 'anomaly_detection', status: 'active', risk_level: 'minimal', deployment_target: 'central', tags: ['threshold', 'adaptive'] }
  ],
  performance: {
    models_tracked: 8,
    avg_health_score: 92.5,
    healthy_count: 6,
    warning_count: 2,
    critical_count: 0,
    active_alerts: 1,
    total_requests_tracked: 15420,
    slo_violations: 0
  },
  drift: {
    total_checks: 24,
    by_severity: { none: 20, low: 3, medium: 1, high: 0, critical: 0 },
    affected_models: ['predictive-maintenance-v1'],
    features_monitored: 9,
    requires_action: 0
  },
  explainability: {
    total_logged: 1250,
    logged_24h: 320,
    sampling_rate: 0.1,
    avg_confidence: 0.87,
    feedback_received: 45,
    corrections_applied: 3,
    models_covered: ['nlp-query-engine-v1', 'rca-engine-v1', 'predictive-maintenance-v1']
  },
  alerts: [],
  inventory: {
    total_models: 8,
    active_models: 8,
    by_type: { anomaly_detection: 2, predictive_maintenance: 1, root_cause_analysis: 1, nlp_query: 1, time_series_forecast: 1, llm_assistant: 1, edge_inference: 1 },
    by_risk_level: { minimal: 5, limited: 3, high: 0, unacceptable: 0 },
    requiring_oversight: 2
  }
}

// Generate performance trend data
const generatePerformanceTrendData = () => {
  const data = []
  for (let i = 24; i >= 0; i--) {
    const date = new Date()
    date.setHours(date.getHours() - i)
    data.push({
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      latency: Math.max(50, 100 + Math.random() * 50 - i * 0.5),
      requests: Math.floor(100 + Math.random() * 50),
      errors: Math.floor(Math.random() * 3)
    })
  }
  return data
}

// Generate drift trend data
const generateDriftTrendData = () => {
  const data = []
  for (let i = 7; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    data.push({
      time: date.toLocaleDateString('en-US', { weekday: 'short' }),
      dataScore: Math.random() * 0.15,
      predictionScore: Math.random() * 0.1,
      threshold: 0.25
    })
  }
  return data
}

// Model Type Icons
const modelTypeIcons = {
  anomaly_detection: AlertTriangle,
  predictive_maintenance: Activity,
  root_cause_analysis: GitBranch,
  nlp_query: MessageSquare,
  time_series_forecast: TrendingUp,
  llm_assistant: Sparkles,
  edge_inference: Cpu,
  classification: Layers,
  regression: BarChart3,
  custom: Brain
}

// Risk Level Colors
const riskLevelColors = {
  minimal: 'text-green-400 bg-green-500/20',
  limited: 'text-yellow-400 bg-yellow-500/20',
  high: 'text-orange-400 bg-orange-500/20',
  unacceptable: 'text-red-400 bg-red-500/20'
}

// Model Card Component
function ModelCard({ model, onClick }) {
  const { t } = useI18n()
  const IconComponent = modelTypeIcons[model.type] || Brain

  const healthScore = model.health?.overall_score || Math.round(85 + Math.random() * 15)
  const healthStatus = healthScore >= 90 ? 'healthy' : healthScore >= 70 ? 'warning' : 'critical'

  const statusColors = {
    healthy: 'border-green-500/30 bg-green-500/10',
    warning: 'border-yellow-500/30 bg-yellow-500/10',
    critical: 'border-red-500/30 bg-red-500/10'
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      onClick={onClick}
      className={`p-4 rounded-xl border ${statusColors[healthStatus]} cursor-pointer transition-all hover:shadow-lg`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg ${riskLevelColors[model.risk_level]} flex items-center justify-center`}>
            <IconComponent className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-semibold text-white text-sm">{model.name}</h4>
            <p className="text-xs text-gray-400">v{model.version}</p>
          </div>
        </div>
        <StatusBadge status={healthStatus} size="sm" />
      </div>

      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="text-center p-2 rounded-lg bg-white/5">
          <p className="text-lg font-bold text-white">{healthScore}</p>
          <p className="text-xs text-gray-500">Health</p>
        </div>
        <div className="text-center p-2 rounded-lg bg-white/5">
          <p className="text-lg font-bold text-cyan-400">{Math.round(50 + Math.random() * 100)}ms</p>
          <p className="text-xs text-gray-500">Latency</p>
        </div>
        <div className="text-center p-2 rounded-lg bg-white/5">
          <p className="text-lg font-bold text-green-400">{(99 + Math.random()).toFixed(1)}%</p>
          <p className="text-xs text-gray-500">Accuracy</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-1">
        {model.tags?.slice(0, 3).map((tag, idx) => (
          <span key={idx} className="px-2 py-0.5 rounded text-xs bg-white/10 text-gray-300">
            {tag}
          </span>
        ))}
        <span className={`px-2 py-0.5 rounded text-xs ${riskLevelColors[model.risk_level]}`}>
          {model.risk_level}
        </span>
      </div>
    </motion.div>
  )
}

// Health Score Gauge Component
function HealthScoreGauge({ score, status }) {
  const getColor = () => {
    if (score >= 90) return '#22c55e'
    if (score >= 70) return '#eab308'
    return '#ef4444'
  }

  return (
    <div className="relative w-40 h-40 mx-auto">
      <svg className="transform -rotate-90 w-full h-full" viewBox="0 0 100 100">
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="#1f2937"
          strokeWidth="8"
        />
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke={getColor()}
          strokeWidth="8"
          strokeDasharray={`${(score / 100) * 283} 283`}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-white">{score.toFixed(0)}</span>
        <span className="text-sm text-gray-400 capitalize">{status}</span>
      </div>
    </div>
  )
}

// Drift Indicator Component
function DriftIndicator({ severity, score }) {
  const severityColors = {
    none: 'bg-green-500',
    low: 'bg-yellow-500',
    medium: 'bg-orange-500',
    high: 'bg-red-500',
    critical: 'bg-red-600'
  }

  return (
    <div className="flex items-center gap-2">
      <div className={`w-3 h-3 rounded-full ${severityColors[severity]}`} />
      <span className="text-sm text-gray-300 capitalize">{severity}</span>
      <span className="text-xs text-gray-500">({(score * 100).toFixed(1)}%)</span>
    </div>
  )
}

// Alert Card Component
function AlertCard({ alert }) {
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
    <div className={`p-4 rounded-xl border ${severityColors[alert.severity]} flex items-start gap-3`}>
      {severityIcons[alert.severity]}
      <div className="flex-1">
        <h4 className="font-medium text-white">{alert.title}</h4>
        <p className="text-sm text-gray-400 mt-1">{alert.description}</p>
        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
          <span>{alert.model_id}</span>
          <span>{new Date(alert.timestamp).toLocaleString()}</span>
        </div>
      </div>
      {!alert.acknowledged && (
        <button className="px-3 py-1 rounded-lg bg-white/10 text-gray-300 hover:bg-white/20 text-sm">
          Acknowledge
        </button>
      )}
    </div>
  )
}

// Compliance Section Component
function ComplianceSection({ inventory }) {
  const { t } = useI18n()

  const complianceItems = [
    { label: 'Model Registry', status: 'compliant', icon: Database },
    { label: 'Risk Classification', status: 'compliant', icon: Scale },
    { label: 'Transparency Logging', status: 'compliant', icon: Eye },
    { label: 'Human Oversight', status: inventory?.requiring_oversight > 0 ? 'attention' : 'compliant', icon: Shield },
    { label: 'Drift Monitoring', status: 'compliant', icon: Activity },
    { label: 'Explainability', status: 'compliant', icon: HelpCircle }
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {complianceItems.map((item, idx) => (
        <div
          key={idx}
          className={`p-3 rounded-lg border ${
            item.status === 'compliant'
              ? 'border-green-500/30 bg-green-500/10'
              : 'border-yellow-500/30 bg-yellow-500/10'
          }`}
        >
          <div className="flex items-center gap-2">
            <item.icon className={`w-4 h-4 ${item.status === 'compliant' ? 'text-green-400' : 'text-yellow-400'}`} />
            <span className="text-sm text-white">{item.label}</span>
          </div>
          <p className={`text-xs mt-1 capitalize ${item.status === 'compliant' ? 'text-green-400' : 'text-yellow-400'}`}>
            {item.status}
          </p>
        </div>
      ))}
    </div>
  )
}

// Main Component
function AIObservabilityPage() {
  const { metrics, userMode } = useDashboard()
  const { t } = useI18n()
  const [dashboardData, setDashboardData] = useState(mockDashboardData)
  const [activeTab, setActiveTab] = useState('overview')
  const [selectedModel, setSelectedModel] = useState(null)
  const [loading, setLoading] = useState(false)

  const performanceTrendData = useMemo(() => generatePerformanceTrendData(), [])
  const driftTrendData = useMemo(() => generateDriftTrendData(), [])

  // Fetch dashboard data
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const response = await fetch(`${API_BASE}/dashboard`)
        if (response.ok) {
          const data = await response.json()
          setDashboardData(data)
        }
      } catch (error) {
        console.log('Using mock data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Eye },
    { id: 'models', label: 'Models', icon: Brain },
    { id: 'performance', label: 'Performance', icon: Activity },
    { id: 'drift', label: 'Drift Detection', icon: TrendingUp },
    { id: 'explainability', label: 'Explainability', icon: HelpCircle },
    { id: 'compliance', label: 'Compliance', icon: Shield }
  ]

  // Model type distribution for chart
  const modelTypeData = useMemo(() => {
    if (!dashboardData?.inventory?.by_type) return []
    return Object.entries(dashboardData.inventory.by_type)
      .filter(([_, count]) => count > 0)
      .map(([type, count]) => ({
        name: type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        value: count,
        color: `hsl(${Math.random() * 360}, 70%, 50%)`
      }))
  }, [dashboardData])

  // Risk level distribution
  const riskLevelData = useMemo(() => {
    if (!dashboardData?.inventory?.by_risk_level) return []
    const colors = { minimal: '#22c55e', limited: '#eab308', high: '#f97316', unacceptable: '#ef4444' }
    return Object.entries(dashboardData.inventory.by_risk_level)
      .filter(([_, count]) => count > 0)
      .map(([level, count]) => ({
        name: level.charAt(0).toUpperCase() + level.slice(1),
        value: count,
        color: colors[level]
      }))
  }, [dashboardData])

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Brain className="w-8 h-8 text-purple-400" />
            AI Observability
          </h1>
          <p className="text-gray-400 mt-1">
            Monitor, analyze, and explain your AI/ML models in production
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 text-gray-300 hover:bg-white/20 transition-colors">
            <Download className="w-4 h-4" />
            Export Report
          </button>
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600 text-white hover:bg-purple-700 transition-colors">
            <Zap className="w-4 h-4" />
            Run Analysis
          </button>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-6 gap-4">
        <MetricCard
          label="Total Models"
          value={dashboardData.overview?.total_models || 0}
          icon={Brain}
          color="purple"
        />
        <MetricCard
          label="Active Models"
          value={dashboardData.overview?.active_models || 0}
          icon={CheckCircle2}
          color="green"
        />
        <MetricCard
          label="Avg Health Score"
          value={`${dashboardData.overview?.avg_health_score?.toFixed(1) || 0}%`}
          icon={Activity}
          color="cyan"
          trend={{ value: 2.5, direction: 'up' }}
        />
        <MetricCard
          label="Drift Alerts"
          value={dashboardData.drift?.requires_action || 0}
          icon={TrendingUp}
          color={dashboardData.drift?.requires_action > 0 ? 'orange' : 'green'}
        />
        <MetricCard
          label="Predictions Logged"
          value={dashboardData.explainability?.logged_24h || 0}
          icon={Eye}
          color="blue"
        />
        <MetricCard
          label="Active Alerts"
          value={dashboardData.alerts?.length || 0}
          icon={AlertTriangle}
          color={dashboardData.alerts?.length > 0 ? 'red' : 'green'}
        />
      </div>

      {/* Tabs Navigation */}
      <div className="flex gap-2 border-b border-industrial-border pb-2 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? 'bg-purple-500/20 text-purple-400 border-b-2 border-purple-500'
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
            <div className="grid grid-cols-3 gap-6">
              {/* Health Score */}
              <Card>
                <CardHeader title="Overall AI Health" icon={Activity} />
                <CardBody>
                  <HealthScoreGauge
                    score={dashboardData.overview?.avg_health_score || 0}
                    status={dashboardData.overview?.avg_health_score >= 90 ? 'healthy' : 'warning'}
                  />
                  <div className="grid grid-cols-3 gap-2 mt-4">
                    <div className="text-center p-2 rounded-lg bg-green-500/10">
                      <p className="text-lg font-bold text-green-400">{dashboardData.overview?.healthy_count || 0}</p>
                      <p className="text-xs text-gray-500">Healthy</p>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-yellow-500/10">
                      <p className="text-lg font-bold text-yellow-400">{dashboardData.overview?.warning_count || 0}</p>
                      <p className="text-xs text-gray-500">Warning</p>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-red-500/10">
                      <p className="text-lg font-bold text-red-400">{dashboardData.overview?.critical_count || 0}</p>
                      <p className="text-xs text-gray-500">Critical</p>
                    </div>
                  </div>
                </CardBody>
              </Card>

              {/* Model Distribution */}
              <Card>
                <CardHeader title="Model Types" icon={PieChart} />
                <CardBody>
                  <DonutChart
                    data={modelTypeData}
                    height={200}
                    innerRadius={50}
                    outerRadius={80}
                  />
                </CardBody>
              </Card>

              {/* Risk Distribution */}
              <Card>
                <CardHeader title="Risk Classification (EU AI Act)" icon={Scale} />
                <CardBody>
                  <DonutChart
                    data={riskLevelData}
                    height={200}
                    innerRadius={50}
                    outerRadius={80}
                  />
                  <div className="mt-4 text-center">
                    <p className="text-sm text-gray-400">
                      {dashboardData.inventory?.requiring_oversight || 0} models require human oversight
                    </p>
                  </div>
                </CardBody>
              </Card>
            </div>

            {/* Performance Trend */}
            <Card>
              <CardHeader title="Performance Trend (24h)" icon={BarChart3} />
              <CardBody>
                <TimeSeriesChart
                  data={performanceTrendData}
                  lines={[
                    { dataKey: 'latency', name: 'Avg Latency (ms)', color: '#06b6d4' },
                    { dataKey: 'requests', name: 'Requests', color: '#8b5cf6' }
                  ]}
                  height={250}
                />
              </CardBody>
            </Card>

            {/* Active Alerts */}
            {dashboardData.alerts?.length > 0 && (
              <Card>
                <CardHeader
                  title="Active Alerts"
                  icon={AlertTriangle}
                  action={
                    <button className="text-sm text-purple-400 hover:underline">
                      View All
                    </button>
                  }
                />
                <CardBody>
                  <div className="space-y-3">
                    {dashboardData.alerts.slice(0, 3).map((alert, idx) => (
                      <AlertCard key={idx} alert={alert} />
                    ))}
                  </div>
                </CardBody>
              </Card>
            )}
          </motion.div>
        )}

        {activeTab === 'models' && (
          <motion.div
            key="models"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader
                title="Registered AI Models"
                icon={Brain}
                action={
                  <div className="flex gap-2">
                    <div className="relative">
                      <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search models..."
                        className="pl-9 pr-4 py-1.5 rounded-lg bg-industrial-card border border-industrial-border text-sm text-white w-48"
                      />
                    </div>
                    <select className="px-3 py-1.5 rounded-lg bg-industrial-card border border-industrial-border text-sm text-white">
                      <option>All Types</option>
                      <option>Anomaly Detection</option>
                      <option>Predictive</option>
                      <option>NLP</option>
                    </select>
                    <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-purple-600 text-white text-sm">
                      Register Model
                    </button>
                  </div>
                }
              />
              <CardBody>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {dashboardData.models?.map((model) => (
                    <ModelCard
                      key={model.model_id}
                      model={model}
                      onClick={() => setSelectedModel(model)}
                    />
                  ))}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {activeTab === 'performance' && (
          <motion.div
            key="performance"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="grid grid-cols-4 gap-4">
              <MetricCard
                label="Total Inferences"
                value={dashboardData.performance?.total_requests_tracked?.toLocaleString() || '0'}
                icon={Zap}
                color="purple"
              />
              <MetricCard
                label="Avg Latency P99"
                value="145ms"
                icon={Clock}
                color="cyan"
                trend={{ value: 5, direction: 'down' }}
              />
              <MetricCard
                label="Error Rate"
                value="0.02%"
                icon={AlertTriangle}
                color="green"
              />
              <MetricCard
                label="SLO Compliance"
                value={`${100 - (dashboardData.performance?.slo_violations || 0)}%`}
                icon={Target}
                color="green"
              />
            </div>

            <Card>
              <CardHeader title="Model Performance Metrics" icon={Activity} />
              <CardBody>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-industrial-border">
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Model</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Status</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Latency P50</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Latency P99</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Requests/s</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Error Rate</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Health</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dashboardData.models?.map((model) => (
                        <tr key={model.model_id} className="border-b border-industrial-border/50 hover:bg-white/5">
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              <Brain className="w-4 h-4 text-purple-400" />
                              <span className="text-white">{model.name}</span>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <StatusBadge status="healthy" size="sm" />
                          </td>
                          <td className="py-3 px-4 text-gray-300">{Math.round(30 + Math.random() * 50)}ms</td>
                          <td className="py-3 px-4 text-gray-300">{Math.round(80 + Math.random() * 100)}ms</td>
                          <td className="py-3 px-4 text-gray-300">{(Math.random() * 50).toFixed(1)}</td>
                          <td className="py-3 px-4 text-green-400">{(Math.random() * 0.1).toFixed(2)}%</td>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
                                <div className="h-full bg-green-500 rounded-full" style={{ width: `${85 + Math.random() * 15}%` }} />
                              </div>
                              <span className="text-sm text-gray-400">{Math.round(85 + Math.random() * 15)}%</span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {activeTab === 'drift' && (
          <motion.div
            key="drift"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="grid grid-cols-4 gap-4">
              <MetricCard
                label="Features Monitored"
                value={dashboardData.drift?.features_monitored || 0}
                icon={Database}
                color="blue"
              />
              <MetricCard
                label="Drift Checks (24h)"
                value={dashboardData.drift?.total_checks || 0}
                icon={Activity}
                color="cyan"
              />
              <MetricCard
                label="Affected Models"
                value={dashboardData.drift?.affected_models?.length || 0}
                icon={AlertTriangle}
                color={dashboardData.drift?.affected_models?.length > 0 ? 'orange' : 'green'}
              />
              <MetricCard
                label="Requires Action"
                value={dashboardData.drift?.requires_action || 0}
                icon={Zap}
                color={dashboardData.drift?.requires_action > 0 ? 'red' : 'green'}
              />
            </div>

            <div className="grid grid-cols-2 gap-6">
              <Card>
                <CardHeader title="Drift Score Trend" icon={TrendingUp} />
                <CardBody>
                  <AreaChartComponent
                    data={driftTrendData}
                    areas={[
                      { dataKey: 'dataScore', name: 'Data Drift', color: '#06b6d4', stackId: '1' },
                      { dataKey: 'predictionScore', name: 'Prediction Drift', color: '#8b5cf6', stackId: '2' }
                    ]}
                    height={250}
                  />
                </CardBody>
              </Card>

              <Card>
                <CardHeader title="Drift by Severity" icon={AlertTriangle} />
                <CardBody>
                  <div className="space-y-4">
                    {Object.entries(dashboardData.drift?.by_severity || {}).map(([severity, count]) => (
                      <div key={severity} className="flex items-center justify-between">
                        <DriftIndicator severity={severity} score={count / (dashboardData.drift?.total_checks || 1)} />
                        <span className="text-lg font-bold text-white">{count}</span>
                      </div>
                    ))}
                  </div>
                </CardBody>
              </Card>
            </div>

            <Card>
              <CardHeader title="Feature Drift Analysis" icon={Layers} />
              <CardBody>
                <div className="grid grid-cols-3 gap-4">
                  {['temperature', 'pressure', 'vibration', 'flow_rate', 'cycle_time', 'oee'].map((feature) => (
                    <div key={feature} className="p-4 rounded-lg border border-industrial-border bg-industrial-card/50">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-medium">{feature.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                        <StatusDot status={Math.random() > 0.2 ? 'up' : 'warning'} />
                      </div>
                      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${Math.random() > 0.7 ? 'bg-yellow-500' : 'bg-green-500'}`}
                          style={{ width: `${Math.random() * 30}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">PSI: {(Math.random() * 0.2).toFixed(3)}</p>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {activeTab === 'explainability' && (
          <motion.div
            key="explainability"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="grid grid-cols-4 gap-4">
              <MetricCard
                label="Predictions Logged"
                value={dashboardData.explainability?.total_logged?.toLocaleString() || '0'}
                icon={Eye}
                color="purple"
              />
              <MetricCard
                label="Logged (24h)"
                value={dashboardData.explainability?.logged_24h || 0}
                icon={Clock}
                color="cyan"
              />
              <MetricCard
                label="Avg Confidence"
                value={`${((dashboardData.explainability?.avg_confidence || 0) * 100).toFixed(0)}%`}
                icon={Target}
                color="green"
              />
              <MetricCard
                label="Human Feedback"
                value={dashboardData.explainability?.feedback_received || 0}
                icon={MessageSquare}
                color="blue"
              />
            </div>

            <div className="grid grid-cols-2 gap-6">
              <Card>
                <CardHeader title="Explanation Methods" icon={HelpCircle} />
                <CardBody>
                  <div className="space-y-4">
                    {[
                      { method: 'Feature Importance', count: 450, pct: 36 },
                      { method: 'SHAP Values', count: 380, pct: 30 },
                      { method: 'Decision Path', count: 250, pct: 20 },
                      { method: 'Attention Weights', count: 170, pct: 14 }
                    ].map((item) => (
                      <div key={item.method}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-300">{item.method}</span>
                          <span className="text-gray-500">{item.count} ({item.pct}%)</span>
                        </div>
                        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                          <div className="h-full bg-purple-500 rounded-full" style={{ width: `${item.pct}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardBody>
              </Card>

              <Card>
                <CardHeader title="Top Contributing Features" icon={BarChart3} />
                <CardBody>
                  <div className="space-y-3">
                    {[
                      { feature: 'temperature', importance: 0.28 },
                      { feature: 'vibration', importance: 0.22 },
                      { feature: 'pressure', importance: 0.18 },
                      { feature: 'operating_hours', importance: 0.15 },
                      { feature: 'load_factor', importance: 0.12 }
                    ].map((item) => (
                      <div key={item.feature} className="flex items-center gap-3">
                        <span className="text-gray-300 w-32">{item.feature}</span>
                        <div className="flex-1 h-4 bg-gray-700 rounded overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-purple-500 to-cyan-500 rounded"
                            style={{ width: `${item.importance * 100}%` }}
                          />
                        </div>
                        <span className="text-gray-400 w-12 text-right">{(item.importance * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>
                </CardBody>
              </Card>
            </div>

            <Card>
              <CardHeader
                title="Recent Prediction Audit Logs"
                icon={FileText}
                action={
                  <button className="text-sm text-purple-400 hover:underline">
                    View All Logs
                  </button>
                }
              />
              <CardBody>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-industrial-border">
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Prediction ID</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Model</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Confidence</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Latency</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Top Feature</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Timestamp</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[1, 2, 3, 4, 5].map((i) => (
                        <tr key={i} className="border-b border-industrial-border/50 hover:bg-white/5">
                          <td className="py-3 px-4 text-sm font-mono text-gray-300">pred-{Date.now() - i * 60000}</td>
                          <td className="py-3 px-4 text-sm text-white">Predictive Maintenance</td>
                          <td className="py-3 px-4 text-sm text-green-400">{(85 + Math.random() * 15).toFixed(1)}%</td>
                          <td className="py-3 px-4 text-sm text-gray-300">{Math.round(50 + Math.random() * 100)}ms</td>
                          <td className="py-3 px-4 text-sm text-cyan-400">temperature</td>
                          <td className="py-3 px-4 text-sm text-gray-500">{new Date(Date.now() - i * 60000).toLocaleTimeString()}</td>
                          <td className="py-3 px-4">
                            <button className="text-purple-400 hover:underline text-sm">
                              Explain
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {activeTab === 'compliance' && (
          <motion.div
            key="compliance"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader
                title="EU AI Act Compliance Status"
                icon={Shield}
                action={
                  <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-purple-600 text-white text-sm">
                    <Download className="w-4 h-4" />
                    Export Compliance Report
                  </button>
                }
              />
              <CardBody>
                <div className="flex items-center gap-6 mb-6 p-4 rounded-lg bg-green-500/10 border border-green-500/30">
                  <CheckCircle2 className="w-12 h-12 text-green-400" />
                  <div>
                    <h3 className="text-xl font-bold text-green-400">Compliant</h3>
                    <p className="text-gray-400">All AI systems meet EU AI Act requirements</p>
                  </div>
                </div>

                <ComplianceSection inventory={dashboardData.inventory} />
              </CardBody>
            </Card>

            <div className="grid grid-cols-2 gap-6">
              <Card>
                <CardHeader title="Risk Classification Inventory" icon={Scale} />
                <CardBody>
                  <div className="space-y-4">
                    {[
                      { level: 'Minimal', count: dashboardData.inventory?.by_risk_level?.minimal || 0, color: 'green', desc: 'Voluntary codes of conduct' },
                      { level: 'Limited', count: dashboardData.inventory?.by_risk_level?.limited || 0, color: 'yellow', desc: 'Transparency obligations' },
                      { level: 'High', count: dashboardData.inventory?.by_risk_level?.high || 0, color: 'orange', desc: 'Strict requirements' },
                      { level: 'Unacceptable', count: dashboardData.inventory?.by_risk_level?.unacceptable || 0, color: 'red', desc: 'Prohibited' }
                    ].map((item) => (
                      <div key={item.level} className={`p-4 rounded-lg border border-${item.color}-500/30 bg-${item.color}-500/10`}>
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className={`font-semibold text-${item.color}-400`}>{item.level} Risk</h4>
                            <p className="text-xs text-gray-500">{item.desc}</p>
                          </div>
                          <span className="text-2xl font-bold text-white">{item.count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardBody>
              </Card>

              <Card>
                <CardHeader title="Human Oversight Requirements" icon={Eye} />
                <CardBody>
                  <div className="text-center py-6">
                    <div className="w-24 h-24 rounded-full bg-purple-500/20 flex items-center justify-center mx-auto mb-4">
                      <span className="text-3xl font-bold text-purple-400">
                        {dashboardData.inventory?.requiring_oversight || 0}
                      </span>
                    </div>
                    <h4 className="text-lg font-semibold text-white">Models Requiring Oversight</h4>
                    <p className="text-gray-400 mt-2 text-sm">
                      These models are classified as limited or high risk and require human oversight for critical decisions
                    </p>
                  </div>

                  <div className="mt-4 space-y-2">
                    {dashboardData.models?.filter(m => m.risk_level === 'limited' || m.risk_level === 'high').map((model) => (
                      <div key={model.model_id} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                        <div className="flex items-center gap-2">
                          <Brain className="w-4 h-4 text-purple-400" />
                          <span className="text-white text-sm">{model.name}</span>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-xs ${riskLevelColors[model.risk_level]}`}>
                          {model.risk_level}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardBody>
              </Card>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Model Detail Modal */}
      <AnimatePresence>
        {selectedModel && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setSelectedModel(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-industrial-card rounded-xl border border-industrial-border p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl ${riskLevelColors[selectedModel.risk_level]} flex items-center justify-center`}>
                    <Brain className="w-6 h-6" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">{selectedModel.name}</h2>
                    <p className="text-gray-400">v{selectedModel.version} - {selectedModel.type}</p>
                  </div>
                </div>
                <button onClick={() => setSelectedModel(null)} className="text-gray-400 hover:text-white">
                  <XCircle className="w-6 h-6" />
                </button>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="p-4 rounded-lg bg-white/5 text-center">
                  <p className="text-2xl font-bold text-green-400">{Math.round(85 + Math.random() * 15)}</p>
                  <p className="text-sm text-gray-500">Health Score</p>
                </div>
                <div className="p-4 rounded-lg bg-white/5 text-center">
                  <p className="text-2xl font-bold text-cyan-400">{Math.round(50 + Math.random() * 100)}ms</p>
                  <p className="text-sm text-gray-500">Avg Latency</p>
                </div>
                <div className="p-4 rounded-lg bg-white/5 text-center">
                  <p className="text-2xl font-bold text-purple-400">{(Math.random() * 0.1).toFixed(2)}%</p>
                  <p className="text-sm text-gray-500">Error Rate</p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="p-4 rounded-lg border border-industrial-border">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Risk Level</h4>
                  <span className={`px-3 py-1 rounded-lg text-sm ${riskLevelColors[selectedModel.risk_level]}`}>
                    {selectedModel.risk_level.toUpperCase()} RISK
                  </span>
                </div>

                <div className="p-4 rounded-lg border border-industrial-border">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Deployment Target</h4>
                  <p className="text-white">{selectedModel.deployment_target}</p>
                </div>

                <div className="p-4 rounded-lg border border-industrial-border">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedModel.tags?.map((tag, idx) => (
                      <span key={idx} className="px-2 py-1 rounded bg-white/10 text-gray-300 text-sm">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-purple-600 text-white hover:bg-purple-700">
                  <Eye className="w-4 h-4" />
                  View Details
                </button>
                <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-white/10 text-gray-300 hover:bg-white/20">
                  <FileText className="w-4 h-4" />
                  Transparency Report
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default AIObservabilityPage
