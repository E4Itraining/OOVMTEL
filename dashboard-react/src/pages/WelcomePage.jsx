import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Factory,
  Shield,
  LineChart,
  Server,
  Briefcase,
  Wrench,
  ChevronRight,
  Sparkles,
  ArrowRight,
  Users,
  Target,
  BarChart3,
  Lock,
  FileCheck,
  Cpu,
  Database,
  Activity,
  Zap,
  Eye,
  MessageSquare,
  CheckCircle2,
  Play
} from 'lucide-react'
import { useDashboard, USER_MODES } from '../context/DashboardContext'
import { useI18n } from '../i18n'

// Persona definitions with detailed descriptions
const PERSONAS = {
  OPERATIONS_MANAGER: {
    id: 'operations_manager',
    icon: Factory,
    color: 'purple',
    gradient: 'from-purple-500 to-pink-500',
    bgGradient: 'from-purple-500/20 to-pink-500/20',
    userMode: USER_MODES.BUSINESS,
    keyMetrics: ['OEE', 'Production', 'Quality', 'Availability'],
    quickActions: ['View Production Dashboard', 'Check Equipment Status', 'Review KPIs'],
    defaultView: '/command-center'
  },
  PLANT_DIRECTOR: {
    id: 'plant_director',
    icon: Briefcase,
    color: 'amber',
    gradient: 'from-amber-500 to-orange-500',
    bgGradient: 'from-amber-500/20 to-orange-500/20',
    userMode: USER_MODES.BUSINESS,
    keyMetrics: ['ROI', 'Cost Savings', 'Efficiency Trends', 'Business Impact'],
    quickActions: ['Executive Summary', 'Financial Impact', 'Strategic KPIs'],
    defaultView: '/command-center'
  },
  DEVOPS_ENGINEER: {
    id: 'devops_engineer',
    icon: Server,
    color: 'cyan',
    gradient: 'from-cyan-500 to-blue-500',
    bgGradient: 'from-cyan-500/20 to-blue-500/20',
    userMode: USER_MODES.TECH,
    keyMetrics: ['Latency', 'Throughput', 'Error Rate', 'Resource Usage'],
    quickActions: ['Check Pipeline Health', 'View Logs', 'Monitor Services'],
    defaultView: '/command-center'
  },
  SECURITY_ANALYST: {
    id: 'security_analyst',
    icon: Shield,
    color: 'red',
    gradient: 'from-red-500 to-rose-500',
    bgGradient: 'from-red-500/20 to-rose-500/20',
    userMode: USER_MODES.TECH,
    keyMetrics: ['Vulnerabilities', 'Compliance Score', 'Threats', 'Audit Status'],
    quickActions: ['Security Dashboard', 'Compliance Report', 'Threat Detection'],
    defaultView: '/command-center'
  },
  COMPLIANCE_OFFICER: {
    id: 'compliance_officer',
    icon: FileCheck,
    color: 'emerald',
    gradient: 'from-emerald-500 to-teal-500',
    bgGradient: 'from-emerald-500/20 to-teal-500/20',
    userMode: USER_MODES.BUSINESS,
    keyMetrics: ['ISO 27001', 'SOC2', 'GDPR', 'Audit Trail'],
    quickActions: ['Compliance Overview', 'Policy Status', 'Audit Reports'],
    defaultView: '/command-center'
  },
  DATA_ANALYST: {
    id: 'data_analyst',
    icon: LineChart,
    color: 'violet',
    gradient: 'from-violet-500 to-purple-500',
    bgGradient: 'from-violet-500/20 to-purple-500/20',
    userMode: USER_MODES.TECH,
    keyMetrics: ['Data Quality', 'Pipeline Health', 'Insights', 'Trends'],
    quickActions: ['Data Explorer', 'Analytics Dashboard', 'Custom Reports'],
    defaultView: '/command-center'
  }
}

// Feature highlights for the welcome screen
const FEATURES = [
  {
    icon: Eye,
    title: 'Unified Visibility',
    description: 'Single pane of glass for all your observability data'
  },
  {
    icon: Zap,
    title: 'Real-time Monitoring',
    description: 'Live metrics, logs, and traces aggregation'
  },
  {
    icon: MessageSquare,
    title: 'AI-Powered Insights',
    description: 'Natural language queries and intelligent recommendations'
  },
  {
    icon: Target,
    title: 'Goal-Oriented Views',
    description: 'Customized dashboards based on your role and objectives'
  }
]

