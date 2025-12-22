import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Leaf,
  Zap,
  Server,
  Cpu,
  HardDrive,
  Thermometer,
  Cloud,
  Monitor,
  Smartphone,
  Database,
  Network,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Target,
  RefreshCw,
  Download,
  Eye,
  Clock,
  Calendar,
  ChevronRight,
  ChevronDown,
  AlertTriangle,
  CheckCircle2,
  Info,
  Activity,
  Gauge,
  Factory,
  Recycle,
  Laptop,
  Trash2,
  Battery,
  Sun,
  Wind
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { TimeSeriesChart, DonutChart, BarChartComponent, AreaChartComponent } from '../components/ui/Charts'
import { StatusBadge, HealthIndicator } from '../components/ui/Status'
import { RadialGauge, LinearGauge, SemiCircleGauge } from '../components/ui/Gauge'

// PUE (Power Usage Effectiveness) Data
const pueData = {
  current: 1.45,
  target: 1.3,
  average: 1.52,
  best: 1.38,
  trend: -3.2 // % improvement
}

// Data center energy metrics
const datacenterMetrics = {
  totalPower: 2450, // kW
  itLoad: 1690, // kW
  cooling: 520, // kW
  lighting: 45, // kW
  other: 195, // kW
  renewableShare: 42, // %
  carbonIntensity: 285, // gCO2/kWh
  monthlyConsumption: 1764000 // kWh
}

// Server efficiency metrics
const serverEfficiency = [
  {
    id: 'cluster-prod',
    name: 'Cluster Production',
    servers: 24,
    cpuUtilization: 68,
    memoryUtilization: 72,
    powerDraw: 580,
    carbonFootprint: 165,
    status: 'optimal'
  },
  {
    id: 'cluster-data',
    name: 'Cluster Data/Analytics',
    servers: 16,
    cpuUtilization: 45,
    memoryUtilization: 78,
    powerDraw: 420,
    carbonFootprint: 120,
    status: 'underutilized'
  },
  {
    id: 'cluster-dev',
    name: 'Cluster Dev/Test',
    servers: 12,
    cpuUtilization: 32,
    memoryUtilization: 45,
    powerDraw: 280,
    carbonFootprint: 80,
    status: 'underutilized'
  },
  {
    id: 'cluster-backup',
    name: 'Cluster Backup/DR',
    servers: 8,
    cpuUtilization: 15,
    memoryUtilization: 35,
    powerDraw: 180,
    carbonFootprint: 51,
    status: 'idle'
  }
]

// Cloud carbon footprint
const cloudCarbon = {
  providers: [
    { name: 'AWS', region: 'eu-west-1', carbon: 145, compute: 65, storage: 45, network: 35 },
    { name: 'Azure', region: 'West Europe', carbon: 120, compute: 55, storage: 40, network: 25 },
    { name: 'GCP', region: 'europe-west1', carbon: 85, compute: 40, storage: 30, network: 15 }
  ],
  totalMonthly: 350, // tCO2e
  trend: -8.5
}

// E-waste and equipment lifecycle
const equipmentLifecycle = {
  totalDevices: 1250,
  categories: [
    { name: 'Serveurs', count: 60, avgAge: 4.2, targetAge: 5, status: 'good' },
    { name: 'Postes de travail', count: 450, avgAge: 3.8, targetAge: 4, status: 'warning' },
    { name: 'Laptops', count: 320, avgAge: 2.9, targetAge: 4, status: 'good' },
    { name: 'Écrans', count: 380, avgAge: 4.5, targetAge: 6, status: 'good' },
    { name: 'Équipements réseau', count: 40, avgAge: 5.1, targetAge: 7, status: 'good' }
  ],
  recycledLastYear: 85,
  refurbishedLastYear: 42,
  ewasteRate: 92 // % properly disposed
}

// Optimization recommendations
const optimizationRecommendations = [
  {
    id: 'opt-001',
    title: 'Consolidation serveurs Dev/Test',
    category: 'Infrastructure',
    impact: 'Réduction 25% consommation cluster',
    savings: '45 tCO2e/an',
    costSaving: '18k€/an',
    effort: 'medium',
    status: 'proposed'
  },
  {
    id: 'opt-002',
    title: 'Migration workloads vers région verte',
    category: 'Cloud',
    impact: 'Réduction 15% empreinte cloud',
    savings: '52 tCO2e/an',
    costSaving: '8k€/an',
    effort: 'high',
    status: 'in_progress'
  },
  {
    id: 'opt-003',
    title: 'Optimisation refroidissement datacenter',
    category: 'Datacenter',
    impact: 'PUE de 1.45 à 1.35',
    savings: '120 tCO2e/an',
    costSaving: '35k€/an',
    effort: 'high',
    status: 'planned'
  },
  {
    id: 'opt-004',
    title: 'Virtualisation postes de travail',
    category: 'Endpoints',
    impact: 'Réduction 40% conso endpoints',
    savings: '28 tCO2e/an',
    costSaving: '12k€/an',
    effort: 'medium',
    status: 'proposed'
  }
]

