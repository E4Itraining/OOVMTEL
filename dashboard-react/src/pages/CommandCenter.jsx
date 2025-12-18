import React, { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Activity,
  Shield,
  BarChart3,
  Server,
  FileCheck,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  ChevronRight,
  Zap,
  Eye,
  Target,
  Factory,
  Package,
  Clock,
  Award,
  Database,
  Cpu,
  Lock,
  CheckCircle,
  XCircle,
  AlertCircle,
  ArrowUpRight,
  Layers,
  RefreshCw,
  MessageSquare,
  Search,
  Gauge,
  LayoutGrid,
  List
} from 'lucide-react'
import { useDashboard, USER_MODES } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { RadialGauge, SemiCircleGauge } from '../components/ui/Gauge'
import { TimeSeriesChart, DonutChart } from '../components/ui/Charts'
import { StatusBadge, LoadingSpinner } from '../components/ui/Status'

// View types for the command center
const VIEW_TYPES = {
  GLOBAL: 'global',
  TECHNICAL: 'technical',
  SECURITY: 'security',
  COMPLIANCE: 'compliance',
  BUSINESS: 'business'
}

// Generate mock data
const generateTimeSeriesData = (points = 24, baseValue = 50, variance = 20) => {
  return Array.from({ length: points }, (_, i) => ({
    time: `${String(i).padStart(2, '0')}:00`,
    value: Math.max(0, baseValue + (Math.random() - 0.5) * variance)
  }))
}

