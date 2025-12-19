import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  X,
  Command,
  BarChart3,
  Server,
  Shield,
  Activity,
  MessageSquare,
  Database,
  Settings,
  FileText,
  Gauge,
  Clock,
  ArrowRight
} from 'lucide-react'
import { useI18n } from '../i18n'

// Searchable items configuration
const SEARCHABLE_ITEMS = [
  { id: 'command-center', path: '/', icon: Command, category: 'pages', keywords: ['home', 'accueil', 'dashboard', 'command'] },
  { id: 'technical', path: '/technical', icon: Server, category: 'pages', keywords: ['tech', 'infrastructure', 'services', 'technique'] },
  { id: 'business-kpi', path: '/business-kpi', icon: BarChart3, category: 'pages', keywords: ['business', 'kpi', 'production', 'oee', 'métier'] },
  { id: 'ai-assistant', path: '/ai-assistant', icon: MessageSquare, category: 'pages', keywords: ['ai', 'assistant', 'chat', 'help', 'aide'] },
  { id: 'grafana', path: '/grafana', icon: Activity, category: 'services', keywords: ['grafana', 'metrics', 'visualization', 'graphs'] },
  { id: 'opensearch', path: '/opensearch', icon: Database, category: 'services', keywords: ['opensearch', 'logs', 'search', 'elasticsearch'] },
  { id: 'kafka', path: '/kafka', icon: MessageSquare, category: 'services', keywords: ['kafka', 'streaming', 'topics', 'messages'] },
  { id: 'observability', path: '/observability', icon: Activity, category: 'services', keywords: ['observability', 'slo', 'sli', 'incidents', 'remediation'] },
  { id: 'security', path: '/security', icon: Shield, category: 'services', keywords: ['security', 'compliance', 'audit', 'sécurité'] },
  // Quick actions
  { id: 'refresh-data', action: 'refresh', icon: Activity, category: 'actions', keywords: ['refresh', 'reload', 'actualiser'] },
  { id: 'export-report', action: 'export', icon: FileText, category: 'actions', keywords: ['export', 'report', 'pdf', 'download'] },
  { id: 'settings', action: 'settings', icon: Settings, category: 'actions', keywords: ['settings', 'preferences', 'paramètres'] }
]

