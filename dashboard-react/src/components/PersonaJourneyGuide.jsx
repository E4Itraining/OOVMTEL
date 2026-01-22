import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ChevronRight,
  ChevronLeft,
  CheckCircle2,
  Circle,
  Target,
  Sparkles,
  X,
  Play,
  Pause,
  RotateCcw,
  Eye,
  TrendingUp,
  Shield,
  Activity,
  BarChart3,
  Factory,
  Server,
  Brain,
  AlertTriangle,
  Database,
  Gauge,
  Settings,
  FileCheck,
  Cpu,
  Network,
  Layers,
  Radio
} from 'lucide-react'
import { PERSONAS, PERSONA_JOURNEYS, JOURNEY_STAGES } from '../pages/WelcomePage'

// Extended journeys with new pages
const EXTENDED_JOURNEYS = {
  // BUSINESS Personas
  [PERSONAS.DIRIGEANT]: {
    name: 'Parcours Dirigeant',
    description: 'Vision strategique et gouvernance',
    stages: [
      { id: 'overview', label: 'Vue Globale', route: '/command-center', icon: Eye, description: 'Tableau de bord executif' },
      { id: 'kpis', label: 'KPIs Metier', route: '/business-kpi', icon: TrendingUp, description: 'Indicateurs cles de performance' },
      { id: 'correlation', label: 'Correlation IT-OT-IA', route: '/correlation', icon: Network, description: 'Impact croise des systemes' },
      { id: 'impact', label: 'Analyse Impact', route: '/impact-analysis', icon: Target, description: 'Preconisations strategiques' },
      { id: 'assistant', label: 'Assistant IA', route: '/ai-assistant', icon: Sparkles, description: 'Questions en langage naturel' }
    ],
    color: 'from-indigo-500 to-purple-600',
    bgColor: 'bg-indigo-500/10'
  },
  [PERSONAS.DIRECTEUR_PRODUCTION]: {
    name: 'Parcours Production',
    description: 'Performance et efficience operationnelle',
    stages: [
      { id: 'command', label: 'Centre Commande', route: '/command-center', icon: Activity, description: 'Vue temps reel production' },
      { id: 'industrial', label: 'Observabilite Industrielle', route: '/industrial-observability', icon: Factory, description: 'Equipements et processus ISA-95' },
      { id: 'kpis', label: 'OEE & Performance', route: '/business-kpi', icon: Gauge, description: 'Metriques de production' },
      { id: 'simulators', label: 'Simulateurs', route: '/simulators', icon: Radio, description: 'Test scenarios production' },
      { id: 'impact', label: 'Optimisations', route: '/impact-analysis', icon: Target, description: 'Recommandations amelioration' }
    ],
    color: 'from-fuchsia-500 to-pink-600',
    bgColor: 'bg-fuchsia-500/10'
  },
  // TECH Personas
  [PERSONAS.DSI]: {
    name: 'Parcours DSI',
    description: 'Gouvernance IT et transformation digitale',
    stages: [
      { id: 'infra', label: 'Infrastructure', route: '/technical', icon: Server, description: 'Sante des systemes' },
      { id: 'correlation', label: 'Correlation IT-OT', route: '/correlation', icon: Network, description: 'Dependances inter-domaines' },
      { id: 'security', label: 'Securite', route: '/cybersecurity-ot', icon: Shield, description: 'Posture de securite globale' },
      { id: 'observability', label: 'Observabilite', route: '/observability', icon: Eye, description: 'SLOs et incidents' },
      { id: 'ai-obs', label: 'IA & ML', route: '/ai-observability', icon: Brain, description: 'Monitoring des modeles IA' }
    ],
    color: 'from-blue-500 to-cyan-600',
    bgColor: 'bg-blue-500/10'
  },
  [PERSONAS.DEVOPS_SRE]: {
    name: 'Parcours DevOps/SRE',
    description: 'Fiabilite et operations',
    stages: [
      { id: 'technical', label: 'Vue Technique', route: '/technical', icon: Server, description: 'Metriques infrastructure' },
      { id: 'observability', label: 'SLOs & Alertes', route: '/observability', icon: AlertTriangle, description: 'Objectifs de niveau de service' },
      { id: 'logs', label: 'Logs & Traces', route: '/opensearch', icon: Database, description: 'Analyse des logs' },
      { id: 'simulators', label: 'Simulateurs', route: '/simulators', icon: Radio, description: 'Generation de charge' },
      { id: 'correlation', label: 'Correlation', route: '/correlation', icon: Layers, description: 'Root cause analysis' }
    ],
    color: 'from-cyan-500 to-teal-600',
    bgColor: 'bg-cyan-500/10'
  },
  [PERSONAS.DATA_MLOPS]: {
    name: 'Parcours Data/MLOps',
    description: 'Donnees et modeles ML',
    stages: [
      { id: 'kafka', label: 'Pipelines Data', route: '/kafka', icon: Database, description: 'Flux de donnees Kafka' },
      { id: 'ai-obs', label: 'AI Observability', route: '/ai-observability', icon: Brain, description: 'Performance des modeles' },
      { id: 'correlation', label: 'Correlation IA', route: '/correlation', icon: Network, description: 'Impact IA sur IT/OT' },
      { id: 'simulators', label: 'Simulateurs', route: '/simulators', icon: Radio, description: 'Generation donnees test' },
      { id: 'grafana', label: 'Visualisation', route: '/grafana', icon: BarChart3, description: 'Dashboards analytiques' }
    ],
    color: 'from-sky-500 to-blue-600',
    bgColor: 'bg-sky-500/10'
  },
  // SECURITY Personas
  [PERSONAS.RSSI]: {
    name: 'Parcours RSSI',
    description: 'Securite et conformite',
    stages: [
      { id: 'cyber', label: 'Cybersecurite OT/IT', route: '/cybersecurity-ot', icon: Shield, description: 'Vue securite unifiee' },
      { id: 'compliance', label: 'Conformite', route: '/security', icon: FileCheck, description: 'Referentiels et audits' },
      { id: 'correlation', label: 'Correlation Menaces', route: '/correlation', icon: Network, description: 'Propagation des risques' },
      { id: 'logs', label: 'Investigation', route: '/opensearch', icon: Eye, description: 'Forensics et logs' },
      { id: 'impact', label: 'Impact Business', route: '/impact-analysis', icon: Target, description: 'Consequences metier' }
    ],
    color: 'from-red-500 to-orange-600',
    bgColor: 'bg-red-500/10'
  },
  [PERSONAS.ANALYSTE_SOC]: {
    name: 'Parcours Analyste SOC',
    description: 'Detection et reponse',
    stages: [
      { id: 'alerts', label: 'Alertes Securite', route: '/cybersecurity-ot', icon: AlertTriangle, description: 'Evenements en cours' },
      { id: 'logs', label: 'Investigation', route: '/opensearch', icon: Database, description: 'Analyse forensique' },
      { id: 'correlation', label: 'Correlation', route: '/correlation', icon: Layers, description: 'Chaines d\'attaque' },
      { id: 'compliance', label: 'Conformite', route: '/security', icon: Shield, description: 'Rapports compliance' },
      { id: 'grafana', label: 'Visualisation', route: '/grafana', icon: Activity, description: 'Dashboards SOC' }
    ],
    color: 'from-orange-500 to-amber-600',
    bgColor: 'bg-orange-500/10'
  },
  // GREENOPS Personas
  [PERSONAS.GREEN_IT_MANAGER]: {
    name: 'Parcours Green IT',
    description: 'Efficience energetique',
    stages: [
      { id: 'technical', label: 'Energie IT', route: '/technical', icon: Cpu, description: 'Consommation infrastructure' },
      { id: 'industrial', label: 'Energie OT', route: '/industrial-observability', icon: Factory, description: 'Consommation equipements' },
      { id: 'correlation', label: 'Correlation', route: '/correlation', icon: Network, description: 'Impact energetique croise' },
      { id: 'grafana', label: 'PUE & Metriques', route: '/grafana', icon: Gauge, description: 'Indicateurs green' },
      { id: 'impact', label: 'Plan Optimisation', route: '/impact-analysis', icon: Target, description: 'Actions d\'amelioration' }
    ],
    color: 'from-green-500 to-teal-600',
    bgColor: 'bg-green-500/10'
  }
}

