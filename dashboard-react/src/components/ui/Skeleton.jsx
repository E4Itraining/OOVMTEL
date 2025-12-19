import React from 'react'
import { motion } from 'framer-motion'

// Base skeleton component with shimmer animation
export function Skeleton({ className = '', variant = 'rectangular', animation = 'pulse' }) {
  const baseClasses = 'bg-industrial-border/50'

  const variantClasses = {
    rectangular: 'rounded-lg',
    circular: 'rounded-full',
    text: 'rounded h-4',
    card: 'rounded-xl'
  }

  const animationClasses = {
    pulse: 'animate-pulse',
    shimmer: 'relative overflow-hidden',
    wave: 'animate-pulse'
  }

  return (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${animationClasses[animation]} ${className}`}
    >
      {animation === 'shimmer' && (
        <motion.div
          className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/10 to-transparent"
          animate={{ translateX: ['0%', '200%'] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
        />
      )}
    </div>
  )
}

// Card skeleton
export function CardSkeleton({ hasHeader = true, rows = 3 }) {
  return (
    <div className="bg-industrial-card border border-industrial-border rounded-xl p-4 space-y-4">
      {hasHeader && (
        <div className="flex items-center gap-3">
          <Skeleton variant="circular" className="w-10 h-10" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-1/3" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      )}
      <div className="space-y-3">
        {[...Array(rows)].map((_, i) => (
          <Skeleton key={i} className="h-4" style={{ width: `${100 - i * 15}%` }} />
        ))}
      </div>
    </div>
  )
}

// Metric card skeleton
export function MetricCardSkeleton() {
  return (
    <div className="bg-industrial-card border border-industrial-border rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <Skeleton className="h-4 w-24" />
        <Skeleton variant="circular" className="w-8 h-8" />
      </div>
      <Skeleton className="h-8 w-20 mb-2" />
      <Skeleton className="h-3 w-16" />
    </div>
  )
}

// Chart skeleton
export function ChartSkeleton({ height = 200 }) {
  return (
    <div className="bg-industrial-card border border-industrial-border rounded-xl p-4">
      <div className="flex items-center justify-between mb-4">
        <Skeleton className="h-5 w-32" />
        <div className="flex gap-2">
          <Skeleton className="h-6 w-16" />
          <Skeleton className="h-6 w-16" />
        </div>
      </div>
      <div className="flex items-end gap-2" style={{ height }}>
        {[...Array(12)].map((_, i) => (
          <Skeleton
            key={i}
            className="flex-1"
            style={{ height: `${Math.random() * 60 + 20}%` }}
          />
        ))}
      </div>
    </div>
  )
}

// Gauge skeleton
export function GaugeSkeleton({ size = 'md' }) {
  const sizes = {
    sm: 'w-24 h-24',
    md: 'w-32 h-32',
    lg: 'w-40 h-40'
  }

  return (
    <div className="flex flex-col items-center gap-3">
      <Skeleton variant="circular" className={sizes[size]} />
      <Skeleton className="h-4 w-16" />
      <Skeleton className="h-3 w-12" />
    </div>
  )
}

// Table skeleton
export function TableSkeleton({ rows = 5, columns = 4 }) {
  return (
    <div className="bg-industrial-card border border-industrial-border rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex gap-4 p-4 border-b border-industrial-border bg-industrial-darker/50">
        {[...Array(columns)].map((_, i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>
      {/* Rows */}
      {[...Array(rows)].map((_, rowIndex) => (
        <div key={rowIndex} className="flex gap-4 p-4 border-b border-industrial-border/50 last:border-0">
          {[...Array(columns)].map((_, colIndex) => (
            <Skeleton
              key={colIndex}
              className="h-4 flex-1"
              style={{ opacity: 1 - (rowIndex * 0.1) }}
            />
          ))}
        </div>
      ))}
    </div>
  )
}

// List skeleton
export function ListSkeleton({ items = 5, showAvatar = true }) {
  return (
    <div className="space-y-3">
      {[...Array(items)].map((_, i) => (
        <div key={i} className="flex items-center gap-3 p-3 bg-industrial-card/50 rounded-lg">
          {showAvatar && <Skeleton variant="circular" className="w-10 h-10" />}
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
          <Skeleton className="h-6 w-16 rounded-full" />
        </div>
      ))}
    </div>
  )
}

// Dashboard skeleton - full page
export function DashboardSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Header metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <MetricCardSkeleton key={i} />
        ))}
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ChartSkeleton height={300} />
        </div>
        <div>
          <CardSkeleton rows={5} />
        </div>
      </div>

      {/* Secondary content */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <TableSkeleton rows={4} columns={3} />
        <ListSkeleton items={4} />
      </div>
    </div>
  )
}

// KPI View skeleton
export function KPIViewSkeleton() {
  return (
    <div className="space-y-6">
      {/* OEE Gauges */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-industrial-card border border-industrial-border rounded-xl p-6 flex flex-col items-center">
            <GaugeSkeleton size="lg" />
          </div>
        ))}
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <MetricCardSkeleton key={i} />
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartSkeleton height={250} />
        <ChartSkeleton height={250} />
      </div>
    </div>
  )
}

// Technical View skeleton
export function TechnicalViewSkeleton() {
  return (
    <div className="space-y-6">
      {/* Service status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-industrial-card border border-industrial-border rounded-xl p-4">
            <div className="flex items-center gap-3 mb-4">
              <Skeleton variant="circular" className="w-12 h-12" />
              <div className="flex-1">
                <Skeleton className="h-5 w-32 mb-2" />
                <Skeleton className="h-3 w-20" />
              </div>
              <Skeleton variant="circular" className="w-3 h-3" />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <Skeleton className="h-3 w-16" />
                <Skeleton className="h-3 w-12" />
              </div>
              <Skeleton className="h-2 w-full rounded-full" />
            </div>
          </div>
        ))}
      </div>

      {/* Infrastructure metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {[...Array(3)].map((_, i) => (
          <MetricCardSkeleton key={i} />
        ))}
      </div>

      {/* Charts */}
      <ChartSkeleton height={300} />
    </div>
  )
}

export default Skeleton
