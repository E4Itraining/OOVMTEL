import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield,
  AlertTriangle,
  Lock,
  Unlock,
  Eye,
  EyeOff,
  Server,
  Network,
  Factory,
  Radio,
  Activity,
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Target,
  Layers,
  RefreshCw,
  ChevronRight,
  ChevronDown,
  Settings,
  FileCheck,
  Zap,
  Wifi,
  WifiOff,
  Globe,
  Database,
  HardDrive,
  Cpu,
  Box,
  ArrowRight,
  ArrowUp,
  ArrowDown,
  Search,
  Filter,
  Download,
  Bell,
  BellOff,
  ShieldAlert,
  ShieldCheck,
  ShieldOff,
  Fingerprint,
  Key,
  UserX,
  Users,
  Bug,
  Skull,
  AlertOctagon,
  Terminal,
  Code,
  FileWarning,
  Gauge,
  Timer,
  Map,
  Crosshair
} from 'lucide-react'
import { useI18n } from '../i18n'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts'

// IEC 62443 Security Levels
const SECURITY_LEVELS = {
  SL1: { name: 'SL1 - Base', description: 'Protection contre intrusions accidentelles', color: 'text-green-400', bg: 'bg-green-500/20' },
  SL2: { name: 'SL2 - Avance', description: 'Protection contre attaques simples', color: 'text-cyan-400', bg: 'bg-cyan-500/20' },
  SL3: { name: 'SL3 - Renforce', description: 'Protection contre attaques sophistiquees', color: 'text-amber-400', bg: 'bg-amber-500/20' },
  SL4: { name: 'SL4 - Maximum', description: 'Protection contre attaques etatiques', color: 'text-red-400', bg: 'bg-red-500/20' }
}

// MITRE ATT&CK for ICS Tactics
const MITRE_ICS_TACTICS = [
  { id: 'initial-access', name: 'Acces Initial', icon: Key, attacks: 12 },
  { id: 'execution', name: 'Execution', icon: Terminal, attacks: 8 },
  { id: 'persistence', name: 'Persistance', icon: Database, attacks: 5 },
  { id: 'privilege-escalation', name: 'Escalade Privileges', icon: ArrowUp, attacks: 3 },
  { id: 'evasion', name: 'Evasion', icon: EyeOff, attacks: 4 },
  { id: 'discovery', name: 'Decouverte', icon: Search, attacks: 15 },
  { id: 'lateral-movement', name: 'Mouvement Lateral', icon: ArrowRight, attacks: 7 },
  { id: 'collection', name: 'Collection', icon: Database, attacks: 6 },
  { id: 'command-control', name: 'C2', icon: Radio, attacks: 2 },
  { id: 'inhibit-response', name: 'Inhibition Reponse', icon: ShieldOff, attacks: 1 },
  { id: 'impair-process', name: 'Alteration Process', icon: AlertOctagon, attacks: 0 },
  { id: 'impact', name: 'Impact', icon: Skull, attacks: 0 }
]

