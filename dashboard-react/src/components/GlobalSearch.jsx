import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  Command,
  Home,
  Server,
  BarChart3,
  MessageSquare,
  Activity,
  Database,
  Shield,
  Lock,
  FileText,
  Settings,
  Gauge,
  AlertTriangle,
  Clock,
  ArrowRight,
  X,
  Zap
} from 'lucide-react'
import { useI18n } from '../i18n'

// Search index - all searchable items
const SEARCH_INDEX = [
  // Pages
  { type: 'page', id: 'command-center', path: '/', icon: Home, keywords: ['home', 'dashboard', 'accueil', 'centre', 'command'] },
  { type: 'page', id: 'technical', path: '/technical', icon: Server, keywords: ['technical', 'technique', 'infrastructure', 'services'] },
  { type: 'page', id: 'business-kpi', path: '/business-kpi', icon: BarChart3, keywords: ['business', 'kpi', 'oee', 'production', 'metrics', 'metriques'] },
  { type: 'page', id: 'ai-assistant', path: '/ai-assistant', icon: MessageSquare, keywords: ['ai', 'assistant', 'chat', 'help', 'aide', 'ia'] },
  { type: 'page', id: 'grafana', path: '/grafana', icon: Activity, keywords: ['grafana', 'graphs', 'visualization'] },
  { type: 'page', id: 'opensearch', path: '/opensearch', icon: Database, keywords: ['opensearch', 'logs', 'search', 'elasticsearch'] },
  { type: 'page', id: 'kafka', path: '/kafka', icon: Zap, keywords: ['kafka', 'messaging', 'queue', 'streaming'] },
  { type: 'page', id: 'observability', path: '/observability', icon: Shield, keywords: ['observability', 'slo', 'sli', 'remediation', 'incidents'] },
  { type: 'page', id: 'security', path: '/security', icon: Lock, keywords: ['security', 'compliance', 'securite', 'conformite', 'audit'] },

  // Features
  { type: 'feature', id: 'oee-dashboard', path: '/business-kpi#oee-section', icon: Gauge, keywords: ['oee', 'efficiency', 'efficacite', 'performance'] },
  { type: 'feature', id: 'equipment-status', path: '/business-kpi#equipment-status', icon: Settings, keywords: ['equipment', 'equipement', 'machines', 'status'] },
  { type: 'feature', id: 'alerts', path: '/observability#alerts', icon: AlertTriangle, keywords: ['alerts', 'alarmes', 'warnings', 'incidents'] },
  { type: 'feature', id: 'reports', path: '/business-kpi#reports', icon: FileText, keywords: ['reports', 'rapports', 'export', 'analytics'] },

  // Actions
  { type: 'action', id: 'ask-ai', path: '/ai-assistant', icon: MessageSquare, keywords: ['ask', 'demander', 'question', 'help'] },
  { type: 'action', id: 'export-data', action: 'export', icon: FileText, keywords: ['export', 'download', 'telecharger', 'csv', 'pdf'] },
  { type: 'action', id: 'refresh', action: 'refresh', icon: Clock, keywords: ['refresh', 'actualiser', 'reload', 'update'] }
]

