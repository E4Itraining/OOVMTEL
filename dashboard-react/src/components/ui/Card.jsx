import React from 'react'
import { motion } from 'framer-motion'
import { ChevronRight, ExternalLink } from 'lucide-react'

export function Card({ children, className = '', onClick, hoverable = false, ...props }) {
  const Component = onClick ? motion.button : motion.div

  return (
    <Component
      className={`card ${hoverable ? 'hover:scale-[1.02] cursor-pointer' : ''} ${className}`}
      onClick={onClick}
      whileHover={hoverable ? { scale: 1.02 } : undefined}
      whileTap={hoverable ? { scale: 0.98 } : undefined}
      {...props}
    >
      {children}
    </Component>
  )
}

export function CardHeader({ title, subtitle, icon: Icon, action, children }) {
  return (
    <div className="card-header">
      <div className="flex items-center gap-3">
        {Icon && (
          <div className="w-8 h-8 rounded-lg bg-industrial-accent/20 flex items-center justify-center">
            <Icon className="w-4 h-4 text-industrial-accent" />
          </div>
        )}
        <div>
          <h3 className="font-semibold text-white">{title}</h3>
          {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
        </div>
      </div>
      {action && <div>{action}</div>}
      {children}
    </div>
  )
}

export function CardBody({ children, className = '' }) {
  return <div className={`card-body ${className}`}>{children}</div>
}

export function MetricCard({ label, value, unit, trend, trendValue, icon: Icon, color = 'cyan', onClick }) {
  const colorClasses = {
    cyan: 'from-cyan-500 to-cyan-600',
    purple: 'from-purple-500 to-purple-600',
    green: 'from-green-500 to-green-600',
    yellow: 'from-yellow-500 to-yellow-600',
    red: 'from-red-500 to-red-600',
  }

  return (
    <Card
      className="p-4"
      onClick={onClick}
      hoverable={!!onClick}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="stat-label">{label}</p>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="stat-value">{value}</span>
            {unit && <span className="text-gray-400 text-sm">{unit}</span>}
          </div>
          {trend && (
            <div className={`flex items-center gap-1 mt-2 text-xs ${
              trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400' : 'text-gray-400'
            }`}>
              <span>{trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}</span>
              <span>{trendValue}</span>
            </div>
          )}
        </div>
        {Icon && (
          <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center shadow-lg`}>
            <Icon className="w-5 h-5 text-white" />
          </div>
        )}
      </div>
    </Card>
  )
}

export function ServiceCard({ name, status, icon: Icon, metrics, onClick }) {
  const statusColors = {
    healthy: 'bg-green-500',
    degraded: 'bg-yellow-500',
    down: 'bg-red-500',
    unknown: 'bg-gray-500',
  }

  return (
    <Card
      className="p-4 group"
      onClick={onClick}
      hoverable
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {Icon && (
            <div className="w-10 h-10 rounded-xl bg-industrial-border/50 flex items-center justify-center group-hover:bg-industrial-accent/20 transition-colors">
              <Icon className="w-5 h-5 text-gray-400 group-hover:text-industrial-accent transition-colors" />
            </div>
          )}
          <div>
            <h4 className="font-medium text-white">{name}</h4>
            <div className="flex items-center gap-2 mt-0.5">
              <span className={`w-2 h-2 rounded-full ${statusColors[status] || statusColors.unknown}`} />
              <span className="text-xs text-gray-400 capitalize">{status}</span>
            </div>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-600 group-hover:text-gray-400 transition-colors" />
      </div>
      {metrics && (
        <div className="grid grid-cols-3 gap-3 mt-4 pt-3 border-t border-industrial-border/50">
          {metrics.map((m, i) => (
            <div key={i} className="text-center">
              <p className="text-lg font-semibold text-white">{m.value}</p>
              <p className="text-[10px] text-gray-500 uppercase">{m.label}</p>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}

export function LinkCard({ title, description, href, icon: Icon }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="card p-4 flex items-center gap-4 hover:border-industrial-accent/50 group"
    >
      {Icon && (
        <div className="w-12 h-12 rounded-xl bg-industrial-border/50 flex items-center justify-center group-hover:bg-industrial-accent/20 transition-colors">
          <Icon className="w-6 h-6 text-gray-400 group-hover:text-industrial-accent transition-colors" />
        </div>
      )}
      <div className="flex-1">
        <h4 className="font-medium text-white">{title}</h4>
        <p className="text-sm text-gray-400">{description}</p>
      </div>
      <ExternalLink className="w-5 h-5 text-gray-600 group-hover:text-industrial-accent transition-colors" />
    </a>
  )
}
