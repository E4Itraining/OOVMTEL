import React, { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plus,
  X,
  GripVertical,
  Maximize2,
  Minimize2,
  Settings,
  Trash2,
  Copy,
  BarChart3,
  Activity,
  Gauge,
  AlertTriangle,
  Clock,
  Server,
  Database,
  TrendingUp,
  PieChart,
  LineChart
} from 'lucide-react'
import { useI18n } from '../i18n'

// Widget types
export const WIDGET_TYPES = {
  METRIC: 'metric',
  CHART: 'chart',
  GAUGE: 'gauge',
  LIST: 'list',
  STATUS: 'status',
  CUSTOM: 'custom'
}

// Widget library
const WIDGET_LIBRARY = [
  {
    id: 'oee-gauge',
    type: WIDGET_TYPES.GAUGE,
    name: 'OEE Gauge',
    description: 'Overall Equipment Effectiveness',
    icon: Gauge,
    defaultSize: { w: 1, h: 1 },
    category: 'business'
  },
  {
    id: 'production-metric',
    type: WIDGET_TYPES.METRIC,
    name: 'Production Today',
    description: 'Daily production count',
    icon: BarChart3,
    defaultSize: { w: 1, h: 1 },
    category: 'business'
  },
  {
    id: 'alerts-list',
    type: WIDGET_TYPES.LIST,
    name: 'Active Alerts',
    description: 'Current system alerts',
    icon: AlertTriangle,
    defaultSize: { w: 2, h: 2 },
    category: 'monitoring'
  },
  {
    id: 'cpu-gauge',
    type: WIDGET_TYPES.GAUGE,
    name: 'CPU Usage',
    description: 'System CPU utilization',
    icon: Activity,
    defaultSize: { w: 1, h: 1 },
    category: 'infrastructure'
  },
  {
    id: 'memory-gauge',
    type: WIDGET_TYPES.GAUGE,
    name: 'Memory Usage',
    description: 'System memory utilization',
    icon: Server,
    defaultSize: { w: 1, h: 1 },
    category: 'infrastructure'
  },
  {
    id: 'services-status',
    type: WIDGET_TYPES.STATUS,
    name: 'Services Status',
    description: 'Backend services health',
    icon: Server,
    defaultSize: { w: 2, h: 1 },
    category: 'infrastructure'
  },
  {
    id: 'trend-chart',
    type: WIDGET_TYPES.CHART,
    name: 'Trend Chart',
    description: 'Time series visualization',
    icon: LineChart,
    defaultSize: { w: 2, h: 2 },
    category: 'analytics'
  },
  {
    id: 'distribution-chart',
    type: WIDGET_TYPES.CHART,
    name: 'Distribution',
    description: 'Pie/donut chart',
    icon: PieChart,
    defaultSize: { w: 1, h: 2 },
    category: 'analytics'
  },
  {
    id: 'kafka-metrics',
    type: WIDGET_TYPES.METRIC,
    name: 'Kafka Throughput',
    description: 'Message rate',
    icon: Database,
    defaultSize: { w: 1, h: 1 },
    category: 'infrastructure'
  },
  {
    id: 'latency-metric',
    type: WIDGET_TYPES.METRIC,
    name: 'API Latency',
    description: 'P95 response time',
    icon: Clock,
    defaultSize: { w: 1, h: 1 },
    category: 'infrastructure'
  }
]

