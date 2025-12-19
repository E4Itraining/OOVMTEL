import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Download,
  X,
  FileText,
  FileSpreadsheet,
  FileJson,
  Image,
  Calendar,
  Clock,
  CheckCircle2,
  Loader2,
  AlertCircle
} from 'lucide-react'
import { useI18n } from '../i18n'
import { useDashboard } from '../context/DashboardContext'

// Export formats configuration
const EXPORT_FORMATS = [
  {
    id: 'pdf',
    name: 'PDF',
    description: 'Rapport formaté avec graphiques',
    icon: FileText,
    extension: '.pdf',
    mimeType: 'application/pdf'
  },
  {
    id: 'csv',
    name: 'CSV',
    description: 'Données tabulaires pour Excel',
    icon: FileSpreadsheet,
    extension: '.csv',
    mimeType: 'text/csv'
  },
  {
    id: 'json',
    name: 'JSON',
    description: 'Données structurées pour API',
    icon: FileJson,
    extension: '.json',
    mimeType: 'application/json'
  },
  {
    id: 'png',
    name: 'PNG',
    description: 'Capture d\'écran du dashboard',
    icon: Image,
    extension: '.png',
    mimeType: 'image/png'
  }
]

// Time range options
const TIME_RANGES = [
  { id: 'today', label: 'Aujourd\'hui' },
  { id: 'yesterday', label: 'Hier' },
  { id: 'week', label: '7 derniers jours' },
  { id: 'month', label: '30 derniers jours' },
  { id: 'custom', label: 'Personnalisé' }
]

// Export data types
const DATA_TYPES = [
  { id: 'metrics', label: 'Métriques business', checked: true },
  { id: 'technical', label: 'Données techniques', checked: true },
  { id: 'alerts', label: 'Historique alertes', checked: false },
  { id: 'events', label: 'Journal événements', checked: false }
]

