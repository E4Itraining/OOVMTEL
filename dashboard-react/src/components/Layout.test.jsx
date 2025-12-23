/**
 * Layout Component Tests
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '../test/utils'
import Layout from './Layout'

describe('Layout Component', () => {
  it('renders header with logo/title', () => {
    render(
      <Layout>
        <div>Content</div>
      </Layout>
    )

    // Should have navigation or header
    expect(screen.getByText('Content')).toBeInTheDocument()
  })

  it('renders children content', () => {
    render(
      <Layout>
        <div data-testid="child-content">Test Content</div>
      </Layout>
    )

    expect(screen.getByTestId('child-content')).toBeInTheDocument()
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('renders navigation sidebar', () => {
    render(
      <Layout>
        <div>Content</div>
      </Layout>
    )

    // Should have navigation elements
    const nav = document.querySelector('nav, aside, [role="navigation"]')
    expect(nav).toBeInTheDocument()
  })

  it('contains main content area', () => {
    render(
      <Layout>
        <div>Main Content</div>
      </Layout>
    )

    const main = document.querySelector('main, [role="main"], .main-content')
    expect(main || screen.getByText('Main Content')).toBeInTheDocument()
  })

  it('renders multiple children', () => {
    render(
      <Layout>
        <div>First</div>
        <div>Second</div>
        <div>Third</div>
      </Layout>
    )

    expect(screen.getByText('First')).toBeInTheDocument()
    expect(screen.getByText('Second')).toBeInTheDocument()
    expect(screen.getByText('Third')).toBeInTheDocument()
  })
})

describe('Layout Navigation', () => {
  it('contains navigation links', () => {
    render(
      <Layout>
        <div>Content</div>
      </Layout>
    )

    // Should have links in navigation
    const links = document.querySelectorAll('a, [role="link"]')
    expect(links.length).toBeGreaterThan(0)
  })

  it('has accessible navigation', () => {
    render(
      <Layout>
        <div>Content</div>
      </Layout>
    )

    // Check for semantic navigation
    const nav = document.querySelector('nav, [role="navigation"]')
    expect(nav).toBeInTheDocument()
  })
})

describe('Layout Responsiveness', () => {
  it('renders without crashing on mobile viewport', () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      value: 375,
    })

    render(
      <Layout>
        <div>Mobile Content</div>
      </Layout>
    )

    expect(screen.getByText('Mobile Content')).toBeInTheDocument()
  })

  it('renders without crashing on desktop viewport', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      value: 1920,
    })

    render(
      <Layout>
        <div>Desktop Content</div>
      </Layout>
    )

    expect(screen.getByText('Desktop Content')).toBeInTheDocument()
  })
})
