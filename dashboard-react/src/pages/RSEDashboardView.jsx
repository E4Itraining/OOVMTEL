import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  TreePine,
  Leaf,
  Factory,
  Zap,
  Droplets,
  Wind,
  Sun,
  Thermometer,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Target,
  Award,
  FileText,
  Calendar,
  Clock,
  ChevronRight,
  ChevronDown,
  RefreshCw,
  Download,
  Eye,
  Globe,
  Building2,
  Truck,
  Users,
  Heart,
  Shield,
  Recycle,
  AlertTriangle,
  CheckCircle2,
  Info,
  Activity
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { TimeSeriesChart, DonutChart, BarChartComponent, AreaChartComponent } from '../components/ui/Charts'
import { StatusBadge, HealthIndicator } from '../components/ui/Status'
import { RadialGauge, LinearGauge, SemiCircleGauge } from '../components/ui/Gauge'

// Carbon footprint data
const carbonFootprint = {
  total: 4250, // tonnes CO2e
  scope1: 850, // Direct emissions
  scope2: 1200, // Indirect energy
  scope3: 2200, // Value chain
  target: 3500,
  reduction: -12.5, // vs last year
  offsetted: 500
}

// ESG Scores
const esgScores = {
  overall: 72,
  environmental: 68,
  social: 78,
  governance: 71,
  trend: +5
}

// CSRD Indicators
const csrdIndicators = [
  {
    id: 'e1',
    category: 'E1 - Changement climatique',
    metrics: [
      { name: 'Émissions GES Scope 1', value: '850 tCO2e', status: 'on_track', target: '< 1000 tCO2e' },
      { name: 'Émissions GES Scope 2', value: '1200 tCO2e', status: 'warning', target: '< 1000 tCO2e' },
      { name: 'Émissions GES Scope 3', value: '2200 tCO2e', status: 'at_risk', target: '< 1800 tCO2e' }
    ],
    score: 65
  },
  {
    id: 'e2',
    category: 'E2 - Pollution',
    metrics: [
      { name: 'Rejets atmosphériques', value: '45 kg', status: 'on_track', target: '< 100 kg' },
      { name: 'Rejets aquatiques', value: '12 m³', status: 'on_track', target: '< 50 m³' }
    ],
    score: 85
  },
  {
    id: 'e3',
    category: 'E3 - Eau & ressources marines',
    metrics: [
      { name: 'Consommation d\'eau', value: '25000 m³', status: 'on_track', target: '< 30000 m³' },
      { name: 'Recyclage eaux', value: '45%', status: 'warning', target: '> 60%' }
    ],
    score: 72
  },
  {
    id: 'e4',
    category: 'E4 - Biodiversité & écosystèmes',
    metrics: [
      { name: 'Surface sites naturels', value: '2.5 ha', status: 'on_track', target: '> 2 ha' },
      { name: 'Espèces protégées', value: '12', status: 'on_track', target: 'Monitoring' }
    ],
    score: 80
  },
  {
    id: 'e5',
    category: 'E5 - Économie circulaire',
    metrics: [
      { name: 'Taux recyclage déchets', value: '78%', status: 'on_track', target: '> 75%' },
      { name: 'Matériaux recyclés utilisés', value: '35%', status: 'warning', target: '> 50%' }
    ],
    score: 68
  },
  {
    id: 's1',
    category: 'S1 - Effectifs propres',
    metrics: [
      { name: 'Taux d\'accidents', value: '1.2', status: 'on_track', target: '< 2' },
      { name: 'Heures formation/employé', value: '32h', status: 'on_track', target: '> 25h' },
      { name: 'Égalité salariale H/F', value: '96%', status: 'on_track', target: '> 95%' }
    ],
    score: 82
  },
  {
    id: 'g1',
    category: 'G1 - Gouvernance',
    metrics: [
      { name: 'Diversité conseil', value: '40%', status: 'on_track', target: '> 33%' },
      { name: 'Politique anti-corruption', value: 'Oui', status: 'on_track', target: 'Requis' }
    ],
    score: 75
  }
]

// Energy consumption breakdown
const energyBreakdown = [
  { name: 'Électricité', value: 45, color: '#3b82f6' },
  { name: 'Gaz naturel', value: 25, color: '#f59e0b' },
  { name: 'Carburants', value: 20, color: '#ef4444' },
  { name: 'Renouvelables', value: 10, color: '#22c55e' }
]

