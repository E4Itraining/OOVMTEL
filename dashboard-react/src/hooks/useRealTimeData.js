import { useEffect, useRef, useCallback, useState } from 'react'
import { useDashboard } from '../context/DashboardContext'

const API_BASE = '/api'
const WS_URL = `ws://${window.location.host}/ws`
const POLLING_INTERVAL = 5000
// Set to true to force demo data without API connections
const OFFLINE_MODE = false

// Demo data to use when API is unavailable
const DEMO_DATA = {
  business: {
    oee: 87.5,
    availability: 92,
    performance: 95,
    quality: 99.2,
    productionToday: 3247,
    cycleTime: 45,
    defectsToday: 12,
    criticalAlarms: 2,
    equipmentStatus: [
      { name: 'Robot-01', status: 'running', efficiency: 94 },
      { name: 'CNC-02', status: 'running', efficiency: 87 },
      { name: 'Conveyor-03', status: 'warning', efficiency: 72 },
      { name: 'Press-04', status: 'running', efficiency: 91 },
      { name: 'Welder-05', status: 'idle', efficiency: 0 },
      { name: 'Assembly-06', status: 'running', efficiency: 88 },
    ],
    productionByProduct: [
      { name: 'Prod A', value: 1250, color: '#06b6d4' },
      { name: 'Prod B', value: 890, color: '#a855f7' },
      { name: 'Prod C', value: 650, color: '#22c55e' },
      { name: 'Prod D', value: 420, color: '#f59e0b' },
    ]
  },
  tech: {
    metricsRate: 85000,
    logsRate: 45000,
    tracesRate: 12000,
    latencyP95: 42,
    errorRate: 0.05,
    kafkaThroughput: 125000,
    cpu: 45,
    memory: 62,
    disk: 38,
    vmActiveSeries: 250000,
    vmStorage: '2.4GB',
    vmQueryLatency: 12,
    osDocuments: 125000,
    osHealth: 'green',
    osNodes: 3,
    kafkaTopics: 12,
    kafkaPartitions: 96,
    kafkaConsumerLag: 0
  },
  services: [
    { name: 'VictoriaMetrics', status: 'up', latency: 5 },
    { name: 'OTEL Collector', status: 'up', latency: 3 },
    { name: 'OpenSearch', status: 'up', latency: 12 },
    { name: 'OpenObserve', status: 'up', latency: 8 },
    { name: 'Grafana', status: 'up', latency: 4 },
    { name: 'Kafka', status: 'up', latency: 2 }
  ],
  events: [
    { id: 1, type: 'production', message: 'Batch #1247 completed', timestamp: new Date().toISOString(), severity: 'info' },
    { id: 2, type: 'quality', message: 'Quality check passed - Line 2', timestamp: new Date().toISOString(), severity: 'success' },
    { id: 3, type: 'maintenance', message: 'Scheduled maintenance - Press-04', timestamp: new Date().toISOString(), severity: 'warning' },
    { id: 4, type: 'alarm', message: 'Temperature threshold alert - Reactor-01', timestamp: new Date().toISOString(), severity: 'warning' }
  ]
}

