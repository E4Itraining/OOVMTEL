import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield,
  FileCheck,
  Users,
  Database,
  Eye,
  Lock,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ChevronRight,
  ChevronDown,
  Calendar,
  FileText,
  UserCheck,
  UserX,
  Mail,
  Download,
  Trash2,
  Edit3,
  Search,
  Filter,
  RefreshCw,
  Settings,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  Info,
  Scale,
  Building2,
  Globe,
  Fingerprint,
  Key,
  Activity
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { TimeSeriesChart, DonutChart, BarChartComponent } from '../components/ui/Charts'
import { StatusBadge, HealthIndicator } from '../components/ui/Status'
import { RadialGauge, LinearGauge, SemiCircleGauge } from '../components/ui/Gauge'

// Mock data for RGPD compliance
const rgpdCompliance = {
  globalScore: 91,
  articles: [
    { id: 'art-5', name: 'Principes (Art. 5)', score: 95, status: 'compliant' },
    { id: 'art-6', name: 'Licéité (Art. 6)', score: 92, status: 'compliant' },
    { id: 'art-7', name: 'Consentement (Art. 7)', score: 88, status: 'partial' },
    { id: 'art-12', name: 'Transparence (Art. 12-14)', score: 94, status: 'compliant' },
    { id: 'art-15', name: 'Droit d\'accès (Art. 15)', score: 96, status: 'compliant' },
    { id: 'art-17', name: 'Droit à l\'effacement (Art. 17)', score: 85, status: 'partial' },
    { id: 'art-25', name: 'Privacy by Design (Art. 25)', score: 82, status: 'partial' },
    { id: 'art-30', name: 'Registre (Art. 30)', score: 98, status: 'compliant' },
    { id: 'art-32', name: 'Sécurité (Art. 32)', score: 91, status: 'compliant' },
    { id: 'art-33', name: 'Notification violation (Art. 33)', score: 89, status: 'partial' }
  ]
}

// Mock data for data processing activities (Registre des traitements)
const dataProcessingActivities = [
  {
    id: 'dpa-001',
    name: 'Gestion des ressources humaines',
    purpose: 'Administration du personnel et paie',
    legalBasis: 'Contrat',
    dataCategories: ['Identité', 'Coordonnées', 'Vie professionnelle', 'Données financières'],
    dataSubjects: ['Salariés', 'Candidats'],
    retention: '5 ans après départ',
    transfers: false,
    pia: false,
    status: 'compliant',
    lastReview: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
  },
  {
    id: 'dpa-002',
    name: 'Gestion commerciale',
    purpose: 'Relation client et facturation',
    legalBasis: 'Contrat',
    dataCategories: ['Identité', 'Coordonnées', 'Données transactionnelles'],
    dataSubjects: ['Clients', 'Prospects'],
    retention: '10 ans pour facturation',
    transfers: false,
    pia: false,
    status: 'compliant',
    lastReview: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000)
  },
  {
    id: 'dpa-003',
    name: 'Vidéosurveillance',
    purpose: 'Sécurité des locaux',
    legalBasis: 'Intérêt légitime',
    dataCategories: ['Images'],
    dataSubjects: ['Salariés', 'Visiteurs'],
    retention: '30 jours',
    transfers: false,
    pia: true,
    status: 'compliant',
    lastReview: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000)
  },
  {
    id: 'dpa-004',
    name: 'Analytics web',
    purpose: 'Mesure d\'audience',
    legalBasis: 'Consentement',
    dataCategories: ['Données navigation', 'Cookies'],
    dataSubjects: ['Visiteurs site'],
    retention: '13 mois',
    transfers: true,
    pia: false,
    status: 'partial',
    lastReview: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000)
  },
  {
    id: 'dpa-005',
    name: 'IA Prédictive Production',
    purpose: 'Maintenance prédictive',
    legalBasis: 'Intérêt légitime',
    dataCategories: ['Données machine', 'Logs opérateurs'],
    dataSubjects: ['Opérateurs'],
    retention: '3 ans',
    transfers: false,
    pia: true,
    status: 'review',
    lastReview: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000)
  }
]