// Sustainability initiatives
const sustainabilityInitiatives = [
  {
    id: 'init-001',
    name: 'Installation panneaux solaires',
    category: 'Énergie',
    status: 'in_progress',
    progress: 65,
    impact: '-150 tCO2e/an',
    deadline: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000),
    budget: '450k€'
  },
  {
    id: 'init-002',
    name: 'Flotte véhicules électriques',
    category: 'Transport',
    status: 'in_progress',
    progress: 40,
    impact: '-80 tCO2e/an',
    deadline: new Date(Date.now() + 180 * 24 * 60 * 60 * 1000),
    budget: '320k€'
  },
  {
    id: 'init-003',
    name: 'Optimisation énergétique bâtiments',
    category: 'Bâtiments',
    status: 'planned',
    progress: 10,
    impact: '-200 tCO2e/an',
    deadline: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
    budget: '850k€'
  },
  {
    id: 'init-004',
    name: 'Programme zéro déchet',
    category: 'Déchets',
    status: 'completed',
    progress: 100,
    impact: '-50 tCO2e/an',
    deadline: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    budget: '75k€'
  }
]

// Generate carbon trend data
const generateCarbonTrend = () => {
  const data = []
  for (let i = 11; i >= 0; i--) {
    const date = new Date()
    date.setMonth(date.getMonth() - i)
    data.push({
      time: date.toLocaleDateString('fr-FR', { month: 'short', year: '2-digit' }),
      scope1: Math.floor(70 + Math.random() * 20),
      scope2: Math.floor(100 + Math.random() * 30),
      scope3: Math.floor(180 + Math.random() * 40)
    })
  }
  return data
}

// Generate ESG trend data
const generateESGTrend = () => {
  const data = []
  for (let i = 11; i >= 0; i--) {
    const date = new Date()
    date.setMonth(date.getMonth() - i)
    data.push({
      time: date.toLocaleDateString('fr-FR', { month: 'short', year: '2-digit' }),
      environmental: Math.min(100, 55 + Math.random() * 10 + (11 - i) * 1.2),
      social: Math.min(100, 65 + Math.random() * 8 + (11 - i) * 1),
      governance: Math.min(100, 60 + Math.random() * 12 + (11 - i) * 0.9)
    })
  }
  return data
}

// Scope Distribution Chart Data
const scopeDistribution = [
  { name: 'Scope 1', value: carbonFootprint.scope1, color: '#22c55e' },
  { name: 'Scope 2', value: carbonFootprint.scope2, color: '#3b82f6' },
  { name: 'Scope 3', value: carbonFootprint.scope3, color: '#f59e0b' }
]

