import React, { useState, useMemo, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Server,
  Database,
  Cpu,
  Factory,
  Network,
  Layers,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ArrowRight,
  ArrowDown,
  Zap,
  Shield,
  Activity,
  GitBranch,
  Link2,
  Target,
  TrendingDown,
  Clock,
  BarChart3,
  Eye,
  Maximize2,
  Minimize2,
  Filter,
  RefreshCw
} from 'lucide-react'

// Types de nœuds dans le graphe
const NODE_TYPES = {
  IT_INFRASTRUCTURE: 'it_infrastructure',
  IT_APPLICATION: 'it_application',
  IT_DATABASE: 'it_database',
  OT_SCADA: 'ot_scada',
  OT_MES: 'ot_mes',
  OT_PLM: 'ot_plm',
  OT_OPCUA: 'ot_opcua',
  OT_EQUIPMENT: 'ot_equipment',
  OT_PRODUCTION_LINE: 'ot_production_line',
  BUSINESS_PROCESS: 'business_process'
}

// Configuration des types de nœuds
const nodeTypeConfig = {
  [NODE_TYPES.IT_INFRASTRUCTURE]: {
    icon: Server,
    color: 'blue',
    label: 'Infrastructure IT',
    zone: 'it'
  },
  [NODE_TYPES.IT_APPLICATION]: {
    icon: Activity,
    color: 'cyan',
    label: 'Application',
    zone: 'it'
  },
  [NODE_TYPES.IT_DATABASE]: {
    icon: Database,
    color: 'purple',
    label: 'Base de données',
    zone: 'it'
  },
  [NODE_TYPES.OT_SCADA]: {
    icon: Cpu,
    color: 'emerald',
    label: 'SCADA',
    zone: 'ot'
  },
  [NODE_TYPES.OT_MES]: {
    icon: Factory,
    color: 'amber',
    label: 'MES',
    zone: 'ot'
  },
  [NODE_TYPES.OT_PLM]: {
    icon: Layers,
    color: 'pink',
    label: 'PLM',
    zone: 'ot'
  },
  [NODE_TYPES.OT_OPCUA]: {
    icon: Network,
    color: 'green',
    label: 'OPC-UA',
    zone: 'ot'
  },
  [NODE_TYPES.OT_EQUIPMENT]: {
    icon: Zap,
    color: 'orange',
    label: 'Équipement',
    zone: 'ot'
  },
  [NODE_TYPES.OT_PRODUCTION_LINE]: {
    icon: GitBranch,
    color: 'teal',
    label: 'Ligne de production',
    zone: 'ot'
  },
  [NODE_TYPES.BUSINESS_PROCESS]: {
    icon: Target,
    color: 'rose',
    label: 'Processus métier',
    zone: 'business'
  }
}

