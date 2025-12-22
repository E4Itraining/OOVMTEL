import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  GitBranch,
  Network,
  AlertTriangle,
  Activity,
  BarChart3,
  TrendingDown,
  Shield,
  Zap,
  Clock,
  Target,
  ChevronRight,
  Filter,
  Download,
  RefreshCw,
  Maximize2,
  Server,
  Factory,
  Layers,
  Eye,
  ArrowRight,
  CheckCircle,
  XCircle,
  Brain,
  Sparkles,
  Link2,
  Radio
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Card, CardHeader, CardBody } from '../components/ui/Card'
import { ITOTImpactGraph, ITOTImpactGraphCompact } from '../components/ui/ITOTImpactGraph'
import { CascadeAnalysisView, CascadeAnalysisCompact } from '../components/ui/CascadeAnalysis'
import { useI18n } from '../i18n'
import { useDashboard } from '../context/DashboardContext'

// Tabs disponibles
const TABS = {
  GRAPH: 'graph',
  CASCADE: 'cascade',
  CORRELATION: 'correlation',
  HISTORY: 'history'
}

// Données de corrélation IT/OT
const correlationData = {
  score: 87,
  lastUpdate: new Date().toISOString(),
  correlatedAlerts: [
    {
      id: 'corr-1',
      itAlert: { system: 'Kafka Cluster', type: 'Lag élevé', value: '2.5K messages' },
      otAlert: { system: 'MES Production', type: 'Ordres retardés', value: '+12 ordres' },
      correlation: 92,
      impact: 'Retard propagation données production vers IT',
      recommendation: 'Augmenter les partitions Kafka pour le topic OT-events'
    },
    {
      id: 'corr-2',
      itAlert: { system: 'OTEL Collector', type: 'Métriques dropped', value: '150/min' },
      otAlert: { system: 'OPC-UA Gateway', type: 'Latence élevée', value: '245ms' },
      correlation: 85,
      impact: 'Perte partielle de télémétrie OT',
      recommendation: 'Optimiser le pipeline OTEL avec batch processing'
    },
    {
      id: 'corr-3',
      itAlert: { system: 'VictoriaMetrics', type: 'Query lente', value: '>500ms' },
      otAlert: { system: 'SCADA Central', type: 'Alertes non affichées', value: '3 alertes' },
      correlation: 78,
      impact: 'Délai affichage alarmes critiques',
      recommendation: 'Créer un index sur les métriques SCADA fréquentes'
    }
  ],
  patterns: [
    {
      id: 'pattern-1',
      name: 'Cascade MES → Production',
      frequency: 'Récurrent',
      lastOccurrence: '2h ago',
      systems: ['MES Production', 'Ligne B', 'Robot Soudure'],
      avgImpact: 12500,
      trend: 'stable'
    },
    {
      id: 'pattern-2',
      name: 'Surcharge SCADA weekend',
      frequency: 'Hebdomadaire',
      lastOccurrence: '3j ago',
      systems: ['SCADA Central', 'OPC-UA Gateway', 'All PLCs'],
      avgImpact: 3200,
      trend: 'down'
    }
  ]
}

// Historique des cascades
const cascadeHistory = [
  {
    id: 'hist-1',
    title: 'Panne Servomoteur CNC 02',
    date: '2024-01-15',
    duration: '52min',
    impact: 18100,
    status: 'resolved',
    rootCause: 'Défaillance mécanique',
    systemsAffected: 9
  },
  {
    id: 'hist-2',
    title: 'Surcharge réseau OT',
    date: '2024-01-14',
    duration: '28min',
    impact: 5400,
    status: 'resolved',
    rootCause: 'Broadcast storm',
    systemsAffected: 15
  },
  {
    id: 'hist-3',
    title: 'Perte sync MES-SCADA',
    date: '2024-01-12',
    duration: '15min',
    impact: 2100,
    status: 'resolved',
    rootCause: 'Timeout base de données',
    systemsAffected: 4
  },
  {
    id: 'hist-4',
    title: 'Défaut capteur température',
    date: '2024-01-10',
    duration: '8min',
    impact: 800,
    status: 'resolved',
    rootCause: 'Dérive calibration',
    systemsAffected: 2
  }
]

