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
  // Métriques OT (Operational Technology) - Zone industrielle
  ot: {
    // Santé globale OT
    globalHealth: 0,
    // Systèmes OT
    scada: {
      status: 'unknown',
      connectedDevices: 0,
      activeAlarms: 0,
      dataPointsPerSec: 0,
      lastSync: null
    },
    mes: {
      status: 'unknown',
      activeOrders: 0,
      completedToday: 0,
      pendingOrders: 0,
      efficiency: 0
    },
    plm: {
      status: 'unknown',
      activeProducts: 0,
      revisionsPending: 0,
      qualityHolds: 0
    },
    opcua: {
      status: 'unknown',
      connectedServers: 0,
      activeSubscriptions: 0,
      tagsMonitored: 0,
      latencyMs: 0
    },
    // Métriques industrielles avancées
    mtbf: 0, // Mean Time Between Failures (heures)
    mttr: 0, // Mean Time To Repair (heures)
    trs: { // Taux de Rendement Synthétique détaillé
      disponibilite: 0,
      performance: 0,
      qualite: 0,
      global: 0
    },
    // Par zone de production
    zones: [],
    // Par ligne de production
    productionLines: [],
    // Chaîne logique-métier (dépendances)
    dependencyChain: [],
    // Impacts actifs
    activeImpacts: [],
    // Cascades d'impact en cours
    activeCascades: []
  },
  // Graphe de dépendances IT/OT
  itotGraph: {
    // Nœuds du graphe (systèmes IT et OT)
    nodes: [],
    // Connexions entre nœuds
    edges: [],
    // Impacts actifs avec propagation
    impacts: [],
    // Métriques du graphe
    stats: {
      totalNodes: 0,
      itNodes: 0,
      otNodes: 0,
      connections: 0,
      healthRate: 100,
      activeImpacts: 0,
      criticalImpacts: 0,
      totalLoss: 0
    }
  },
  // Corrélations IT/OT
  correlations: {
    // Alertes corrélées IT/OT
    correlatedAlerts: [],
    // Patterns détectés
    detectedPatterns: [],
    // Score de corrélation global
    correlationScore: 0,
    // Dernière analyse
    lastAnalysis: null
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
    setError
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