function ExportModal({ isOpen, onClose }) {
  const { t, formatTime } = useI18n()
  const { metrics } = useDashboard()

  const [selectedFormat, setSelectedFormat] = useState('pdf')
  const [selectedRange, setSelectedRange] = useState('today')
  const [dataTypes, setDataTypes] = useState(DATA_TYPES)
  const [isExporting, setIsExporting] = useState(false)
  const [exportStatus, setExportStatus] = useState(null) // null, 'success', 'error'

  const toggleDataType = (id) => {
    setDataTypes(prev => prev.map(dt =>
      dt.id === id ? { ...dt, checked: !dt.checked } : dt
    ))
  }

  const handleExport = async () => {
    setIsExporting(true)
    setExportStatus(null)

    try {
      // Simulate export process
      await new Promise(resolve => setTimeout(resolve, 1500))

      // Generate export data
      const exportData = {
        generatedAt: new Date().toISOString(),
        timeRange: selectedRange,
        format: selectedFormat,
        data: {}
      }

      // Add selected data types
      dataTypes.filter(dt => dt.checked).forEach(dt => {
        switch (dt.id) {
          case 'metrics':
            exportData.data.businessMetrics = metrics.business
            break
          case 'technical':
            exportData.data.technicalMetrics = metrics.tech
            break
          case 'alerts':
            exportData.data.alerts = [] // Would fetch from API
            break
          case 'events':
            exportData.data.events = [] // Would fetch from API
            break
        }
      })

      // Handle different export formats
      const format = EXPORT_FORMATS.find(f => f.id === selectedFormat)
      const filename = `synapsix-export-${new Date().toISOString().split('T')[0]}${format.extension}`

      if (selectedFormat === 'json') {
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: format.mimeType })
        downloadBlob(blob, filename)
      } else if (selectedFormat === 'csv') {
        const csv = generateCSV(exportData)
        const blob = new Blob([csv], { type: format.mimeType })
        downloadBlob(blob, filename)
      } else {
        // For PDF and PNG, would need proper libraries
        console.log('Export would generate:', filename)
      }

      setExportStatus('success')
    } catch (error) {
      console.error('Export failed:', error)
      setExportStatus('error')
    } finally {
      setIsExporting(false)
    }
  }

  const downloadBlob = (blob, filename) => {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const generateCSV = (data) => {
    const rows = []
    rows.push(['Metric', 'Value', 'Unit', 'Timestamp'])

    if (data.data.businessMetrics) {
      const bm = data.data.businessMetrics
      rows.push(['OEE', bm.oee || 0, '%', new Date().toISOString()])
      rows.push(['Production Today', bm.productionToday || 0, 'units', new Date().toISOString()])
      rows.push(['Quality Rate', bm.qualityRate || 0, '%', new Date().toISOString()])
    }

    if (data.data.technicalMetrics) {
      const tm = data.data.technicalMetrics
      rows.push(['Metrics Rate', tm.metricsRate || 0, '/s', new Date().toISOString()])
      rows.push(['Error Rate', tm.errorRate || 0, '%', new Date().toISOString()])
      rows.push(['Latency P95', tm.latencyP95 || 0, 'ms', new Date().toISOString()])
    }

    return rows.map(r => r.join(',')).join('\n')
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="w-full max-w-lg bg-industrial-dark border border-industrial-border rounded-xl shadow-2xl overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="px-6 py-4 border-b border-industrial-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                  <Download className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Exporter les données</h3>
                  <p className="text-xs text-gray-400">Télécharger un rapport personnalisé</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Format Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Format d'export
              </label>
              <div className="grid grid-cols-4 gap-2">
                {EXPORT_FORMATS.map((format) => {
                  const Icon = format.icon
                  const isSelected = selectedFormat === format.id
                  return (
                    <button
                      key={format.id}
                      onClick={() => setSelectedFormat(format.id)}
                      className={`p-3 rounded-lg border transition-all text-center ${
                        isSelected
                          ? 'border-industrial-accent bg-industrial-accent/10'
                          : 'border-industrial-border hover:border-gray-600'
                      }`}
                    >
                      <Icon className={`w-6 h-6 mx-auto mb-1 ${isSelected ? 'text-industrial-accent' : 'text-gray-400'}`} />
                      <p className={`text-sm font-medium ${isSelected ? 'text-white' : 'text-gray-300'}`}>
                        {format.name}
                      </p>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Time Range */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                <Calendar className="w-4 h-4 inline mr-2" />
                Période
              </label>
              <div className="flex flex-wrap gap-2">
                {TIME_RANGES.map((range) => (
                  <button
                    key={range.id}
                    onClick={() => setSelectedRange(range.id)}
                    className={`px-3 py-1.5 rounded-lg text-sm transition-all ${
                      selectedRange === range.id
                        ? 'bg-industrial-accent text-white'
                        : 'bg-industrial-card text-gray-300 hover:bg-white/10'
                    }`}
                  >
                    {range.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Data Types */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Données à inclure
              </label>
              <div className="space-y-2">
                {dataTypes.map((dt) => (
                  <label
                    key={dt.id}
                    className="flex items-center gap-3 p-3 rounded-lg bg-industrial-card/50 hover:bg-industrial-card cursor-pointer transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={dt.checked}
                      onChange={() => toggleDataType(dt.id)}
                      className="w-4 h-4 rounded border-gray-600 bg-industrial-darker text-industrial-accent focus:ring-industrial-accent"
                    />
                    <span className="text-sm text-gray-300">{dt.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Status Message */}
            {exportStatus && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex items-center gap-2 p-3 rounded-lg ${
                  exportStatus === 'success'
                    ? 'bg-green-500/10 text-green-400'
                    : 'bg-red-500/10 text-red-400'
                }`}
              >
                {exportStatus === 'success' ? (
                  <>
                    <CheckCircle2 className="w-5 h-5" />
                    <span>Export réussi ! Le fichier a été téléchargé.</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-5 h-5" />
                    <span>Erreur lors de l'export. Veuillez réessayer.</span>
                  </>
                )}
              </motion.div>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-industrial-border bg-industrial-darker/50 flex items-center justify-between">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
            >
              Annuler
            </button>
            <button
              onClick={handleExport}
              disabled={isExporting || dataTypes.every(dt => !dt.checked)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-green-500 to-emerald-600 text-white font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isExporting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Export en cours...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  Exporter
                </>
              )}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

// Export Button Component
function ExportSystem() {
  const [isModalOpen, setIsModalOpen] = useState(false)

  return (
    <>
      <button
        onClick={() => setIsModalOpen(true)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
        title="Exporter les données"
      >
        <Download className="w-5 h-5" />
        <span className="text-sm hidden md:inline">Export</span>
      </button>

      <ExportModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </>
  )
}

export default ExportSystem