// Generate PUE trend data
const generatePUETrend = () => {
  const data = []
  for (let i = 23; i >= 0; i--) {
    data.push({
      time: `${23 - i}:00`,
      pue: 1.4 + Math.random() * 0.15,
      itLoad: 1600 + Math.random() * 200,
      cooling: 480 + Math.random() * 80
    })
  }
  return data
}

// Generate energy consumption trend
const generateEnergyTrend = () => {
  const data = []
  for (let i = 29; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    data.push({
      time: date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }),
      consumption: 55000 + Math.random() * 10000,
      renewable: 22000 + Math.random() * 5000
    })
  }
  return data
}

// Power distribution data
const powerDistribution = [
  { name: 'IT Load', value: datacenterMetrics.itLoad, color: '#3b82f6' },
  { name: 'Refroidissement', value: datacenterMetrics.cooling, color: '#06b6d4' },
  { name: 'Éclairage', value: datacenterMetrics.lighting, color: '#eab308' },
  { name: 'Autres', value: datacenterMetrics.other, color: '#6b7280' }
]

// Server Cluster Card
function ServerClusterCard({ cluster, isExpanded, onToggle }) {
  const statusColors = {
    optimal: 'border-green-500/30 hover:border-green-500/50',
    underutilized: 'border-yellow-500/30 hover:border-yellow-500/50',
    overloaded: 'border-red-500/30 hover:border-red-500/50',
    idle: 'border-gray-500/30 hover:border-gray-500/50'
  }

  const statusLabels = {
    optimal: 'Optimal',
    underutilized: 'Sous-utilisé',
    overloaded: 'Surchargé',
    idle: 'Inactif'
  }

  return (
    <motion.div
      className={`rounded-xl border bg-industrial-card/50 ${statusColors[cluster.status]} transition-all duration-300`}
      layout
    >
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-4">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
            cluster.status === 'optimal' ? 'bg-green-500/20' :
            cluster.status === 'underutilized' ? 'bg-yellow-500/20' :
            cluster.status === 'idle' ? 'bg-gray-500/20' : 'bg-red-500/20'
          }`}>
            <Server className={`w-5 h-5 ${
              cluster.status === 'optimal' ? 'text-green-400' :
              cluster.status === 'underutilized' ? 'text-yellow-400' :
              cluster.status === 'idle' ? 'text-gray-400' : 'text-red-400'
            }`} />
          </div>
          <div>
            <h3 className="font-semibold text-white">{cluster.name}</h3>
            <p className="text-sm text-gray-400">{cluster.servers} serveurs</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-6">
            <div className="text-right">
              <p className="text-lg font-semibold text-white">{cluster.cpuUtilization}%</p>
              <p className="text-xs text-gray-500">CPU</p>
            </div>
            <div className="text-right">
              <p className="text-lg font-semibold text-white">{cluster.powerDraw} kW</p>
              <p className="text-xs text-gray-500">Consommation</p>
            </div>
          </div>
          <span className={`px-2 py-1 rounded text-xs ${
            cluster.status === 'optimal' ? 'bg-green-500/20 text-green-400' :
            cluster.status === 'underutilized' ? 'bg-yellow-500/20 text-yellow-400' :
            cluster.status === 'idle' ? 'bg-gray-500/20 text-gray-400' :
            'bg-red-500/20 text-red-400'
          }`}>
            {statusLabels[cluster.status]}
          </span>
          <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
        </div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 pt-2 border-t border-industrial-border/50">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-3 rounded-lg bg-industrial-darker/50">
                  <p className="text-xs text-gray-500">Utilisation CPU</p>
                  <p className="text-lg font-semibold text-white">{cluster.cpuUtilization}%</p>
                  <div className="h-1 mt-1 bg-industrial-darker rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        cluster.cpuUtilization >= 70 ? 'bg-green-500' :
                        cluster.cpuUtilization >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${cluster.cpuUtilization}%` }}
                    />
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-industrial-darker/50">
                  <p className="text-xs text-gray-500">Utilisation Mémoire</p>
                  <p className="text-lg font-semibold text-white">{cluster.memoryUtilization}%</p>
                  <div className="h-1 mt-1 bg-industrial-darker rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        cluster.memoryUtilization >= 70 ? 'bg-green-500' :
                        cluster.memoryUtilization >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${cluster.memoryUtilization}%` }}
                    />
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-industrial-darker/50">
                  <p className="text-xs text-gray-500">Consommation</p>
                  <p className="text-lg font-semibold text-white">{cluster.powerDraw} kW</p>
                </div>
                <div className="p-3 rounded-lg bg-industrial-darker/50">
                  <p className="text-xs text-gray-500">Empreinte carbone</p>
                  <p className="text-lg font-semibold text-white">{cluster.carbonFootprint} kgCO2/j</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Recommendation Card
function RecommendationCard({ recommendation }) {
  const effortColors = {
    low: 'bg-green-500/20 text-green-400',
    medium: 'bg-yellow-500/20 text-yellow-400',
    high: 'bg-red-500/20 text-red-400'
  }

  const statusColors = {
    proposed: 'border-gray-500/50 bg-gray-500/5',
    in_progress: 'border-blue-500/50 bg-blue-500/5',
    planned: 'border-purple-500/50 bg-purple-500/5',
    completed: 'border-green-500/50 bg-green-500/5'
  }

  const statusLabels = {
    proposed: 'Proposé',
    in_progress: 'En cours',
    planned: 'Planifié',
    completed: 'Terminé'
  }

  return (
    <motion.div
      whileHover={{ x: 4 }}
      className={`p-4 rounded-xl border ${statusColors[recommendation.status]}`}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-xs bg-white/10 text-gray-300">
              {recommendation.category}
            </span>
            <span className={`px-2 py-0.5 rounded text-xs ${effortColors[recommendation.effort]}`}>
              Effort: {recommendation.effort}
            </span>
          </div>
          <h4 className="font-medium text-white">{recommendation.title}</h4>
          <p className="text-sm text-gray-400 mt-1">{recommendation.impact}</p>
        </div>
        <span className={`px-2 py-1 rounded text-xs ${
          recommendation.status === 'completed' ? 'bg-green-500/20 text-green-400' :
          recommendation.status === 'in_progress' ? 'bg-blue-500/20 text-blue-400' :
          recommendation.status === 'planned' ? 'bg-purple-500/20 text-purple-400' :
          'bg-gray-500/20 text-gray-400'
        }`}>
          {statusLabels[recommendation.status]}
        </span>
      </div>
      <div className="flex items-center gap-4 text-xs">
        <span className="flex items-center gap-1 text-green-400">
          <Leaf className="w-3 h-3" />
          {recommendation.savings}
        </span>
        <span className="flex items-center gap-1 text-cyan-400">
          <TrendingDown className="w-3 h-3" />
          {recommendation.costSaving}
        </span>
      </div>
    </motion.div>
  )
}

function GreenITDashboardView() {
  const { t } = useI18n()
  const [activeTab, setActiveTab] = useState('overview')
  const [expandedCluster, setExpandedCluster] = useState(null)

  const pueTrend = generatePUETrend()
  const energyTrend = generateEnergyTrend()

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: Eye },
    { id: 'datacenter', label: 'Datacenter', icon: Server },
    { id: 'cloud', label: 'Cloud Carbon', icon: Cloud },
    { id: 'equipment', label: 'Équipements', icon: Laptop },
    { id: 'optimization', label: 'Optimisations', icon: Target }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-teal-600 flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            Dashboard Green IT
          </h1>
          <p className="text-gray-400 mt-1">
            Efficience énergétique, PUE et empreinte carbone IT
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn btn-ghost flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Actualiser
          </button>
          <button className="btn btn-ghost flex items-center gap-2">
            <Download className="w-4 h-4" />
            Rapport
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all
                ${activeTab === tab.id
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                  : 'bg-industrial-card/50 text-gray-400 border border-industrial-border hover:text-white'
                }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <MetricCard
          label="PUE actuel"
          value={pueData.current.toFixed(2)}
          icon={Gauge}
          color={pueData.current <= 1.4 ? 'green' : pueData.current <= 1.6 ? 'yellow' : 'red'}
          trend={pueData.trend}
        />
        <MetricCard
          label="Consommation IT"
          value={`${(datacenterMetrics.itLoad / 1000).toFixed(1)}`}
          unit="MW"
          icon={Zap}
          color="cyan"
        />
        <MetricCard
          label="% Renouvelable"
          value={datacenterMetrics.renewableShare}
          unit="%"
          icon={Sun}
          color="green"
        />
        <MetricCard
          label="Cloud CO2"
          value={cloudCarbon.totalMonthly}
          unit="tCO2e/mois"
          icon={Cloud}
          color="blue"
          trend={cloudCarbon.trend}
        />
        <MetricCard
          label="Équipements"
          value={equipmentLifecycle.totalDevices}
          icon={Monitor}
          color="purple"
        />
        <MetricCard
          label="Taux recyclage"
          value={equipmentLifecycle.ewasteRate}
          unit="%"
          icon={Recycle}
          color="green"
        />
      </div>

      {activeTab === 'overview' && (
        <>
          {/* PUE & Energy */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-1">
              <CardHeader
                title="PUE (Power Usage Effectiveness)"
                subtitle="Efficacité énergétique datacenter"
                icon={Gauge}
              />
              <CardBody>
                <div className="flex flex-col items-center">
                  <SemiCircleGauge
                    value={pueData.current}
                    max={2.5}
                    label="PUE"
                    color={pueData.current <= 1.4 ? '#22c55e' : pueData.current <= 1.6 ? '#eab308' : '#ef4444'}
                  />
                  <div className="mt-4 grid grid-cols-2 gap-4 w-full">
                    <div className="p-3 rounded-lg bg-industrial-darker/50 text-center">
                      <p className="text-xs text-gray-500">Objectif</p>
                      <p className="text-lg font-semibold text-cyan-400">{pueData.target}</p>
                    </div>
                    <div className="p-3 rounded-lg bg-industrial-darker/50 text-center">
                      <p className="text-xs text-gray-500">Moyenne</p>
                      <p className="text-lg font-semibold text-gray-400">{pueData.average}</p>
                    </div>
                  </div>
                  <div className="mt-3 p-3 rounded-lg bg-green-500/10 border border-green-500/30 w-full">
                    <div className="flex items-center gap-2">
                      <TrendingDown className="w-4 h-4 text-green-400" />
                      <span className="text-sm text-green-400">{pueData.trend}% vs mois précédent</span>
                    </div>
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader
                title="Tendance PUE 24h"
                subtitle="Variation horaire"
                icon={Activity}
              />
              <CardBody>
                <div className="h-64">
                  <TimeSeriesChart
                    data={pueTrend}
                    lines={[
                      { key: 'pue', color: '#22c55e', name: 'PUE' }
                    ]}
                  />
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Power Distribution & Recommendations */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader
                title="Répartition consommation"
                subtitle="Distribution par catégorie"
                icon={Zap}
              />
              <CardBody>
                <div className="flex items-center gap-8">
                  <div className="w-40 h-40">
                    <DonutChart data={powerDistribution} />
                  </div>
                  <div className="flex-1 space-y-3">
                    {powerDistribution.map((item) => (
                      <div key={item.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                          <span className="text-sm text-gray-400">{item.name}</span>
                        </div>
                        <span className="text-sm font-medium text-white">{item.value} kW</span>
                      </div>
                    ))}
                    <div className="pt-2 border-t border-industrial-border">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-400 font-medium">Total</span>
                        <span className="text-sm font-bold text-white">{datacenterMetrics.totalPower} kW</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader
                title="Recommandations"
                subtitle="Optimisations proposées"
                icon={Target}
              />
              <CardBody>
                <div className="space-y-3">
                  {optimizationRecommendations.slice(0, 3).map((rec) => (
                    <RecommendationCard key={rec.id} recommendation={rec} />
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>
        </>
      )}

      {activeTab === 'datacenter' && (
        <>
          <Card>
            <CardHeader
              title="Efficacité des clusters"
              subtitle="Utilisation et consommation par cluster"
              icon={Server}
            />
            <CardBody>
              <div className="space-y-3">
                {serverEfficiency.map((cluster) => (
                  <ServerClusterCard
                    key={cluster.id}
                    cluster={cluster}
                    isExpanded={expandedCluster === cluster.id}
                    onToggle={() => setExpandedCluster(expandedCluster === cluster.id ? null : cluster.id)}
                  />
                ))}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="Consommation énergétique"
              subtitle="Évolution sur 30 jours"
              icon={Zap}
            />
            <CardBody>
              <div className="h-64">
                <TimeSeriesChart
                  data={energyTrend}
                  lines={[
                    { key: 'consumption', color: '#3b82f6', name: 'Consommation totale' },
                    { key: 'renewable', color: '#22c55e', name: 'Énergie renouvelable' }
                  ]}
                />
              </div>
            </CardBody>
          </Card>
        </>
      )}

      {activeTab === 'cloud' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader
              title="Empreinte cloud par provider"
              subtitle="Émissions CO2 par fournisseur"
              icon={Cloud}
            />
            <CardBody>
              <div className="space-y-4">
                {cloudCarbon.providers.map((provider) => (
                  <div key={provider.name} className="p-4 rounded-xl border border-industrial-border bg-industrial-card/50">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="font-semibold text-white">{provider.name}</h4>
                        <p className="text-sm text-gray-400">{provider.region}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-white">{provider.carbon}</p>
                        <p className="text-xs text-gray-500">tCO2e/mois</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      <div className="p-2 rounded-lg bg-industrial-darker/50 text-center">
                        <p className="text-xs text-gray-500">Compute</p>
                        <p className="text-sm font-medium text-blue-400">{provider.compute} t</p>
                      </div>
                      <div className="p-2 rounded-lg bg-industrial-darker/50 text-center">
                        <p className="text-xs text-gray-500">Storage</p>
                        <p className="text-sm font-medium text-cyan-400">{provider.storage} t</p>
                      </div>
                      <div className="p-2 rounded-lg bg-industrial-darker/50 text-center">
                        <p className="text-xs text-gray-500">Network</p>
                        <p className="text-sm font-medium text-purple-400">{provider.network} t</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="Évolution empreinte cloud"
              subtitle="Tendance mensuelle"
              icon={TrendingDown}
            />
            <CardBody>
              <div className="flex flex-col items-center mb-6">
                <div className="text-4xl font-bold text-white">{cloudCarbon.totalMonthly}</div>
                <div className="text-sm text-gray-400">tCO2e / mois</div>
                <div className={`flex items-center gap-1 mt-2 ${cloudCarbon.trend < 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {cloudCarbon.trend < 0 ? <TrendingDown className="w-4 h-4" /> : <TrendingUp className="w-4 h-4" />}
                  <span className="text-sm font-medium">{Math.abs(cloudCarbon.trend)}% vs mois précédent</span>
                </div>
              </div>
              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
                  <h4 className="font-medium text-green-400 mb-2">Actions réalisées</h4>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>• Migration vers régions bas carbone</li>
                    <li>• Optimisation instances spot</li>
                    <li>• Compression stockage froid</li>
                  </ul>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>
      )}

      {activeTab === 'equipment' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader
              title="Cycle de vie équipements"
              subtitle="Âge moyen par catégorie"
              icon={Laptop}
            />
            <CardBody>
              <div className="space-y-4">
                {equipmentLifecycle.categories.map((cat) => {
                  const ageRatio = cat.avgAge / cat.targetAge
                  return (
                    <div key={cat.name} className="p-3 rounded-lg bg-industrial-darker/50">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <p className="text-sm font-medium text-white">{cat.name}</p>
                          <p className="text-xs text-gray-500">{cat.count} unités</p>
                        </div>
                        <div className="text-right">
                          <p className={`text-sm font-semibold ${
                            cat.status === 'good' ? 'text-green-400' : 'text-yellow-400'
                          }`}>
                            {cat.avgAge} / {cat.targetAge} ans
                          </p>
                        </div>
                      </div>
                      <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            ageRatio <= 0.7 ? 'bg-green-500' :
                            ageRatio <= 0.9 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${Math.min(100, ageRatio * 100)}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="Gestion e-waste"
              subtitle="Recyclage et réutilisation"
              icon={Recycle}
            />
            <CardBody>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/30 text-center">
                  <p className="text-3xl font-bold text-green-400">{equipmentLifecycle.recycledLastYear}</p>
                  <p className="text-sm text-gray-400">Équipements recyclés</p>
                  <p className="text-xs text-gray-500">année en cours</p>
                </div>
                <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 text-center">
                  <p className="text-3xl font-bold text-blue-400">{equipmentLifecycle.refurbishedLastYear}</p>
                  <p className="text-sm text-gray-400">Reconditionnés</p>
                  <p className="text-xs text-gray-500">année en cours</p>
                </div>
              </div>
              <div className="p-4 rounded-lg bg-industrial-darker/50">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Taux de traitement DEEE</span>
                  <span className="text-lg font-bold text-green-400">{equipmentLifecycle.ewasteRate}%</span>
                </div>
                <div className="h-3 bg-industrial-darker rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full"
                    style={{ width: `${equipmentLifecycle.ewasteRate}%` }}
                  />
                </div>
              </div>
            </CardBody>
          </Card>
        </div>
      )}

      {activeTab === 'optimization' && (
        <Card>
          <CardHeader
            title="Plan d'optimisation Green IT"
            subtitle="Recommandations et actions"
            icon={Target}
          />
          <CardBody>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {optimizationRecommendations.map((rec) => (
                <RecommendationCard key={rec.id} recommendation={rec} />
              ))}
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}

export default GreenITDashboardView