// Widget component
function Widget({ widget, onRemove, onResize, onConfigure, isEditing }) {
  const [isHovered, setIsHovered] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)

  const widgetDef = WIDGET_LIBRARY.find(w => w.id === widget.type) || WIDGET_LIBRARY[0]
  const Icon = widgetDef.icon

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className={`bg-industrial-card border border-industrial-border rounded-xl overflow-hidden ${
        isExpanded ? 'fixed inset-4 z-50' : ''
      }`}
      style={{
        gridColumn: `span ${isExpanded ? 'full' : widget.size?.w || widgetDef.defaultSize.w}`,
        gridRow: `span ${isExpanded ? 'full' : widget.size?.h || widgetDef.defaultSize.h}`
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Widget Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-industrial-border/50">
        <div className="flex items-center gap-2">
          {isEditing && (
            <button className="cursor-grab text-gray-500 hover:text-white">
              <GripVertical className="w-4 h-4" />
            </button>
          )}
          <Icon className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-medium text-white">{widget.title || widgetDef.name}</h3>
        </div>

        <AnimatePresence>
          {(isHovered || isEditing) && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-1"
            >
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-1 text-gray-500 hover:text-white transition-colors"
              >
                {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
              {isEditing && (
                <>
                  <button
                    onClick={() => onConfigure?.(widget)}
                    className="p-1 text-gray-500 hover:text-white transition-colors"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => onRemove?.(widget.id)}
                    className="p-1 text-gray-500 hover:text-red-400 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Widget Content */}
      <div className="p-4">
        <WidgetContent widget={widget} type={widgetDef.type} />
      </div>
    </motion.div>
  )
}

// Widget content renderer
function WidgetContent({ widget, type }) {
  switch (type) {
    case WIDGET_TYPES.METRIC:
      return (
        <div className="text-center">
          <p className="text-3xl font-bold text-white">{widget.value || '0'}</p>
          <p className="text-sm text-gray-500 mt-1">{widget.unit || ''}</p>
          {widget.trend && (
            <div className={`flex items-center justify-center gap-1 mt-2 text-sm ${
              widget.trend > 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              <TrendingUp className={`w-4 h-4 ${widget.trend < 0 ? 'rotate-180' : ''}`} />
              <span>{Math.abs(widget.trend)}%</span>
            </div>
          )}
        </div>
      )

    case WIDGET_TYPES.GAUGE:
      const percentage = widget.value || 0
      return (
        <div className="flex flex-col items-center">
          <div className="relative w-24 h-24">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="48"
                cy="48"
                r="40"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                className="text-industrial-border"
              />
              <circle
                cx="48"
                cy="48"
                r="40"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                strokeDasharray={`${percentage * 2.51} 251`}
                className="text-cyan-400"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xl font-bold text-white">{percentage}%</span>
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-2">{widget.label || ''}</p>
        </div>
      )

    case WIDGET_TYPES.LIST:
      const items = widget.items || []
      return (
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {items.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">No items</p>
          ) : (
            items.map((item, index) => (
              <div
                key={index}
                className="flex items-center gap-2 p-2 rounded bg-industrial-border/30"
              >
                <span className={`w-2 h-2 rounded-full ${
                  item.severity === 'critical' ? 'bg-red-400' :
                  item.severity === 'warning' ? 'bg-yellow-400' : 'bg-blue-400'
                }`} />
                <span className="text-sm text-gray-300 truncate">{item.text}</span>
              </div>
            ))
          )}
        </div>
      )

    case WIDGET_TYPES.STATUS:
      const services = widget.services || []
      return (
        <div className="grid grid-cols-2 gap-2">
          {services.map((service, index) => (
            <div
              key={index}
              className="flex items-center gap-2 p-2 rounded bg-industrial-border/30"
            >
              <span className={`w-2 h-2 rounded-full ${
                service.status === 'healthy' ? 'bg-green-400' :
                service.status === 'degraded' ? 'bg-yellow-400' : 'bg-red-400'
              }`} />
              <span className="text-xs text-gray-300">{service.name}</span>
            </div>
          ))}
        </div>
      )

    case WIDGET_TYPES.CHART:
      return (
        <div className="h-32 flex items-center justify-center text-gray-500">
          <LineChart className="w-8 h-8" />
          <span className="ml-2 text-sm">Chart placeholder</span>
        </div>
      )

    default:
      return (
        <div className="text-center text-gray-500">
          <p className="text-sm">Widget content</p>
        </div>
      )
  }
}

// Widget selector modal
function WidgetSelector({ isOpen, onClose, onSelect }) {
  const { t } = useI18n()
  const [selectedCategory, setSelectedCategory] = useState('all')

  const categories = [
    { id: 'all', label: 'All' },
    { id: 'business', label: 'Business' },
    { id: 'infrastructure', label: 'Infrastructure' },
    { id: 'monitoring', label: 'Monitoring' },
    { id: 'analytics', label: 'Analytics' }
  ]

  const filteredWidgets = selectedCategory === 'all'
    ? WIDGET_LIBRARY
    : WIDGET_LIBRARY.filter(w => w.category === selectedCategory)

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="w-full max-w-2xl max-h-[80vh] bg-industrial-dark border border-industrial-border rounded-xl shadow-2xl overflow-hidden"
          onClick={e => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-industrial-border">
            <h2 className="text-lg font-semibold text-white">
              {t('widgets.addWidget') || 'Add Widget'}
            </h2>
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Categories */}
          <div className="flex gap-2 p-4 border-b border-industrial-border overflow-x-auto">
            {categories.map(cat => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-3 py-1.5 rounded-lg text-sm whitespace-nowrap transition-colors ${
                  selectedCategory === cat.id
                    ? 'bg-cyan-500/20 text-cyan-400'
                    : 'bg-industrial-border/50 text-gray-400 hover:text-white'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Widget Grid */}
          <div className="p-4 overflow-y-auto max-h-[50vh]">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {filteredWidgets.map(widget => {
                const Icon = widget.icon
                return (
                  <button
                    key={widget.id}
                    onClick={() => {
                      onSelect(widget)
                      onClose()
                    }}
                    className="p-4 rounded-xl bg-industrial-card border border-industrial-border hover:border-cyan-500/50 transition-all text-left group"
                  >
                    <div className="w-10 h-10 rounded-lg bg-industrial-border/50 flex items-center justify-center mb-3 group-hover:bg-cyan-500/20 transition-colors">
                      <Icon className="w-5 h-5 text-gray-400 group-hover:text-cyan-400 transition-colors" />
                    </div>
                    <h3 className="font-medium text-white text-sm">{widget.name}</h3>
                    <p className="text-xs text-gray-500 mt-1">{widget.description}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs px-2 py-0.5 rounded bg-industrial-border/50 text-gray-400">
                        {widget.defaultSize.w}x{widget.defaultSize.h}
                      </span>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

// Dashboard builder component
export function DashboardBuilder({ initialWidgets = [], onSave }) {
  const { t } = useI18n()
  const [widgets, setWidgets] = useState(initialWidgets)
  const [isEditing, setIsEditing] = useState(false)
  const [showSelector, setShowSelector] = useState(false)

  const addWidget = useCallback((widgetDef) => {
    const newWidget = {
      id: `widget_${Date.now()}`,
      type: widgetDef.id,
      title: widgetDef.name,
      size: { ...widgetDef.defaultSize },
      config: {}
    }
    setWidgets(prev => [...prev, newWidget])
  }, [])

  const removeWidget = useCallback((widgetId) => {
    setWidgets(prev => prev.filter(w => w.id !== widgetId))
  }, [])

  const handleSave = useCallback(() => {
    onSave?.(widgets)
    setIsEditing(false)
  }, [widgets, onSave])

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">
          {t('widgets.dashboard') || 'Dashboard'}
        </h2>
        <div className="flex gap-2">
          {isEditing ? (
            <>
              <button
                onClick={() => setShowSelector(true)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-industrial-card border border-industrial-border hover:border-cyan-500/50 transition-all text-sm text-gray-300"
              >
                <Plus className="w-4 h-4" />
                {t('widgets.add') || 'Add Widget'}
              </button>
              <button
                onClick={handleSave}
                className="px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white text-sm"
              >
                {t('common.save') || 'Save'}
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 rounded-lg text-gray-400 hover:text-white text-sm"
              >
                {t('common.cancel') || 'Cancel'}
              </button>
            </>
          ) : (
            <button
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-industrial-card border border-industrial-border hover:border-cyan-500/50 transition-all text-sm text-gray-300"
            >
              <Settings className="w-4 h-4" />
              {t('widgets.customize') || 'Customize'}
            </button>
          )}
        </div>
      </div>

      {/* Widget Grid */}
      <div className="grid grid-cols-4 gap-4 auto-rows-[120px]">
        <AnimatePresence>
          {widgets.map(widget => (
            <Widget
              key={widget.id}
              widget={widget}
              onRemove={removeWidget}
              isEditing={isEditing}
            />
          ))}
        </AnimatePresence>

        {widgets.length === 0 && (
          <div className="col-span-4 flex flex-col items-center justify-center py-12 text-center">
            <div className="w-16 h-16 rounded-xl bg-industrial-border/50 flex items-center justify-center mb-4">
              <Plus className="w-8 h-8 text-gray-500" />
            </div>
            <p className="text-gray-500">
              {t('widgets.empty') || 'No widgets added'}
            </p>
            <button
              onClick={() => {
                setIsEditing(true)
                setShowSelector(true)
              }}
              className="mt-4 px-4 py-2 rounded-lg bg-cyan-500/20 text-cyan-400 text-sm hover:bg-cyan-500/30 transition-colors"
            >
              {t('widgets.addFirst') || 'Add your first widget'}
            </button>
          </div>
        )}
      </div>

      {/* Widget Selector Modal */}
      <WidgetSelector
        isOpen={showSelector}
        onClose={() => setShowSelector(false)}
        onSelect={addWidget}
      />
    </div>
  )
}

export default DashboardBuilder
