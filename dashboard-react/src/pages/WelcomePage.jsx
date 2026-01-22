import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Activity,
  Building2,
  Server,
  Shield,
  Scale,
  BarChart3,
  ChevronRight,
  Sparkles,
  ArrowRight,
  Users,
  Target,
  Briefcase,
  Network,
  Lock,
  FileCheck,
  Cpu,
  TrendingUp,
  Eye,
  Layers,
  CheckCircle2,
  Leaf,
  Zap,
  CircuitBoard,
  Database,
  Gavel,
  Factory,
  PiggyBank,
  TreePine,
  Recycle,
  Gauge,
  AlertTriangle,
  ClipboardCheck
} from 'lucide-react'
import { useI18n } from '../i18n'

// Define industrial personas organized by domain
export const PERSONAS = {
  // BUSINESS - Vision métier et stratégique
  DIRIGEANT: 'dirigeant',
  CFO: 'cfo',
  DIRECTEUR_PRODUCTION: 'directeur_production',
  // TECH - Technique et data
  DSI: 'dsi',
  DATA_MLOPS: 'data_mlops',
  DEVOPS_SRE: 'devops_sre',
  // SÉCURITÉ - Cybersécurité
  RSSI: 'rssi',
  ANALYSTE_SOC: 'analyste_soc',
  // JURIDIQUE - Conformité et régulations
  DPO: 'dpo',
  RESPONSABLE_CONFORMITE: 'responsable_conformite',
  // GREENOPS - Durabilité et environnement
  RESPONSABLE_RSE: 'responsable_rse',
  GREEN_IT_MANAGER: 'green_it_manager'
}

// Persona journey stages
export const JOURNEY_STAGES = {
  DISCOVERY: 'discovery',
  ASSESSMENT: 'assessment',
  ACTION: 'action',
  MONITORING: 'monitoring'
}

