import React, { useState, useEffect, createContext, useContext } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X,
  ChevronRight,
  ChevronLeft,
  Check,
  Play,
  Home,
  Server,
  BarChart3,
  MessageSquare,
  Shield,
  Activity,
  Sparkles,
  Brain
} from 'lucide-react'
import { useI18n } from '../i18n'

// Onboarding Context
const OnboardingContext = createContext(null)

export function useOnboarding() {
  const context = useContext(OnboardingContext)
  if (!context) {
    throw new Error('useOnboarding must be used within OnboardingProvider')
  }
  return context
}

// Tour steps configuration
const TOUR_STEPS = [
  {
    id: 'welcome',
    target: null, // Full screen overlay
    title: 'Bienvenue sur SYNAPSIX',
    description: 'Votre plateforme d\'observabilité industrielle unifiée. Ce tour vous guidera à travers les principales fonctionnalités.',
    icon: Sparkles,
    path: null
  },
  {
    id: 'command-center',
    target: '[data-tour="command-center"]',
    title: 'Centre de Commande',
    description: 'Vue d\'ensemble de votre système avec les métriques clés, l\'état des services et les alertes actives.',
    icon: Home,
    path: '/'
  },
  {
    id: 'technical',
    target: '[data-tour="technical"]',
    title: 'Vue Technique',
    description: 'Surveillez votre infrastructure : VictoriaMetrics, OpenSearch, Kafka et le pipeline de données.',
    icon: Server,
    path: '/technical'
  },
  {
    id: 'business-kpi',
    target: '[data-tour="business-kpi"]',
    title: 'KPIs Business',
    description: 'Suivez vos indicateurs métier : OEE, production, qualité et état des équipements.',
    icon: BarChart3,
    path: '/business-kpi'
  },
  {
    id: 'ai-assistant',
    target: '[data-tour="ai-assistant"]',
    title: 'Assistant IA',
    description: 'Posez vos questions en langage naturel pour analyser vos données et obtenir des insights.',
    icon: MessageSquare,
    path: '/ai-assistant'
  },
  {
    id: 'security',
    target: '[data-tour="security"]',
    title: 'Sécurité & Conformité',
    description: 'Gérez la conformité (ISO 27001, NIS 2, RGPD), la vidéosurveillance et les audits.',
    icon: Shield,
    path: '/security'
  },
  {
    id: 'observability',
    target: '[data-tour="observability"]',
    title: 'Observabilité',
    description: 'Gérez vos SLOs, incidents et la remédiation automatique.',
    icon: Activity,
    path: '/observability'
  },
  {
    id: 'llm-observability',
    target: '[data-tour="llm-observability"]',
    title: 'Observabilité LLM',
    description: 'Surveillez les performances de vos modèles IA : latence, tokens, coûts et taux d\'erreur. Visualisez les métriques par fournisseur.',
    icon: Brain,
    path: '/observability/llm'
  },
  {
    id: 'complete',
    target: null,
    title: 'Tour terminé !',
    description: 'Vous êtes prêt à utiliser SYNAPSIX. N\'hésitez pas à explorer et à poser des questions à l\'assistant IA.',
    icon: Check,
    path: null
  }
]

