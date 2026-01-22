import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Play,
  Pause,
  RefreshCw,
  Settings,
  Activity,
  Server,
  Database,
  Radio,
  Thermometer,
  Gauge,
  Factory,
  Cpu,
  Network,
  Zap,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
  BarChart3,
  Sliders,
  Eye,
  Download,
  Upload,
  ChevronDown,
  ChevronRight,
  Terminal,
  Box,
  Layers,
  Target,
  Workflow
} from 'lucide-react'
import { useI18n } from '../i18n'

// Simulator types configuration
const SIMULATOR_TYPES = {
  SCADA: {
    id: 'scada',
    name: 'SCADA Simulator',
    description: 'Systeme SCADA industriel - Temperature, pression, debit, vibrations',
    icon: Thermometer,
    color: 'from-red-500 to-orange-600',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    textColor: 'text-red-400',
    metrics: ['temperature', 'pressure', 'flow_rate', 'vibration', 'power_consumption'],
    defaultRate: 500,
    kafkaTopic: 'scada-metrics',
    zones: ['OT-Zone-A', 'OT-Zone-B', 'DMZ']
  },
  MES: {
    id: 'mes',
    name: 'MES Simulator',
    description: 'Manufacturing Execution System - Production, qualite, cycles',
    icon: Factory,
    color: 'from-blue-500 to-cyan-600',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    textColor: 'text-blue-400',
    metrics: ['production_count', 'cycle_time', 'defect_rate', 'oee', 'downtime'],
    defaultRate: 100,
    kafkaTopic: 'mes-events',
    zones: ['Production-Line-1', 'Production-Line-2', 'Assembly']
  },
  PLM: {
    id: 'plm',
    name: 'PLM Simulator',
    description: 'Product Lifecycle Management - Documents, revisions, workflows',
    icon: Workflow,
    color: 'from-purple-500 to-pink-600',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30',
    textColor: 'text-purple-400',
    metrics: ['document_versions', 'change_requests', 'approval_time', 'bom_changes'],
    defaultRate: 20,
    kafkaTopic: 'plm-data',
    zones: ['Engineering', 'Quality', 'Operations']
  },
  OPCUA: {
    id: 'opcua',
    name: 'OPC-UA Simulator',
    description: 'Protocole OPC-UA - Noeuds, valeurs, alarmes temps reel',
    icon: Network,
    color: 'from-green-500 to-emerald-600',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    textColor: 'text-green-400',
    metrics: ['node_values', 'alarms', 'events', 'subscriptions'],
    defaultRate: 200,
    kafkaTopic: 'opcua-nodes',
    zones: ['PLC-Network', 'DCS-Network', 'HMI-Network']
  },
  IT_INFRA: {
    id: 'it_infra',
    name: 'IT Infrastructure',
    description: 'Infrastructure IT - Serveurs, conteneurs, reseau',
    icon: Server,
    color: 'from-cyan-500 to-blue-600',
    bgColor: 'bg-cyan-500/10',
    borderColor: 'border-cyan-500/30',
    textColor: 'text-cyan-400',
    metrics: ['cpu_usage', 'memory_usage', 'disk_io', 'network_latency', 'container_count'],
    defaultRate: 300,
    kafkaTopic: 'it-metrics',
    zones: ['Datacenter-1', 'Cloud-AWS', 'Edge-Nodes']
  },
  SECURITY: {
    id: 'security',
    name: 'Security Events',
    description: 'Evenements securite - Authentification, firewall, IDS/IPS',
    icon: AlertTriangle,
    color: 'from-amber-500 to-red-600',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/30',
    textColor: 'text-amber-400',
    metrics: ['auth_events', 'firewall_logs', 'ids_alerts', 'vulnerability_scans'],
    defaultRate: 50,
    kafkaTopic: 'security-events',
    zones: ['Perimeter', 'Internal', 'OT-Firewall']
  }
}

