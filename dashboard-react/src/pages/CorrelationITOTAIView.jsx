import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Activity,
  Server,
  Factory,
  Cpu,
  Network,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Eye,
  Layers,
  Target,
  RefreshCw,
  ChevronRight,
  ArrowRight,
  ArrowDown,
  ArrowUp,
  Zap,
  Database,
  Shield,
  Brain,
  GitBranch,
  Link,
  Unlink,
  CircuitBoard,
  Workflow,
  LineChart,
  Timer,
  Box,
  Radio,
  Gauge,
  Thermometer,
  Search,
  Filter,
  Play,
  Pause,
  Settings,
  Info,
  HelpCircle
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
  Sankey,
  ScatterChart,
  Scatter,
  ZAxis,
  Cell,
  ReferenceLine
} from 'recharts'

// Domain definitions
const DOMAINS = {
  IT: {
    id: 'it',
    name: 'IT (Infrastructure)',
    icon: Server,
    color: 'from-blue-500 to-cyan-600',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    textColor: 'text-blue-400',
    metrics: ['cpu_usage', 'memory_usage', 'disk_io', 'network_latency', 'error_rate', 'response_time']
  },
  OT: {
    id: 'ot',
    name: 'OT (Operations)',
    icon: Factory,
    color: 'from-green-500 to-emerald-600',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    textColor: 'text-green-400',
    metrics: ['oee', 'cycle_time', 'temperature', 'vibration', 'pressure', 'production_rate']
  },
  AI: {
    id: 'ai',
    name: 'AI (Intelligence)',
    icon: Brain,
    color: 'from-purple-500 to-pink-600',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30',
    textColor: 'text-purple-400',
    metrics: ['model_accuracy', 'inference_latency', 'prediction_drift', 'token_usage', 'anomaly_score', 'confidence']
  }
}

// Known correlation patterns (causal knowledge base)
const CORRELATION_PATTERNS = [
  {
    id: 'it_database_ot_mes',
    name: 'Base de donnees -> MES',
    description: 'Latence BDD impacte le temps de cycle MES',
    source: { domain: 'it', metric: 'response_time', component: 'PostgreSQL' },
    target: { domain: 'ot', metric: 'cycle_time', component: 'MES-Server' },
    correlation: 0.87,
    lag: 30, // seconds
    impact: 'high',
    causality: 'confirmed'
  },
  {
    id: 'ot_temp_ai_drift',
    name: 'Temperature -> Derive IA',
    description: 'Variations temperature causent derive du modele predictif',
    source: { domain: 'ot', metric: 'temperature', component: 'Moteur-Principal' },
    target: { domain: 'ai', metric: 'prediction_drift', component: 'RUL-Model' },
    correlation: 0.72,
    lag: 120,
    impact: 'medium',
    causality: 'probable'
  },
  {
    id: 'ai_anomaly_it_alert',
    name: 'Anomalie IA -> Alerte IT',
    description: 'Detection anomalie declenche alertes monitoring',
    source: { domain: 'ai', metric: 'anomaly_score', component: 'AnomalyDetector' },
    target: { domain: 'it', metric: 'alert_count', component: 'Prometheus' },
    correlation: 0.95,
    lag: 5,
    impact: 'high',
    causality: 'confirmed'
  },
  {
    id: 'it_cpu_ot_scada',
    name: 'CPU Serveur -> SCADA',
    description: 'Saturation CPU degrade rafraichissement SCADA',
    source: { domain: 'it', metric: 'cpu_usage', component: 'SCADA-Server' },
    target: { domain: 'ot', metric: 'refresh_rate', component: 'SCADA-HMI' },
    correlation: -0.83,
    lag: 10,
    impact: 'critical',
    causality: 'confirmed'
  },
  {
    id: 'ot_vibration_ai_prediction',
    name: 'Vibration -> Prediction RUL',
    description: 'Augmentation vibration reduit prediction RUL',
    source: { domain: 'ot', metric: 'vibration', component: 'Pompe-Hydraulique' },
    target: { domain: 'ai', metric: 'rul_prediction', component: 'RUL-Model' },
    correlation: -0.91,
    lag: 0,
    impact: 'high',
    causality: 'confirmed'
  },
  {
    id: 'ai_inference_it_memory',
    name: 'Inference IA -> Memoire',
    description: 'Charge inference impacte consommation memoire',
    source: { domain: 'ai', metric: 'inference_count', component: 'ML-Service' },
    target: { domain: 'it', metric: 'memory_usage', component: 'ML-Server' },
    correlation: 0.78,
    lag: 2,
    impact: 'medium',
    causality: 'confirmed'
  },
  {
    id: 'it_network_ot_opcua',
    name: 'Reseau -> OPC-UA',
    description: 'Latence reseau impacte communication OPC-UA',
    source: { domain: 'it', metric: 'network_latency', component: 'OT-Gateway' },
    target: { domain: 'ot', metric: 'opcua_timeout', component: 'OPC-UA-Server' },
    correlation: 0.89,
    lag: 0,
    impact: 'critical',
    causality: 'confirmed'
  },
  {
    id: 'ot_oee_ai_forecast',
    name: 'OEE -> Prevision Production',
    description: 'OEE reel alimente modele de prevision',
    source: { domain: 'ot', metric: 'oee', component: 'Production-Line-1' },
    target: { domain: 'ai', metric: 'forecast_accuracy', component: 'Production-Forecast' },
    correlation: 0.85,
    lag: 300,
    impact: 'medium',
    causality: 'confirmed'
  }
]