export function OnboardingProvider({ children }) {
  const [isActive, setIsActive] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [hasCompletedTour, setHasCompletedTour] = useState(false)

  // Check if user has completed the tour
  useEffect(() => {
    const completed = localStorage.getItem('onboardingCompleted')
    setHasCompletedTour(completed === 'true')
  }, [])

  const startTour = () => {
    setCurrentStep(0)
    setIsActive(true)
  }

  const endTour = (completed = false) => {
    setIsActive(false)
    setCurrentStep(0)
    if (completed) {
      setHasCompletedTour(true)
      localStorage.setItem('onboardingCompleted', 'true')
    }
  }

  const nextStep = () => {
    if (currentStep < TOUR_STEPS.length - 1) {
      setCurrentStep(prev => prev + 1)
    } else {
      endTour(true)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const goToStep = (index) => {
    if (index >= 0 && index < TOUR_STEPS.length) {
      setCurrentStep(index)
    }
  }

  const resetTour = () => {
    localStorage.removeItem('onboardingCompleted')
    setHasCompletedTour(false)
  }

  return (
    <OnboardingContext.Provider value={{
      isActive,
      currentStep,
      steps: TOUR_STEPS,
      hasCompletedTour,
      startTour,
      endTour,
      nextStep,
      prevStep,
      goToStep,
      resetTour
    }}>
      {children}
    </OnboardingContext.Provider>
  )
}

// Tour Step Overlay Component
function TourStepOverlay() {
  const navigate = useNavigate()
  const location = useLocation()
  const { t } = useI18n()
  const {
    isActive,
    currentStep,
    steps,
    nextStep,
    prevStep,
    endTour
  } = useOnboarding()

  const step = steps[currentStep]
  const Icon = step?.icon || Sparkles
  const isFirstStep = currentStep === 0
  const isLastStep = currentStep === steps.length - 1
  const isFullScreen = !step?.target

  // Navigate to step path if needed
  useEffect(() => {
    if (isActive && step?.path && location.pathname !== step.path) {
      navigate(step.path)
    }
  }, [isActive, currentStep, step, location.pathname, navigate])

  if (!isActive) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100]"
      >
        {/* Backdrop */}
        <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

        {/* Tour Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className={`absolute ${isFullScreen
            ? 'left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2'
            : 'left-1/2 bottom-8 -translate-x-1/2'
          }`}
        >
          <div className="w-[420px] bg-industrial-dark border border-industrial-border rounded-2xl shadow-2xl overflow-hidden">
            {/* Header */}
            <div className="px-6 py-4 bg-gradient-to-r from-cyan-500/10 via-blue-500/10 to-purple-500/10 border-b border-industrial-border">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400 uppercase tracking-wider">
                      Étape {currentStep + 1} / {steps.length}
                    </p>
                    <h3 className="text-lg font-semibold text-white">{step.title}</h3>
                  </div>
                </div>
                <button
                  onClick={() => endTour(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="px-6 py-5">
              <p className="text-gray-300 leading-relaxed">{step.description}</p>

              {/* Progress Dots */}
              <div className="flex items-center justify-center gap-2 mt-6">
                {steps.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => {}}
                    className={`w-2 h-2 rounded-full transition-all ${
                      index === currentStep
                        ? 'w-6 bg-industrial-accent'
                        : index < currentStep
                          ? 'bg-green-500'
                          : 'bg-industrial-border'
                    }`}
                  />
                ))}
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-industrial-border bg-industrial-darker/50 flex items-center justify-between">
              <button
                onClick={() => endTour(false)}
                className="text-sm text-gray-400 hover:text-white transition-colors"
              >
                Passer le tour
              </button>

              <div className="flex items-center gap-2">
                {!isFirstStep && (
                  <button
                    onClick={prevStep}
                    className="flex items-center gap-1 px-4 py-2 rounded-lg border border-industrial-border text-gray-300 hover:bg-white/5 transition-colors"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    Précédent
                  </button>
                )}
                <button
                  onClick={nextStep}
                  className="flex items-center gap-1 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-medium hover:opacity-90 transition-opacity"
                >
                  {isLastStep ? (
                    <>
                      Terminer
                      <Check className="w-4 h-4" />
                    </>
                  ) : (
                    <>
                      Suivant
                      <ChevronRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

// Start Tour Button (for header or welcome page)
export function StartTourButton({ compact = false }) {
  const { startTour, hasCompletedTour } = useOnboarding()

  return (
    <button
      onClick={startTour}
      className={`flex items-center gap-2 ${
        compact
          ? 'p-2 rounded-lg hover:bg-white/5'
          : 'px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-500/30 hover:border-cyan-500/50'
      } text-cyan-400 transition-all`}
      title="Démarrer le tour guidé"
    >
      <Play className="w-4 h-4" />
      {!compact && <span className="text-sm">Tour guidé</span>}
    </button>
  )
}

// Main Onboarding Tour Component
function OnboardingTour() {
  return <TourStepOverlay />
}

export default OnboardingTour
