import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Activity,
  Factory,
  Server,
  Shield,
  ClipboardCheck,
  BarChart3,
  ChevronRight,
  Sparkles,
  ArrowRight
} from 'lucide-react'
import { useI18n } from '../i18n'

// Define the 6 personas
const PERSONAS = {
  OPERATIONS_MANAGER: 'operations_manager',
  PLANT_DIRECTOR: 'plant_director',
  DEVOPS_ENGINEER: 'devops_engineer',
  SECURITY_ANALYST: 'security_analyst',
  COMPLIANCE_OFFICER: 'compliance_officer',
  DATA_ANALYST: 'data_analyst'
}

const getPersonaConfig = (t) => [
  {
    id: PERSONAS.OPERATIONS_MANAGER,
    icon: Factory,
    color: 'from-purple-500 to-purple-600',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30',
    textColor: 'text-purple-400',
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
    id: PERSONAS.PLANT_DIRECTOR,
    icon: BarChart3,
    color: 'from-blue-500 to-blue-600',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    textColor: 'text-blue-400',
    title: t('personas.plantDirector.title'),
    description: t('personas.plantDirector.description'),
    features: [
      t('personas.plantDirector.feature1'),
      t('personas.plantDirector.feature2'),
      t('personas.plantDirector.feature3')
    ],
    defaultRoute: '/business-kpi',
    focusAreas: ['kpis', 'finance', 'trends']
  },
  {
    id: PERSONAS.DEVOPS_ENGINEER,
    icon: Server,
    color: 'from-cyan-500 to-cyan-600',
    bgColor: 'bg-cyan-500/10',
    borderColor: 'border-cyan-500/30',
    textColor: 'text-cyan-400',
    title: t('personas.devopsEngineer.title'),
    description: t('personas.devopsEngineer.description'),
    features: [
      t('personas.devopsEngineer.feature1'),
      t('personas.devopsEngineer.feature2'),
      t('personas.devopsEngineer.feature3')
    ],
    defaultRoute: '/technical',
    focusAreas: ['infrastructure', 'pipelines', 'services']
  },
  {
    id: PERSONAS.SECURITY_ANALYST,
    icon: Shield,
    color: 'from-red-500 to-red-600',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    textColor: 'text-red-400',
    title: t('personas.securityAnalyst.title'),
    description: t('personas.securityAnalyst.description'),
    features: [
      t('personas.securityAnalyst.feature1'),
      t('personas.securityAnalyst.feature2'),
      t('personas.securityAnalyst.feature3')
    ],
    defaultRoute: '/security',
    focusAreas: ['vulnerabilities', 'threats', 'audit']
  },
  {
    id: PERSONAS.COMPLIANCE_OFFICER,
    icon: ClipboardCheck,
    color: 'from-green-500 to-green-600',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    textColor: 'text-green-400',
    title: t('personas.complianceOfficer.title'),
    description: t('personas.complianceOfficer.description'),
    features: [
      t('personas.complianceOfficer.feature1'),
      t('personas.complianceOfficer.feature2'),
      t('personas.complianceOfficer.feature3')
    ],
    defaultRoute: '/security',
    focusAreas: ['compliance', 'policies', 'reports']
  },
  {
    id: PERSONAS.DATA_ANALYST,
    icon: Activity,
    color: 'from-orange-500 to-orange-600',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30',
    textColor: 'text-orange-400',
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
      className={`relative p-6 rounded-2xl border-2 transition-all duration-300 text-left w-full
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
            <ChevronRight className="w-4 h-4 text-white" />
          </div>
        </motion.div>
      )}

      <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${persona.color} flex items-center justify-center mb-4 shadow-lg`}>
        <Icon className="w-7 h-7 text-white" />
      </div>

      <h3 className={`font-bold text-lg mb-2 ${isSelected ? persona.textColor : 'text-white'}`}>
        {persona.title}
      </h3>

      <p className="text-sm text-gray-400 mb-4 line-clamp-2">
        {persona.description}
      </p>

      <AnimatePresence>
        {isSelected && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-2"
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

function WelcomePage() {
  const navigate = useNavigate()
  const { t } = useI18n()
  const [selectedPersona, setSelectedPersona] = useState(null)

  const personas = getPersonaConfig(t)

  const handleContinue = () => {
    if (selectedPersona) {
      // Store persona preference
      localStorage.setItem('selectedPersona', selectedPersona.id)
      // Navigate to appropriate default route
      navigate('/command-center')
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
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500 via-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
              <Activity className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">
            {t('welcome.title')}
          </h1>
          <p className="text-xl text-gray-400 mb-2">
            {t('welcome.subtitle')}
          </p>
          <div className="flex items-center justify-center gap-2 text-sm text-cyan-400">
            <Sparkles className="w-4 h-4" />
            <span>{t('welcome.tagline')}</span>
          </div>
        </motion.div>

        {/* Persona Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="w-full max-w-6xl"
        >
          <h2 className="text-center text-lg font-medium text-gray-300 mb-6">
            {t('welcome.selectPersona')}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {personas.map((persona, idx) => (
              <motion.div
                key={persona.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * idx }}
              >
                <PersonaCard
                  persona={persona}
                  isSelected={selectedPersona?.id === persona.id}
                  onSelect={setSelectedPersona}
                />
              </motion.div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
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
          className="mt-12 text-center text-xs text-gray-500"
        >
          {t('welcome.hint')}
        </motion.p>
      </div>
    </div>
  )
}

export { PERSONAS }
export default WelcomePage
