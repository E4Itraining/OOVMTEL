import React, { useState, useEffect, createContext, useContext } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutGrid,
  Plus,
  X,
  GripVertical,
  Settings,
  Trash2,
  Check,
  Activity,
  BarChart3,
  Gauge,
  AlertTriangle,
  Clock,
  TrendingUp,
  Server,
  Database,
  Zap
} from 'lucide-react'
import { useI18n } from '../i18n'
import { useDashboard } from '../context/DashboardContext'

// Widgets Context
const WidgetsContext = createContext(null)

export function useWidgets() {
  const context = useContext(WidgetsContext)
  if (!context) {
    throw new Error('useWidgets must be used within WidgetsProvider')
  }
  return context
}

// Available widget types
const WIDGET_TYPES = {
  oee: {
    id: 'oee',
    title: 'OEE',
    icon: Gauge,
    color: 'from-purple-500 to-purple-600',
    size: 'small'
  },
  production: {
    id: 'production',
    title: 'Production',
    icon: BarChart3,
    color: 'from-cyan-500 to-cyan-600',
    size: 'small'
  },
  errorRate: {
    id: 'errorRate',
    title: 'Taux d\'erreur',
    icon: AlertTriangle,
    color: 'from-red-500 to-red-600',
    size: 'small'
  },
  metricsRate: {
    id: 'metricsRate',
    title: 'Metrics/s',
    icon: Activity,
    color: 'from-green-500 to-green-600',
    size: 'small'
  },
  latency: {
    id: 'latency',
    title: 'Latence P95',
    icon: Zap,
    color: 'from-yellow-500 to-yellow-600',
    size: 'small'
  },
  serviceHealth: {
    id: 'serviceHealth',
    title: 'État Services',
    icon: Server,
    color: 'from-blue-500 to-blue-600',
    size: 'medium'
  },
  alerts: {
    id: 'alerts',
    title: 'Alertes Actives',
    icon: AlertTriangle,
    color: 'from-orange-500 to-orange-600',
    size: 'medium'
  },
  trend: {
    id: 'trend',
    title: 'Tendance OEE',
    icon: TrendingUp,
    color: 'from-indigo-500 to-indigo-600',
    size: 'large'
  }
}

// Default widgets configuration
const DEFAULT_WIDGETS = [
  { id: 'w1', type: 'oee', order: 0 },
  { id: 'w2', type: 'production', order: 1 },
  { id: 'w3', type: 'errorRate', order: 2 },
  { id: 'w4', type: 'metricsRate', order: 3 }
]

export function WidgetsProvider({ children }) {
  const [widgets, setWidgets] = useState([])
  const [isEditMode, setIsEditMode] = useState(false)

  // Load widgets from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('dashboardWidgets')
    if (saved) {
      setWidgets(JSON.parse(saved))
    } else {
      setWidgets(DEFAULT_WIDGETS)
    }
  }, [])

  // Save widgets to localStorage
  useEffect(() => {
    if (widgets.length > 0) {
      localStorage.setItem('dashboardWidgets', JSON.stringify(widgets))
    }
  }, [widgets])

  const addWidget = (type) => {
    const newWidget = {
      id: `w${Date.now()}`,
      type,
      order: widgets.length
    }
    setWidgets(prev => [...prev, newWidget])
  }

  const removeWidget = (id) => {
    setWidgets(prev => prev.filter(w => w.id !== id))
  }

  const reorderWidgets = (startIndex, endIndex) => {
    const result = Array.from(widgets)
    const [removed] = result.splice(startIndex, 1)
    result.splice(endIndex, 0, removed)
    setWidgets(result.map((w, i) => ({ ...w, order: i })))
  }

  const resetWidgets = () => {
    setWidgets(DEFAULT_WIDGETS)
    localStorage.removeItem('dashboardWidgets')
  }

  return (
    <WidgetsContext.Provider value={{
      widgets,
      widgetTypes: WIDGET_TYPES,
      isEditMode,
      setIsEditMode,
      addWidget,
      removeWidget,
      reorderWidgets,
      resetWidgets
    }}>
      {children}
    </WidgetsContext.Provider>
  )
}