// Industrial scenarios / use cases
const USE_CASES = [
  {
    id: 'normal_operations',
    name: 'Operations Normales',
    description: 'Simulation standard sans anomalies',
    icon: CheckCircle2,
    color: 'text-green-400',
    simulators: ['scada', 'mes', 'opcua', 'it_infra'],
    anomalyRate: 0,
    duration: null // continuous
  },
  {
    id: 'thermal_drift',
    name: 'Derive Thermique',
    description: 'Augmentation progressive temperature moteur principal',
    icon: Thermometer,
    color: 'text-orange-400',
    simulators: ['scada', 'opcua'],
    anomalyRate: 0.3,
    duration: 300, // 5 min
    scenario: {
      type: 'gradual_increase',
      metric: 'temperature',
      target: 95,
      rampTime: 180
    }
  },
  {
    id: 'production_slowdown',
    name: 'Ralentissement Production',
    description: 'Baisse OEE due a des micro-arrets repetitifs',
    icon: TrendingUp,
    color: 'text-yellow-400',
    simulators: ['mes', 'scada', 'plm'],
    anomalyRate: 0.4,
    duration: 600,
    scenario: {
      type: 'periodic_drops',
      metric: 'oee',
      frequency: 60,
      dropPercent: 15
    }
  },
  {
    id: 'network_latency',
    name: 'Latence Reseau OT-IT',
    description: 'Degradation connectivite entre zones OT et IT',
    icon: Network,
    color: 'text-red-400',
    simulators: ['it_infra', 'opcua', 'security'],
    anomalyRate: 0.5,
    duration: 240,
    scenario: {
      type: 'spike_pattern',
      metric: 'network_latency',
      baselineMs: 5,
      spikeMs: 500,
      spikeFrequency: 30
    }
  },
  {
    id: 'cyber_attack',
    name: 'Simulation Cyberattaque',
    description: 'Tentatives intrusion et scan de vulnerabilites',
    icon: AlertTriangle,
    color: 'text-red-500',
    simulators: ['security', 'it_infra', 'opcua'],
    anomalyRate: 0.8,
    duration: 180,
    scenario: {
      type: 'attack_pattern',
      phases: ['reconnaissance', 'initial_access', 'lateral_movement']
    }
  },
  {
    id: 'predictive_maintenance',
    name: 'Maintenance Predictive',
    description: 'Degradation progressive pour tester detection RUL',
    icon: Gauge,
    color: 'text-purple-400',
    simulators: ['scada', 'opcua', 'mes'],
    anomalyRate: 0.25,
    duration: 900,
    scenario: {
      type: 'degradation_curve',
      metrics: ['vibration', 'temperature', 'power_consumption'],
      degradationRate: 0.02
    }
  },
  {
    id: 'it_ot_correlation',
    name: 'Correlation IT-OT',
    description: 'Incident IT impactant la production OT',
    icon: Layers,
    color: 'text-cyan-400',
    simulators: ['it_infra', 'scada', 'mes', 'opcua'],
    anomalyRate: 0.6,
    duration: 420,
    scenario: {
      type: 'cascade_failure',
      trigger: 'database_slowdown',
      impacts: ['mes_delay', 'scada_timeout', 'production_drop']
    }
  },
  {
    id: 'ai_drift',
    name: 'Derive Modele IA',
    description: 'Degradation predictions modele de maintenance',
    icon: Cpu,
    color: 'text-pink-400',
    simulators: ['scada', 'mes'],
    anomalyRate: 0.35,
    duration: 600,
    scenario: {
      type: 'model_drift',
      driftType: 'concept_drift',
      accuracy_decay: 0.05
    }
  }
]

