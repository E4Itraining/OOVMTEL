import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    // Test environment
    environment: 'jsdom',

    // Global test setup
    globals: true,
    setupFiles: ['./src/test/setup.js'],

    // Include patterns
    include: ['src/**/*.{test,spec}.{js,jsx,ts,tsx}'],
    exclude: ['node_modules', 'dist'],

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.{js,ts}',
        '**/main.jsx',
      ],
      thresholds: {
        statements: 70,
        branches: 70,
        functions: 70,
        lines: 70,
      },
    },

    // Reporter
    reporters: ['verbose', 'html'],

    // Watch mode
    watch: false,

    // Timeout
    testTimeout: 10000,

    // CSS handling
    css: {
      modules: {
        classNameStrategy: 'non-scoped',
      },
    },

    // Mock server port
    server: {
      deps: {
        inline: ['framer-motion'],
      },
    },
  },
})
