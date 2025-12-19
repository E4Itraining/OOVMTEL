import React, { useState, useEffect, createContext, useContext } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Star,
  X,
  Plus,
  GripVertical,
  Trash2,
  Edit2,
  Check,
  BarChart3,
  Server,
  Shield,
  Activity,
  MessageSquare,
  Database,
  Home,
  Eye
} from 'lucide-react'
import { useI18n } from '../i18n'

// Favorites Context
const FavoritesContext = createContext(null)

export function useFavorites() {
  const context = useContext(FavoritesContext)
  if (!context) {
    throw new Error('useFavorites must be used within FavoritesProvider')
  }
  return context
}

// Icon mapping for favorites
const ICON_MAP = {
  '/': Home,
  '/command-center': Home,
  '/technical': Server,
  '/business-kpi': BarChart3,
  '/ai-assistant': MessageSquare,
  '/grafana': Activity,
  '/opensearch': Database,
  '/kafka': MessageSquare,
  '/observability': Eye,
  '/security': Shield
}

export function FavoritesProvider({ children }) {
  const [favorites, setFavorites] = useState([])

  // Load favorites from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('favorites')
    if (saved) {
      setFavorites(JSON.parse(saved))
    }
  }, [])

  // Save favorites to localStorage
  useEffect(() => {
    localStorage.setItem('favorites', JSON.stringify(favorites))
  }, [favorites])

  const addFavorite = (path, label) => {
    const newFavorite = {
      id: Date.now().toString(),
      path,
      label,
      order: favorites.length
    }
    setFavorites(prev => [...prev, newFavorite])
  }

  const removeFavorite = (id) => {
    setFavorites(prev => prev.filter(f => f.id !== id))
  }

  const updateFavorite = (id, updates) => {
    setFavorites(prev => prev.map(f =>
      f.id === id ? { ...f, ...updates } : f
    ))
  }

  const reorderFavorites = (startIndex, endIndex) => {
    const result = Array.from(favorites)
    const [removed] = result.splice(startIndex, 1)
    result.splice(endIndex, 0, removed)
    setFavorites(result.map((f, i) => ({ ...f, order: i })))
  }

  const isFavorite = (path) => {
    return favorites.some(f => f.path === path)
  }

  return (
    <FavoritesContext.Provider value={{
      favorites,
      addFavorite,
      removeFavorite,
      updateFavorite,
      reorderFavorites,
      isFavorite
    }}>
      {children}
    </FavoritesContext.Provider>
  )
}

// Favorite Star Button (for adding/removing current page)
export function FavoriteButton() {
  const location = useLocation()
  const { t } = useI18n()
  const { favorites, addFavorite, removeFavorite, isFavorite } = useFavorites()

  const currentPath = location.pathname
  const isCurrentFavorite = isFavorite(currentPath)

  const handleToggle = () => {
    if (isCurrentFavorite) {
      const favorite = favorites.find(f => f.path === currentPath)
      if (favorite) {
        removeFavorite(favorite.id)
      }
    } else {
      // Get label from translation or path
      const pathKey = currentPath.replace('/', '') || 'commandCenter'
      const label = t(`nav.main.${pathKey}`) || pathKey
      addFavorite(currentPath, label)
    }
  }

  return (
    <button
      onClick={handleToggle}
      className={`p-2 rounded-lg transition-all ${
        isCurrentFavorite
          ? 'text-yellow-400 hover:bg-yellow-500/10'
          : 'text-gray-400 hover:text-yellow-400 hover:bg-white/5'
      }`}
      title={isCurrentFavorite ? 'Retirer des favoris' : 'Ajouter aux favoris'}
    >
      <Star className={`w-5 h-5 ${isCurrentFavorite ? 'fill-current' : ''}`} />
    </button>
  )
}