// Generate mock time series data
const generateTimeSeriesData = (baseValue, variance, length = 60) => {
  return Array.from({ length }, (_, i) => {
    const trend = Math.sin(i / 10) * variance * 0.3
    const noise = (Math.random() - 0.5) * variance
    return {
      time: i,
      value: baseValue + trend + noise
    }
  })
}

// Generate correlated events
const generateCorrelatedEvents = () => {
  const now = Date.now()
  const events = []

  // IT events
  events.push({
    id: 'evt-1',
    domain: 'it',
    timestamp: now - 180000,
    type: 'spike',
    metric: 'cpu_usage',
    component: 'SCADA-Server',
    value: 92,
    severity: 'warning',
    correlatedWith: ['evt-2', 'evt-3']
  })

  // OT events (caused by IT)
  events.push({
    id: 'evt-2',
    domain: 'ot',
    timestamp: now - 170000,
    type: 'degradation',
    metric: 'refresh_rate',
    component: 'SCADA-HMI',
    value: 0.5,
    severity: 'warning',
    correlatedWith: ['evt-1']
  })

  events.push({
    id: 'evt-3',
    domain: 'ot',
    timestamp: now - 165000,
    type: 'alert',
    metric: 'cycle_time',
    component: 'MES-Server',
    value: 45,
    severity: 'high',
    correlatedWith: ['evt-1']
  })

  // AI detection
  events.push({
    id: 'evt-4',
    domain: 'ai',
    timestamp: now - 160000,
    type: 'anomaly_detected',
    metric: 'anomaly_score',
    component: 'AnomalyDetector',
    value: 0.87,
    severity: 'info',
    correlatedWith: ['evt-1', 'evt-2', 'evt-3']
  })

  // Recent independent events
  events.push({
    id: 'evt-5',
    domain: 'ot',
    timestamp: now - 60000,
    type: 'threshold',
    metric: 'temperature',
    component: 'Moteur-Principal',
    value: 78,
    severity: 'warning',
    correlatedWith: []
  })

  events.push({
    id: 'evt-6',
    domain: 'ai',
    timestamp: now - 55000,
    type: 'drift_detected',
    metric: 'prediction_drift',
    component: 'RUL-Model',
    value: 0.12,
    severity: 'low',
    correlatedWith: ['evt-5']
  })

  return events.sort((a, b) => b.timestamp - a.timestamp)
}