// Mock data for data subject requests
const dataSubjectRequests = [
  {
    id: 'DSR-2024-001',
    type: 'access',
    subject: 'Jean Dupont',
    email: 'j.dupont@email.com',
    requestDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    deadline: new Date(Date.now() + 25 * 24 * 60 * 60 * 1000),
    status: 'in_progress',
    assignee: 'Marie Martin'
  },
  {
    id: 'DSR-2024-002',
    type: 'erasure',
    subject: 'Sophie Bernard',
    email: 's.bernard@email.com',
    requestDate: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
    deadline: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000),
    status: 'pending_validation',
    assignee: 'Pierre Durand'
  },
  {
    id: 'DSR-2024-003',
    type: 'portability',
    subject: 'Michel Leroy',
    email: 'm.leroy@email.com',
    requestDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    deadline: new Date(Date.now() + 28 * 24 * 60 * 60 * 1000),
    status: 'new',
    assignee: null
  },
  {
    id: 'DSR-2024-004',
    type: 'rectification',
    subject: 'Claire Moreau',
    email: 'c.moreau@email.com',
    requestDate: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000),
    deadline: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000),
    status: 'completed',
    assignee: 'Marie Martin'
  }
]

// Mock data for consent management
const consentStats = {
  total: 45200,
  valid: 38420,
  expired: 3200,
  withdrawn: 2100,
  pending: 1480,
  byPurpose: [
    { purpose: 'Marketing', consented: 28500, refused: 16700 },
    { purpose: 'Analytics', consented: 32100, refused: 13100 },
    { purpose: 'Personnalisation', consented: 25800, refused: 19400 },
    { purpose: 'Partenaires', consented: 18200, refused: 27000 }
  ]
}

// Mock data for data breaches
const dataBreaches = [
  {
    id: 'DB-2024-001',
    date: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000),
    type: 'Accès non autorisé',
    severity: 'medium',
    affectedRecords: 150,
    notifiedCNIL: true,
    notifiedSubjects: true,
    status: 'closed',
    rootCause: 'Mot de passe compromis'
  },
  {
    id: 'DB-2024-002',
    date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
    type: 'Perte de données',
    severity: 'low',
    affectedRecords: 12,
    notifiedCNIL: false,
    notifiedSubjects: false,
    status: 'investigating',
    rootCause: 'Erreur utilisateur'
  }
]

// Mock data for PIAs (Privacy Impact Assessments)
const piaList = [
  {
    id: 'PIA-001',
    name: 'Système IA Contrôle Qualité',
    status: 'completed',
    riskLevel: 'medium',
    lastUpdate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    nextReview: new Date(Date.now() + 335 * 24 * 60 * 60 * 1000)
  },
  {
    id: 'PIA-002',
    name: 'Vidéosurveillance Sites Production',
    status: 'completed',
    riskLevel: 'low',
    lastUpdate: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000),
    nextReview: new Date(Date.now() + 305 * 24 * 60 * 60 * 1000)
  },
  {
    id: 'PIA-003',
    name: 'Plateforme RH Analytique',
    status: 'in_progress',
    riskLevel: 'high',
    lastUpdate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    nextReview: null
  }
]

// Generate consent trend data
const generateConsentTrend = () => {
  const data = []
  for (let i = 30; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    data.push({
      time: date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }),
      optIn: Math.floor(Math.random() * 200) + 300,
      optOut: Math.floor(Math.random() * 50) + 20
    })
  }
  return data
}

