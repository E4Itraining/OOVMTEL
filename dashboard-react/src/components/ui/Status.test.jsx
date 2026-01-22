/**
 * Status Component Tests
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '../../test/utils'
import { StatusBadge, StatusDot, HealthIndicator, LoadingSpinner, Skeleton } from './Status'

describe('StatusBadge Component', () => {
  it('renders with default status', () => {
    render(<StatusBadge status="ok" />)
    expect(screen.getByText('OK')).toBeInTheDocument()
  })

  it('renders with custom label', () => {
    render(<StatusBadge status="ok" label="Online" />)
    expect(screen.getByText('Online')).toBeInTheDocument()
  })

  it('applies correct color for healthy status', () => {
    render(<StatusBadge status="healthy" />)
    const badge = screen.getByText('Healthy')
    expect(badge).toBeInTheDocument()
  })

  it('applies correct color for warning status', () => {
    render(<StatusBadge status="warning" />)
    const badge = screen.getByText('Warning')
    expect(badge).toBeInTheDocument()
  })

  it('applies correct color for error status', () => {
    render(<StatusBadge status="error" />)
    const badge = screen.getByText('Error')
    expect(badge).toBeInTheDocument()
  })

  it('handles unknown status gracefully', () => {
    render(<StatusBadge status="unknown" />)
    const badge = screen.getByText('Unknown')
    expect(badge).toBeInTheDocument()
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<StatusBadge status="ok" size="sm" />)
    expect(screen.getByText('OK')).toBeInTheDocument()

    rerender(<StatusBadge status="ok" size="lg" />)
    expect(screen.getByText('OK')).toBeInTheDocument()
  })
})

describe('StatusDot Component', () => {
  it('renders with default size', () => {
    render(<StatusDot status="ok" />)
    const dot = document.querySelector('.rounded-full')
    expect(dot).toBeInTheDocument()
  })

  it('renders with custom size', () => {
    render(<StatusDot status="ok" size="lg" />)
    const dot = document.querySelector('.rounded-full')
    expect(dot).toBeInTheDocument()
  })

  it('renders with pulse animation by default', () => {
    render(<StatusDot status="ok" />)
    const animatedDot = document.querySelector('.animate-ping')
    expect(animatedDot).toBeInTheDocument()
  })

  it('can disable pulse animation', () => {
    render(<StatusDot status="ok" pulse={false} />)
    const animatedDot = document.querySelector('.animate-ping')
    expect(animatedDot).not.toBeInTheDocument()
  })

  it('renders healthy status with green color', () => {
    render(<StatusDot status="healthy" />)
    const dot = document.querySelector('.bg-green-500')
    expect(dot).toBeInTheDocument()
  })

  it('renders warning status with yellow color', () => {
    render(<StatusDot status="warning" />)
    const dot = document.querySelector('.bg-yellow-500')
    expect(dot).toBeInTheDocument()
  })

  it('renders error status with red color', () => {
    render(<StatusDot status="error" />)
    const dot = document.querySelector('.bg-red-500')
    expect(dot).toBeInTheDocument()
  })

  it('renders unknown status with gray color', () => {
    render(<StatusDot status="unknown" />)
    const dot = document.querySelector('.bg-gray-500')
    expect(dot).toBeInTheDocument()
  })
})

describe('HealthIndicator Component', () => {
  it('renders with services list', () => {
    const services = [
      { name: 'API', status: 'healthy' },
      { name: 'DB', status: 'healthy' },
    ]
    render(<HealthIndicator services={services} />)
    expect(screen.getByText('System Health')).toBeInTheDocument()
  })

  it('displays correct health percentage', () => {
    const services = [
      { name: 'API', status: 'healthy' },
      { name: 'DB', status: 'healthy' },
    ]
    render(<HealthIndicator services={services} />)
    expect(screen.getByText('100%')).toBeInTheDocument()
  })

  it('shows correct counts for different statuses', () => {
    const services = [
      { name: 'API', status: 'healthy' },
      { name: 'DB', status: 'degraded' },
      { name: 'Cache', status: 'down' },
    ]
    render(<HealthIndicator services={services} />)
    expect(screen.getByText(/1 Healthy/)).toBeInTheDocument()
    expect(screen.getByText(/1 Degraded/)).toBeInTheDocument()
    expect(screen.getByText(/1 Down/)).toBeInTheDocument()
  })

  it('handles empty services array', () => {
    render(<HealthIndicator services={[]} />)
    expect(screen.getByText('System Health')).toBeInTheDocument()
    expect(screen.getByText('0%')).toBeInTheDocument()
  })
})

describe('LoadingSpinner Component', () => {
  it('renders with default size', () => {
    render(<LoadingSpinner />)
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('renders with label', () => {
    render(<LoadingSpinner label="Loading data..." />)
    expect(screen.getByText('Loading data...')).toBeInTheDocument()
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<LoadingSpinner size="sm" />)
    expect(document.querySelector('.w-4')).toBeInTheDocument()

    rerender(<LoadingSpinner size="lg" />)
    expect(document.querySelector('.w-12')).toBeInTheDocument()
  })
})

describe('Skeleton Component', () => {
  it('renders with default class', () => {
    render(<Skeleton />)
    const skeleton = document.querySelector('.skeleton')
    expect(skeleton).toBeInTheDocument()
  })

  it('accepts custom className', () => {
    render(<Skeleton className="h-10 w-full" />)
    const skeleton = document.querySelector('.skeleton.h-10.w-full')
    expect(skeleton).toBeInTheDocument()
  })
})