// Define persona-specific journeys
export const PERSONA_JOURNEYS = {
  // ═══════════════════════════════════════════════════════════════════════════
  // BUSINESS - Vision métier et stratégique
  // ═══════════════════════════════════════════════════════════════════════════
  [PERSONAS.DIRIGEANT]: {
    name: 'Parcours Dirigeant',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Vue d\'ensemble', route: '/command-center', icon: Eye },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'KPIs Stratégiques', route: '/business-kpi', icon: TrendingUp },
      { id: JOURNEY_STAGES.ACTION, label: 'Impact & Préconisations', route: '/impact-analysis', icon: Target },
      { id: JOURNEY_STAGES.MONITORING, label: 'Assistant IA', route: '/ai-assistant', icon: Sparkles }
    ],
    defaultRoute: '/command-center',
    focusAreas: ['strategy', 'roi', 'risk', 'performance', 'governance']
  },
  [PERSONAS.CFO]: {
    name: 'Parcours CFO',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Vue Financière', route: '/command-center', icon: PiggyBank },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'Coûts & ROI', route: '/business-kpi', icon: TrendingUp },
      { id: JOURNEY_STAGES.ACTION, label: 'Impact Financier', route: '/impact-analysis', icon: Target },
      { id: JOURNEY_STAGES.MONITORING, label: 'Budgets IT', route: '/business-kpi#costs', icon: BarChart3 }
    ],
    defaultRoute: '/command-center',
    focusAreas: ['costs', 'roi', 'budget', 'financial-impact', 'capex-opex']
  },
  [PERSONAS.DIRECTEUR_PRODUCTION]: {
    name: 'Parcours Production',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Centre de Commande', route: '/command-center', icon: Factory },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'OEE & Performance', route: '/business-kpi', icon: Gauge },
      { id: JOURNEY_STAGES.ACTION, label: 'Optimisations', route: '/impact-analysis', icon: Target },
      { id: JOURNEY_STAGES.MONITORING, label: 'Équipements', route: '/business-kpi#equipment', icon: Activity }
    ],
    defaultRoute: '/command-center',
    focusAreas: ['production', 'oee', 'equipment', 'quality', 'maintenance']
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // TECH - Technique et data
  // ═══════════════════════════════════════════════════════════════════════════
  [PERSONAS.DSI]: {
    name: 'Parcours DSI',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Infrastructure', route: '/technical', icon: Server },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'Performance SI', route: '/observability', icon: Activity },
      { id: JOURNEY_STAGES.ACTION, label: 'Impact & Préconisations', route: '/impact-analysis', icon: Target },
      { id: JOURNEY_STAGES.MONITORING, label: 'Gouvernance IT', route: '/security', icon: Shield }
    ],
    defaultRoute: '/technical',
    focusAreas: ['infrastructure', 'digital-transformation', 'budget', 'services', 'innovation']
  },
  [PERSONAS.DATA_MLOPS]: {
    name: 'Parcours Data & MLOps',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Dashboard MLOps', route: '/mlops-dashboard', icon: Database },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'Modèles ML', route: '/mlops-dashboard#models', icon: BarChart3 },
      { id: JOURNEY_STAGES.ACTION, label: 'Data Quality', route: '/mlops-dashboard#quality', icon: CircuitBoard },
      { id: JOURNEY_STAGES.MONITORING, label: 'Observabilité IA', route: '/mlops-dashboard#observability', icon: Activity }
    ],
    defaultRoute: '/mlops-dashboard',
    focusAreas: ['data-quality', 'ml-models', 'drift', 'pipelines', 'feature-engineering']
  },
  [PERSONAS.DEVOPS_SRE]: {
    name: 'Parcours DevOps / SRE',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Infrastructure', route: '/technical', icon: Server },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'SLOs & Fiabilité', route: '/observability', icon: Gauge },
      { id: JOURNEY_STAGES.ACTION, label: 'Incidents', route: '/observability#runbooks', icon: AlertTriangle },
      { id: JOURNEY_STAGES.MONITORING, label: 'Logs & Traces', route: '/opensearch', icon: Eye }
    ],
    defaultRoute: '/technical',
    focusAreas: ['slos', 'reliability', 'incidents', 'automation', 'monitoring']
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // SÉCURITÉ - Cybersécurité
  // ═══════════════════════════════════════════════════════════════════════════
  [PERSONAS.RSSI]: {
    name: 'Parcours RSSI',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Posture Sécurité', route: '/security', icon: Shield },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'Vulnérabilités', route: '/security#vulnerabilities', icon: Lock },
      { id: JOURNEY_STAGES.ACTION, label: 'Remédiation', route: '/impact-analysis', icon: Target },
      { id: JOURNEY_STAGES.MONITORING, label: 'Conformité', route: '/security#compliance', icon: FileCheck }
    ],
    defaultRoute: '/security',
    focusAreas: ['cybersecurity', 'threats', 'compliance', 'incidents', 'audit']
  },
  [PERSONAS.ANALYSTE_SOC]: {
    name: 'Parcours Analyste SOC',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Dashboard SOC', route: '/soc-dashboard', icon: AlertTriangle },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'Incidents', route: '/soc-dashboard#incidents', icon: Shield },
      { id: JOURNEY_STAGES.ACTION, label: 'Threat Intel', route: '/soc-dashboard#threats', icon: Eye },
      { id: JOURNEY_STAGES.MONITORING, label: 'Forensics', route: '/soc-dashboard#forensics', icon: Activity }
    ],
    defaultRoute: '/soc-dashboard',
    focusAreas: ['threats', 'incidents', 'forensics', 'detection', 'response']
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // JURIDIQUE - Conformité et régulations
  // ═══════════════════════════════════════════════════════════════════════════
  [PERSONAS.DPO]: {
    name: 'Parcours DPO',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Dashboard DPO', route: '/dpo-dashboard', icon: FileCheck },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'Registre Traitements', route: '/dpo-dashboard#registry', icon: Database },
      { id: JOURNEY_STAGES.ACTION, label: 'Demandes & Droits', route: '/dpo-dashboard#requests', icon: Target },
      { id: JOURNEY_STAGES.MONITORING, label: 'Consentements', route: '/dpo-dashboard#consent', icon: Eye }
    ],
    defaultRoute: '/dpo-dashboard',
    focusAreas: ['rgpd', 'privacy', 'consent', 'data-processing', 'rights']
  },
  [PERSONAS.RESPONSABLE_CONFORMITE]: {
    name: 'Parcours Conformité',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Dashboard Conformité', route: '/compliance-dashboard', icon: Scale },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'Réglementations', route: '/compliance-dashboard#frameworks', icon: Gavel },
      { id: JOURNEY_STAGES.ACTION, label: 'AI Act & Audits', route: '/compliance-dashboard#aiact', icon: Target },
      { id: JOURNEY_STAGES.MONITORING, label: 'Plan d\'Actions', route: '/compliance-dashboard#actions', icon: ClipboardCheck }
    ],
    defaultRoute: '/compliance-dashboard',
    focusAreas: ['nis2', 'ai-act', 'dora', 'iso27001', 'audit']
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // GREENOPS - Durabilité et environnement
  // ═══════════════════════════════════════════════════════════════════════════
  [PERSONAS.RESPONSABLE_RSE]: {
    name: 'Parcours RSE',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Dashboard RSE', route: '/rse-dashboard', icon: TreePine },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'Empreinte Carbone', route: '/rse-dashboard#carbon', icon: Leaf },
      { id: JOURNEY_STAGES.ACTION, label: 'Reporting CSRD', route: '/rse-dashboard#csrd', icon: Target },
      { id: JOURNEY_STAGES.MONITORING, label: 'Score ESG', route: '/rse-dashboard#esg', icon: BarChart3 }
    ],
    defaultRoute: '/rse-dashboard',
    focusAreas: ['carbon-footprint', 'sustainability', 'esg', 'csrd', 'energy']
  },
  [PERSONAS.GREEN_IT_MANAGER]: {
    name: 'Parcours Green IT',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Dashboard Green IT', route: '/greenit-dashboard', icon: Zap },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'PUE & Datacenter', route: '/greenit-dashboard#datacenter', icon: Gauge },
      { id: JOURNEY_STAGES.ACTION, label: 'Cloud Carbon', route: '/greenit-dashboard#cloud', icon: Recycle },
      { id: JOURNEY_STAGES.MONITORING, label: 'Optimisations', route: '/greenit-dashboard#optimization', icon: Activity }
    ],
    defaultRoute: '/greenit-dashboard',
    focusAreas: ['pue', 'energy-efficiency', 'e-waste', 'cloud-carbon', 'optimization']
  }
}