// CSRD Category Card
function CSRDCategoryCard({ indicator, isExpanded, onToggle }) {
  const statusColors = {
    on_track: 'text-green-400',
    warning: 'text-yellow-400',
    at_risk: 'text-red-400'
  }

  const statusIcons = {
    on_track: CheckCircle2,
    warning: AlertTriangle,
    at_risk: AlertTriangle
  }

  return (
    <motion.div
      className="rounded-xl border border-industrial-border bg-industrial-card/50 transition-all duration-300"
      layout
    >
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12">
            <RadialGauge
              value={indicator.score}
              max={100}
              color={indicator.score >= 75 ? '#22c55e' : indicator.score >= 50 ? '#eab308' : '#ef4444'}
              size={48}
              showLabel
            />
          </div>
          <div>
            <h3 className="font-semibold text-white">{indicator.category}</h3>
            <p className="text-sm text-gray-400">{indicator.metrics.length} indicateurs</p>
          </div>
        </div>
        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 pt-2 border-t border-industrial-border/50 space-y-3">
              {indicator.metrics.map((metric, idx) => {
                const StatusIcon = statusIcons[metric.status]
                return (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-industrial-darker/50">
                    <div className="flex items-center gap-3">
                      <StatusIcon className={`w-4 h-4 ${statusColors[metric.status]}`} />
                      <div>
                        <p className="text-sm text-white">{metric.name}</p>
                        <p className="text-xs text-gray-500">Cible: {metric.target}</p>
                      </div>
                    </div>
                    <span className={`font-semibold ${statusColors[metric.status]}`}>{metric.value}</span>
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Initiative Card
function InitiativeCard({ initiative }) {
  const statusColors = {
    completed: 'border-green-500/50 bg-green-500/5',
    in_progress: 'border-blue-500/50 bg-blue-500/5',
    planned: 'border-gray-500/50 bg-gray-500/5'
  }

  const statusLabels = {
    completed: 'Terminé',
    in_progress: 'En cours',
    planned: 'Planifié'
  }

  const daysUntilDeadline = Math.ceil((initiative.deadline - new Date()) / (1000 * 60 * 60 * 24))

  return (
    <motion.div
      whileHover={{ x: 4 }}
      className={`p-4 rounded-xl border ${statusColors[initiative.status]}`}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-xs bg-white/10 text-gray-300">
              {initiative.category}
            </span>
            <span className={`px-2 py-0.5 rounded text-xs ${
              initiative.status === 'completed' ? 'bg-green-500/20 text-green-400' :
              initiative.status === 'in_progress' ? 'bg-blue-500/20 text-blue-400' :
              'bg-gray-500/20 text-gray-400'
            }`}>
              {statusLabels[initiative.status]}
            </span>
          </div>
          <h4 className="font-medium text-white">{initiative.name}</h4>
          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Leaf className="w-3 h-3 text-green-400" />
              {initiative.impact}
            </span>
            <span>Budget: {initiative.budget}</span>
            {initiative.status !== 'completed' && (
              <span className={daysUntilDeadline <= 30 ? 'text-yellow-400' : ''}>
                {daysUntilDeadline}j restants
              </span>
            )}
          </div>
        </div>
      </div>
      {initiative.status !== 'completed' && (
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Progression</span>
            <span className="text-white">{initiative.progress}%</span>
          </div>
          <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full"
              style={{ width: `${initiative.progress}%` }}
            />
          </div>
        </div>
      )}
    </motion.div>
  )
}

function RSEDashboardView() {
  const { t } = useI18n()
  const [activeTab, setActiveTab] = useState('overview')
  const [expandedCategory, setExpandedCategory] = useState(null)

  const carbonTrend = generateCarbonTrend()
  const esgTrend = generateESGTrend()

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: Eye },
    { id: 'carbon', label: 'Empreinte carbone', icon: Factory },
    { id: 'csrd', label: 'Reporting CSRD', icon: FileText },
    { id: 'initiatives', label: 'Initiatives', icon: Leaf },
    { id: 'esg', label: 'Score ESG', icon: Award }
  ]

  const carbonProgress = Math.round((1 - carbonFootprint.total / 5000) * 100)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center">
              <TreePine className="w-5 h-5 text-white" />
            </div>
            Dashboard RSE & Durabilité
          </h1>
          <p className="text-gray-400 mt-1">
            Empreinte carbone, reporting ESG/CSRD et initiatives durables
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn btn-ghost flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Actualiser
          </button>
          <button className="btn btn-ghost flex items-center gap-2">
            <Download className="w-4 h-4" />
            Rapport CSRD
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
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
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
          label="Empreinte CO2"
          value={`${(carbonFootprint.total / 1000).toFixed(1)}k`}
          unit="tCO2e"
          icon={Factory}
          color="yellow"
          trend={carbonFootprint.reduction}
        />
        <MetricCard
          label="Score ESG"
          value={esgScores.overall}
          unit="/100"
          icon={Award}
          color="green"
          trend={esgScores.trend}
        />
        <MetricCard
          label="Score E"
          value={esgScores.environmental}
          unit="/100"
          icon={Leaf}
          color={esgScores.environmental >= 70 ? 'green' : 'yellow'}
        />
        <MetricCard
          label="Score S"
          value={esgScores.social}
          unit="/100"
          icon={Users}
          color={esgScores.social >= 70 ? 'green' : 'yellow'}
        />
        <MetricCard
          label="Score G"
          value={esgScores.governance}
          unit="/100"
          icon={Shield}
          color={esgScores.governance >= 70 ? 'green' : 'yellow'}
        />
        <MetricCard
          label="Initiatives actives"
          value={sustainabilityInitiatives.filter(i => i.status === 'in_progress').length}
          icon={Target}
          color="cyan"
        />
      </div>

      {activeTab === 'overview' && (
        <>
          {/* Carbon & ESG Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-1">
              <CardHeader
                title="Empreinte carbone"
                subtitle="Répartition par scope"
                icon={Factory}
              />
              <CardBody>
                <div className="flex flex-col items-center">
                  <div className="w-40 h-40">
                    <DonutChart data={scopeDistribution} />
                  </div>
                  <div className="mt-4 w-full space-y-2">
                    {scopeDistribution.map((item) => (
                      <div key={item.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                          <span className="text-sm text-gray-400">{item.name}</span>
                        </div>
                        <span className="text-sm font-medium text-white">{item.value} tCO2e</span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 p-3 rounded-lg bg-green-500/10 border border-green-500/30 w-full">
                    <div className="flex items-center gap-2">
                      <TrendingDown className="w-4 h-4 text-green-400" />
                      <span className="text-sm text-green-400">{carbonFootprint.reduction}% vs année précédente</span>
                    </div>
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader
                title="Évolution des émissions"
                subtitle="Tendance sur 12 mois par scope"
                icon={TrendingUp}
              />
              <CardBody>
                <div className="h-64">
                  <TimeSeriesChart
                    data={carbonTrend}
                    lines={[
                      { key: 'scope1', color: '#22c55e', name: 'Scope 1' },
                      { key: 'scope2', color: '#3b82f6', name: 'Scope 2' },
                      { key: 'scope3', color: '#f59e0b', name: 'Scope 3' }
                    ]}
                  />
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Initiatives & CSRD Summary */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader
                title="Initiatives en cours"
                subtitle="Projets de réduction d'impact"
                icon={Leaf}
              />
              <CardBody>
                <div className="space-y-3">
                  {sustainabilityInitiatives
                    .filter(i => i.status === 'in_progress')
                    .map((initiative) => (
                      <InitiativeCard key={initiative.id} initiative={initiative} />
                    ))
                  }
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader
                title="Indicateurs CSRD"
                subtitle="Performance par catégorie"
                icon={FileText}
              />
              <CardBody>
                <div className="space-y-3">
                  {csrdIndicators.slice(0, 5).map((indicator) => (
                    <div key={indicator.id} className="flex items-center gap-4">
                      <div className="w-12 h-12">
                        <RadialGauge
                          value={indicator.score}
                          max={100}
                          color={indicator.score >= 75 ? '#22c55e' : indicator.score >= 50 ? '#eab308' : '#ef4444'}
                          size={48}
                          showLabel
                        />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-white">{indicator.category}</p>
                        <p className="text-xs text-gray-400">{indicator.metrics.length} indicateurs</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>
        </>
      )}

      {activeTab === 'carbon' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-1">
            <CardHeader
              title="Objectif de réduction"
              subtitle="Trajectoire vers neutralité"
              icon={Target}
            />
            <CardBody>
              <div className="flex flex-col items-center">
                <SemiCircleGauge
                  value={carbonFootprint.total}
                  max={5000}
                  label="tCO2e"
                  color={carbonFootprint.total <= carbonFootprint.target ? '#22c55e' : '#eab308'}
                />
                <div className="mt-4 space-y-2 w-full">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Objectif 2024</span>
                    <span className="text-white">{carbonFootprint.target} tCO2e</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Émissions actuelles</span>
                    <span className="text-white">{carbonFootprint.total} tCO2e</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Compensé</span>
                    <span className="text-green-400">{carbonFootprint.offsetted} tCO2e</span>
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader
              title="Détail par scope"
              subtitle="Sources d'émissions"
              icon={Factory}
            />
            <CardBody>
              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-green-500" />
                      <span className="text-white font-medium">Scope 1 - Émissions directes</span>
                    </div>
                    <span className="text-white">{carbonFootprint.scope1} tCO2e</span>
                  </div>
                  <p className="text-sm text-gray-400 mb-2">Combustion sur site, flotte véhicules, procédés industriels</p>
                  <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
                    <div className="h-full bg-green-500 rounded-full" style={{ width: `${(carbonFootprint.scope1 / carbonFootprint.total) * 100}%` }} />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-blue-500" />
                      <span className="text-white font-medium">Scope 2 - Énergie indirecte</span>
                    </div>
                    <span className="text-white">{carbonFootprint.scope2} tCO2e</span>
                  </div>
                  <p className="text-sm text-gray-400 mb-2">Électricité, chaleur, vapeur achetés</p>
                  <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(carbonFootprint.scope2 / carbonFootprint.total) * 100}%` }} />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-yellow-500" />
                      <span className="text-white font-medium">Scope 3 - Chaîne de valeur</span>
                    </div>
                    <span className="text-white">{carbonFootprint.scope3} tCO2e</span>
                  </div>
                  <p className="text-sm text-gray-400 mb-2">Achats, transport, déplacements, fin de vie produits</p>
                  <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
                    <div className="h-full bg-yellow-500 rounded-full" style={{ width: `${(carbonFootprint.scope3 / carbonFootprint.total) * 100}%` }} />
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>

          <Card className="lg:col-span-3">
            <CardHeader
              title="Mix énergétique"
              subtitle="Répartition des sources d'énergie"
              icon={Zap}
            />
            <CardBody>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {energyBreakdown.map((source) => (
                  <div key={source.name} className="p-4 rounded-xl bg-industrial-darker/50">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${source.color}20` }}>
                        {source.name === 'Électricité' && <Zap className="w-5 h-5" style={{ color: source.color }} />}
                        {source.name === 'Gaz naturel' && <Factory className="w-5 h-5" style={{ color: source.color }} />}
                        {source.name === 'Carburants' && <Truck className="w-5 h-5" style={{ color: source.color }} />}
                        {source.name === 'Renouvelables' && <Sun className="w-5 h-5" style={{ color: source.color }} />}
                      </div>
                      <div>
                        <p className="text-white font-semibold">{source.value}%</p>
                        <p className="text-xs text-gray-400">{source.name}</p>
                      </div>
                    </div>
                    <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${source.value}%`, backgroundColor: source.color }} />
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>
      )}

      {activeTab === 'csrd' && (
        <div className="space-y-4">
          {csrdIndicators.map((indicator) => (
            <CSRDCategoryCard
              key={indicator.id}
              indicator={indicator}
              isExpanded={expandedCategory === indicator.id}
              onToggle={() => setExpandedCategory(expandedCategory === indicator.id ? null : indicator.id)}
            />
          ))}
        </div>
      )}

      {activeTab === 'initiatives' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {sustainabilityInitiatives.map((initiative) => (
            <InitiativeCard key={initiative.id} initiative={initiative} />
          ))}
        </div>
      )}

      {activeTab === 'esg' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader
              title="Scores ESG"
              subtitle="Évaluation Environnement, Social, Gouvernance"
              icon={Award}
            />
            <CardBody>
              <div className="flex flex-col items-center mb-6">
                <SemiCircleGauge
                  value={esgScores.overall}
                  max={100}
                  label="Score ESG global"
                  color={esgScores.overall >= 70 ? '#22c55e' : esgScores.overall >= 50 ? '#eab308' : '#ef4444'}
                />
              </div>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-400 flex items-center gap-2">
                      <Leaf className="w-4 h-4 text-green-400" />
                      Environnement
                    </span>
                    <span className="text-sm font-medium text-white">{esgScores.environmental}/100</span>
                  </div>
                  <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
                    <div className="h-full bg-green-500 rounded-full" style={{ width: `${esgScores.environmental}%` }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-400 flex items-center gap-2">
                      <Users className="w-4 h-4 text-blue-400" />
                      Social
                    </span>
                    <span className="text-sm font-medium text-white">{esgScores.social}/100</span>
                  </div>
                  <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: `${esgScores.social}%` }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-400 flex items-center gap-2">
                      <Shield className="w-4 h-4 text-purple-400" />
                      Gouvernance
                    </span>
                    <span className="text-sm font-medium text-white">{esgScores.governance}/100</span>
                  </div>
                  <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
                    <div className="h-full bg-purple-500 rounded-full" style={{ width: `${esgScores.governance}%` }} />
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="Évolution ESG"
              subtitle="Progression sur 12 mois"
              icon={TrendingUp}
            />
            <CardBody>
              <div className="h-64">
                <TimeSeriesChart
                  data={esgTrend}
                  lines={[
                    { key: 'environmental', color: '#22c55e', name: 'Environnement' },
                    { key: 'social', color: '#3b82f6', name: 'Social' },
                    { key: 'governance', color: '#a855f7', name: 'Gouvernance' }
                  ]}
                />
              </div>
            </CardBody>
          </Card>
        </div>
      )}
    </div>
  )
}

export default RSEDashboardView