// Health Score Component
function HealthScore({ score, label, size = 'md', color = 'auto' }) {
  const getColor = () => {
    if (color !== 'auto') return color
    if (score >= 90) return 'green'
    if (score >= 70) return 'yellow'
    return 'red'
  }

  const colorClass = getColor()
  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24',
    lg: 'w-32 h-32'
  }

  return (
    <div className="text-center">
      <div className={`relative ${sizeClasses[size]} mx-auto`}>
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="50%"
            cy="50%"
            r="45%"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-gray-700"
          />
          <circle
            cx="50%"
            cy="50%"
            r="45%"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            strokeDasharray={`${score * 2.83} 283`}
            className={`text-${colorClass}-500`}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-2xl font-bold text-${colorClass}-400`}>{score}</span>
        </div>
      </div>
      {label && <p className="text-sm text-gray-400 mt-2">{label}</p>}
    </div>
  )
}

// Quick Stat Card
function QuickStat({ icon: Icon, label, value, unit, trend, trendValue, color = 'cyan', onClick }) {
  return (
    <motion.div
      onClick={onClick}
      className={`p-4 rounded-xl bg-industrial-card/50 border border-industrial-border hover:border-${color}-500/50 transition-all cursor-pointer group`}
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className={`w-10 h-10 rounded-lg bg-${color}-500/10 flex items-center justify-center`}>
          <Icon className={`w-5 h-5 text-${color}-400`} />
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-xs ${trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
            {trend === 'up' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {trendValue}
          </div>
        )}
      </div>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-bold text-white">{value}</span>
        {unit && <span className="text-sm text-gray-500">{unit}</span>}
      </div>
      <p className="text-sm text-gray-400 mt-1">{label}</p>
      <div className="flex items-center gap-1 mt-2 text-xs text-gray-500 group-hover:text-industrial-accent transition-colors">
        <span>View details</span>
        <ArrowUpRight className="w-3 h-3" />
      </div>
    </motion.div>
  )
}

// View Card for navigation
function ViewCard({ icon: Icon, title, description, stats, color, gradient, onClick, isActive }) {
  return (
    <motion.div
      onClick={onClick}
      className={`relative p-6 rounded-2xl border-2 transition-all cursor-pointer overflow-hidden
        ${isActive
          ? `border-${color}-500 bg-gradient-to-br from-${color}-500/20 to-${color}-600/10`
          : 'border-industrial-border bg-industrial-card/50 hover:border-gray-600'
        }`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* Background glow */}
      {isActive && (
        <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-10`} />
      )}

      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          <ChevronRight className={`w-5 h-5 ${isActive ? `text-${color}-400` : 'text-gray-500'}`} />
        </div>

        <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
        <p className="text-sm text-gray-400 mb-4">{description}</p>

        {/* Mini stats */}
        <div className="flex items-center gap-4">
          {stats.map((stat, i) => (
            <div key={i} className="flex items-center gap-2">
              <stat.icon className={`w-4 h-4 text-${stat.color}-400`} />
              <span className="text-sm font-medium text-white">{stat.value}</span>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}

// Backend Source Badge
function BackendSource({ name, status, onClick }) {
  const statusColors = {
    healthy: 'green',
    warning: 'yellow',
    error: 'red'
  }
  const color = statusColors[status] || 'gray'

  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-industrial-card border border-industrial-border hover:border-gray-600 transition-all text-sm"
    >
      <span className={`w-2 h-2 rounded-full bg-${color}-500`} />
      <span className="text-gray-300">{name}</span>
      <ArrowUpRight className="w-3 h-3 text-gray-500" />
    </button>
  )
}

// Alert Item
function AlertItem({ severity, title, source, time, onDrillDown }) {
  const severityConfig = {
    critical: { color: 'red', icon: XCircle, bg: 'bg-red-500/10' },
    warning: { color: 'yellow', icon: AlertCircle, bg: 'bg-yellow-500/10' },
    info: { color: 'blue', icon: AlertCircle, bg: 'bg-blue-500/10' }
  }
  const config = severityConfig[severity] || severityConfig.info

  return (
    <motion.div
      className={`flex items-center gap-4 p-3 rounded-lg ${config.bg} cursor-pointer hover:bg-opacity-20 transition-all`}
      onClick={onDrillDown}
      whileHover={{ x: 4 }}
    >
      <config.icon className={`w-5 h-5 text-${config.color}-400 flex-shrink-0`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white truncate">{title}</p>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span>{source}</span>
          <span>•</span>
          <span>{time}</span>
        </div>
      </div>
      <ChevronRight className="w-4 h-4 text-gray-500" />
    </motion.div>
  )
}

// Global Overview Section
function GlobalOverview({ metrics, navigate, t }) {
  const overallHealth = useMemo(() => {
    const techHealth = 92
    const securityHealth = 88
    const complianceHealth = 95
    const businessHealth = 87
    return Math.round((techHealth + securityHealth + complianceHealth + businessHealth) / 4)
  }, [])

  const recentAlerts = [
    { severity: 'warning', title: 'High CPU usage on worker-node-03', source: 'VictoriaMetrics', time: '2 min ago' },
    { severity: 'critical', title: 'API response time exceeds SLO', source: 'OpenSearch', time: '5 min ago' },
    { severity: 'info', title: 'New security patch available', source: 'Security Scanner', time: '15 min ago' },
    { severity: 'warning', title: 'Kafka consumer lag increasing', source: 'Kafka', time: '20 min ago' }
  ]

  const backends = [
    { name: 'VictoriaMetrics', status: 'healthy' },
    { name: 'OpenSearch', status: 'healthy' },
    { name: 'Kafka', status: 'warning' },
    { name: 'OTEL Collector', status: 'healthy' },
    { name: 'Grafana', status: 'healthy' }
  ]

  return (
    <div className="space-y-6">
      {/* Top Row - Health Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Overall Health */}
        <motion.div
          className="lg:col-span-1 p-6 rounded-2xl bg-gradient-to-br from-industrial-card to-industrial-darker border border-industrial-border"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h3 className="text-lg font-semibold text-white mb-4">{t('commandCenter.overallHealth')}</h3>
          <SemiCircleGauge
            value={overallHealth}
            label={t('commandCenter.systemHealth')}
            size={180}
          />
          <div className="mt-4 flex items-center justify-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <span className="text-sm text-gray-400">{t('commandCenter.allSystemsOperational')}</span>
          </div>
        </motion.div>

        {/* Quick Stats Grid */}
        <div className="lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-4">
          <QuickStat
            icon={Factory}
            label={t('metrics.business.oee')}
            value={metrics.business?.oee || "87.5"}
            unit="%"
            trend="up"
            trendValue="+2.3%"
            color="purple"
            onClick={() => navigate('/business-kpi')}
          />
          <QuickStat
            icon={Gauge}
            label={t('metrics.tech.latencyP95')}
            value={metrics.tech?.latencyP95 || "23"}
            unit="ms"
            trend="down"
            trendValue="-3ms"
            color="cyan"
            onClick={() => navigate('/technical')}
          />
          <QuickStat
            icon={Shield}
            label={t('commandCenter.securityScore')}
            value="88"
            unit="/100"
            color="red"
            onClick={() => navigate('/security')}
          />
          <QuickStat
            icon={FileCheck}
            label={t('commandCenter.complianceScore')}
            value="95"
            unit="%"
            trend="up"
            trendValue="+2%"
            color="emerald"
            onClick={() => navigate('/security')}
          />
        </div>
      </div>

      {/* View Cards - Navigation Hub */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <ViewCard
          icon={Server}
          title={t('commandCenter.technicalView')}
          description={t('commandCenter.technicalDescription')}
          gradient="from-cyan-500 to-blue-500"
          color="cyan"
          stats={[
            { icon: Activity, value: '1.2K/s', color: 'cyan' },
            { icon: Database, value: '99.9%', color: 'green' }
          ]}
          onClick={() => navigate('/technical')}
        />
        <ViewCard
          icon={Shield}
          title={t('commandCenter.securityView')}
          description={t('commandCenter.securityDescription')}
          gradient="from-red-500 to-rose-500"
          color="red"
          stats={[
            { icon: AlertTriangle, value: '2', color: 'red' },
            { icon: Lock, value: '95%', color: 'green' }
          ]}
          onClick={() => navigate('/security')}
        />
        <ViewCard
          icon={FileCheck}
          title={t('commandCenter.complianceView')}
          description={t('commandCenter.complianceDescription')}
          gradient="from-emerald-500 to-teal-500"
          color="emerald"
          stats={[
            { icon: CheckCircle, value: '42/45', color: 'green' },
            { icon: Clock, value: '7d', color: 'gray' }
          ]}
          onClick={() => navigate('/security')}
        />
        <ViewCard
          icon={BarChart3}
          title={t('commandCenter.businessView')}
          description={t('commandCenter.businessDescription')}
          gradient="from-purple-500 to-pink-500"
          color="purple"
          stats={[
            { icon: TrendingUp, value: '+12%', color: 'green' },
            { icon: Target, value: '87%', color: 'purple' }
          ]}
          onClick={() => navigate('/business-kpi')}
        />
      </div>

      {/* Bottom Row - Alerts & Sources */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Alerts */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-industrial-card/50 border border-industrial-border">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-400" />
              {t('commandCenter.recentAlerts')}
            </h3>
            <button className="text-sm text-industrial-accent hover:underline">
              {t('common.viewAll')}
            </button>
          </div>
          <div className="space-y-2">
            {recentAlerts.map((alert, i) => (
              <AlertItem
                key={i}
                {...alert}
                onDrillDown={() => navigate('/observability')}
              />
            ))}
          </div>
        </div>

        {/* Data Sources */}
        <div className="p-6 rounded-2xl bg-industrial-card/50 border border-industrial-border">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Database className="w-5 h-5 text-cyan-400" />
              {t('commandCenter.dataSources')}
            </h3>
            <button className="p-2 rounded-lg hover:bg-white/5 transition-colors">
              <RefreshCw className="w-4 h-4 text-gray-400" />
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {backends.map((backend, i) => (
              <BackendSource
                key={i}
                {...backend}
                onClick={() => navigate(`/details/${backend.name.toLowerCase().replace(' ', '-')}`)}
              />
            ))}
          </div>

          <div className="mt-6 pt-4 border-t border-industrial-border">
            <h4 className="text-sm font-medium text-gray-400 mb-3">{t('commandCenter.dataFlow')}</h4>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Ingestion Rate</span>
              <span className="text-white font-medium">2.4K events/s</span>
            </div>
            <div className="flex items-center justify-between text-sm mt-2">
              <span className="text-gray-500">Processing Lag</span>
              <span className="text-green-400 font-medium">12ms</span>
            </div>
            <div className="flex items-center justify-between text-sm mt-2">
              <span className="text-gray-500">Storage Used</span>
              <span className="text-white font-medium">45.2 GB</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function CommandCenter() {
  const navigate = useNavigate()
  const { userMode, metrics, isLoading, selectedPersona } = useDashboard()
  const { t } = useI18n()
  const [viewMode, setViewMode] = useState('grid')

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <LoadingSpinner size="lg" label={t('common.loading')} />
      </div>
    )
  }

  return (
    <div>
      {/* Page Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-white">{t('commandCenter.title')}</h1>
            <span className="px-3 py-1 rounded-full bg-green-500/10 text-green-400 text-sm font-medium flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              {t('connection.realtime')}
            </span>
          </div>
          <p className="text-gray-400">{t('commandCenter.subtitle')}</p>
        </div>

        <div className="flex items-center gap-3">
          {/* View Toggle */}
          <div className="flex items-center gap-1 p-1 rounded-lg bg-industrial-card border border-industrial-border">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-md transition-colors ${viewMode === 'grid' ? 'bg-industrial-accent text-white' : 'text-gray-400 hover:text-white'}`}
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-md transition-colors ${viewMode === 'list' ? 'bg-industrial-accent text-white' : 'text-gray-400 hover:text-white'}`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>

          {/* AI Assistant Button */}
          <motion.button
            onClick={() => navigate('/assistant')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium shadow-lg shadow-purple-500/25"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <MessageSquare className="w-4 h-4" />
            {t('commandCenter.askAI')}
          </motion.button>
        </div>
      </div>

      {/* Main Content */}
      <GlobalOverview metrics={metrics} navigate={navigate} t={t} />
    </div>
  )
}

export default CommandCenter