const getPersonaConfig = (t) => [
  // ═══════════════════════════════════════════════════════════════════════════
  // BUSINESS - Vision métier et stratégique
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: PERSONAS.DIRIGEANT,
    icon: Building2,
    color: 'from-indigo-500 to-purple-600',
    bgColor: 'bg-indigo-500/10',
    borderColor: 'border-indigo-500/30',
    textColor: 'text-indigo-400',
    category: 'business',
    categoryLabel: 'BUSINESS',
    title: t('personas.dirigeant.title'),
    description: t('personas.dirigeant.description'),
    features: [
      t('personas.dirigeant.feature1'),
      t('personas.dirigeant.feature2'),
      t('personas.dirigeant.feature3')
    ],
    defaultRoute: '/command-center',
    focusAreas: ['strategy', 'roi', 'governance']
  },
  {
    id: PERSONAS.CFO,
    icon: PiggyBank,
    color: 'from-violet-500 to-purple-600',
    bgColor: 'bg-violet-500/10',
    borderColor: 'border-violet-500/30',
    textColor: 'text-violet-400',
    category: 'business',
    categoryLabel: 'BUSINESS',
    title: t('personas.cfo.title'),
    description: t('personas.cfo.description'),
    features: [
      t('personas.cfo.feature1'),
      t('personas.cfo.feature2'),
      t('personas.cfo.feature3')
    ],
    defaultRoute: '/command-center',
    focusAreas: ['costs', 'roi', 'budget']
  },
  {
    id: PERSONAS.DIRECTEUR_PRODUCTION,
    icon: Factory,
    color: 'from-fuchsia-500 to-pink-600',
    bgColor: 'bg-fuchsia-500/10',
    borderColor: 'border-fuchsia-500/30',
    textColor: 'text-fuchsia-400',
    category: 'business',
    categoryLabel: 'BUSINESS',
    title: t('personas.directeurProduction.title'),
    description: t('personas.directeurProduction.description'),
    features: [
      t('personas.directeurProduction.feature1'),
      t('personas.directeurProduction.feature2'),
      t('personas.directeurProduction.feature3')
    ],
    defaultRoute: '/command-center',
    focusAreas: ['production', 'oee', 'equipment']
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // TECH - Technique et data
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: PERSONAS.DSI,
    icon: Cpu,
    color: 'from-blue-500 to-cyan-600',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    textColor: 'text-blue-400',
    category: 'tech',
    categoryLabel: 'TECH',
    title: t('personas.dsi.title'),
    description: t('personas.dsi.description'),
    features: [
      t('personas.dsi.feature1'),
      t('personas.dsi.feature2'),
      t('personas.dsi.feature3')
    ],
    defaultRoute: '/technical',
    focusAreas: ['infrastructure', 'digital', 'innovation']
  },
  {
    id: PERSONAS.DATA_MLOPS,
    icon: CircuitBoard,
    color: 'from-sky-500 to-blue-600',
    bgColor: 'bg-sky-500/10',
    borderColor: 'border-sky-500/30',
    textColor: 'text-sky-400',
    category: 'tech',
    categoryLabel: 'TECH',
    title: t('personas.dataMlops.title'),
    description: t('personas.dataMlops.description'),
    features: [
      t('personas.dataMlops.feature1'),
      t('personas.dataMlops.feature2'),
      t('personas.dataMlops.feature3')
    ],
    defaultRoute: '/mlops-dashboard',
    focusAreas: ['data-quality', 'ml-models', 'pipelines']
  },
  {
    id: PERSONAS.DEVOPS_SRE,
    icon: Server,
    color: 'from-cyan-500 to-teal-600',
    bgColor: 'bg-cyan-500/10',
    borderColor: 'border-cyan-500/30',
    textColor: 'text-cyan-400',
    category: 'tech',
    categoryLabel: 'TECH',
    title: t('personas.devopsSre.title'),
    description: t('personas.devopsSre.description'),
    features: [
      t('personas.devopsSre.feature1'),
      t('personas.devopsSre.feature2'),
      t('personas.devopsSre.feature3')
    ],
    defaultRoute: '/technical',
    focusAreas: ['slos', 'reliability', 'automation']
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // SÉCURITÉ - Cybersécurité
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: PERSONAS.RSSI,
    icon: Shield,
    color: 'from-red-500 to-orange-600',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    textColor: 'text-red-400',
    category: 'security',
    categoryLabel: 'SÉCURITÉ',
    title: t('personas.rssi.title'),
    description: t('personas.rssi.description'),
    features: [
      t('personas.rssi.feature1'),
      t('personas.rssi.feature2'),
      t('personas.rssi.feature3')
    ],
    defaultRoute: '/security',
    focusAreas: ['security', 'threats', 'compliance']
  },
  {
    id: PERSONAS.ANALYSTE_SOC,
    icon: AlertTriangle,
    color: 'from-orange-500 to-amber-600',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30',
    textColor: 'text-orange-400',
    category: 'security',
    categoryLabel: 'SÉCURITÉ',
    title: t('personas.analyteSoc.title'),
    description: t('personas.analyteSoc.description'),
    features: [
      t('personas.analyteSoc.feature1'),
      t('personas.analyteSoc.feature2'),
      t('personas.analyteSoc.feature3')
    ],
    defaultRoute: '/soc-dashboard',
    focusAreas: ['threats', 'incidents', 'forensics']
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // JURIDIQUE - Conformité et régulations
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: PERSONAS.DPO,
    icon: FileCheck,
    color: 'from-amber-500 to-yellow-600',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/30',
    textColor: 'text-amber-400',
    category: 'legal',
    categoryLabel: 'JURIDIQUE',
    title: t('personas.dpo.title'),
    description: t('personas.dpo.description'),
    features: [
      t('personas.dpo.feature1'),
      t('personas.dpo.feature2'),
      t('personas.dpo.feature3')
    ],
    defaultRoute: '/dpo-dashboard',
    focusAreas: ['rgpd', 'privacy', 'data-processing']
  },
  {
    id: PERSONAS.RESPONSABLE_CONFORMITE,
    icon: Scale,
    color: 'from-yellow-500 to-orange-600',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/30',
    textColor: 'text-yellow-400',
    category: 'legal',
    categoryLabel: 'JURIDIQUE',
    title: t('personas.responsableConformite.title'),
    description: t('personas.responsableConformite.description'),
    features: [
      t('personas.responsableConformite.feature1'),
      t('personas.responsableConformite.feature2'),
      t('personas.responsableConformite.feature3')
    ],
    defaultRoute: '/compliance-dashboard',
    focusAreas: ['nis2', 'ai-act', 'audit']
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // GREENOPS - Durabilité et environnement
  // ═══════════════════════════════════════════════════════════════════════════
  {
    id: PERSONAS.RESPONSABLE_RSE,
    icon: TreePine,
    color: 'from-emerald-500 to-green-600',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/30',
    textColor: 'text-emerald-400',
    category: 'greenops',
    categoryLabel: 'GREENOPS',
    title: t('personas.responsableRse.title'),
    description: t('personas.responsableRse.description'),
    features: [
      t('personas.responsableRse.feature1'),
      t('personas.responsableRse.feature2'),
      t('personas.responsableRse.feature3')
    ],
    defaultRoute: '/rse-dashboard',
    focusAreas: ['carbon-footprint', 'sustainability', 'esg']
  },
  {
    id: PERSONAS.GREEN_IT_MANAGER,
    icon: Leaf,
    color: 'from-green-500 to-teal-600',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    textColor: 'text-green-400',
    category: 'greenops',
    categoryLabel: 'GREENOPS',
    title: t('personas.greenItManager.title'),
    description: t('personas.greenItManager.description'),
    features: [
      t('personas.greenItManager.feature1'),
      t('personas.greenItManager.feature2'),
      t('personas.greenItManager.feature3')
    ],
    defaultRoute: '/greenit-dashboard',
    focusAreas: ['pue', 'energy-efficiency', 'cloud-carbon']
  }
]

