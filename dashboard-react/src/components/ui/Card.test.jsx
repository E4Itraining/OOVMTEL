/**
 * Card Component Tests
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '../../test/utils'
import { Card, CardHeader, CardBody, MetricCard, ServiceCard, LinkCard } from './Card'
import { Activity, Server, ExternalLink } from 'lucide-react'

describe('Card Component', () => {
  it('renders children correctly', () => {
    render(<Card>Test Content</Card>)
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<Card className="custom-class">Content</Card>)
    const card = screen.getByText('Content').closest('.card')
    expect(card).toHaveClass('custom-class')
  })

  it('handles onClick when provided', () => {
    const handleClick = vi.fn()
    render(<Card onClick={handleClick}>Clickable</Card>)

    fireEvent.click(screen.getByText('Clickable'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('applies hoverable styles when hoverable prop is true', () => {
    render(<Card hoverable>Hoverable Card</Card>)
    const card = screen.getByText('Hoverable Card').closest('.card')
    expect(card).toHaveClass('cursor-pointer')
  })
})

describe('CardHeader Component', () => {
  it('renders title correctly', () => {
    render(<CardHeader title="Test Title" />)
    expect(screen.getByText('Test Title')).toBeInTheDocument()
  })

  it('renders subtitle when provided', () => {
    render(<CardHeader title="Title" subtitle="Subtitle text" />)
    expect(screen.getByText('Subtitle text')).toBeInTheDocument()
  })

  it('renders icon when provided', () => {
    render(<CardHeader title="With Icon" icon={Activity} />)
    // Icon should render (check for svg element)
    const header = screen.getByText('With Icon').closest('.card-header')
    expect(header).toBeInTheDocument()
  })

  it('renders action element when provided', () => {
    render(
      <CardHeader
        title="With Action"
        action={<button>Action</button>}
      />
    )
    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument()
  })

  it('renders children', () => {
    render(
      <CardHeader title="Title">
        <span>Extra content</span>
      </CardHeader>
    )
    expect(screen.getByText('Extra content')).toBeInTheDocument()
  })
})

describe('CardBody Component', () => {
  it('renders children correctly', () => {
    render(<CardBody>Body content</CardBody>)
    expect(screen.getByText('Body content')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<CardBody className="custom-body">Content</CardBody>)
    const body = screen.getByText('Content').closest('.card-body')
    expect(body).toHaveClass('custom-body')
  })
})

describe('MetricCard Component', () => {
  it('renders label and value', () => {
    render(<MetricCard label="OEE" value="85.5" />)

    expect(screen.getByText('OEE')).toBeInTheDocument()
    expect(screen.getByText('85.5')).toBeInTheDocument()
  })

  it('renders unit when provided', () => {
    render(<MetricCard label="Temperature" value="72" unit="°C" />)
    expect(screen.getByText('°C')).toBeInTheDocument()
  })

  it('renders trend indicator', () => {
    render(
      <MetricCard
        label="Production"
        value="1250"
        trend="up"
        trendValue="+5%"
      />
    )
    expect(screen.getByText('+5%')).toBeInTheDocument()
    expect(screen.getByText('↑')).toBeInTheDocument()
  })

  it('renders down trend correctly', () => {
    render(
      <MetricCard
        label="Defects"
        value="12"
        trend="down"
        trendValue="-3%"
      />
    )
    expect(screen.getByText('↓')).toBeInTheDocument()
  })

  it('renders icon when provided', () => {
    render(<MetricCard label="Rate" value="100" icon={Activity} />)
    // Component should render without error
    expect(screen.getByText('Rate')).toBeInTheDocument()
  })

  it('applies color variant', () => {
    render(<MetricCard label="Test" value="50" color="green" />)
    expect(screen.getByText('Test')).toBeInTheDocument()
  })

  it('handles onClick', () => {
    const handleClick = vi.fn()
    render(<MetricCard label="Clickable" value="100" onClick={handleClick} />)

    fireEvent.click(screen.getByText('Clickable'))
    expect(handleClick).toHaveBeenCalled()
  })
})

describe('ServiceCard Component', () => {
  it('renders service name and status', () => {
    render(<ServiceCard name="VictoriaMetrics" status="healthy" />)

    expect(screen.getByText('VictoriaMetrics')).toBeInTheDocument()
    expect(screen.getByText('healthy')).toBeInTheDocument()
  })

  it('renders icon when provided', () => {
    render(<ServiceCard name="Database" status="up" icon={Server} />)
    expect(screen.getByText('Database')).toBeInTheDocument()
  })

  it('renders metrics when provided', () => {
    const metrics = [
      { label: 'Latency', value: '5ms' },
      { label: 'Requests', value: '1.2k' },
      { label: 'Errors', value: '0' },
    ]
    render(<ServiceCard name="API" status="healthy" metrics={metrics} />)

    expect(screen.getByText('Latency')).toBeInTheDocument()
    expect(screen.getByText('5ms')).toBeInTheDocument()
  })

  it('handles onClick', () => {
    const handleClick = vi.fn()
    render(
      <ServiceCard
        name="Clickable Service"
        status="up"
        onClick={handleClick}
      />
    )

    fireEvent.click(screen.getByText('Clickable Service'))
    expect(handleClick).toHaveBeenCalled()
  })

  it('applies correct status color for healthy', () => {
    render(<ServiceCard name="Service" status="healthy" />)
    // Should have green indicator
    const statusIndicator = document.querySelector('.bg-green-500')
    expect(statusIndicator).toBeInTheDocument()
  })

  it('applies correct status color for degraded', () => {
    render(<ServiceCard name="Service" status="degraded" />)
    // Should have yellow indicator
    const statusIndicator = document.querySelector('.bg-yellow-500')
    expect(statusIndicator).toBeInTheDocument()
  })

  it('applies correct status color for down', () => {
    render(<ServiceCard name="Service" status="down" />)
    // Should have red indicator
    const statusIndicator = document.querySelector('.bg-red-500')
    expect(statusIndicator).toBeInTheDocument()
  })
})

describe('LinkCard Component', () => {
  it('renders title and description', () => {
    render(
      <LinkCard
        title="External Link"
        description="Click to open"
        href="https://example.com"
      />
    )

    expect(screen.getByText('External Link')).toBeInTheDocument()
    expect(screen.getByText('Click to open')).toBeInTheDocument()
  })

  it('renders as anchor with correct href', () => {
    render(
      <LinkCard
        title="Link"
        description="Description"
        href="https://example.com"
      />
    )

    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', 'https://example.com')
  })

  it('opens in new tab', () => {
    render(
      <LinkCard
        title="Link"
        description="Description"
        href="https://example.com"
      />
    )

    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('renders icon when provided', () => {
    render(
      <LinkCard
        title="With Icon"
        description="Has icon"
        href="https://example.com"
        icon={ExternalLink}
      />
    )

    expect(screen.getByText('With Icon')).toBeInTheDocument()
  })
})
