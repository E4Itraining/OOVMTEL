import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Activity,
  Factory,
  Thermometer,
  Gauge,
  Zap,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Settings,
  Eye,
  Layers,
  Target,
  RefreshCw,
  ChevronRight,
  Radio,
  Cpu,
  HardDrive,
  Network,
  Server,
  Box,
  CircuitBoard,
  Workflow,
  LineChart,
  PieChart,
  Timer,
  Wrench,
  Shield,
  Database,
  ArrowUp,
  ArrowDown,
  ArrowRight,
  Minus,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react'
import { useI18n } from '../i18n'
import {
  LineChart as RechartsLine,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
  Cell,
  PieChart as RechartsPie,
  Pie
} from 'recharts'

// ISA-95 Levels Configuration
const ISA95_LEVELS = {
  LEVEL_0: {
    id: 0,
    name: 'Niveau 0 - Process',
    description: 'Capteurs, actionneurs, instrumentation',
    icon: Radio,
    color: 'from-red-500 to-orange-600',
    bgColor: 'bg-red-500/10',
    textColor: 'text-red-400'
  },
  LEVEL_1: {
    id: 1,
    name: 'Niveau 1 - Controle',
    description: 'PLC, DCS, controleurs locaux',
    icon: CircuitBoard,
    color: 'from-orange-500 to-amber-600',
    bgColor: 'bg-orange-500/10',
    textColor: 'text-orange-400'
  },
  LEVEL_2: {
    id: 2,
    name: 'Niveau 2 - Supervision',
    description: 'SCADA, HMI, historiens',
    icon: Eye,
    color: 'from-yellow-500 to-lime-600',
    bgColor: 'bg-yellow-500/10',
    textColor: 'text-yellow-400'
  },
  LEVEL_3: {
    id: 3,
    name: 'Niveau 3 - MES/MOM',
    description: 'Execution, ordonnancement, qualite',
    icon: Factory,
    color: 'from-green-500 to-emerald-600',
    bgColor: 'bg-green-500/10',
    textColor: 'text-green-400'
  },
  LEVEL_4: {
    id: 4,
    name: 'Niveau 4 - ERP/Business',
    description: 'Planification, gestion, reporting',
    icon: BarChart3,
    color: 'from-blue-500 to-cyan-600',
    bgColor: 'bg-blue-500/10',
    textColor: 'text-blue-400'
  }
}

// Equipment types
const EQUIPMENT_TYPES = {
  MOTOR: { name: 'Moteur', icon: Zap, metrics: ['temperature', 'vibration', 'current', 'rpm'] },
  PUMP: { name: 'Pompe', icon: RefreshCw, metrics: ['flow', 'pressure', 'temperature', 'power'] },
  CONVEYOR: { name: 'Convoyeur', icon: ArrowRight, metrics: ['speed', 'load', 'alignment', 'tension'] },
  ROBOT: { name: 'Robot', icon: Box, metrics: ['cycle_time', 'accuracy', 'temperature', 'torque'] },
  FURNACE: { name: 'Four', icon: Thermometer, metrics: ['temperature', 'pressure', 'gas_flow', 'power'] },
  PRESS: { name: 'Presse', icon: ArrowDown, metrics: ['force', 'position', 'cycle_time', 'oil_temp'] },
  CNC: { name: 'CNC', icon: Settings, metrics: ['spindle_speed', 'feed_rate', 'tool_wear', 'vibration'] },
  COMPRESSOR: { name: 'Compresseur', icon: Gauge, metrics: ['pressure', 'temperature', 'flow', 'power'] }
}

