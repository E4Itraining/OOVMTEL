import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Scale,
  Shield,
  FileCheck,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ChevronRight,
  ChevronDown,
  Calendar,
  FileText,
  Building2,
  Globe,
  Cpu,
  Network,
  Database,
  Eye,
  Lock,
  RefreshCw,
  Download,
  Filter,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  Info,
  Gavel,
  BookOpen,
  ClipboardCheck,
  Target,
  Activity,
  Layers,
  Award,
  BarChart3
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { TimeSeriesChart, DonutChart, BarChartComponent } from '../components/ui/Charts'
import { StatusBadge, HealthIndicator } from '../components/ui/Status'
import { RadialGauge, LinearGauge, SemiCircleGauge } from '../components/ui/Gauge'

// Mock data for regulatory frameworks
const regulatoryFrameworks = [
  {
    id: 'nis2',
    name: 'NIS 2',
    fullName: 'Network and Information Security Directive 2',
    deadline: new Date('2024-10-17'),
    status: 'partial',
    score: 78,
    categories: [
      { name: 'Gouvernance', score: 95, status: 'compliant' },
      { name: 'Gestion des risques', score: 82, status: 'partial' },
      { name: 'Gestion des incidents', score: 90, status: 'compliant' },
      { name: 'Continuité d\'activité', score: 75, status: 'partial' },
      { name: 'Chaîne d\'approvisionnement', score: 68, status: 'partial' },
      { name: 'Cryptographie', score: 94, status: 'compliant' },
      { name: 'MFA & Accès', score: 98, status: 'compliant' }
    ]
  },
  {
    id: 'aiact',
    name: 'AI Act',
    fullName: 'European Artificial Intelligence Act',
    deadline: new Date('2025-08-02'),
    status: 'partial',
    score: 72,
    categories: [
      { name: 'Inventaire systèmes IA', score: 85, status: 'partial' },
      { name: 'Classification risques', score: 78, status: 'partial' },
      { name: 'Gouvernance données', score: 72, status: 'partial' },
      { name: 'Documentation technique', score: 65, status: 'partial' },
      { name: 'Transparence', score: 90, status: 'compliant' },
      { name: 'Supervision humaine', score: 80, status: 'partial' },
      { name: 'Conformité', score: 45, status: 'pending' }
    ]
  },
  {
    id: 'dora',
    name: 'DORA',
    fullName: 'Digital Operational Resilience Act',
    deadline: new Date('2025-01-17'),
    status: 'partial',
    score: 81,
    categories: [
      { name: 'Gestion risques TIC', score: 85, status: 'partial' },
      { name: 'Incidents TIC', score: 88, status: 'partial' },
      { name: 'Tests résilience', score: 75, status: 'partial' },
      { name: 'Risques tiers', score: 78, status: 'partial' },
      { name: 'Partage d\'information', score: 82, status: 'partial' }
    ]
  },
  {
    id: 'iso27001',
    name: 'ISO 27001:2022',
    fullName: 'Information Security Management System',
    deadline: new Date('2025-03-15'),
    status: 'compliant',
    score: 94,
    categories: [
      { name: 'Contexte organisation', score: 96, status: 'compliant' },
      { name: 'Leadership', score: 95, status: 'compliant' },
      { name: 'Planification', score: 92, status: 'compliant' },
      { name: 'Support', score: 94, status: 'compliant' },
      { name: 'Fonctionnement', score: 95, status: 'compliant' },
      { name: 'Évaluation performance', score: 93, status: 'compliant' },
      { name: 'Amélioration', score: 91, status: 'compliant' }
    ]
  }
]

// AI systems for AI Act compliance
const aiSystems = [
  {
    id: 'ai-001',
    name: 'Maintenance Prédictive IA',
    riskLevel: 'limited',
    status: 'compliant',
    transparency: true,
    humanOversight: true,
    documentation: 'complete'
  },
  {
    id: 'ai-002',
    name: 'Contrôle Qualité Vision',
    riskLevel: 'high',
    status: 'partial',
    transparency: true,
    humanOversight: true,
    documentation: 'partial'
  },
  {
    id: 'ai-003',
    name: 'Assistant Conversationnel',
    riskLevel: 'limited',
    status: 'compliant',
    transparency: true,
    humanOversight: true,
    documentation: 'complete'
  },
  {
    id: 'ai-004',
    name: 'Détection Anomalies Réseau',
    riskLevel: 'high',
    status: 'partial',
    transparency: false,
    humanOversight: true,
    documentation: 'partial'
  },
  {
    id: 'ai-005',
    name: 'Optimisation Énergétique',
    riskLevel: 'minimal',
    status: 'compliant',
    transparency: true,
    humanOversight: false,
    documentation: 'complete'
  }
]