// Favorites Dropdown Panel
function FavoritesPanel({ isOpen, onClose }) {
  const navigate = useNavigate()
  const { t } = useI18n()
  const { favorites, removeFavorite, updateFavorite } = useFavorites()
  const [editingId, setEditingId] = useState(null)
  const [editLabel, setEditLabel] = useState('')

  const handleEdit = (favorite) => {
    setEditingId(favorite.id)
    setEditLabel(favorite.label)
  }

  const handleSaveEdit = () => {
    if (editingId && editLabel.trim()) {
      updateFavorite(editingId, { label: editLabel.trim() })
    }
    setEditingId(null)
    setEditLabel('')
  }

  const handleNavigate = (path) => {
    navigate(path)
    onClose()
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -10, scale: 0.95 }}
        className="absolute right-0 top-full mt-2 w-72 bg-industrial-dark border border-industrial-border rounded-xl shadow-2xl z-50 overflow-hidden"
      >
        {/* Header */}
        <div className="px-4 py-3 border-b border-industrial-border bg-industrial-darker/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Star className="w-5 h-5 text-yellow-400" />
              <h3 className="font-semibold text-white">Favoris</h3>
              <span className="px-2 py-0.5 bg-industrial-card text-gray-400 text-xs rounded">
                {favorites.length}
              </span>
            </div>
            <button
              onClick={onClose}
              className="p-1 hover:bg-white/10 rounded transition-colors"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          </div>
        </div>

        {/* Favorites List */}
        <div className="max-h-64 overflow-y-auto">
          {favorites.length > 0 ? (
            <div className="py-2">
              {favorites.map((favorite) => {
                const Icon = ICON_MAP[favorite.path] || Star
                const isEditing = editingId === favorite.id

                return (
                  <div
                    key={favorite.id}
                    className="flex items-center gap-2 px-2 py-1 group"
                  >
                    <button className="p-1 text-gray-600 cursor-grab hover:text-gray-400">
                      <GripVertical className="w-4 h-4" />
                    </button>

                    {isEditing ? (
                      <div className="flex-1 flex items-center gap-2">
                        <input
                          type="text"
                          value={editLabel}
                          onChange={(e) => setEditLabel(e.target.value)}
                          className="flex-1 px-2 py-1 bg-industrial-card border border-industrial-border rounded text-sm text-white"
                          autoFocus
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleSaveEdit()
                            if (e.key === 'Escape') setEditingId(null)
                          }}
                        />
                        <button
                          onClick={handleSaveEdit}
                          className="p-1 text-green-400 hover:bg-green-500/10 rounded"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <>
                        <button
                          onClick={() => handleNavigate(favorite.path)}
                          className="flex-1 flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-white/5 transition-colors text-left"
                        >
                          <Icon className="w-4 h-4 text-gray-400" />
                          <span className="text-sm text-gray-300">{favorite.label}</span>
                        </button>

                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => handleEdit(favorite)}
                            className="p-1 text-gray-400 hover:text-white hover:bg-white/10 rounded"
                          >
                            <Edit2 className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => removeFavorite(favorite.id)}
                            className="p-1 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="px-4 py-8 text-center">
              <Star className="w-10 h-10 text-gray-600 mx-auto mb-2" />
              <p className="text-gray-400 text-sm">Aucun favori</p>
              <p className="text-gray-500 text-xs mt-1">
                Cliquez sur l'étoile pour ajouter une page
              </p>
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  )
}

// Main Favorites System Component (for header)
function FavoritesSystem() {
  const [isOpen, setIsOpen] = useState(false)
  const { favorites } = useFavorites()

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 p-2 rounded-lg text-gray-400 hover:text-yellow-400 hover:bg-white/5 transition-colors"
        title="Favoris"
      >
        <Star className={`w-5 h-5 ${favorites.length > 0 ? 'text-yellow-400' : ''}`} />
        {favorites.length > 0 && (
          <span className="text-xs text-gray-400">{favorites.length}</span>
        )}
      </button>

      <FavoritesPanel isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </div>
  )
}

export default FavoritesSystem
