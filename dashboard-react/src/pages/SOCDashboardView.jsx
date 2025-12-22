import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield,
  AlertTriangle,
  AlertOctagon,
  Eye,
  Search,
  Target,
  Activity,
  Clock,
  Calendar,
  ChevronRight,
  ChevronDown,
  RefreshCw,
  Download,
  Filter,
  Play,
  Pause,
  SkipForward,
  XCircle,
  CheckCircle2,
  AlertCircle,
  Info,
  Bug,
  Skull,
  Globe,
  Network,
  Server,
  Database,
  Lock,
  Unlock,
  Key,
  UserX,
  Mail,
  FileWarning,
  Zap,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Map,
  Crosshair,
  Radio,
  Siren,
  Timer,
  History,
  Terminal,
  Code
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { TimeSeriesChart, DonutChart, BarChartComponent } from '../components/ui/Charts'
import { StatusBadge, HealthIndicator } from '../components/ui/Status'
import { RadialGauge, LinearGauge, SemiCircleGauge } from '../components/ui/Gauge'

// Active security incidents
const activeIncidents = [
  {
    id: 'INC-2024-0142',
    title: 'Tentative de brute force SSH',
    severity: 'high',
    source: '203.0.113.42',
    target: 'srv-prod-01',
    category: 'intrusion_attempt',
    status: 'investigating',
    assignee: 'Sophie Martin',
    detectedAt: new Date(Date.now() - 15 * 60 * 1000),
    iocCount: 12,
    affectedAssets: 1
  },
  {
    id: 'INC-2024-0141',
    title: 'Malware détecté sur poste utilisateur',
    severity: 'critical',
    source: 'workstation-0234',
    target: 'Internal Network',
    category: 'malware',
    status: 'containment',
    assignee: 'Marc Dubois',
    detectedAt: new Date(Date.now() - 45 * 60 * 1000),
    iocCount: 8,
    affectedAssets: 3
  },
  {
    id: 'INC-2024-0140',
    title: 'Exfiltration données suspecte',
    severity: 'critical',
    source: 'db-analytics-02',
    target: '185.234.xxx.xxx',
    category: 'data_exfiltration',
    status: 'investigating',
    assignee: 'Sophie Martin',
    detectedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    iocCount: 5,
    affectedAssets: 2
  },
  {
    id: 'INC-2024-0139',
    title: 'Scan de ports interne',
    severity: 'medium',
    source: '10.0.5.142',
    target: 'Subnet 10.0.1.0/24',
    category: 'reconnaissance',
    status: 'monitoring',
    assignee: null,
    detectedAt: new Date(Date.now() - 4 * 60 * 60 * 1000),
    iocCount: 3,
    affectedAssets: 0
  }
]

// Security alerts queue
const alertsQueue = [
  { id: 'ALT-8842', type: 'Firewall Block', source: '103.45.xxx.xxx', count: 234, severity: 'low', time: '2min' },
  { id: 'ALT-8841', type: 'Failed Login', source: 'admin@company.com', count: 15, severity: 'medium', time: '5min' },
  { id: 'ALT-8840', type: 'Privilege Escalation', source: 'srv-web-03', count: 1, severity: 'high', time: '8min' },
  { id: 'ALT-8839', type: 'DNS Anomaly', source: 'workstation-0089', count: 42, severity: 'medium', time: '12min' },
  { id: 'ALT-8838', type: 'Policy Violation', source: 'user.jones', count: 3, severity: 'low', time: '15min' },
  { id: 'ALT-8837', type: 'Suspicious Download', source: 'workstation-0156', count: 1, severity: 'high', time: '18min' }
]

// Threat intelligence
const threatIntelligence = {
  activeThreats: 12,
  iocMatches: 47,
  blockedIPs: 1842,
  newIndicators: 156,
  feeds: [
    { name: 'AlienVault OTX', status: 'active', lastSync: '5min', indicators: 12450 },
    { name: 'MISP Community', status: 'active', lastSync: '15min', indicators: 8920 },
    { name: 'VirusTotal', status: 'active', lastSync: '2min', indicators: 45000 },
    { name: 'AbuseIPDB', status: 'active', lastSync: '10min', indicators: 23400 }
  ]
}

