import React from 'react'
import { motion } from 'framer-motion'
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Loader2
} from 'lucide-react'

export function StatusBadge({ status, label, size = 'md' }) {
  const statusConfig = {
    healthy: { color: 'green', icon: CheckCircle, label: 'Healthy' },
    ok: { color: 'green', icon: CheckCircle, label: 'OK' },
    running: { color: 'green', icon: CheckCircle, label: 'Running' },
    active: { color: 'green', icon: CheckCircle, label: 'Active' },
    degraded: { color: 'yellow', icon: AlertTriangle, label: 'Degraded' },
    warning: { color: 'yellow', icon: AlertTriangle, label: 'Warning' },
    pending: { color: 'yellow', icon: Loader2, label: 'Pending' },
    down: { color: 'red', icon: XCircle, label: 'Down' },
    error: { color: 'red', icon: XCircle, label: 'Error' },
    critical: { color: 'red', icon: XCircle, label: 'Critical' },
    unknown: { color: 'gray', icon: HelpCircle, label: 'Unknown' },
  }

  const config = statusConfig[status?.toLowerCase()] || statusConfig.unknown
  const Icon = config.icon
  const displayLabel = label || config.label

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-2.5 py-1 text-sm gap-1.5',
    lg: 'px-3 py-1.5 text-base gap-2'
  }

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  }

  return (
    <span className={`badge badge-${config.color} inline-flex items-center ${sizeClasses[size]}`}>
      <Icon className={`${iconSizes[size]} ${status === 'pending' ? 'animate-spin' : ''}`} />
      <span>{displayLabel}</span>
    </span>
  )
}

export function StatusDot({ status, pulse = true, size = 'md' }) {
  const statusColors = {
    healthy: 'bg-green-500',
    ok: 'bg-green-500',
    running: 'bg-green-500',
    active: 'bg-green-500',
    degraded: 'bg-yellow-500',
    warning: 'bg-yellow-500',
    down: 'bg-red-500',
    error: 'bg-red-500',
    critical: 'bg-red-500',
    unknown: 'bg-gray-500',
  }

  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  }

  const color = statusColors[status?.toLowerCase()] || statusColors.unknown

  return (
    <span className="relative inline-flex">
      <span className={`${sizeClasses[size]} rounded-full ${color}`} />
      {pulse && status !== 'unknown' && (
        <span className={`absolute inset-0 ${sizeClasses[size]} rounded-full ${color} animate-ping opacity-75`} />
      )}
    </span>
  )
}

export function HealthIndicator({ services }) {
  const total = services.length
  const healthy = services.filter(s => ['healthy', 'ok', 'running', 'active'].includes(s.status?.toLowerCase())).length
  const degraded = services.filter(s => ['degraded', 'warning'].includes(s.status?.toLowerCase())).length
  const down = services.filter(s => ['down', 'error', 'critical'].includes(s.status?.toLowerCase())).length

  const healthPercent = total > 0 ? (healthy / total) * 100 : 0

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-400">System Health</span>
        <span className={`text-lg font-semibold ${
          healthPercent >= 80 ? 'text-green-400' :
          healthPercent >= 50 ? 'text-yellow-400' : 'text-red-400'
        }`}>
          {Math.round(healthPercent)}%
        </span>
      </div>
      <div className="h-2 bg-industrial-border rounded-full overflow-hidden flex">
        {healthy > 0 && (
          <motion.div
            className="h-full bg-green-500"
            initial={{ width: 0 }}
            animate={{ width: `${(healthy / total) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        )}
        {degraded > 0 && (
          <motion.div
            className="h-full bg-yellow-500"
            initial={{ width: 0 }}
            animate={{ width: `${(degraded / total) * 100}%` }}
            transition={{ duration: 0.5, delay: 0.1 }}
          />
        )}
        {down > 0 && (
          <motion.div
            className="h-full bg-red-500"
            initial={{ width: 0 }}
            animate={{ width: `${(down / total) * 100}%` }}
            transition={{ duration: 0.5, delay: 0.2 }}
          />
        )}
      </div>
      <div className="flex justify-between text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          {healthy} Healthy
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-yellow-500" />
          {degraded} Degraded
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-red-500" />
          {down} Down
        </span>
      </div>
    </div>
  )
}

export function AlertBanner({ type = 'info', message, onDismiss }) {
  const typeConfig = {
    info: { bg: 'bg-cyan-500/10', border: 'border-cyan-500/30', text: 'text-cyan-400' },
    success: { bg: 'bg-green-500/10', border: 'border-green-500/30', text: 'text-green-400' },
    warning: { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400' },
    error: { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400' },
  }

  const config = typeConfig[type]

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={`${config.bg} ${config.border} ${config.text} border rounded-lg p-4 flex items-center justify-between`}
    >
      <span>{message}</span>
      {onDismiss && (
        <button onClick={onDismiss} className="hover:opacity-70">
          <XCircle className="w-5 h-5" />
        </button>
      )}
    </motion.div>
  )
}

export function LoadingSpinner({ size = 'md', label }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  }

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <Loader2 className={`${sizeClasses[size]} text-industrial-accent animate-spin`} />
      {label && <span className="text-sm text-gray-400">{label}</span>}
    </div>
  )
}

export function Skeleton({ className = '', ...props }) {
  return (
    <div className={`skeleton ${className}`} {...props} />
  )
}