function PersonaCard({ persona, isSelected, onSelect }) {
  const Icon = persona.icon

  return (
    <motion.button
      onClick={() => onSelect(persona)}
      className={`relative p-5 rounded-2xl border-2 transition-all duration-300 text-left w-full
        ${isSelected
          ? `${persona.bgColor} ${persona.borderColor} shadow-lg shadow-${persona.textColor}/20`
          : 'bg-industrial-card/50 border-industrial-border hover:border-industrial-accent/30 hover:bg-industrial-card'
        }`}
      whileHover={{ scale: 1.02, y: -4 }}
      whileTap={{ scale: 0.98 }}
      layout
    >
      {/* Category badge */}
      <div className="absolute top-3 right-3">
        {isSelected ? (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 500 }}
          >
            <div className={`w-6 h-6 rounded-full bg-gradient-to-br ${persona.color} flex items-center justify-center`}>
              <CheckCircle2 className="w-4 h-4 text-white" />
            </div>
          </motion.div>
        ) : (
          <span className="text-[10px] font-semibold text-gray-500 bg-industrial-darker/50 px-2 py-1 rounded-md border border-industrial-border">
            {persona.categoryLabel}
          </span>
        )}
      </div>

      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${persona.color} flex items-center justify-center mb-3 shadow-lg`}>
        <Icon className="w-6 h-6 text-white" />
      </div>

      <h3 className={`font-bold text-base mb-1.5 ${isSelected ? persona.textColor : 'text-white'}`}>
        {persona.title}
      </h3>

      <p className="text-xs text-gray-400 mb-3 line-clamp-2">
        {persona.description}
      </p>

      <AnimatePresence>
        {isSelected && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-1.5"
          >
            {persona.features.map((feature, idx) => (
              <div key={idx} className="flex items-center gap-2 text-xs text-gray-300">
                <div className={`w-1.5 h-1.5 rounded-full bg-gradient-to-br ${persona.color}`} />
                {feature}
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  )
}

function JourneyPreview({ persona }) {
  const journey = PERSONA_JOURNEYS[persona.id]
  if (!journey) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="mt-6 p-4 rounded-xl bg-industrial-card/50 border border-industrial-border"
    >
      <div className="flex items-center gap-2 mb-4">
        <Target className="w-5 h-5 text-cyan-400" />
        <span className="font-semibold text-white">Votre Parcours Personnalisé</span>
      </div>

      <div className="flex items-center justify-between">
        {journey.stages.map((stage, idx) => {
          const StageIcon = stage.icon
          return (
            <React.Fragment key={stage.id}>
              <div className="flex flex-col items-center gap-2">
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${persona.color} flex items-center justify-center`}>
                  <StageIcon className="w-5 h-5 text-white" />
                </div>
                <span className="text-xs text-gray-400 text-center max-w-[80px]">{stage.label}</span>
              </div>
              {idx < journey.stages.length - 1 && (
                <ChevronRight className="w-5 h-5 text-gray-600 flex-shrink-0" />
              )}
            </React.Fragment>
          )
        })}
      </div>
    </motion.div>
  )
}

