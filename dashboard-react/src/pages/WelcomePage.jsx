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
  CheckCircle2
} from 'lucide-react'
import { useI18n } from '../i18n'

// Define the extended personas for French enterprise roles
export const PERSONAS = {
  // Executive/Strategic personas
  DIRIGEANT: 'dirigeant',
  DSI: 'dsi',
  // Security/Compliance personas
  RSSI: 'rssi',
  RSI: 'rsi',
  DPO_JURISTE: 'dpo_juriste',
  // Operational personas (kept from original)
  OPERATIONS_MANAGER: 'operations_manager',
  DEVOPS_ENGINEER: 'devops_engineer',
  DATA_ANALYST: 'data_analyst'
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
  [PERSONAS.RSSI]: {
    name: 'Parcours RSSI',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Posture Sécurité', route: '/security', icon: Shield },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'Vulnérabilités', route: '/security#vulnerabilities', icon: Lock },
      { id: JOURNEY_STAGES.ACTION, label: 'Impact & Préconisations', route: '/impact-analysis', icon: Target },
      { id: JOURNEY_STAGES.MONITORING, label: 'Conformité', route: '/security#compliance', icon: FileCheck }
    ],
    defaultRoute: '/security',
    focusAreas: ['cybersecurity', 'threats', 'compliance', 'incidents', 'audit']
  },
  [PERSONAS.RSI]: {
    name: 'Parcours RSI',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Systèmes', route: '/technical', icon: Cpu },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'Observabilité', route: '/observability', icon: Eye },
      { id: JOURNEY_STAGES.ACTION, label: 'Remédiation', route: '/observability#runbooks', icon: Target },
      { id: JOURNEY_STAGES.MONITORING, label: 'Monitoring', route: '/grafana', icon: Activity }
    ],
    defaultRoute: '/technical',
    focusAreas: ['systems', 'operations', 'maintenance', 'support', 'monitoring']
  },
  [PERSONAS.DPO_JURISTE]: {
    name: 'Parcours DPO/Juriste',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Conformité RGPD', route: '/security#compliance', icon: FileCheck },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'Régulations EU', route: '/security#euRegulations', icon: Scale },
      { id: JOURNEY_STAGES.ACTION, label: 'Impact & Préconisations', route: '/impact-analysis', icon: Target },
      { id: JOURNEY_STAGES.MONITORING, label: 'Audit Trail', route: '/security#audit', icon: Eye }
    ],
    defaultRoute: '/security',
    focusAreas: ['rgpd', 'nis2', 'ai-act', 'privacy', 'legal', 'compliance']
  },
  [PERSONAS.OPERATIONS_MANAGER]: {
    name: 'Parcours Opérations',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Centre de Commande', route: '/command-center', icon: Layers },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'KPIs Production', route: '/business-kpi', icon: BarChart3 },
      { id: JOURNEY_STAGES.ACTION, label: 'Impact & Préconisations', route: '/impact-analysis', icon: Target },
      { id: JOURNEY_STAGES.MONITORING, label: 'Équipements', route: '/business-kpi#equipment', icon: Activity }
    ],
    defaultRoute: '/command-center',
    focusAreas: ['production', 'oee', 'equipment', 'quality', 'maintenance']
  },
  [PERSONAS.DEVOPS_ENGINEER]: {
    name: 'Parcours DevOps',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Infrastructure', route: '/technical', icon: Server },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'Pipelines', route: '/kafka', icon: Network },
      { id: JOURNEY_STAGES.ACTION, label: 'Observabilité', route: '/observability', icon: Eye },
      { id: JOURNEY_STAGES.MONITORING, label: 'Logs & Traces', route: '/opensearch', icon: Activity }
    ],
    defaultRoute: '/technical',
    focusAreas: ['infrastructure', 'pipelines', 'services', 'automation', 'monitoring']
  },
  [PERSONAS.DATA_ANALYST]: {
    name: 'Parcours Data Analyst',
    stages: [
      { id: JOURNEY_STAGES.DISCOVERY, label: 'Vue Données', route: '/dashboard', icon: BarChart3 },
      { id: JOURNEY_STAGES.ASSESSMENT, label: 'Métriques', route: '/grafana', icon: Activity },
      { id: JOURNEY_STAGES.ACTION, label: 'Impact & Préconisations', route: '/impact-analysis', icon: Target },
      { id: JOURNEY_STAGES.MONITORING, label: 'Exploration', route: '/opensearch', icon: Eye }
    ],
    defaultRoute: '/dashboard',
    focusAreas: ['metrics', 'logs', 'traces', 'analytics', 'patterns']
  }
}

