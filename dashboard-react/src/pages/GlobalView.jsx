import React, { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Activity,
  BarChart3,
  Database,
  Server,
  Cpu,
  HardDrive,
  MessageSquare,
  Search,
  Gauge,
  Factory,
  Package,
  AlertTriangle,
  TrendingUp,
  Clock,
  Zap,
  Target,
  Award
} from 'lucide-react'
import { useDashboard, USER_MODES } from '../context/DashboardContext'
import { Card, CardHeader, CardBody, MetricCard, ServiceCard, LinkCard } from '../components/ui/Card'
import { RadialGauge, SemiCircleGauge, LinearGauge } from '../components/ui/Gauge'
import { TimeSeriesChart, BarChartComponent, DonutChart, SparklineChart } from '../components/ui/Charts'
import { StatusBadge, HealthIndicator, LoadingSpinner } from '../components/ui/Status'

// Generate mock time series data
const generateTimeSeriesData = (points = 20, baseValue = 50, variance = 20) => {
  return Array.from({ length: points }, (_, i) => ({
    time: `${String(i).padStart(2, '0')}:00`,
    value: Math.max(0, baseValue + (Math.random() - 0.5) * variance)
  }))
}

function BusinessView({ metrics, navigate }) {
  const equipmentData = useMemo(() => [
    { name: 'Robot-01', status: 'running', efficiency: 94 },
    { name: 'CNC-02', status: 'running', efficiency: 87 },
    { name: 'Conveyor-03', status: 'warning', efficiency: 72 },
    { name: 'Press-04', status: 'running', efficiency: 91 },
    { name: 'Welder-05', status: 'idle', efficiency: 0 },
    { name: 'Assembly-06', status: 'running', efficiency: 88 },
  ], [])

  const productionData = useMemo(() => [
    { name: 'Prod A', value: 1250, color: '#06b6d4' },
    { name: 'Prod B', value: 890, color: '#a855f7' },
    { name: 'Prod C', value: 650, color: '#22c55e' },
    { name: 'Prod D', value: 420, color: '#f59e0b' },
  ], [])

  const oeeHistory = useMemo(() => generateTimeSeriesData(24, 85, 10), [])

  return (
    <div className="space-y-6">
      {/* Hero KPI Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* OEE Gauge */}
        <Card className="lg:col-span-1 p-6">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-white mb-4">OEE Global</h3>
            <SemiCircleGauge
              value={metrics.business?.oee || 87.5}
              label="Overall Equipment Effectiveness"
              size={220}
            />
            <div className="grid grid-cols-3 gap-4 mt-6">
              <div>
                <RadialGauge value={metrics.business?.availability || 92} size={80} color="green" />
                <p className="text-xs text-gray-400 mt-2">Disponibilité</p>
              </div>
              <div>
                <RadialGauge value={metrics.business?.performance || 95} size={80} color="cyan" />
                <p className="text-xs text-gray-400 mt-2">Performance</p>
              </div>
              <div>
                <RadialGauge value={metrics.business?.quality || 99} size={80} color="purple" />
                <p className="text-xs text-gray-400 mt-2">Qualité</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Key Metrics */}
        <div className="lg:col-span-2 grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            label="Production Jour"
            value={metrics.business?.productionToday?.toLocaleString() || "3,247"}
            unit="unités"
            icon={Package}
            color="cyan"
            trend="up"
            trendValue="+12% vs hier"
          />
          <MetricCard
            label="Taux Qualité"
            value={metrics.business?.quality || "99.2"}
            unit="%"
            icon={Award}
            color="green"
            trend="up"
            trendValue="+0.3%"
          />
          <MetricCard
            label="Temps Cycle"
            value={metrics.business?.cycleTime || "45"}
            unit="sec"
            icon={Clock}
            color="purple"
            trend="down"
            trendValue="-2.1 sec"
          />
          <MetricCard
            label="Alertes Critiques"
            value={metrics.business?.criticalAlarms || "2"}
            icon={AlertTriangle}
            color={metrics.business?.criticalAlarms > 0 ? "red" : "green"}
          />
        </div>
      </div>

      {/* Production & Equipment Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Production by Product */}
        <Card>
          <CardHeader title="Production par Produit" icon={BarChart3} />
          <CardBody>
            <div className="flex items-center gap-6">
              <div className="w-48 h-48">
                <DonutChart data={productionData} height={192} innerRadius={50} outerRadius={75} />
              </div>
              <div className="flex-1 space-y-3">
                {productionData.map((item) => (
                  <div key={item.name} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-sm text-gray-300">{item.name}</span>
                    </div>
                    <span className="font-medium text-white">{item.value.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardBody>
        </Card>

        {/* OEE Trend */}
        <Card>
          <CardHeader title="Tendance OEE (24h)" icon={TrendingUp} />
          <CardBody>
            <TimeSeriesChart
              data={oeeHistory}
              lines={[{ dataKey: 'value', color: 'cyan', name: 'OEE' }]}
              height={220}
            />
          </CardBody>
        </Card>
      </div>

      {/* Equipment Grid */}
      <Card>
        <CardHeader title="Statut Équipements" icon={Factory} />
        <CardBody>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {equipmentData.map((eq) => (
              <motion.div
                key={eq.name}
                className={`p-4 rounded-xl border transition-all cursor-pointer hover:scale-105
                  ${eq.status === 'running' ? 'bg-green-500/10 border-green-500/30' :
                    eq.status === 'warning' ? 'bg-yellow-500/10 border-yellow-500/30' :
                    eq.status === 'idle' ? 'bg-gray-500/10 border-gray-500/30' :
                    'bg-red-500/10 border-red-500/30'
                  }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <div className="flex items-center justify-between mb-2">
                  <Server className="w-5 h-5 text-gray-400" />
                  <StatusBadge status={eq.status} size="sm" />
                </div>
                <h4 className="font-medium text-white text-sm">{eq.name}</h4>
                {eq.efficiency > 0 && (
                  <div className="mt-2">
                    <LinearGauge value={eq.efficiency} color="auto" height="h-1" showValue={false} />
                    <span className="text-xs text-gray-400">{eq.efficiency}% eff.</span>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* Quick Access Links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <LinkCard
          title="Grafana"
          description="Tableaux de bord détaillés"
          href="http://localhost:3000"
          icon={Activity}
        />
        <LinkCard
          title="OpenSearch"
          description="Analyse des logs"
          href="http://localhost:5601"
          icon={Search}
        />
        <LinkCard
          title="Kafka UI"
          description="Flux de données temps réel"
          href="http://localhost:8090"
          icon={MessageSquare}
        />
      </div>
    </div>
  )
}

function TechView({ metrics, navigate }) {
  const services = useMemo(() => [
    { name: 'VictoriaMetrics', status: 'healthy', icon: Database, metrics: [
      { label: 'Series', value: metrics.tech?.vmActiveSeries?.toLocaleString() || '125K' },
      { label: 'Storage', value: metrics.tech?.vmStorage || '2.4GB' },
      { label: 'Latency', value: `${metrics.tech?.vmQueryLatency || 12}ms` }
    ]},
    { name: 'OpenSearch', status: 'healthy', icon: Search, metrics: [
      { label: 'Docs', value: metrics.tech?.osDocuments?.toLocaleString() || '1.2M' },
      { label: 'Health', value: metrics.tech?.osHealth || 'Green' },
      { label: 'Nodes', value: metrics.tech?.osNodes || '3' }
    ]},
    { name: 'Kafka', status: 'healthy', icon: MessageSquare, metrics: [
      { label: 'Topics', value: metrics.tech?.kafkaTopics || '12' },
      { label: 'Partitions', value: metrics.tech?.kafkaPartitions || '96' },
      { label: 'Lag', value: metrics.tech?.kafkaConsumerLag || '0' }
    ]},
    { name: 'OTEL Collector', status: 'healthy', icon: Zap, metrics: [
      { label: 'Recv/s', value: `${metrics.tech?.metricsRate || 1250}` },
      { label: 'Export/s', value: `${Math.round((metrics.tech?.metricsRate || 1250) * 0.98)}` },
      { label: 'Errors', value: '0' }
    ]},
    { name: 'Grafana', status: 'healthy', icon: Activity, metrics: [
      { label: 'Dashboards', value: '6' },
      { label: 'Alerts', value: '12' },
      { label: 'Users', value: '3' }
    ]},
    { name: 'OpenObserve', status: 'healthy', icon: Target, metrics: [
      { label: 'Logs/s', value: `${metrics.tech?.logsRate || 520}` },
      { label: 'Traces/s', value: `${metrics.tech?.tracesRate || 180}` },
      { label: 'Retention', value: '7d' }
    ]},
  ], [metrics.tech])

  const pipelineData = useMemo(() => generateTimeSeriesData(30, 1000, 300), [])
  const resourceData = useMemo(() => [
    { name: 'CPU', value: metrics.tech?.cpu || 45 },
    { name: 'Memory', value: metrics.tech?.memory || 62 },
    { name: 'Disk', value: metrics.tech?.disk || 38 },
    { name: 'Network', value: 28 },
  ], [metrics.tech])

  return (
    <div className="space-y-6">
      {/* Pipeline Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Metrics Rate"
          value={metrics.tech?.metricsRate?.toLocaleString() || "1,250"}
          unit="pts/s"
          icon={Gauge}
          color="cyan"
          trend="up"
          trendValue="+5%"
        />
        <MetricCard
          label="Logs Rate"
          value={metrics.tech?.logsRate?.toLocaleString() || "520"}
          unit="rec/s"
          icon={Database}
          color="purple"
        />
        <MetricCard
          label="Latency P95"
          value={metrics.tech?.latencyP95 || "23"}
          unit="ms"
          icon={Zap}
          color="green"
          trend="down"
          trendValue="-3ms"
        />
        <MetricCard
          label="Error Rate"
          value={metrics.tech?.errorRate || "0.02"}
          unit="%"
          icon={AlertTriangle}
          color={metrics.tech?.errorRate > 1 ? "red" : "green"}
        />
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {services.map((service) => (
          <ServiceCard
            key={service.name}
            name={service.name}
            status={service.status}
            icon={service.icon}
            metrics={service.metrics}
            onClick={() => navigate(`/details/${service.name.toLowerCase().replace(' ', '-')}`)}
          />
        ))}
      </div>

      {/* Pipeline & Resources */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Data Pipeline */}
        <Card>
          <CardHeader title="Data Pipeline Throughput" icon={Activity} />
          <CardBody>
            <TimeSeriesChart
              data={pipelineData}
              lines={[
                { dataKey: 'value', color: 'cyan', name: 'Throughput' }
              ]}
              height={220}
            />
          </CardBody>
        </Card>

        {/* Resource Usage */}
        <Card>
          <CardHeader title="Resource Utilization" icon={Cpu} />
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
      </div>

      {/* System Health Overview */}
      <Card>
        <CardHeader title="System Health Overview" icon={Server} />
        <CardBody>
          <HealthIndicator services={services} />
        </CardBody>
      </Card>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <LinkCard
          title="Grafana Dashboards"
          description="Visualisations avancées"
          href="http://localhost:3000"
          icon={Activity}
        />
        <LinkCard
          title="OpenSearch Dashboards"
          description="Log analytics & search"
          href="http://localhost:5601"
          icon={Search}
        />
        <LinkCard
          title="Kafka UI"
          description="Topic management & monitoring"
          href="http://localhost:8090"
          icon={MessageSquare}
        />
      </div>
    </div>
  )
}

function GlobalView() {
  const navigate = useNavigate()
  const { userMode, metrics, isLoading } = useDashboard()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <LoadingSpinner size="lg" label="Chargement des données..." />
      </div>
    )
  }

  return (
    <div>
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">
          {userMode === USER_MODES.TECH ? 'Vue Technique' : 'Vue Business'}
        </h1>
        <p className="text-gray-400 mt-1">
          {userMode === USER_MODES.TECH
            ? 'Infrastructure & Pipeline de données'
            : 'KPIs Production & Performance Industrielle'
          }
        </p>
      </div>

      {/* Content based on user mode */}
      {userMode === USER_MODES.TECH ? (
        <TechView metrics={metrics} navigate={navigate} />
      ) : (
        <BusinessView metrics={metrics} navigate={navigate} />
      )}
    </div>
  )
}

export default GlobalView