// Generate mock real-time data
const generateEquipmentData = () => {
  const equipments = [
    { id: 'MOT-001', type: 'MOTOR', name: 'Moteur Principal L1', zone: 'Production-Line-1', level: 0 },
    { id: 'MOT-002', type: 'MOTOR', name: 'Moteur Ventilation', zone: 'Production-Line-1', level: 0 },
    { id: 'PMP-001', type: 'PUMP', name: 'Pompe Hydraulique A', zone: 'Utilities', level: 0 },
    { id: 'PMP-002', type: 'PUMP', name: 'Pompe Refroidissement', zone: 'Utilities', level: 0 },
    { id: 'CNV-001', type: 'CONVEYOR', name: 'Convoyeur Principal', zone: 'Assembly', level: 1 },
    { id: 'CNV-002', type: 'CONVEYOR', name: 'Convoyeur Sortie', zone: 'Packaging', level: 1 },
    { id: 'ROB-001', type: 'ROBOT', name: 'Robot Soudure R1', zone: 'Welding', level: 1 },
    { id: 'ROB-002', type: 'ROBOT', name: 'Robot Pick&Place', zone: 'Assembly', level: 1 },
    { id: 'FUR-001', type: 'FURNACE', name: 'Four Traitement T1', zone: 'Heat-Treatment', level: 0 },
    { id: 'PRS-001', type: 'PRESS', name: 'Presse Emboutissage', zone: 'Stamping', level: 1 },
    { id: 'CNC-001', type: 'CNC', name: 'Centre Usinage CNC', zone: 'Machining', level: 1 },
    { id: 'CMP-001', type: 'COMPRESSOR', name: 'Compresseur Air', zone: 'Utilities', level: 0 }
  ]

  return equipments.map(eq => {
    const type = EQUIPMENT_TYPES[eq.type]
    const health = 70 + Math.random() * 30
    const hasAlert = Math.random() < 0.15

    const metrics = {}
    type.metrics.forEach(metric => {
      metrics[metric] = {
        value: 50 + Math.random() * 50,
        unit: getMetricUnit(metric),
        status: hasAlert && Math.random() < 0.3 ? 'warning' : 'normal',
        trend: Math.random() < 0.5 ? 'up' : 'down'
      }
    })

    return {
      ...eq,
      health,
      status: health > 90 ? 'optimal' : health > 70 ? 'normal' : health > 50 ? 'degraded' : 'critical',
      lastUpdate: new Date().toISOString(),
      metrics,
      alerts: hasAlert ? [{ type: 'warning', message: 'Valeur proche du seuil' }] : [],
      rul: Math.floor(100 + Math.random() * 900) // Remaining Useful Life in hours
    }
  })
}

const getMetricUnit = (metric) => {
  const units = {
    temperature: 'C', vibration: 'mm/s', current: 'A', rpm: 'tr/min',
    flow: 'm3/h', pressure: 'bar', power: 'kW', speed: 'm/min',
    load: '%', alignment: 'mm', tension: 'N', cycle_time: 's',
    accuracy: 'mm', torque: 'Nm', gas_flow: 'Nm3/h', force: 'kN',
    position: 'mm', oil_temp: 'C', spindle_speed: 'tr/min',
    feed_rate: 'mm/min', tool_wear: '%'
  }
  return units[metric] || ''
}

// KPI Card Component
function KPICard({ title, value, unit, icon: Icon, trend, trendValue, color, subtitle }) {
  const isPositive = trend === 'up'
  const TrendIcon = trend === 'up' ? ArrowUp : trend === 'down' ? ArrowDown : Minus

  return (
    <motion.div
      className="p-4 rounded-xl bg-industrial-card/50 border border-industrial-border hover:border-industrial-accent/30 transition-all"
      whileHover={{ scale: 1.02, y: -2 }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-xs ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            <TrendIcon className="w-3 h-3" />
            {trendValue}%
          </div>
        )}
      </div>
      <p className="text-xs text-gray-400 mb-1">{title}</p>
      <p className="text-2xl font-bold text-white">
        {value}<span className="text-sm text-gray-400 ml-1">{unit}</span>
      </p>
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
    </motion.div>
  )
}

