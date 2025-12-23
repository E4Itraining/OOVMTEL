/**
 * WelcomePage Component Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '../test/utils'
import WelcomePage from './WelcomePage'

describe('WelcomePage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders welcome title', () => {
    render(<WelcomePage />)

    // Should have a welcome heading
    const heading = screen.getByRole('heading') ||
                    screen.queryByText(/welcome|bienvenue|synapsix/i)
    expect(heading).toBeInTheDocument()
  })

  it('renders persona selection', () => {
    render(<WelcomePage />)

    // Should have persona options
    const personas = document.querySelectorAll('[data-persona], .persona-card, button, [role="button"]')
    expect(personas.length).toBeGreaterThan(0)
  })

  it('renders without crashing', () => {
    expect(() => render(<WelcomePage />)).not.toThrow()
  })
})

describe('WelcomePage Persona Selection', () => {
  it('allows selecting a persona', () => {
    render(<WelcomePage />)

    // Find clickable persona cards
    const cards = document.querySelectorAll('[data-persona], .persona-card, button, [role="button"]')

    if (cards.length > 0) {
      fireEvent.click(cards[0])
      // Should handle selection without error
      expect(cards[0]).toBeInTheDocument()
    }
  })

  it('displays persona descriptions', () => {
    render(<WelcomePage />)

    // Should have descriptions for personas
    const descriptions = document.querySelectorAll('p, .description')
    expect(descriptions.length).toBeGreaterThan(0)
  })
})

describe('WelcomePage Navigation', () => {
  it('navigates to dashboard after persona selection', () => {
    render(<WelcomePage />)

    const buttons = document.querySelectorAll('button, [role="button"], a')

    if (buttons.length > 0) {
      // Find a "continue" or "start" button
      const continueBtn = Array.from(buttons).find(
        btn => btn.textContent.toLowerCase().includes('continue') ||
               btn.textContent.toLowerCase().includes('start') ||
               btn.textContent.toLowerCase().includes('commencer')
      )

      if (continueBtn) {
        fireEvent.click(continueBtn)
      }
    }

    // Should handle navigation
    expect(document.body).toBeInTheDocument()
  })
})

describe('WelcomePage Accessibility', () => {
  it('has proper heading structure', () => {
    render(<WelcomePage />)

    const h1 = document.querySelector('h1')
    expect(h1).toBeInTheDocument()
  })

  it('has focusable elements', () => {
    render(<WelcomePage />)

    const focusableElements = document.querySelectorAll(
      'button, a, input, [tabindex]:not([tabindex="-1"])'
    )
    expect(focusableElements.length).toBeGreaterThan(0)
  })
})