// Zone Configuration (Purdue Model / IEC 62443)
const ZONES = [
  {
    id: 'zone-5',
    name: 'Zone 5 - Enterprise',
    level: 5,
    color: 'from-blue-500 to-indigo-600',
    bgColor: 'bg-blue-500/10',
    textColor: 'text-blue-400',
    assets: ['ERP', 'Email', 'Web', 'AD'],
    securityLevel: 'SL2',
    threats: 8,
    vulnerabilities: 12
  },
  {
    id: 'zone-4',
    name: 'Zone 4 - Business Planning',
    level: 4,
    color: 'from-cyan-500 to-blue-600',
    bgColor: 'bg-cyan-500/10',
    textColor: 'text-cyan-400',
    assets: ['MES', 'Historian', 'BI'],
    securityLevel: 'SL2',
    threats: 5,
    vulnerabilities: 8
  },
  {
    id: 'zone-35',
    name: 'Zone 3.5 - DMZ Industrielle',
    level: 3.5,
    color: 'from-purple-500 to-pink-600',
    bgColor: 'bg-purple-500/10',
    textColor: 'text-purple-400',
    assets: ['Data Diode', 'Firewall', 'Jump Server'],
    securityLevel: 'SL3',
    threats: 2,
    vulnerabilities: 3
  },
  {
    id: 'zone-3',
    name: 'Zone 3 - Site Operations',
    level: 3,
    color: 'from-green-500 to-emerald-600',
    bgColor: 'bg-green-500/10',
    textColor: 'text-green-400',
    assets: ['SCADA Server', 'HMI', 'Engineering WS'],
    securityLevel: 'SL3',
    threats: 3,
    vulnerabilities: 5
  },
  {
    id: 'zone-2',
    name: 'Zone 2 - Area Control',
    level: 2,
    color: 'from-amber-500 to-orange-600',
    bgColor: 'bg-amber-500/10',
    textColor: 'text-amber-400',
    assets: ['PLC', 'DCS', 'RTU'],
    securityLevel: 'SL3',
    threats: 1,
    vulnerabilities: 4
  },
  {
    id: 'zone-1',
    name: 'Zone 1 - Basic Control',
    level: 1,
    color: 'from-orange-500 to-red-600',
    bgColor: 'bg-orange-500/10',
    textColor: 'text-orange-400',
    assets: ['Sensors', 'Actuators', 'I/O'],
    securityLevel: 'SL2',
    threats: 0,
    vulnerabilities: 2
  },
  {
    id: 'zone-0',
    name: 'Zone 0 - Process',
    level: 0,
    color: 'from-red-500 to-pink-600',
    bgColor: 'bg-red-500/10',
    textColor: 'text-red-400',
    assets: ['Field Devices', 'Instruments'],
    securityLevel: 'SL1',
    threats: 0,
    vulnerabilities: 1
  }
]

// Security Events
const generateSecurityEvents = () => {
  const eventTypes = [
    { type: 'auth_failure', severity: 'warning', icon: UserX },
    { type: 'port_scan', severity: 'high', icon: Search },
    { type: 'modbus_anomaly', severity: 'critical', icon: AlertOctagon },
    { type: 'firmware_change', severity: 'high', icon: Code },
    { type: 'new_device', severity: 'warning', icon: Wifi },
    { type: 'protocol_violation', severity: 'high', icon: FileWarning },
    { type: 'access_denied', severity: 'warning', icon: Lock },
    { type: 'config_change', severity: 'medium', icon: Settings }
  ]

  const zones = ['Zone 5', 'Zone 4', 'Zone 3.5', 'Zone 3', 'Zone 2']

  return Array.from({ length: 15 }, (_, i) => {
    const event = eventTypes[Math.floor(Math.random() * eventTypes.length)]
    return {
      id: `evt-${i}`,
      ...event,
      zone: zones[Math.floor(Math.random() * zones.length)],
      source: `192.168.${Math.floor(Math.random() * 10)}.${Math.floor(Math.random() * 255)}`,
      timestamp: Date.now() - i * 60000 * Math.random() * 10,
      details: `Evenement ${event.type} detecte`
    }
  }).sort((a, b) => b.timestamp - a.timestamp)
}

// Vulnerability data
const VULNERABILITIES = [
  { id: 'CVE-2024-1234', severity: 'critical', cvss: 9.8, asset: 'PLC Siemens S7-1500', zone: 'Zone 2', status: 'open', age: 5 },
  { id: 'CVE-2024-5678', severity: 'high', cvss: 8.2, asset: 'SCADA Server', zone: 'Zone 3', status: 'mitigated', age: 12 },
  { id: 'CVE-2023-9012', severity: 'high', cvss: 7.5, asset: 'Historian DB', zone: 'Zone 4', status: 'open', age: 45 },
  { id: 'CVE-2024-3456', severity: 'medium', cvss: 5.3, asset: 'HMI Panel', zone: 'Zone 3', status: 'patched', age: 3 },
  { id: 'CVE-2024-7890', severity: 'medium', cvss: 4.8, asset: 'Engineering WS', zone: 'Zone 3', status: 'open', age: 8 },
  { id: 'CVE-2024-2345', severity: 'low', cvss: 3.1, asset: 'RTU Modbus', zone: 'Zone 2', status: 'accepted', age: 60 }
]

