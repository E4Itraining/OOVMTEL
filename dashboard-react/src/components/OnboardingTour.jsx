import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X,
  ChevronRight,
  ChevronLeft,
  Home,
  BarChart3,
  MessageSquare,
  Bell,
  Search,
  Settings,
  Check,
  Sparkles,
  Target,
  Zap
} from 'lucide-react'
import { useI18n } from '../i18n'

// Tour steps configuration
const TOUR_STEPS = [
  {
    id: 'welcome',
    target: null, // Modal step, no target
    title: 'onboarding.welcome.title',
    description: 'onboarding.welcome.description',
    icon: Sparkles,
    position: 'center'
  },
  {
    id: 'sidebar',
    target: '[data-tour="sidebar"]',
    title: 'onboarding.sidebar.title',
    description: 'onboarding.sidebar.description',
    icon: Home,
    position: 'right'
  },
  {
    id: 'search',
    target: '[data-tour="search"]',
    title: 'onboarding.search.title',
    description: 'onboarding.search.description',
    icon: Search,
    position: 'bottom'
  },
  {
    id: 'notifications',
    target: '[data-tour="notifications"]',
    title: 'onboarding.notifications.title',
    description: 'onboarding.notifications.description',
    icon: Bell,
    position: 'bottom-left'
  },
  {
    id: 'kpi',
    target: '[data-tour="kpi"]',
    title: 'onboarding.kpi.title',
    description: 'onboarding.kpi.description',
    icon: BarChart3,
    position: 'bottom'
  },
  {
    id: 'ai-assistant',
    target: '[data-tour="ai-assistant"]',
    title: 'onboarding.aiAssistant.title',
    description: 'onboarding.aiAssistant.description',
    icon: MessageSquare,
    position: 'left'
  },
  {
    id: 'mode-toggle',
    target: '[data-tour="mode-toggle"]',
    title: 'onboarding.modeToggle.title',
    description: 'onboarding.modeToggle.description',
    icon: Settings,
    position: 'top'
  },
  {
    id: 'complete',
    target: null,
    title: 'onboarding.complete.title',
    description: 'onboarding.complete.description',
    icon: Check,
    position: 'center'
  }
]

// Checklist items for post-tour
const CHECKLIST_ITEMS = [
  { id: 'explore-dashboard', labelKey: 'onboarding.checklist.exploreDashboard', completed: false },
  { id: 'configure-alerts', labelKey: 'onboarding.checklist.configureAlerts', completed: false },
  { id: 'try-ai', labelKey: 'onboarding.checklist.tryAI', completed: false },
  { id: 'customize-view', labelKey: 'onboarding.checklist.customizeView', completed: false }
]

