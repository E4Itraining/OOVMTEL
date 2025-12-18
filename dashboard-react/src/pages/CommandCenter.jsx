import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Bell,
  CheckCircle2,
  ChevronRight,
  Clock,
  Database,
  Factory,
  Gauge,
  MessageSquare,
  Server,
  Shield,
  TrendingUp,
  Wifi,
  XCircle,
  Zap
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { HealthIndicator, StatusBadge } from '../components/ui/Status'
import { SemiCircleGauge } from '../components/ui/Gauge'

// Quick navigation cards for specialized views
const QUICK_NAV = [
  {
    id: 'technical',
    path: '/technical',
    icon: Server,
    color: 'from-cyan-500 to-cyan-600',
    bgColor: 'bg-cyan-500/10',
    borderColor: 'hover:border-cyan-500/50'
  },
  {
    id: 'business',
    path: '/business-kpi',
    icon: BarChart3,
    color: 'from-purple-500 to-purple-600',
    bgColor: 'bg-purple-500/10',
    borderColor: 'hover:border-purple-500/50'
  },
  {
    id: 'security',
    path: '/security',
    icon: Shield,
    color: 'from-red-500 to-red-600',
    bgColor: 'bg-red-500/10',
    borderColor: 'hover:border-red-500/50'
  },
  {
    id: 'observability',
    path: '/observability',
    icon: Activity,
    color: 'from-green-500 to-green-600',
    bgColor: 'bg-green-500/10',
    borderColor: 'hover:border-green-500/50'
  }
]

// System health status mock data
const SYSTEM_HEALTH = {
  overall: 94,
  services: [
    { name: 'VictoriaMetrics', status: 'healthy', latency: 12, icon: Database },
    { name: 'OpenSearch', status: 'healthy', latency: 45, icon: Database },
    { name: 'Kafka', status: 'degraded', latency: 89, icon: MessageSquare },
    { name: 'OTEL Collector', status: 'healthy', latency: 5, icon: Activity }
  ],
  alerts: [
    { id: 1, severity: 'warning', message: 'Kafka consumer lag increasing', time: '2 min ago', service: 'Kafka' },
    { id: 2, severity: 'info', message: 'Scheduled maintenance in 2 hours', time: '15 min ago', service: 'System' }
  ]
}

