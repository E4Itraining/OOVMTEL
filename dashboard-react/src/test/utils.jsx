/**
 * OOVMTEL Test Utilities
 *
 * Common utilities and wrappers for testing React components.
 */

import React from 'react'
import { render } from '@testing-library/react'
import { BrowserRouter, MemoryRouter } from 'react-router-dom'
import { I18nProvider } from '../i18n/I18nContext'
import { DashboardProvider } from '../context/DashboardContext'

/**
 * All-in-one provider wrapper for testing
 */
function AllProviders({ children, initialRoute = '/' }) {
  return (
    <MemoryRouter initialEntries={[initialRoute]}>
      <I18nProvider>
        <DashboardProvider>
          {children}
        </DashboardProvider>
      </I18nProvider>
    </MemoryRouter>
  )
}

/**
 * Custom render with all providers
 */
function customRender(ui, options = {}) {
  const { initialRoute = '/', ...renderOptions } = options

  return render(ui, {
    wrapper: ({ children }) => (
      <AllProviders initialRoute={initialRoute}>{children}</AllProviders>
    ),
    ...renderOptions,
  })
}

/**
 * Render with just Router (for simpler tests)
 */
function renderWithRouter(ui, { route = '/' } = {}) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      {ui}
    </MemoryRouter>
  )
}

/**
 * Render with I18n context only
 */
function renderWithI18n(ui, options = {}) {
  return render(
    <I18nProvider>
      {ui}
    </I18nProvider>,
    options
  )
}

/**
 * Mock metrics data for testing
 */
export const mockMetricsData = {
  business: {
    oee: 85.5,
    quality_rate: 96.2,
    production_today: 1250,
    cycle_time: 25.3,
    defects_today: 12,
    critical_alarms: 3,
    availability: 94.0,
    performance: 91.2,
    equipment: [
      { id: 'eq1', name: 'CNC-001', status: 'running', health: 95 },
      { id: 'eq2', name: 'ROBOT-001', status: 'idle', health: 88 },
      { id: 'eq3', name: 'PRESS-001', status: 'maintenance', health: 72 },
    ],
    production_by_product: {
      ProductA: 450,
      ProductB: 380,
      ProductC: 420,
    },
    alarms: [
      { id: 'a1', severity: 'warning', message: 'Temperature high on CNC-001' },
      { id: 'a2', severity: 'critical', message: 'Vibration alert on PRESS-001' },
    ],
  },
  tech: {
    metrics_rate: 85000,
    logs_rate: 45000,
    traces_rate: 12000,
    latency_p95: 45.0,
    error_rate: 0.05,
    cpu_usage: 35.0,
    memory_usage: 62.0,
    disk_usage: 45.0,
    vm_active_series: 250000,
    vm_storage_size: 5000000000,
    vm_query_latency: 15.0,
    os_documents: 125000,
    os_health: 'green',
    os_nodes: 1,
  },
  services: [
    { name: 'VictoriaMetrics', status: 'up', port: 8428, latency_ms: 5.2 },
    { name: 'OTEL Collector', status: 'up', port: 4317, latency_ms: 3.1 },
    { name: 'OpenSearch', status: 'up', port: 9200, latency_ms: 12.4 },
  ],
  events: [
    {
      time: new Date().toISOString(),
      type: 'alert',
      title: 'High Temperature',
      desc: 'Temperature exceeded threshold on CNC-001',
    },
    {
      time: new Date().toISOString(),
      type: 'production',
      title: 'Batch Complete',
      desc: 'Batch #1234 completed successfully',
    },
  ],
  timestamp: new Date().toISOString(),
}

/**
 * Mock user personas for testing
 */
export const mockPersonas = [
  { id: 'ops_manager', name: 'Operations Manager', icon: 'BarChart3' },
  { id: 'maintenance', name: 'Maintenance Engineer', icon: 'Wrench' },
  { id: 'quality', name: 'Quality Manager', icon: 'CheckCircle' },
  { id: 'it_ops', name: 'IT Operations', icon: 'Server' },
]

/**
 * Wait for async operations
 */
export const waitFor = async (callback, { timeout = 1000, interval = 50 } = {}) => {
  const startTime = Date.now()
  while (Date.now() - startTime < timeout) {
    try {
      await callback()
      return
    } catch (e) {
      await new Promise(resolve => setTimeout(resolve, interval))
    }
  }
  await callback()
}

/**
 * Create mock WebSocket connection
 */
export function createMockWebSocket() {
  return {
    send: vi.fn(),
    close: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  }
}

/**
 * Mock API response
 */
export function mockApiResponse(data, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
  })
}

// Re-export everything from testing-library
export * from '@testing-library/react'

// Override render with custom render
export { customRender as render, renderWithRouter, renderWithI18n }
