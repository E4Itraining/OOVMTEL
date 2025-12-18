import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'

const DashboardContext = createContext(null)

export const USER_MODES = {
  TECH: 'tech',
  BUSINESS: 'business'
}

export const VIEW_LEVELS = {
  GLOBAL: 'global',
  DETAILED: 'detailed'
}

const defaultMetrics = {
  business: {
    oee: 0,
    availability: 0,
    performance: 0,
    quality: 0,
    productionToday: 0,
    cycleTime: 0,
    defectsToday: 0,
    criticalAlarms: 0,
    equipmentStatus: [],
    productionByProduct: []
  },
  tech: {
    metricsRate: 0,
    logsRate: 0,
    tracesRate: 0,
    latencyP95: 0,
    errorRate: 0,
    kafkaThroughput: 0,
    cpu: 0,
    memory: 0,
    disk: 0,
    vmActiveSeries: 0,
    vmStorage: '',
    vmQueryLatency: 0,
    osDocuments: 0,
    osHealth: 'green',
    osNodes: 0,
    kafkaTopics: 0,
    kafkaPartitions: 0,
    kafkaConsumerLag: 0
  },
  services: [],
  events: [],
  lastUpdate: null
}

export function DashboardProvider({ children }) {
  const [userMode, setUserMode] = useState(() => {
    return localStorage.getItem('userMode') || USER_MODES.BUSINESS
  })
  const [viewLevel, setViewLevel] = useState(VIEW_LEVELS.GLOBAL)
  const [selectedService, setSelectedService] = useState(null)
  const [selectedPersona, setSelectedPersona] = useState(() => {
    return localStorage.getItem('oovmtel_selected_persona') || null
  })
  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState(() => {
    return localStorage.getItem('oovmtel_has_visited') === 'true'
  })
  const [metrics, setMetrics] = useState(defaultMetrics)
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  // Persist user mode preference
  useEffect(() => {
    localStorage.setItem('userMode', userMode)
  }, [userMode])

  const toggleUserMode = useCallback(() => {
    setUserMode(prev => prev === USER_MODES.TECH ? USER_MODES.BUSINESS : USER_MODES.TECH)
  }, [])

  const switchToGlobal = useCallback(() => {
    setViewLevel(VIEW_LEVELS.GLOBAL)
    setSelectedService(null)
  }, [])

  const drillDown = useCallback((service) => {
    setSelectedService(service)
    setViewLevel(VIEW_LEVELS.DETAILED)
  }, [])

  const updateMetrics = useCallback((newMetrics) => {
    setMetrics(prev => ({
      ...prev,
      ...newMetrics,
      lastUpdate: new Date()
    }))
    setIsLoading(false)
    setError(null)
  }, [])

  const value = {
    // State
    userMode,
    viewLevel,
    selectedService,
    selectedPersona,
    hasCompletedOnboarding,
    metrics,
    isConnected,
    isLoading,
    error,

    // Actions
    setUserMode,
    toggleUserMode,
    switchToGlobal,
    drillDown,
    updateMetrics,
    setIsConnected,
    setIsLoading,
    setError,
    setSelectedPersona,
    setHasCompletedOnboarding
  }

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  )
}

export function useDashboard() {
  const context = useContext(DashboardContext)
  if (!context) {
    throw new Error('useDashboard must be used within a DashboardProvider')
  }
  return context
}

export default DashboardContext
