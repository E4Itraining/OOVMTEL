import React, { useState, useEffect } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  Activity,
  Search,
  MessageSquare,
  Briefcase,
  Wrench,
  ChevronLeft,
  ChevronDown,
  ChevronRight,
  Wifi,
  WifiOff,
  RefreshCw,
  Bell,
  Globe,
  Home,
  BarChart3,
  TrendingUp,
  Settings2,
  AlertTriangle,
  FileText,
  Target,
  LineChart,
  PieChart,
  Server,
  Database,
  Gauge,
  Zap,
  Eye,
  Clock,
  Star,
  Layers,
  Shield,
  Lock,
  Command,
  Lightbulb,
  Sparkles,
  UserCircle2,
  GitBranch,
  Brain
} from 'lucide-react'
import { useDashboard, USER_MODES } from '../context/DashboardContext'
import { useRealTimeData } from '../hooks/useRealTimeData'
import { useI18n, LANGUAGES } from '../i18n'
import Breadcrumbs from './Breadcrumbs'
import GlobalSearch from './GlobalSearch'
import NotificationCenter from './NotificationCenter'
import FavoritesSystem, { FavoriteButton } from './FavoritesSystem'
import ExportSystem from './ExportSystem'
import OnboardingTour, { StartTourButton } from './OnboardingTour'

// Dynamic navigation configuration based on profile
const getNavConfig = (t, userMode) => {
  // Main navigation items (always visible)
  const mainNav = [
    {
      id: 'command-center',
      path: '/',
      icon: Home,
      getLabel: () => t('nav.main.commandCenter'),
      submenu: []
    },
    {
      id: 'technical',
      path: '/technical',
      icon: Server,
      getLabel: () => t('nav.main.technicalView'),
      submenu: []
    },
    {
      id: 'business-kpi',
      path: '/business-kpi',
      icon: BarChart3,
      getLabel: () => t('nav.main.businessKPI'),
      submenu: []
    },
    {
      id: 'ai-assistant',
      path: '/ai-assistant',
      icon: MessageSquare,
      getLabel: () => t('nav.main.aiAssistant'),
      submenu: []
    },
    {
      id: 'impact-analysis',
      path: '/impact-analysis',
      icon: Target,
      getLabel: () => t('nav.main.impactAnalysis') || 'Impact & Préconisations',
      submenu: []
    },
    {
      id: 'impact-chain',
      path: '/impact-chain',
      icon: GitBranch,
      getLabel: () => t('nav.main.impactChain') || 'Chaîne d\'Impact IT/OT',
      submenu: []
    }
  ]

  // Profile-specific menu items
  const profileMenus = {
    [USER_MODES.BUSINESS]: [
      {
        id: 'production',
        icon: BarChart3,
        getLabel: () => t('nav.business.production'),
        submenu: [
          { id: 'prod-overview', icon: LayoutDashboard, getLabel: () => t('nav.home.overview'), path: '/business-kpi', hash: '#oee-section' },
          { id: 'prod-kpis', icon: Target, getLabel: () => t('nav.business.kpis'), path: '/business-kpi', hash: '#production-metrics' },
          { id: 'prod-trends', icon: TrendingUp, getLabel: () => t('nav.business.trends'), path: '/business-kpi', hash: '#oee-trend' }
        ]
      },
      {
        id: 'quality',
        icon: Gauge,
        getLabel: () => t('nav.business.quality'),
        submenu: [
          { id: 'quality-rate', icon: PieChart, getLabel: () => t('metrics.business.qualityRate'), path: '/business-kpi', hash: '#quality-section' },
          { id: 'defects', icon: AlertTriangle, getLabel: () => t('metrics.business.defectsToday'), path: '/business-kpi', hash: '#production-metrics' }
        ]
      },
      {
        id: 'equipment',
        icon: Settings2,
        getLabel: () => t('nav.business.equipment'),
        submenu: [
          { id: 'equipment-status', icon: Activity, getLabel: () => t('metrics.business.equipmentStatus'), path: '/business-kpi', hash: '#equipment-status' },
          { id: 'maintenance', icon: Wrench, getLabel: () => t('metrics.business.maintenance'), path: '/business-kpi', hash: '#maintenance-section' }
        ]
      },
      {
        id: 'reports',
        icon: FileText,
        getLabel: () => t('nav.business.reports'),
        submenu: [
          { id: 'analytics', icon: LineChart, getLabel: () => t('nav.business.analytics'), path: '/dashboard', hash: '#analytics' },
          { id: 'oee-trend', icon: TrendingUp, getLabel: () => t('metrics.business.oeeTrend'), path: '/business-kpi', hash: '#oee-trend' }
        ]
      }
    ],
    [USER_MODES.TECH]: [
      {
        id: 'metrics',
        icon: Activity,
        getLabel: () => t('nav.tech.metrics'),
        submenu: [
          { id: 'metrics-overview', icon: LayoutDashboard, getLabel: () => t('nav.home.overview'), path: '/technical' },
          { id: 'performance', icon: Gauge, getLabel: () => t('nav.tech.performance'), path: '/technical' }
        ]
      },
      {
        id: 'infrastructure',
        icon: Server,
        getLabel: () => t('nav.tech.infrastructure'),
        submenu: [
          { id: 'services', icon: Layers, getLabel: () => t('nav.tech.services'), path: '/technical' },
          { id: 'databases', icon: Database, getLabel: () => t('nav.tech.databases'), path: '/technical' }
        ]
      },
      {
        id: 'monitoring',
        icon: Eye,
        getLabel: () => t('nav.tech.monitoring'),
        submenu: [
          { id: 'logs', icon: FileText, getLabel: () => t('nav.tech.logs'), path: '/opensearch' },
          { id: 'alerts', icon: AlertTriangle, getLabel: () => t('nav.tech.alerts'), path: '/observability' }
        ]
      }
    ]
  }

  // Service pages (always visible)
  const serviceNav = [
    { id: 'grafana', path: '/grafana', icon: Activity, getLabel: () => t('nav.main.grafana') },
    { id: 'opensearch', path: '/opensearch', icon: Search, getLabel: () => t('nav.main.opensearch') },
    { id: 'kafka', path: '/kafka', icon: MessageSquare, getLabel: () => t('nav.main.kafka') },
    { id: 'observability', path: '/observability', icon: Shield, getLabel: () => t('nav.main.observability') },
    { id: 'ai-observability', path: '/ai-observability', icon: Brain, getLabel: () => t('nav.main.aiObservability') || 'AI Observability' },
    { id: 'security', path: '/security', icon: Lock, getLabel: () => t('nav.main.security') }
  ]

  return {
    mainNav,
    profileMenus: profileMenus[userMode] || [],
    serviceNav
  }
}

