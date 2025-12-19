import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Bell,
  X,
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle,
  Clock,
  Trash2,
  Check,
  Settings,
  Filter,
  Volume2,
  VolumeX,
  ChevronRight
} from 'lucide-react'
import { useI18n } from '../i18n'

// Notification types
export const NOTIFICATION_TYPES = {
  CRITICAL: 'critical',
  WARNING: 'warning',
  INFO: 'info',
  SUCCESS: 'success'
}

// Demo notifications
const DEMO_NOTIFICATIONS = [
  {
    id: '1',
    type: NOTIFICATION_TYPES.CRITICAL,
    title: 'Critical: Production Line 2 Down',
    message: 'Equipment failure detected. Immediate attention required.',
    timestamp: new Date(Date.now() - 5 * 60000),
    read: false,
    source: 'Equipment Monitor',
    actionUrl: '/business-kpi#equipment-status'
  },
  {
    id: '2',
    type: NOTIFICATION_TYPES.WARNING,
    title: 'Kafka Consumer Lag Increasing',
    message: 'Consumer lag has exceeded 1000 messages on topic production-metrics.',
    timestamp: new Date(Date.now() - 15 * 60000),
    read: false,
    source: 'Kafka Monitor',
    actionUrl: '/kafka'
  },
  {
    id: '3',
    type: NOTIFICATION_TYPES.INFO,
    title: 'Scheduled Maintenance',
    message: 'System maintenance window starting in 2 hours.',
    timestamp: new Date(Date.now() - 30 * 60000),
    read: true,
    source: 'System',
    actionUrl: null
  },
  {
    id: '4',
    type: NOTIFICATION_TYPES.SUCCESS,
    title: 'Backup Completed',
    message: 'Daily backup completed successfully. 2.3 GB archived.',
    timestamp: new Date(Date.now() - 60 * 60000),
    read: true,
    source: 'Backup Service',
    actionUrl: null
  },
  {
    id: '5',
    type: NOTIFICATION_TYPES.WARNING,
    title: 'High Memory Usage',
    message: 'VictoriaMetrics memory usage at 85%.',
    timestamp: new Date(Date.now() - 90 * 60000),
    read: true,
    source: 'Infrastructure',
    actionUrl: '/technical'
  }
]

// Type config
const TYPE_CONFIG = {
  [NOTIFICATION_TYPES.CRITICAL]: {
    icon: AlertCircle,
    color: 'text-red-400',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30'
  },
  [NOTIFICATION_TYPES.WARNING]: {
    icon: AlertTriangle,
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/30'
  },
  [NOTIFICATION_TYPES.INFO]: {
    icon: Info,
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30'
  },
  [NOTIFICATION_TYPES.SUCCESS]: {
    icon: CheckCircle,
    color: 'text-green-400',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30'
  }
}