// Security Score Card
function SecurityScoreCard({ title, score, maxScore, icon: Icon, color, trend }) {
  const percentage = (score / maxScore) * 100

  return (
    <motion.div
      className="p-4 rounded-xl bg-industrial-card/50 border border-industrial-border"
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-xs ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {trend > 0 ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
            {Math.abs(trend)}%
          </div>
        )}
      </div>
      <p className="text-xs text-gray-400 mb-1">{title}</p>
      <div className="flex items-end gap-2">
        <span className="text-2xl font-bold text-white">{score}</span>
        <span className="text-sm text-gray-400 mb-1">/{maxScore}</span>
      </div>
      <div className="h-1.5 bg-industrial-darker rounded-full overflow-hidden mt-2">
        <motion.div
          className={`h-full rounded-full ${
            percentage > 80 ? 'bg-green-500' :
            percentage > 60 ? 'bg-cyan-500' :
            percentage > 40 ? 'bg-amber-500' : 'bg-red-500'
          }`}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
        />
      </div>
    </motion.div>
  )
}

// Zone Security Card
function ZoneCard({ zone, isSelected, onClick }) {
  return (
    <motion.button
      onClick={() => onClick(zone)}
      className={`w-full p-4 rounded-xl text-left transition-all border-2 ${
        isSelected
          ? `${zone.bgColor} ${zone.textColor} border-current`
          : 'bg-industrial-card/50 border-industrial-border hover:border-industrial-accent/30'
      }`}
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${zone.color} flex items-center justify-center`}>
            <Shield className="w-4 h-4 text-white" />
          </div>
          <div>
            <h4 className={`font-semibold text-sm ${isSelected ? zone.textColor : 'text-white'}`}>
              {zone.name}
            </h4>
            <p className="text-[10px] text-gray-500">{zone.assets.join(', ')}</p>
          </div>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded ${SECURITY_LEVELS[zone.securityLevel].bg} ${SECURITY_LEVELS[zone.securityLevel].color}`}>
          {zone.securityLevel}
        </span>
      </div>

      <div className="flex items-center justify-between text-xs mt-3">
        <span className="flex items-center gap-1 text-amber-400">
          <AlertTriangle className="w-3 h-3" />
          {zone.threats} menaces
        </span>
        <span className="flex items-center gap-1 text-red-400">
          <Bug className="w-3 h-3" />
          {zone.vulnerabilities} vuln.
        </span>
      </div>
    </motion.button>
  )
}

// MITRE ATT&CK Heatmap
function MitreHeatmap({ tactics }) {
  return (
    <div className="grid grid-cols-4 gap-2">
      {tactics.map((tactic) => {
        const Icon = tactic.icon
        const intensity = Math.min(tactic.attacks / 15, 1)

        return (
          <motion.div
            key={tactic.id}
            className={`p-3 rounded-lg text-center transition-all cursor-pointer ${
              tactic.attacks > 10 ? 'bg-red-500/20 border border-red-500/30' :
              tactic.attacks > 5 ? 'bg-amber-500/20 border border-amber-500/30' :
              tactic.attacks > 0 ? 'bg-cyan-500/20 border border-cyan-500/30' :
              'bg-industrial-darker border border-industrial-border'
            }`}
            whileHover={{ scale: 1.05 }}
          >
            <Icon className={`w-5 h-5 mx-auto mb-1 ${
              tactic.attacks > 10 ? 'text-red-400' :
              tactic.attacks > 5 ? 'text-amber-400' :
              tactic.attacks > 0 ? 'text-cyan-400' :
              'text-gray-500'
            }`} />
            <p className="text-[10px] text-gray-400 truncate">{tactic.name}</p>
            <p className={`text-sm font-bold ${
              tactic.attacks > 10 ? 'text-red-400' :
              tactic.attacks > 5 ? 'text-amber-400' :
              tactic.attacks > 0 ? 'text-cyan-400' :
              'text-gray-500'
            }`}>{tactic.attacks}</p>
          </motion.div>
        )
      })}
    </div>
  )
}