// Simulator Card Component
function SimulatorCard({ simulator, status, onToggle, onConfigure }) {
  const Icon = simulator.icon
  const isRunning = status?.running || false
  const metrics = status?.metrics || {}

  return (
    <motion.div
      className={`relative p-4 rounded-xl border-2 transition-all duration-300
        ${isRunning
          ? `${simulator.bgColor} ${simulator.borderColor}`
          : 'bg-industrial-card/50 border-industrial-border hover:border-industrial-accent/30'
        }`}
      whileHover={{ scale: 1.01 }}
    >
      {/* Status indicator */}
      <div className="absolute top-3 right-3 flex items-center gap-2">
        {isRunning && (
          <motion.div
            className={`flex items-center gap-1 px-2 py-1 rounded-full ${simulator.bgColor}`}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <motion.div
              className={`w-2 h-2 rounded-full bg-green-500`}
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 1 }}
            />
            <span className="text-xs text-green-400">{metrics.rate || simulator.defaultRate}/s</span>
          </motion.div>
        )}
      </div>

      {/* Header */}
      <div className="flex items-start gap-3 mb-3">
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${simulator.color} flex items-center justify-center shadow-lg`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <div className="flex-1">
          <h3 className={`font-bold ${isRunning ? simulator.textColor : 'text-white'}`}>
            {simulator.name}
          </h3>
          <p className="text-xs text-gray-400 line-clamp-2">{simulator.description}</p>
        </div>
      </div>

      {/* Metrics preview */}
      {isRunning && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mb-3 grid grid-cols-2 gap-2"
        >
          <div className="p-2 rounded-lg bg-industrial-darker/50">
            <span className="text-xs text-gray-500">Messages</span>
            <p className={`text-sm font-bold ${simulator.textColor}`}>
              {(metrics.totalMessages || 0).toLocaleString()}
            </p>
          </div>
          <div className="p-2 rounded-lg bg-industrial-darker/50">
            <span className="text-xs text-gray-500">Topic</span>
            <p className="text-xs font-mono text-gray-300 truncate">{simulator.kafkaTopic}</p>
          </div>
        </motion.div>
      )}

      {/* Zones */}
      <div className="flex flex-wrap gap-1 mb-3">
        {simulator.zones.map((zone) => (
          <span
            key={zone}
            className="text-[10px] px-2 py-0.5 rounded-full bg-industrial-darker/50 text-gray-400 border border-industrial-border"
          >
            {zone}
          </span>
        ))}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <motion.button
          onClick={() => onToggle(simulator.id)}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all
            ${isRunning
              ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/30'
              : `bg-gradient-to-r ${simulator.color} text-white hover:opacity-90`
            }`}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {isRunning ? (
            <>
              <Pause className="w-4 h-4" />
              Arreter
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Demarrer
            </>
          )}
        </motion.button>
        <motion.button
          onClick={() => onConfigure(simulator.id)}
          className="p-2 rounded-lg bg-industrial-card border border-industrial-border hover:border-industrial-accent/30 text-gray-400 hover:text-white"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Settings className="w-4 h-4" />
        </motion.button>
      </div>
    </motion.div>
  )
}