function TourTooltip({ step, position, onNext, onPrev, onSkip, currentStep, totalSteps }) {
  const { t } = useI18n()
  const Icon = step.icon

  const positionClasses = {
    'center': 'fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2',
    'right': 'absolute left-full ml-4 top-1/2 -translate-y-1/2',
    'left': 'absolute right-full mr-4 top-1/2 -translate-y-1/2',
    'bottom': 'absolute top-full mt-4 left-1/2 -translate-x-1/2',
    'top': 'absolute bottom-full mb-4 left-1/2 -translate-x-1/2',
    'bottom-left': 'absolute top-full mt-4 right-0',
    'bottom-right': 'absolute top-full mt-4 left-0'
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className={`${position === 'center' ? positionClasses.center : ''} w-80 bg-industrial-dark border border-industrial-border rounded-xl shadow-2xl z-[100] overflow-hidden`}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-cyan-500/20 to-purple-500/20 p-4 border-b border-industrial-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
            <Icon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-white">
              {t(step.title) || step.title}
            </h3>
            <p className="text-xs text-gray-400">
              {currentStep + 1} / {totalSteps}
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <p className="text-sm text-gray-300 leading-relaxed">
          {t(step.description) || step.description}
        </p>
      </div>

      {/* Progress dots */}
      <div className="flex justify-center gap-1.5 pb-3">
        {[...Array(totalSteps)].map((_, i) => (
          <div
            key={i}
            className={`w-2 h-2 rounded-full transition-colors ${
              i === currentStep
                ? 'bg-cyan-400'
                : i < currentStep
                ? 'bg-cyan-400/50'
                : 'bg-industrial-border'
            }`}
          />
        ))}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between p-4 border-t border-industrial-border bg-industrial-darker/50">
        <button
          onClick={onSkip}
          className="text-sm text-gray-500 hover:text-white transition-colors"
        >
          {t('onboarding.skip') || 'Skip tour'}
        </button>

        <div className="flex gap-2">
          {currentStep > 0 && (
            <button
              onClick={onPrev}
              className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-400 hover:text-white transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
              {t('common.back') || 'Back'}
            </button>
          )}

          <button
            onClick={onNext}
            className="flex items-center gap-1 px-4 py-1.5 text-sm bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-lg hover:from-cyan-400 hover:to-blue-400 transition-colors"
          >
            {currentStep === totalSteps - 1 ? (
              <>
                {t('onboarding.finish') || 'Finish'}
                <Check className="w-4 h-4" />
              </>
            ) : (
              <>
                {t('common.next') || 'Next'}
                <ChevronRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </motion.div>
  )
}

function Spotlight({ target }) {
  const [rect, setRect] = useState(null)

  useEffect(() => {
    if (target) {
      const element = document.querySelector(target)
      if (element) {
        const updateRect = () => {
          const r = element.getBoundingClientRect()
          setRect({
            top: r.top - 8,
            left: r.left - 8,
            width: r.width + 16,
            height: r.height + 16
          })
        }
        updateRect()
        window.addEventListener('resize', updateRect)
        window.addEventListener('scroll', updateRect)
        return () => {
          window.removeEventListener('resize', updateRect)
          window.removeEventListener('scroll', updateRect)
        }
      }
    }
    setRect(null)
  }, [target])

  if (!rect) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[90] pointer-events-none"
    >
      {/* Overlay with cutout */}
      <svg className="absolute inset-0 w-full h-full">
        <defs>
          <mask id="spotlight-mask">
            <rect width="100%" height="100%" fill="white" />
            <rect
              x={rect.left}
              y={rect.top}
              width={rect.width}
              height={rect.height}
              rx="12"
              fill="black"
            />
          </mask>
        </defs>
        <rect
          width="100%"
          height="100%"
          fill="rgba(0, 0, 0, 0.75)"
          mask="url(#spotlight-mask)"
        />
      </svg>

      {/* Highlight border */}
      <div
        className="absolute border-2 border-cyan-400 rounded-xl"
        style={{
          top: rect.top,
          left: rect.left,
          width: rect.width,
          height: rect.height
        }}
      >
        <div className="absolute inset-0 rounded-xl bg-cyan-400/10 animate-pulse" />
      </div>
    </motion.div>
  )
}

function OnboardingTour({ isOpen, onClose, onComplete }) {
  const { t } = useI18n()
  const [currentStep, setCurrentStep] = useState(0)
  const step = TOUR_STEPS[currentStep]

  const handleNext = useCallback(() => {
    if (currentStep < TOUR_STEPS.length - 1) {
      setCurrentStep(prev => prev + 1)
    } else {
      // Tour complete
      localStorage.setItem('synapsix_tour_completed', 'true')
      onComplete?.()
      onClose()
    }
  }, [currentStep, onClose, onComplete])

  const handlePrev = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }, [currentStep])

  const handleSkip = useCallback(() => {
    localStorage.setItem('synapsix_tour_skipped', 'true')
    onClose()
  }, [onClose])

  // Close on escape
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        handleSkip()
      }
    }
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown)
    }
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, handleSkip])

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[80]">
        {/* Backdrop for center modals */}
        {!step.target && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/75 backdrop-blur-sm"
          />
        )}

        {/* Spotlight for targeted steps */}
        {step.target && <Spotlight target={step.target} />}

        {/* Tooltip */}
        <TourTooltip
          step={step}
          position={step.position}
          onNext={handleNext}
          onPrev={handlePrev}
          onSkip={handleSkip}
          currentStep={currentStep}
          totalSteps={TOUR_STEPS.length}
        />
      </div>
    </AnimatePresence>
  )
}