const getPersonaConfig = (t) => [
  // Strategic Leadership
  {
    id: PERSONAS.DIRIGEANT,
    icon: Building2,
    color: 'from-indigo-500 to-purple-600',
    bgColor: 'bg-indigo-500/10',
    borderColor: 'border-indigo-500/30',
    textColor: 'text-indigo-400',
    category: 'strategic',
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
    id: PERSONAS.DSI,
    icon: Cpu,
    color: 'from-blue-500 to-cyan-600',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    textColor: 'text-blue-400',
    category: 'strategic',
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
  // Security & Compliance
  {
    id: PERSONAS.RSSI,
    icon: Shield,
    color: 'from-red-500 to-orange-600',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    textColor: 'text-red-400',
    category: 'security',
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
    id: PERSONAS.RSI,
    icon: Server,
    color: 'from-cyan-500 to-teal-600',
    bgColor: 'bg-cyan-500/10',
    borderColor: 'border-cyan-500/30',
    textColor: 'text-cyan-400',
    category: 'operational',
    title: t('personas.rsi.title'),
    description: t('personas.rsi.description'),
    features: [
      t('personas.rsi.feature1'),
      t('personas.rsi.feature2'),
      t('personas.rsi.feature3')
    ],
    defaultRoute: '/technical',
    focusAreas: ['systems', 'operations', 'support']
  },
  {
    id: PERSONAS.DPO_JURISTE,
    icon: Scale,
    color: 'from-emerald-500 to-green-600',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/30',
    textColor: 'text-emerald-400',
    category: 'security',
    title: t('personas.dpoJuriste.title'),
    description: t('personas.dpoJuriste.description'),
    features: [
      t('personas.dpoJuriste.feature1'),
      t('personas.dpoJuriste.feature2'),
      t('personas.dpoJuriste.feature3')
    ],
    defaultRoute: '/security',
    focusAreas: ['rgpd', 'compliance', 'legal']
  },
  // Operational
  {
    id: PERSONAS.OPERATIONS_MANAGER,
    icon: Briefcase,
    color: 'from-purple-500 to-pink-600',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30',
    textColor: 'text-purple-400',
    category: 'operational',
    title: t('personas.operationsManager.title'),
    description: t('personas.operationsManager.description'),
    features: [
      t('personas.operationsManager.feature1'),
      t('personas.operationsManager.feature2'),
      t('personas.operationsManager.feature3')
    ],
    defaultRoute: '/command-center',
    focusAreas: ['production', 'oee', 'equipment']
  },
  {
    id: PERSONAS.DEVOPS_ENGINEER,
    icon: Network,
    color: 'from-amber-500 to-orange-600',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/30',
    textColor: 'text-amber-400',
    category: 'operational',
    title: t('personas.devopsEngineer.title'),
    description: t('personas.devopsEngineer.description'),
    features: [
      t('personas.devopsEngineer.feature1'),
      t('personas.devopsEngineer.feature2'),
      t('personas.devopsEngineer.feature3')
    ],
    defaultRoute: '/technical',
    focusAreas: ['infrastructure', 'pipelines', 'automation']
  },
  {
    id: PERSONAS.DATA_ANALYST,
    icon: BarChart3,
    color: 'from-rose-500 to-red-600',
    bgColor: 'bg-rose-500/10',
    borderColor: 'border-rose-500/30',
    textColor: 'text-rose-400',
    category: 'operational',
    title: t('personas.dataAnalyst.title'),
    description: t('personas.dataAnalyst.description'),
    features: [
      t('personas.dataAnalyst.feature1'),
      t('personas.dataAnalyst.feature2'),
      t('personas.dataAnalyst.feature3')
    ],
    defaultRoute: '/observability',
    focusAreas: ['metrics', 'logs', 'traces']
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
      {isSelected && (
        <motion.div
          className="absolute top-3 right-3"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 500 }}
        >
          <div className={`w-6 h-6 rounded-full bg-gradient-to-br ${persona.color} flex items-center justify-center`}>
            <CheckCircle2 className="w-4 h-4 text-white" />
          </div>
        </motion.div>
      )}

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
    { id: 'all', label: 'Tous les profils', icon: Users },
    { id: 'strategic', label: 'Direction', icon: Building2 },
    { id: 'security', label: 'Sécurité & Conformité', icon: Shield },
    { id: 'operational', label: 'Opérationnel', icon: Briefcase }
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
