import React, { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Factory,
  Package,
  TrendingUp,
  TrendingDown,
  Target,
  Award,
  Clock,
  AlertTriangle,
  DollarSign,
  BarChart3,
  PieChart,
  Activity,
  ArrowLeft,
  ChevronRight,
  ChevronDown,
  Calendar,
  Filter,
  Download,
  RefreshCw,
  Eye,
  Gauge,
  Zap,
  CheckCircle,
  XCircle,
  AlertCircle,
  Users,
  Wrench,
  Percent,
  Timer,
  Box,
  Layers
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { SemiCircleGauge, RadialGauge, LinearGauge } from '../components/ui/Gauge'
import { TimeSeriesChart, DonutChart, AreaChartComponent } from '../components/ui/Charts'
import { StatusBadge, LoadingSpinner } from '../components/ui/Status'

// Generate mock time series data
const generateTimeSeriesData = (points = 24, baseValue = 50, variance = 20) => {
  return Array.from({ length: points }, (_, i) => ({
    time: `${String(i).padStart(2, '0')}:00`,
    value: Math.max(0, baseValue + (Math.random() - 0.5) * variance),
    target: baseValue * 1.1
  }))
}

// KPI Card with drill-down capability
function KPICard({ icon: Icon, title, value, unit, target, actual, trend, trendValue, color, status, onClick, children }) {
  const progressPercent = target ? Math.min((actual / target) * 100, 100) : 0

  return (
    <motion.div
      onClick={onClick}
      className={`p-6 rounded-2xl bg-industrial-card border border-industrial-border hover:border-${color}-500/50 transition-all cursor-pointer group`}
      whileHover={{ scale: 1.01, y: -2 }}
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 rounded-xl bg-${color}-500/10 flex items-center justify-center`}>
          <Icon className={`w-6 h-6 text-${color}-400`} />
        </div>
        {status && (
          <StatusBadge status={status} size="sm" />
        )}
      </div>

      <h3 className="text-sm font-medium text-gray-400 mb-2">{title}</h3>

      <div className="flex items-baseline gap-2 mb-3">
        <span className="text-3xl font-bold text-white">{value}</span>
        {unit && <span className="text-lg text-gray-500">{unit}</span>}
      </div>

      {target && (
        <div className="mb-3">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-500">Progress to target</span>
            <span className="text-white">{Math.round(progressPercent)}%</span>
          </div>
          <div className="h-2 rounded-full bg-gray-700 overflow-hidden">
            <motion.div
              className={`h-full rounded-full bg-${color}-500`}
              initial={{ width: 0 }}
              animate={{ width: `${progressPercent}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
          <div className="flex justify-between text-xs mt-1">
            <span className="text-gray-500">Target: {target}{unit}</span>
          </div>
        </div>
      )}

      {trend && (
        <div className={`flex items-center gap-1 text-sm ${trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400' : 'text-gray-400'}`}>
          {trend === 'up' ? <TrendingUp className="w-4 h-4" /> : trend === 'down' ? <TrendingDown className="w-4 h-4" /> : null}
          <span>{trendValue}</span>
          <span className="text-gray-500 ml-1">vs. last period</span>
        </div>
      )}

      {children}

      <div className="flex items-center gap-1 mt-3 text-xs text-gray-500 group-hover:text-industrial-accent transition-colors">
        <span>View details</span>
        <ChevronRight className="w-3 h-3" />
      </div>
    </motion.div>
  )
}