function NotificationItem({ notification, onMarkRead, onDelete, onAction }) {
  const { t, formatTime } = useI18n()
  const config = TYPE_CONFIG[notification.type]
  const Icon = config.icon

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className={`p-4 border-b border-industrial-border/50 last:border-0 ${
        !notification.read ? 'bg-industrial-accent/5' : ''
      }`}
    >
      <div className="flex gap-3">
        <div className={`flex-shrink-0 w-10 h-10 rounded-lg ${config.bgColor} flex items-center justify-center`}>
          <Icon className={`w-5 h-5 ${config.color}`} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className={`font-medium text-sm ${!notification.read ? 'text-white' : 'text-gray-300'}`}>
              {notification.title}
            </h4>
            <span className="text-xs text-gray-500 flex-shrink-0">
              {formatTime(notification.timestamp)}
            </span>
          </div>

          <p className="text-sm text-gray-400 mt-1 line-clamp-2">
            {notification.message}
          </p>

          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-gray-500">
              {notification.source}
            </span>

            <div className="flex items-center gap-2">
              {!notification.read && (
                <button
                  onClick={() => onMarkRead(notification.id)}
                  className="p-1 text-gray-500 hover:text-cyan-400 transition-colors"
                  title={t('notifications.markRead') || 'Mark as read'}
                >
                  <Check className="w-4 h-4" />
                </button>
              )}

              {notification.actionUrl && (
                <button
                  onClick={() => onAction(notification.actionUrl)}
                  className="p-1 text-gray-500 hover:text-cyan-400 transition-colors"
                  title={t('notifications.viewDetails') || 'View details'}
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              )}

              <button
                onClick={() => onDelete(notification.id)}
                className="p-1 text-gray-500 hover:text-red-400 transition-colors"
                title={t('notifications.delete') || 'Delete'}
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

function NotificationCenter({ isOpen, onClose, onNavigate }) {
  const { t } = useI18n()
  const [notifications, setNotifications] = useState(DEMO_NOTIFICATIONS)
  const [filter, setFilter] = useState('all')
  const [soundEnabled, setSoundEnabled] = useState(true)

  // Filter notifications
  const filteredNotifications = notifications.filter(n => {
    if (filter === 'all') return true
    if (filter === 'unread') return !n.read
    return n.type === filter
  })

  const unreadCount = notifications.filter(n => !n.read).length

  const markAsRead = useCallback((id) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    )
  }, [])

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }, [])

  const deleteNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }, [])

  const clearAll = useCallback(() => {
    setNotifications([])
  }, [])

  const handleAction = useCallback((url) => {
    if (url && onNavigate) {
      onNavigate(url)
      onClose()
    }
  }, [onNavigate, onClose])

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, x: 20, scale: 0.95 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          exit={{ opacity: 0, x: 20, scale: 0.95 }}
          className="absolute right-4 top-20 w-96 max-h-[70vh] bg-industrial-dark border border-industrial-border rounded-xl shadow-2xl overflow-hidden flex flex-col"
          onClick={e => e.stopPropagation()}
        >
          {/* Header */}
          <div className="p-4 border-b border-industrial-border">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Bell className="w-5 h-5 text-cyan-400" />
                <h3 className="font-semibold text-white">
                  {t('notifications.title') || 'Notifications'}
                </h3>
                {unreadCount > 0 && (
                  <span className="px-2 py-0.5 text-xs bg-cyan-500/20 text-cyan-400 rounded-full">
                    {unreadCount}
                  </span>
                )}
              </div>
              <button
                onClick={onClose}
                className="p-1 text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-2">
              <div className="flex-1 flex gap-1 overflow-x-auto">
                {['all', 'unread', NOTIFICATION_TYPES.CRITICAL, NOTIFICATION_TYPES.WARNING].map((f) => (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    className={`px-3 py-1 text-xs rounded-full whitespace-nowrap transition-colors ${
                      filter === f
                        ? 'bg-cyan-500/20 text-cyan-400'
                        : 'bg-industrial-border/50 text-gray-400 hover:text-white'
                    }`}
                  >
                    {t(`notifications.filter.${f}`) || f.charAt(0).toUpperCase() + f.slice(1)}
                  </button>
                ))}
              </div>

              <button
                onClick={() => setSoundEnabled(!soundEnabled)}
                className={`p-1.5 rounded ${soundEnabled ? 'text-cyan-400' : 'text-gray-500'}`}
                title={soundEnabled ? 'Mute' : 'Unmute'}
              >
                {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Notification List */}
          <div className="flex-1 overflow-y-auto">
            {filteredNotifications.length === 0 ? (
              <div className="p-8 text-center">
                <Bell className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-500">
                  {t('notifications.empty') || 'No notifications'}
                </p>
              </div>
            ) : (
              <AnimatePresence>
                {filteredNotifications.map(notification => (
                  <NotificationItem
                    key={notification.id}
                    notification={notification}
                    onMarkRead={markAsRead}
                    onDelete={deleteNotification}
                    onAction={handleAction}
                  />
                ))}
              </AnimatePresence>
            )}
          </div>

          {/* Footer Actions */}
          {notifications.length > 0 && (
            <div className="p-3 border-t border-industrial-border flex items-center justify-between">
              <button
                onClick={markAllAsRead}
                className="text-xs text-gray-400 hover:text-cyan-400 transition-colors"
                disabled={unreadCount === 0}
              >
                {t('notifications.markAllRead') || 'Mark all as read'}
              </button>
              <button
                onClick={clearAll}
                className="text-xs text-gray-400 hover:text-red-400 transition-colors"
              >
                {t('notifications.clearAll') || 'Clear all'}
              </button>
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

// Hook to manage notifications
export function useNotifications() {
  const [notifications, setNotifications] = useState(DEMO_NOTIFICATIONS)

  const addNotification = useCallback((notification) => {
    const newNotification = {
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false,
      ...notification
    }
    setNotifications(prev => [newNotification, ...prev])

    // Play sound if browser supports it
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.ico'
      })
    }
  }, [])

  const unreadCount = notifications.filter(n => !n.read).length

  return {
    notifications,
    unreadCount,
    addNotification
  }
}

export default NotificationCenter