// Audit schedule
const auditSchedule = [
  {
    id: 'audit-001',
    name: 'Audit ISO 27001 - Recertification',
    type: 'external',
    date: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000),
    auditor: 'Bureau Veritas',
    scope: 'SMSI complet',
    status: 'planned'
  },
  {
    id: 'audit-002',
    name: 'Audit interne NIS 2',
    type: 'internal',
    date: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000),
    auditor: 'Équipe Conformité',
    scope: 'Mesures de sécurité',
    status: 'planned'
  },
  {
    id: 'audit-003',
    name: 'Revue AI Act - Systèmes haut risque',
    type: 'internal',
    date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
    auditor: 'DPO + DSI',
    scope: 'Systèmes IA classifiés',
    status: 'planned'
  },
  {
    id: 'audit-004',
    name: 'Test de pénétration',
    type: 'external',
    date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
    auditor: 'CyberDefense SA',
    scope: 'Infrastructure IT',
    status: 'completed'
  }
]

// Action items
const actionItems = [
  {
    id: 'action-001',
    title: 'Finaliser documentation technique AI Act',
    regulation: 'AI Act',
    priority: 'high',
    dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
    status: 'in_progress',
    assignee: 'DSI',
    progress: 65
  },
  {
    id: 'action-002',
    title: 'Mettre en place PCA/PRA NIS 2',
    regulation: 'NIS 2',
    priority: 'critical',
    dueDate: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000),
    status: 'in_progress',
    assignee: 'RSSI',
    progress: 45
  },
  {
    id: 'action-003',
    title: 'Évaluation risques fournisseurs DORA',
    regulation: 'DORA',
    priority: 'high',
    dueDate: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000),
    status: 'pending',
    assignee: 'Achats',
    progress: 20
  },
  {
    id: 'action-004',
    title: 'Audit interne contrôles ISO 27001',
    regulation: 'ISO 27001',
    priority: 'medium',
    dueDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000),
    status: 'planned',
    assignee: 'Qualité',
    progress: 0
  }
]

// Compliance trend data
const generateComplianceTrend = () => {
  const data = []
  for (let i = 11; i >= 0; i--) {
    const date = new Date()
    date.setMonth(date.getMonth() - i)
    data.push({
      time: date.toLocaleDateString('fr-FR', { month: 'short', year: '2-digit' }),
      nis2: Math.min(100, 60 + Math.random() * 10 + (11 - i) * 2),
      aiact: Math.min(100, 45 + Math.random() * 8 + (11 - i) * 2.5),
      dora: Math.min(100, 55 + Math.random() * 12 + (11 - i) * 2),
      iso27001: Math.min(100, 85 + Math.random() * 5 + (11 - i) * 0.8)
    })
  }
  return data
}

