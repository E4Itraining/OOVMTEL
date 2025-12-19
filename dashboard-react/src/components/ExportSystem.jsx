import React, { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Download,
  FileText,
  FileSpreadsheet,
  File,
  Image,
  Calendar,
  Clock,
  CheckCircle,
  Loader2,
  X,
  ChevronDown,
  Mail,
  Send
} from 'lucide-react'
import { useI18n } from '../i18n'

// Export formats
export const EXPORT_FORMATS = {
  CSV: 'csv',
  JSON: 'json',
  PDF: 'pdf',
  XLSX: 'xlsx',
  PNG: 'png'
}

// Format configurations
const FORMAT_CONFIG = {
  [EXPORT_FORMATS.CSV]: {
    icon: FileSpreadsheet,
    label: 'CSV',
    description: 'Comma-separated values',
    mime: 'text/csv',
    extension: '.csv'
  },
  [EXPORT_FORMATS.JSON]: {
    icon: FileText,
    label: 'JSON',
    description: 'JavaScript Object Notation',
    mime: 'application/json',
    extension: '.json'
  },
  [EXPORT_FORMATS.PDF]: {
    icon: File,
    label: 'PDF',
    description: 'Portable Document Format',
    mime: 'application/pdf',
    extension: '.pdf'
  },
  [EXPORT_FORMATS.XLSX]: {
    icon: FileSpreadsheet,
    label: 'Excel',
    description: 'Microsoft Excel Spreadsheet',
    mime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    extension: '.xlsx'
  },
  [EXPORT_FORMATS.PNG]: {
    icon: Image,
    label: 'PNG',
    description: 'Image snapshot',
    mime: 'image/png',
    extension: '.png'
  }
}

