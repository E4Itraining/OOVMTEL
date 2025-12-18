import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Activity,
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  BarChart3,
  Calendar,
  CheckCircle2,
  Clock,
  DollarSign,
  Factory,
  Gauge,
  Layers,
  Package,
  PieChart,
  Settings,
  Target,
  TrendingDown,
  TrendingUp,
  Wrench,
  XCircle
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { SemiCircleGauge, RadialGauge } from '../components/ui/Gauge'
import { TimeSeriesChart, DonutChart } from '../components/ui/Charts'

// OEE Components breakdown
const OEE_COMPONENTS = [
  { id: 'availability', label: 'Availability', value: 95.2, target: 95, color: 'green', icon: Clock },
  { id: 'performance', label: 'Performance', value: 88.5, target: 90, color: 'yellow', icon: Gauge },
  { id: 'quality', label: 'Quality', value: 99.1, target: 98, color: 'green', icon: CheckCircle2 }
]

// Production by product mock data
const PRODUCTION_BY_PRODUCT = [
  { name: 'Product A', value: 4500, color: '#06b6d4' },
  { name: 'Product B', value: 3200, color: '#8b5cf6' },
  { name: 'Product C', value: 2800, color: '#10b981' },
  { name: 'Product D', value: 1500, color: '#f59e0b' }
]

// Equipment status
const EQUIPMENT_STATUS = [
  { id: 'line-1', name: 'Production Line 1', status: 'running', oee: 92.3, uptime: '23h 45m' },
  { id: 'line-2', name: 'Production Line 2', status: 'running', oee: 88.1, uptime: '18h 30m' },
  { id: 'line-3', name: 'Production Line 3', status: 'maintenance', oee: 0, uptime: '-' },
  { id: 'line-4', name: 'Production Line 4', status: 'stopped', oee: 0, uptime: '-' },
  { id: 'line-5', name: 'Production Line 5', status: 'running', oee: 94.7, uptime: '47h 12m' }
]

// Financial impact mock data
const FINANCIAL_METRICS = [
  { id: 'revenue', label: 'Daily Revenue', value: 125000, unit: '$', trend: 'up', trendValue: '+5.2%' },
  { id: 'cost', label: 'Production Cost', value: 78500, unit: '$', trend: 'down', trendValue: '-2.1%' },
  { id: 'margin', label: 'Gross Margin', value: 37.2, unit: '%', trend: 'up', trendValue: '+1.8%' },
  { id: 'waste', label: 'Waste Cost', value: 3200, unit: '$', trend: 'down', trendValue: '-8.5%' }
]

function OEEGaugeCard({ component }) {
  const Icon = component.icon
  const isOnTarget = component.value >= component.target

  return (
    <div className="p-4 rounded-xl bg-industrial-card/50 border border-industrial-border">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Icon className="w-5 h-5 text-gray-400" />
          <span className="text-sm font-medium text-gray-300">{component.label}</span>
        </div>
        {isOnTarget ? (
          <CheckCircle2 className="w-5 h-5 text-green-400" />
        ) : (
          <AlertTriangle className="w-5 h-5 text-yellow-400" />
        )}
      </div>
      <div className="flex items-end justify-between">
        <div>
          <p className="text-3xl font-bold text-white">{component.value}%</p>
          <p className="text-xs text-gray-500">Target: {component.target}%</p>
        </div>
        <div className={`px-2 py-1 rounded text-xs font-medium ${
          isOnTarget ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
        }`}>
          {isOnTarget ? 'On Target' : 'Below Target'}
        </div>
      </div>
    </div>
  )
}

