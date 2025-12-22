import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Target,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  Clock,
  DollarSign,
  Shield,
  Server,
  Activity,
  Zap,
  Users,
  FileText,
  ChevronRight,
  ChevronDown,
  Lightbulb,
  ArrowUpRight,
  ArrowDownRight,
  BarChart3,
  PieChart,
  Sparkles,
  Brain,
  Filter,
  Download,
  RefreshCw,
  Eye,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  ExternalLink
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Card, CardHeader, CardBody } from '../components/ui/Card'
import { useI18n } from '../i18n'
import { PERSONAS, PERSONA_JOURNEYS } from './WelcomePage'

// Impact categories
const IMPACT_CATEGORIES = {
  FINANCIAL: 'financial',
  OPERATIONAL: 'operational',
  SECURITY: 'security',
  COMPLIANCE: 'compliance',
  PERFORMANCE: 'performance'
}

// Priority levels
const PRIORITY = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low'
}

// Sample impact analysis data
const generateImpactData = (persona) => {
  const baseData = {
    summary: {
      totalImpacts: 12,
      criticalItems: 3,
      estimatedSavings: 45000,
      riskReduction: 32,
      actionItems: 8,
      completedActions: 3
    },
    impacts: [
      {
        id: 1,
        category: IMPACT_CATEGORIES.FINANCIAL,
        title: 'Optimisation des coûts d\'infrastructure',
        description: 'Réduction potentielle des coûts cloud de 25% via le rightsizing des instances',
        currentValue: 12000,
        projectedValue: 9000,
        unit: '€/mois',
        trend: 'down',
        priority: PRIORITY.HIGH,
        confidence: 87,
        affectedSystems: ['AWS EC2', 'Kubernetes', 'RDS'],
        recommendations: [
          'Redimensionner les instances EC2 surdimensionnées',
          'Activer les Reserved Instances pour les workloads stables',
          'Implémenter l\'auto-scaling basé sur les métriques réelles'
        ],
        aiInsight: 'L\'analyse des métriques des 30 derniers jours montre une utilisation moyenne CPU de 23% sur les instances de production.',
        timeToImplement: '2-4 semaines',
        roi: '+33% économies annuelles'
      },
      {
        id: 2,
        category: IMPACT_CATEGORIES.SECURITY,
        title: 'Réduction des vulnérabilités critiques',
        description: '3 CVE critiques détectées nécessitant une action immédiate',
        currentValue: 3,
        projectedValue: 0,
        unit: 'vulnérabilités',
        trend: 'down',
        priority: PRIORITY.CRITICAL,
        confidence: 95,
        affectedSystems: ['Apache Log4j', 'OpenSSL', 'Node.js'],
        recommendations: [
          'Appliquer immédiatement les patches de sécurité',
          'Mettre à jour Log4j vers la version 2.17.1+',
          'Planifier une revue de sécurité complète'
        ],
        aiInsight: 'Ces vulnérabilités sont activement exploitées. Risque d\'intrusion estimé à 78% sans action.',
        timeToImplement: 'Immédiat - 24h',
        roi: 'Réduction risque cyber de 85%'
      },
      {
        id: 3,
        category: IMPACT_CATEGORIES.OPERATIONAL,
        title: 'Amélioration du temps de réponse',
        description: 'Optimisation possible de la latence P95 de 340ms à 120ms',
        currentValue: 340,
        projectedValue: 120,
        unit: 'ms',
        trend: 'down',
        priority: PRIORITY.HIGH,
        confidence: 82,
        affectedSystems: ['API Gateway', 'Base de données', 'Cache Redis'],
        recommendations: [
          'Implémenter un cache Redis pour les requêtes fréquentes',
          'Optimiser les indexes de la base de données',
          'Activer le CDN pour les assets statiques'
        ],
        aiInsight: 'L\'analyse des traces montre que 67% de la latence provient des requêtes N+1 sur la base de données.',
        timeToImplement: '1-2 semaines',
        roi: '+15% satisfaction utilisateur'
      },
      {
        id: 4,
        category: IMPACT_CATEGORIES.COMPLIANCE,
        title: 'Conformité NIS 2',
        description: 'Actions requises pour la mise en conformité avant échéance',
        currentValue: 68,
        projectedValue: 95,
        unit: '% conformité',
        trend: 'up',
        priority: PRIORITY.HIGH,
        confidence: 90,
        affectedSystems: ['Gestion des accès', 'Logs d\'audit', 'Plan de continuité'],
        recommendations: [
          'Formaliser le plan de réponse aux incidents',
          'Mettre en place la notification 24h à l\'ANSSI',
          'Renforcer la gestion des identités privilégiées'
        ],
        aiInsight: 'Échéance réglementaire dans 45 jours. 4 contrôles majeurs restent non conformes.',
        timeToImplement: '3-4 semaines',
        roi: 'Évitement pénalités jusqu\'à 2% CA'
      },
      {
        id: 5,
        category: IMPACT_CATEGORIES.PERFORMANCE,
        title: 'Optimisation OEE Production',
        description: 'Potentiel d\'amélioration de l\'OEE de 83% à 89%',
        currentValue: 83,
        projectedValue: 89,
        unit: '%',
        trend: 'up',
        priority: PRIORITY.MEDIUM,
        confidence: 78,
        affectedSystems: ['Ligne A', 'Ligne B', 'Maintenance prédictive'],
        recommendations: [
          'Réduire les micro-arrêts sur la Ligne A',
          'Optimiser les changements de série',
          'Implémenter la maintenance prédictive IA'
        ],
        aiInsight: 'Les micro-arrêts représentent 45% des pertes de performance. Pattern détecté toutes les 4h.',
        timeToImplement: '4-6 semaines',
        roi: '+180K€ production annuelle'
      }
    ],
    trendData: [
      { name: 'Jan', impact: 45, resolved: 12 },
      { name: 'Fév', impact: 52, resolved: 18 },
      { name: 'Mar', impact: 48, resolved: 22 },
      { name: 'Avr', impact: 38, resolved: 28 },
      { name: 'Mai', impact: 42, resolved: 35 },
      { name: 'Juin', impact: 35, resolved: 40 }
    ]
  }

  // Customize data based on persona
  const personaFilters = {
    [PERSONAS.DIRIGEANT]: [IMPACT_CATEGORIES.FINANCIAL, IMPACT_CATEGORIES.COMPLIANCE],
    [PERSONAS.DSI]: [IMPACT_CATEGORIES.OPERATIONAL, IMPACT_CATEGORIES.PERFORMANCE],
    [PERSONAS.RSSI]: [IMPACT_CATEGORIES.SECURITY, IMPACT_CATEGORIES.COMPLIANCE],
    [PERSONAS.RSI]: [IMPACT_CATEGORIES.OPERATIONAL, IMPACT_CATEGORIES.PERFORMANCE],
    [PERSONAS.DPO_JURISTE]: [IMPACT_CATEGORIES.COMPLIANCE, IMPACT_CATEGORIES.SECURITY],
    [PERSONAS.OPERATIONS_MANAGER]: [IMPACT_CATEGORIES.PERFORMANCE, IMPACT_CATEGORIES.OPERATIONAL],
    [PERSONAS.DEVOPS_ENGINEER]: [IMPACT_CATEGORIES.OPERATIONAL, IMPACT_CATEGORIES.PERFORMANCE],
    [PERSONAS.DATA_ANALYST]: [IMPACT_CATEGORIES.PERFORMANCE, IMPACT_CATEGORIES.OPERATIONAL]
  }

  const relevantCategories = personaFilters[persona] || Object.values(IMPACT_CATEGORIES)

  return {
    ...baseData,
    impacts: baseData.impacts.filter(i => relevantCategories.includes(i.category))
  }
}