// Checklist component for post-tour
export function OnboardingChecklist({ onDismiss }) {
  const { t } = useI18n()
  const [items, setItems] = useState(CHECKLIST_ITEMS)
  const [isMinimized, setIsMinimized] = useState(false)

  const completedCount = items.filter(i => i.completed).length
  const progress = (completedCount / items.length) * 100

  const toggleItem = (id) => {
    setItems(prev => prev.map(item =>
      item.id === id ? { ...item, completed: !item.completed } : item
    ))
  }

  if (isMinimized) {
    return (
      <motion.button
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        onClick={() => setIsMinimized(false)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full shadow-lg flex items-center justify-center z-40"
      >
        <Target className="w-6 h-6 text-white" />
        <span className="absolute -top-1 -right-1 w-5 h-5 bg-white text-industrial-darker rounded-full text-xs font-bold flex items-center justify-center">
          {items.length - completedCount}
        </span>
      </motion.button>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-6 right-6 w-80 bg-industrial-dark border border-industrial-border rounded-xl shadow-2xl z-40 overflow-hidden"
    >
      {/* Header */}
      <div className="p-4 border-b border-industrial-border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-cyan-400" />
            <h3 className="font-semibold text-white">
              {t('onboarding.checklist.title') || 'Getting Started'}
            </h3>
          </div>
          <div className="flex gap-1">
            <button
              onClick={() => setIsMinimized(true)}
              className="p-1 text-gray-500 hover:text-white transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
            <button
              onClick={onDismiss}
              className="p-1 text-gray-500 hover:text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Progress bar */}
        <div className="h-1.5 bg-industrial-border rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            className="h-full bg-gradient-to-r from-cyan-500 to-purple-600"
          />
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {completedCount} / {items.length} {t('onboarding.checklist.completed') || 'completed'}
        </p>
      </div>

      {/* Items */}
      <div className="p-3 space-y-2">
        {items.map(item => (
          <button
            key={item.id}
            onClick={() => toggleItem(item.id)}
            className={`w-full flex items-center gap-3 p-2 rounded-lg transition-all ${
              item.completed
                ? 'bg-green-500/10 text-green-400'
                : 'bg-industrial-border/30 text-gray-300 hover:bg-industrial-border/50'
            }`}
          >
            <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
              item.completed
                ? 'border-green-400 bg-green-400'
                : 'border-gray-500'
            }`}>
              {item.completed && <Check className="w-3 h-3 text-industrial-darker" />}
            </div>
            <span className={`text-sm ${item.completed ? 'line-through' : ''}`}>
              {t(item.labelKey) || item.id}
            </span>
          </button>
        ))}
      </div>
    </motion.div>
  )
}

// Hook to manage tour state
export function useOnboardingTour() {
  const [isOpen, setIsOpen] = useState(false)
  const [showChecklist, setShowChecklist] = useState(false)

  useEffect(() => {
    const tourCompleted = localStorage.getItem('synapsix_tour_completed')
    const tourSkipped = localStorage.getItem('synapsix_tour_skipped')
    const hasVisited = localStorage.getItem('synapsix_visited')

    if (!tourCompleted && !tourSkipped && hasVisited) {
      // Show tour after first visit
      setIsOpen(true)
    }

    if (tourCompleted && !localStorage.getItem('synapsix_checklist_dismissed')) {
      setShowChecklist(true)
    }

    localStorage.setItem('synapsix_visited', 'true')
  }, [])

  return {
    isOpen,
    showChecklist,
    startTour: () => setIsOpen(true),
    closeTour: () => setIsOpen(false),
    dismissChecklist: () => {
      localStorage.setItem('synapsix_checklist_dismissed', 'true')
      setShowChecklist(false)
    },
    onComplete: () => setShowChecklist(true)
  }
}

export default OnboardingTour
