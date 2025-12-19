import React, { useState, useEffect, useCallback, createContext, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Star,
  Plus,
  X,
  Home,
  Server,
  BarChart3,
  MessageSquare,
  Activity,
  Database,
  Shield,
  Lock,
  Zap,
  Edit2,
  Trash2,
  GripVertical,
  ChevronRight
} from 'lucide-react'
import { useI18n } from '../i18n'

// Context for favorites
const FavoritesContext = createContext(null)

// Default shortcuts
const DEFAULT_SHORTCUTS = [
  { id: 'cmd-center', path: '/', icon: 'Home', label: 'Command Center', isDefault: true },
  { id: 'kpi', path: '/business-kpi', icon: 'BarChart3', label: 'Business KPI', isDefault: true },
  { id: 'technical', path: '/technical', icon: 'Server', label: 'Technical', isDefault: true }
]

// Icon mapping
const ICON_MAP = {
  Home,
  Server,
  BarChart3,
  MessageSquare,
  Activity,
  Database,
  Shield,
  Lock,
  Zap,
  Star
}

// Available pages for favorites
const AVAILABLE_PAGES = [
  { id: 'command-center', path: '/', icon: 'Home', labelKey: 'nav.main.commandCenter' },
  { id: 'technical', path: '/technical', icon: 'Server', labelKey: 'nav.main.technicalView' },
  { id: 'business-kpi', path: '/business-kpi', icon: 'BarChart3', labelKey: 'nav.main.businessKPI' },
  { id: 'ai-assistant', path: '/ai-assistant', icon: 'MessageSquare', labelKey: 'nav.main.aiAssistant' },
  { id: 'grafana', path: '/grafana', icon: 'Activity', labelKey: 'nav.main.grafana' },
  { id: 'opensearch', path: '/opensearch', icon: 'Database', labelKey: 'nav.main.opensearch' },
  { id: 'kafka', path: '/kafka', icon: 'Zap', labelKey: 'nav.main.kafka' },
  { id: 'observability', path: '/observability', icon: 'Shield', labelKey: 'nav.main.observability' },
  { id: 'security', path: '/security', icon: 'Lock', labelKey: 'nav.main.security' }
]

export function FavoritesProvider({ children }) {
  const [favorites, setFavorites] = useState([])
  const [shortcuts, setShortcuts] = useState(DEFAULT_SHORTCUTS)

  // Load from localStorage
  useEffect(() => {
    const storedFavorites = localStorage.getItem('synapsix_favorites')
    const storedShortcuts = localStorage.getItem('synapsix_shortcuts')

    if (storedFavorites) {
      setFavorites(JSON.parse(storedFavorites))
    }
    if (storedShortcuts) {
      setShortcuts(JSON.parse(storedShortcuts))
    }
  }, [])

  // Save to localStorage
  useEffect(() => {
    localStorage.setItem('synapsix_favorites', JSON.stringify(favorites))
  }, [favorites])

  useEffect(() => {
    localStorage.setItem('synapsix_shortcuts', JSON.stringify(shortcuts))
  }, [shortcuts])

  const addFavorite = useCallback((page) => {
    setFavorites(prev => {
      if (prev.some(f => f.id === page.id)) return prev
      return [...prev, { ...page, addedAt: new Date().toISOString() }]
    })
  }, [])

  const removeFavorite = useCallback((id) => {
    setFavorites(prev => prev.filter(f => f.id !== id))
  }, [])

  const isFavorite = useCallback((id) => {
    return favorites.some(f => f.id === id)
  }, [favorites])

  const toggleFavorite = useCallback((page) => {
    if (isFavorite(page.id)) {
      removeFavorite(page.id)
    } else {
      addFavorite(page)
    }
  }, [isFavorite, removeFavorite, addFavorite])

  const addShortcut = useCallback((shortcut) => {
    setShortcuts(prev => {
      if (prev.length >= 6) return prev // Max 6 shortcuts
      if (prev.some(s => s.id === shortcut.id)) return prev
      return [...prev, { ...shortcut, isDefault: false }]
    })
  }, [])

  const removeShortcut = useCallback((id) => {
    setShortcuts(prev => prev.filter(s => s.id !== id))
  }, [])

  const reorderShortcuts = useCallback((startIndex, endIndex) => {
    setShortcuts(prev => {
      const result = Array.from(prev)
      const [removed] = result.splice(startIndex, 1)
      result.splice(endIndex, 0, removed)
      return result
    })
  }, [])

  const value = {
    favorites,
    shortcuts,
    addFavorite,
    removeFavorite,
    isFavorite,
    toggleFavorite,
    addShortcut,
    removeShortcut,
    reorderShortcuts
  }

  return (
    <FavoritesContext.Provider value={value}>
      {children}
    </FavoritesContext.Provider>
  )
}

export function useFavorites() {
  const context = useContext(FavoritesContext)
  if (!context) {
    throw new Error('useFavorites must be used within a FavoritesProvider')
  }
  return context
}

// Favorite button component
export function FavoriteButton({ page, size = 'md' }) {
  const { isFavorite, toggleFavorite } = useFavorites()
  const isActive = isFavorite(page.id)

  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  }

  return (
    <motion.button
      onClick={(e) => {
        e.stopPropagation()
        e.preventDefault()
        toggleFavorite(page)
      }}
      className={`p-1 rounded transition-colors ${
        isActive
          ? 'text-yellow-400'
          : 'text-gray-500 hover:text-yellow-400'
      }`}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      title={isActive ? 'Remove from favorites' : 'Add to favorites'}
    >
      <Star className={`${sizes[size]} ${isActive ? 'fill-current' : ''}`} />
    </motion.button>
  )
}