function WelcomePage() {
  const navigate = useNavigate()
  const { t } = useI18n()
  const [selectedPersona, setSelectedPersona] = useState(null)
  const [activeCategory, setActiveCategory] = useState('all')

  const personas = getPersonaConfig(t)

  const categories = [
    { id: 'all', label: 'Tous', icon: Users },
    { id: 'business', label: 'Business', icon: Building2 },
    { id: 'tech', label: 'Tech', icon: Cpu },
    { id: 'security', label: 'Sécurité', icon: Shield },
    { id: 'legal', label: 'Juridique', icon: Scale },
    { id: 'greenops', label: 'GreenOps', icon: Leaf }
  ]

  const filteredPersonas = activeCategory === 'all'
    ? personas
    : personas.filter(p => p.category === activeCategory)

  const handleContinue = () => {
    if (selectedPersona) {
      // Store persona preference
      localStorage.setItem('selectedPersona', selectedPersona.id)

      // Store journey information
      const journey = PERSONA_JOURNEYS[selectedPersona.id]
      if (journey) {
        localStorage.setItem('personaJourney', JSON.stringify(journey))
        localStorage.setItem('currentJourneyStage', '0')
      }

      // Navigate to the default route for the persona
      navigate(selectedPersona.defaultRoute || '/command-center')
    }
  }

  const handleSkip = () => {
    navigate('/command-center')
  }

  return (
    <div className="min-h-screen bg-industrial-darker flex flex-col">
      {/* Background gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-industrial-dark via-industrial-darker to-black opacity-80" />
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-cyan-900/20 via-transparent to-transparent" />

      {/* Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500 via-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
              <Activity className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">
            {t('welcome.title')}
          </h1>
          <p className="text-lg text-gray-400 mb-2">
            {t('welcome.subtitle')}
          </p>
          <div className="flex items-center justify-center gap-2 text-sm text-cyan-400">
            <Sparkles className="w-4 h-4" />
            <span>{t('welcome.tagline')}</span>
          </div>
        </motion.div>

        {/* Category Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-wrap justify-center gap-2 mb-6"
        >
          {categories.map((cat) => {
            const CatIcon = cat.icon
            return (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
                  ${activeCategory === cat.id
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                    : 'bg-industrial-card/50 text-gray-400 border border-industrial-border hover:text-white hover:border-industrial-accent/30'
                  }`}
              >
                <CatIcon className="w-4 h-4" />
                {cat.label}
              </button>
            )
          })}
        </motion.div>

        {/* Persona Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="w-full max-w-6xl"
        >
          <h2 className="text-center text-base font-medium text-gray-300 mb-4">
            {t('welcome.selectPersona')}
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
            <AnimatePresence mode="popLayout">
              {filteredPersonas.map((persona, idx) => (
                <motion.div
                  key={persona.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: 0.05 * idx }}
                  layout
                >
                  <PersonaCard
                    persona={persona}
                    isSelected={selectedPersona?.id === persona.id}
                    onSelect={setSelectedPersona}
                  />
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* Journey Preview */}
          <AnimatePresence>
            {selectedPersona && (
              <JourneyPreview persona={selectedPersona} />
            )}
          </AnimatePresence>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-6">
            <motion.button
              onClick={handleContinue}
              disabled={!selectedPersona}
              className={`flex items-center gap-3 px-8 py-4 rounded-xl font-semibold text-lg transition-all
                ${selectedPersona
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:from-cyan-400 hover:to-blue-400 shadow-lg shadow-cyan-500/30'
                  : 'bg-industrial-card text-gray-500 cursor-not-allowed'
                }`}
              whileHover={selectedPersona ? { scale: 1.05 } : undefined}
              whileTap={selectedPersona ? { scale: 0.95 } : undefined}
            >
              {t('welcome.continue')}
              <ArrowRight className="w-5 h-5" />
            </motion.button>

            <button
              onClick={handleSkip}
              className="text-gray-400 hover:text-white transition-colors text-sm underline underline-offset-4"
            >
              {t('welcome.skip')}
            </button>
          </div>
        </motion.div>

        {/* Footer hint */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-8 text-center text-xs text-gray-500"
        >
          {t('welcome.hint')}
        </motion.p>
      </div>
    </div>
  )
}

export default WelcomePage
