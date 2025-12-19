import React from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ChevronRight,
  Home,
  Server,
  BarChart3,
  MessageSquare,
  Activity,
  Database,
  Shield,
  Lock,
  Zap,
  Eye,
  Settings
} from 'lucide-react'
import { useI18n } from '../i18n'

// Route configuration for breadcrumbs
const ROUTE_CONFIG = {
  '/': { icon: Home, labelKey: 'nav.main.commandCenter', parent: null },
  '/command-center': { icon: Home, labelKey: 'nav.main.commandCenter', parent: null },
  '/technical': { icon: Server, labelKey: 'nav.main.technicalView', parent: '/' },
  '/business-kpi': { icon: BarChart3, labelKey: 'nav.main.businessKPI', parent: '/' },
  '/ai-assistant': { icon: MessageSquare, labelKey: 'nav.main.aiAssistant', parent: '/' },
  '/dashboard': { icon: Activity, labelKey: 'nav.main.dashboard', parent: '/' },
  '/grafana': { icon: Activity, labelKey: 'nav.main.grafana', parent: '/' },
  '/opensearch': { icon: Database, labelKey: 'nav.main.opensearch', parent: '/' },
  '/kafka': { icon: Zap, labelKey: 'nav.main.kafka', parent: '/' },
  '/observability': { icon: Eye, labelKey: 'nav.main.observability', parent: '/' },
  '/security': { icon: Lock, labelKey: 'nav.main.security', parent: '/' },
  '/details': { icon: Settings, labelKey: 'nav.main.details', parent: '/technical' }
}

// Service names for detail views
const SERVICE_NAMES = {
  'victoriametrics': 'VictoriaMetrics',
  'opensearch': 'OpenSearch',
  'kafka': 'Kafka',
  'otel': 'OTEL Collector',
  'grafana': 'Grafana'
}

function Breadcrumbs({ className = '' }) {
  const location = useLocation()
  const navigate = useNavigate()
  const params = useParams()
  const { t } = useI18n()

  // Build breadcrumb trail
  const buildBreadcrumbs = () => {
    const breadcrumbs = []
    let currentPath = location.pathname

    // Handle detail views with params
    if (currentPath.startsWith('/details/')) {
      const basePath = '/details'
      const serviceName = params.service

      // Add parent (technical view)
      breadcrumbs.unshift({
        path: '/technical',
        label: t('nav.main.technicalView'),
        icon: Server,
        isLast: false
      })

      // Add home
      breadcrumbs.unshift({
        path: '/',
        label: t('nav.main.commandCenter'),
        icon: Home,
        isLast: false
      })

      // Add current detail
      breadcrumbs.push({
        path: currentPath,
        label: SERVICE_NAMES[serviceName] || serviceName,
        icon: Settings,
        isLast: true
      })

      return breadcrumbs
    }

    // Build trail from current path going up to root
    while (currentPath) {
      const config = ROUTE_CONFIG[currentPath]

      if (config) {
        breadcrumbs.unshift({
          path: currentPath,
          label: t(config.labelKey) || currentPath,
          icon: config.icon,
          isLast: breadcrumbs.length === 0
        })
        currentPath = config.parent
      } else {
        // Try to match partial paths
        const segments = currentPath.split('/').filter(Boolean)
        if (segments.length > 0) {
          const parentPath = '/' + segments.slice(0, -1).join('/')
          currentPath = parentPath || null
        } else {
          break
        }
      }
    }

    return breadcrumbs
  }

  const breadcrumbs = buildBreadcrumbs()

  // Don't show if only home
  if (breadcrumbs.length <= 1) {
    return null
  }

  return (
    <nav className={`flex items-center gap-1 text-sm ${className}`}>
      {breadcrumbs.map((crumb, index) => {
        const Icon = crumb.icon
        const isLast = crumb.isLast

        return (
          <React.Fragment key={crumb.path}>
            {index > 0 && (
              <ChevronRight className="w-4 h-4 text-gray-600 flex-shrink-0" />
            )}

            {isLast ? (
              <span className="flex items-center gap-1.5 text-white font-medium">
                <Icon className="w-4 h-4 text-cyan-400" />
                <span className="truncate max-w-[200px]">{crumb.label}</span>
              </span>
            ) : (
              <motion.button
                onClick={() => navigate(crumb.path)}
                className="flex items-center gap-1.5 text-gray-400 hover:text-white transition-colors"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Icon className="w-4 h-4" />
                <span className="truncate max-w-[150px]">{crumb.label}</span>
              </motion.button>
            )}
          </React.Fragment>
        )
      })}
    </nav>
  )
}

export default Breadcrumbs