// Animated background particles
function AnimatedBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Grid pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.03)_1px,transparent_1px)] bg-[size:60px_60px]" />

      {/* Floating orbs */}
      <motion.div
        className="absolute w-96 h-96 rounded-full bg-cyan-500/5 blur-3xl"
        animate={{
          x: [0, 100, 0],
          y: [0, -50, 0],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
        style={{ top: '10%', left: '10%' }}
      />
      <motion.div
        className="absolute w-80 h-80 rounded-full bg-purple-500/5 blur-3xl"
        animate={{
          x: [0, -80, 0],
          y: [0, 80, 0],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
        style={{ top: '50%', right: '10%' }}
      />
      <motion.div
        className="absolute w-64 h-64 rounded-full bg-emerald-500/5 blur-3xl"
        animate={{
          x: [0, 60, 0],
          y: [0, -60, 0],
        }}
        transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
        style={{ bottom: '10%', left: '30%' }}
      />
    </div>
  )
}

// Persona Card Component
function PersonaCard({ persona, personaKey, isSelected, onSelect, t }) {
  const Icon = persona.icon

  return (
    <motion.button
      onClick={() => onSelect(personaKey)}
      className={`relative p-6 rounded-2xl border-2 transition-all duration-300 text-left w-full
        ${isSelected
          ? `border-${persona.color}-500 bg-gradient-to-br ${persona.bgGradient}`
          : 'border-industrial-border bg-industrial-card/50 hover:border-gray-600 hover:bg-industrial-card'
        }`}
      whileHover={{ scale: 1.02, y: -4 }}
      whileTap={{ scale: 0.98 }}
    >
      {isSelected && (
        <motion.div
          className="absolute top-3 right-3"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
        >
          <CheckCircle2 className={`w-6 h-6 text-${persona.color}-400`} />
        </motion.div>
      )}

      <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${persona.gradient} flex items-center justify-center mb-4 shadow-lg`}>
        <Icon className="w-7 h-7 text-white" />
      </div>

      <h3 className="text-lg font-semibold text-white mb-2">
        {t(`personas.${persona.id}.title`)}
      </h3>
      <p className="text-sm text-gray-400 mb-4">
        {t(`personas.${persona.id}.description`)}
      </p>

      <div className="flex flex-wrap gap-2">
        {persona.keyMetrics.slice(0, 3).map((metric, i) => (
          <span
            key={i}
            className={`px-2 py-1 rounded-md text-xs font-medium
              ${isSelected
                ? `bg-${persona.color}-500/20 text-${persona.color}-300`
                : 'bg-white/5 text-gray-400'
              }`}
          >
            {metric}
          </span>
        ))}
      </div>
    </motion.button>
  )
}

// Quick Start Guide Step
function GuideStep({ step, index, isActive }) {
  return (
    <motion.div
      className={`flex items-start gap-4 p-4 rounded-xl transition-all
        ${isActive ? 'bg-industrial-accent/10 border border-industrial-accent/30' : 'opacity-60'}`}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: isActive ? 1 : 0.6, x: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
        ${isActive ? 'bg-industrial-accent text-white' : 'bg-gray-700 text-gray-400'}`}>
        {index + 1}
      </div>
      <div>
        <h4 className={`font-medium ${isActive ? 'text-white' : 'text-gray-400'}`}>
          {step.title}
        </h4>
        <p className="text-sm text-gray-500 mt-1">{step.description}</p>
      </div>
    </motion.div>
  )
}

function WelcomePage() {
  const navigate = useNavigate()
  const { setUserMode, setSelectedPersona } = useDashboard()
  const { t } = useI18n()

  const [selectedPersonaKey, setSelectedPersonaKey] = useState(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [showGuide, setShowGuide] = useState(false)
  const [isFirstVisit, setIsFirstVisit] = useState(true)

  // Check if user has visited before
  useEffect(() => {
    const hasVisited = localStorage.getItem('oovmtel_has_visited')
    if (hasVisited) {
      setIsFirstVisit(false)
    }
  }, [])

  const guideSteps = [
    { title: t('guide.step1.title'), description: t('guide.step1.description') },
    { title: t('guide.step2.title'), description: t('guide.step2.description') },
    { title: t('guide.step3.title'), description: t('guide.step3.description') },
    { title: t('guide.step4.title'), description: t('guide.step4.description') }
  ]

  const handlePersonaSelect = (personaKey) => {
    setSelectedPersonaKey(personaKey)
  }

  const handleContinue = () => {
    if (selectedPersonaKey) {
      const persona = PERSONAS[selectedPersonaKey]
      setUserMode(persona.userMode)
      if (setSelectedPersona) {
        setSelectedPersona(selectedPersonaKey)
      }
      localStorage.setItem('oovmtel_selected_persona', selectedPersonaKey)
      localStorage.setItem('oovmtel_has_visited', 'true')
      navigate(persona.defaultView)
    }
  }

  const handleSkip = () => {
    localStorage.setItem('oovmtel_has_visited', 'true')
    navigate('/command-center')
  }

  return (
    <div className="min-h-screen bg-industrial-darker relative overflow-hidden">
      <AnimatedBackground />

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-industrial-accent/10 border border-industrial-accent/30 mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Sparkles className="w-4 h-4 text-industrial-accent" />
            <span className="text-sm font-medium text-industrial-accent">
              {t('welcome.badge')}
            </span>
          </motion.div>

          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            {t('welcome.title')}
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            {t('welcome.subtitle')}
          </p>
        </motion.div>

        {/* Features Row */}
        <motion.div
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          {FEATURES.map((feature, i) => (
            <motion.div
              key={i}
              className="p-4 rounded-xl bg-industrial-card/30 border border-industrial-border"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.1 }}
            >
              <feature.icon className="w-8 h-8 text-industrial-accent mb-3" />
              <h3 className="font-medium text-white text-sm mb-1">{feature.title}</h3>
              <p className="text-xs text-gray-500">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Persona Selection */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-white mb-2">
              {t('welcome.selectPersona')}
            </h2>
            <p className="text-gray-400">
              {t('welcome.selectPersonaDescription')}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {Object.entries(PERSONAS).map(([key, persona], i) => (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 + i * 0.1 }}
              >
                <PersonaCard
                  persona={persona}
                  personaKey={key}
                  isSelected={selectedPersonaKey === key}
                  onSelect={handlePersonaSelect}
                  t={t}
                />
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          className="flex items-center justify-center gap-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <button
            onClick={handleSkip}
            className="px-6 py-3 rounded-xl text-gray-400 hover:text-white transition-colors"
          >
            {t('welcome.skip')}
          </button>

          <motion.button
            onClick={handleContinue}
            disabled={!selectedPersonaKey}
            className={`flex items-center gap-2 px-8 py-3 rounded-xl font-semibold transition-all
              ${selectedPersonaKey
                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40'
                : 'bg-gray-700 text-gray-400 cursor-not-allowed'
              }`}
            whileHover={selectedPersonaKey ? { scale: 1.02 } : {}}
            whileTap={selectedPersonaKey ? { scale: 0.98 } : {}}
          >
            <Play className="w-5 h-5" />
            {t('welcome.getStarted')}
            <ArrowRight className="w-5 h-5" />
          </motion.button>
        </motion.div>

        {/* Quick Start Guide Toggle */}
        {isFirstVisit && (
          <motion.div
            className="mt-12 text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
          >
            <button
              onClick={() => setShowGuide(!showGuide)}
              className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            >
              <ChevronRight className={`w-4 h-4 transition-transform ${showGuide ? 'rotate-90' : ''}`} />
              {t('welcome.showGuide')}
            </button>

            <AnimatePresence>
              {showGuide && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden mt-6"
                >
                  <div className="max-w-lg mx-auto space-y-3">
                    {guideSteps.map((step, i) => (
                      <GuideStep
                        key={i}
                        step={step}
                        index={i}
                        isActive={i <= currentStep}
                      />
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default WelcomePage