// Données par défaut du graphe IT/OT
const defaultGraphData = {
  nodes: [
    // Zone IT
    { id: 'it-k8s', type: NODE_TYPES.IT_INFRASTRUCTURE, name: 'Kubernetes Cluster', status: 'healthy', metrics: { cpu: 45, memory: 62 }, layer: 0 },
    { id: 'it-kafka', type: NODE_TYPES.IT_INFRASTRUCTURE, name: 'Kafka Cluster', status: 'healthy', metrics: { throughput: '15K/s', lag: 120 }, layer: 0 },
    { id: 'it-api', type: NODE_TYPES.IT_APPLICATION, name: 'API Gateway', status: 'healthy', metrics: { latency: '45ms', rps: 2500 }, layer: 1 },
    { id: 'it-collector', type: NODE_TYPES.IT_APPLICATION, name: 'OTEL Collector', status: 'warning', metrics: { metricsRate: '12K/s', dropped: 15 }, layer: 1 },
    { id: 'it-victoria', type: NODE_TYPES.IT_DATABASE, name: 'VictoriaMetrics', status: 'healthy', metrics: { series: '2.5M', queryLatency: '12ms' }, layer: 2 },
    { id: 'it-opensearch', type: NODE_TYPES.IT_DATABASE, name: 'OpenSearch', status: 'healthy', metrics: { docs: '45M', health: 'green' }, layer: 2 },

    // Zone OT
    { id: 'ot-scada', type: NODE_TYPES.OT_SCADA, name: 'SCADA Central', status: 'healthy', metrics: { devices: 124, alarms: 2 }, layer: 0 },
    { id: 'ot-mes', type: NODE_TYPES.OT_MES, name: 'MES Production', status: 'warning', metrics: { orders: 45, efficiency: '87%' }, layer: 0 },
    { id: 'ot-plm', type: NODE_TYPES.OT_PLM, name: 'PLM Engineering', status: 'healthy', metrics: { products: 234, revisions: 12 }, layer: 0 },
    { id: 'ot-opcua', type: NODE_TYPES.OT_OPCUA, name: 'OPC-UA Gateway', status: 'healthy', metrics: { servers: 8, tags: 5600 }, layer: 1 },

    // Équipements
    { id: 'eq-cnc-01', type: NODE_TYPES.OT_EQUIPMENT, name: 'CNC Machine 01', status: 'healthy', metrics: { oee: '92%', cycles: 1245 }, layer: 2 },
    { id: 'eq-cnc-02', type: NODE_TYPES.OT_EQUIPMENT, name: 'CNC Machine 02', status: 'error', metrics: { oee: '0%', downtime: '2h15' }, layer: 2 },
    { id: 'eq-robot-01', type: NODE_TYPES.OT_EQUIPMENT, name: 'Robot Soudure', status: 'warning', metrics: { oee: '78%', temp: '68°C' }, layer: 2 },
    { id: 'eq-conv-01', type: NODE_TYPES.OT_EQUIPMENT, name: 'Convoyeur A', status: 'healthy', metrics: { speed: '2.5m/s', items: 4520 }, layer: 2 },

    // Lignes de production
    { id: 'line-a', type: NODE_TYPES.OT_PRODUCTION_LINE, name: 'Ligne A - Assemblage', status: 'healthy', metrics: { oee: '89%', output: 1240 }, layer: 3 },
    { id: 'line-b', type: NODE_TYPES.OT_PRODUCTION_LINE, name: 'Ligne B - Usinage', status: 'error', metrics: { oee: '45%', output: 320 }, layer: 3 },
    { id: 'line-c', type: NODE_TYPES.OT_PRODUCTION_LINE, name: 'Ligne C - Finition', status: 'warning', metrics: { oee: '72%', output: 890 }, layer: 3 },

    // Processus métier
    { id: 'bp-production', type: NODE_TYPES.BUSINESS_PROCESS, name: 'Production Journalière', status: 'warning', metrics: { target: '3000', actual: '2450' }, layer: 4 },
    { id: 'bp-quality', type: NODE_TYPES.BUSINESS_PROCESS, name: 'Contrôle Qualité', status: 'healthy', metrics: { rate: '99.2%', defects: 8 }, layer: 4 },
    { id: 'bp-delivery', type: NODE_TYPES.BUSINESS_PROCESS, name: 'Expédition Client', status: 'healthy', metrics: { onTime: '96%', delayed: 4 }, layer: 4 }
  ],
  edges: [
    // IT vers OT
    { from: 'it-kafka', to: 'ot-scada', type: 'data', label: 'Events Stream' },
    { from: 'it-kafka', to: 'ot-mes', type: 'data', label: 'Orders Stream' },
    { from: 'it-api', to: 'ot-plm', type: 'api', label: 'REST API' },
    { from: 'it-collector', to: 'it-victoria', type: 'metrics', label: 'Metrics' },
    { from: 'it-collector', to: 'it-opensearch', type: 'logs', label: 'Logs/Traces' },

    // OT interne
    { from: 'ot-scada', to: 'ot-opcua', type: 'control', label: 'Control' },
    { from: 'ot-opcua', to: 'eq-cnc-01', type: 'control', label: 'PLC' },
    { from: 'ot-opcua', to: 'eq-cnc-02', type: 'control', label: 'PLC' },
    { from: 'ot-opcua', to: 'eq-robot-01', type: 'control', label: 'PLC' },
    { from: 'ot-opcua', to: 'eq-conv-01', type: 'control', label: 'PLC' },
    { from: 'ot-mes', to: 'eq-cnc-01', type: 'order', label: 'Work Order' },
    { from: 'ot-mes', to: 'eq-cnc-02', type: 'order', label: 'Work Order' },

    // Équipements vers lignes
    { from: 'eq-cnc-01', to: 'line-a', type: 'production', label: 'Output' },
    { from: 'eq-cnc-02', to: 'line-b', type: 'production', label: 'Output', impacted: true },
    { from: 'eq-robot-01', to: 'line-b', type: 'production', label: 'Output', impacted: true },
    { from: 'eq-conv-01', to: 'line-c', type: 'production', label: 'Output' },

    // Lignes vers processus métier
    { from: 'line-a', to: 'bp-production', type: 'business', label: 'Units' },
    { from: 'line-b', to: 'bp-production', type: 'business', label: 'Units', impacted: true },
    { from: 'line-c', to: 'bp-production', type: 'business', label: 'Units' },
    { from: 'bp-production', to: 'bp-quality', type: 'business', label: 'QC' },
    { from: 'bp-quality', to: 'bp-delivery', type: 'business', label: 'Approved' },

    // OT vers IT (telemetrie)
    { from: 'ot-scada', to: 'it-collector', type: 'telemetry', label: 'OTLP' },
    { from: 'ot-mes', to: 'it-collector', type: 'telemetry', label: 'OTLP' },
    { from: 'ot-opcua', to: 'it-collector', type: 'telemetry', label: 'OTLP' }
  ],
  impacts: [
    {
      id: 'imp-1',
      source: 'eq-cnc-02',
      title: 'Panne CNC Machine 02',
      severity: 'critical',
      propagation: ['eq-cnc-02', 'line-b', 'bp-production'],
      lostProduction: 180,
      estimatedCost: 15600,
      duration: '2h 15min',
      rootCause: 'Défaillance servomoteur axe Y'
    },
    {
      id: 'imp-2',
      source: 'eq-robot-01',
      title: 'Surchauffe Robot Soudure',
      severity: 'warning',
      propagation: ['eq-robot-01', 'line-b'],
      lostProduction: 45,
      estimatedCost: 3800,
      duration: '45min',
      rootCause: 'Température ambiante élevée'
    }
  ]
}