// Equipment Health Card
function EquipmentCard({ equipment, onClick }) {
  const type = EQUIPMENT_TYPES[equipment.type]
  const Icon = type?.icon || Box
  const level = ISA95_LEVELS[`LEVEL_${equipment.level}`]

  const statusColors = {
    optimal: 'text-green-400 bg-green-500/10 border-green-500/30',
    normal: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
    degraded: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
    critical: 'text-red-400 bg-red-500/10 border-red-500/30'
  }

  return (
    <motion.button
      onClick={() => onClick(equipment)}
      className={`w-full p-4 rounded-xl border-2 text-left transition-all ${statusColors[equipment.status]} hover:scale-[1.01]`}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.99 }}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${level.color} flex items-center justify-center`}>
            <Icon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h4 className="font-semibold text-white text-sm">{equipment.name}</h4>
            <p className="text-xs text-gray-400">{equipment.id} - {equipment.zone}</p>
          </div>
        </div>
        {equipment.alerts.length > 0 && (
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          </motion.div>
        )}
      </div>

      {/* Health gauge */}
      <div className="mb-3">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-gray-400">Sante</span>
          <span className="font-mono text-white">{Math.round(equipment.health)}%</span>
        </div>
        <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
          <motion.div
            className={`h-full rounded-full ${
              equipment.health > 90 ? 'bg-green-500' :
              equipment.health > 70 ? 'bg-cyan-500' :
              equipment.health > 50 ? 'bg-amber-500' : 'bg-red-500'
            }`}
            initial={{ width: 0 }}
            animate={{ width: `${equipment.health}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>

      {/* Key metrics preview */}
      <div className="grid grid-cols-2 gap-2">
        {Object.entries(equipment.metrics).slice(0, 2).map(([key, metric]) => (
          <div key={key} className="text-xs">
            <span className="text-gray-500 capitalize">{key.replace('_', ' ')}</span>
            <p className={`font-mono ${metric.status === 'warning' ? 'text-amber-400' : 'text-gray-300'}`}>
              {metric.value.toFixed(1)} {metric.unit}
            </p>
          </div>
        ))}
      </div>

      {/* RUL indicator */}
      <div className="mt-2 pt-2 border-t border-industrial-border">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-500 flex items-center gap-1">
            <Clock className="w-3 h-3" /> RUL
          </span>
          <span className={`font-mono ${equipment.rul < 200 ? 'text-red-400' : equipment.rul < 500 ? 'text-amber-400' : 'text-green-400'}`}>
            {equipment.rul}h
          </span>
        </div>
      </div>
    </motion.button>
  )
}