// Security Event Row
function SecurityEventRow({ event, onClick }) {
  const Icon = event.icon
  const severityColors = {
    critical: 'text-red-400 bg-red-500/10 border-red-500/30',
    high: 'text-orange-400 bg-orange-500/10 border-orange-500/30',
    warning: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
    medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30',
    low: 'text-green-400 bg-green-500/10 border-green-500/30'
  }

  return (
    <motion.button
      onClick={() => onClick(event)}
      className={`w-full p-3 rounded-lg text-left transition-all border ${severityColors[event.severity]} hover:scale-[1.01]`}
      whileHover={{ x: 4 }}
    >
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${severityColors[event.severity]}`}>
          <Icon className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <p className="text-sm text-white font-medium truncate">{event.type.replace('_', ' ')}</p>
            <span className="text-[10px] text-gray-500">
              {new Date(event.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <span>{event.zone}</span>
            <span className="text-gray-600">|</span>
            <span className="font-mono">{event.source}</span>
          </div>
        </div>
      </div>
    </motion.button>
  )
}

// Vulnerability Table
function VulnerabilityTable({ vulnerabilities, onSelect }) {
  const severityColors = {
    critical: 'text-red-400',
    high: 'text-orange-400',
    medium: 'text-amber-400',
    low: 'text-green-400'
  }

  const statusColors = {
    open: 'bg-red-500/20 text-red-400',
    mitigated: 'bg-amber-500/20 text-amber-400',
    patched: 'bg-green-500/20 text-green-400',
    accepted: 'bg-gray-500/20 text-gray-400'
  }

  return (
    <div className="space-y-2">
      {vulnerabilities.map((vuln) => (
        <motion.button
          key={vuln.id}
          onClick={() => onSelect(vuln)}
          className="w-full p-3 rounded-lg bg-industrial-card/50 border border-industrial-border hover:border-industrial-accent/30 text-left transition-all"
          whileHover={{ x: 4 }}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-mono text-cyan-400">{vuln.id}</span>
            <span className={`text-xs px-2 py-0.5 rounded ${statusColors[vuln.status]}`}>
              {vuln.status}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-white">{vuln.asset}</p>
              <p className="text-xs text-gray-500">{vuln.zone}</p>
            </div>
            <div className="text-right">
              <p className={`text-lg font-bold ${severityColors[vuln.severity]}`}>{vuln.cvss}</p>
              <p className="text-[10px] text-gray-500">{vuln.age}j</p>
            </div>
          </div>
        </motion.button>
      ))}
    </div>
  )
}

// Network Topology Visualization
function NetworkTopology({ zones, selectedZone }) {
  return (
    <div className="relative h-96 bg-industrial-darker rounded-xl border border-industrial-border p-4 overflow-hidden">
      {/* Background grid */}
      <div className="absolute inset-0 opacity-10">
        <svg className="w-full h-full">
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.5" />
          </pattern>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      {/* Zones */}
      <div className="relative h-full flex flex-col justify-between">
        {zones.map((zone, idx) => {
          const isSelected = selectedZone?.id === zone.id
          const width = 100 - idx * 8

          return (
            <motion.div
              key={zone.id}
              className={`relative rounded-lg border-2 transition-all ${
                isSelected
                  ? `${zone.bgColor} border-current ${zone.textColor}`
                  : 'bg-industrial-card/30 border-industrial-border'
              }`}
              style={{ width: `${width}%`, marginLeft: `${idx * 4}%` }}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <div className="flex items-center justify-between p-2">
                <div className="flex items-center gap-2">
                  <div className={`w-6 h-6 rounded bg-gradient-to-br ${zone.color} flex items-center justify-center`}>
                    <span className="text-[10px] text-white font-bold">{zone.level}</span>
                  </div>
                  <span className={`text-xs font-medium ${isSelected ? zone.textColor : 'text-gray-400'}`}>
                    {zone.name}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {zone.threats > 0 && (
                    <span className="flex items-center gap-1 text-[10px] text-amber-400">
                      <AlertTriangle className="w-3 h-3" />
                      {zone.threats}
                    </span>
                  )}
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${SECURITY_LEVELS[zone.securityLevel].bg} ${SECURITY_LEVELS[zone.securityLevel].color}`}>
                    {zone.securityLevel}
                  </span>
                </div>
              </div>
            </motion.div>
          )
        })}

        {/* Data Diode indicator */}
        <motion.div
          className="absolute left-1/2 -translate-x-1/2 top-[45%]"
          animate={{ y: [0, -5, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
        >
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-purple-500/20 border border-purple-500/30">
            <Shield className="w-4 h-4 text-purple-400" />
            <span className="text-xs text-purple-400">Data Diode</span>
            <ArrowDown className="w-4 h-4 text-purple-400" />
          </div>
        </motion.div>
      </div>
    </div>
  )
}

// Compliance Radar
function ComplianceRadar() {
  const data = [
    { subject: 'IEC 62443', score: 78, fullMark: 100 },
    { subject: 'NIS 2', score: 85, fullMark: 100 },
    { subject: 'ISO 27001', score: 92, fullMark: 100 },
    { subject: 'NIST CSF', score: 70, fullMark: 100 },
    { subject: 'CIS Controls', score: 65, fullMark: 100 },
    { subject: 'SOC 2', score: 88, fullMark: 100 }
  ]

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data}>
          <PolarGrid stroke="#374151" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#9CA3AF', fontSize: 10 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#6B7280', fontSize: 8 }} />
          <Radar
            name="Score"
            dataKey="score"
            stroke="#06B6D4"
            fill="#06B6D4"
            fillOpacity={0.3}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

// Main Component
function CybersecurityOTView() {
  const { t } = useI18n()
  const [events, setEvents] = useState([])
  const [selectedZone, setSelectedZone] = useState(null)
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [viewMode, setViewMode] = useState('overview') // overview | events | vulnerabilities

  // Load events
  useEffect(() => {
    setEvents(generateSecurityEvents())

    if (autoRefresh) {
      const interval = setInterval(() => {
        setEvents(generateSecurityEvents())
      }, 15000)
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  // Calculate stats
  const stats = {
    totalThreats: ZONES.reduce((sum, z) => sum + z.threats, 0),
    totalVulnerabilities: ZONES.reduce((sum, z) => sum + z.vulnerabilities, 0),
    criticalVulns: VULNERABILITIES.filter(v => v.severity === 'critical' && v.status === 'open').length,
    openVulns: VULNERABILITIES.filter(v => v.status === 'open').length,
    securityScore: 76,
    complianceScore: 82
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-orange-600 flex items-center justify-center">
              <ShieldAlert className="w-5 h-5 text-white" />
            </div>
            Cybersecurite OT/IT
          </h1>
          <p className="text-gray-400 mt-1">
            Surveillance et protection des systemes industriels (IEC 62443 / MITRE ATT&CK for ICS)
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* View mode */}
          <div className="flex items-center rounded-lg bg-industrial-card border border-industrial-border">
            {['overview', 'events', 'vulnerabilities'].map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-3 py-2 text-sm transition-all capitalize ${
                  viewMode === mode
                    ? 'bg-red-500/20 text-red-400'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {mode === 'overview' ? 'Vue Globale' : mode === 'events' ? 'Evenements' : 'Vulnerabilites'}
              </button>
            ))}
          </div>

          {/* Auto refresh */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${
              autoRefresh
                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                : 'bg-industrial-card text-gray-400 border border-industrial-border'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Security Score Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <SecurityScoreCard
          title="Score Securite Global"
          score={stats.securityScore}
          maxScore={100}
          icon={Shield}
          color="from-cyan-500 to-blue-600"
          trend={3}
        />
        <SecurityScoreCard
          title="Conformite IEC 62443"
          score={stats.complianceScore}
          maxScore={100}
          icon={FileCheck}
          color="from-green-500 to-emerald-600"
          trend={5}
        />
        <SecurityScoreCard
          title="Menaces Actives"
          score={stats.totalThreats}
          maxScore={50}
          icon={AlertTriangle}
          color="from-amber-500 to-orange-600"
          trend={-2}
        />
        <SecurityScoreCard
          title="Vulnerabilites Critiques"
          score={stats.criticalVulns}
          maxScore={10}
          icon={Bug}
          color="from-red-500 to-pink-600"
        />
        <SecurityScoreCard
          title="Vulns. Ouvertes"
          score={stats.openVulns}
          maxScore={20}
          icon={ShieldOff}
          color="from-orange-500 to-red-600"
        />
        <SecurityScoreCard
          title="Zones Protegees"
          score={ZONES.length}
          maxScore={7}
          icon={Layers}
          color="from-purple-500 to-indigo-600"
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left Column - Topology & Zones */}
        <div className="xl:col-span-2 space-y-6">
          {/* Network Topology */}
          <div>
            <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
              <Network className="w-5 h-5 text-cyan-400" />
              Architecture Reseau (Modele Purdue)
            </h2>
            <NetworkTopology zones={ZONES} selectedZone={selectedZone} />
          </div>

          {/* Zones Grid */}
          <div>
            <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
              <Layers className="w-5 h-5 text-purple-400" />
              Zones de Securite
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {ZONES.slice(0, 6).map((zone) => (
                <ZoneCard
                  key={zone.id}
                  zone={zone}
                  isSelected={selectedZone?.id === zone.id}
                  onClick={setSelectedZone}
                />
              ))}
            </div>
          </div>

          {/* MITRE ATT&CK for ICS */}
          <div>
            <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
              <Target className="w-5 h-5 text-red-400" />
              MITRE ATT&CK for ICS - Detection des Tactiques
            </h2>
            <MitreHeatmap tactics={MITRE_ICS_TACTICS} />
          </div>
        </div>

        {/* Right Column - Events & Compliance */}
        <div className="space-y-6">
          {/* Security Events */}
          <div>
            <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-amber-400" />
              Evenements Securite
            </h2>
            <div className="space-y-2 max-h-80 overflow-y-auto pr-2">
              {events.slice(0, 8).map((event) => (
                <SecurityEventRow
                  key={event.id}
                  event={event}
                  onClick={setSelectedEvent}
                />
              ))}
            </div>
          </div>

          {/* Compliance Radar */}
          <div className="p-4 rounded-xl bg-industrial-card/50 border border-industrial-border">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">
              <FileCheck className="w-4 h-4 text-green-400" />
              Conformite Multi-Referentiels
            </h3>
            <ComplianceRadar />
          </div>

          {/* Top Vulnerabilities */}
          <div>
            <h2 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">
              <Bug className="w-4 h-4 text-red-400" />
              Vulnerabilites Prioritaires
            </h2>
            <VulnerabilityTable
              vulnerabilities={VULNERABILITIES.slice(0, 4)}
              onSelect={(v) => console.log('Selected:', v)}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default CybersecurityOTView