export function useRealTimeData() {
  const { updateMetrics, setIsConnected, setError, setIsLoading } = useDashboard()
  const wsRef = useRef(null)
  const pollingRef = useRef(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5
  const apiFailureCount = useRef(0)
  const maxApiFailures = 3

  const loadDemoData = useCallback(() => {
    console.log('Loading demo data (API unavailable)')
    // Add slight randomness to demo data to simulate real-time updates
    const randomVariation = (value, variance = 0.05) => {
      return value * (1 + (Math.random() - 0.5) * variance * 2)
    }

    const demoWithVariation = {
      business: {
        ...DEMO_DATA.business,
        oee: Math.round(randomVariation(DEMO_DATA.business.oee, 0.02) * 10) / 10,
        productionToday: Math.round(randomVariation(DEMO_DATA.business.productionToday, 0.03)),
        cycleTime: Math.round(randomVariation(DEMO_DATA.business.cycleTime, 0.05)),
      },
      tech: {
        ...DEMO_DATA.tech,
        metricsRate: Math.round(randomVariation(DEMO_DATA.tech.metricsRate)),
        logsRate: Math.round(randomVariation(DEMO_DATA.tech.logsRate)),
        tracesRate: Math.round(randomVariation(DEMO_DATA.tech.tracesRate)),
        cpu: Math.round(randomVariation(DEMO_DATA.tech.cpu, 0.1)),
        memory: Math.round(randomVariation(DEMO_DATA.tech.memory, 0.1)),
      },
      services: DEMO_DATA.services,
      events: DEMO_DATA.events
    }

    updateMetrics(demoWithVariation)
  }, [updateMetrics])

  const fetchMetrics = useCallback(async () => {
    try {
      const [metricsRes, servicesRes, eventsRes] = await Promise.all([
        fetch(`${API_BASE}/metrics`),
        fetch(`${API_BASE}/services`),
        fetch(`${API_BASE}/events`)
      ])

      if (!metricsRes.ok || !servicesRes.ok || !eventsRes.ok) {
        throw new Error('Failed to fetch data')
      }

      const [metricsData, servicesData, eventsData] = await Promise.all([
        metricsRes.json(),
        servicesRes.json(),
        eventsRes.json()
      ])

      updateMetrics({
        business: metricsData.business || metricsData,
        tech: metricsData.tech || {},
        services: servicesData.services || servicesData || [],
        events: eventsData.events || eventsData || []
      })

      apiFailureCount.current = 0
      setError(null)
    } catch (err) {
      console.error('Error fetching metrics:', err)
      apiFailureCount.current++

      // After multiple API failures, fall back to demo data
      if (apiFailureCount.current >= maxApiFailures) {
        loadDemoData()
        setError('API unavailable - showing demo data')
      } else {
        setError(err.message)
        setIsLoading(false)
      }
    }
  }, [updateMetrics, setError, setIsLoading, loadDemoData])

  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    try {
      wsRef.current = new WebSocket(WS_URL)

      wsRef.current.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        reconnectAttempts.current = 0
        // Clear polling when WS is connected
        if (pollingRef.current) {
          clearInterval(pollingRef.current)
          pollingRef.current = null
        }
      }

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          updateMetrics({
            business: data.business || data,
            tech: data.tech || {},
            services: data.services || [],
            events: data.events || []
          })
        } catch (err) {
          console.error('Error parsing WebSocket message:', err)
        }
      }

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        wsRef.current = null

        // Attempt reconnect with backoff
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
          reconnectAttempts.current++
          setTimeout(connectWebSocket, delay)
        } else {
          // Fall back to polling
          startPolling()
        }
      }

      wsRef.current.onerror = (err) => {
        console.error('WebSocket error:', err)
        wsRef.current?.close()
      }
    } catch (err) {
      console.error('Failed to create WebSocket:', err)
      startPolling()
    }
  }, [updateMetrics, setIsConnected])

  const startPolling = useCallback(() => {
    if (pollingRef.current) return

    console.log('Starting HTTP polling fallback')
    fetchMetrics() // Initial fetch
    pollingRef.current = setInterval(fetchMetrics, POLLING_INTERVAL)
  }, [fetchMetrics])

  useEffect(() => {
    // Initialize data - either from API or demo data
    const initializeData = async () => {
      // Always offline mode - use demo data without API calls
      if (OFFLINE_MODE) {
        console.log('Offline mode enabled - using demo data')
        loadDemoData()
        setIsConnected(false)
        // Start demo data polling to simulate real-time updates
        if (!pollingRef.current) {
          pollingRef.current = setInterval(loadDemoData, POLLING_INTERVAL)
        }
        return
      }

      // Online mode - try to connect to API
      try {
        // Quick connectivity check with timeout
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 3000)

        const response = await fetch(`${API_BASE}/metrics`, {
          signal: controller.signal
        })
        clearTimeout(timeoutId)

        if (response.ok) {
          // API is available, proceed normally
          await fetchMetrics()
          connectWebSocket()
        } else {
          throw new Error('API not ready')
        }
      } catch (err) {
        // API unavailable, load demo data immediately
        console.log('API unavailable, loading demo data')
        loadDemoData()
        // Still try polling in background in case API comes up
        startPolling()
      }
    }

    initializeData()

    // Cleanup
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
  }, [connectWebSocket, fetchMetrics, loadDemoData, startPolling, setIsConnected])

  return { refetch: fetchMetrics, loadDemoData }
}

export function useServiceDetails(serviceName) {
  const [details, setDetails] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchDetails = useCallback(async () => {
    if (!serviceName) return

    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/services/${serviceName}`)
      if (!response.ok) throw new Error('Failed to fetch service details')
      const data = await response.json()
      setDetails(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [serviceName])

  useEffect(() => {
    fetchDetails()
  }, [fetchDetails])

  return { details, loading, error, refetch: fetchDetails }
}
