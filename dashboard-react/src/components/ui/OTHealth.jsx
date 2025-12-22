import React, { useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  Factory,
  Cpu,
  Database,
  Network,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Activity,
  Layers,
  GitBranch,
  ArrowRight,
  Zap,
  Settings,
  BarChart3,
  Target
} from 'lucide-react'
import { StatusBadge, StatusDot } from './Status'
import { RadialGauge, LinearGauge } from './Gauge'

// Configuration des systèmes OT
const OT_SYSTEMS = {
  scada: {
    name: 'SCADA',
    fullName: 'Supervisory Control and Data Acquisition',
    icon: Cpu,
    color: 'cyan'
  },
  mes: {
    name: 'MES',
    fullName: 'Manufacturing Execution System',
    icon: Factory,
    color: 'purple'
  },
  plm: {
    name: 'PLM',
    fullName: 'Product Lifecycle Management',
    icon: Layers,
    color: 'amber'
  },
  opcua: {
    name: 'OPC-UA',
    fullName: 'OPC Unified Architecture',
    icon: Network,
    color: 'green'
  }
}

// Carte d'état d'un système OT
export function OTSystemCard({ system, data, onClick }) {
  const config = OT_SYSTEMS[system]
  if (!config) return null

  const Icon = config.icon
  const isHealthy = ['healthy', 'ok', 'running', 'active'].includes(data?.status?.toLowerCase())
  const isWarning = ['degraded', 'warning'].includes(data?.status?.toLowerCase())

  return (
    <motion.div
      className={`p-4 rounded-xl border-2 cursor-pointer transition-all
        ${isHealthy ? 'bg-green-500/5 border-green-500/30 hover:border-green-500/50' :
          isWarning ? 'bg-yellow-500/5 border-yellow-500/30 hover:border-yellow-500/50' :
          data?.status === 'unknown' ? 'bg-gray-500/5 border-gray-500/30 hover:border-gray-500/50' :
          'bg-red-500/5 border-red-500/30 hover:border-red-500/50'
        }`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-3">
        <div className={`w-10 h-10 rounded-lg bg-${config.color}-500/20 flex items-center justify-center`}>
          <Icon className={`w-5 h-5 text-${config.color}-400`} />
        </div>
        <StatusDot status={data?.status || 'unknown'} size="md" />
      </div>

      <h4 className="font-semibold text-white mb-1">{config.name}</h4>
      <p className="text-xs text-gray-500 mb-3">{config.fullName}</p>

      {system === 'scada' && data && (
        <div className="space-y-1 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-400">Devices</span>
            <span className="text-white">{data.connectedDevices}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Data pts/s</span>
            <span className="text-white">{data.dataPointsPerSec}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Alarmes</span>
            <span className={data.activeAlarms > 0 ? 'text-red-400' : 'text-green-400'}>
              {data.activeAlarms}
            </span>
          </div>
        </div>
      )}

      {system === 'mes' && data && (
        <div className="space-y-1 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-400">Ordres actifs</span>
            <span className="text-white">{data.activeOrders}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Complétés</span>
            <span className="text-green-400">{data.completedToday}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Efficacité</span>
            <span className="text-white">{data.efficiency}%</span>
          </div>
        </div>
      )}

      {system === 'plm' && data && (
        <div className="space-y-1 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-400">Produits actifs</span>
            <span className="text-white">{data.activeProducts}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Révisions</span>
            <span className="text-yellow-400">{data.revisionsPending}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Qualité holds</span>
            <span className={data.qualityHolds > 0 ? 'text-red-400' : 'text-green-400'}>
              {data.qualityHolds}
            </span>
          </div>
        </div>
      )}

      {system === 'opcua' && data && (
        <div className="space-y-1 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-400">Serveurs</span>
            <span className="text-white">{data.connectedServers}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Tags</span>
            <span className="text-white">{data.tagsMonitored}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Latence</span>
            <span className={data.latencyMs > 100 ? 'text-yellow-400' : 'text-green-400'}>
              {data.latencyMs}ms
            </span>
          </div>
        </div>
      )}
    </motion.div>
  )
}

// Indicateur de santé globale OT
export function OTHealthIndicator({ otData }) {
  const systems = ['scada', 'mes', 'plm', 'opcua']
  const healthyCount = systems.filter(s =>
    ['healthy', 'ok', 'running', 'active'].includes(otData?.[s]?.status?.toLowerCase())
  ).length
  const healthPercent = (healthyCount / systems.length) * 100

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Factory className="w-5 h-5 text-cyan-400" />
          <span className="font-medium text-white">Santé Zone OT</span>
        </div>
        <span className={`text-2xl font-bold ${
          healthPercent >= 75 ? 'text-green-400' :
          healthPercent >= 50 ? 'text-yellow-400' : 'text-red-400'
        }`}>
          {Math.round(healthPercent)}%
        </span>
      </div>

      <div className="h-3 bg-industrial-border rounded-full overflow-hidden">
        <motion.div
          className={`h-full ${
            healthPercent >= 75 ? 'bg-gradient-to-r from-green-500 to-emerald-400' :
            healthPercent >= 50 ? 'bg-gradient-to-r from-yellow-500 to-amber-400' :
            'bg-gradient-to-r from-red-500 to-rose-400'
          }`}
          initial={{ width: 0 }}
          animate={{ width: `${healthPercent}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>

      <div className="grid grid-cols-4 gap-2">
        {systems.map(system => {
          const config = OT_SYSTEMS[system]
          const status = otData?.[system]?.status || 'unknown'
          const isHealthy = ['healthy', 'ok', 'running', 'active'].includes(status.toLowerCase())

          return (
            <div key={system} className="text-center">
              <div className={`w-8 h-8 mx-auto rounded-lg flex items-center justify-center
                ${isHealthy ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                <config.icon className={`w-4 h-4 ${isHealthy ? 'text-green-400' : 'text-red-400'}`} />
              </div>
              <span className="text-xs text-gray-400 mt-1">{config.name}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// Métriques industrielles avancées (MTBF, MTTR, TRS)
export function IndustrialMetrics({ mtbf, mttr, trs }) {
  return (
    <div className="space-y-4">
      <h4 className="font-medium text-white flex items-center gap-2">
        <BarChart3 className="w-4 h-4 text-cyan-400" />
        Métriques Industrielles
      </h4>

      <div className="grid grid-cols-2 gap-4">
        {/* MTBF */}
        <div className="p-3 rounded-lg bg-industrial-card border border-industrial-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">MTBF</span>
            <Clock className="w-4 h-4 text-green-400" />
          </div>
          <div className="text-xl font-bold text-white">{mtbf || 0}h</div>
          <p className="text-xs text-gray-500">Temps moyen entre pannes</p>
        </div>

        {/* MTTR */}
        <div className="p-3 rounded-lg bg-industrial-card border border-industrial-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">MTTR</span>
            <Settings className="w-4 h-4 text-yellow-400" />
          </div>
          <div className="text-xl font-bold text-white">{mttr || 0}h</div>
          <p className="text-xs text-gray-500">Temps moyen de réparation</p>
        </div>
      </div>

      {/* TRS Détaillé */}
      <div className="p-4 rounded-lg bg-industrial-card border border-industrial-border">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-white">TRS Détaillé</span>
          <span className={`text-lg font-bold ${
            (trs?.global || 0) >= 85 ? 'text-green-400' :
            (trs?.global || 0) >= 70 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {trs?.global || 0}%
          </span>
        </div>

        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-gray-400">Disponibilité</span>
              <span className="text-white">{trs?.disponibilite || 0}%</span>
            </div>
            <LinearGauge value={trs?.disponibilite || 0} color="green" showValue={false} height="h-1.5" />
          </div>
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-gray-400">Performance</span>
              <span className="text-white">{trs?.performance || 0}%</span>
            </div>
            <LinearGauge value={trs?.performance || 0} color="cyan" showValue={false} height="h-1.5" />
          </div>
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-gray-400">Qualité</span>
              <span className="text-white">{trs?.qualite || 0}%</span>
            </div>
            <LinearGauge value={trs?.qualite || 0} color="purple" showValue={false} height="h-1.5" />
          </div>
        </div>
      </div>
    </div>
  )
}

// Vue agrégée par zone de production
export function ProductionZoneView({ zones }) {
  const defaultZones = zones?.length > 0 ? zones : [
    { id: 'zone-a', name: 'Zone A - Assemblage', status: 'running', oee: 87, lines: 3, activeAlarms: 0 },
    { id: 'zone-b', name: 'Zone B - Usinage', status: 'running', oee: 82, lines: 4, activeAlarms: 1 },
    { id: 'zone-c', name: 'Zone C - Finition', status: 'warning', oee: 71, lines: 2, activeAlarms: 2 },
    { id: 'zone-d', name: 'Zone D - Stockage', status: 'running', oee: 95, lines: 1, activeAlarms: 0 }
  ]

  return (
    <div className="space-y-3">
      <h4 className="font-medium text-white flex items-center gap-2">
        <Layers className="w-4 h-4 text-purple-400" />
        Zones de Production
      </h4>

      <div className="space-y-2">
        {defaultZones.map(zone => (
          <motion.div
            key={zone.id}
            className={`p-3 rounded-lg border cursor-pointer transition-all
              ${zone.status === 'running' ? 'bg-green-500/5 border-green-500/20 hover:border-green-500/40' :
                zone.status === 'warning' ? 'bg-yellow-500/5 border-yellow-500/20 hover:border-yellow-500/40' :
                'bg-red-500/5 border-red-500/20 hover:border-red-500/40'
              }`}
            whileHover={{ x: 4 }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <StatusDot status={zone.status} size="sm" />
                <div>
                  <span className="text-sm font-medium text-white">{zone.name}</span>
                  <span className="text-xs text-gray-500 ml-2">({zone.lines} lignes)</span>
                </div>
              </div>
              <div className="flex items-center gap-4">
                {zone.activeAlarms > 0 && (
                  <span className="flex items-center gap-1 text-xs text-red-400">
                    <AlertTriangle className="w-3 h-3" />
                    {zone.activeAlarms}
                  </span>
                )}
                <div className="text-right">
                  <span className={`text-sm font-bold ${
                    zone.oee >= 85 ? 'text-green-400' :
                    zone.oee >= 70 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {zone.oee}%
                  </span>
                  <span className="text-xs text-gray-500 ml-1">OEE</span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

// Chaîne logique-métier (dépendances équipements)
export function DependencyChainView({ chain }) {
  const defaultChain = chain?.length > 0 ? chain : [
    {
      id: 'chain-1',
      name: 'Ligne Principale',
      steps: [
        { id: 's1', name: 'Réception MP', status: 'ok', type: 'input' },
        { id: 's2', name: 'Usinage CNC', status: 'ok', type: 'process' },
        { id: 's3', name: 'Assemblage', status: 'warning', type: 'process' },
        { id: 's4', name: 'Contrôle Qualité', status: 'ok', type: 'check' },
        { id: 's5', name: 'Emballage', status: 'ok', type: 'output' }
      ],
      impactLevel: 'medium'
    },
    {
      id: 'chain-2',
      name: 'Ligne Secondaire',
      steps: [
        { id: 's1', name: 'Stock Composants', status: 'ok', type: 'input' },
        { id: 's2', name: 'Soudure', status: 'error', type: 'process' },
        { id: 's3', name: 'Test Électrique', status: 'blocked', type: 'check' },
        { id: 's4', name: 'Expédition', status: 'blocked', type: 'output' }
      ],
      impactLevel: 'critical'
    }
  ]

  const getStepColor = (status) => {
    switch (status) {
      case 'ok': return 'bg-green-500'
      case 'warning': return 'bg-yellow-500'
      case 'error': return 'bg-red-500'
      case 'blocked': return 'bg-gray-500'
      default: return 'bg-gray-500'
    }
  }

  const getStepBorderColor = (status) => {
    switch (status) {
      case 'ok': return 'border-green-500/50'
      case 'warning': return 'border-yellow-500/50'
      case 'error': return 'border-red-500/50'
      case 'blocked': return 'border-gray-500/50'
      default: return 'border-gray-500/50'
    }
  }

  return (
    <div className="space-y-4">
      <h4 className="font-medium text-white flex items-center gap-2">
        <GitBranch className="w-4 h-4 text-cyan-400" />
        Chaîne Logique-Métier
      </h4>

      <div className="space-y-4">
        {defaultChain.map(chain => (
          <div
            key={chain.id}
            className={`p-4 rounded-lg border ${
              chain.impactLevel === 'critical' ? 'bg-red-500/5 border-red-500/30' :
              chain.impactLevel === 'medium' ? 'bg-yellow-500/5 border-yellow-500/30' :
              'bg-industrial-card border-industrial-border'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-white">{chain.name}</span>
              {chain.impactLevel === 'critical' && (
                <span className="px-2 py-0.5 rounded text-xs bg-red-500/20 text-red-400">
                  Impact Critique
                </span>
              )}
              {chain.impactLevel === 'medium' && (
                <span className="px-2 py-0.5 rounded text-xs bg-yellow-500/20 text-yellow-400">
                  Impact Modéré
                </span>
              )}
            </div>

            <div className="flex items-center gap-1 overflow-x-auto pb-2">
              {chain.steps.map((step, idx) => (
                <React.Fragment key={step.id}>
                  <div
                    className={`flex-shrink-0 px-3 py-2 rounded-lg border-2 ${getStepBorderColor(step.status)}`}
                    title={step.name}
                  >
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${getStepColor(step.status)}`} />
                      <span className="text-xs text-white whitespace-nowrap">{step.name}</span>
                    </div>
                  </div>
                  {idx < chain.steps.length - 1 && (
                    <ArrowRight className={`w-4 h-4 flex-shrink-0 ${
                      step.status === 'error' || step.status === 'blocked' ? 'text-red-400' :
                      step.status === 'warning' ? 'text-yellow-400' : 'text-gray-500'
                    }`} />
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// Impact actif sur la production
export function ActiveImpactsView({ impacts }) {
  const defaultImpacts = impacts?.length > 0 ? impacts : [
    {
      id: 'imp-1',
      title: 'Arrêt Ligne Soudure',
      severity: 'critical',
      affectedLines: ['Ligne B', 'Ligne C'],
      lostProduction: 145,
      estimatedCost: 12500,
      duration: '2h 15min',
      rootCause: 'Défaillance robot soudure RS-02'
    },
    {
      id: 'imp-2',
      title: 'Ralentissement Zone Assemblage',
      severity: 'warning',
      affectedLines: ['Ligne A'],
      lostProduction: 32,
      estimatedCost: 2800,
      duration: '45min',
      rootCause: 'Approvisionnement composants retardé'
    }
  ]

  return (
    <div className="space-y-4">
      <h4 className="font-medium text-white flex items-center gap-2">
        <Target className="w-4 h-4 text-red-400" />
        Impacts Actifs sur Production
      </h4>

      <div className="space-y-3">
        {defaultImpacts.map(impact => (
          <div
            key={impact.id}
            className={`p-4 rounded-lg border ${
              impact.severity === 'critical' ? 'bg-red-500/10 border-red-500/30' :
              'bg-yellow-500/10 border-yellow-500/30'
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <AlertTriangle className={`w-4 h-4 ${
                  impact.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'
                }`} />
                <span className="font-medium text-white">{impact.title}</span>
              </div>
              <span className={`px-2 py-0.5 rounded text-xs ${
                impact.severity === 'critical' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
              }`}>
                {impact.severity === 'critical' ? 'Critique' : 'Modéré'}
              </span>
            </div>

            <p className="text-xs text-gray-400 mb-3">Cause: {impact.rootCause}</p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div>
                <span className="text-gray-500">Lignes affectées</span>
                <div className="text-white font-medium">{impact.affectedLines.join(', ')}</div>
              </div>
              <div>
                <span className="text-gray-500">Production perdue</span>
                <div className="text-red-400 font-medium">{impact.lostProduction} unités</div>
              </div>
              <div>
                <span className="text-gray-500">Coût estimé</span>
                <div className="text-red-400 font-medium">{impact.estimatedCost.toLocaleString()}€</div>
              </div>
              <div>
                <span className="text-gray-500">Durée</span>
                <div className="text-white font-medium">{impact.duration}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// Composant principal combiné pour une vue d'ensemble OT
export function OTOverviewPanel({ otData }) {
  return (
    <div className="space-y-6">
      <OTHealthIndicator otData={otData} />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <OTSystemCard system="scada" data={otData?.scada} />
        <OTSystemCard system="mes" data={otData?.mes} />
        <OTSystemCard system="plm" data={otData?.plm} />
        <OTSystemCard system="opcua" data={otData?.opcua} />
      </div>

      <IndustrialMetrics
        mtbf={otData?.mtbf}
        mttr={otData?.mttr}
        trs={otData?.trs}
      />

      <ProductionZoneView zones={otData?.zones} />

      <DependencyChainView chain={otData?.dependencyChain} />

      <ActiveImpactsView impacts={otData?.activeImpacts} />
    </div>
  )
}

export default OTOverviewPanel
