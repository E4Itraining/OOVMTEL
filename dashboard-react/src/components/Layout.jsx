import React from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  Activity,
  Search,
  MessageSquare,
  Settings,
  User,
  Briefcase,
  Wrench,
  ChevronLeft,
  Wifi,
  WifiOff,
  RefreshCw,
  Bell,
  Moon,
  Sun
} from 'lucide-react'
import { useDashboard, USER_MODES } from '../context/DashboardContext'
import { useRealTimeData } from '../hooks/useRealTimeData'

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Vue Globale', labelEn: 'Global View' },
  { path: '/grafana', icon: Activity, label: 'Grafana', labelEn: 'Grafana' },
  { path: '/opensearch', icon: Search, label: 'OpenSearch', labelEn: 'OpenSearch' },
  { path: '/kafka', icon: MessageSquare, label: 'Kafka', labelEn: 'Kafka' },
]

function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const {
    userMode,
    setUserMode,
    isConnected,
    metrics,
    viewLevel,
    switchToGlobal
  } = useDashboard()
  const { refetch } = useRealTimeData()
  const [sidebarOpen, setSidebarOpen] = React.useState(true)

  const isDetailView = location.pathname.startsWith('/details')

  return (
    <div className="min-h-screen flex bg-industrial-darker">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarOpen ? 240 : 72 }}
        className="fixed left-0 top-0 h-full bg-industrial-dark/95 backdrop-blur-lg border-r border-industrial-border z-40 flex flex-col"
      >
        {/* Logo */}
        <div className="h-16 flex items-center px-4 border-b border-industrial-border">
          <motion.div
            className="flex items-center gap-3"
            animate={{ opacity: sidebarOpen ? 1 : 0 }}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="font-bold text-lg text-white">OOVMTEL</h1>
                <p className="text-xs text-gray-500">Industrial Observability</p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-2 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200
                  ${isActive
                    ? 'bg-industrial-accent/20 text-industrial-accent'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {sidebarOpen && (
                  <span className="font-medium text-sm">{item.label}</span>
                )}
              </button>
            )
          })}
        </nav>

        {/* User Mode Toggle */}
        <div className="p-4 border-t border-industrial-border">
          {sidebarOpen && (
            <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">
              Parcours Utilisateur
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
              title="Parcours Business"
            >
              <Briefcase className="w-4 h-4" />
              {sidebarOpen && <span className="text-sm">Business</span>}
            </button>
            <button
              onClick={() => setUserMode(USER_MODES.TECH)}
              className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg transition-all
                ${userMode === USER_MODES.TECH
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-gray-500 hover:text-white hover:bg-white/5'
                }`}
              title="Parcours Technique"
            >
              <Wrench className="w-4 h-4" />
              {sidebarOpen && <span className="text-sm">Tech</span>}
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
      <div className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-60' : 'ml-[72px]'}`}>
        {/* Top Header */}
        <header className="h-16 bg-industrial-dark/80 backdrop-blur-lg border-b border-industrial-border sticky top-0 z-30 flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            {isDetailView && (
              <button
                onClick={() => navigate(-1)}
                className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
                <span>Retour</span>
              </button>
            )}
            <div className="flex items-center gap-2">
              {isConnected ? (
                <Wifi className="w-4 h-4 text-green-500" />
              ) : (
                <WifiOff className="w-4 h-4 text-red-500" />
              )}
              <span className="text-sm text-gray-400">
                {isConnected ? 'Temps réel' : 'Hors ligne'}
              </span>
              {metrics.lastUpdate && (
                <span className="text-xs text-gray-500">
                  {new Date(metrics.lastUpdate).toLocaleTimeString('fr-FR')}
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={refetch}
              className="btn btn-ghost p-2"
              title="Rafraîchir"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            <button className="btn btn-ghost p-2 relative">
              <Bell className="w-5 h-5" />
              {metrics.business?.criticalAlarms > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-[10px] flex items-center justify-center">
                  {metrics.business.criticalAlarms}
                </span>
              )}
            </button>
            <div className="w-px h-6 bg-industrial-border" />
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-industrial-card border border-industrial-border">
              {userMode === USER_MODES.TECH ? (
                <Wrench className="w-4 h-4 text-cyan-400" />
              ) : (
                <Briefcase className="w-4 h-4 text-purple-400" />
              )}
              <span className="text-sm font-medium">
                {userMode === USER_MODES.TECH ? 'Mode Tech' : 'Mode Business'}
              </span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
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
    </div>
  )
}

export default Layout