function QuickNavCard({ item, t }) {
  const navigate = useNavigate()
  const Icon = item.icon

  return (
    <motion.button
      onClick={() => navigate(item.path)}
      className={`relative p-5 rounded-xl border border-industrial-border bg-industrial-card/50
        ${item.borderColor} transition-all duration-300 text-left w-full group`}
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${item.color} flex items-center justify-center mb-3 shadow-lg group-hover:scale-110 transition-transform`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <h3 className="font-semibold text-white mb-1 group-hover:text-cyan-400 transition-colors">
        {t(`commandCenter.quickNav.${item.id}.title`)}
      </h3>
      <p className="text-xs text-gray-400 line-clamp-2">
        {t(`commandCenter.quickNav.${item.id}.description`)}
      </p>
      <ChevronRight className="absolute top-5 right-4 w-5 h-5 text-gray-600 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all" />
    </motion.button>
  )
}

function ServiceStatusRow({ service }) {
  const statusColors = {
    healthy: 'text-green-400',
    degraded: 'text-yellow-400',
    down: 'text-red-400'
  }

  const Icon = service.icon

  return (
    <div className="flex items-center justify-between py-3 border-b border-industrial-border/50 last:border-0">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-industrial-border/50 flex items-center justify-center">
          <Icon className="w-4 h-4 text-gray-400" />
        </div>
        <div>
          <p className="text-sm font-medium text-white">{service.name}</p>
          <p className={`text-xs ${statusColors[service.status]} capitalize`}>{service.status}</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-sm font-mono text-gray-300">{service.latency}ms</p>
        <p className="text-xs text-gray-500">latency</p>
      </div>
    </div>
  )
}

function AlertRow({ alert }) {
  const severityConfig = {
    critical: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10' },
    warning: { icon: AlertTriangle, color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
    info: { icon: Bell, color: 'text-blue-400', bg: 'bg-blue-500/10' }
  }

  const config = severityConfig[alert.severity] || severityConfig.info
  const Icon = config.icon

  return (
    <div className={`flex items-start gap-3 p-3 rounded-lg ${config.bg}`}>
      <Icon className={`w-5 h-5 mt-0.5 ${config.color}`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-white">{alert.message}</p>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-xs text-gray-400">{alert.service}</span>
          <span className="text-xs text-gray-600">•</span>
          <span className="text-xs text-gray-500">{alert.time}</span>
        </div>
      </div>
    </div>
  )
}

function CommandCenter() {
  const navigate = useNavigate()
  const { t } = useI18n()
  const { metrics, isConnected } = useDashboard()
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  // Get stored persona
  const storedPersona = localStorage.getItem('selectedPersona')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">
            {t('commandCenter.title')}
          </h1>
          <p className="text-gray-400 mt-1">
            {t('commandCenter.subtitle')}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-industrial-card border border-industrial-border">
            <Clock className="w-4 h-4 text-gray-400" />
            <span className="text-sm font-mono text-white">
              {currentTime.toLocaleTimeString()}
            </span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-industrial-card border border-industrial-border">
            {isConnected ? (
              <>
                <Wifi className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-400">{t('connection.realtime')}</span>
              </>
            ) : (
              <>
                <Wifi className="w-4 h-4 text-red-400" />
                <span className="text-sm text-red-400">{t('connection.offline')}</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Quick Navigation */}
      <div>
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">
          {t('commandCenter.quickAccess')}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {QUICK_NAV.map((item) => (
            <QuickNavCard key={item.id} item={item} t={t} />
          ))}
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Health Overview */}
        <Card className="lg:col-span-2">
          <CardHeader
            title={t('commandCenter.systemHealth.title')}
            subtitle={t('commandCenter.systemHealth.subtitle')}
            icon={Activity}
          />
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Overall Health Gauge */}
              <div className="flex flex-col items-center justify-center p-4">
                <SemiCircleGauge
                  value={SYSTEM_HEALTH.overall}
                  max={100}
                  label={t('commandCenter.systemHealth.overall')}
                  unit="%"
                  size={180}
                  color={SYSTEM_HEALTH.overall > 90 ? 'green' : SYSTEM_HEALTH.overall > 70 ? 'yellow' : 'red'}
                />
                <div className="mt-4 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-400" />
                  <span className="text-sm text-gray-300">
                    {SYSTEM_HEALTH.services.filter(s => s.status === 'healthy').length}/{SYSTEM_HEALTH.services.length} {t('commandCenter.systemHealth.servicesHealthy')}
                  </span>
                </div>
              </div>

              {/* Services Status */}
              <div className="space-y-1">
                <h4 className="text-sm font-medium text-gray-400 mb-3">
                  {t('commandCenter.systemHealth.backendServices')}
                </h4>
                {SYSTEM_HEALTH.services.map((service, idx) => (
                  <ServiceStatusRow key={idx} service={service} />
                ))}
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Alerts Panel */}
        <Card>
          <CardHeader
            title={t('commandCenter.alerts.title')}
            subtitle={`${SYSTEM_HEALTH.alerts.length} ${t('commandCenter.alerts.active')}`}
            icon={Bell}
            action={
              <button className="text-xs text-cyan-400 hover:text-cyan-300">
                {t('common.viewAll')}
              </button>
            }
          />
          <CardBody className="space-y-3">
            {SYSTEM_HEALTH.alerts.length > 0 ? (
              SYSTEM_HEALTH.alerts.map((alert) => (
                <AlertRow key={alert.id} alert={alert} />
              ))
            ) : (
              <div className="text-center py-8">
                <CheckCircle2 className="w-12 h-12 text-green-400 mx-auto mb-3" />
                <p className="text-gray-400">{t('commandCenter.alerts.noAlerts')}</p>
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* Key Metrics Row */}
      <div>
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">
          {t('commandCenter.keyMetrics')}
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <MetricCard
            label={t('metrics.business.oee')}
            value={metrics.business?.oee?.toFixed(1) || '0'}
            unit="%"
            icon={Gauge}
            color="purple"
          />
          <MetricCard
            label={t('metrics.business.productionToday')}
            value={metrics.business?.productionToday?.toLocaleString() || '0'}
            icon={Factory}
            color="cyan"
          />
          <MetricCard
            label={t('metrics.tech.metricsRate')}
            value={metrics.tech?.metricsRate?.toLocaleString() || '0'}
            unit="/s"
            icon={Activity}
            color="green"
          />
          <MetricCard
            label={t('metrics.tech.errorRate')}
            value={metrics.tech?.errorRate?.toFixed(2) || '0'}
            unit="%"
            icon={AlertTriangle}
            color={metrics.tech?.errorRate > 1 ? 'red' : 'green'}
          />
          <MetricCard
            label={t('metrics.tech.latencyP95')}
            value={metrics.tech?.latencyP95?.toFixed(0) || '0'}
            unit="ms"
            icon={Zap}
            color="yellow"
          />
          <MetricCard
            label={t('metrics.business.criticalAlarms')}
            value={metrics.business?.criticalAlarms || '0'}
            icon={Bell}
            color={metrics.business?.criticalAlarms > 0 ? 'red' : 'green'}
          />
        </div>
      </div>

      {/* AI Assistant Prompt */}
      <motion.button
        onClick={() => navigate('/ai-assistant')}
        className="w-full p-6 rounded-xl bg-gradient-to-r from-cyan-500/10 via-blue-500/10 to-purple-500/10 border border-cyan-500/30 hover:border-cyan-500/50 transition-all group"
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
              <MessageSquare className="w-7 h-7 text-white" />
            </div>
            <div className="text-left">
              <h3 className="text-lg font-semibold text-white group-hover:text-cyan-400 transition-colors">
                {t('commandCenter.aiAssistant.title')}
              </h3>
              <p className="text-sm text-gray-400">
                {t('commandCenter.aiAssistant.description')}
              </p>
            </div>
          </div>
          <ArrowRight className="w-6 h-6 text-gray-400 group-hover:text-cyan-400 group-hover:translate-x-2 transition-all" />
        </div>
      </motion.button>
    </div>
  )
}

export default CommandCenter