// Domain Card Component
function DomainCard({ domain, metrics, isSelected, onClick }) {
  const Icon = domain.icon

  return (
    <motion.button
      onClick={() => onClick(domain.id)}
      className={`p-4 rounded-xl border-2 text-left transition-all w-full ${
        isSelected
          ? `${domain.bgColor} ${domain.borderColor}`
          : 'bg-industrial-card/50 border-industrial-border hover:border-industrial-accent/30'
      }`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${domain.color} flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className={`font-semibold ${isSelected ? domain.textColor : 'text-white'}`}>
            {domain.name}
          </h3>
          <p className="text-xs text-gray-400">{metrics.healthy}/{metrics.total} metriques OK</p>
        </div>
      </div>

      {/* Mini health bars */}
      <div className="space-y-1.5">
        {domain.metrics.slice(0, 3).map((metric) => (
          <div key={metric} className="flex items-center gap-2">
            <span className="text-[10px] text-gray-500 w-20 truncate">{metric.replace('_', ' ')}</span>
            <div className="flex-1 h-1.5 bg-industrial-darker rounded-full overflow-hidden">
              <motion.div
                className={`h-full rounded-full ${
                  Math.random() > 0.2 ? 'bg-green-500' : 'bg-amber-500'
                }`}
                initial={{ width: 0 }}
                animate={{ width: `${60 + Math.random() * 40}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </motion.button>
  )
}

// Correlation Pattern Card
function CorrelationCard({ pattern, onClick }) {
  const sourceDomain = DOMAINS[pattern.source.domain.toUpperCase()]
  const targetDomain = DOMAINS[pattern.target.domain.toUpperCase()]
  const SourceIcon = sourceDomain?.icon || Box
  const TargetIcon = targetDomain?.icon || Box

  const impactColors = {
    critical: 'text-red-400 bg-red-500/10',
    high: 'text-orange-400 bg-orange-500/10',
    medium: 'text-amber-400 bg-amber-500/10',
    low: 'text-green-400 bg-green-500/10'
  }

  return (
    <motion.button
      onClick={() => onClick(pattern)}
      className="w-full p-4 rounded-xl bg-industrial-card/50 border border-industrial-border hover:border-cyan-500/30 text-left transition-all"
      whileHover={{ scale: 1.01, y: -2 }}
      whileTap={{ scale: 0.99 }}
    >
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold text-white text-sm">{pattern.name}</h4>
        <span className={`text-xs px-2 py-0.5 rounded-full ${impactColors[pattern.impact]}`}>
          {pattern.impact}
        </span>
      </div>

      {/* Visual flow */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${sourceDomain?.color} flex items-center justify-center`}>
            <SourceIcon className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-xs text-gray-400">{pattern.source.metric}</p>
            <p className="text-[10px] text-gray-500">{pattern.source.component}</p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <div className="w-8 h-0.5 bg-gradient-to-r from-gray-600 to-cyan-500" />
          <ArrowRight className="w-4 h-4 text-cyan-400" />
          <div className="w-8 h-0.5 bg-gradient-to-r from-cyan-500 to-gray-600" />
        </div>

        <div className="flex items-center gap-2">
          <div>
            <p className="text-xs text-gray-400 text-right">{pattern.target.metric}</p>
            <p className="text-[10px] text-gray-500 text-right">{pattern.target.component}</p>
          </div>
          <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${targetDomain?.color} flex items-center justify-center`}>
            <TargetIcon className="w-4 h-4 text-white" />
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-gray-500">
          Correlation: <span className={`font-mono ${Math.abs(pattern.correlation) > 0.8 ? 'text-cyan-400' : 'text-gray-400'}`}>
            {(pattern.correlation * 100).toFixed(0)}%
          </span>
        </span>
        <span className="text-gray-500">
          Lag: <span className="font-mono text-gray-400">{pattern.lag}s</span>
        </span>
        <span className={`flex items-center gap-1 ${
          pattern.causality === 'confirmed' ? 'text-green-400' : 'text-amber-400'
        }`}>
          {pattern.causality === 'confirmed' ? <CheckCircle2 className="w-3 h-3" /> : <HelpCircle className="w-3 h-3" />}
          {pattern.causality}
        </span>
      </div>
    </motion.button>
  )
}

// Event Timeline Component
function EventTimeline({ events, selectedEvent, onSelectEvent }) {
  const domainColors = {
    it: 'bg-blue-500',
    ot: 'bg-green-500',
    ai: 'bg-purple-500'
  }

  const severityColors = {
    critical: 'border-red-500',
    high: 'border-orange-500',
    warning: 'border-amber-500',
    low: 'border-yellow-500',
    info: 'border-cyan-500'
  }

  return (
    <div className="space-y-2">
      {events.map((event, idx) => (
        <motion.button
          key={event.id}
          onClick={() => onSelectEvent(event)}
          className={`w-full p-3 rounded-lg text-left transition-all border-l-4 ${severityColors[event.severity]} ${
            selectedEvent?.id === event.id
              ? 'bg-cyan-500/10 border border-cyan-500/30'
              : 'bg-industrial-card/50 border border-industrial-border hover:border-industrial-accent/30'
          }`}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: idx * 0.05 }}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${domainColors[event.domain]}`} />
              <span className="text-xs font-mono text-gray-400">
                {new Date(event.timestamp).toLocaleTimeString()}
              </span>
            </div>
            {event.correlatedWith.length > 0 && (
              <span className="flex items-center gap-1 text-[10px] text-cyan-400">
                <Link className="w-3 h-3" />
                {event.correlatedWith.length}
              </span>
            )}
          </div>
          <p className="text-sm text-white mt-1">{event.type}: {event.metric}</p>
          <p className="text-xs text-gray-500">{event.component}</p>
        </motion.button>
      ))}
    </div>
  )
}

// Correlation Detail Modal
function CorrelationDetailModal({ pattern, onClose }) {
  const sourceDomain = DOMAINS[pattern.source.domain.toUpperCase()]
  const targetDomain = DOMAINS[pattern.target.domain.toUpperCase()]
  const SourceIcon = sourceDomain?.icon || Box
  const TargetIcon = targetDomain?.icon || Box

  // Generate correlated time series
  const sourceData = generateTimeSeriesData(50, 20)
  const targetData = sourceData.map((d, i) => ({
    time: d.time,
    value: d.value * pattern.correlation + (Math.random() - 0.5) * 10
  }))

  const combinedData = sourceData.map((d, i) => ({
    time: d.time,
    source: d.value,
    target: targetData[i].value
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
          <div>
            <h2 className="text-xl font-bold text-white">{pattern.name}</h2>
            <p className="text-sm text-gray-400 mt-1">{pattern.description}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-industrial-darker text-gray-400 hover:text-white"
          >
            <XCircle className="w-5 h-5" />
          </button>
        </div>

        {/* Visual Flow */}
        <div className="flex items-center justify-center gap-4 mb-6 p-6 bg-industrial-darker rounded-xl">
          <div className="text-center">
            <div className={`w-16 h-16 mx-auto rounded-xl bg-gradient-to-br ${sourceDomain?.color} flex items-center justify-center mb-2`}>
              <SourceIcon className="w-8 h-8 text-white" />
            </div>
            <p className={`text-sm font-semibold ${sourceDomain?.textColor}`}>{sourceDomain?.name}</p>
            <p className="text-xs text-gray-400">{pattern.source.metric}</p>
            <p className="text-xs text-gray-500">{pattern.source.component}</p>
          </div>

          <div className="flex flex-col items-center">
            <div className="flex items-center gap-2">
              <div className="w-20 h-1 bg-gradient-to-r from-blue-500 via-cyan-500 to-purple-500 rounded" />
              <motion.div
                animate={{ x: [0, 10, 0] }}
                transition={{ repeat: Infinity, duration: 1.5 }}
              >
                <ArrowRight className="w-6 h-6 text-cyan-400" />
              </motion.div>
              <div className="w-20 h-1 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 rounded" />
            </div>
            <div className="mt-2 text-center">
              <p className="text-xs text-gray-400">Lag: {pattern.lag}s</p>
              <p className={`text-lg font-bold ${pattern.correlation > 0 ? 'text-green-400' : 'text-red-400'}`}>
                {pattern.correlation > 0 ? '+' : ''}{(pattern.correlation * 100).toFixed(0)}%
              </p>
            </div>
          </div>

          <div className="text-center">
            <div className={`w-16 h-16 mx-auto rounded-xl bg-gradient-to-br ${targetDomain?.color} flex items-center justify-center mb-2`}>
              <TargetIcon className="w-8 h-8 text-white" />
            </div>
            <p className={`text-sm font-semibold ${targetDomain?.textColor}`}>{targetDomain?.name}</p>
            <p className="text-xs text-gray-400">{pattern.target.metric}</p>
            <p className="text-xs text-gray-500">{pattern.target.component}</p>
          </div>
        </div>

        {/* Correlation Stats */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="p-4 rounded-xl bg-industrial-darker">
            <p className="text-xs text-gray-400 mb-1">Coefficient</p>
            <p className={`text-2xl font-bold ${Math.abs(pattern.correlation) > 0.8 ? 'text-cyan-400' : 'text-gray-300'}`}>
              {pattern.correlation.toFixed(2)}
            </p>
          </div>
          <div className="p-4 rounded-xl bg-industrial-darker">
            <p className="text-xs text-gray-400 mb-1">Delai Causal</p>
            <p className="text-2xl font-bold text-white">{pattern.lag}<span className="text-sm text-gray-400">s</span></p>
          </div>
          <div className="p-4 rounded-xl bg-industrial-darker">
            <p className="text-xs text-gray-400 mb-1">Impact</p>
            <p className={`text-2xl font-bold capitalize ${
              pattern.impact === 'critical' ? 'text-red-400' :
              pattern.impact === 'high' ? 'text-orange-400' :
              pattern.impact === 'medium' ? 'text-amber-400' : 'text-green-400'
            }`}>
              {pattern.impact}
            </p>
          </div>
          <div className="p-4 rounded-xl bg-industrial-darker">
            <p className="text-xs text-gray-400 mb-1">Causalite</p>
            <p className={`text-2xl font-bold capitalize ${
              pattern.causality === 'confirmed' ? 'text-green-400' : 'text-amber-400'
            }`}>
              {pattern.causality}
            </p>
          </div>
        </div>

        {/* Time Series Chart */}
        <div className="p-4 rounded-xl bg-industrial-darker mb-6">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <LineChart className="w-4 h-4 text-cyan-400" />
            Correlation Temporelle
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={combinedData}>
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
                <Area
                  type="monotone"
                  dataKey="source"
                  stroke="#3B82F6"
                  fill="#3B82F6"
                  fillOpacity={0.2}
                  strokeWidth={2}
                  name={pattern.source.metric}
                />
                <Area
                  type="monotone"
                  dataKey="target"
                  stroke="#8B5CF6"
                  fill="#8B5CF6"
                  fillOpacity={0.2}
                  strokeWidth={2}
                  name={pattern.target.metric}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recommendations */}
        <div className="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/30">
          <h3 className="text-sm font-semibold text-cyan-400 mb-2 flex items-center gap-2">
            <Info className="w-4 h-4" />
            Recommandations
          </h3>
          <ul className="text-sm text-gray-300 space-y-1">
            <li>- Configurer une alerte preemptive sur {pattern.source.metric} pour anticiper l'impact</li>
            <li>- Ajouter un dashboard de correlation pour surveiller cette relation</li>
            <li>- Considerer l'ajout d'un buffer/cache pour reduire la propagation</li>
          </ul>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 mt-6">
          <button className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium hover:opacity-90">
            <Target className="w-4 h-4" />
            Creer Regle d'Alerte
          </button>
          <button className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-industrial-darker text-gray-300 border border-industrial-border hover:border-industrial-accent/30">
            <Eye className="w-4 h-4" />
            Voir dans Grafana
          </button>
          <button className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-industrial-darker text-gray-300 border border-industrial-border hover:border-industrial-accent/30">
            <Database className="w-4 h-4" />
            Exporter Analyse
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}

// Cross-Domain Metrics Scatter
function CrossDomainScatter({ data }) {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="x" name="IT Metric" stroke="#6B7280" fontSize={10} />
          <YAxis dataKey="y" name="OT Metric" stroke="#6B7280" fontSize={10} />
          <ZAxis dataKey="z" range={[50, 400]} name="Impact" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '8px'
            }}
          />
          <Scatter name="Correlations" data={data} fill="#06B6D4">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.correlation > 0.8 ? '#10B981' : entry.correlation > 0.5 ? '#F59E0B' : '#EF4444'} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}

// Main Component
function CorrelationITOTAIView() {
  const { t } = useI18n()
  const [selectedDomains, setSelectedDomains] = useState(['it', 'ot', 'ai'])
  const [selectedPattern, setSelectedPattern] = useState(null)
  const [events, setEvents] = useState([])
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [autoAnalyze, setAutoAnalyze] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  // Load events
  useEffect(() => {
    setEvents(generateCorrelatedEvents())

    if (autoAnalyze) {
      const interval = setInterval(() => {
        setEvents(generateCorrelatedEvents())
      }, 10000)
      return () => clearInterval(interval)
    }
  }, [autoAnalyze])

  // Filter patterns based on selected domains
  const filteredPatterns = CORRELATION_PATTERNS.filter(p =>
    selectedDomains.includes(p.source.domain) || selectedDomains.includes(p.target.domain)
  ).filter(p =>
    searchQuery === '' ||
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Generate scatter data
  const scatterData = filteredPatterns.map(p => ({
    x: 50 + Math.random() * 50,
    y: 50 + Math.random() * 50,
    z: Math.abs(p.correlation) * 100,
    correlation: Math.abs(p.correlation),
    name: p.name
  }))

  // Domain metrics mock
  const domainMetrics = {
    it: { total: 6, healthy: 5 },
    ot: { total: 6, healthy: 4 },
    ai: { total: 6, healthy: 6 }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 via-purple-500 to-pink-500 flex items-center justify-center">
              <Layers className="w-5 h-5 text-white" />
            </div>
            Correlation IT-OT-IA
          </h1>
          <p className="text-gray-400 mt-1">
            Analyse des correlations et dependances entre domaines IT, OT et IA
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 rounded-lg bg-industrial-card border border-industrial-border text-white text-sm focus:outline-none focus:border-cyan-500/50"
            />
          </div>

          {/* Auto analyze toggle */}
          <button
            onClick={() => setAutoAnalyze(!autoAnalyze)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${
              autoAnalyze
                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                : 'bg-industrial-card text-gray-400 border border-industrial-border'
            }`}
          >
            {autoAnalyze ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
            Auto-analyse
          </button>
        </div>
      </div>

      {/* Domain Selection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.values(DOMAINS).map((domain) => (
          <DomainCard
            key={domain.id}
            domain={domain}
            metrics={domainMetrics[domain.id]}
            isSelected={selectedDomains.includes(domain.id)}
            onClick={(id) => {
              setSelectedDomains(prev =>
                prev.includes(id)
                  ? prev.filter(d => d !== id)
                  : [...prev, id]
              )
            }}
          />
        ))}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Correlation Patterns */}
        <div className="xl:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-cyan-400" />
              Patterns de Correlation ({filteredPatterns.length})
            </h2>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filteredPatterns.map((pattern) => (
              <CorrelationCard
                key={pattern.id}
                pattern={pattern}
                onClick={setSelectedPattern}
              />
            ))}
          </div>

          {/* Cross-Domain Scatter */}
          <div className="p-4 rounded-xl bg-industrial-card/50 border border-industrial-border">
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <Activity className="w-4 h-4 text-purple-400" />
              Matrice de Correlation Inter-Domaines
            </h3>
            <CrossDomainScatter data={scatterData} />
          </div>
        </div>

        {/* Event Timeline */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Clock className="w-5 h-5 text-amber-400" />
            Evenements Correles
          </h2>

          <EventTimeline
            events={events}
            selectedEvent={selectedEvent}
            onSelectEvent={setSelectedEvent}
          />

          {/* Legend */}
          <div className="p-4 rounded-xl bg-industrial-card/50 border border-industrial-border">
            <h3 className="text-xs font-semibold text-gray-400 mb-2">Legende</h3>
            <div className="space-y-2 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-500" />
                <span className="text-gray-400">IT (Infrastructure)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-gray-400">OT (Operations)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-purple-500" />
                <span className="text-gray-400">AI (Intelligence)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Correlation Detail Modal */}
      <AnimatePresence>
        {selectedPattern && (
          <CorrelationDetailModal
            pattern={selectedPattern}
            onClose={() => setSelectedPattern(null)}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

export default CorrelationITOTAIView