// MITRE ATT&CK mapping
const mitreMapping = [
  { tactic: 'Initial Access', techniques: 3, detected: 2, color: '#ef4444' },
  { tactic: 'Execution', techniques: 5, detected: 1, color: '#f97316' },
  { tactic: 'Persistence', techniques: 4, detected: 0, color: '#eab308' },
  { tactic: 'Privilege Escalation', techniques: 3, detected: 1, color: '#84cc16' },
  { tactic: 'Defense Evasion', techniques: 6, detected: 2, color: '#22c55e' },
  { tactic: 'Credential Access', techniques: 2, detected: 1, color: '#06b6d4' },
  { tactic: 'Discovery', techniques: 4, detected: 3, color: '#3b82f6' },
  { tactic: 'Lateral Movement', techniques: 2, detected: 0, color: '#8b5cf6' },
  { tactic: 'Collection', techniques: 3, detected: 1, color: '#a855f7' },
  { tactic: 'Exfiltration', techniques: 2, detected: 2, color: '#ec4899' }
]

// SOC metrics
const socMetrics = {
  mttr: 45, // minutes
  mttd: 8, // minutes
  alertsToday: 1247,
  incidentsToday: 12,
  falsePositiveRate: 23,
  automationRate: 67,
  slaCompliance: 94
}

// Investigation timeline (for selected incident)
const investigationTimeline = [
  { time: '14:32:15', event: 'Alert triggered', type: 'detection', details: 'Suspicious SSH activity detected' },
  { time: '14:32:18', event: 'Auto-enrichment', type: 'automation', details: 'IP reputation check: Malicious (Score: 92/100)' },
  { time: '14:32:20', event: 'SIEM correlation', type: 'automation', details: '3 related events found in last 24h' },
  { time: '14:35:00', event: 'Analyst assigned', type: 'action', details: 'Sophie Martin assigned to incident' },
  { time: '14:38:00', event: 'Investigation started', type: 'action', details: 'Log analysis in progress' },
  { time: '14:42:00', event: 'IOC extracted', type: 'finding', details: '12 indicators of compromise identified' }
]

// Generate alert trend data
const generateAlertTrend = () => {
  const data = []
  for (let i = 23; i >= 0; i--) {
    data.push({
      time: `${23 - i}:00`,
      critical: Math.floor(Math.random() * 5),
      high: Math.floor(Math.random() * 15) + 5,
      medium: Math.floor(Math.random() * 40) + 20,
      low: Math.floor(Math.random() * 60) + 30
    })
  }
  return data
}

// Alert severity distribution
const severityDistribution = [
  { name: 'Critical', value: 8, color: '#ef4444' },
  { name: 'High', value: 45, color: '#f97316' },
  { name: 'Medium', value: 234, color: '#eab308' },
  { name: 'Low', value: 960, color: '#22c55e' }
]

