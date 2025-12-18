import React, { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Search,
  Database,
  FileText,
  Server,
  HardDrive,
  Clock,
  ExternalLink,
  Filter,
  RefreshCw,
  TrendingUp,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'
import { useDashboard, USER_MODES } from '../context/DashboardContext'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { TimeSeriesChart, BarChartComponent, DonutChart } from '../components/ui/Charts'
import { StatusBadge } from '../components/ui/Status'
import { useI18n } from '../i18n'

const OPENSEARCH_URL = 'http://localhost:5601'

const indices = [
  { name: 'industrial-logs', docs: 1250000, size: '2.4GB', status: 'green', shards: 5 },
  { name: 'industrial-metrics', docs: 890000, size: '1.8GB', status: 'green', shards: 3 },
  { name: 'industrial-traces', docs: 450000, size: '980MB', status: 'green', shards: 3 },
  { name: 'scada-events', docs: 125000, size: '320MB', status: 'green', shards: 2 },
  { name: 'mes-events', docs: 89000, size: '180MB', status: 'yellow', shards: 2 },
]

const recentLogs = [
  { timestamp: '14:32:15', level: 'ERROR', source: 'SCADA-01', message: 'Connection timeout to PLC controller' },
  { timestamp: '14:32:10', level: 'WARN', source: 'MES-02', message: 'Production rate below threshold' },
  { timestamp: '14:32:05', level: 'INFO', source: 'OPC-UA', message: 'Node subscription renewed' },
  { timestamp: '14:32:00', level: 'INFO', source: 'OTEL', message: 'Batch exported successfully' },
  { timestamp: '14:31:55', level: 'DEBUG', source: 'Kafka', message: 'Consumer group rebalanced' },
]

function OpenSearchView() {
  const { userMode, metrics } = useDashboard()
  const { t } = useI18n()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState('all')

  const ingestionData = useMemo(() =>
    Array.from({ length: 24 }, (_, i) => ({
      time: `${String(i).padStart(2, '0')}:00`,
      logs: Math.floor(400 + Math.random() * 200),
      traces: Math.floor(100 + Math.random() * 100)
    }))
  , [])

  const logLevelData = useMemo(() => [
    { name: 'INFO', value: 65, color: '#22c55e' },
    { name: 'WARN', value: 20, color: '#f59e0b' },
    { name: 'ERROR', value: 10, color: '#ef4444' },
    { name: 'DEBUG', value: 5, color: '#64748b' },
  ], [])

  const clusterHealth = {
    status: 'green',
    nodes: 3,
    activePrimaryShards: 15,
    activeShards: 30,
    relocatingShards: 0,
    initializingShards: 0,
    unassignedShards: 0
  }

  const levelColors = {
    ERROR: 'text-red-400 bg-red-500/10',
    WARN: 'text-yellow-400 bg-yellow-500/10',
    INFO: 'text-green-400 bg-green-500/10',
    DEBUG: 'text-gray-400 bg-gray-500/10',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Search className="w-6 h-6 text-white" />
            </div>
            {t('services.opensearch.title')}
          </h1>
          <p className="text-gray-400 mt-1">{t('services.opensearch.description')}</p>
        </div>
        <a
          href={OPENSEARCH_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
        >
          <ExternalLink className="w-4 h-4" />
          {t('services.opensearch.discover')}
        </a>
      </div>

      {/* Search Bar */}
      <Card className="p-4">
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher dans les logs... (ex: error OR warn, source:SCADA-*)"
              className="w-full pl-10 pr-4 py-3 bg-industrial-dark border border-industrial-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-industrial-accent"
            />
          </div>
          <select
            value={selectedIndex}
            onChange={(e) => setSelectedIndex(e.target.value)}
            className="px-4 py-3 bg-industrial-dark border border-industrial-border rounded-lg text-white focus:outline-none focus:border-industrial-accent"
          >
            <option value="all">Tous les indices</option>
            {indices.map(idx => (
              <option key={idx.name} value={idx.name}>{idx.name}</option>
            ))}
          </select>
          <button className="btn btn-secondary">
            <Filter className="w-4 h-4" />
            Filtres
          </button>
        </div>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Documents Totaux"
          value={metrics.tech?.osDocuments?.toLocaleString() || "2.8M"}
          icon={FileText}
          color="cyan"
        />
        <MetricCard
          label="Cluster Health"
          value={clusterHealth.status.toUpperCase()}
          icon={CheckCircle}
          color="green"
        />
        <MetricCard
          label="Nodes Actifs"
          value={clusterHealth.nodes.toString()}
          icon={Server}
          color="purple"
        />
        <MetricCard
          label="Stockage Total"
          value="5.7"
          unit="GB"
          icon={HardDrive}
          color="yellow"
        />
      </div>

      {/* Indices Table & Log Levels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Indices */}
        <Card className="lg:col-span-2">
          <CardHeader title="Indices" icon={Database} />
          <CardBody className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-industrial-border">
                    <th className="text-left p-4 text-sm font-medium text-gray-400">Index</th>
                    <th className="text-left p-4 text-sm font-medium text-gray-400">Documents</th>
                    <th className="text-left p-4 text-sm font-medium text-gray-400">Taille</th>
                    <th className="text-left p-4 text-sm font-medium text-gray-400">Shards</th>
                    <th className="text-left p-4 text-sm font-medium text-gray-400">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {indices.map((idx) => (
                    <motion.tr
                      key={idx.name}
                      className="border-b border-industrial-border/50 hover:bg-industrial-dark/50 cursor-pointer"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      <td className="p-4">
                        <span className="font-medium text-white">{idx.name}</span>
                      </td>
                      <td className="p-4 text-gray-300">{idx.docs.toLocaleString()}</td>
                      <td className="p-4 text-gray-300">{idx.size}</td>
                      <td className="p-4 text-gray-300">{idx.shards}</td>
                      <td className="p-4">
                        <StatusBadge status={idx.status} size="sm" />
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>

        {/* Log Levels Distribution - ENHANCED with center label */}
        <Card>
          <CardHeader title="Distribution Logs" icon={TrendingUp} />
          <CardBody>
            <DonutChart
              data={logLevelData}
              height={180}
              innerRadius={45}
              outerRadius={70}
              centerValue="2.8M"
              centerLabel="Total Logs"
              showLabels
              labelType="percent"
            />
            <div className="mt-4 space-y-2">
              {logLevelData.map((level) => (
                <div key={level.name} className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: level.color }} />
                    <span className="text-gray-400">{level.name}</span>
                  </span>
                  <span className="text-white font-medium">{level.value}%</span>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Ingestion Chart & Recent Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ingestion Rate - ENHANCED with dual axis and thresholds */}
        <Card>
          <CardHeader title="Taux d'Ingestion (24h)" icon={TrendingUp} />
          <CardBody>
            <TimeSeriesChart
              data={ingestionData}
              lines={[
                { dataKey: 'logs', color: 'cyan', name: 'Logs' }
              ]}
              height={280}
              showLegend
              yAxisLabel="Logs"
              yAxisUnit="rec/s"
              xAxisLabel="Heure"
              dualYAxis
              rightAxisLabel="Traces"
              rightAxisUnit="rec/s"
              rightAxisLines={[
                { dataKey: 'traces', color: 'purple', name: 'Traces', dashed: true }
              ]}
              warningThreshold={550}
              criticalThreshold={650}
              showThresholdZones
              enableBrush
              brushHeight={30}
            />
          </CardBody>
        </Card>

        {/* Recent Logs */}
        <Card>
          <CardHeader
            title="Logs Récents"
            icon={FileText}
            action={
              <button className="btn btn-ghost text-sm">
                <RefreshCw className="w-4 h-4" />
              </button>
            }
          />
          <CardBody className="p-0">
            <div className="divide-y divide-industrial-border/50 max-h-[300px] overflow-y-auto scrollbar-thin">
              {recentLogs.map((log, i) => (
                <motion.div
                  key={i}
                  className="p-3 hover:bg-industrial-dark/50"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-gray-500 font-mono">{log.timestamp}</span>
                    <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${levelColors[log.level]}`}>
                      {log.level}
                    </span>
                    <span className="text-xs text-gray-400">{log.source}</span>
                  </div>
                  <p className="text-sm text-gray-300 font-mono">{log.message}</p>
                </motion.div>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Cluster Health Details */}
      <Card>
        <CardHeader title="Cluster Health Details" icon={Server} />
        <CardBody>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            {[
              { label: 'Active Primary', value: clusterHealth.activePrimaryShards, color: 'green' },
              { label: 'Active Total', value: clusterHealth.activeShards, color: 'cyan' },
              { label: 'Relocating', value: clusterHealth.relocatingShards, color: 'yellow' },
              { label: 'Initializing', value: clusterHealth.initializingShards, color: 'purple' },
              { label: 'Unassigned', value: clusterHealth.unassignedShards, color: clusterHealth.unassignedShards > 0 ? 'red' : 'green' },
              { label: 'Total Nodes', value: clusterHealth.nodes, color: 'cyan' },
            ].map((item) => (
              <div key={item.label} className="text-center p-4 rounded-lg bg-industrial-dark/50">
                <p className={`text-2xl font-bold text-${item.color}-400`}>{item.value}</p>
                <p className="text-xs text-gray-500 mt-1">{item.label}</p>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

export default OpenSearchView