// Individual Widget Component
function Widget({ widget, isEditMode, onRemove }) {
  const { metrics } = useDashboard()
  const widgetConfig = WIDGET_TYPES[widget.type]

  if (!widgetConfig) return null

  const Icon = widgetConfig.icon

  // Get widget value based on type
  const getValue = () => {
    switch (widget.type) {
      case 'oee':
        return { value: metrics.business?.oee?.toFixed(1) || '0', unit: '%' }
      case 'production':
        return { value: metrics.business?.productionToday?.toLocaleString() || '0', unit: '' }
      case 'errorRate':
        return { value: metrics.tech?.errorRate?.toFixed(2) || '0', unit: '%' }
      case 'metricsRate':
        return { value: metrics.tech?.metricsRate?.toLocaleString() || '0', unit: '/s' }
      case 'latency':
        return { value: metrics.tech?.latencyP95?.toFixed(0) || '0', unit: 'ms' }
      case 'alerts':
        return { value: metrics.business?.criticalAlarms || '0', unit: '' }
      default:
        return { value: '-', unit: '' }
    }
  }

  const { value, unit } = getValue()

  return (
    <motion.div
      layout
      className={`relative p-4 rounded-xl border border-industrial-border bg-industrial-card/50
        ${isEditMode ? 'ring-2 ring-industrial-accent/30 ring-dashed' : ''}`}
    >
      {isEditMode && (
        <>
          <button className="absolute top-2 left-2 p-1 cursor-grab text-gray-500 hover:text-white">
            <GripVertical className="w-4 h-4" />
          </button>
          <button
            onClick={() => onRemove(widget.id)}
            className="absolute top-2 right-2 p-1 text-gray-500 hover:text-red-400 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </>
      )}

      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${widgetConfig.color} flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div>
          <p className="text-2xl font-bold text-white">
            {value}<span className="text-sm text-gray-400 ml-1">{unit}</span>
          </p>
          <p className="text-xs text-gray-500">{widgetConfig.title}</p>
        </div>
      </div>
    </motion.div>
  )
}

// Add Widget Modal
function AddWidgetModal({ isOpen, onClose, onAdd }) {
  const { widgets, widgetTypes } = useWidgets()

  // Get available widgets (not already added)
  const availableWidgets = Object.values(widgetTypes).filter(
    wt => !widgets.some(w => w.type === wt.id)
  )

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="w-full max-w-md bg-industrial-dark border border-industrial-border rounded-xl shadow-2xl overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="px-6 py-4 border-b border-industrial-border">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Ajouter un widget</h3>
              <button onClick={onClose} className="p-1 hover:bg-white/10 rounded">
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
          </div>

          <div className="p-4 max-h-80 overflow-y-auto">
            {availableWidgets.length > 0 ? (
              <div className="grid grid-cols-2 gap-3">
                {availableWidgets.map((wt) => {
                  const Icon = wt.icon
                  return (
                    <button
                      key={wt.id}
                      onClick={() => {
                        onAdd(wt.id)
                        onClose()
                      }}
                      className="p-4 rounded-lg border border-industrial-border hover:border-industrial-accent/50 bg-industrial-card/50 hover:bg-industrial-accent/10 transition-all text-left"
                    >
                      <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${wt.color} flex items-center justify-center mb-2`}>
                        <Icon className="w-5 h-5 text-white" />
                      </div>
                      <p className="font-medium text-white">{wt.title}</p>
                      <p className="text-xs text-gray-500 mt-1 capitalize">{wt.size}</p>
                    </button>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-8">
                <Check className="w-10 h-10 text-green-400 mx-auto mb-2" />
                <p className="text-gray-400">Tous les widgets sont déjà ajoutés</p>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

// Widgets Grid Component
export function WidgetsGrid() {
  const { widgets, isEditMode, removeWidget, addWidget } = useWidgets()
  const [showAddModal, setShowAddModal] = useState(false)

  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {widgets
          .sort((a, b) => a.order - b.order)
          .map((widget) => (
            <Widget
              key={widget.id}
              widget={widget}
              isEditMode={isEditMode}
              onRemove={removeWidget}
            />
          ))}

        {isEditMode && (
          <button
            onClick={() => setShowAddModal(true)}
            className="p-4 rounded-xl border-2 border-dashed border-industrial-border hover:border-industrial-accent/50 flex flex-col items-center justify-center gap-2 text-gray-500 hover:text-industrial-accent transition-colors"
          >
            <Plus className="w-6 h-6" />
            <span className="text-sm">Ajouter</span>
          </button>
        )}
      </div>

      <AddWidgetModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAdd={addWidget}
      />
    </>
  )
}

// Edit Mode Toggle Button
export function WidgetsEditButton() {
  const { isEditMode, setIsEditMode, resetWidgets } = useWidgets()

  return (
    <div className="flex items-center gap-2">
      {isEditMode && (
        <button
          onClick={resetWidgets}
          className="px-3 py-1.5 text-xs text-gray-400 hover:text-white transition-colors"
        >
          Réinitialiser
        </button>
      )}
      <button
        onClick={() => setIsEditMode(!isEditMode)}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all ${
          isEditMode
            ? 'bg-industrial-accent text-white'
            : 'text-gray-400 hover:text-white hover:bg-white/5'
        }`}
      >
        {isEditMode ? (
          <>
            <Check className="w-4 h-4" />
            <span className="text-sm">Terminé</span>
          </>
        ) : (
          <>
            <LayoutGrid className="w-4 h-4" />
            <span className="text-sm">Personnaliser</span>
          </>
        )}
      </button>
    </div>
  )
}

// Main DashboardWidgets Component
function DashboardWidgets() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
          Widgets personnalisés
        </h2>
        <WidgetsEditButton />
      </div>
      <WidgetsGrid />
    </div>
  )
}

export default DashboardWidgets