// Equipment Status Grid
function EquipmentGrid({ equipment }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {equipment.map((eq) => (
        <motion.div
          key={eq.name}
          className={`p-4 rounded-xl border transition-all cursor-pointer
            ${eq.status === 'running' ? 'bg-green-500/10 border-green-500/30 hover:border-green-500/50' :
              eq.status === 'warning' ? 'bg-yellow-500/10 border-yellow-500/30 hover:border-yellow-500/50' :
              eq.status === 'idle' ? 'bg-gray-500/10 border-gray-500/30 hover:border-gray-500/50' :
              'bg-red-500/10 border-red-500/30 hover:border-red-500/50'
            }`}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex items-center justify-between mb-2">
            <Factory className="w-5 h-5 text-gray-400" />
            <span className={`text-xs font-medium px-2 py-0.5 rounded
              ${eq.status === 'running' ? 'bg-green-500/20 text-green-400' :
                eq.status === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                eq.status === 'idle' ? 'bg-gray-500/20 text-gray-400' :
                'bg-red-500/20 text-red-400'
              }`}
            >
              {eq.status}
            </span>
          </div>
          <h4 className="font-medium text-white text-sm mb-1">{eq.name}</h4>
          {eq.efficiency > 0 && (
            <div className="mt-2">
              <LinearGauge value={eq.efficiency} color="auto" height="h-1" showValue={false} />
              <div className="flex justify-between mt-1">
                <span className="text-xs text-gray-500">Efficiency</span>
                <span className="text-xs text-white">{eq.efficiency}%</span>
              </div>
            </div>
          )}
        </motion.div>
      ))}
    </div>
  )
}

// Financial Impact Card
function FinancialImpactCard({ savings, costs, efficiency }) {
  return (
    <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/5 border-green-500/30">
      <CardBody>
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center">
            <DollarSign className="w-6 h-6 text-green-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Financial Impact</h3>
            <p className="text-sm text-gray-400">This month</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 rounded-lg bg-black/20">
            <p className="text-2xl font-bold text-green-400">+${savings}K</p>
            <p className="text-xs text-gray-400 mt-1">Cost Savings</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-black/20">
            <p className="text-2xl font-bold text-yellow-400">${costs}K</p>
            <p className="text-xs text-gray-400 mt-1">Downtime Cost</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-black/20">
            <p className="text-2xl font-bold text-cyan-400">{efficiency}%</p>
            <p className="text-xs text-gray-400 mt-1">ROI</p>
          </div>
        </div>
      </CardBody>
    </Card>
  )
}