// Framework Card Component
function FrameworkCard({ framework, isExpanded, onToggle }) {
  const statusColors = {
    compliant: 'border-green-500/30 hover:border-green-500/50',
    partial: 'border-yellow-500/30 hover:border-yellow-500/50',
    'non-compliant': 'border-red-500/30 hover:border-red-500/50',
    pending: 'border-blue-500/30 hover:border-blue-500/50'
  }

  const daysUntilDeadline = Math.ceil((framework.deadline - new Date()) / (1000 * 60 * 60 * 24))
  const isUrgent = daysUntilDeadline <= 90 && framework.status !== 'compliant'

  return (
    <motion.div
      className={`rounded-xl border bg-industrial-card/50 ${statusColors[framework.status]} transition-all duration-300`}
      layout
    >
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-4">
          <div className="w-16 h-16">
            <RadialGauge
              value={framework.score}
              max={100}
              color={framework.score >= 90 ? '#22c55e' : framework.score >= 70 ? '#eab308' : '#ef4444'}
              size={64}
              showLabel
            />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-white text-lg">{framework.name}</h3>
              {isUrgent && (
                <span className="px-2 py-0.5 rounded text-xs bg-red-500/20 text-red-400 animate-pulse">
                  Urgent
                </span>
              )}
            </div>
            <p className="text-sm text-gray-400">{framework.fullName}</p>
            <div className="flex items-center gap-2 mt-1">
              <Clock className="w-3 h-3 text-gray-500" />
              <span className={`text-xs ${isUrgent ? 'text-red-400' : 'text-gray-500'}`}>
                Échéance: {framework.deadline.toLocaleDateString('fr-FR')} ({daysUntilDeadline}j)
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className={`px-3 py-1 rounded-lg text-sm font-medium ${
            framework.status === 'compliant' ? 'bg-green-500/20 text-green-400' :
            framework.status === 'partial' ? 'bg-yellow-500/20 text-yellow-400' :
            'bg-red-500/20 text-red-400'
          }`}>
            {framework.status === 'compliant' ? 'Conforme' :
             framework.status === 'partial' ? 'Partiel' : 'Non conforme'}
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
                {framework.categories.map((cat) => (
                  <div key={cat.name} className="p-3 rounded-lg bg-industrial-darker/50">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-gray-400">{cat.name}</span>
                      <span className={`text-xs font-bold ${
                        cat.score >= 90 ? 'text-green-400' :
                        cat.score >= 70 ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {cat.score}%
                      </span>
                    </div>
                    <div className="h-1.5 bg-industrial-darker rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          cat.score >= 90 ? 'bg-green-500' :
                          cat.score >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${cat.score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex items-center justify-end mt-4">
                <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-industrial-accent/20 text-industrial-accent hover:bg-industrial-accent/30 transition-colors text-sm">
                  Voir le détail complet
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// AI System Card for AI Act compliance
function AISystemCard({ system }) {
  const riskColors = {
    minimal: 'bg-green-500/20 text-green-400 border-green-500/30',
    limited: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    unacceptable: 'bg-red-500/20 text-red-400 border-red-500/30'
  }

  const riskLabels = {
    minimal: 'Risque minimal',
    limited: 'Risque limité',
    high: 'Haut risque',
    unacceptable: 'Inacceptable'
  }

  return (
    <div className="p-4 rounded-xl border border-industrial-border bg-industrial-card/50">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
            <Cpu className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h4 className="font-medium text-white">{system.name}</h4>
            <span className={`inline-block px-2 py-0.5 rounded text-xs border mt-1 ${riskColors[system.riskLevel]}`}>
              {riskLabels[system.riskLevel]}
            </span>
          </div>
        </div>
        <span className={`px-2 py-1 rounded text-xs ${
          system.status === 'compliant' ? 'bg-green-500/20 text-green-400' :
          'bg-yellow-500/20 text-yellow-400'
        }`}>
          {system.status === 'compliant' ? 'Conforme' : 'Partiel'}
        </span>
      </div>

      <div className="flex items-center gap-4 text-xs">
        <div className="flex items-center gap-1">
          <Eye className={`w-3 h-3 ${system.transparency ? 'text-green-400' : 'text-gray-500'}`} />
          <span className={system.transparency ? 'text-green-400' : 'text-gray-500'}>
            Transparence
          </span>
        </div>
        <div className="flex items-center gap-1">
          <Activity className={`w-3 h-3 ${system.humanOversight ? 'text-green-400' : 'text-gray-500'}`} />
          <span className={system.humanOversight ? 'text-green-400' : 'text-gray-500'}>
            Supervision
          </span>
        </div>
        <div className="flex items-center gap-1">
          <FileText className={`w-3 h-3 ${
            system.documentation === 'complete' ? 'text-green-400' :
            system.documentation === 'partial' ? 'text-yellow-400' : 'text-gray-500'
          }`} />
          <span className={
            system.documentation === 'complete' ? 'text-green-400' :
            system.documentation === 'partial' ? 'text-yellow-400' : 'text-gray-500'
          }>
            Documentation
          </span>
        </div>
      </div>
    </div>
  )
}

// Action Item Card
function ActionItemCard({ action }) {
  const priorityColors = {
    critical: 'border-red-500/50 bg-red-500/5',
    high: 'border-orange-500/50 bg-orange-500/5',
    medium: 'border-yellow-500/50 bg-yellow-500/5',
    low: 'border-green-500/50 bg-green-500/5'
  }

  const daysUntilDue = Math.ceil((action.dueDate - new Date()) / (1000 * 60 * 60 * 24))

  return (
    <motion.div
      whileHover={{ x: 4 }}
      className={`p-4 rounded-xl border ${priorityColors[action.priority]}`}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-xs bg-white/10 text-gray-300">
              {action.regulation}
            </span>
            <span className={`px-2 py-0.5 rounded text-xs ${
              action.priority === 'critical' ? 'bg-red-500/20 text-red-400' :
              action.priority === 'high' ? 'bg-orange-500/20 text-orange-400' :
              action.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-green-500/20 text-green-400'
            }`}>
              {action.priority}
            </span>
          </div>
          <h4 className="font-medium text-white">{action.title}</h4>
          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            <span>Assigné: {action.assignee}</span>
            <span className={daysUntilDue <= 14 ? 'text-red-400' : ''}>
              Échéance: {daysUntilDue}j
            </span>
          </div>
        </div>
      </div>
      <div>
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-400">Progression</span>
          <span className="text-white">{action.progress}%</span>
        </div>
        <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
            style={{ width: `${action.progress}%` }}
          />
        </div>
      </div>
    </motion.div>
  )
}

function ComplianceDashboardView() {
  const { t } = useI18n()
  const [activeTab, setActiveTab] = useState('overview')
  const [expandedFramework, setExpandedFramework] = useState(null)

  const complianceTrend = generateComplianceTrend()

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: Eye },
    { id: 'frameworks', label: 'Réglementations', icon: Scale },
    { id: 'aiact', label: 'AI Act', icon: Cpu },
    { id: 'audits', label: 'Audits', icon: ClipboardCheck },
    { id: 'actions', label: 'Actions', icon: Target }
  ]

  const riskDistribution = [
    { name: 'Minimal', value: aiSystems.filter(s => s.riskLevel === 'minimal').length, color: '#22c55e' },
    { name: 'Limité', value: aiSystems.filter(s => s.riskLevel === 'limited').length, color: '#3b82f6' },
    { name: 'Haut', value: aiSystems.filter(s => s.riskLevel === 'high').length, color: '#f97316' }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-500 to-orange-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            Dashboard Conformité
          </h1>
          <p className="text-gray-400 mt-1">
            Suivi réglementaire EU : NIS 2, AI Act, DORA, ISO 27001
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
                  ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
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
        {regulatoryFrameworks.map((fw) => (
          <MetricCard
            key={fw.id}
            label={fw.name}
            value={fw.score}
            unit="%"
            icon={fw.score >= 90 ? CheckCircle2 : fw.score >= 70 ? AlertCircle : AlertTriangle}
            color={fw.score >= 90 ? 'green' : fw.score >= 70 ? 'yellow' : 'red'}
          />
        ))}
        <MetricCard
          label="Audits planifiés"
          value={auditSchedule.filter(a => a.status === 'planned').length}
          icon={ClipboardCheck}
          color="blue"
        />
        <MetricCard
          label="Actions critiques"
          value={actionItems.filter(a => a.priority === 'critical').length}
          icon={AlertTriangle}
          color={actionItems.filter(a => a.priority === 'critical').length > 0 ? 'red' : 'green'}
        />
      </div>

      {activeTab === 'overview' && (
        <>
          {/* Compliance Trend */}
          <Card>
            <CardHeader
              title="Évolution de la conformité"
              subtitle="Progression sur 12 mois"
              icon={TrendingUp}
            />
            <CardBody>
              <div className="h-64">
                <TimeSeriesChart
                  data={complianceTrend}
                  lines={[
                    { key: 'nis2', color: '#06b6d4', name: 'NIS 2' },
                    { key: 'aiact', color: '#a855f7', name: 'AI Act' },
                    { key: 'dora', color: '#f59e0b', name: 'DORA' },
                    { key: 'iso27001', color: '#22c55e', name: 'ISO 27001' }
                  ]}
                />
              </div>
            </CardBody>
          </Card>

          {/* Frameworks Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader
                title="État des réglementations"
                subtitle="Conformité par framework"
                icon={Scale}
              />
              <CardBody>
                <div className="space-y-4">
                  {regulatoryFrameworks.map((fw) => {
                    const daysUntilDeadline = Math.ceil((fw.deadline - new Date()) / (1000 * 60 * 60 * 24))
                    return (
                      <div key={fw.id} className="flex items-center gap-4">
                        <div className="w-16 h-16">
                          <RadialGauge
                            value={fw.score}
                            max={100}
                            color={fw.score >= 90 ? '#22c55e' : fw.score >= 70 ? '#eab308' : '#ef4444'}
                            size={64}
                            showLabel
                          />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-semibold text-white">{fw.name}</h4>
                            {daysUntilDeadline <= 90 && fw.status !== 'compliant' && (
                              <span className="px-2 py-0.5 rounded text-xs bg-red-500/20 text-red-400">
                                {daysUntilDeadline}j
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-gray-400">{fw.fullName}</p>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs ${
                          fw.status === 'compliant' ? 'bg-green-500/20 text-green-400' :
                          'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {fw.status === 'compliant' ? 'Conforme' : 'Partiel'}
                        </span>
                      </div>
                    )
                  })}
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader
                title="Actions prioritaires"
                subtitle="Prochaines échéances"
                icon={Target}
              />
              <CardBody>
                <div className="space-y-3">
                  {actionItems
                    .sort((a, b) => a.dueDate - b.dueDate)
                    .slice(0, 4)
                    .map((action) => (
                      <ActionItemCard key={action.id} action={action} />
                    ))
                  }
                </div>
              </CardBody>
            </Card>
          </div>
        </>
      )}

      {activeTab === 'frameworks' && (
        <div className="space-y-4">
          {regulatoryFrameworks.map((framework) => (
            <FrameworkCard
              key={framework.id}
              framework={framework}
              isExpanded={expandedFramework === framework.id}
              onToggle={() => setExpandedFramework(expandedFramework === framework.id ? null : framework.id)}
            />
          ))}
        </div>
      )}

      {activeTab === 'aiact' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-1">
            <CardHeader
              title="Classification des risques"
              subtitle="Répartition des systèmes IA"
              icon={Cpu}
            />
            <CardBody>
              <div className="flex flex-col items-center">
                <div className="w-40 h-40">
                  <DonutChart data={riskDistribution} />
                </div>
                <div className="mt-4 w-full space-y-2">
                  {riskDistribution.map((item) => (
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

          <Card className="lg:col-span-2">
            <CardHeader
              title="Inventaire des systèmes IA"
              subtitle="Conformité AI Act par système"
              icon={Database}
            />
            <CardBody>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {aiSystems.map((system) => (
                  <AISystemCard key={system.id} system={system} />
                ))}
              </div>
            </CardBody>
          </Card>
        </div>
      )}

      {activeTab === 'audits' && (
        <Card>
          <CardHeader
            title="Calendrier des audits"
            subtitle="Audits planifiés et réalisés"
            icon={ClipboardCheck}
          />
          <CardBody>
            <div className="space-y-4">
              {auditSchedule.map((audit) => {
                const isPast = audit.date < new Date()
                return (
                  <div
                    key={audit.id}
                    className={`p-4 rounded-xl border ${
                      isPast ? 'border-green-500/30 bg-green-500/5' : 'border-industrial-border bg-industrial-card/50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                          isPast ? 'bg-green-500/20' : 'bg-blue-500/20'
                        }`}>
                          <ClipboardCheck className={`w-5 h-5 ${isPast ? 'text-green-400' : 'text-blue-400'}`} />
                        </div>
                        <div>
                          <h4 className="font-medium text-white">{audit.name}</h4>
                          <p className="text-sm text-gray-400">{audit.scope}</p>
                          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                            <span className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {audit.date.toLocaleDateString('fr-FR')}
                            </span>
                            <span>{audit.auditor}</span>
                            <span className={`px-2 py-0.5 rounded ${
                              audit.type === 'external' ? 'bg-purple-500/20 text-purple-400' : 'bg-cyan-500/20 text-cyan-400'
                            }`}>
                              {audit.type === 'external' ? 'Externe' : 'Interne'}
                            </span>
                          </div>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-lg text-sm ${
                        audit.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {audit.status === 'completed' ? 'Terminé' : 'Planifié'}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardBody>
        </Card>
      )}

      {activeTab === 'actions' && (
        <Card>
          <CardHeader
            title="Plan d'actions"
            subtitle="Actions de mise en conformité"
            icon={Target}
          />
          <CardBody>
            <div className="space-y-4">
              {actionItems.map((action) => (
                <ActionItemCard key={action.id} action={action} />
              ))}
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}

export default ComplianceDashboardView