// Language Switcher Component
function LanguageSwitcher({ compact = false }) {
  const { language, setLanguage, languageLabels, languages } = useI18n()
  const [isOpen, setIsOpen] = useState(false)

  const flagEmojis = {
    [LANGUAGES.FR]: 'FR',
    [LANGUAGES.EN]: 'EN',
    [LANGUAGES.NL]: 'NL',
    [LANGUAGES.DE]: 'DE'
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-industrial-card/50 border border-industrial-border hover:border-industrial-accent/50 transition-all"
        title="Change language"
      >
        <Globe className="w-4 h-4 text-industrial-accent" />
        {!compact && (
          <>
            <span className="text-sm font-medium">{flagEmojis[language]}</span>
            <ChevronDown className={`w-3 h-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </>
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            <div
              className="fixed inset-0 z-40"
              onClick={() => setIsOpen(false)}
            />
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute right-0 top-full mt-1 w-40 bg-industrial-card border border-industrial-border rounded-lg shadow-xl z-50 overflow-hidden"
            >
              {Object.values(languages).map((lang) => (
                <button
                  key={lang}
                  onClick={() => {
                    setLanguage(lang)
                    setIsOpen(false)
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-2.5 text-left hover:bg-white/5 transition-colors
                    ${language === lang ? 'bg-industrial-accent/10 text-industrial-accent' : 'text-gray-300'}`}
                >
                  <span className="font-mono text-sm">{flagEmojis[lang]}</span>
                  <span className="text-sm">{languageLabels[lang]}</span>
                </button>
              ))}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

// Submenu Item Component
function SubmenuItem({ item, isActive, onClick, sidebarOpen }) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-all
        ${isActive
          ? 'bg-industrial-accent/10 text-industrial-accent'
          : 'text-gray-400 hover:text-white hover:bg-white/5'
        }`}
    >
      <item.icon className="w-4 h-4 flex-shrink-0" />
      {sidebarOpen && <span>{item.getLabel()}</span>}
    </button>
  )
}

// Expandable Menu Section Component
function MenuSection({ item, isExpanded, onToggle, sidebarOpen, navigate, location }) {
  const hasSubmenu = item.submenu && item.submenu.length > 0
  const isActive = item.path && location.pathname === item.path

  const handleClick = () => {
    if (hasSubmenu) {
      onToggle()
    } else if (item.path) {
      navigate(item.path + (item.hash || ''))
    }
  }

  return (
    <div className="space-y-1">
      <button
        onClick={handleClick}
        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200
          ${isActive
            ? 'bg-industrial-accent/20 text-industrial-accent'
            : 'text-gray-400 hover:text-white hover:bg-white/5'
          }`}
      >
        <item.icon className="w-5 h-5 flex-shrink-0" />
        {sidebarOpen && (
          <>
            <span className="font-medium text-sm flex-1 text-left">{item.getLabel()}</span>
            {hasSubmenu && (
              <ChevronRight className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
            )}
          </>
        )}
      </button>

      {/* Submenu */}
      <AnimatePresence>
        {hasSubmenu && isExpanded && sidebarOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden ml-4 pl-2 border-l border-industrial-border/50 space-y-0.5"
          >
            {item.submenu.map((subItem) => (
              <SubmenuItem
                key={subItem.id}
                item={subItem}
                isActive={false}
                onClick={() => navigate((subItem.path || item.path || '/') + (subItem.hash || ''))}
                sidebarOpen={sidebarOpen}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const {
    userMode,
    setUserMode,
    isConnected,
    metrics
  } = useDashboard()
  const { refetch } = useRealTimeData()
  const { t, formatTime } = useI18n()

  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [expandedMenus, setExpandedMenus] = useState({})
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false)

  // Keyboard shortcut for search (Cmd/Ctrl + K)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsSearchOpen(true)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const isDetailView = location.pathname.startsWith('/details')
  const navConfig = getNavConfig(t, userMode)

  const toggleMenu = (menuId) => {
    setExpandedMenus(prev => ({
      ...prev,
      [menuId]: !prev[menuId]
    }))
  }

  return (
    <div className="min-h-screen flex bg-industrial-darker">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarOpen ? 260 : 72 }}
        className="fixed left-0 top-0 h-full bg-industrial-dark/95 backdrop-blur-lg border-r border-industrial-border z-40 flex flex-col"
      >
        {/* Logo - Synapsix Branding */}
        <div className="h-16 flex items-center px-4 border-b border-industrial-border">
          <motion.div
            className="flex items-center gap-3"
            animate={{ opacity: 1 }}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Activity className="w-6 h-6 text-white" />
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="font-bold text-lg text-white tracking-tight">{t('app.name')}</h1>
                <p className="text-xs text-gray-500">{t('app.tagline')}</p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto scrollbar-thin">
          {/* Home/Dashboard Section */}
          {navConfig.mainNav.map((item) => (
            <MenuSection
              key={item.id}
              item={item}
              isExpanded={expandedMenus[item.id]}
              onToggle={() => toggleMenu(item.id)}
              sidebarOpen={sidebarOpen}
              navigate={navigate}
              location={location}
            />
          ))}

          {/* Profile-specific Menu */}
          {sidebarOpen && navConfig.profileMenus.length > 0 && (
            <div className="pt-4 mt-4 border-t border-industrial-border/50">
              <p className="px-3 text-xs text-gray-500 uppercase tracking-wider mb-2">
                {userMode === USER_MODES.BUSINESS ? t('nav.business.title') : t('nav.tech.title')}
              </p>
            </div>
          )}

          {navConfig.profileMenus.map((item) => (
            <MenuSection
              key={item.id}
              item={item}
              isExpanded={expandedMenus[item.id]}
              onToggle={() => toggleMenu(item.id)}
              sidebarOpen={sidebarOpen}
              navigate={navigate}
              location={location}
            />
          ))}

          {/* Services Section */}
          {sidebarOpen && (
            <div className="pt-4 mt-4 border-t border-industrial-border/50">
              <p className="px-3 text-xs text-gray-500 uppercase tracking-wider mb-2">
                Services
              </p>
            </div>
          )}

          {navConfig.serviceNav.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <button
                key={item.id}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200
                  ${isActive
                    ? 'bg-industrial-accent/20 text-industrial-accent'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {sidebarOpen && (
                  <span className="font-medium text-sm">{item.getLabel()}</span>
                )}
              </button>
            )
          })}
        </nav>

        {/* User Mode Toggle */}
        <div className="p-4 border-t border-industrial-border">
          {sidebarOpen && (
            <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">
              {t('profiles.title')}
            </p>
          )}
          <div className={`flex ${sidebarOpen ? 'gap-2' : 'flex-col gap-2'}`}>
            <button
              onClick={() => setUserMode(USER_MODES.BUSINESS)}
              className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg transition-all
                ${userMode === USER_MODES.BUSINESS
                  ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                  : 'text-gray-500 hover:text-white hover:bg-white/5'
                }`}
              title={t('profiles.business.label')}
            >
              <Briefcase className="w-4 h-4" />
              {sidebarOpen && <span className="text-sm">{t('profiles.business.name')}</span>}
            </button>
            <button
              onClick={() => setUserMode(USER_MODES.TECH)}
              className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg transition-all
                ${userMode === USER_MODES.TECH
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-gray-500 hover:text-white hover:bg-white/5'
                }`}
              title={t('profiles.tech.label')}
            >
              <Wrench className="w-4 h-4" />
              {sidebarOpen && <span className="text-sm">{t('profiles.tech.name')}</span>}
            </button>
          </div>
        </div>

        {/* Toggle Button */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute -right-3 top-20 w-6 h-6 bg-industrial-card border border-industrial-border rounded-full flex items-center justify-center text-gray-400 hover:text-white transition-colors"
        >
          <ChevronLeft className={`w-4 h-4 transition-transform ${sidebarOpen ? '' : 'rotate-180'}`} />
        </button>
      </motion.aside>

      {/* Main Content */}
      <div className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-[260px]' : 'ml-[72px]'}`}>
        {/* Top Header */}
        <header className="h-16 bg-industrial-dark/80 backdrop-blur-lg border-b border-industrial-border sticky top-0 z-30 flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            {isDetailView && (
              <button
                onClick={() => navigate(-1)}
                className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
                <span>{t('common.back')}</span>
              </button>
            )}
            {/* Search Button */}
            <button
              onClick={() => setIsSearchOpen(true)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-industrial-card/50 border border-industrial-border hover:border-industrial-accent/50 transition-all"
            >
              <Search className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-500 hidden md:inline">Rechercher...</span>
              <kbd className="hidden md:flex items-center gap-0.5 px-1.5 py-0.5 bg-industrial-darker rounded text-xs text-gray-500">
                <Command className="w-3 h-3" />K
              </kbd>
            </button>
            <div className="flex items-center gap-2">
              {isConnected ? (
                <Wifi className="w-4 h-4 text-green-500" />
              ) : (
                <WifiOff className="w-4 h-4 text-red-500" />
              )}
              <span className="text-sm text-gray-400">
                {isConnected ? t('connection.realtime') : t('connection.offline')}
              </span>
              {metrics.lastUpdate && (
                <span className="text-xs text-gray-500">
                  {formatTime(metrics.lastUpdate)}
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Persona Switcher Button */}
            <button
              onClick={() => navigate('/welcome')}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-industrial-card/50 border border-industrial-border hover:border-industrial-accent/50 transition-all"
              title={t('nav.changePersona') || 'Changer de profil'}
            >
              <UserCircle2 className="w-4 h-4 text-industrial-accent" />
              <span className="text-sm text-gray-400 hidden md:inline">{t('nav.persona') || 'Profil'}</span>
            </button>

            {/* Tour Button */}
            <StartTourButton compact />

            {/* Export Button */}
            <ExportSystem />

            {/* Favorites */}
            <FavoritesSystem />

            {/* Favorite Current Page */}
            <FavoriteButton />

            {/* Language Switcher */}
            <LanguageSwitcher />

            <button
              onClick={refetch}
              className="btn btn-ghost p-2"
              title={t('common.refresh')}
            >
              <RefreshCw className="w-5 h-5" />
            </button>

            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                className="btn btn-ghost p-2 relative"
                title={t('common.notifications')}
              >
                <Bell className="w-5 h-5" />
                {metrics.business?.criticalAlarms > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-[10px] flex items-center justify-center">
                    {metrics.business.criticalAlarms}
                  </span>
                )}
              </button>
              <NotificationCenter
                isOpen={isNotificationsOpen}
                onClose={() => setIsNotificationsOpen(false)}
              />
            </div>

            <div className="w-px h-6 bg-industrial-border" />
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-industrial-card border border-industrial-border">
              {userMode === USER_MODES.TECH ? (
                <Wrench className="w-4 h-4 text-cyan-400" />
              ) : (
                <Briefcase className="w-4 h-4 text-purple-400" />
              )}
              <span className="text-sm font-medium">
                {userMode === USER_MODES.TECH ? t('profiles.modeLabel.tech') : t('profiles.modeLabel.business')}
              </span>
            </div>
          </div>
        </header>

        {/* Global Search Modal */}
        <GlobalSearch isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />

        {/* Page Content */}
        <main className="p-6">
          {/* Breadcrumbs */}
          <Breadcrumbs />

          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {/* Onboarding Tour Overlay */}
      <OnboardingTour />
    </div>
  )
}

export default Layout
