import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  AlertTriangle,
  ArrowDown,
  ArrowRight,
  Zap,
  Clock,
  Target,
  TrendingDown,
  Shield,
  Activity,
  Server,
  Factory,
  Database,
  Cpu,
  Network,
  GitBranch,
  Layers,
  Eye,
  ChevronDown,
  ChevronRight,
  Play,
  Pause,
  SkipForward,
  RefreshCw,
  Download,
  Filter,
  Info,
  CheckCircle,
  XCircle,
  MinusCircle
} from 'lucide-react'
import { LinearGauge } from './Gauge'

// Types d'événements de cascade
const CASCADE_EVENT_TYPES = {
  ROOT_CAUSE: 'root_cause',
  DIRECT_IMPACT: 'direct_impact',
  INDIRECT_IMPACT: 'indirect_impact',
  BUSINESS_IMPACT: 'business_impact',
  MITIGATION: 'mitigation'
}

const eventTypeConfig = {
  [CASCADE_EVENT_TYPES.ROOT_CAUSE]: {
    color: 'red',
    label: 'Cause Racine',
    icon: AlertTriangle
  },
  [CASCADE_EVENT_TYPES.DIRECT_IMPACT]: {
    color: 'orange',
    label: 'Impact Direct',
    icon: Zap
  },
  [CASCADE_EVENT_TYPES.INDIRECT_IMPACT]: {
    color: 'yellow',
    label: 'Impact Indirect',
    icon: ArrowRight
  },
  [CASCADE_EVENT_TYPES.BUSINESS_IMPACT]: {
    color: 'purple',
    label: 'Impact Métier',
    icon: Target
  },
  [CASCADE_EVENT_TYPES.MITIGATION]: {
    color: 'green',
    label: 'Mitigation',
    icon: Shield
  }
}

// Données par défaut de cascade
const defaultCascadeData = {
  id: 'cascade-001',
  title: 'Panne Servomoteur CNC Machine 02',
  startTime: '2024-01-15T08:23:00Z',
  status: 'active', // active, contained, resolved
  severity: 'critical',
  timeline: [
    {
      id: 'evt-1',
      timestamp: '08:23:15',
      type: CASCADE_EVENT_TYPES.ROOT_CAUSE,
      system: 'CNC Machine 02',
      systemType: 'ot_equipment',
      description: 'Défaillance servomoteur axe Y détectée',
      metrics: { temperature: '95°C', vibration: 'Critique' },
      affectedCapacity: 100
    },
    {
      id: 'evt-2',
      timestamp: '08:23:45',
      type: CASCADE_EVENT_TYPES.DIRECT_IMPACT,
      system: 'OPC-UA Gateway',
      systemType: 'ot_opcua',
      description: 'Perte de communication avec Machine 02',
      metrics: { lostTags: 45, reconnectAttempts: 3 },
      affectedCapacity: 15
    },
    {
      id: 'evt-3',
      timestamp: '08:24:00',
      type: CASCADE_EVENT_TYPES.DIRECT_IMPACT,
      system: 'SCADA Central',
      systemType: 'ot_scada',
      description: 'Alarme critique générée',
      metrics: { alarmLevel: 'P1', acknowledged: false },
      affectedCapacity: 0
    },
    {
      id: 'evt-4',
      timestamp: '08:25:00',
      type: CASCADE_EVENT_TYPES.DIRECT_IMPACT,
      system: 'MES Production',
      systemType: 'ot_mes',
      description: 'Ordre de fabrication OF-2024-1234 bloqué',
      metrics: { affectedOrders: 12, queueBacklog: '+8' },
      affectedCapacity: 25
    },
    {
      id: 'evt-5',
      timestamp: '08:26:00',
      type: CASCADE_EVENT_TYPES.INDIRECT_IMPACT,
      system: 'Ligne B - Usinage',
      systemType: 'ot_production_line',
      description: 'Production ralentie à 50% de capacité',
      metrics: { currentOEE: '45%', targetOEE: '85%' },
      affectedCapacity: 50
    },
    {
      id: 'evt-6',
      timestamp: '08:30:00',
      type: CASCADE_EVENT_TYPES.INDIRECT_IMPACT,
      system: 'Robot Soudure',
      systemType: 'ot_equipment',
      description: 'Attente pièces en amont - cycle interrompu',
      metrics: { waitTime: '4min 30s', cyclesLost: 12 },
      affectedCapacity: 30
    },
    {
      id: 'evt-7',
      timestamp: '08:35:00',
      type: CASCADE_EVENT_TYPES.INDIRECT_IMPACT,
      system: 'Ligne C - Finition',
      systemType: 'ot_production_line',
      description: 'Pénurie de pièces en entrée',
      metrics: { bufferLevel: '15%', eta: '12min' },
      affectedCapacity: 20
    },
    {
      id: 'evt-8',
      timestamp: '08:45:00',
      type: CASCADE_EVENT_TYPES.BUSINESS_IMPACT,
      system: 'Production Journalière',
      systemType: 'business_process',
      description: 'Objectif production compromis',
      metrics: { gap: '-180 unités', impactRevenu: '15 600€' },
      affectedCapacity: 40
    },
    {
      id: 'evt-9',
      timestamp: '09:00:00',
      type: CASCADE_EVENT_TYPES.BUSINESS_IMPACT,
      system: 'Expédition Client',
      systemType: 'business_process',
      description: 'Risque retard commande CLI-2024-567',
      metrics: { clientPriority: 'VIP', penalty: '2 500€' },
      affectedCapacity: 15
    },
    {
      id: 'evt-10',
      timestamp: '09:15:00',
      type: CASCADE_EVENT_TYPES.MITIGATION,
      system: 'Équipe Maintenance',
      systemType: 'human',
      description: 'Intervention technique initiée',
      metrics: { eta: '45min', technicien: 'J. Martin' },
      affectedCapacity: 0
    }
  ],
  affectedSystems: {
    direct: ['CNC Machine 02', 'OPC-UA Gateway', 'SCADA Central', 'MES Production'],
    indirect: ['Ligne B - Usinage', 'Robot Soudure', 'Ligne C - Finition'],
    business: ['Production Journalière', 'Expédition Client']
  },
  kpis: {
    totalDowntime: 52, // minutes
    productionLoss: 180, // unités
    financialImpact: 18100, // €
    systemsAffected: 9,
    mttr: 45 // minutes estimé
  }
}

