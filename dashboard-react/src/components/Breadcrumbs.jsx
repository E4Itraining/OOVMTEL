import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'
import { useI18n } from '../i18n'

// Route configuration for breadcrumbs
const ROUTE_CONFIG = {
  '/': { key: 'commandCenter', parent: null },
  '/command-center': { key: 'commandCenter', parent: null },
  '/technical': { key: 'technicalView', parent: '/' },
  '/business-kpi': { key: 'businessKPI', parent: '/' },
  '/ai-assistant': { key: 'aiAssistant', parent: '/' },
  '/dashboard': { key: 'dashboard', parent: '/' },
  '/grafana': { key: 'grafana', parent: '/' },
  '/opensearch': { key: 'opensearch', parent: '/' },
  '/kafka': { key: 'kafka', parent: '/' },
  '/observability': { key: 'observability', parent: '/' },
  '/security': { key: 'security', parent: '/' }
}

function Breadcrumbs() {
  const location = useLocation()
  const navigate = useNavigate()
  const { t } = useI18n()

  // Build breadcrumb trail
  const buildBreadcrumbs = () => {
    const breadcrumbs = []
    let currentPath = location.pathname

    // Handle dynamic routes like /details/:service
    if (currentPath.startsWith('/details/')) {
      const serviceName = currentPath.split('/')[2]
      breadcrumbs.unshift({
        path: currentPath,
        label: serviceName.charAt(0).toUpperCase() + serviceName.slice(1),
        isActive: true
      })
      currentPath = '/technical'
    }

    // Build parent chain
    while (currentPath) {
      const config = ROUTE_CONFIG[currentPath]
      if (config) {
        breadcrumbs.unshift({
          path: currentPath,
          label: t(`nav.main.${config.key}`) || config.key,
          isActive: currentPath === location.pathname
        })
        currentPath = config.parent
      } else {
        break
      }
    }

    return breadcrumbs
  }

  const breadcrumbs = buildBreadcrumbs()

  // Don't show breadcrumbs on home page
  if (location.pathname === '/' || location.pathname === '/command-center') {
    return null
  }

  return (
    <nav className="flex items-center gap-2 text-sm mb-4">
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-1 text-gray-400 hover:text-white transition-colors"
      >
        <Home className="w-4 h-4" />
      </button>

      {breadcrumbs.map((crumb, index) => (
        <React.Fragment key={crumb.path}>
          <ChevronRight className="w-4 h-4 text-gray-600" />
          {crumb.isActive ? (
            <span className="text-white font-medium">{crumb.label}</span>
          ) : (
            <button
              onClick={() => navigate(crumb.path)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              {crumb.label}
            </button>
          )}
        </React.Fragment>
      ))}
    </nav>
  )
}

export default Breadcrumbs
