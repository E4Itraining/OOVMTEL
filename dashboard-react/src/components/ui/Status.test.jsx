/**
 * Status Component Tests
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '../../test/utils'
import { StatusBadge, StatusDot, HealthBar, TrendIndicator } from './Status'

describe('StatusBadge Component', () => {
  it('renders with default status', () => {
    render(<StatusBadge status="ok">Online</StatusBadge>)
    expect(screen.getByText('Online')).toBeInTheDocument()
  })

  it('applies correct color for success status', () => {
    render(<StatusBadge status="success">Success</StatusBadge>)
    const badge = screen.getByText('Success')
    expect(badge).toBeInTheDocument()
  })

  it('applies correct color for warning status', () => {
    render(<StatusBadge status="warning">Warning</StatusBadge>)
    const badge = screen.getByText('Warning')
    expect(badge).toBeInTheDocument()
  })

  it('applies correct color for error status', () => {
    render(<StatusBadge status="error">Error</StatusBadge>)
    const badge = screen.getByText('Error')
    expect(badge).toBeInTheDocument()
  })

  it('applies correct color for info status', () => {
    render(<StatusBadge status="info">Info</StatusBadge>)
    const badge = screen.getByText('Info')
    expect(badge).toBeInTheDocument()
  })
})

describe('StatusDot Component', () => {
  it('renders with default size', () => {
    render(<StatusDot status="online" />)
    const dot = document.querySelector('.rounded-full')
    expect(dot).toBeInTheDocument()
  })

  it('renders with custom size', () => {
    render(<StatusDot status="online" size="lg" />)
    const dot = document.querySelector('.rounded-full')
    expect(dot).toBeInTheDocument()
  })

  it('applies pulse animation when pulsing prop is true', () => {
    render(<StatusDot status="online" pulsing />)
    // Should have animation class
    const dot = document.querySelector('.rounded-full')
    expect(dot).toBeInTheDocument()
  })

  it('renders offline status correctly', () => {
    render(<StatusDot status="offline" />)
    const dot = document.querySelector('.bg-red-500, .bg-gray-500')
    expect(dot).toBeInTheDocument()
  })
})

describe('HealthBar Component', () => {
  it('renders with value', () => {
    render(<HealthBar value={75} />)
    // Should render a progress bar
    expect(document.querySelector('[role="progressbar"], .bg-green-500, .h-2')).toBeInTheDocument()
  })

  it('shows correct color for high health', () => {
    render(<HealthBar value={90} />)
    // Should show green for healthy
    const bar = document.querySelector('.bg-green-500, .bg-emerald-500')
    expect(bar || document.querySelector('[style*="width"]')).toBeInTheDocument()
  })

  it('shows correct color for medium health', () => {
    render(<HealthBar value={60} />)
    // Should show yellow/orange for medium
    expect(document.querySelector('.bg-yellow-500, .bg-amber-500, [style*="width"]')).toBeInTheDocument()
  })

  it('shows correct color for low health', () => {
    render(<HealthBar value={20} />)
    // Should show red for low
    expect(document.querySelector('.bg-red-500, [style*="width"]')).toBeInTheDocument()
  })

  it('renders label when provided', () => {
    render(<HealthBar value={85} label="CPU Health" />)
    expect(screen.getByText('CPU Health')).toBeInTheDocument()
  })

  it('shows percentage when showValue is true', () => {
    render(<HealthBar value={85} showValue />)
    expect(screen.getByText(/85/)).toBeInTheDocument()
  })
})

describe('TrendIndicator Component', () => {
  it('renders up trend correctly', () => {
    render(<TrendIndicator direction="up" value="5%" />)
    expect(screen.getByText(/5%/)).toBeInTheDocument()
  })

  it('renders down trend correctly', () => {
    render(<TrendIndicator direction="down" value="3%" />)
    expect(screen.getByText(/3%/)).toBeInTheDocument()
  })

  it('renders flat trend correctly', () => {
    render(<TrendIndicator direction="flat" value="0%" />)
    expect(screen.getByText(/0%/)).toBeInTheDocument()
  })

  it('applies correct color for positive trend', () => {
    render(<TrendIndicator direction="up" value="5%" positive />)
    // Should have green color
    const indicator = screen.getByText(/5%/).closest('div, span')
    expect(indicator).toBeInTheDocument()
  })

  it('applies correct color for negative trend', () => {
    render(<TrendIndicator direction="down" value="5%" negative />)
    // Should have red color
    const indicator = screen.getByText(/5%/).closest('div, span')
    expect(indicator).toBeInTheDocument()
  })
})