// Composant pour un nœud du graphe
function GraphNode({ node, isSelected, isInImpactPath, onClick, position }) {
  const config = nodeTypeConfig[node.type]
  const Icon = config.icon

  const statusColors = {
    healthy: 'border-green-500/50 bg-green-500/10',
    warning: 'border-yellow-500/50 bg-yellow-500/10',
    error: 'border-red-500/50 bg-red-500/10',
    unknown: 'border-gray-500/50 bg-gray-500/10'
  }

  const statusDotColors = {
    healthy: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
    unknown: 'bg-gray-500'
  }

  return (
    <motion.div
      className={`absolute cursor-pointer transition-all duration-300 ${
        isSelected ? 'z-20' : 'z-10'
      }`}
      style={{ left: position.x, top: position.y }}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{
        opacity: 1,
        scale: isSelected ? 1.1 : 1,
        boxShadow: isInImpactPath ? '0 0 20px rgba(239, 68, 68, 0.5)' : 'none'
      }}
      whileHover={{ scale: 1.05 }}
      onClick={() => onClick(node)}
    >
      <div className={`p-3 rounded-xl border-2 backdrop-blur-sm ${statusColors[node.status]} ${
        isInImpactPath ? 'ring-2 ring-red-500 ring-offset-2 ring-offset-industrial-bg' : ''
      } ${isSelected ? 'ring-2 ring-cyan-500 ring-offset-2 ring-offset-industrial-bg' : ''}`}>
        <div className="flex items-center gap-2 mb-2">
          <div className={`w-8 h-8 rounded-lg bg-${config.color}-500/20 flex items-center justify-center`}>
            <Icon className={`w-4 h-4 text-${config.color}-400`} />
          </div>
          <span className={`w-2 h-2 rounded-full ${statusDotColors[node.status]} ${
            node.status === 'error' ? 'animate-pulse' : ''
          }`} />
        </div>
        <h4 className="text-xs font-medium text-white truncate max-w-[120px]">{node.name}</h4>
        <span className={`text-[10px] text-${config.color}-400`}>{config.label}</span>

        {/* Métriques clés */}
        <div className="mt-2 space-y-0.5">
          {Object.entries(node.metrics).slice(0, 2).map(([key, value]) => (
            <div key={key} className="flex justify-between text-[10px]">
              <span className="text-gray-500 capitalize">{key}</span>
              <span className="text-gray-300">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}

// Composant pour afficher les détails de l'impact
function ImpactDetailPanel({ impact, nodes, onClose }) {
  if (!impact) return null

  const affectedNodes = impact.propagation.map(id => nodes.find(n => n.id === id)).filter(Boolean)

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="absolute right-4 top-4 w-80 bg-industrial-card border-2 border-red-500/30 rounded-xl p-4 z-30"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <AlertTriangle className={`w-5 h-5 ${
            impact.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'
          }`} />
          <h3 className="font-semibold text-white">{impact.title}</h3>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white"
        >
          <XCircle className="w-5 h-5" />
        </button>
      </div>

      {/* Chaîne de propagation */}
      <div className="mb-4">
        <span className="text-xs text-gray-400 block mb-2">Chaîne de propagation</span>
        <div className="flex flex-wrap items-center gap-1">
          {affectedNodes.map((node, idx) => (
            <React.Fragment key={node.id}>
              <span className={`px-2 py-0.5 rounded text-xs ${
                idx === 0 ? 'bg-red-500/20 text-red-400' : 'bg-orange-500/20 text-orange-400'
              }`}>
                {node.name}
              </span>
              {idx < affectedNodes.length - 1 && (
                <ArrowRight className="w-3 h-3 text-gray-500" />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Métriques d'impact */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/20">
          <span className="text-xs text-gray-400">Production perdue</span>
          <div className="text-lg font-bold text-red-400">{impact.lostProduction} unités</div>
        </div>
        <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/20">
          <span className="text-xs text-gray-400">Coût estimé</span>
          <div className="text-lg font-bold text-red-400">{impact.estimatedCost.toLocaleString()}€</div>
        </div>
      </div>

      {/* Détails */}
      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-gray-400" />
          <span className="text-gray-400">Durée:</span>
          <span className="text-white">{impact.duration}</span>
        </div>
        <div className="flex items-start gap-2">
          <Target className="w-4 h-4 text-gray-400 mt-0.5" />
          <span className="text-gray-400">Cause:</span>
          <span className="text-white">{impact.rootCause}</span>
        </div>
      </div>
    </motion.div>
  )
}

// Composant pour la légende des zones
function GraphLegend() {
  return (
    <div className="absolute left-4 bottom-4 p-3 bg-industrial-card/90 backdrop-blur-sm border border-industrial-border rounded-xl z-20">
      <h4 className="text-xs font-medium text-gray-400 mb-2">Légende</h4>
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-blue-500/50" />
          <span className="text-xs text-gray-300">Zone IT</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-emerald-500/50" />
          <span className="text-xs text-gray-300">Zone OT</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-rose-500/50" />
          <span className="text-xs text-gray-300">Processus Métier</span>
        </div>
        <div className="h-px bg-industrial-border my-2" />
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-xs text-gray-300">Healthy</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <span className="text-xs text-gray-300">Warning</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <span className="text-xs text-gray-300">Error</span>
        </div>
      </div>
    </div>
  )
}

// Composant liste des impacts actifs
function ActiveImpactsList({ impacts, selectedImpact, onSelectImpact }) {
  return (
    <div className="space-y-2">
      {impacts.map(impact => (
        <motion.button
          key={impact.id}
          className={`w-full p-3 rounded-lg border text-left transition-all ${
            selectedImpact?.id === impact.id
              ? 'bg-red-500/20 border-red-500/50'
              : 'bg-industrial-card border-industrial-border hover:border-red-500/30'
          }`}
          onClick={() => onSelectImpact(impact)}
          whileHover={{ x: 4 }}
        >
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className={`w-4 h-4 ${
              impact.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'
            }`} />
            <span className="text-sm font-medium text-white">{impact.title}</span>
          </div>
          <div className="flex items-center gap-4 text-xs text-gray-400">
            <span>-{impact.lostProduction} unités</span>
            <span>{impact.estimatedCost.toLocaleString()}€</span>
            <span>{impact.propagation.length} systèmes</span>
          </div>
        </motion.button>
      ))}
    </div>
  )
}

// Statistiques du graphe
function GraphStats({ nodes, edges, impacts }) {
  const stats = useMemo(() => {
    const itNodes = nodes.filter(n => nodeTypeConfig[n.type]?.zone === 'it')
    const otNodes = nodes.filter(n => nodeTypeConfig[n.type]?.zone === 'ot')
    const healthyNodes = nodes.filter(n => n.status === 'healthy')
    const criticalImpacts = impacts.filter(i => i.severity === 'critical')

    return {
      totalNodes: nodes.length,
      itNodes: itNodes.length,
      otNodes: otNodes.length,
      connections: edges.length,
      healthRate: Math.round((healthyNodes.length / nodes.length) * 100),
      activeImpacts: impacts.length,
      criticalImpacts: criticalImpacts.length,
      totalLoss: impacts.reduce((sum, i) => sum + i.estimatedCost, 0)
    }
  }, [nodes, edges, impacts])

  return (
    <div className="grid grid-cols-4 gap-3">
      <div className="p-3 rounded-lg bg-industrial-card border border-industrial-border">
        <div className="flex items-center gap-2 mb-1">
          <Server className="w-4 h-4 text-blue-400" />
          <span className="text-xs text-gray-400">Nœuds IT</span>
        </div>
        <div className="text-xl font-bold text-white">{stats.itNodes}</div>
      </div>
      <div className="p-3 rounded-lg bg-industrial-card border border-industrial-border">
        <div className="flex items-center gap-2 mb-1">
          <Factory className="w-4 h-4 text-emerald-400" />
          <span className="text-xs text-gray-400">Nœuds OT</span>
        </div>
        <div className="text-xl font-bold text-white">{stats.otNodes}</div>
      </div>
      <div className="p-3 rounded-lg bg-industrial-card border border-industrial-border">
        <div className="flex items-center gap-2 mb-1">
          <Link2 className="w-4 h-4 text-cyan-400" />
          <span className="text-xs text-gray-400">Connexions</span>
        </div>
        <div className="text-xl font-bold text-white">{stats.connections}</div>
      </div>
      <div className="p-3 rounded-lg bg-industrial-card border border-industrial-border">
        <div className="flex items-center gap-2 mb-1">
          <CheckCircle className="w-4 h-4 text-green-400" />
          <span className="text-xs text-gray-400">Santé globale</span>
        </div>
        <div className={`text-xl font-bold ${
          stats.healthRate >= 80 ? 'text-green-400' :
          stats.healthRate >= 60 ? 'text-yellow-400' : 'text-red-400'
        }`}>{stats.healthRate}%</div>
      </div>
    </div>
  )
}

// Composant principal du graphe IT/OT
export function ITOTImpactGraph({ data = defaultGraphData, className = '' }) {
  const [selectedNode, setSelectedNode] = useState(null)
  const [selectedImpact, setSelectedImpact] = useState(null)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [viewFilter, setViewFilter] = useState('all') // 'all', 'it', 'ot', 'impacts'

  // Calculer les positions des nœuds (layout en couches)
  const nodePositions = useMemo(() => {
    const positions = {}
    const layerWidth = 850
    const layerSpacing = 140
    const startX = 50
    const startY = 30

    // Grouper les nœuds par couche
    const layers = {}
    data.nodes.forEach(node => {
      const layer = node.layer || 0
      if (!layers[layer]) layers[layer] = []
      layers[layer].push(node)
    })

    // Calculer les positions
    Object.entries(layers).forEach(([layer, nodes]) => {
      const nodeSpacing = layerWidth / (nodes.length + 1)
      nodes.forEach((node, idx) => {
        positions[node.id] = {
          x: startX + nodeSpacing * (idx + 1) - 70,
          y: startY + parseInt(layer) * layerSpacing
        }
      })
    })

    return positions
  }, [data.nodes])

  // Filtrer les nœuds selon le filtre actif
  const filteredNodes = useMemo(() => {
    if (viewFilter === 'all') return data.nodes
    if (viewFilter === 'it') return data.nodes.filter(n => nodeTypeConfig[n.type]?.zone === 'it')
    if (viewFilter === 'ot') return data.nodes.filter(n => nodeTypeConfig[n.type]?.zone === 'ot')
    if (viewFilter === 'impacts') {
      const impactedIds = new Set(data.impacts.flatMap(i => i.propagation))
      return data.nodes.filter(n => impactedIds.has(n.id))
    }
    return data.nodes
  }, [data.nodes, data.impacts, viewFilter])

  // Nœuds dans le chemin d'impact sélectionné
  const impactPathNodes = useMemo(() => {
    if (!selectedImpact) return new Set()
    return new Set(selectedImpact.propagation)
  }, [selectedImpact])

  const handleNodeClick = useCallback((node) => {
    setSelectedNode(selectedNode?.id === node.id ? null : node)
  }, [selectedNode])

  const handleImpactSelect = useCallback((impact) => {
    setSelectedImpact(selectedImpact?.id === impact.id ? null : impact)
    setSelectedNode(null)
  }, [selectedImpact])

  return (
    <div className={`bg-industrial-card border border-industrial-border rounded-xl overflow-hidden ${className} ${
      isFullscreen ? 'fixed inset-4 z-50' : ''
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-industrial-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
            <GitBranch className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-white">Graphe d'Impact IT/OT</h3>
            <p className="text-xs text-gray-400">Visualisation des dépendances et propagation d'impact</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Filtres */}
          <div className="flex items-center gap-1 p-1 bg-industrial-border rounded-lg">
            {[
              { id: 'all', label: 'Tout' },
              { id: 'it', label: 'IT' },
              { id: 'ot', label: 'OT' },
              { id: 'impacts', label: 'Impacts' }
            ].map(filter => (
              <button
                key={filter.id}
                className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                  viewFilter === filter.id
                    ? 'bg-cyan-500/20 text-cyan-400'
                    : 'text-gray-400 hover:text-white'
                }`}
                onClick={() => setViewFilter(filter.id)}
              >
                {filter.label}
              </button>
            ))}
          </div>

          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-2 rounded-lg bg-industrial-border hover:bg-industrial-accent/20 transition-colors"
          >
            {isFullscreen ? (
              <Minimize2 className="w-4 h-4 text-gray-400" />
            ) : (
              <Maximize2 className="w-4 h-4 text-gray-400" />
            )}
          </button>
        </div>
      </div>

      {/* Statistiques */}
      <div className="p-4 border-b border-industrial-border">
        <GraphStats nodes={data.nodes} edges={data.edges} impacts={data.impacts} />
      </div>

      {/* Zone du graphe et panneau latéral */}
      <div className="flex">
        {/* Graphe principal */}
        <div className="flex-1 relative h-[600px] overflow-hidden bg-gradient-to-br from-industrial-bg via-industrial-card to-industrial-bg">
          {/* Grille de fond */}
          <svg className="absolute inset-0 w-full h-full">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />

            {/* Lignes de connexion */}
            {data.edges.map((edge, idx) => {
              const fromPos = nodePositions[edge.from]
              const toPos = nodePositions[edge.to]
              if (!fromPos || !toPos) return null

              const isImpacted = edge.impacted || (selectedImpact &&
                selectedImpact.propagation.includes(edge.from) &&
                selectedImpact.propagation.includes(edge.to))

              return (
                <g key={idx}>
                  <line
                    x1={fromPos.x + 70}
                    y1={fromPos.y + 50}
                    x2={toPos.x + 70}
                    y2={toPos.y + 10}
                    stroke={isImpacted ? 'rgba(239, 68, 68, 0.6)' : 'rgba(6, 182, 212, 0.2)'}
                    strokeWidth={isImpacted ? 3 : 1}
                    strokeDasharray={isImpacted ? '' : '4,4'}
                  />
                  {isImpacted && (
                    <circle r="4" fill="#ef4444">
                      <animateMotion
                        dur="1s"
                        repeatCount="indefinite"
                        path={`M${fromPos.x + 70},${fromPos.y + 50} L${toPos.x + 70},${toPos.y + 10}`}
                      />
                    </circle>
                  )}
                </g>
              )
            })}
          </svg>

          {/* Zones IT/OT */}
          <div className="absolute left-2 top-2 px-2 py-1 bg-blue-500/20 border border-blue-500/30 rounded text-xs text-blue-400">
            Zone IT
          </div>
          <div className="absolute left-2 top-[180px] px-2 py-1 bg-emerald-500/20 border border-emerald-500/30 rounded text-xs text-emerald-400">
            Zone OT
          </div>
          <div className="absolute left-2 top-[460px] px-2 py-1 bg-rose-500/20 border border-rose-500/30 rounded text-xs text-rose-400">
            Processus Métier
          </div>

          {/* Nœuds du graphe */}
          {filteredNodes.map(node => (
            <GraphNode
              key={node.id}
              node={node}
              position={nodePositions[node.id]}
              isSelected={selectedNode?.id === node.id}
              isInImpactPath={impactPathNodes.has(node.id)}
              onClick={handleNodeClick}
            />
          ))}

          {/* Légende */}
          <GraphLegend />

          {/* Panneau de détail d'impact */}
          <AnimatePresence>
            {selectedImpact && (
              <ImpactDetailPanel
                impact={selectedImpact}
                nodes={data.nodes}
                onClose={() => setSelectedImpact(null)}
              />
            )}
          </AnimatePresence>
        </div>

        {/* Panneau latéral - Impacts actifs */}
        <div className="w-72 border-l border-industrial-border p-4 bg-industrial-card/50">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-medium text-white flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              Impacts Actifs
            </h4>
            <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400 text-xs">
              {data.impacts.length}
            </span>
          </div>

          <ActiveImpactsList
            impacts={data.impacts}
            selectedImpact={selectedImpact}
            onSelectImpact={handleImpactSelect}
          />

          {/* Résumé des pertes */}
          <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown className="w-4 h-4 text-red-400" />
              <span className="text-xs text-gray-400">Impact total</span>
            </div>
            <div className="text-xl font-bold text-red-400">
              {data.impacts.reduce((sum, i) => sum + i.estimatedCost, 0).toLocaleString()}€
            </div>
            <div className="text-xs text-gray-400 mt-1">
              {data.impacts.reduce((sum, i) => sum + i.lostProduction, 0)} unités perdues
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Export du composant compact pour intégration dans d'autres vues
export function ITOTImpactGraphCompact({ data = defaultGraphData, onExpand }) {
  const criticalImpacts = data.impacts.filter(i => i.severity === 'critical')
  const totalCost = data.impacts.reduce((sum, i) => sum + i.estimatedCost, 0)

  return (
    <motion.div
      className="p-4 rounded-xl bg-industrial-card border border-industrial-border cursor-pointer hover:border-cyan-500/30 transition-all"
      whileHover={{ scale: 1.01 }}
      onClick={onExpand}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <GitBranch className="w-5 h-5 text-cyan-400" />
          <span className="font-medium text-white">Chaîne d'Impact IT/OT</span>
        </div>
        <Maximize2 className="w-4 h-4 text-gray-400" />
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="text-center">
          <div className="text-2xl font-bold text-white">{data.nodes.length}</div>
          <div className="text-xs text-gray-400">Systèmes</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-400">{criticalImpacts.length}</div>
          <div className="text-xs text-gray-400">Critiques</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-400">{(totalCost / 1000).toFixed(0)}K€</div>
          <div className="text-xs text-gray-400">Impact</div>
        </div>
      </div>
    </motion.div>
  )
}

export default ITOTImpactGraph