// Use Case Card Component
function UseCaseCard({ useCase, isActive, onActivate }) {
  const Icon = useCase.icon

  return (
    <motion.button
      onClick={() => onActivate(useCase.id)}
      className={`w-full p-4 rounded-xl border-2 text-left transition-all duration-300
        ${isActive
          ? 'bg-cyan-500/10 border-cyan-500/30'
          : 'bg-industrial-card/50 border-industrial-border hover:border-industrial-accent/30'
        }`}
      whileHover={{ scale: 1.01, y: -2 }}
      whileTap={{ scale: 0.99 }}
    >
      <div className="flex items-start gap-3">
        <div className={`w-10 h-10 rounded-lg bg-industrial-darker flex items-center justify-center ${useCase.color}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h4 className={`font-semibold ${isActive ? 'text-cyan-400' : 'text-white'}`}>
              {useCase.name}
            </h4>
            {isActive && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="w-5 h-5 rounded-full bg-cyan-500 flex items-center justify-center"
              >
                <CheckCircle2 className="w-3 h-3 text-white" />
              </motion.div>
            )}
          </div>
          <p className="text-xs text-gray-400 mt-1">{useCase.description}</p>

          {/* Simulators involved */}
          <div className="flex flex-wrap gap-1 mt-2">
            {useCase.simulators.map((simId) => {
              const sim = Object.values(SIMULATOR_TYPES).find(s => s.id === simId)
              return sim ? (
                <span
                  key={simId}
                  className={`text-[10px] px-1.5 py-0.5 rounded ${sim.bgColor} ${sim.textColor}`}
                >
                  {sim.id.toUpperCase()}
                </span>
              ) : null
            })}
          </div>

          {/* Duration & Anomaly rate */}
          <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
            {useCase.duration ? (
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {Math.floor(useCase.duration / 60)}min
              </span>
            ) : (
              <span className="flex items-center gap-1">
                <RefreshCw className="w-3 h-3" />
                Continu
              </span>
            )}
            {useCase.anomalyRate > 0 && (
              <span className="flex items-center gap-1 text-amber-400">
                <AlertTriangle className="w-3 h-3" />
                {Math.round(useCase.anomalyRate * 100)}% anomalies
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.button>
  )
}

// Configuration Modal
function ConfigModal({ simulator, config, onSave, onClose }) {
  const [localConfig, setLocalConfig] = useState(config)

  if (!simulator) return null

  const Icon = simulator.icon

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-industrial-card rounded-2xl border border-industrial-border p-6 max-w-md w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 mb-6">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${simulator.color} flex items-center justify-center`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Configuration {simulator.name}</h3>
            <p className="text-sm text-gray-400">Parametres du simulateur</p>
          </div>
        </div>

        <div className="space-y-4">
          {/* Data Rate */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Debit de donnees (points/seconde)
            </label>
            <div className="flex items-center gap-3">
              <input
                type="range"
                min="10"
                max="1000"
                value={localConfig.rate || simulator.defaultRate}
                onChange={(e) => setLocalConfig({ ...localConfig, rate: parseInt(e.target.value) })}
                className="flex-1 h-2 bg-industrial-darker rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-sm font-mono text-cyan-400 w-16 text-right">
                {localConfig.rate || simulator.defaultRate}/s
              </span>
            </div>
          </div>

          {/* Zone Selection */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Zones actives</label>
            <div className="flex flex-wrap gap-2">
              {simulator.zones.map((zone) => (
                <button
                  key={zone}
                  onClick={() => {
                    const zones = localConfig.zones || simulator.zones
                    const newZones = zones.includes(zone)
                      ? zones.filter(z => z !== zone)
                      : [...zones, zone]
                    setLocalConfig({ ...localConfig, zones: newZones })
                  }}
                  className={`px-3 py-1.5 rounded-lg text-sm transition-all
                    ${(localConfig.zones || simulator.zones).includes(zone)
                      ? `${simulator.bgColor} ${simulator.borderColor} ${simulator.textColor} border`
                      : 'bg-industrial-darker text-gray-400 border border-industrial-border hover:border-industrial-accent/30'
                    }`}
                >
                  {zone}
                </button>
              ))}
            </div>
          </div>

          {/* Metrics Selection */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Metriques generees</label>
            <div className="flex flex-wrap gap-2">
              {simulator.metrics.map((metric) => (
                <button
                  key={metric}
                  onClick={() => {
                    const metrics = localConfig.metrics || simulator.metrics
                    const newMetrics = metrics.includes(metric)
                      ? metrics.filter(m => m !== metric)
                      : [...metrics, metric]
                    setLocalConfig({ ...localConfig, metrics: newMetrics })
                  }}
                  className={`px-2 py-1 rounded text-xs font-mono transition-all
                    ${(localConfig.metrics || simulator.metrics).includes(metric)
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                      : 'bg-industrial-darker text-gray-500 border border-industrial-border'
                    }`}
                >
                  {metric}
                </button>
              ))}
            </div>
          </div>

          {/* Anomaly injection */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Injection d'anomalies
            </label>
            <div className="flex items-center gap-3">
              <input
                type="range"
                min="0"
                max="100"
                value={(localConfig.anomalyRate || 0) * 100}
                onChange={(e) => setLocalConfig({ ...localConfig, anomalyRate: parseInt(e.target.value) / 100 })}
                className="flex-1 h-2 bg-industrial-darker rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-sm font-mono text-amber-400 w-12 text-right">
                {Math.round((localConfig.anomalyRate || 0) * 100)}%
              </span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 rounded-lg bg-industrial-darker text-gray-400 hover:text-white border border-industrial-border hover:border-industrial-accent/30 transition-all"
          >
            Annuler
          </button>
          <button
            onClick={() => {
              onSave(simulator.id, localConfig)
              onClose()
            }}
            className="flex-1 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium hover:opacity-90 transition-all"
          >
            Appliquer
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}

// Global Stats Component
function GlobalStats({ simulatorStatus, activeUseCase }) {
  const runningCount = Object.values(simulatorStatus).filter(s => s.running).length
  const totalMessages = Object.values(simulatorStatus).reduce((sum, s) => sum + (s.metrics?.totalMessages || 0), 0)
  const totalRate = Object.values(simulatorStatus)
    .filter(s => s.running)
    .reduce((sum, s) => sum + (s.metrics?.rate || 0), 0)

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <motion.div
        className="p-4 rounded-xl bg-industrial-card/50 border border-industrial-border"
        whileHover={{ scale: 1.02 }}
      >
        <div className="flex items-center gap-2 mb-2">
          <Activity className="w-4 h-4 text-green-400" />
          <span className="text-xs text-gray-400">Simulateurs Actifs</span>
        </div>
        <p className="text-2xl font-bold text-white">
          {runningCount}/{Object.keys(SIMULATOR_TYPES).length}
        </p>
      </motion.div>

      <motion.div
        className="p-4 rounded-xl bg-industrial-card/50 border border-industrial-border"
        whileHover={{ scale: 1.02 }}
      >
        <div className="flex items-center gap-2 mb-2">
          <Upload className="w-4 h-4 text-cyan-400" />
          <span className="text-xs text-gray-400">Debit Total</span>
        </div>
        <p className="text-2xl font-bold text-white">
          {totalRate.toLocaleString()}<span className="text-sm text-gray-400">/s</span>
        </p>
      </motion.div>

      <motion.div
        className="p-4 rounded-xl bg-industrial-card/50 border border-industrial-border"
        whileHover={{ scale: 1.02 }}
      >
        <div className="flex items-center gap-2 mb-2">
          <Database className="w-4 h-4 text-purple-400" />
          <span className="text-xs text-gray-400">Messages Totaux</span>
        </div>
        <p className="text-2xl font-bold text-white">
          {totalMessages.toLocaleString()}
        </p>
      </motion.div>

      <motion.div
        className="p-4 rounded-xl bg-industrial-card/50 border border-industrial-border"
        whileHover={{ scale: 1.02 }}
      >
        <div className="flex items-center gap-2 mb-2">
          <Target className="w-4 h-4 text-amber-400" />
          <span className="text-xs text-gray-400">Scenario Actif</span>
        </div>
        <p className="text-sm font-medium text-white truncate">
          {activeUseCase ? USE_CASES.find(u => u.id === activeUseCase)?.name : 'Aucun'}
        </p>
      </motion.div>
    </div>
  )
}

// Main Component
function SimulatorLauncher() {
  const { t } = useI18n()
  const [simulatorStatus, setSimulatorStatus] = useState({})
  const [activeUseCase, setActiveUseCase] = useState(null)
  const [configModal, setConfigModal] = useState({ open: false, simulatorId: null })
  const [simulatorConfigs, setSimulatorConfigs] = useState({})
  const [showUseCases, setShowUseCases] = useState(true)
  const [logs, setLogs] = useState([])

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSimulatorStatus(prev => {
        const updated = { ...prev }
        Object.keys(updated).forEach(id => {
          if (updated[id].running) {
            const config = simulatorConfigs[id] || {}
            const sim = Object.values(SIMULATOR_TYPES).find(s => s.id === id)
            const rate = config.rate || sim?.defaultRate || 100
            updated[id] = {
              ...updated[id],
              metrics: {
                ...updated[id].metrics,
                rate,
                totalMessages: (updated[id].metrics?.totalMessages || 0) + rate
              }
            }
          }
        })
        return updated
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [simulatorConfigs])

  const handleToggleSimulator = async (simulatorId) => {
    const isRunning = simulatorStatus[simulatorId]?.running

    // Add log
    const sim = Object.values(SIMULATOR_TYPES).find(s => s.id === simulatorId)
    setLogs(prev => [{
      timestamp: new Date().toISOString(),
      level: isRunning ? 'info' : 'success',
      message: `${sim?.name} ${isRunning ? 'arrete' : 'demarre'}`
    }, ...prev.slice(0, 49)])

    setSimulatorStatus(prev => ({
      ...prev,
      [simulatorId]: {
        running: !isRunning,
        metrics: isRunning ? {} : { totalMessages: 0, rate: simulatorConfigs[simulatorId]?.rate || sim?.defaultRate }
      }
    }))

    // Call API to start/stop simulator
    try {
      const action = isRunning ? 'stop' : 'start'
      const config = simulatorConfigs[simulatorId] || {}
      await fetch(`/api/simulators/${simulatorId}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })
    } catch (error) {
      console.error('Failed to toggle simulator:', error)
    }
  }

  const handleConfigureSimulator = (simulatorId) => {
    setConfigModal({ open: true, simulatorId })
  }

  const handleSaveConfig = (simulatorId, config) => {
    setSimulatorConfigs(prev => ({
      ...prev,
      [simulatorId]: config
    }))
    setLogs(prev => [{
      timestamp: new Date().toISOString(),
      level: 'info',
      message: `Configuration ${simulatorId.toUpperCase()} mise a jour`
    }, ...prev.slice(0, 49)])
  }

  const handleActivateUseCase = async (useCaseId) => {
    const useCase = USE_CASES.find(u => u.id === useCaseId)
    if (!useCase) return

    // If clicking same use case, deactivate
    if (activeUseCase === useCaseId) {
      setActiveUseCase(null)
      // Stop all simulators from use case
      useCase.simulators.forEach(simId => {
        if (simulatorStatus[simId]?.running) {
          handleToggleSimulator(simId)
        }
      })
      setLogs(prev => [{
        timestamp: new Date().toISOString(),
        level: 'warning',
        message: `Scenario "${useCase.name}" desactive`
      }, ...prev.slice(0, 49)])
      return
    }

    setActiveUseCase(useCaseId)
    setLogs(prev => [{
      timestamp: new Date().toISOString(),
      level: 'success',
      message: `Scenario "${useCase.name}" active`
    }, ...prev.slice(0, 49)])

    // Start all required simulators with use case config
    for (const simId of useCase.simulators) {
      if (!simulatorStatus[simId]?.running) {
        // Set anomaly rate from use case
        setSimulatorConfigs(prev => ({
          ...prev,
          [simId]: {
            ...prev[simId],
            anomalyRate: useCase.anomalyRate
          }
        }))
        await handleToggleSimulator(simId)
      }
    }

    // Call API to activate scenario
    try {
      await fetch(`/api/scenarios/${useCaseId}/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(useCase.scenario)
      })
    } catch (error) {
      console.error('Failed to activate scenario:', error)
    }
  }

  const handleStartAll = () => {
    Object.values(SIMULATOR_TYPES).forEach(sim => {
      if (!simulatorStatus[sim.id]?.running) {
        handleToggleSimulator(sim.id)
      }
    })
  }

  const handleStopAll = () => {
    Object.values(SIMULATOR_TYPES).forEach(sim => {
      if (simulatorStatus[sim.id]?.running) {
        handleToggleSimulator(sim.id)
      }
    })
    setActiveUseCase(null)
  }

  const selectedSimulator = configModal.simulatorId
    ? Object.values(SIMULATOR_TYPES).find(s => s.id === configModal.simulatorId)
    : null

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
              <Radio className="w-5 h-5 text-white" />
            </div>
            Lanceur de Simulateurs
          </h1>
          <p className="text-gray-400 mt-1">
            Generez des donnees industrielles realistes pour tester et demonstrer la plateforme
          </p>
        </div>

        <div className="flex items-center gap-3">
          <motion.button
            onClick={handleStartAll}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-green-500 to-emerald-600 text-white font-medium hover:opacity-90"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Play className="w-4 h-4" />
            Tout Demarrer
          </motion.button>
          <motion.button
            onClick={handleStopAll}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Pause className="w-4 h-4" />
            Tout Arreter
          </motion.button>
        </div>
      </div>

      {/* Global Stats */}
      <GlobalStats simulatorStatus={simulatorStatus} activeUseCase={activeUseCase} />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Simulators Grid */}
        <div className="xl:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Server className="w-5 h-5 text-cyan-400" />
            Simulateurs Industriels
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.values(SIMULATOR_TYPES).map((simulator) => (
              <SimulatorCard
                key={simulator.id}
                simulator={simulator}
                status={simulatorStatus[simulator.id]}
                onToggle={handleToggleSimulator}
                onConfigure={handleConfigureSimulator}
              />
            ))}
          </div>
        </div>

        {/* Use Cases Panel */}
        <div className="space-y-4">
          <button
            onClick={() => setShowUseCases(!showUseCases)}
            className="w-full flex items-center justify-between text-lg font-semibold text-white"
          >
            <span className="flex items-center gap-2">
              <Target className="w-5 h-5 text-amber-400" />
              Scenarios & Use Cases
            </span>
            <motion.div
              animate={{ rotate: showUseCases ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ChevronDown className="w-5 h-5 text-gray-400" />
            </motion.div>
          </button>

          <AnimatePresence>
            {showUseCases && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-3 overflow-hidden"
              >
                {USE_CASES.map((useCase) => (
                  <UseCaseCard
                    key={useCase.id}
                    useCase={useCase}
                    isActive={activeUseCase === useCase.id}
                    onActivate={handleActivateUseCase}
                  />
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Activity Log */}
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">
              <Terminal className="w-4 h-4 text-gray-400" />
              Journal d'Activite
            </h3>
            <div className="bg-industrial-darker rounded-xl border border-industrial-border p-3 h-48 overflow-y-auto font-mono text-xs">
              {logs.length === 0 ? (
                <p className="text-gray-500">Aucune activite...</p>
              ) : (
                logs.map((log, idx) => (
                  <div key={idx} className="flex items-start gap-2 mb-1">
                    <span className="text-gray-500 shrink-0">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span className={`
                      ${log.level === 'success' ? 'text-green-400' : ''}
                      ${log.level === 'warning' ? 'text-amber-400' : ''}
                      ${log.level === 'error' ? 'text-red-400' : ''}
                      ${log.level === 'info' ? 'text-gray-300' : ''}
                    `}>
                      {log.message}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Configuration Modal */}
      <AnimatePresence>
        {configModal.open && selectedSimulator && (
          <ConfigModal
            simulator={selectedSimulator}
            config={simulatorConfigs[configModal.simulatorId] || {}}
            onSave={handleSaveConfig}
            onClose={() => setConfigModal({ open: false, simulatorId: null })}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

export default SimulatorLauncher
