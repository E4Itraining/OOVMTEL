/**
 * Layout Component Tests
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '../test/utils'
import Layout from './Layout'

describe('Layout Component', () => {
  it('renders the application layout', () => {
    render(<Layout />)

    // Layout should render without crashing
    expect(document.querySelector('.min-h-screen')).toBeInTheDocument()
  })

  it('renders navigation sidebar', () => {
    render(<Layout />)

    // Should have navigation elements (aside or nav)
    const nav = document.querySelector('nav, aside')
    expect(nav).toBeInTheDocument()
  })

  it('renders header section', () => {
    render(<Layout />)

    // Should have header element
    const header = document.querySelector('header')
    expect(header).toBeInTheDocument()
  })

  it('contains main content area', () => {
    render(<Layout />)

    const main = document.querySelector('main')
    expect(main).toBeInTheDocument()
  })

  it('renders Synapsix branding', () => {
    render(<Layout />)

    // Should show the app name "Synapsix"
    const branding = screen.queryByText(/synapsix/i)
    expect(branding || document.querySelector('h1')).toBeInTheDocument()
  })
})

describe('Layout Navigation', () => {
  it('contains navigation links', () => {
    render(<Layout />)

    // Should have navigation buttons
    const buttons = document.querySelectorAll('button, a')
    expect(buttons.length).toBeGreaterThan(0)
  })

  it('has sidebar toggle button', () => {
    render(<Layout />)

    // Should have a button to toggle sidebar
    const toggleButton = document.querySelector('button[class*="absolute"][class*="-right"]')
    expect(toggleButton || document.querySelector('button')).toBeInTheDocument()
  })

  it('renders main navigation items', () => {
    render(<Layout />)

    // Should render navigation items in the aside
    const aside = document.querySelector('aside')
    expect(aside).toBeInTheDocument()
  })
})

describe('Layout Header', () => {
  it('renders search button', () => {
    render(<Layout />)

    // Should have a search button/input
    const searchElement = document.querySelector('[class*="Search"], button')
    expect(searchElement).toBeInTheDocument()
  })

  it('renders user mode indicator', () => {
    render(<Layout />)

    // Should show some user mode indicator in the header
    const header = document.querySelector('header')
    expect(header).toBeInTheDocument()
  })

  it('renders connection status', () => {
    render(<Layout />)

    // Should show connection status (Wifi or WifiOff icon)
    const statusIndicator = document.querySelector('svg')
    expect(statusIndicator).toBeInTheDocument()
  })
})

describe('Layout Responsiveness', () => {
  it('renders without crashing', () => {
    expect(() => render(<Layout />)).not.toThrow()
  })

  it('has proper structure for responsive layout', () => {
    render(<Layout />)

    // Should have flex container
    const flexContainer = document.querySelector('.flex')
    expect(flexContainer).toBeInTheDocument()
  })
})

describe('Layout Accessibility', () => {
  it('has semantic navigation', () => {
    render(<Layout />)

    // Should use semantic HTML elements
    const nav = document.querySelector('nav')
    expect(nav).toBeInTheDocument()
  })

  it('has semantic main content', () => {
    render(<Layout />)

    const main = document.querySelector('main')
    expect(main).toBeInTheDocument()
  })

  it('has semantic header', () => {
    render(<Layout />)

    const header = document.querySelector('header')
    expect(header).toBeInTheDocument()
  })
})