// Export data to CSV
function exportToCSV(data, filename) {
  if (!Array.isArray(data) || data.length === 0) {
    console.error('Invalid data for CSV export')
    return
  }

  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map(row =>
      headers.map(header => {
        const value = row[header]
        // Escape quotes and wrap in quotes if contains comma
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`
        }
        return value
      }).join(',')
    )
  ].join('\n')

  downloadFile(csvContent, filename + '.csv', 'text/csv')
}

// Export data to JSON
function exportToJSON(data, filename) {
  const jsonContent = JSON.stringify(data, null, 2)
  downloadFile(jsonContent, filename + '.json', 'application/json')
}

// Helper to trigger file download
function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// Export button component
export function ExportButton({ data, filename = 'export', formats = [EXPORT_FORMATS.CSV, EXPORT_FORMATS.JSON], className = '' }) {
  const { t } = useI18n()
  const [isOpen, setIsOpen] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [exportedFormat, setExportedFormat] = useState(null)

  const handleExport = async (format) => {
    setIsExporting(true)
    setExportedFormat(null)

    try {
      // Simulate export delay for UX
      await new Promise(resolve => setTimeout(resolve, 500))

      const timestamp = new Date().toISOString().split('T')[0]
      const exportFilename = `${filename}_${timestamp}`

      switch (format) {
        case EXPORT_FORMATS.CSV:
          exportToCSV(data, exportFilename)
          break
        case EXPORT_FORMATS.JSON:
          exportToJSON(data, exportFilename)
          break
        case EXPORT_FORMATS.PDF:
          // PDF export would require a library like jsPDF
          console.log('PDF export - implement with jsPDF')
          alert('PDF export coming soon!')
          break
        case EXPORT_FORMATS.XLSX:
          // Excel export would require a library like xlsx
          console.log('XLSX export - implement with xlsx library')
          alert('Excel export coming soon!')
          break
        case EXPORT_FORMATS.PNG:
          // Screenshot export would require html2canvas
          console.log('PNG export - implement with html2canvas')
          alert('Image export coming soon!')
          break
        default:
          console.error('Unknown export format:', format)
      }

      setExportedFormat(format)
      setTimeout(() => setExportedFormat(null), 2000)
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsExporting(false)
      setIsOpen(false)
    }
  }

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isExporting}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-industrial-card border border-industrial-border hover:border-cyan-500/50 transition-all text-sm text-gray-300 hover:text-white disabled:opacity-50"
      >
        {isExporting ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : exportedFormat ? (
          <CheckCircle className="w-4 h-4 text-green-400" />
        ) : (
          <Download className="w-4 h-4" />
        )}
        <span>{t('export.button') || 'Export'}</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute right-0 top-full mt-2 w-56 bg-industrial-dark border border-industrial-border rounded-xl shadow-xl z-50 overflow-hidden"
            >
              <div className="p-2">
                <p className="px-3 py-2 text-xs text-gray-500 uppercase tracking-wider">
                  {t('export.selectFormat') || 'Select format'}
                </p>
                {formats.map(format => {
                  const config = FORMAT_CONFIG[format]
                  const Icon = config.icon
                  return (
                    <button
                      key={format}
                      onClick={() => handleExport(format)}
                      className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-industrial-border/50 transition-colors"
                    >
                      <Icon className="w-5 h-5 text-cyan-400" />
                      <div className="text-left">
                        <p className="text-sm text-white">{config.label}</p>
                        <p className="text-xs text-gray-500">{config.description}</p>
                      </div>
                    </button>
                  )
                })}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

// Scheduled report modal
export function ScheduledReportModal({ isOpen, onClose }) {
  const { t } = useI18n()
  const [schedule, setSchedule] = useState({
    frequency: 'daily',
    time: '09:00',
    format: EXPORT_FORMATS.PDF,
    recipients: '',
    includeKPI: true,
    includeTechnical: true,
    includeAlerts: true
  })
  const [isSaving, setIsSaving] = useState(false)

  const handleSave = async () => {
    setIsSaving(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('Scheduled report saved:', schedule)
    setIsSaving(false)
    onClose()
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="w-full max-w-lg bg-industrial-dark border border-industrial-border rounded-xl shadow-2xl"
          onClick={e => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-industrial-border">
            <div className="flex items-center gap-3">
              <Calendar className="w-5 h-5 text-cyan-400" />
              <h2 className="text-lg font-semibold text-white">
                {t('reports.scheduleTitle') || 'Schedule Report'}
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-4 space-y-4">
            {/* Frequency */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                {t('reports.frequency') || 'Frequency'}
              </label>
              <div className="flex gap-2">
                {['daily', 'weekly', 'monthly'].map(freq => (
                  <button
                    key={freq}
                    onClick={() => setSchedule(s => ({ ...s, frequency: freq }))}
                    className={`flex-1 px-3 py-2 rounded-lg text-sm transition-colors ${
                      schedule.frequency === freq
                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                        : 'bg-industrial-border/50 text-gray-400 border border-transparent hover:text-white'
                    }`}
                  >
                    {t(`reports.${freq}`) || freq.charAt(0).toUpperCase() + freq.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Time */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                {t('reports.time') || 'Time'}
              </label>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-gray-500" />
                <input
                  type="time"
                  value={schedule.time}
                  onChange={e => setSchedule(s => ({ ...s, time: e.target.value }))}
                  className="flex-1 px-3 py-2 rounded-lg bg-industrial-darker border border-industrial-border focus:border-cyan-500/50 focus:outline-none text-white"
                />
              </div>
            </div>

            {/* Format */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                {t('reports.format') || 'Format'}
              </label>
              <select
                value={schedule.format}
                onChange={e => setSchedule(s => ({ ...s, format: e.target.value }))}
                className="w-full px-3 py-2 rounded-lg bg-industrial-darker border border-industrial-border focus:border-cyan-500/50 focus:outline-none text-white"
              >
                <option value={EXPORT_FORMATS.PDF}>PDF</option>
                <option value={EXPORT_FORMATS.XLSX}>Excel</option>
                <option value={EXPORT_FORMATS.CSV}>CSV</option>
              </select>
            </div>

            {/* Recipients */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                {t('reports.recipients') || 'Email Recipients'}
              </label>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-gray-500" />
                <input
                  type="text"
                  value={schedule.recipients}
                  onChange={e => setSchedule(s => ({ ...s, recipients: e.target.value }))}
                  placeholder="email1@example.com, email2@example.com"
                  className="flex-1 px-3 py-2 rounded-lg bg-industrial-darker border border-industrial-border focus:border-cyan-500/50 focus:outline-none text-white placeholder-gray-600"
                />
              </div>
            </div>

            {/* Content selection */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                {t('reports.include') || 'Include'}
              </label>
              <div className="space-y-2">
                {[
                  { key: 'includeKPI', label: t('reports.includeKPI') || 'Business KPIs' },
                  { key: 'includeTechnical', label: t('reports.includeTechnical') || 'Technical Metrics' },
                  { key: 'includeAlerts', label: t('reports.includeAlerts') || 'Active Alerts' }
                ].map(item => (
                  <label key={item.key} className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={schedule[item.key]}
                      onChange={e => setSchedule(s => ({ ...s, [item.key]: e.target.checked }))}
                      className="w-4 h-4 rounded border-industrial-border bg-industrial-darker text-cyan-500 focus:ring-cyan-500/50"
                    />
                    <span className="text-sm text-gray-300">{item.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 p-4 border-t border-industrial-border">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
            >
              {t('common.cancel') || 'Cancel'}
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white text-sm hover:from-cyan-400 hover:to-blue-400 transition-colors disabled:opacity-50"
            >
              {isSaving ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              {t('reports.schedule') || 'Schedule'}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

// Hook for export functionality
export function useExport() {
  const [isExporting, setIsExporting] = useState(false)

  const exportData = useCallback(async (data, filename, format) => {
    setIsExporting(true)
    try {
      const timestamp = new Date().toISOString().split('T')[0]
      const exportFilename = `${filename}_${timestamp}`

      switch (format) {
        case EXPORT_FORMATS.CSV:
          exportToCSV(data, exportFilename)
          break
        case EXPORT_FORMATS.JSON:
          exportToJSON(data, exportFilename)
          break
        default:
          console.error('Unsupported format:', format)
      }
    } finally {
      setIsExporting(false)
    }
  }, [])

  return { exportData, isExporting }
}

export default ExportButton