// Timeline d'un événement de cascade
function CascadeEventCard({ event, isExpanded, onToggle, showConnector = true }) {
  const config = eventTypeConfig[event.type]
  const Icon = config.icon

  const systemIcons = {
    ot_equipment: Zap,
    ot_opcua: Network,
    ot_scada: Cpu,
    ot_mes: Factory,
    ot_production_line: GitBranch,
    business_process: Target,
    human: Activity
  }
  const SystemIcon = systemIcons[event.systemType] || Server

  return (
    <div className="relative">
      {/* Connecteur vertical */}
      {showConnector && (
        <div className="absolute left-6 top-12 w-0.5 h-full bg-industrial-border" />
      )}

      <motion.div
        className={`relative z-10 ml-0 p-4 rounded-xl border-2 transition-all cursor-pointer ${
          isExpanded
            ? `bg-${config.color}-500/10 border-${config.color}-500/50`
            : 'bg-industrial-card border-industrial-border hover:border-industrial-accent/30'
        }`}
        onClick={onToggle}
        whileHover={{ x: 4 }}
      >
        <div className="flex items-start gap-4">
          {/* Indicateur de temps et type */}
          <div className="flex flex-col items-center">
            <div className={`w-12 h-12 rounded-xl bg-${config.color}-500/20 flex items-center justify-center`}>
              <Icon className={`w-6 h-6 text-${config.color}-400`} />
            </div>
            <span className="mt-2 text-xs text-gray-400">{event.timestamp}</span>
          </div>

          {/* Contenu principal */}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className={`px-2 py-0.5 rounded text-xs bg-${config.color}-500/20 text-${config.color}-400`}>
                {config.label}
              </span>
              <span className="text-sm text-gray-400 flex items-center gap-1">
                <SystemIcon className="w-3 h-3" />
                {event.system}
              </span>
            </div>

            <p className="text-sm text-white mb-2">{event.description}</p>

            {/* Métriques */}
            <div className="flex flex-wrap gap-3">
              {Object.entries(event.metrics).map(([key, value]) => (
                <div key={key} className="text-xs">
                  <span className="text-gray-500">{key}: </span>
                  <span className={`font-medium ${
                    event.type === CASCADE_EVENT_TYPES.ROOT_CAUSE ? 'text-red-400' :
                    event.type === CASCADE_EVENT_TYPES.MITIGATION ? 'text-green-400' :
                    'text-white'
                  }`}>{value}</span>
                </div>
              ))}
            </div>

            {/* Barre d'impact sur capacité */}
            {event.affectedCapacity > 0 && (
              <div className="mt-3">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-400">Impact capacité</span>
                  <span className={`${
                    event.affectedCapacity > 50 ? 'text-red-400' :
                    event.affectedCapacity > 25 ? 'text-yellow-400' :
                    'text-orange-400'
                  }`}>{event.affectedCapacity}%</span>
                </div>
                <div className="h-1.5 bg-industrial-border rounded-full overflow-hidden">
                  <motion.div
                    className={`h-full ${
                      event.affectedCapacity > 50 ? 'bg-red-500' :
                      event.affectedCapacity > 25 ? 'bg-yellow-500' :
                      'bg-orange-500'
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${event.affectedCapacity}%` }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                  />
                </div>
              </div>
            )}
          </div>

          <ChevronRight className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
        </div>
      </motion.div>
    </div>
  )
}