// Time Range Selector
function TimeRangeSelector({ value, onChange }) {
  const options = [
    { label: 'Today', value: '1d' },
    { label: '7 Days', value: '7d' },
    { label: '30 Days', value: '30d' },
    { label: 'Quarter', value: '90d' },
    { label: 'Year', value: '365d' }
  ]

  return (
    <div className="flex items-center gap-1 p-1 rounded-lg bg-industrial-card border border-industrial-border">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors
            ${value === option.value
              ? 'bg-industrial-accent text-white'
              : 'text-gray-400 hover:text-white'
            }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}

function BusinessKPIView() {
  const navigate = useNavigate()
  const { metrics, isLoading } = useDashboard()
  const { t } = useI18n()

  const [timeRange, setTimeRange] = useState('7d')
  const [expandedSection, setExpandedSection] = useState(null)

  const equipmentData = useMemo(() => [
    { name: 'Robot-01', status: 'running', efficiency: 94 },
    { name: 'CNC-02', status: 'running', efficiency: 87 },
    { name: 'Conveyor-03', status: 'warning', efficiency: 72 },
    { name: 'Press-04', status: 'running', efficiency: 91 },
    { name: 'Welder-05', status: 'idle', efficiency: 0 },
    { name: 'Assembly-06', status: 'running', efficiency: 88 }
  ], [])

  const productionData = useMemo(() => [
    { name: 'Product A', value: 1250, color: '#06b6d4' },
    { name: 'Product B', value: 890, color: '#a855f7' },
    { name: 'Product C', value: 650, color: '#22c55e' },
    { name: 'Product D', value: 420, color: '#f59e0b' }
  ], [])

  const oeeHistory = useMemo(() => generateTimeSeriesData(24, 85, 10), [])
  const productionHistory = useMemo(() => generateTimeSeriesData(24, 3000, 500), [])

  const qualityMetrics = useMemo(() => [
    { label: 'First Pass Yield', value: 98.5, target: 99, unit: '%', status: 'warning' },
    { label: 'Defect Rate', value: 0.8, target: 0.5, unit: '%', status: 'warning' },
    { label: 'Rework Rate', value: 1.2, target: 1.0, unit: '%', status: 'warning' },
    { label: 'Scrap Rate', value: 0.5, target: 0.5, unit: '%', status: 'healthy' }
  ], [])

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
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/command-center')}
            className="p-2 rounded-lg hover:bg-white/5 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-400" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white">{t('businessKPI.title')}</h1>
            <p className="text-gray-400">{t('businessKPI.subtitle')}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <TimeRangeSelector value={timeRange} onChange={setTimeRange} />

          <button className="p-2 rounded-lg bg-industrial-card border border-industrial-border hover:border-gray-600 transition-colors">
            <Filter className="w-5 h-5 text-gray-400" />
          </button>

          <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-industrial-card border border-industrial-border hover:border-gray-600 transition-colors text-sm text-gray-300">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      {/* OEE Hero Section */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
        {/* OEE Gauge */}
        <Card className="lg:col-span-1 p-6">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-white mb-4">{t('metrics.business.oee')}</h3>
            <SemiCircleGauge
              value={metrics.business?.oee || 87.5}
              label={t('metrics.business.oeeDescription')}
              size={200}
            />
            <div className="grid grid-cols-3 gap-3 mt-6">
              <div className="text-center">
                <RadialGauge value={metrics.business?.availability || 92} size={70} color="green" />
                <p className="text-xs text-gray-400 mt-2">{t('metrics.business.availability')}</p>
              </div>
              <div className="text-center">
                <RadialGauge value={metrics.business?.performance || 95} size={70} color="cyan" />
                <p className="text-xs text-gray-400 mt-2">{t('metrics.business.performance')}</p>
              </div>
              <div className="text-center">
                <RadialGauge value={metrics.business?.quality || 99} size={70} color="purple" />
                <p className="text-xs text-gray-400 mt-2">{t('metrics.business.quality')}</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Key KPIs */}
        <div className="lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-4">
          <KPICard
            icon={Package}
            title={t('metrics.business.productionToday')}
            value={(metrics.business?.productionToday || 3247).toLocaleString()}
            unit="units"
            target={3500}
            actual={metrics.business?.productionToday || 3247}
            trend="up"
            trendValue="+12%"
            color="cyan"
          />
          <KPICard
            icon={Award}
            title={t('metrics.business.qualityRate')}
            value={metrics.business?.quality || 99.2}
            unit="%"
            target={99.5}
            actual={metrics.business?.quality || 99.2}
            trend="up"
            trendValue="+0.3%"
            color="green"
          />
          <KPICard
            icon={Clock}
            title={t('metrics.business.cycleTime')}
            value={metrics.business?.cycleTime || 45}
            unit="sec"
            target={42}
            actual={metrics.business?.cycleTime || 45}
            trend="down"
            trendValue="-2.1 sec"
            color="purple"
          />
          <KPICard
            icon={Gauge}
            title="Machine Utilization"
            value="78"
            unit="%"
            target={85}
            actual={78}
            trend="up"
            trendValue="+5%"
            color="yellow"
          />
        </div>
      </div>

      {/* Financial Impact & Production */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <FinancialImpactCard savings={125} costs={23} efficiency={18} />

        <Card className="lg:col-span-2">
          <CardHeader title={t('metrics.business.oeeTrend')} icon={TrendingUp} />
          <CardBody>
            <TimeSeriesChart
              data={oeeHistory}
              lines={[
                { dataKey: 'value', color: 'cyan', name: 'OEE' },
                { dataKey: 'target', color: 'green', name: 'Target', dashed: true }
              ]}
              height={220}
              yAxisLabel="OEE"
              yAxisUnit="%"
              yMin={60}
              yMax={100}
              warningThreshold={75}
              criticalThreshold={65}
              showThresholdZones
              tooltipUnit="%"
            />
          </CardBody>
        </Card>
      </div>

      {/* Production & Quality */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Production by Product */}
        <Card>
          <CardHeader title={t('metrics.business.productionByProduct')} icon={BarChart3} />
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
                    <div className="text-right">
                      <span className="font-medium text-white">{item.value.toLocaleString()}</span>
                      <span className="text-xs text-gray-500 ml-2">units</span>
                    </div>
                  </div>
                ))}
                <div className="pt-3 border-t border-industrial-border">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-white">Total</span>
                    <span className="font-bold text-white">
                      {productionData.reduce((a, b) => a + b.value, 0).toLocaleString()} units
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Quality Metrics */}
        <Card>
          <CardHeader title="Quality Metrics" icon={Award} />
          <CardBody>
            <div className="space-y-4">
              {qualityMetrics.map((metric) => (
                <div key={metric.label} className="p-3 rounded-lg bg-industrial-darker">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">{metric.label}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold text-white">{metric.value}{metric.unit}</span>
                      <StatusBadge status={metric.status} size="sm" />
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 rounded-full bg-gray-700 overflow-hidden">
                      <div
                        className={`h-full rounded-full ${metric.status === 'healthy' ? 'bg-green-500' : 'bg-yellow-500'}`}
                        style={{ width: `${Math.min((metric.value / metric.target) * 100, 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500">Target: {metric.target}{metric.unit}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Equipment Status */}
      <Card className="mb-6">
        <CardHeader title={t('metrics.business.equipmentStatus')} icon={Factory} />
        <CardBody>
          <EquipmentGrid equipment={equipmentData} />
        </CardBody>
      </Card>

      {/* Alerts & Maintenance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Alerts */}
        <Card>
          <CardHeader
            title="Active Alerts"
            icon={AlertTriangle}
            action={
              <button className="text-sm text-industrial-accent hover:underline">View all</button>
            }
          />
          <CardBody>
            <div className="space-y-2">
              {[
                { severity: 'critical', message: 'Conveyor-03 efficiency below threshold', time: '5 min ago' },
                { severity: 'warning', message: 'CNC-02 temperature rising', time: '12 min ago' },
                { severity: 'warning', message: 'Production target may not be met', time: '30 min ago' },
                { severity: 'info', message: 'Scheduled maintenance in 2 hours', time: '1 hour ago' }
              ].map((alert, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-lg flex items-start gap-3 cursor-pointer hover:bg-white/5 transition-colors
                    ${alert.severity === 'critical' ? 'bg-red-500/10 border border-red-500/30' :
                      alert.severity === 'warning' ? 'bg-yellow-500/10 border border-yellow-500/30' :
                      'bg-blue-500/10 border border-blue-500/30'
                    }`}
                >
                  {alert.severity === 'critical' ? <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" /> :
                   alert.severity === 'warning' ? <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0" /> :
                   <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0" />}
                  <div className="flex-1">
                    <p className="text-sm text-white">{alert.message}</p>
                    <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-500" />
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Upcoming Maintenance */}
        <Card>
          <CardHeader title="Upcoming Maintenance" icon={Wrench} />
          <CardBody>
            <div className="space-y-3">
              {[
                { equipment: 'CNC-02', type: 'Preventive', date: 'Today, 14:00', duration: '2h' },
                { equipment: 'Robot-01', type: 'Calibration', date: 'Tomorrow, 08:00', duration: '1h' },
                { equipment: 'Welder-05', type: 'Repair', date: 'Dec 20, 09:00', duration: '4h' },
                { equipment: 'All Systems', type: 'Inspection', date: 'Dec 22, 06:00', duration: '3h' }
              ].map((item, i) => (
                <div key={i} className="p-3 rounded-lg bg-industrial-darker flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                      <Wrench className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{item.equipment}</p>
                      <p className="text-xs text-gray-500">{item.type}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-white">{item.date}</p>
                    <p className="text-xs text-gray-500">{item.duration}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default BusinessKPIView
