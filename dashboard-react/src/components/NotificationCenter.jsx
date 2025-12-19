import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Bell,
  X,
  AlertTriangle,
  CheckCircle2,
  Info,
  XCircle,
  Clock,
  Trash2,
  Check,
  Filter,
  Settings
} from 'lucide-react'
import { useI18n } from '../i18n'

// Notification types configuration
const NOTIFICATION_TYPES = {
  critical: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/30' },
  warning: { icon: AlertTriangle, color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30' },
  success: { icon: CheckCircle2, color: 'text-green-400', bg: 'bg-green-500/10', border: 'border-green-500/30' },
  info: { icon: Info, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/30' }
}

// Demo notifications
const DEMO_NOTIFICATIONS = [
  {
    id: 1,
    type: 'warning',
    title: 'Kafka Consumer Lag',
    message: 'Consumer lag increasing on topic production-events',
    timestamp: new Date(Date.now() - 2 * 60 * 1000),
    read: false,
    service: 'Kafka'
  },
  {
    id: 2,
    type: 'info',
    title: 'Maintenance programmée',
    message: 'Maintenance VictoriaMetrics prévue dans 2 heures',
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    read: false,
    service: 'System'
  },
  {
    id: 3,
    type: 'success',
    title: 'Déploiement réussi',
    message: 'Version 2.1.0 déployée avec succès',
    timestamp: new Date(Date.now() - 45 * 60 * 1000),
    read: true,
    service: 'CI/CD'
  },
  {
    id: 4,
    type: 'critical',
    title: 'SLO à risque',
    message: 'SLO Latency API à 98.5%, seuil: 99%',
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    read: false,
    service: 'Observability'
  }
]

function NotificationItem({ notification, onMarkRead, onDismiss }) {
  const { t, formatTime } = useI18n()
  const config = NOTIFICATION_TYPES[notification.type] || NOTIFICATION_TYPES.info
  const Icon = config.icon

  const getRelativeTime = (date) => {
    const now = new Date()
    const diff = Math.floor((now - date) / 1000)

    if (diff < 60) return 'À l\'instant'
    if (diff < 3600) return `Il y a ${Math.floor(diff / 60)} min`
    if (diff < 86400) return `Il y a ${Math.floor(diff / 3600)} h`
    return formatTime(date)
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className={`p-4 border-b border-industrial-border/50 last:border-0 ${!notification.read ? 'bg-industrial-accent/5' : ''}`}
    >
      <div className="flex gap-3">
        <div className={`w-10 h-10 rounded-lg ${config.bg} flex items-center justify-center flex-shrink-0`}>
          <Icon className={`w-5 h-5 ${config.color}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className={`font-medium ${!notification.read ? 'text-white' : 'text-gray-300'}`}>
                {notification.title}
              </p>
              <p className="text-sm text-gray-400 mt-0.5">{notification.message}</p>
            </div>
            {!notification.read && (
              <div className="w-2 h-2 rounded-full bg-industrial-accent flex-shrink-0 mt-2" />
            )}
          </div>
          <div className="flex items-center justify-between mt-2">
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <span className="px-2 py-0.5 bg-industrial-card rounded">{notification.service}</span>
              <Clock className="w-3 h-3" />
              <span>{getRelativeTime(notification.timestamp)}</span>
            </div>
            <div className="flex items-center gap-1">
              {!notification.read && (
                <button
                  onClick={() => onMarkRead(notification.id)}
                  className="p-1.5 hover:bg-white/10 rounded text-gray-400 hover:text-white transition-colors"
                  title="Marquer comme lu"
                >
                  <Check className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={() => onDismiss(notification.id)}
                className="p-1.5 hover:bg-white/10 rounded text-gray-400 hover:text-red-400 transition-colors"
                title="Supprimer"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

function NotificationCenter({ isOpen, onClose, anchorRef }) {
  const { t } = useI18n()
  const [notifications, setNotifications] = useState(DEMO_NOTIFICATIONS)
  const [filter, setFilter] = useState('all') // all, unread, critical

  const unreadCount = notifications.filter(n => !n.read).length
  const criticalCount = notifications.filter(n => n.type === 'critical' && !n.read).length

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'unread') return !n.read
    if (filter === 'critical') return n.type === 'critical'
    return true
  })

  const handleMarkRead = (id) => {
    setNotifications(prev => prev.map(n =>
      n.id === id ? { ...n, read: true } : n
    ))
  }

  const handleDismiss = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const handleMarkAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }

  const handleClearAll = () => {
    setNotifications([])
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -10, scale: 0.95 }}
        className="absolute right-0 top-full mt-2 w-96 bg-industrial-dark border border-industrial-border rounded-xl shadow-2xl z-50 overflow-hidden"
      >
        {/* Header */}
        <div className="px-4 py-3 border-b border-industrial-border bg-industrial-darker/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-industrial-accent" />
              <h3 className="font-semibold text-white">Notifications</h3>
              {unreadCount > 0 && (
                <span className="px-2 py-0.5 bg-industrial-accent/20 text-industrial-accent text-xs rounded-full">
                  {unreadCount}
                </span>
              )}
            </div>
            <button
              onClick={onClose}
              className="p-1 hover:bg-white/10 rounded transition-colors"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2 mt-3">
            {[
              { key: 'all', label: 'Tout' },
              { key: 'unread', label: `Non lu (${unreadCount})` },
              { key: 'critical', label: `Critique (${criticalCount})` }
            ].map(f => (
              <button
                key={f.key}
                onClick={() => setFilter(f.key)}
                className={`px-3 py-1.5 text-xs rounded-lg transition-colors
                  ${filter === f.key
                    ? 'bg-industrial-accent/20 text-industrial-accent'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Notifications List */}
        <div className="max-h-80 overflow-y-auto">
          {filteredNotifications.length > 0 ? (
            <AnimatePresence>
              {filteredNotifications.map(notification => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onMarkRead={handleMarkRead}
                  onDismiss={handleDismiss}
                />
              ))}
            </AnimatePresence>
          ) : (
            <div className="px-4 py-8 text-center">
              <CheckCircle2 className="w-10 h-10 text-green-400 mx-auto mb-2" />
              <p className="text-gray-400">Aucune notification</p>
            </div>
          )}
        </div>

        {/* Footer */}
        {notifications.length > 0 && (
          <div className="px-4 py-3 border-t border-industrial-border bg-industrial-darker/50 flex items-center justify-between">
            <button
              onClick={handleMarkAllRead}
              className="text-xs text-gray-400 hover:text-white transition-colors"
            >
              Tout marquer comme lu
            </button>
            <button
              onClick={handleClearAll}
              className="text-xs text-red-400 hover:text-red-300 transition-colors"
            >
              Tout effacer
            </button>
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  )
}

export default NotificationCenter