// Graphe de propagation simplifié
function PropagationGraph({ cascade }) {
  const layers = useMemo(() => {
    return [
      { label: 'Cause Racine', events: cascade.timeline.filter(e => e.type === CASCADE_EVENT_TYPES.ROOT_CAUSE) },
      { label: 'Impacts Directs', events: cascade.timeline.filter(e => e.type === CASCADE_EVENT_TYPES.DIRECT_IMPACT) },
      { label: 'Impacts Indirects', events: cascade.timeline.filter(e => e.type === CASCADE_EVENT_TYPES.INDIRECT_IMPACT) },
      { label: 'Impacts Métier', events: cascade.timeline.filter(e => e.type === CASCADE_EVENT_TYPES.BUSINESS_IMPACT) },
      { label: 'Mitigation', events: cascade.timeline.filter(e => e.type === CASCADE_EVENT_TYPES.MITIGATION) }
    ].filter(layer => layer.events.length > 0)
  }, [cascade.timeline])

  return (
    <div className="p-4 bg-industrial-card border border-industrial-border rounded-xl">
      <h4 className="font-medium text-white mb-4 flex items-center gap-2">
        <Eye className="w-4 h-4 text-cyan-400" />
        Vue Propagation
      </h4>

      <div className="space-y-4">
        {layers.map((layer, layerIdx) => (
          <div key={layer.label}>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs text-gray-400">{layer.label}</span>
              <div className="flex-1 h-px bg-industrial-border" />
            </div>

            <div className="flex flex-wrap gap-2">
              {layer.events.map(event => {
                const config = eventTypeConfig[event.type]
                return (
                  <div
                    key={event.id}
                    className={`px-3 py-1.5 rounded-lg bg-${config.color}-500/10 border border-${config.color}-500/30 text-xs`}
                  >
                    <span className={`text-${config.color}-400`}>{event.system}</span>
                  </div>
                )
              })}
            </div>

            {layerIdx < layers.length - 1 && (
              <div className="flex justify-center my-2">
                <ArrowDown className="w-4 h-4 text-gray-500" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// KPIs de la cascade
function CascadeKPIs({ kpis }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
      <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
        <div className="flex items-center gap-2 mb-1">
          <Clock className="w-4 h-4 text-red-400" />
          <span className="text-xs text-gray-400">Downtime</span>
        </div>
        <div className="text-xl font-bold text-red-400">{kpis.totalDowntime}min</div>
      </div>

      <div className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/20">
        <div className="flex items-center gap-2 mb-1">
          <TrendingDown className="w-4 h-4 text-orange-400" />
          <span className="text-xs text-gray-400">Production</span>
        </div>
        <div className="text-xl font-bold text-orange-400">-{kpis.productionLoss}</div>
      </div>

      <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/20">
        <div className="flex items-center gap-2 mb-1">
          <Target className="w-4 h-4 text-purple-400" />
          <span className="text-xs text-gray-400">Impact €</span>
        </div>
        <div className="text-xl font-bold text-purple-400">{kpis.financialImpact.toLocaleString()}€</div>
      </div>

      <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
        <div className="flex items-center gap-2 mb-1">
          <Layers className="w-4 h-4 text-yellow-400" />
          <span className="text-xs text-gray-400">Systèmes</span>
        </div>
        <div className="text-xl font-bold text-yellow-400">{kpis.systemsAffected}</div>
      </div>

      <div className="p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
        <div className="flex items-center gap-2 mb-1">
          <Activity className="w-4 h-4 text-cyan-400" />
          <span className="text-xs text-gray-400">MTTR Est.</span>
        </div>
        <div className="text-xl font-bold text-cyan-400">{kpis.mttr}min</div>
      </div>
    </div>
  )
}

// Résumé des systèmes affectés
function AffectedSystemsSummary({ systems }) {
  return (
    <div className="p-4 bg-industrial-card border border-industrial-border rounded-xl">
      <h4 className="font-medium text-white mb-4 flex items-center gap-2">
        <AlertTriangle className="w-4 h-4 text-red-400" />
        Systèmes Affectés
      </h4>

      <div className="space-y-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2 h-2 rounded-full bg-red-500" />
            <span className="text-xs text-gray-400">Impact Direct ({systems.direct.length})</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {systems.direct.map(sys => (
              <span key={sys} className="px-2 py-1 rounded bg-red-500/10 text-xs text-red-400">
                {sys}
              </span>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2 h-2 rounded-full bg-yellow-500" />
            <span className="text-xs text-gray-400">Impact Indirect ({systems.indirect.length})</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {systems.indirect.map(sys => (
              <span key={sys} className="px-2 py-1 rounded bg-yellow-500/10 text-xs text-yellow-400">
                {sys}
              </span>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2 h-2 rounded-full bg-purple-500" />
            <span className="text-xs text-gray-400">Impact Métier ({systems.business.length})</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {systems.business.map(sys => (
              <span key={sys} className="px-2 py-1 rounded bg-purple-500/10 text-xs text-purple-400">
                {sys}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Composant principal d'analyse de cascade
export function CascadeAnalysisView({ cascade = defaultCascadeData }) {
  const [expandedEvent, setExpandedEvent] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentEventIndex, setCurrentEventIndex] = useState(0)
  const [filterType, setFilterType] = useState('all')

  const filteredTimeline = useMemo(() => {
    if (filterType === 'all') return cascade.timeline
    return cascade.timeline.filter(e => e.type === filterType)
  }, [cascade.timeline, filterType])

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying)
  }

  const handleNext = () => {
    if (currentEventIndex < cascade.timeline.length - 1) {
      setCurrentEventIndex(currentEventIndex + 1)
    }
  }

  const statusConfig = {
    active: { color: 'red', label: 'En cours', icon: AlertTriangle },
    contained: { color: 'yellow', label: 'Contenu', icon: MinusCircle },
    resolved: { color: 'green', label: 'Résolu', icon: CheckCircle }
  }
  const status = statusConfig[cascade.status]
  const StatusIcon = status.icon

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <div className={`w-14 h-14 rounded-2xl bg-${status.color}-500/20 flex items-center justify-center`}>
            <StatusIcon className={`w-7 h-7 text-${status.color}-400`} />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h2 className="text-xl font-bold text-white">{cascade.title}</h2>
              <span className={`px-2 py-0.5 rounded text-xs bg-${status.color}-500/20 text-${status.color}-400`}>
                {status.label}
              </span>
            </div>
            <p className="text-sm text-gray-400">
              Démarré à {new Date(cascade.startTime).toLocaleTimeString('fr-FR')} •
              {cascade.timeline.length} événements dans la chaîne
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="p-2 rounded-lg bg-industrial-border hover:bg-industrial-accent/20 transition-colors">
            <RefreshCw className="w-4 h-4 text-gray-400" />
          </button>
          <button className="p-2 rounded-lg bg-industrial-border hover:bg-industrial-accent/20 transition-colors">
            <Download className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </div>

      {/* KPIs */}
      <CascadeKPIs kpis={cascade.kpis} />

      {/* Contrôles de lecture */}
      <div className="flex items-center justify-between p-3 bg-industrial-card border border-industrial-border rounded-xl">
        <div className="flex items-center gap-2">
          <button
            onClick={handlePlayPause}
            className={`p-2 rounded-lg ${isPlaying ? 'bg-red-500/20 text-red-400' : 'bg-cyan-500/20 text-cyan-400'}`}
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          <button
            onClick={handleNext}
            className="p-2 rounded-lg bg-industrial-border hover:bg-industrial-accent/20 text-gray-400"
          >
            <SkipForward className="w-4 h-4" />
          </button>
          <span className="text-sm text-gray-400 ml-2">
            Événement {currentEventIndex + 1} / {cascade.timeline.length}
          </span>
        </div>

        {/* Filtres */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-industrial-border border-none text-sm text-gray-300 focus:outline-none"
          >
            <option value="all">Tous les types</option>
            {Object.entries(eventTypeConfig).map(([key, config]) => (
              <option key={key} value={key}>{config.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Contenu principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline des événements */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="font-medium text-white flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            Timeline de Propagation
          </h3>

          <div className="space-y-0">
            {filteredTimeline.map((event, idx) => (
              <CascadeEventCard
                key={event.id}
                event={event}
                isExpanded={expandedEvent === event.id}
                onToggle={() => setExpandedEvent(expandedEvent === event.id ? null : event.id)}
                showConnector={idx < filteredTimeline.length - 1}
              />
            ))}
          </div>
        </div>

        {/* Panneau latéral */}
        <div className="space-y-4">
          <PropagationGraph cascade={cascade} />
          <AffectedSystemsSummary systems={cascade.affectedSystems} />
        </div>
      </div>
    </div>
  )
}

// Version compacte pour intégration
export function CascadeAnalysisCompact({ cascade = defaultCascadeData, onExpand }) {
  const status = {
    active: { color: 'red', label: 'En cours' },
    contained: { color: 'yellow', label: 'Contenu' },
    resolved: { color: 'green', label: 'Résolu' }
  }[cascade.status]

  return (
    <motion.div
      className="p-4 rounded-xl bg-industrial-card border border-industrial-border cursor-pointer hover:border-red-500/30 transition-all"
      whileHover={{ scale: 1.01 }}
      onClick={onExpand}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className={`w-5 h-5 text-${status.color}-400`} />
          <span className="font-medium text-white">{cascade.title}</span>
        </div>
        <span className={`px-2 py-0.5 rounded text-xs bg-${status.color}-500/20 text-${status.color}-400`}>
          {status.label}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2 text-center">
        <div>
          <div className="text-lg font-bold text-red-400">{cascade.kpis.totalDowntime}min</div>
          <div className="text-xs text-gray-400">Downtime</div>
        </div>
        <div>
          <div className="text-lg font-bold text-orange-400">-{cascade.kpis.productionLoss}</div>
          <div className="text-xs text-gray-400">Unités</div>
        </div>
        <div>
          <div className="text-lg font-bold text-purple-400">{(cascade.kpis.financialImpact / 1000).toFixed(1)}K€</div>
          <div className="text-xs text-gray-400">Impact</div>
        </div>
      </div>

      {/* Mini timeline */}
      <div className="mt-3 flex gap-1">
        {cascade.timeline.slice(0, 8).map(event => {
          const config = eventTypeConfig[event.type]
          return (
            <div
              key={event.id}
              className={`flex-1 h-1.5 rounded-full bg-${config.color}-500/50`}
              title={event.system}
            />
          )
        })}
        {cascade.timeline.length > 8 && (
          <span className="text-xs text-gray-500">+{cascade.timeline.length - 8}</span>
        )}
      </div>
    </motion.div>
  )
}

export default CascadeAnalysisView