// Get journey for a persona (use extended if available, fallback to original)
const getJourneyForPersona = (personaId) => {
  return EXTENDED_JOURNEYS[personaId] || PERSONA_JOURNEYS[personaId]
}

// Journey Progress Indicator
function JourneyProgress({ stages, currentStageIndex, onStageClick }) {
  return (
    <div className="flex items-center justify-between w-full">
      {stages.map((stage, idx) => {
        const Icon = stage.icon
        const isCompleted = idx < currentStageIndex
        const isCurrent = idx === currentStageIndex
        const isPending = idx > currentStageIndex

        return (
          <React.Fragment key={stage.id}>
            <button
              onClick={() => onStageClick(idx)}
              className={`flex flex-col items-center gap-1 transition-all ${
                isCurrent ? 'scale-110' : 'hover:scale-105'
              }`}
            >
              <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                isCompleted ? 'bg-green-500' :
                isCurrent ? 'bg-cyan-500 ring-2 ring-cyan-500/50 ring-offset-2 ring-offset-industrial-darker' :
                'bg-industrial-card border border-industrial-border'
              }`}>
                {isCompleted ? (
                  <CheckCircle2 className="w-5 h-5 text-white" />
                ) : (
                  <Icon className={`w-5 h-5 ${isCurrent ? 'text-white' : 'text-gray-400'}`} />
                )}
              </div>
              <span className={`text-xs max-w-[80px] text-center ${
                isCurrent ? 'text-cyan-400 font-medium' :
                isCompleted ? 'text-green-400' :
                'text-gray-500'
              }`}>
                {stage.label}
              </span>
            </button>

            {idx < stages.length - 1 && (
              <div className={`flex-1 h-0.5 mx-2 ${
                isCompleted ? 'bg-green-500' :
                isCurrent ? 'bg-gradient-to-r from-green-500 to-gray-600' :
                'bg-gray-700'
              }`} />
            )}
          </React.Fragment>
        )
      })}
    </div>
  )
}

// Main Component
function PersonaJourneyGuide() {
  const navigate = useNavigate()
  const location = useLocation()
  const [isExpanded, setIsExpanded] = useState(true)
  const [isMinimized, setIsMinimized] = useState(false)
  const [currentStageIndex, setCurrentStageIndex] = useState(0)

  // Get persona from localStorage
  const personaId = localStorage.getItem('selectedPersona')
  const journey = personaId ? getJourneyForPersona(personaId) : null

  // Update current stage based on location
  useEffect(() => {
    if (journey) {
      const stageIndex = journey.stages.findIndex(s => s.route === location.pathname)
      if (stageIndex !== -1) {
        setCurrentStageIndex(stageIndex)
        localStorage.setItem('currentJourneyStage', stageIndex.toString())
      }
    }
  }, [location.pathname, journey])

  // Load saved stage index
  useEffect(() => {
    const savedIndex = localStorage.getItem('currentJourneyStage')
    if (savedIndex) {
      setCurrentStageIndex(parseInt(savedIndex, 10))
    }
  }, [])

  if (!journey || !personaId) {
    return null
  }

  const currentStage = journey.stages[currentStageIndex]
  const nextStage = journey.stages[currentStageIndex + 1]
  const prevStage = journey.stages[currentStageIndex - 1]
  const progress = ((currentStageIndex + 1) / journey.stages.length) * 100

  const handleNavigateToStage = (index) => {
    const stage = journey.stages[index]
    if (stage) {
      setCurrentStageIndex(index)
      localStorage.setItem('currentJourneyStage', index.toString())
      navigate(stage.route)
    }
  }

  const handleNext = () => {
    if (nextStage) {
      handleNavigateToStage(currentStageIndex + 1)
    }
  }

  const handlePrev = () => {
    if (prevStage) {
      handleNavigateToStage(currentStageIndex - 1)
    }
  }

  const handleReset = () => {
    setCurrentStageIndex(0)
    localStorage.setItem('currentJourneyStage', '0')
    navigate(journey.stages[0].route)
  }

  if (isMinimized) {
    return (
      <motion.button
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        onClick={() => setIsMinimized(false)}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg shadow-cyan-500/30 hover:scale-105 transition-transform"
      >
        <Target className="w-5 h-5" />
        <span className="font-medium">Parcours: {Math.round(progress)}%</span>
      </motion.button>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 w-full max-w-4xl px-4"
    >
      <div className={`rounded-2xl bg-industrial-card/95 backdrop-blur-xl border border-industrial-border shadow-2xl overflow-hidden transition-all ${
        isExpanded ? '' : 'max-h-20'
      }`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-industrial-border">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${journey.color} flex items-center justify-center`}>
              <Target className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-white">{journey.name}</h3>
              <p className="text-xs text-gray-400">{journey.description}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Progress indicator */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-industrial-darker">
              <div className="w-20 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-cyan-500 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                />
              </div>
              <span className="text-xs text-cyan-400 font-mono">{Math.round(progress)}%</span>
            </div>

            {/* Controls */}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors"
            >
              {isExpanded ? <ChevronLeft className="w-4 h-4 rotate-90" /> : <ChevronLeft className="w-4 h-4 -rotate-90" />}
            </button>
            <button
              onClick={() => setIsMinimized(true)}
              className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Expanded Content */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              {/* Progress Steps */}
              <div className="p-4 border-b border-industrial-border">
                <JourneyProgress
                  stages={journey.stages}
                  currentStageIndex={currentStageIndex}
                  onStageClick={handleNavigateToStage}
                />
              </div>

              {/* Current Stage Info */}
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {/* Previous */}
                    <button
                      onClick={handlePrev}
                      disabled={!prevStage}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                        prevStage
                          ? 'bg-industrial-darker text-gray-300 hover:text-white hover:bg-white/5'
                          : 'bg-industrial-darker/50 text-gray-600 cursor-not-allowed'
                      }`}
                    >
                      <ChevronLeft className="w-4 h-4" />
                      {prevStage && <span className="text-sm">{prevStage.label}</span>}
                    </button>

                    {/* Current */}
                    <div className="text-center">
                      <p className="text-xs text-gray-500 mb-1">Etape actuelle</p>
                      <p className="text-lg font-semibold text-white">{currentStage.label}</p>
                      <p className="text-xs text-gray-400">{currentStage.description}</p>
                    </div>

                    {/* Next */}
                    <button
                      onClick={handleNext}
                      disabled={!nextStage}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                        nextStage
                          ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:opacity-90'
                          : 'bg-green-500/20 text-green-400 cursor-default'
                      }`}
                    >
                      {nextStage ? (
                        <>
                          <span className="text-sm">{nextStage.label}</span>
                          <ChevronRight className="w-4 h-4" />
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="w-4 h-4" />
                          <span className="text-sm">Termine!</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Reset */}
                  <button
                    onClick={handleReset}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-all"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span className="text-sm">Recommencer</span>
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

export default PersonaJourneyGuide