// Composant de corrélation
function CorrelationPanel() {
  return (
    <div className="space-y-6">
      {/* Score global */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-cyan-500/30">
          <div className="flex items-center gap-2 mb-2">
            <Brain className="w-5 h-5 text-cyan-400" />
            <span className="text-sm text-gray-400">Score Corrélation</span>
          </div>
          <div className="text-3xl font-bold text-white">{correlationData.score}%</div>
          <p className="text-xs text-gray-400 mt-1">Qualité alignement IT/OT</p>
        </div>

        <div className="p-4 rounded-xl bg-industrial-card border border-industrial-border">
          <div className="flex items-center gap-2 mb-2">
            <Link2 className="w-5 h-5 text-orange-400" />
            <span className="text-sm text-gray-400">Alertes Corrélées</span>
          </div>
          <div className="text-3xl font-bold text-orange-400">{correlationData.correlatedAlerts.length}</div>
          <p className="text-xs text-gray-400 mt-1">Nécessitant attention</p>
        </div>

        <div className="p-4 rounded-xl bg-industrial-card border border-industrial-border">
          <div className="flex items-center gap-2 mb-2">
            <Radio className="w-5 h-5 text-purple-400" />
            <span className="text-sm text-gray-400">Patterns Détectés</span>
          </div>
          <div className="text-3xl font-bold text-purple-400">{correlationData.patterns.length}</div>
          <p className="text-xs text-gray-400 mt-1">Récurrences identifiées</p>
        </div>

        <div className="p-4 rounded-xl bg-industrial-card border border-industrial-border">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-5 h-5 text-green-400" />
            <span className="text-sm text-gray-400">Analyse</span>
          </div>
          <div className="text-xl font-bold text-green-400">Temps réel</div>
          <p className="text-xs text-gray-400 mt-1">IA active</p>
        </div>
      </div>

      {/* Alertes corrélées */}
      <div>
        <h3 className="font-medium text-white mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-orange-400" />
          Alertes Corrélées IT/OT
        </h3>

        <div className="space-y-4">
          {correlationData.correlatedAlerts.map(alert => (
            <motion.div
              key={alert.id}
              className="p-4 rounded-xl bg-industrial-card border border-industrial-border hover:border-orange-500/30 transition-all"
              whileHover={{ x: 4 }}
            >
              <div className="flex items-start gap-4">
                {/* IT Alert */}
                <div className="flex-1 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                  <div className="flex items-center gap-2 mb-1">
                    <Server className="w-4 h-4 text-blue-400" />
                    <span className="text-xs text-blue-400">IT</span>
                  </div>
                  <div className="text-sm font-medium text-white">{alert.itAlert.system}</div>
                  <div className="text-xs text-gray-400">{alert.itAlert.type}</div>
                  <div className="text-sm text-blue-400 mt-1">{alert.itAlert.value}</div>
                </div>

                {/* Corrélation indicator */}
                <div className="flex flex-col items-center py-2">
                  <div className={`px-2 py-1 rounded text-xs font-medium ${
                    alert.correlation >= 90 ? 'bg-green-500/20 text-green-400' :
                    alert.correlation >= 80 ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-orange-500/20 text-orange-400'
                  }`}>
                    {alert.correlation}%
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-500 my-1" />
                  <Link2 className="w-4 h-4 text-gray-500" />
                </div>

                {/* OT Alert */}
                <div className="flex-1 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                  <div className="flex items-center gap-2 mb-1">
                    <Factory className="w-4 h-4 text-emerald-400" />
                    <span className="text-xs text-emerald-400">OT</span>
                  </div>
                  <div className="text-sm font-medium text-white">{alert.otAlert.system}</div>
                  <div className="text-xs text-gray-400">{alert.otAlert.type}</div>
                  <div className="text-sm text-emerald-400 mt-1">{alert.otAlert.value}</div>
                </div>
              </div>

              {/* Impact et recommandation */}
              <div className="mt-3 pt-3 border-t border-industrial-border">
                <div className="flex items-start gap-2 mb-2">
                  <Target className="w-4 h-4 text-red-400 mt-0.5" />
                  <span className="text-sm text-gray-300">{alert.impact}</span>
                </div>
                <div className="flex items-start gap-2">
                  <Sparkles className="w-4 h-4 text-cyan-400 mt-0.5" />
                  <span className="text-sm text-cyan-400">{alert.recommendation}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Patterns détectés */}
      <div>
        <h3 className="font-medium text-white mb-4 flex items-center gap-2">
          <Radio className="w-5 h-5 text-purple-400" />
          Patterns Récurrents
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {correlationData.patterns.map(pattern => (
            <div
              key={pattern.id}
              className="p-4 rounded-xl bg-industrial-card border border-industrial-border"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-white">{pattern.name}</span>
                <span className={`px-2 py-0.5 rounded text-xs ${
                  pattern.trend === 'up' ? 'bg-red-500/20 text-red-400' :
                  pattern.trend === 'down' ? 'bg-green-500/20 text-green-400' :
                  'bg-gray-500/20 text-gray-400'
                }`}>
                  {pattern.trend === 'up' ? '↑ Augmente' : pattern.trend === 'down' ? '↓ Diminue' : '→ Stable'}
                </span>
              </div>

              <div className="flex flex-wrap gap-1 mb-3">
                {pattern.systems.map(sys => (
                  <span key={sys} className="px-2 py-0.5 rounded bg-purple-500/10 text-xs text-purple-400">
                    {sys}
                  </span>
                ))}
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-gray-500">Fréquence</span>
                  <div className="text-white">{pattern.frequency}</div>
                </div>
                <div>
                  <span className="text-gray-500">Dernière occurrence</span>
                  <div className="text-white">{pattern.lastOccurrence}</div>
                </div>
                <div className="col-span-2">
                  <span className="text-gray-500">Impact moyen</span>
                  <div className="text-orange-400 font-medium">{pattern.avgImpact.toLocaleString()}€</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Composant historique
function HistoryPanel() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="font-medium text-white flex items-center gap-2">
          <Clock className="w-5 h-5 text-cyan-400" />
          Historique des Cascades (30 derniers jours)
        </h3>
        <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-industrial-border hover:bg-industrial-accent/20 text-sm text-gray-300">
          <Download className="w-4 h-4" />
          Exporter
        </button>
      </div>

      {/* Statistiques globales */}
      <div className="grid grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-industrial-card border border-industrial-border">
          <div className="text-2xl font-bold text-white">{cascadeHistory.length}</div>
          <div className="text-sm text-gray-400">Cascades totales</div>
        </div>
        <div className="p-4 rounded-xl bg-industrial-card border border-industrial-border">
          <div className="text-2xl font-bold text-yellow-400">
            {Math.round(cascadeHistory.reduce((sum, c) => sum + parseInt(c.duration), 0) / cascadeHistory.length)}min
          </div>
          <div className="text-sm text-gray-400">Durée moyenne</div>
        </div>
        <div className="p-4 rounded-xl bg-industrial-card border border-industrial-border">
          <div className="text-2xl font-bold text-red-400">
            {(cascadeHistory.reduce((sum, c) => sum + c.impact, 0) / 1000).toFixed(1)}K€
          </div>
          <div className="text-sm text-gray-400">Impact total</div>
        </div>
        <div className="p-4 rounded-xl bg-industrial-card border border-industrial-border">
          <div className="text-2xl font-bold text-green-400">100%</div>
          <div className="text-sm text-gray-400">Taux résolution</div>
        </div>
      </div>

      {/* Liste des cascades */}
      <div className="overflow-hidden rounded-xl border border-industrial-border">
        <table className="w-full">
          <thead className="bg-industrial-card">
            <tr className="text-left text-xs text-gray-400">
              <th className="p-4">Date</th>
              <th className="p-4">Incident</th>
              <th className="p-4">Cause Racine</th>
              <th className="p-4">Durée</th>
              <th className="p-4">Systèmes</th>
              <th className="p-4">Impact</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-industrial-border">
            {cascadeHistory.map(cascade => (
              <tr key={cascade.id} className="hover:bg-industrial-card/50 cursor-pointer">
                <td className="p-4 text-sm text-gray-300">{cascade.date}</td>
                <td className="p-4">
                  <span className="text-sm text-white font-medium">{cascade.title}</span>
                </td>
                <td className="p-4 text-sm text-gray-400">{cascade.rootCause}</td>
                <td className="p-4 text-sm text-yellow-400">{cascade.duration}</td>
                <td className="p-4 text-sm text-gray-300">{cascade.systemsAffected}</td>
                <td className="p-4 text-sm text-red-400 font-medium">{cascade.impact.toLocaleString()}€</td>
                <td className="p-4">
                  <span className="flex items-center gap-1 text-xs text-green-400">
                    <CheckCircle className="w-3 h-3" />
                    Résolu
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Page principale
function ImpactChainPage() {
  const { t } = useI18n()
  const navigate = useNavigate()
  const { metrics } = useDashboard()
  const [activeTab, setActiveTab] = useState(TABS.GRAPH)
  const [showFullGraph, setShowFullGraph] = useState(false)

  const tabs = [
    { id: TABS.GRAPH, label: 'Graphe IT/OT', icon: GitBranch },
    { id: TABS.CASCADE, label: 'Analyse Cascade', icon: Layers },
    { id: TABS.CORRELATION, label: 'Corrélation', icon: Link2 },
    { id: TABS.HISTORY, label: 'Historique', icon: Clock }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
              <GitBranch className="w-5 h-5 text-white" />
            </div>
            Chaîne d'Impact IT/OT
          </h1>
          <p className="text-gray-400 mt-1">
            Analyse des dépendances et propagation d'impact entre systèmes IT et OT
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-industrial-card border border-industrial-border hover:border-cyan-500/50 transition-colors">
            <RefreshCw className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-300">Actualiser</span>
          </button>
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-industrial-card border border-industrial-border hover:border-cyan-500/50 transition-colors">
            <Download className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-300">Exporter</span>
          </button>
        </div>
      </div>

      {/* Alerte active si impact en cours */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-4 rounded-xl bg-gradient-to-r from-red-500/20 via-orange-500/10 to-yellow-500/10 border border-red-500/30"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-red-500/20 flex items-center justify-center animate-pulse">
              <AlertTriangle className="w-5 h-5 text-red-400" />
            </div>
            <div>
              <h3 className="font-semibold text-white">Cascade d'impact en cours</h3>
              <p className="text-sm text-gray-400">
                Panne CNC Machine 02 → 9 systèmes affectés → Impact estimé: 18 100€
              </p>
            </div>
          </div>
          <button
            onClick={() => setActiveTab(TABS.CASCADE)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
          >
            <Eye className="w-4 h-4" />
            Analyser
          </button>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="flex items-center gap-2 p-1 bg-industrial-card border border-industrial-border rounded-xl">
        {tabs.map(tab => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-white border border-cyan-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-industrial-border'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium">{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* Contenu des tabs */}
      <AnimatePresence mode="wait">
        {activeTab === TABS.GRAPH && (
          <motion.div
            key="graph"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <ITOTImpactGraph />
          </motion.div>
        )}

        {activeTab === TABS.CASCADE && (
          <motion.div
            key="cascade"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <CascadeAnalysisView />
          </motion.div>
        )}

        {activeTab === TABS.CORRELATION && (
          <motion.div
            key="correlation"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <CorrelationPanel />
          </motion.div>
        )}

        {activeTab === TABS.HISTORY && (
          <motion.div
            key="history"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <HistoryPanel />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Navigation vers autres vues */}
      <Card className="bg-industrial-card/50 border-industrial-border">
        <CardBody className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Target className="w-5 h-5 text-cyan-400" />
              <span className="font-medium text-white">Explorer plus en détail</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => navigate('/impact-analysis')}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-industrial-border hover:bg-industrial-accent/20 text-gray-300 transition-colors"
              >
                Analyse d'Impact
                <ChevronRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 transition-colors"
              >
                Vue Globale
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

export default ImpactChainPage
