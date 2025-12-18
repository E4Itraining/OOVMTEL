import React, { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Activity,
  BarChart3,
  Layout,
  Bell,
  Users,
  Clock,
  ExternalLink,
  Eye,
  ChevronRight,
  RefreshCw,
  Maximize2
} from 'lucide-react'
import { useDashboard, USER_MODES } from '../context/DashboardContext'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { TimeSeriesChart, BarChartComponent } from '../components/ui/Charts'
import { StatusBadge } from '../components/ui/Status'
import { useI18n } from '../i18n'

const GRAFANA_URL = 'http://localhost:3000'

const dashboards = [
  {
    id: 'industrial-control-center',
    name: 'Industrial Control Center',
    description: 'Centre de contrôle avec OEE, alertes et monitoring équipements',
    category: 'business',
    panels: 12,
    views: 1250,
    lastUpdated: '2 min ago'
  },
  {
    id: 'unified-business-tech-view',
    name: 'Unified Business/Tech View',
    description: 'Vue unifiée des métriques business et techniques',
    category: 'both',
    panels: 18,
    views: 890,
    lastUpdated: '5 min ago'
  },
  {
    id: 'system-health-overview',
    name: 'System Health Overview',
    description: 'Santé de l\'infrastructure et des composants',
    category: 'tech',
    panels: 10,
    views: 650,
    lastUpdated: '1 min ago'
  },
  {
    id: 'pipeline-health',
    name: 'Pipeline Health',
    description: 'OTEL collector, Kafka throughput et data flow',
    category: 'tech',
    panels: 8,
    views: 420,
    lastUpdated: '3 min ago'
  },
  {
    id: 'realtime-streaming',
    name: 'Real-time Streaming',
    description: 'Ingestion temps réel et latences',
    category: 'tech',
    panels: 6,
    views: 380,
    lastUpdated: '1 min ago'
  },
  {
    id: 'ai-observability',
    name: 'AI Observability',
    description: 'Anomaly detection et maintenance prédictive',
    category: 'tech',
    panels: 9,
    views: 290,
    lastUpdated: '10 min ago'
  }
]

const alerts = [
  { id: 1, name: 'High CPU Usage', status: 'firing', severity: 'warning', since: '15 min' },
  { id: 2, name: 'Equipment Downtime', status: 'resolved', severity: 'critical', since: '2h ago' },
  { id: 3, name: 'Low OEE Alert', status: 'pending', severity: 'warning', since: '5 min' },
]

function GrafanaView() {
  const { userMode } = useDashboard()
  const { t } = useI18n()
  const [selectedCategory, setSelectedCategory] = useState('all')

  const filteredDashboards = useMemo(() => {
    if (selectedCategory === 'all') return dashboards
    if (selectedCategory === 'recommended') {
      return dashboards.filter(d =>
        userMode === USER_MODES.TECH
          ? ['tech', 'both'].includes(d.category)
          : ['business', 'both'].includes(d.category)
      )
    }
    return dashboards.filter(d => d.category === selectedCategory)
  }, [selectedCategory, userMode])

  const queryData = useMemo(() =>
    Array.from({ length: 24 }, (_, i) => ({
      time: `${String(i).padStart(2, '0')}:00`,
      queries: Math.floor(50 + Math.random() * 100),
      latency: Math.floor(10 + Math.random() * 30)
    }))
  , [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            {t('services.grafana.title')}
          </h1>
          <p className="text-gray-400 mt-1">{t('services.grafana.description')}</p>
        </div>
        <a
          href={GRAFANA_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
        >
          <ExternalLink className="w-4 h-4" />
          {t('services.grafana.explore')}
        </a>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Dashboards"
          value="6"
          icon={Layout}
          color="cyan"
        />
        <MetricCard
          label="Alertes Actives"
          value="2"
          icon={Bell}
          color="yellow"
        />
        <MetricCard
          label="Vues Aujourd'hui"
          value="3,890"
          icon={Eye}
          color="purple"
        />
        <MetricCard
          label="Utilisateurs"
          value="3"
          icon={Users}
          color="green"
        />
      </div>

      {/* Dashboard Category Filter */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {['all', 'recommended', 'business', 'tech'].map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all
              ${selectedCategory === cat
                ? 'bg-industrial-accent text-white'
                : 'bg-industrial-card text-gray-400 hover:text-white hover:bg-industrial-border'
              }`}
          >
            {cat === 'all' ? 'Tous' :
             cat === 'recommended' ? 'Recommandés' :
             cat === 'business' ? 'Business' : 'Technique'}
          </button>
        ))}
      </div>

      {/* Dashboards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredDashboards.map((dashboard, index) => (
          <motion.a
            key={dashboard.id}
            href={`${GRAFANA_URL}/d/${dashboard.id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="card p-4 group cursor-pointer"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`badge ${
                    dashboard.category === 'business' ? 'badge-info' :
                    dashboard.category === 'tech' ? 'badge-success' :
                    'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                  }`}>
                    {dashboard.category === 'both' ? 'Unified' : dashboard.category}
                  </span>
                </div>
                <h3 className="font-semibold text-white group-hover:text-industrial-accent transition-colors">
                  {dashboard.name}
                </h3>
                <p className="text-sm text-gray-400 mt-1 line-clamp-2">
                  {dashboard.description}
                </p>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-600 group-hover:text-industrial-accent transition-colors" />
            </div>
            <div className="flex items-center gap-4 mt-4 pt-3 border-t border-industrial-border/50 text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <BarChart3 className="w-3 h-3" />
                {dashboard.panels} panels
              </span>
              <span className="flex items-center gap-1">
                <Eye className="w-3 h-3" />
                {dashboard.views}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {dashboard.lastUpdated}
              </span>
            </div>
          </motion.a>
        ))}
      </div>

      {/* Alerts & Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Alerts */}
        <Card>
          <CardHeader title="Alertes Grafana" icon={Bell} />
          <CardBody>
            <div className="space-y-3">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-industrial-dark/50"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      alert.status === 'firing' ? 'bg-red-500 animate-pulse' :
                      alert.status === 'pending' ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`} />
                    <div>
                      <p className="font-medium text-white">{alert.name}</p>
                      <p className="text-xs text-gray-500">{alert.since}</p>
                    </div>
                  </div>
                  <StatusBadge status={alert.status} size="sm" />
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Query Performance */}
        <Card>
          <CardHeader title="Performance des Requêtes" icon={Activity} />
          <CardBody>
            <TimeSeriesChart
              data={queryData}
              lines={[
                { dataKey: 'queries', color: 'cyan', name: 'Queries/min' },
                { dataKey: 'latency', color: 'purple', name: 'Latency (ms)' }
              ]}
              height={200}
              showLegend
            />
          </CardBody>
        </Card>
      </div>

      {/* Embedded Preview */}
      <Card>
        <CardHeader
          title="Aperçu - Industrial Control Center"
          icon={Maximize2}
          action={
            <a
              href={`${GRAFANA_URL}/d/industrial-control-center`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-ghost text-sm"
            >
              <ExternalLink className="w-4 h-4" />
              Plein écran
            </a>
          }
        />
        <CardBody className="p-0">
          <div className="relative bg-industrial-dark rounded-b-xl overflow-hidden" style={{ height: '500px' }}>
            <iframe
              src={`${GRAFANA_URL}/d/industrial-control-center?orgId=1&kiosk=tv`}
              className="w-full h-full border-0"
              title="Grafana Dashboard Preview"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-industrial-dark via-transparent to-transparent pointer-events-none" />
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

export default GrafanaView
