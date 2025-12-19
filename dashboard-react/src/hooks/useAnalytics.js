import { useCallback, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'

// Analytics event types
export const ANALYTICS_EVENTS = {
  // Page views
  PAGE_VIEW: 'page_view',

  // User actions
  BUTTON_CLICK: 'button_click',
  LINK_CLICK: 'link_click',
  FORM_SUBMIT: 'form_submit',

  // Feature usage
  FEATURE_USED: 'feature_used',
  SEARCH_PERFORMED: 'search_performed',
  EXPORT_INITIATED: 'export_initiated',

  // AI Assistant
  AI_QUERY: 'ai_query',
  AI_SUGGESTION_CLICKED: 'ai_suggestion_clicked',

  // Navigation
  NAVIGATION: 'navigation',
  SIDEBAR_TOGGLE: 'sidebar_toggle',
  MODE_SWITCH: 'mode_switch',

  // Errors
  ERROR_OCCURRED: 'error_occurred',
  API_ERROR: 'api_error',

  // Performance
  PERFORMANCE_METRIC: 'performance_metric',

  // Session
  SESSION_START: 'session_start',
  SESSION_END: 'session_end'
}

// Analytics queue for batching
let analyticsQueue = []
let flushTimeout = null

// Configuration
const ANALYTICS_CONFIG = {
  enabled: true,
  debug: process.env.NODE_ENV === 'development',
  batchSize: 10,
  flushInterval: 5000, // 5 seconds
  endpoint: '/api/analytics', // Backend endpoint
  sessionTimeout: 30 * 60 * 1000 // 30 minutes
}

// Generate session ID
function generateSessionId() {
  return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// Get or create session
function getSession() {
  const stored = sessionStorage.getItem('synapsix_analytics_session')
  if (stored) {
    const session = JSON.parse(stored)
    const now = Date.now()
    if (now - session.lastActivity < ANALYTICS_CONFIG.sessionTimeout) {
      session.lastActivity = now
      sessionStorage.setItem('synapsix_analytics_session', JSON.stringify(session))
      return session
    }
  }

  const newSession = {
    id: generateSessionId(),
    startTime: Date.now(),
    lastActivity: Date.now(),
    pageViews: 0
  }
  sessionStorage.setItem('synapsix_analytics_session', JSON.stringify(newSession))
  return newSession
}

// Send events to backend
async function sendEvents(events) {
  if (!ANALYTICS_CONFIG.enabled || events.length === 0) return

  try {
    if (ANALYTICS_CONFIG.debug) {
      console.log('[Analytics] Sending events:', events)
    }

    // In production, send to backend
    // await fetch(ANALYTICS_CONFIG.endpoint, {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ events })
    // })

    // For demo, just log to console
    if (ANALYTICS_CONFIG.debug) {
      console.table(events.map(e => ({
        event: e.event,
        page: e.properties?.page,
        timestamp: new Date(e.timestamp).toISOString()
      })))
    }
  } catch (error) {
    console.error('[Analytics] Failed to send events:', error)
  }
}

// Flush the queue
function flushQueue() {
  if (analyticsQueue.length > 0) {
    const events = [...analyticsQueue]
    analyticsQueue = []
    sendEvents(events)
  }
}

// Add event to queue
function queueEvent(event) {
  analyticsQueue.push(event)

  if (analyticsQueue.length >= ANALYTICS_CONFIG.batchSize) {
    flushQueue()
  } else if (!flushTimeout) {
    flushTimeout = setTimeout(() => {
      flushQueue()
      flushTimeout = null
    }, ANALYTICS_CONFIG.flushInterval)
  }
}

// Track event function
export function trackEvent(eventName, properties = {}) {
  const session = getSession()

  const event = {
    event: eventName,
    properties: {
      ...properties,
      sessionId: session.id,
      page: window.location.pathname,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
      screenSize: `${window.innerWidth}x${window.innerHeight}`,
      language: navigator.language
    },
    timestamp: Date.now()
  }

  // Add user info if available
  const user = localStorage.getItem('synapsix_user')
  if (user) {
    try {
      const userData = JSON.parse(user)
      event.properties.userId = userData.email
      event.properties.userRole = userData.role
    } catch (e) {
      // Ignore parsing errors
    }
  }

  // Add persona if available
  const persona = localStorage.getItem('selectedPersona')
  if (persona) {
    event.properties.persona = persona
  }

  queueEvent(event)

  // Update session page views
  if (eventName === ANALYTICS_EVENTS.PAGE_VIEW) {
    session.pageViews++
    sessionStorage.setItem('synapsix_analytics_session', JSON.stringify(session))
  }
}

// Track page view
export function trackPageView(pageName, additionalProps = {}) {
  trackEvent(ANALYTICS_EVENTS.PAGE_VIEW, {
    pageName,
    ...additionalProps
  })
}

// Track feature usage
export function trackFeatureUsage(featureName, additionalProps = {}) {
  trackEvent(ANALYTICS_EVENTS.FEATURE_USED, {
    featureName,
    ...additionalProps
  })
}

// Track error
export function trackError(error, context = {}) {
  trackEvent(ANALYTICS_EVENTS.ERROR_OCCURRED, {
    errorMessage: error.message || String(error),
    errorStack: error.stack,
    ...context
  })
}

// Track performance metric
export function trackPerformance(metricName, value, unit = 'ms') {
  trackEvent(ANALYTICS_EVENTS.PERFORMANCE_METRIC, {
    metricName,
    value,
    unit
  })
}

// Hook for analytics
export function useAnalytics() {
  const location = useLocation()
  const prevPathRef = useRef(location.pathname)

  // Track page views on route change
  useEffect(() => {
    if (location.pathname !== prevPathRef.current) {
      trackPageView(location.pathname)
      prevPathRef.current = location.pathname
    }
  }, [location.pathname])

  // Track session start
  useEffect(() => {
    trackEvent(ANALYTICS_EVENTS.SESSION_START)

    // Track session end on unload
    const handleUnload = () => {
      trackEvent(ANALYTICS_EVENTS.SESSION_END)
      flushQueue()
    }

    window.addEventListener('beforeunload', handleUnload)
    return () => {
      window.removeEventListener('beforeunload', handleUnload)
    }
  }, [])

  // Memoized tracking functions
  const track = useCallback((eventName, properties) => {
    trackEvent(eventName, properties)
  }, [])

  const trackClick = useCallback((elementName, additionalProps = {}) => {
    trackEvent(ANALYTICS_EVENTS.BUTTON_CLICK, {
      elementName,
      ...additionalProps
    })
  }, [])

  const trackSearch = useCallback((query, resultsCount) => {
    trackEvent(ANALYTICS_EVENTS.SEARCH_PERFORMED, {
      query,
      resultsCount
    })
  }, [])

  const trackAIQuery = useCallback((query, responseTime) => {
    trackEvent(ANALYTICS_EVENTS.AI_QUERY, {
      queryLength: query.length,
      responseTime
    })
  }, [])

  const trackExport = useCallback((format, dataType) => {
    trackEvent(ANALYTICS_EVENTS.EXPORT_INITIATED, {
      format,
      dataType
    })
  }, [])

  const trackModeSwitch = useCallback((fromMode, toMode) => {
    trackEvent(ANALYTICS_EVENTS.MODE_SWITCH, {
      fromMode,
      toMode
    })
  }, [])

  return {
    track,
    trackClick,
    trackSearch,
    trackAIQuery,
    trackExport,
    trackModeSwitch,
    trackFeatureUsage,
    trackError,
    trackPerformance
  }
}

// HOC for tracking component visibility
export function withAnalytics(WrappedComponent, componentName) {
  return function AnalyticsWrapper(props) {
    useEffect(() => {
      trackFeatureUsage(componentName, { action: 'viewed' })
    }, [])

    return <WrappedComponent {...props} />
  }
}

// Performance monitoring utility
export function measurePerformance(name, fn) {
  const start = performance.now()
  const result = fn()
  const duration = performance.now() - start
  trackPerformance(name, duration)
  return result
}

// Async performance monitoring
export async function measureAsyncPerformance(name, fn) {
  const start = performance.now()
  const result = await fn()
  const duration = performance.now() - start
  trackPerformance(name, duration)
  return result
}

export default useAnalytics