// Color mapping for categories
const categoryConfig = {
  [IMPACT_CATEGORIES.FINANCIAL]: { color: 'emerald', icon: DollarSign, label: 'Financier' },
  [IMPACT_CATEGORIES.OPERATIONAL]: { color: 'blue', icon: Activity, label: 'Opérationnel' },
  [IMPACT_CATEGORIES.SECURITY]: { color: 'red', icon: Shield, label: 'Sécurité' },
  [IMPACT_CATEGORIES.COMPLIANCE]: { color: 'purple', icon: FileText, label: 'Conformité' },
  [IMPACT_CATEGORIES.PERFORMANCE]: { color: 'amber', icon: Zap, label: 'Performance' }
}

const priorityConfig = {
  [PRIORITY.CRITICAL]: { color: 'red', label: 'Critique' },
  [PRIORITY.HIGH]: { color: 'orange', label: 'Haute' },
  [PRIORITY.MEDIUM]: { color: 'yellow', label: 'Moyenne' },
  [PRIORITY.LOW]: { color: 'green', label: 'Basse' }
}

function ImpactCard({ impact, isExpanded, onToggle }) {
  const category = categoryConfig[impact.category]
  const priority = priorityConfig[impact.priority]
  const CategoryIcon = category.icon

  return (
    <motion.div
      layout
      className={`rounded-xl border-2 transition-all duration-300 overflow-hidden
        ${isExpanded
          ? `bg-industrial-card border-${category.color}-500/50`
          : 'bg-industrial-card/50 border-industrial-border hover:border-industrial-accent/30'
        }`}
    >
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-start gap-4 text-left"
      >
        <div className={`w-12 h-12 rounded-xl bg-${category.color}-500/20 flex items-center justify-center flex-shrink-0`}>
          <CategoryIcon className={`w-6 h-6 text-${category.color}-400`} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`px-2 py-0.5 rounded text-xs font-medium bg-${priority.color}-500/20 text-${priority.color}-400`}>
              {priority.label}
            </span>
            <span className={`px-2 py-0.5 rounded text-xs bg-${category.color}-500/10 text-${category.color}-400`}>
              {category.label}
            </span>
          </div>

          <h3 className="font-semibold text-white mb-1">{impact.title}</h3>
          <p className="text-sm text-gray-400 line-clamp-1">{impact.description}</p>

          <div className="flex items-center gap-4 mt-2">
            <div className="flex items-center gap-1">
              {impact.trend === 'up' ? (
                <ArrowUpRight className="w-4 h-4 text-green-400" />
              ) : (
                <ArrowDownRight className="w-4 h-4 text-green-400" />
              )}
              <span className="text-sm text-gray-300">
                {impact.currentValue} → {impact.projectedValue} {impact.unit}
              </span>
            </div>
            <div className="flex items-center gap-1">
              <Brain className="w-4 h-4 text-cyan-400" />
              <span className="text-xs text-gray-400">{impact.confidence}% confiance</span>
            </div>
          </div>
        </div>

        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-industrial-border"
          >
            <div className="p-4 space-y-4">
              {/* AI Insight */}
              <div className="p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-4 h-4 text-cyan-400" />
                  <span className="text-sm font-medium text-cyan-400">Analyse IA</span>
                </div>
                <p className="text-sm text-gray-300">{impact.aiInsight}</p>
              </div>

              {/* Affected Systems */}
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2">Systèmes impactés</h4>
                <div className="flex flex-wrap gap-2">
                  {impact.affectedSystems.map((system, idx) => (
                    <span key={idx} className="px-2 py-1 rounded bg-industrial-border text-xs text-gray-300">
                      {system}
                    </span>
                  ))}
                </div>
              </div>

              {/* Recommendations */}
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2">Préconisations</h4>
                <ul className="space-y-2">
                  {impact.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-300">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Meta info */}
              <div className="flex items-center justify-between pt-2 border-t border-industrial-border">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4 text-gray-400" />
                    <span className="text-xs text-gray-400">{impact.timeToImplement}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <TrendingUp className="w-4 h-4 text-green-400" />
                    <span className="text-xs text-green-400">{impact.roi}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button className="p-2 rounded-lg bg-industrial-border hover:bg-industrial-accent/20 transition-colors">
                    <ThumbsUp className="w-4 h-4 text-gray-400" />
                  </button>
                  <button className="p-2 rounded-lg bg-industrial-border hover:bg-industrial-accent/20 transition-colors">
                    <ThumbsDown className="w-4 h-4 text-gray-400" />
                  </button>
                  <button className="flex items-center gap-2 px-3 py-2 rounded-lg bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 transition-colors text-sm">
                    <Lightbulb className="w-4 h-4" />
                    Créer Action
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

function SummaryCard({ icon: Icon, label, value, subValue, color, trend }) {
  return (
    <Card className="bg-industrial-card/50">
      <CardBody className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className={`w-10 h-10 rounded-lg bg-${color}-500/20 flex items-center justify-center`}>
            <Icon className={`w-5 h-5 text-${color}-400`} />
          </div>
          {trend && (
            <div className={`flex items-center gap-1 ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
              {trend > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              <span className="text-xs font-medium">{Math.abs(trend)}%</span>
            </div>
          )}
        </div>
        <div className="text-2xl font-bold text-white mb-1">{value}</div>
        <div className="text-sm text-gray-400">{label}</div>
        {subValue && <div className="text-xs text-gray-500 mt-1">{subValue}</div>}
      </CardBody>
    </Card>
  )
}

function ImpactAnalysisView() {
  const { t } = useI18n()
  const navigate = useNavigate()
  const [expandedId, setExpandedId] = useState(null)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedPriority, setSelectedPriority] = useState('all')

  // Get current persona
  const storedPersona = localStorage.getItem('selectedPersona') || PERSONAS.DIRIGEANT
  const [impactData, setImpactData] = useState(() => generateImpactData(storedPersona))

  // Filter impacts
  const filteredImpacts = impactData.impacts.filter(impact => {
    if (selectedCategory !== 'all' && impact.category !== selectedCategory) return false
    if (selectedPriority !== 'all' && impact.priority !== selectedPriority) return false
    return true
  })

  const handleRefresh = () => {
    setImpactData(generateImpactData(storedPersona))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
              <Target className="w-5 h-5 text-white" />
            </div>
            {t('impactAnalysis.title')}
          </h1>
          <p className="text-gray-400 mt-1">{t('impactAnalysis.subtitle')}</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-industrial-card border border-industrial-border hover:border-cyan-500/50 transition-colors"
          >
            <RefreshCw className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-300">Actualiser</span>
          </button>
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-industrial-card border border-industrial-border hover:border-cyan-500/50 transition-colors">
            <Download className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-300">Exporter</span>
          </button>
          <button
            onClick={() => navigate('/ai-assistant')}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-600 text-white hover:from-cyan-400 hover:to-purple-500 transition-colors"
          >
            <MessageSquare className="w-4 h-4" />
            <span className="text-sm">Consulter l'Assistant</span>
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <SummaryCard
          icon={Target}
          label="Impacts identifiés"
          value={impactData.summary.totalImpacts}
          subValue={`${impactData.summary.criticalItems} critiques`}
          color="cyan"
        />
        <SummaryCard
          icon={DollarSign}
          label="Économies potentielles"
          value={`${(impactData.summary.estimatedSavings / 1000).toFixed(0)}K€`}
          subValue="par an"
          color="emerald"
          trend={12}
        />
        <SummaryCard
          icon={Shield}
          label="Réduction risque"
          value={`${impactData.summary.riskReduction}%`}
          subValue="score global"
          color="red"
          trend={8}
        />
        <SummaryCard
          icon={Lightbulb}
          label="Actions recommandées"
          value={impactData.summary.actionItems}
          subValue={`${impactData.summary.completedActions} complétées`}
          color="amber"
        />
        <SummaryCard
          icon={Brain}
          label="Analyses IA"
          value="Active"
          subValue="Dernière: il y a 5 min"
          color="purple"
        />
      </div>

      {/* AI Insight Banner */}
      <Card className="bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-pink-500/10 border-cyan-500/30">
        <CardBody className="p-4">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-white mb-1">Synthèse IA - Priorités du jour</h3>
              <p className="text-sm text-gray-300">
                L'analyse des données des dernières 24h révèle <span className="text-red-400 font-medium">3 actions critiques</span> nécessitant
                une intervention immédiate. Les vulnérabilités de sécurité détectées présentent un risque élevé d'exploitation.
                Une économie de <span className="text-emerald-400 font-medium">45K€ annuels</span> est réalisable via l'optimisation infrastructure.
              </p>
            </div>
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-sm text-white">
              <ExternalLink className="w-4 h-4" />
              Rapport complet
            </button>
          </div>
        </CardBody>
      </Card>

      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-400">Filtrer:</span>
        </div>

        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-3 py-2 rounded-lg bg-industrial-card border border-industrial-border text-sm text-gray-300 focus:outline-none focus:border-cyan-500/50"
        >
          <option value="all">Toutes catégories</option>
          {Object.entries(categoryConfig).map(([key, config]) => (
            <option key={key} value={key}>{config.label}</option>
          ))}
        </select>

        <select
          value={selectedPriority}
          onChange={(e) => setSelectedPriority(e.target.value)}
          className="px-3 py-2 rounded-lg bg-industrial-card border border-industrial-border text-sm text-gray-300 focus:outline-none focus:border-cyan-500/50"
        >
          <option value="all">Toutes priorités</option>
          {Object.entries(priorityConfig).map(([key, config]) => (
            <option key={key} value={key}>{config.label}</option>
          ))}
        </select>

        <span className="text-sm text-gray-500">
          {filteredImpacts.length} résultat{filteredImpacts.length > 1 ? 's' : ''}
        </span>
      </div>

      {/* Impact Cards */}
      <div className="space-y-4">
        <AnimatePresence>
          {filteredImpacts.map(impact => (
            <ImpactCard
              key={impact.id}
              impact={impact}
              isExpanded={expandedId === impact.id}
              onToggle={() => setExpandedId(expandedId === impact.id ? null : impact.id)}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* Empty State */}
      {filteredImpacts.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-industrial-card mx-auto mb-4 flex items-center justify-center">
            <Eye className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-white mb-2">Aucun impact correspondant</h3>
          <p className="text-gray-400">Modifiez les filtres pour voir plus de résultats</p>
        </div>
      )}

      {/* Journey Navigation */}
      <Card className="bg-industrial-card/50 border-industrial-border">
        <CardBody className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Target className="w-5 h-5 text-cyan-400" />
              <span className="font-medium text-white">Prochaine étape de votre parcours</span>
            </div>
            <button
              onClick={() => navigate('/ai-assistant')}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 transition-colors"
            >
              Consulter l'Assistant IA
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

export default ImpactAnalysisView
