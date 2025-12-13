import { useEffect, useRef, useCallback, useState } from 'react'
import { useDashboard } from '../context/DashboardContext'

const API_BASE = '/api'
const WS_URL = `ws://${window.location.host}/ws`
const POLLING_INTERVAL = 5000

export function useRealTimeData() {
  const { updateMetrics, setIsConnected, setError } = useDashboard()
  const wsRef = useRef(null)
  const pollingRef = useRef(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

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

      setError(null)
    } catch (err) {
      console.error('Error fetching metrics:', err)
      setError(err.message)
    }
  }, [updateMetrics, setError])

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
    // Try WebSocket first, fall back to polling
    fetchMetrics() // Initial data load
    connectWebSocket()

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
  }, [connectWebSocket, fetchMetrics])

  return { refetch: fetchMetrics }
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