function EquipmentRow({ equipment }) {
  const statusConfig = {
    running: { icon: CheckCircle2, color: 'text-green-400', bg: 'bg-green-500/10', label: 'Running' },
    maintenance: { icon: Wrench, color: 'text-yellow-400', bg: 'bg-yellow-500/10', label: 'Maintenance' },
    stopped: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10', label: 'Stopped' },
    error: { icon: AlertTriangle, color: 'text-red-400', bg: 'bg-red-500/10', label: 'Error' }
  }

  const status = statusConfig[equipment.status] || statusConfig.stopped
  const Icon = status.icon

  return (
    <div className="flex items-center justify-between py-3 border-b border-industrial-border/50 last:border-0">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg ${status.bg} flex items-center justify-center`}>
          <Icon className={`w-5 h-5 ${status.color}`} />
        </div>
        <div>
          <p className="text-sm font-medium text-white">{equipment.name}</p>
          <p className={`text-xs ${status.color}`}>{status.label}</p>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="text-right">
          <p className="text-sm font-semibold text-white">
            {equipment.status === 'running' ? `${equipment.oee}%` : '-'}
          </p>
          <p className="text-xs text-gray-500">OEE</p>
        </div>
        <div className="text-right">
          <p className="text-sm font-mono text-gray-300">{equipment.uptime}</p>
          <p className="text-xs text-gray-500">Uptime</p>
        </div>
      </div>
    </div>
  )
}

function FinancialMetricCard({ metric }) {
  const TrendIcon = metric.trend === 'up' ? TrendingUp : TrendingDown
  const isPositive = (metric.id === 'revenue' || metric.id === 'margin')
    ? metric.trend === 'up'
    : metric.trend === 'down'

  return (
    <div className="p-4 rounded-xl bg-industrial-card/50 border border-industrial-border">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">{metric.label}</span>
        <div className={`flex items-center gap-1 text-xs ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
          <TrendIcon className="w-3 h-3" />
          <span>{metric.trendValue}</span>
        </div>
      </div>
      <p className="text-2xl font-bold text-white">
        {metric.unit === '$' ? '$' : ''}{metric.value.toLocaleString()}{metric.unit === '%' ? '%' : ''}
      </p>
    </div>
  )
}