// Shortcuts bar component
export function ShortcutsBar({ className = '' }) {
  const navigate = useNavigate()
  const { t } = useI18n()
  const { shortcuts } = useFavorites()
  const [isEditing, setIsEditing] = useState(false)

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {shortcuts.map((shortcut) => {
        const Icon = ICON_MAP[shortcut.icon] || Star
        return (
          <motion.button
            key={shortcut.id}
            onClick={() => navigate(shortcut.path)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-industrial-card/50 border border-industrial-border hover:border-cyan-500/50 transition-all text-sm"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Icon className="w-4 h-4 text-cyan-400" />
            <span className="text-gray-300 hidden md:inline">{shortcut.label}</span>
          </motion.button>
        )
      })}
    </div>
  )
}

// Favorites panel/dropdown
export function FavoritesPanel({ isOpen, onClose }) {
  const navigate = useNavigate()
  const { t } = useI18n()
  const { favorites, shortcuts, removeFavorite, addShortcut, removeShortcut } = useFavorites()

  const handleNavigate = (path) => {
    navigate(path)
    onClose()
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="absolute right-4 top-20 w-80 bg-industrial-dark border border-industrial-border rounded-xl shadow-2xl overflow-hidden"
          onClick={e => e.stopPropagation()}
        >
          {/* Header */}
          <div className="p-4 border-b border-industrial-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Star className="w-5 h-5 text-yellow-400" />
                <h3 className="font-semibold text-white">
                  {t('favorites.title') || 'Favorites'}
                </h3>
              </div>
              <button
                onClick={onClose}
                className="p-1 text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Shortcuts section */}
          <div className="p-4 border-b border-industrial-border">
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">
              {t('favorites.shortcuts') || 'Quick Access'}
            </p>
            <div className="space-y-2">
              {shortcuts.map(shortcut => {
                const Icon = ICON_MAP[shortcut.icon] || Star
                return (
                  <div
                    key={shortcut.id}
                    className="flex items-center gap-3 p-2 rounded-lg bg-industrial-border/30 group"
                  >
                    <Icon className="w-4 h-4 text-cyan-400" />
                    <button
                      onClick={() => handleNavigate(shortcut.path)}
                      className="flex-1 text-left text-sm text-gray-300 hover:text-white"
                    >
                      {shortcut.label}
                    </button>
                    {!shortcut.isDefault && (
                      <button
                        onClick={() => removeShortcut(shortcut.id)}
                        className="p-1 text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                )
              })}
            </div>
          </div>

          {/* Favorites section */}
          <div className="p-4 max-h-64 overflow-y-auto">
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">
              {t('favorites.pages') || 'Favorite Pages'}
            </p>

            {favorites.length === 0 ? (
              <div className="text-center py-6">
                <Star className="w-10 h-10 text-gray-600 mx-auto mb-2" />
                <p className="text-sm text-gray-500">
                  {t('favorites.empty') || 'No favorites yet'}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  {t('favorites.emptyHint') || 'Click the star icon on any page to add it here'}
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {favorites.map(favorite => {
                  const Icon = ICON_MAP[favorite.icon] || Star
                  const isShortcut = shortcuts.some(s => s.id === favorite.id)
                  return (
                    <div
                      key={favorite.id}
                      className="flex items-center gap-3 p-2 rounded-lg hover:bg-industrial-border/30 group"
                    >
                      <Icon className="w-4 h-4 text-gray-400" />
                      <button
                        onClick={() => handleNavigate(favorite.path)}
                        className="flex-1 text-left text-sm text-gray-300 hover:text-white"
                      >
                        {favorite.label}
                      </button>
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-all">
                        {!isShortcut && shortcuts.length < 6 && (
                          <button
                            onClick={() => addShortcut(favorite)}
                            className="p-1 text-gray-500 hover:text-cyan-400"
                            title="Add to shortcuts"
                          >
                            <Plus className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => removeFavorite(favorite.id)}
                          className="p-1 text-gray-500 hover:text-red-400"
                          title="Remove from favorites"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* Add more favorites */}
          <div className="p-3 border-t border-industrial-border">
            <p className="text-xs text-gray-500 mb-2">
              {t('favorites.addMore') || 'Quick add:'}
            </p>
            <div className="flex flex-wrap gap-1">
              {AVAILABLE_PAGES.filter(p => !favorites.some(f => f.id === p.id)).slice(0, 4).map(page => {
                const Icon = ICON_MAP[page.icon] || Star
                return (
                  <button
                    key={page.id}
                    onClick={() => {
                      const { toggleFavorite } = useFavorites()
                      toggleFavorite({
                        ...page,
                        label: t(page.labelKey) || page.id
                      })
                    }}
                    className="flex items-center gap-1 px-2 py-1 rounded bg-industrial-border/30 text-xs text-gray-400 hover:text-white hover:bg-industrial-border/50 transition-colors"
                  >
                    <Plus className="w-3 h-3" />
                    {t(page.labelKey) || page.id}
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

export default FavoritesContext