function GlobalSearch({ isOpen, onClose }) {
  const navigate = useNavigate()
  const { t } = useI18n()
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [recentSearches, setRecentSearches] = useState([])
  const inputRef = useRef(null)

  // Load recent searches from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('recentSearches')
    if (saved) {
      setRecentSearches(JSON.parse(saved))
    }
  }, [])

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // Reset state when closed
  useEffect(() => {
    if (!isOpen) {
      setQuery('')
      setSelectedIndex(0)
    }
  }, [isOpen])

  // Filter items based on query
  const filteredItems = query.length > 0
    ? SEARCHABLE_ITEMS.filter(item => {
        const searchLower = query.toLowerCase()
        const labelMatch = t(`nav.main.${item.id}`)?.toLowerCase().includes(searchLower) ||
                          t(`search.items.${item.id}`)?.toLowerCase().includes(searchLower)
        const keywordMatch = item.keywords.some(k => k.includes(searchLower))
        return labelMatch || keywordMatch
      })
    : recentSearches.length > 0
      ? SEARCHABLE_ITEMS.filter(item => recentSearches.includes(item.id))
      : SEARCHABLE_ITEMS.slice(0, 6)

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex(prev => Math.min(prev + 1, filteredItems.length - 1))
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex(prev => Math.max(prev - 1, 0))
          break
        case 'Enter':
          e.preventDefault()
          if (filteredItems[selectedIndex]) {
            handleSelect(filteredItems[selectedIndex])
          }
          break
        case 'Escape':
          e.preventDefault()
          onClose()
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, filteredItems, selectedIndex])

  const handleSelect = (item) => {
    // Save to recent searches
    const newRecent = [item.id, ...recentSearches.filter(id => id !== item.id)].slice(0, 5)
    setRecentSearches(newRecent)
    localStorage.setItem('recentSearches', JSON.stringify(newRecent))

    if (item.path) {
      navigate(item.path)
    } else if (item.action) {
      // Handle actions
      switch (item.action) {
        case 'refresh':
          window.location.reload()
          break
        case 'settings':
          // Could open settings modal
          break
        case 'export':
          // Could trigger export
          break
      }
    }
    onClose()
  }

  const getCategoryLabel = (category) => {
    const labels = {
      pages: t('search.categories.pages') || 'Pages',
      services: t('search.categories.services') || 'Services',
      actions: t('search.categories.actions') || 'Actions'
    }
    return labels[category] || category
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-start justify-center pt-[15vh]"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -20 }}
          className="w-full max-w-xl bg-industrial-dark border border-industrial-border rounded-xl shadow-2xl overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Search Input */}
          <div className="flex items-center gap-3 px-4 py-4 border-b border-industrial-border">
            <Search className="w-5 h-5 text-gray-400" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value)
                setSelectedIndex(0)
              }}
              placeholder={t('search.placeholder') || 'Rechercher pages, services, actions...'}
              className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none text-lg"
            />
            {query && (
              <button
                onClick={() => setQuery('')}
                className="p-1 hover:bg-white/10 rounded"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            )}
            <kbd className="hidden md:flex items-center gap-1 px-2 py-1 bg-industrial-card rounded text-xs text-gray-500">
              ESC
            </kbd>
          </div>

          {/* Results */}
          <div className="max-h-80 overflow-y-auto">
            {query.length === 0 && recentSearches.length > 0 && (
              <div className="px-4 py-2">
                <div className="flex items-center gap-2 text-xs text-gray-500 uppercase tracking-wider">
                  <Clock className="w-3 h-3" />
                  {t('search.recent') || 'Récent'}
                </div>
              </div>
            )}

            {filteredItems.length > 0 ? (
              <div className="py-2">
                {filteredItems.map((item, index) => {
                  const Icon = item.icon
                  const isSelected = index === selectedIndex
                  return (
                    <button
                      key={item.id}
                      onClick={() => handleSelect(item)}
                      onMouseEnter={() => setSelectedIndex(index)}
                      className={`w-full flex items-center gap-3 px-4 py-3 transition-colors
                        ${isSelected ? 'bg-industrial-accent/10' : 'hover:bg-white/5'}`}
                    >
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center
                        ${isSelected ? 'bg-industrial-accent/20' : 'bg-industrial-card'}`}>
                        <Icon className={`w-5 h-5 ${isSelected ? 'text-industrial-accent' : 'text-gray-400'}`} />
                      </div>
                      <div className="flex-1 text-left">
                        <p className={`font-medium ${isSelected ? 'text-white' : 'text-gray-300'}`}>
                          {t(`nav.main.${item.id}`) || t(`search.items.${item.id}`) || item.id}
                        </p>
                        <p className="text-xs text-gray-500">
                          {getCategoryLabel(item.category)}
                        </p>
                      </div>
                      {isSelected && (
                        <ArrowRight className="w-4 h-4 text-industrial-accent" />
                      )}
                    </button>
                  )
                })}
              </div>
            ) : (
              <div className="px-4 py-8 text-center">
                <Search className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                <p className="text-gray-400">{t('search.noResults') || 'Aucun résultat'}</p>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-3 border-t border-industrial-border bg-industrial-darker/50">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1">
                  <kbd className="px-1.5 py-0.5 bg-industrial-card rounded">↑</kbd>
                  <kbd className="px-1.5 py-0.5 bg-industrial-card rounded">↓</kbd>
                  {t('search.navigate') || 'Naviguer'}
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="px-1.5 py-0.5 bg-industrial-card rounded">↵</kbd>
                  {t('search.select') || 'Sélectionner'}
                </span>
              </div>
              <span className="flex items-center gap-1">
                <Command className="w-3 h-3" />K
              </span>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default GlobalSearch