function BusinessKPIView() {
  const { t } = useI18n()
  const { metrics } = useDashboard()
  const [selectedPeriod, setSelectedPeriod] = useState('today')

  // Calculate overall OEE
  const overallOEE = (OEE_COMPONENTS.reduce((acc, c) => acc * c.value, 1) / 1000000).toFixed(1)

  // Mock OEE trend data
  const oeeTrendData = Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    oee: 80 + Math.random() * 15,
    target: 85
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">
            {t('businessKPI.title')}
          </h1>
          <p className="text-gray-400 mt-1">
            {t('businessKPI.subtitle')}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center rounded-lg bg-industrial-card border border-industrial-border p-1">
            {['today', 'week', 'month'].map((period) => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  selectedPeriod === period
                    ? 'bg-industrial-accent/20 text-cyan-400'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {t(`businessKPI.period.${period}`)}
              </button>
            ))}
          </div>
          <button className="btn btn-ghost flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            {t('time.custom')}
          </button>
        </div>
      </div>

      {/* Main OEE Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Overall OEE Gauge */}
        <Card className="lg:col-span-1">
          <CardHeader
            title={t('businessKPI.oee.title')}
            subtitle={t('businessKPI.oee.subtitle')}
            icon={Target}
          />
          <CardBody className="flex flex-col items-center justify-center py-6">
            <SemiCircleGauge
              value={parseFloat(overallOEE)}
              max={100}
              label={t('metrics.business.oee')}
              unit="%"
              size={200}
              color={parseFloat(overallOEE) >= 85 ? 'green' : parseFloat(overallOEE) >= 70 ? 'yellow' : 'red'}
            />
            <div className="mt-4 flex items-center gap-2">
              <Target className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-400">Target: 85%</span>
            </div>
          </CardBody>
        </Card>

        {/* OEE Components */}
        <Card className="lg:col-span-2">
          <CardHeader
            title={t('businessKPI.oee.components')}
            subtitle={t('businessKPI.oee.componentsSubtitle')}
            icon={PieChart}
          />
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {OEE_COMPONENTS.map((component) => (
                <OEEGaugeCard key={component.id} component={component} />
              ))}
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Production & Quality Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <MetricCard
          label={t('metrics.business.productionToday')}
          value={metrics.business?.productionToday?.toLocaleString() || '12,000'}
          unit="units"
          icon={Package}
          color="cyan"
          trend="up"
          trendValue="+8.2%"
        />
        <MetricCard
          label={t('metrics.business.cycleTime')}
          value={metrics.business?.cycleTime?.toFixed(1) || '45.2'}
          unit="s"
          icon={Clock}
          color="purple"
        />
        <MetricCard
          label={t('metrics.business.qualityRate')}
          value="99.1"
          unit="%"
          icon={CheckCircle2}
          color="green"
        />
        <MetricCard
          label={t('metrics.business.defectsToday')}
          value={metrics.business?.defectsToday || '23'}
          icon={AlertTriangle}
          color={metrics.business?.defectsToday > 50 ? 'red' : 'yellow'}
        />
        <MetricCard
          label="Scrap Rate"
          value="0.8"
          unit="%"
          icon={XCircle}
          color="green"
        />
        <MetricCard
          label={t('metrics.business.criticalAlarms')}
          value={metrics.business?.criticalAlarms || '2'}
          icon={AlertTriangle}
          color={metrics.business?.criticalAlarms > 5 ? 'red' : 'yellow'}
        />
      </div>

      {/* Financial Impact & Production by Product */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Financial Impact */}
        <Card>
          <CardHeader
            title={t('businessKPI.financial.title')}
            subtitle={t('businessKPI.financial.subtitle')}
            icon={DollarSign}
          />
          <CardBody>
            <div className="grid grid-cols-2 gap-4">
              {FINANCIAL_METRICS.map((metric) => (
                <FinancialMetricCard key={metric.id} metric={metric} />
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Production by Product */}
        <Card>
          <CardHeader
            title={t('businessKPI.production.byProduct')}
            subtitle={t('businessKPI.production.distribution')}
            icon={Layers}
          />
          <CardBody>
            <div className="flex items-center gap-6">
              <div className="w-40 h-40">
                <DonutChart data={PRODUCTION_BY_PRODUCT} />
              </div>
              <div className="flex-1 space-y-3">
                {PRODUCTION_BY_PRODUCT.map((product) => (
                  <div key={product.name} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: product.color }} />
                      <span className="text-sm text-gray-300">{product.name}</span>
                    </div>
                    <span className="text-sm font-medium text-white">{product.value.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* OEE Trend Chart */}
      <Card>
        <CardHeader
          title={t('businessKPI.oee.trend')}
          subtitle={t('businessKPI.oee.trendSubtitle')}
          icon={TrendingUp}
        />
        <CardBody>
          <div className="h-64">
            <TimeSeriesChart
              data={oeeTrendData}
              lines={[
                { key: 'oee', color: '#06b6d4', name: 'OEE' },
                { key: 'target', color: '#6b7280', name: 'Target', dashed: true }
              ]}
            />
          </div>
        </CardBody>
      </Card>

      {/* Equipment Status & Maintenance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Equipment Status */}
        <Card>
          <CardHeader
            title={t('businessKPI.equipment.status')}
            subtitle={t('businessKPI.equipment.statusSubtitle')}
            icon={Factory}
          />
          <CardBody className="space-y-1">
            {EQUIPMENT_STATUS.map((equipment) => (
              <EquipmentRow key={equipment.id} equipment={equipment} />
            ))}
          </CardBody>
        </Card>

        {/* Maintenance Schedule */}
        <Card>
          <CardHeader
            title={t('businessKPI.maintenance.title')}
            subtitle={t('businessKPI.maintenance.subtitle')}
            icon={Wrench}
          />
          <CardBody>
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-yellow-400">Production Line 3</span>
                  <span className="text-xs text-yellow-400/70">In Progress</span>
                </div>
                <p className="text-xs text-gray-400">Preventive maintenance - Estimated completion: 2h</p>
              </div>

              <div className="p-4 rounded-lg bg-industrial-darker/50 border border-industrial-border">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-300">Production Line 1</span>
                  <span className="text-xs text-gray-500">Scheduled</span>
                </div>
                <p className="text-xs text-gray-400">Next maintenance: Tomorrow at 06:00</p>
              </div>

              <div className="p-4 rounded-lg bg-industrial-darker/50 border border-industrial-border">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-300">Production Line 5</span>
                  <span className="text-xs text-gray-500">Scheduled</span>
                </div>
                <p className="text-xs text-gray-400">Next maintenance: In 3 days</p>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default BusinessKPIView
