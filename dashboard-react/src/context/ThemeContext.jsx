import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'

const ThemeContext = createContext(null)

export const THEMES = {
  DARK: 'dark',
  LIGHT: 'light',
  SYSTEM: 'system'
}

// Color palette definitions
const COLOR_PALETTES = {
  dark: {
    '--bg-primary': '#0a0a0f',
    '--bg-secondary': '#12121a',
    '--bg-card': '#1a1a24',
    '--bg-border': '#2a2a3a',
    '--text-primary': '#ffffff',
    '--text-secondary': '#a1a1aa',
    '--text-muted': '#71717a',
    '--accent-primary': '#06b6d4',
    '--accent-secondary': '#8b5cf6',
    '--success': '#22c55e',
    '--warning': '#f59e0b',
    '--error': '#ef4444',
    '--info': '#3b82f6'
  },
  light: {
    '--bg-primary': '#f8fafc',
    '--bg-secondary': '#ffffff',
    '--bg-card': '#ffffff',
    '--bg-border': '#e2e8f0',
    '--text-primary': '#0f172a',
    '--text-secondary': '#475569',
    '--text-muted': '#94a3b8',
    '--accent-primary': '#0891b2',
    '--accent-secondary': '#7c3aed',
    '--success': '#16a34a',
    '--warning': '#d97706',
    '--error': '#dc2626',
    '--info': '#2563eb'
  }
}

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('synapsix_theme') || THEMES.DARK
  })
  const [resolvedTheme, setResolvedTheme] = useState(THEMES.DARK)

  // Resolve system theme
  useEffect(() => {
    const resolveTheme = () => {
      if (theme === THEMES.SYSTEM) {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        return prefersDark ? THEMES.DARK : THEMES.LIGHT
      }
      return theme
    }

    setResolvedTheme(resolveTheme())

    // Listen for system theme changes
    if (theme === THEMES.SYSTEM) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const handler = (e) => {
        setResolvedTheme(e.matches ? THEMES.DARK : THEMES.LIGHT)
      }
      mediaQuery.addEventListener('change', handler)
      return () => mediaQuery.removeEventListener('change', handler)
    }
  }, [theme])

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement

    // Remove existing theme classes
    root.classList.remove('dark', 'light')

    // Add new theme class
    root.classList.add(resolvedTheme)

    // Apply CSS variables
    const palette = COLOR_PALETTES[resolvedTheme]
    Object.entries(palette).forEach(([key, value]) => {
      root.style.setProperty(key, value)
    })

    // Update meta theme-color
    const metaThemeColor = document.querySelector('meta[name="theme-color"]')
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', palette['--bg-primary'])
    }

    // Save to localStorage
    localStorage.setItem('synapsix_theme', theme)
  }, [theme, resolvedTheme])

  const toggleTheme = useCallback(() => {
    setTheme(prev => {
      if (prev === THEMES.DARK) return THEMES.LIGHT
      if (prev === THEMES.LIGHT) return THEMES.SYSTEM
      return THEMES.DARK
    })
  }, [])

  const setThemeMode = useCallback((newTheme) => {
    if (Object.values(THEMES).includes(newTheme)) {
      setTheme(newTheme)
    }
  }, [])

  const isDark = resolvedTheme === THEMES.DARK

  const value = {
    theme,
    resolvedTheme,
    isDark,
    setTheme: setThemeMode,
    toggleTheme,
    THEMES
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

// Theme toggle component
export function ThemeToggle({ showLabel = false, className = '' }) {
  const { theme, toggleTheme, isDark, THEMES } = useTheme()

  const getIcon = () => {
    switch (theme) {
      case THEMES.DARK:
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        )
      case THEMES.LIGHT:
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        )
      case THEMES.SYSTEM:
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        )
      default:
        return null
    }
  }

  const getLabel = () => {
    switch (theme) {
      case THEMES.DARK: return 'Dark'
      case THEMES.LIGHT: return 'Light'
      case THEMES.SYSTEM: return 'System'
      default: return ''
    }
  }

  return (
    <button
      onClick={toggleTheme}
      className={`flex items-center gap-2 p-2 rounded-lg transition-colors ${
        isDark
          ? 'text-gray-400 hover:text-white hover:bg-white/5'
          : 'text-gray-600 hover:text-gray-900 hover:bg-black/5'
      } ${className}`}
      title={`Current: ${getLabel()}. Click to toggle.`}
    >
      {getIcon()}
      {showLabel && <span className="text-sm">{getLabel()}</span>}
    </button>
  )
}

// Theme selector dropdown
export function ThemeSelector({ className = '' }) {
  const { theme, setTheme, THEMES } = useTheme()
  const [isOpen, setIsOpen] = useState(false)

  const options = [
    { value: THEMES.DARK, label: 'Dark', icon: '🌙' },
    { value: THEMES.LIGHT, label: 'Light', icon: '☀️' },
    { value: THEMES.SYSTEM, label: 'System', icon: '💻' }
  ]

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-industrial-card/50 border border-industrial-border hover:border-industrial-accent/50 transition-all"
      >
        <span>{options.find(o => o.value === theme)?.icon}</span>
        <span className="text-sm">{options.find(o => o.value === theme)?.label}</span>
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 top-full mt-1 w-36 bg-industrial-card border border-industrial-border rounded-lg shadow-xl z-50 overflow-hidden">
            {options.map(option => (
              <button
                key={option.value}
                onClick={() => {
                  setTheme(option.value)
                  setIsOpen(false)
                }}
                className={`w-full flex items-center gap-2 px-4 py-2.5 text-left hover:bg-white/5 transition-colors ${
                  theme === option.value ? 'bg-industrial-accent/10 text-industrial-accent' : 'text-gray-300'
                }`}
              >
                <span>{option.icon}</span>
                <span className="text-sm">{option.label}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default ThemeContext