// ISA-95 Level Overview
function ISA95LevelCard({ level, equipmentCount, alertCount }) {
  const Icon = level.icon

  return (
    <motion.div
      className={`p-3 rounded-lg ${level.bgColor} border border-opacity-30`}
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex items-center gap-2 mb-2">
        <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${level.color} flex items-center justify-center`}>
          <Icon className="w-4 h-4 text-white" />
        </div>
        <div>
          <p className={`text-xs font-semibold ${level.textColor}`}>Niveau {level.id}</p>
          <p className="text-[10px] text-gray-500">{level.description}</p>
        </div>
      </div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-gray-400">{equipmentCount} equip.</span>
        {alertCount > 0 && (
          <span className="text-amber-400 flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" /> {alertCount}
          </span>
        )}
      </div>
    </motion.div>
  )
}

// Equipment Detail Modal
function EquipmentDetailModal({ equipment, onClose }) {
  const [selectedMetric, setSelectedMetric] = useState(null)
  const type = EQUIPMENT_TYPES[equipment.type]
  const Icon = type?.icon || Box

  // Generate mock historical data
  const historyData = Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    ...Object.fromEntries(
      type.metrics.map(m => [m, 40 + Math.random() * 40 + (i > 18 ? 10 : 0)])
    )
  }))

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
        className="bg-industrial-card rounded-2xl border border-industrial-border p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
              <Icon className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">{equipment.name}</h2>
              <p className="text-sm text-gray-400">{equipment.id} - {equipment.zone}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  equipment.status === 'optimal' ? 'bg-green-500/20 text-green-400' :
                  equipment.status === 'normal' ? 'bg-cyan-500/20 text-cyan-400' :
                  equipment.status === 'degraded' ? 'bg-amber-500/20 text-amber-400' :
                  'bg-red-500/20 text-red-400'
                }`}>
                  {equipment.status.toUpperCase()}
                </span>
                <span className="text-xs text-gray-500">
                  Niveau ISA-95: {equipment.level}
                </span>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-industrial-darker text-gray-400 hover:text-white transition-colors"
          >
            <XCircle className="w-5 h-5" />
          </button>
        </div>

        {/* Health & RUL */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="p-4 rounded-xl bg-industrial-darker">
            <p className="text-xs text-gray-400 mb-2">Sante Globale</p>
            <div className="flex items-end gap-2">
              <span className="text-3xl font-bold text-white">{Math.round(equipment.health)}</span>
              <span className="text-gray-400 mb-1">%</span>
            </div>
            <div className="h-2 bg-industrial-card rounded-full overflow-hidden mt-2">
              <div
                className={`h-full rounded-full ${
                  equipment.health > 90 ? 'bg-green-500' :
                  equipment.health > 70 ? 'bg-cyan-500' :
                  equipment.health > 50 ? 'bg-amber-500' : 'bg-red-500'
                }`}
                style={{ width: `${equipment.health}%` }}
              />
            </div>
          </div>

          <div className="p-4 rounded-xl bg-industrial-darker">
            <p className="text-xs text-gray-400 mb-2">Duree de Vie Restante (RUL)</p>
            <div className="flex items-end gap-2">
              <span className={`text-3xl font-bold ${
                equipment.rul < 200 ? 'text-red-400' : equipment.rul < 500 ? 'text-amber-400' : 'text-green-400'
              }`}>{equipment.rul}</span>
              <span className="text-gray-400 mb-1">heures</span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {equipment.rul < 200 ? 'Maintenance urgente requise' :
               equipment.rul < 500 ? 'Planifier maintenance' :
               'Equipement en bon etat'}
            </p>
          </div>

          <div className="p-4 rounded-xl bg-industrial-darker">
            <p className="text-xs text-gray-400 mb-2">Alertes Actives</p>
            <div className="flex items-end gap-2">
              <span className={`text-3xl font-bold ${equipment.alerts.length > 0 ? 'text-amber-400' : 'text-green-400'}`}>
                {equipment.alerts.length}
              </span>
              <span className="text-gray-400 mb-1">alertes</span>
            </div>
            {equipment.alerts.length > 0 && (
              <p className="text-xs text-amber-400 mt-2 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                {equipment.alerts[0].message}
              </p>
            )}
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            Metriques Temps Reel
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(equipment.metrics).map(([key, metric]) => (
              <button
                key={key}
                onClick={() => setSelectedMetric(selectedMetric === key ? null : key)}
                className={`p-3 rounded-lg text-left transition-all ${
                  selectedMetric === key
                    ? 'bg-cyan-500/20 border border-cyan-500/30'
                    : 'bg-industrial-darker hover:bg-industrial-card'
                } ${metric.status === 'warning' ? 'border-l-2 border-l-amber-500' : ''}`}
              >
                <p className="text-xs text-gray-400 capitalize mb-1">{key.replace('_', ' ')}</p>
                <p className={`text-lg font-bold ${metric.status === 'warning' ? 'text-amber-400' : 'text-white'}`}>
                  {metric.value.toFixed(1)} <span className="text-xs text-gray-400">{metric.unit}</span>
                </p>
                <div className={`flex items-center gap-1 text-xs mt-1 ${
                  metric.trend === 'up' ? 'text-green-400' : 'text-red-400'
                }`}>
                  {metric.trend === 'up' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
                  {metric.trend === 'up' ? '+' : '-'}2.3%
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Historical Chart */}
        <div className="p-4 rounded-xl bg-industrial-darker">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <LineChart className="w-4 h-4 text-purple-400" />
            Historique 24h {selectedMetric && `- ${selectedMetric.replace('_', ' ')}`}
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={historyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#6B7280" fontSize={10} />
                <YAxis stroke="#6B7280" fontSize={10} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                />
                {(selectedMetric ? [selectedMetric] : type.metrics.slice(0, 2)).map((metric, idx) => (
                  <Area
                    key={metric}
                    type="monotone"
                    dataKey={metric}
                    stroke={idx === 0 ? '#06B6D4' : '#8B5CF6'}
                    fill={idx === 0 ? '#06B6D4' : '#8B5CF6'}
                    fillOpacity={0.2}
                    strokeWidth={2}
                  />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 mt-6">
          <button className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium hover:opacity-90">
            <Wrench className="w-4 h-4" />
            Creer Ordre de Travail
          </button>
          <button className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-industrial-darker text-gray-300 border border-industrial-border hover:border-industrial-accent/30">
            <Eye className="w-4 h-4" />
            Voir dans Grafana
          </button>
          <button className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-industrial-darker text-gray-300 border border-industrial-border hover:border-industrial-accent/30">
            <Database className="w-4 h-4" />
            Exporter Donnees
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}

// Main Component
function IndustrialObservabilityView() {
  const { t } = useI18n()
  const [equipments, setEquipments] = useState([])
  const [selectedEquipment, setSelectedEquipment] = useState(null)
  const [filterLevel, setFilterLevel] = useState(null)
  const [filterStatus, setFilterStatus] = useState(null)
  const [viewMode, setViewMode] = useState('grid') // grid | list | hierarchy
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Load and refresh data
  useEffect(() => {
    setEquipments(generateEquipmentData())

    if (autoRefresh) {
      const interval = setInterval(() => {
        setEquipments(generateEquipmentData())
      }, 5000)
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  // Calculate stats
  const stats = {
    total: equipments.length,
    optimal: equipments.filter(e => e.status === 'optimal').length,
    normal: equipments.filter(e => e.status === 'normal').length,
    degraded: equipments.filter(e => e.status === 'degraded').length,
    critical: equipments.filter(e => e.status === 'critical').length,
    alerts: equipments.reduce((sum, e) => sum + e.alerts.length, 0),
    avgHealth: equipments.reduce((sum, e) => sum + e.health, 0) / equipments.length,
    lowRul: equipments.filter(e => e.rul < 200).length
  }

  // Filter equipments
  const filteredEquipments = equipments.filter(e => {
    if (filterLevel !== null && e.level !== filterLevel) return false
    if (filterStatus && e.status !== filterStatus) return false
    return true
  })

  // Group by level for hierarchy view
  const equipmentsByLevel = Object.values(ISA95_LEVELS).map(level => ({
    ...level,
    equipments: filteredEquipments.filter(e => e.level === level.id),
    alertCount: filteredEquipments.filter(e => e.level === level.id && e.alerts.length > 0).length
  }))

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center">
              <Factory className="w-5 h-5 text-white" />
            </div>
            Observabilite Industrielle
          </h1>
          <p className="text-gray-400 mt-1">
            Supervision temps reel des equipements et processus industriels (ISA-95)
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Auto refresh toggle */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${
              autoRefresh
                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                : 'bg-industrial-card text-gray-400 border border-industrial-border'
            }`}
          >
            {autoRefresh ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
            Auto-refresh
          </button>

          {/* View mode */}
          <div className="flex items-center rounded-lg bg-industrial-card border border-industrial-border">
            {['grid', 'list', 'hierarchy'].map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-3 py-2 text-sm transition-all ${
                  viewMode === mode
                    ? 'bg-cyan-500/20 text-cyan-400'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {mode === 'grid' ? 'Grille' : mode === 'list' ? 'Liste' : 'Hierarchie'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <KPICard
          title="Equipements Totaux"
          value={stats.total}
          unit=""
          icon={Box}
          color="from-cyan-500 to-blue-600"
        />
        <KPICard
          title="Sante Moyenne"
          value={stats.avgHealth.toFixed(1)}
          unit="%"
          icon={Activity}
          trend="up"
          trendValue="2.3"
          color="from-green-500 to-emerald-600"
        />
        <KPICard
          title="En Etat Optimal"
          value={stats.optimal}
          unit=""
          icon={CheckCircle2}
          color="from-emerald-500 to-green-600"
        />
        <KPICard
          title="Alertes Actives"
          value={stats.alerts}
          unit=""
          icon={AlertTriangle}
          color="from-amber-500 to-orange-600"
        />
        <KPICard
          title="Degradation"
          value={stats.degraded + stats.critical}
          unit=""
          icon={TrendingDown}
          color="from-red-500 to-pink-600"
        />
        <KPICard
          title="Maintenance Urgente"
          value={stats.lowRul}
          unit=""
          icon={Wrench}
          subtitle="RUL < 200h"
          color="from-purple-500 to-indigo-600"
        />
      </div>

      {/* ISA-95 Level Overview */}
      <div className="grid grid-cols-5 gap-3">
        {Object.values(ISA95_LEVELS).map((level) => {
          const levelEquipments = equipments.filter(e => e.level === level.id)
          const alertCount = levelEquipments.filter(e => e.alerts.length > 0).length
          return (
            <button
              key={level.id}
              onClick={() => setFilterLevel(filterLevel === level.id ? null : level.id)}
              className={`transition-all ${filterLevel === level.id ? 'ring-2 ring-cyan-500 ring-offset-2 ring-offset-industrial-darker rounded-lg' : ''}`}
            >
              <ISA95LevelCard
                level={level}
                equipmentCount={levelEquipments.length}
                alertCount={alertCount}
              />
            </button>
          )
        })}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-400">Filtrer par statut:</span>
        {['optimal', 'normal', 'degraded', 'critical'].map((status) => (
          <button
            key={status}
            onClick={() => setFilterStatus(filterStatus === status ? null : status)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filterStatus === status
                ? status === 'optimal' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                  status === 'normal' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' :
                  status === 'degraded' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                  'bg-red-500/20 text-red-400 border border-red-500/30'
                : 'bg-industrial-card text-gray-400 border border-industrial-border hover:border-industrial-accent/30'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
        {(filterLevel !== null || filterStatus) && (
          <button
            onClick={() => { setFilterLevel(null); setFilterStatus(null) }}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs text-gray-400 hover:text-white bg-industrial-card border border-industrial-border"
          >
            <RotateCcw className="w-3 h-3" />
            Reset
          </button>
        )}
      </div>

      {/* Equipment Grid/List */}
      {viewMode === 'hierarchy' ? (
        <div className="space-y-6">
          {equipmentsByLevel.map((level) => (
            <div key={level.id}>
              <div className="flex items-center gap-2 mb-3">
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${level.color} flex items-center justify-center`}>
                  <level.icon className="w-4 h-4 text-white" />
                </div>
                <h3 className={`font-semibold ${level.textColor}`}>{level.name}</h3>
                <span className="text-xs text-gray-500">({level.equipments.length} equipements)</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 pl-10">
                {level.equipments.map((equipment) => (
                  <EquipmentCard
                    key={equipment.id}
                    equipment={equipment}
                    onClick={setSelectedEquipment}
                  />
                ))}
                {level.equipments.length === 0 && (
                  <p className="text-gray-500 text-sm">Aucun equipement a ce niveau</p>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className={`grid gap-4 ${
          viewMode === 'grid'
            ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
            : 'grid-cols-1'
        }`}>
          {filteredEquipments.map((equipment) => (
            <EquipmentCard
              key={equipment.id}
              equipment={equipment}
              onClick={setSelectedEquipment}
            />
          ))}
        </div>
      )}

      {/* Equipment Detail Modal */}
      <AnimatePresence>
        {selectedEquipment && (
          <EquipmentDetailModal
            equipment={selectedEquipment}
            onClose={() => setSelectedEquipment(null)}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

export default IndustrialObservabilityView