function GlobalSearch({ isOpen, onClose }) {
  const { t } = useI18n()
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [recentSearches, setRecentSearches] = useState([])

  // Load recent searches
  useEffect(() => {
    const stored = localStorage.getItem('synapsix_recent_searches')
    if (stored) {
      setRecentSearches(JSON.parse(stored))
    }
  }, [])

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
    if (!isOpen) {
      setQuery('')
      setResults([])
      setSelectedIndex(0)
    }
  }, [isOpen])

  // Search function
  const performSearch = useCallback((searchQuery) => {
    if (!searchQuery.trim()) {
      setResults([])
      return
    }

    const normalizedQuery = searchQuery.toLowerCase().trim()
    const searchWords = normalizedQuery.split(' ')

    const matches = SEARCH_INDEX.filter(item => {
      const titleMatch = t(`search.items.${item.id}`)?.toLowerCase().includes(normalizedQuery)
      const keywordMatch = item.keywords.some(keyword =>
        searchWords.some(word => keyword.includes(word) || word.includes(keyword))
      )
      return titleMatch || keywordMatch
    }).map(item => ({
      ...item,
      title: t(`search.items.${item.id}`) || item.id,
      description: t(`search.descriptions.${item.id}`) || ''
    }))

    setResults(matches.slice(0, 8))
    setSelectedIndex(0)
  }, [t])

  // Handle query change
  useEffect(() => {
    performSearch(query)
  }, [query, performSearch])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex(prev => Math.min(prev + 1, results.length - 1))
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex(prev => Math.max(prev - 1, 0))
          break
        case 'Enter':
          e.preventDefault()
          if (results[selectedIndex]) {
            handleSelect(results[selectedIndex])
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
  }, [isOpen, results, selectedIndex, onClose])

  // Handle selection
  const handleSelect = (item) => {
    // Save to recent searches
    const newRecent = [item.id, ...recentSearches.filter(id => id !== item.id)].slice(0, 5)
    setRecentSearches(newRecent)
    localStorage.setItem('synapsix_recent_searches', JSON.stringify(newRecent))

    if (item.path) {
      navigate(item.path)
    } else if (item.action) {
      // Handle actions
      switch (item.action) {
        case 'export':
          window.dispatchEvent(new CustomEvent('synapsix:export'))
          break
        case 'refresh':
          window.dispatchEvent(new CustomEvent('synapsix:refresh'))
          break
      }
    }
    onClose()
  }

  // Get recent items for display
  const recentItems = recentSearches
    .map(id => SEARCH_INDEX.find(item => item.id === id))
    .filter(Boolean)
    .map(item => ({
      ...item,
      title: t(`search.items.${item.id}`) || item.id,
      description: t(`search.descriptions.${item.id}`) || ''
    }))

  const typeLabels = {
    page: t('search.types.page') || 'Page',
    feature: t('search.types.feature') || 'Feature',
    action: t('search.types.action') || 'Action'
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className="w-full max-w-2xl bg-industrial-dark border border-industrial-border rounded-2xl shadow-2xl overflow-hidden"
          onClick={e => e.stopPropagation()}
        >
          {/* Search Input */}
          <div className="flex items-center gap-3 px-4 py-4 border-b border-industrial-border">
            <Search className="w-5 h-5 text-gray-400" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t('search.placeholder') || 'Search pages, features, actions...'}
              className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none text-lg"
            />
            <div className="flex items-center gap-1 px-2 py-1 rounded bg-industrial-border/50 text-gray-500 text-xs">
              <Command className="w-3 h-3" />
              <span>K</span>
            </div>
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Results */}
          <div className="max-h-[400px] overflow-y-auto">
            {query && results.length === 0 && (
              <div className="px-4 py-8 text-center text-gray-500">
                {t('search.noResults') || 'No results found'}
              </div>
            )}

            {!query && recentItems.length > 0 && (
              <div className="p-2">
                <p className="px-3 py-2 text-xs text-gray-500 uppercase tracking-wider">
                  {t('search.recent') || 'Recent'}
                </p>
                {recentItems.map((item, index) => (
                  <SearchResultItem
                    key={item.id}
                    item={item}
                    isSelected={false}
                    onClick={() => handleSelect(item)}
                    typeLabel={typeLabels[item.type]}
                  />
                ))}
              </div>
            )}

            {results.length > 0 && (
              <div className="p-2">
                {results.map((item, index) => (
                  <SearchResultItem
                    key={item.id}
                    item={item}
                    isSelected={index === selectedIndex}
                    onClick={() => handleSelect(item)}
                    typeLabel={typeLabels[item.type]}
                  />
                ))}
              </div>
            )}

            {!query && recentItems.length === 0 && (
              <div className="p-2">
                <p className="px-3 py-2 text-xs text-gray-500 uppercase tracking-wider">
                  {t('search.suggestions') || 'Quick Access'}
                </p>
                {SEARCH_INDEX.filter(item => item.type === 'page').slice(0, 5).map((item, index) => (
                  <SearchResultItem
                    key={item.id}
                    item={{
                      ...item,
                      title: t(`search.items.${item.id}`) || item.id,
                      description: t(`search.descriptions.${item.id}`) || ''
                    }}
                    isSelected={index === selectedIndex}
                    onClick={() => handleSelect(item)}
                    typeLabel={typeLabels[item.type]}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-3 border-t border-industrial-border flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 rounded bg-industrial-border">↑↓</kbd>
                {t('search.navigate') || 'Navigate'}
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 rounded bg-industrial-border">↵</kbd>
                {t('search.select') || 'Select'}
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 rounded bg-industrial-border">esc</kbd>
                {t('search.close') || 'Close'}
              </span>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

function SearchResultItem({ item, isSelected, onClick, typeLabel }) {
  const Icon = item.icon

  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all ${
        isSelected
          ? 'bg-industrial-accent/20 text-white'
          : 'text-gray-300 hover:bg-industrial-border/50'
      }`}
    >
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
        isSelected ? 'bg-industrial-accent/30' : 'bg-industrial-border/50'
      }`}>
        <Icon className={`w-5 h-5 ${isSelected ? 'text-cyan-400' : 'text-gray-400'}`} />
      </div>
      <div className="flex-1 text-left">
        <p className="font-medium">{item.title}</p>
        {item.description && (
          <p className="text-sm text-gray-500 truncate">{item.description}</p>
        )}
      </div>
      <span className={`px-2 py-0.5 rounded text-xs ${
        isSelected ? 'bg-industrial-accent/30 text-cyan-400' : 'bg-industrial-border/50 text-gray-500'
      }`}>
        {typeLabel}
      </span>
      {isSelected && (
        <ArrowRight className="w-4 h-4 text-cyan-400" />
      )}
    </button>
  )
}

// Hook to use global search
export function useGlobalSearch() {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsOpen(prev => !prev)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
    toggle: () => setIsOpen(prev => !prev)
  }
}

export default GlobalSearch