// Incident Card Component
function IncidentCard({ incident, isExpanded, onToggle }) {
  const severityColors = {
    critical: 'border-red-500/50 bg-red-500/5',
    high: 'border-orange-500/50 bg-orange-500/5',
    medium: 'border-yellow-500/50 bg-yellow-500/5',
    low: 'border-green-500/50 bg-green-500/5'
  }

  const severityBadge = {
    critical: 'bg-red-500/20 text-red-400 animate-pulse',
    high: 'bg-orange-500/20 text-orange-400',
    medium: 'bg-yellow-500/20 text-yellow-400',
    low: 'bg-green-500/20 text-green-400'
  }

  const statusColors = {
    investigating: 'bg-blue-500/20 text-blue-400',
    containment: 'bg-purple-500/20 text-purple-400',
    eradication: 'bg-orange-500/20 text-orange-400',
    recovery: 'bg-cyan-500/20 text-cyan-400',
    monitoring: 'bg-gray-500/20 text-gray-400',
    closed: 'bg-green-500/20 text-green-400'
  }

  const categoryIcons = {
    intrusion_attempt: Lock,
    malware: Bug,
    data_exfiltration: Database,
    reconnaissance: Search,
    phishing: Mail,
    dos: Zap
  }

  const Icon = categoryIcons[incident.category] || AlertTriangle
  const timeSinceDetection = Math.floor((new Date() - incident.detectedAt) / 60000)

  return (
    <motion.div
      className={`rounded-xl border ${severityColors[incident.severity]} transition-all duration-300`}
      layout
    >
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
            incident.severity === 'critical' ? 'bg-red-500/20' :
            incident.severity === 'high' ? 'bg-orange-500/20' :
            'bg-yellow-500/20'
          }`}>
            <Icon className={`w-6 h-6 ${
              incident.severity === 'critical' ? 'text-red-400' :
              incident.severity === 'high' ? 'text-orange-400' :
              'text-yellow-400'
            }`} />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-mono text-xs text-gray-400">{incident.id}</span>
              <span className={`px-2 py-0.5 rounded text-xs ${severityBadge[incident.severity]}`}>
                {incident.severity.toUpperCase()}
              </span>
              <span className={`px-2 py-0.5 rounded text-xs ${statusColors[incident.status]}`}>
                {incident.status}
              </span>
            </div>
            <h3 className="font-semibold text-white">{incident.title}</h3>
            <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {timeSinceDetection} min
              </span>
              <span>{incident.source} → {incident.target}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-4">
            <div className="text-center">
              <p className="text-lg font-semibold text-white">{incident.iocCount}</p>
              <p className="text-xs text-gray-500">IOCs</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-semibold text-white">{incident.affectedAssets}</p>
              <p className="text-xs text-gray-500">Assets</p>
            </div>
          </div>
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
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="p-3 rounded-lg bg-industrial-darker/50">
                  <p className="text-xs text-gray-500">Source IP</p>
                  <p className="text-sm font-mono text-white">{incident.source}</p>
                </div>
                <div className="p-3 rounded-lg bg-industrial-darker/50">
                  <p className="text-xs text-gray-500">Cible</p>
                  <p className="text-sm text-white">{incident.target}</p>
                </div>
                <div className="p-3 rounded-lg bg-industrial-darker/50">
                  <p className="text-xs text-gray-500">Assigné</p>
                  <p className="text-sm text-white">{incident.assignee || 'Non assigné'}</p>
                </div>
                <div className="p-3 rounded-lg bg-industrial-darker/50">
                  <p className="text-xs text-gray-500">Détection</p>
                  <p className="text-sm text-white">{incident.detectedAt.toLocaleTimeString('fr-FR')}</p>
                </div>
              </div>

              {/* Timeline */}
              <div className="mb-4">
                <p className="text-xs text-gray-500 uppercase mb-2">Timeline</p>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {investigationTimeline.map((event, idx) => (
                    <div key={idx} className="flex items-start gap-3 text-sm">
                      <span className="font-mono text-xs text-gray-500 w-16">{event.time}</span>
                      <div className={`w-2 h-2 rounded-full mt-1.5 ${
                        event.type === 'detection' ? 'bg-red-400' :
                        event.type === 'automation' ? 'bg-cyan-400' :
                        event.type === 'action' ? 'bg-blue-400' :
                        'bg-purple-400'
                      }`} />
                      <div>
                        <p className="text-white">{event.event}</p>
                        <p className="text-xs text-gray-500">{event.details}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <button className="px-3 py-1.5 rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors text-sm flex items-center gap-1">
                    <Eye className="w-4 h-4" />
                    Investiguer
                  </button>
                  <button className="px-3 py-1.5 rounded-lg bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 transition-colors text-sm flex items-center gap-1">
                    <Target className="w-4 h-4" />
                    Contenir
                  </button>
                </div>
                <button className="px-3 py-1.5 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors text-sm flex items-center gap-1">
                  <Siren className="w-4 h-4" />
                  Escalader
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Alert Queue Item
function AlertQueueItem({ alert }) {
  const severityColors = {
    critical: 'border-l-red-500',
    high: 'border-l-orange-500',
    medium: 'border-l-yellow-500',
    low: 'border-l-green-500'
  }

  return (
    <div className={`p-3 rounded-r-lg bg-industrial-darker/50 border-l-4 ${severityColors[alert.severity]} flex items-center justify-between`}>
      <div className="flex items-center gap-3">
        <div className="text-center">
          <p className="text-lg font-bold text-white">{alert.count}</p>
          <p className="text-[10px] text-gray-500">events</p>
        </div>
        <div>
          <p className="text-sm font-medium text-white">{alert.type}</p>
          <p className="text-xs text-gray-500">{alert.source}</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-400">{alert.time}</span>
        <button className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
          <ChevronRight className="w-4 h-4 text-gray-400" />
        </button>
      </div>
    </div>
  )
}

function SOCDashboardView() {
  const { t } = useI18n()
  const [activeTab, setActiveTab] = useState('overview')
  const [expandedIncident, setExpandedIncident] = useState(null)

  const alertTrend = generateAlertTrend()

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: Eye },
    { id: 'incidents', label: 'Incidents', icon: AlertOctagon },
    { id: 'alerts', label: 'Alertes', icon: AlertTriangle },
    { id: 'threats', label: 'Threat Intel', icon: Skull },
    { id: 'forensics', label: 'Forensics', icon: Search }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            Dashboard SOC
          </h1>
          <p className="text-gray-400 mt-1">
            Security Operations Center - Détection, réponse et analyse des menaces
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-500/20 border border-green-500/30">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-sm text-green-400">Monitoring actif</span>
          </div>
          <button className="btn btn-ghost flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Live
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
                  ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
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
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        <MetricCard
          label="Incidents actifs"
          value={activeIncidents.filter(i => i.status !== 'closed').length}
          icon={AlertOctagon}
          color={activeIncidents.filter(i => i.severity === 'critical').length > 0 ? 'red' : 'yellow'}
        />
        <MetricCard
          label="Alertes 24h"
          value={socMetrics.alertsToday}
          icon={AlertTriangle}
          color="yellow"
        />
        <MetricCard
          label="MTTD"
          value={socMetrics.mttd}
          unit="min"
          icon={Timer}
          color="cyan"
        />
        <MetricCard
          label="MTTR"
          value={socMetrics.mttr}
          unit="min"
          icon={Clock}
          color="blue"
        />
        <MetricCard
          label="Taux auto"
          value={socMetrics.automationRate}
          unit="%"
          icon={Zap}
          color="green"
        />
        <MetricCard
          label="IOCs détectés"
          value={threatIntelligence.iocMatches}
          icon={Crosshair}
          color="purple"
        />
        <MetricCard
          label="IPs bloquées"
          value={threatIntelligence.blockedIPs}
          icon={Lock}
          color="red"
        />
      </div>

      {activeTab === 'overview' && (
        <>
          {/* Active Incidents & Alert Queue */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader
                title="Incidents actifs"
                subtitle="Incidents en cours de traitement"
                icon={AlertOctagon}
              />
              <CardBody>
                <div className="space-y-3">
                  {activeIncidents.map((incident) => (
                    <IncidentCard
                      key={incident.id}
                      incident={incident}
                      isExpanded={expandedIncident === incident.id}
                      onToggle={() => setExpandedIncident(expandedIncident === incident.id ? null : incident.id)}
                    />
                  ))}
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader
                title="Queue d'alertes"
                subtitle="Alertes en attente"
                icon={AlertTriangle}
              />
              <CardBody>
                <div className="space-y-2">
                  {alertsQueue.map((alert) => (
                    <AlertQueueItem key={alert.id} alert={alert} />
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Alert Trend & Severity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader
                title="Tendance des alertes"
                subtitle="Distribution horaire par sévérité"
                icon={Activity}
              />
              <CardBody>
                <div className="h-64">
                  <TimeSeriesChart
                    data={alertTrend}
                    lines={[
                      { key: 'critical', color: '#ef4444', name: 'Critical' },
                      { key: 'high', color: '#f97316', name: 'High' },
                      { key: 'medium', color: '#eab308', name: 'Medium' },
                      { key: 'low', color: '#22c55e', name: 'Low' }
                    ]}
                  />
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader
                title="Distribution par sévérité"
                subtitle="Répartition des alertes"
                icon={BarChart3}
              />
              <CardBody>
                <div className="flex items-center gap-8">
                  <div className="w-40 h-40">
                    <DonutChart data={severityDistribution} />
                  </div>
                  <div className="flex-1 space-y-3">
                    {severityDistribution.map((item) => (
                      <div key={item.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                          <span className="text-sm text-gray-400">{item.name}</span>
                        </div>
                        <span className="text-sm font-medium text-white">{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
        </>
      )}

      {activeTab === 'incidents' && (
        <Card>
          <CardHeader
            title="Tous les incidents"
            subtitle="Gestion des incidents de sécurité"
            icon={AlertOctagon}
          />
          <CardBody>
            <div className="space-y-3">
              {activeIncidents.map((incident) => (
                <IncidentCard
                  key={incident.id}
                  incident={incident}
                  isExpanded={expandedIncident === incident.id}
                  onToggle={() => setExpandedIncident(expandedIncident === incident.id ? null : incident.id)}
                />
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {activeTab === 'threats' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader
              title="Threat Intelligence Feeds"
              subtitle="Sources de renseignement sur les menaces"
              icon={Radio}
            />
            <CardBody>
              <div className="space-y-3">
                {threatIntelligence.feeds.map((feed) => (
                  <div key={feed.name} className="p-4 rounded-xl border border-industrial-border bg-industrial-card/50">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center">
                          <Globe className="w-4 h-4 text-purple-400" />
                        </div>
                        <div>
                          <h4 className="font-medium text-white">{feed.name}</h4>
                          <p className="text-xs text-gray-500">Sync: {feed.lastSync}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                        <span className="text-xs text-green-400">{feed.status}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-lg font-bold text-white">{feed.indicators.toLocaleString()}</span>
                      <span className="text-xs text-gray-500 ml-1">indicateurs</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="MITRE ATT&CK Coverage"
              subtitle="Détections par tactique"
              icon={Target}
            />
            <CardBody>
              <div className="space-y-3">
                {mitreMapping.map((tactic) => (
                  <div key={tactic.tactic} className="flex items-center gap-3">
                    <div className="w-32 text-sm text-gray-400 truncate">{tactic.tactic}</div>
                    <div className="flex-1 h-6 bg-industrial-darker rounded-full overflow-hidden flex">
                      <div
                        className="h-full flex items-center justify-end pr-2"
                        style={{
                          width: `${(tactic.detected / tactic.techniques) * 100}%`,
                          backgroundColor: tactic.color
                        }}
                      >
                        <span className="text-[10px] text-white font-bold">{tactic.detected}</span>
                      </div>
                    </div>
                    <div className="w-16 text-right text-sm text-gray-500">
                      {tactic.detected}/{tactic.techniques}
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>
      )}

      {activeTab === 'forensics' && (
        <Card>
          <CardHeader
            title="Investigation forensique"
            subtitle="Analyse approfondie des incidents"
            icon={Search}
          />
          <CardBody>
            <div className="p-8 text-center">
              <div className="w-16 h-16 rounded-full bg-cyan-500/20 flex items-center justify-center mx-auto mb-4">
                <Terminal className="w-8 h-8 text-cyan-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Console Forensique</h3>
              <p className="text-gray-400 mb-4">
                Sélectionnez un incident pour lancer une investigation approfondie
              </p>
              <button className="px-6 py-3 rounded-lg bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 transition-colors">
                Ouvrir la console
              </button>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}

export default SOCDashboardView