// Data Subject Request Card Component
function DSRCard({ request, t }) {
  const typeIcons = {
    access: Eye,
    erasure: Trash2,
    portability: Download,
    rectification: Edit3,
    objection: UserX
  }

  const typeLabels = {
    access: 'Accès',
    erasure: 'Effacement',
    portability: 'Portabilité',
    rectification: 'Rectification',
    objection: 'Opposition'
  }

  const statusColors = {
    new: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    in_progress: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    pending_validation: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    completed: 'bg-green-500/20 text-green-400 border-green-500/30',
    rejected: 'bg-red-500/20 text-red-400 border-red-500/30'
  }

  const Icon = typeIcons[request.type] || FileText
  const daysRemaining = Math.ceil((request.deadline - new Date()) / (1000 * 60 * 60 * 24))
  const isUrgent = daysRemaining <= 7

  return (
    <motion.div
      whileHover={{ x: 4 }}
      className={`p-4 rounded-xl border bg-industrial-card/50 ${isUrgent ? 'border-red-500/50' : 'border-industrial-border'}`}
    >
      <div className="flex items-start gap-4">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
          request.type === 'erasure' ? 'bg-red-500/20' : 'bg-cyan-500/20'
        }`}>
          <Icon className={`w-5 h-5 ${request.type === 'erasure' ? 'text-red-400' : 'text-cyan-400'}`} />
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-xs text-gray-400">{request.id}</span>
            <span className={`px-2 py-0.5 rounded text-xs border ${statusColors[request.status]}`}>
              {request.status.replace('_', ' ')}
            </span>
          </div>
          <h4 className="font-medium text-white">{typeLabels[request.type]}</h4>
          <p className="text-sm text-gray-400">{request.subject}</p>
          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Mail className="w-3 h-3" />
              {request.email}
            </span>
            <span className={`flex items-center gap-1 ${isUrgent ? 'text-red-400' : ''}`}>
              <Clock className="w-3 h-3" />
              {daysRemaining} jours restants
            </span>
          </div>
        </div>

        <button className="px-3 py-1.5 rounded-lg bg-industrial-accent/20 text-industrial-accent hover:bg-industrial-accent/30 transition-colors text-sm">
          Traiter
        </button>
      </div>
    </motion.div>
  )
}

// Processing Activity Card Component
function ProcessingActivityCard({ activity, isExpanded, onToggle }) {
  const statusColors = {
    compliant: 'border-green-500/30 hover:border-green-500/50',
    partial: 'border-yellow-500/30 hover:border-yellow-500/50',
    review: 'border-blue-500/30 hover:border-blue-500/50',
    'non-compliant': 'border-red-500/30 hover:border-red-500/50'
  }

  const statusBadgeColors = {
    compliant: 'bg-green-500/20 text-green-400',
    partial: 'bg-yellow-500/20 text-yellow-400',
    review: 'bg-blue-500/20 text-blue-400',
    'non-compliant': 'bg-red-500/20 text-red-400'
  }

  return (
    <motion.div
      className={`rounded-xl border bg-industrial-card/50 ${statusColors[activity.status]} transition-all duration-300`}
      layout
    >
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
            <Database className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h3 className="font-semibold text-white">{activity.name}</h3>
            <p className="text-sm text-gray-400">{activity.purpose}</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className={`px-2 py-1 rounded text-xs ${statusBadgeColors[activity.status]}`}>
            {activity.status}
          </span>
          {activity.pia && (
            <span className="px-2 py-1 rounded text-xs bg-purple-500/20 text-purple-400">
              AIPD
            </span>
          )}
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
            <div className="px-4 pb-4 pt-2 border-t border-industrial-border/50 space-y-3">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Base légale</p>
                  <p className="text-sm text-white">{activity.legalBasis}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Durée conservation</p>
                  <p className="text-sm text-white">{activity.retention}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Personnes concernées</p>
                  <p className="text-sm text-white">{activity.dataSubjects.join(', ')}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Transfert hors UE</p>
                  <p className={`text-sm ${activity.transfers ? 'text-yellow-400' : 'text-green-400'}`}>
                    {activity.transfers ? 'Oui' : 'Non'}
                  </p>
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Catégories de données</p>
                <div className="flex flex-wrap gap-1">
                  {activity.dataCategories.map((cat, idx) => (
                    <span key={idx} className="px-2 py-0.5 rounded text-xs bg-white/5 text-gray-300">
                      {cat}
                    </span>
                  ))}
                </div>
              </div>
              <div className="flex items-center justify-between pt-2">
                <span className="text-xs text-gray-500">
                  Dernière révision: {activity.lastReview.toLocaleDateString('fr-FR')}
                </span>
                <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-industrial-accent/20 text-industrial-accent hover:bg-industrial-accent/30 transition-colors text-sm">
                  Voir détails
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

function DPODashboardView() {
  const { t } = useI18n()
  const [activeTab, setActiveTab] = useState('overview')
  const [expandedActivity, setExpandedActivity] = useState(null)

  const consentTrend = generateConsentTrend()

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: Eye },
    { id: 'registry', label: 'Registre', icon: FileCheck },
    { id: 'requests', label: 'Demandes', icon: Users },
    { id: 'consent', label: 'Consentements', icon: UserCheck },
    { id: 'breaches', label: 'Violations', icon: AlertTriangle }
  ]

  const consentDistribution = [
    { name: 'Valides', value: consentStats.valid, color: '#22c55e' },
    { name: 'Expirés', value: consentStats.expired, color: '#eab308' },
    { name: 'Retirés', value: consentStats.withdrawn, color: '#ef4444' },
    { name: 'En attente', value: consentStats.pending, color: '#3b82f6' }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-600 flex items-center justify-center">
              <FileCheck className="w-5 h-5 text-white" />
            </div>
            Dashboard DPO
          </h1>
          <p className="text-gray-400 mt-1">
            Conformité RGPD, protection des données et gestion des droits
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn btn-ghost flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Actualiser
          </button>
          <button className="btn btn-ghost flex items-center gap-2">
            <Download className="w-4 h-4" />
            Exporter
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
                  ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
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
          label="Score RGPD"
          value={rgpdCompliance.globalScore}
          unit="%"
          icon={Shield}
          color="green"
        />
        <MetricCard
          label="Traitements"
          value={dataProcessingActivities.length}
          icon={Database}
          color="cyan"
        />
        <MetricCard
          label="Demandes en cours"
          value={dataSubjectRequests.filter(r => r.status !== 'completed').length}
          icon={Users}
          color="yellow"
        />
        <MetricCard
          label="Consentements actifs"
          value={`${(consentStats.valid / 1000).toFixed(1)}k`}
          icon={UserCheck}
          color="blue"
        />
        <MetricCard
          label="AIPD"
          value={piaList.length}
          icon={FileText}
          color="purple"
        />
        <MetricCard
          label="Violations"
          value={dataBreaches.filter(b => b.status !== 'closed').length}
          icon={AlertTriangle}
          color={dataBreaches.filter(b => b.status !== 'closed').length > 0 ? 'red' : 'green'}
        />
      </div>

      {activeTab === 'overview' && (
        <>
          {/* RGPD Compliance Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-1">
              <CardHeader
                title="Conformité RGPD"
                subtitle="Score global de conformité"
                icon={Shield}
              />
              <CardBody>
                <div className="flex flex-col items-center">
                  <SemiCircleGauge
                    value={rgpdCompliance.globalScore}
                    max={100}
                    label="Score RGPD"
                    color={rgpdCompliance.globalScore >= 90 ? '#22c55e' : rgpdCompliance.globalScore >= 75 ? '#eab308' : '#ef4444'}
                  />
                  <div className="mt-4 w-full space-y-2">
                    {rgpdCompliance.articles.slice(0, 5).map((article) => (
                      <div key={article.id} className="flex items-center justify-between">
                        <span className="text-sm text-gray-400">{article.name}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-2 bg-industrial-darker rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                article.score >= 90 ? 'bg-green-500' : article.score >= 75 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${article.score}%` }}
                            />
                          </div>
                          <span className="text-xs text-white w-8 text-right">{article.score}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader
                title="Demandes des personnes concernées"
                subtitle="Demandes récentes et en cours"
                icon={Users}
              />
              <CardBody>
                <div className="space-y-3">
                  {dataSubjectRequests.slice(0, 4).map((request) => (
                    <DSRCard key={request.id} request={request} t={t} />
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Consent & Breaches */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader
                title="Consentements"
                subtitle="Répartition des consentements"
                icon={UserCheck}
              />
              <CardBody>
                <div className="flex items-center gap-8">
                  <div className="w-40 h-40">
                    <DonutChart data={consentDistribution} />
                  </div>
                  <div className="flex-1 space-y-3">
                    {consentDistribution.map((item) => (
                      <div key={item.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                          <span className="text-sm text-gray-400">{item.name}</span>
                        </div>
                        <span className="text-sm font-medium text-white">{item.value.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader
                title="AIPD en cours"
                subtitle="Analyses d'impact sur la protection des données"
                icon={FileText}
              />
              <CardBody>
                <div className="space-y-3">
                  {piaList.map((pia) => (
                    <div key={pia.id} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                          pia.riskLevel === 'high' ? 'bg-red-500/20' :
                          pia.riskLevel === 'medium' ? 'bg-yellow-500/20' : 'bg-green-500/20'
                        }`}>
                          <Shield className={`w-4 h-4 ${
                            pia.riskLevel === 'high' ? 'text-red-400' :
                            pia.riskLevel === 'medium' ? 'text-yellow-400' : 'text-green-400'
                          }`} />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-white">{pia.name}</p>
                          <p className="text-xs text-gray-500">Risque: {pia.riskLevel}</p>
                        </div>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs ${
                        pia.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {pia.status === 'completed' ? 'Terminée' : 'En cours'}
                      </span>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>
        </>
      )}

      {activeTab === 'registry' && (
        <Card>
          <CardHeader
            title="Registre des traitements"
            subtitle="Article 30 RGPD - Registre des activités de traitement"
            icon={Database}
          />
          <CardBody>
            <div className="space-y-3">
              {dataProcessingActivities.map((activity) => (
                <ProcessingActivityCard
                  key={activity.id}
                  activity={activity}
                  isExpanded={expandedActivity === activity.id}
                  onToggle={() => setExpandedActivity(expandedActivity === activity.id ? null : activity.id)}
                />
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {activeTab === 'requests' && (
        <Card>
          <CardHeader
            title="Demandes des personnes concernées"
            subtitle="Gestion des droits RGPD"
            icon={Users}
          />
          <CardBody>
            <div className="space-y-3">
              {dataSubjectRequests.map((request) => (
                <DSRCard key={request.id} request={request} t={t} />
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {activeTab === 'consent' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader
              title="Évolution des consentements"
              subtitle="Opt-in vs Opt-out sur 30 jours"
              icon={TrendingUp}
            />
            <CardBody>
              <div className="h-64">
                <TimeSeriesChart
                  data={consentTrend}
                  lines={[
                    { key: 'optIn', color: '#22c55e', name: 'Opt-in' },
                    { key: 'optOut', color: '#ef4444', name: 'Opt-out' }
                  ]}
                />
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="Consentements par finalité"
              subtitle="Taux d'acceptation par type"
              icon={UserCheck}
            />
            <CardBody>
              <div className="space-y-4">
                {consentStats.byPurpose.map((item) => {
                  const rate = Math.round((item.consented / (item.consented + item.refused)) * 100)
                  return (
                    <div key={item.purpose}>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm text-gray-400">{item.purpose}</span>
                        <span className="text-sm text-white">{rate}%</span>
                      </div>
                      <div className="h-2 bg-industrial-darker rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-green-500 to-green-400 rounded-full"
                          style={{ width: `${rate}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardBody>
          </Card>
        </div>
      )}

      {activeTab === 'breaches' && (
        <Card>
          <CardHeader
            title="Violations de données"
            subtitle="Historique et gestion des incidents"
            icon={AlertTriangle}
          />
          <CardBody>
            <div className="space-y-4">
              {dataBreaches.map((breach) => (
                <div
                  key={breach.id}
                  className={`p-4 rounded-xl border ${
                    breach.severity === 'high' ? 'border-red-500/50 bg-red-500/5' :
                    breach.severity === 'medium' ? 'border-yellow-500/50 bg-yellow-500/5' :
                    'border-green-500/50 bg-green-500/5'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        breach.severity === 'high' ? 'bg-red-500/20' :
                        breach.severity === 'medium' ? 'bg-yellow-500/20' :
                        'bg-green-500/20'
                      }`}>
                        <AlertTriangle className={`w-5 h-5 ${
                          breach.severity === 'high' ? 'text-red-400' :
                          breach.severity === 'medium' ? 'text-yellow-400' :
                          'text-green-400'
                        }`} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-sm text-gray-400">{breach.id}</span>
                          <span className={`px-2 py-0.5 rounded text-xs ${
                            breach.status === 'closed' ? 'bg-green-500/20 text-green-400' :
                            'bg-yellow-500/20 text-yellow-400'
                          }`}>
                            {breach.status === 'closed' ? 'Clôturé' : 'En cours'}
                          </span>
                        </div>
                        <h4 className="font-medium text-white mt-1">{breach.type}</h4>
                        <p className="text-sm text-gray-400">{breach.rootCause}</p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          <span>{breach.affectedRecords} enregistrements affectés</span>
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {breach.date.toLocaleDateString('fr-FR')}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <div className="flex items-center gap-2 text-xs">
                        <span className={breach.notifiedCNIL ? 'text-green-400' : 'text-gray-500'}>
                          CNIL {breach.notifiedCNIL ? '✓' : '○'}
                        </span>
                        <span className={breach.notifiedSubjects ? 'text-green-400' : 'text-gray-500'}>
                          Personnes {breach.notifiedSubjects ? '✓' : '○'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}

export default DPODashboardView
