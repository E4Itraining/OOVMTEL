import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield,
  Lock,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Eye,
  FileText,
  Target,
  TrendingUp,
  TrendingDown,
  Server,
  Database,
  RefreshCw,
  ChevronRight,
  ChevronDown,
  Settings,
  XCircle,
  AlertCircle,
  CheckCircle,
  History,
  Brain,
  Zap,
  Activity,
  BarChart3,
  PieChart,
  ShieldCheck,
  ShieldAlert,
  KeyRound,
  UserCheck,
  FileWarning,
  Scan,
  Bug,
  CircleDot,
  Sparkles,
  Lightbulb,
  ArrowRight,
  ExternalLink,
  Filter,
  Download,
  Video,
  Play,
  Pause,
  Camera,
  Circle,
  MapPin,
  Calendar,
  Maximize2,
  Scale,
  Globe,
  Building2,
  Cpu,
  Network,
  Users,
  FileCheck,
  AlertOctagon,
  Info,
  Layers
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { TimeSeriesChart, DonutChart, AreaChartComponent, BarChartComponent } from '../components/ui/Charts'
import { StatusBadge, StatusDot, HealthIndicator } from '../components/ui/Status'
import { RadialGauge, LinearGauge, SemiCircleGauge } from '../components/ui/Gauge'

// Mock data for compliance frameworks
const complianceFrameworks = [
  {
    id: 'iso27001',
    name: 'ISO 27001',
    score: 94,
    status: 'compliant',
    lastAudit: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    nextAudit: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000),
    controls: { passed: 114, failed: 3, pending: 5 }
  },
  {
    id: 'soc2',
    name: 'SOC 2 Type II',
    score: 98,
    status: 'compliant',
    lastAudit: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000),
    nextAudit: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000),
    controls: { passed: 78, failed: 1, pending: 2 }
  },
  {
    id: 'gdpr',
    name: 'GDPR',
    score: 91,
    status: 'partial',
    lastAudit: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
    nextAudit: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
    controls: { passed: 45, failed: 4, pending: 3 }
  },
  {
    id: 'nis2',
    name: 'NIS 2',
    score: 87,
    status: 'partial',
    lastAudit: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000),
    nextAudit: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000),
    controls: { passed: 52, failed: 6, pending: 4 }
  },
  {
    id: 'aiact',
    name: 'AI Act',
    score: 78,
    status: 'partial',
    lastAudit: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
    nextAudit: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
    controls: { passed: 38, failed: 8, pending: 6 }
  }
]

// AI Act detailed compliance data
const aiActRequirements = [
  {
    id: 'aiact-001',
    category: 'risk_management',
    name: 'Système de gestion des risques IA',
    description: 'Mise en place d\'un système de gestion des risques pour les systèmes d\'IA à haut risque',
    status: 'compliant',
    progress: 95,
    deadline: new Date(Date.now() + 180 * 24 * 60 * 60 * 1000),
    priority: 'critical'
  },
  {
    id: 'aiact-002',
    category: 'data_governance',
    name: 'Gouvernance des données d\'entraînement',
    description: 'Pratiques de gouvernance des données pour les jeux de données d\'entraînement, de validation et de test',
    status: 'partial',
    progress: 72,
    deadline: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000),
    priority: 'high'
  },
  {
    id: 'aiact-003',
    category: 'documentation',
    name: 'Documentation technique',
    description: 'Documentation technique complète démontrant la conformité avant mise sur le marché',
    status: 'partial',
    progress: 65,
    deadline: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000),
    priority: 'high'
  },
  {
    id: 'aiact-004',
    category: 'transparency',
    name: 'Obligations de transparence',
    description: 'Information des utilisateurs qu\'ils interagissent avec un système d\'IA',
    status: 'compliant',
    progress: 100,
    deadline: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000),
    priority: 'medium'
  },
  {
    id: 'aiact-005',
    category: 'human_oversight',
    name: 'Supervision humaine',
    description: 'Mesures permettant une supervision humaine efficace des systèmes d\'IA',
    status: 'partial',
    progress: 80,
    deadline: new Date(Date.now() + 150 * 24 * 60 * 60 * 1000),
    priority: 'critical'
  },
  {
    id: 'aiact-006',
    category: 'accuracy',
    name: 'Précision et robustesse',
    description: 'Niveaux appropriés de précision, robustesse et cybersécurité',
    status: 'partial',
    progress: 68,
    deadline: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000),
    priority: 'high'
  },
  {
    id: 'aiact-007',
    category: 'logging',
    name: 'Journalisation automatique',
    description: 'Capacités de journalisation automatique pendant le fonctionnement du système',
    status: 'compliant',
    progress: 92,
    deadline: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000),
    priority: 'medium'
  },
  {
    id: 'aiact-008',
    category: 'conformity',
    name: 'Évaluation de conformité',
    description: 'Procédure d\'évaluation de conformité avant mise sur le marché',
    status: 'pending',
    progress: 45,
    deadline: new Date(Date.now() + 180 * 24 * 60 * 60 * 1000),
    priority: 'critical'
  }
]

// AI systems inventory with risk classification
const aiSystemsInventory = [
  {
    id: 'ai-sys-001',
    name: 'Maintenance Prédictive IA',
    description: 'Prédiction des pannes équipements',
    riskLevel: 'limited',
    status: 'compliant',
    lastAssessment: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
    provider: 'Interne',
    useCases: ['Maintenance', 'Optimisation']
  },
  {
    id: 'ai-sys-002',
    name: 'Assistant IA Conversationnel',
    description: 'Chatbot pour requêtes opérateurs',
    riskLevel: 'limited',
    status: 'compliant',
    lastAssessment: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
    provider: 'Anthropic',
    useCases: ['Support', 'Analyse']
  },
  {
    id: 'ai-sys-003',
    name: 'Contrôle Qualité Vision',
    description: 'Détection automatique des défauts',
    riskLevel: 'high',
    status: 'partial',
    lastAssessment: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    provider: 'Interne',
    useCases: ['Qualité', 'Production']
  },
  {
    id: 'ai-sys-004',
    name: 'Détection Anomalies Sécurité',
    description: 'Surveillance comportementale réseau',
    riskLevel: 'high',
    status: 'partial',
    lastAssessment: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000),
    provider: 'Interne',
    useCases: ['Sécurité', 'Monitoring']
  },
  {
    id: 'ai-sys-005',
    name: 'Optimisation Énergie',
    description: 'Gestion intelligente consommation',
    riskLevel: 'minimal',
    status: 'compliant',
    lastAssessment: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000),
    provider: 'Externe',
    useCases: ['Énergie', 'Durabilité']
  }
]

// NIS 2 detailed compliance data
const nis2Requirements = [
  {
    id: 'nis2-001',
    category: 'governance',
    name: 'Gouvernance Cybersécurité',
    description: 'Approbation des mesures de gestion des risques par l\'organe de direction',
    status: 'compliant',
    progress: 95,
    deadline: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000),
    priority: 'critical'
  },
  {
    id: 'nis2-002',
    category: 'risk_management',
    name: 'Analyse des risques cyber',
    description: 'Politiques d\'analyse des risques et sécurité des systèmes d\'information',
    status: 'partial',
    progress: 82,
    deadline: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000),
    priority: 'critical'
  },
  {
    id: 'nis2-003',
    category: 'incident_handling',
    name: 'Gestion des incidents',
    description: 'Procédures de gestion et notification des incidents',
    status: 'compliant',
    progress: 90,
    deadline: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000),
    priority: 'high'
  },
  {
    id: 'nis2-004',
    category: 'business_continuity',
    name: 'Continuité d\'activité',
    description: 'Plans de continuité incluant gestion des sauvegardes et reprise après sinistre',
    status: 'partial',
    progress: 75,
    deadline: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000),
    priority: 'high'
  },
  {
    id: 'nis2-005',
    category: 'supply_chain',
    name: 'Sécurité chaîne d\'approvisionnement',
    description: 'Sécurité dans les relations avec les fournisseurs et prestataires',
    status: 'partial',
    progress: 68,
    deadline: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000),
    priority: 'high'
  },
  {
    id: 'nis2-006',
    category: 'security_development',
    name: 'Sécurité développement et maintenance',
    description: 'Sécurité dans l\'acquisition, le développement et la maintenance des systèmes',
    status: 'compliant',
    progress: 88,
    deadline: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000),
    priority: 'medium'
  },
  {
    id: 'nis2-007',
    category: 'effectiveness',
    name: 'Évaluation de l\'efficacité',
    description: 'Politiques et procédures pour évaluer l\'efficacité des mesures',
    status: 'partial',
    progress: 72,
    deadline: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000),
    priority: 'medium'
  },
  {
    id: 'nis2-008',
    category: 'crypto',
    name: 'Cryptographie',
    description: 'Politiques d\'utilisation de la cryptographie et du chiffrement',
    status: 'compliant',
    progress: 94,
    deadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
    priority: 'high'
  },
  {
    id: 'nis2-009',
    category: 'hr_security',
    name: 'Sécurité des ressources humaines',
    description: 'Contrôle d\'accès et gestion des actifs',
    status: 'compliant',
    progress: 91,
    deadline: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000),
    priority: 'medium'
  },
  {
    id: 'nis2-010',
    category: 'mfa',
    name: 'Authentification multi-facteurs',
    description: 'Solutions d\'authentification MFA et communications sécurisées',
    status: 'compliant',
    progress: 98,
    deadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
    priority: 'critical'
  }
]

// NIS 2 incident reports
const nis2Incidents = [
  {
    id: 'inc-001',
    type: 'significant',
    title: 'Tentative d\'intrusion détectée',
    description: 'Activité suspecte sur le réseau OT bloquée par le firewall',
    status: 'resolved',
    reportedToAuthority: true,
    detectionTime: new Date(Date.now() - 48 * 60 * 60 * 1000),
    resolutionTime: new Date(Date.now() - 44 * 60 * 60 * 1000),
    impact: 'low'
  },
  {
    id: 'inc-002',
    type: 'minor',
    title: 'Vulnérabilité critique patchée',
    description: 'CVE-2024-1234 corrigé dans les 24h suivant la découverte',
    status: 'resolved',
    reportedToAuthority: false,
    detectionTime: new Date(Date.now() - 72 * 60 * 60 * 1000),
    resolutionTime: new Date(Date.now() - 48 * 60 * 60 * 1000),
    impact: 'medium'
  }
]

// Mock data for vulnerabilities
const vulnerabilities = [
  {
    id: 'CVE-2024-1234',
    severity: 'critical',
    title: 'Remote Code Execution in API Gateway',
    service: 'API Gateway',
    discovered: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    status: 'in_progress',
    cvss: 9.8,
    assignee: 'Security Team'
  },
  {
    id: 'CVE-2024-5678',
    severity: 'high',
    title: 'SQL Injection in User Service',
    service: 'User Service',
    discovered: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    status: 'patched',
    cvss: 8.1,
    assignee: 'DevOps Team'
  },
  {
    id: 'CVE-2024-9012',
    severity: 'medium',
    title: 'Cross-Site Scripting in Dashboard',
    service: 'Frontend',
    discovered: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    status: 'open',
    cvss: 6.5,
    assignee: 'Frontend Team'
  },
  {
    id: 'CVE-2024-3456',
    severity: 'low',
    title: 'Information Disclosure in Logs',
    service: 'Logging Service',
    discovered: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
    status: 'open',
    cvss: 3.2,
    assignee: 'Ops Team'
  }
]

// Mock data for AI insights
const aiInsights = [
  {
    id: 'ai-001',
    type: 'anomaly',
    severity: 'warning',
    title: 'Unusual login pattern detected',
    description: 'AI detected 340% increase in failed login attempts from IP range 192.168.x.x',
    confidence: 94,
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    recommendation: 'Consider implementing rate limiting or temporary IP blocking'
  },
  {
    id: 'ai-002',
    type: 'prediction',
    severity: 'info',
    title: 'Certificate expiration predicted',
    description: 'SSL certificate for api.example.com will expire in 14 days',
    confidence: 100,
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    recommendation: 'Schedule certificate renewal before expiration'
  },
  {
    id: 'ai-003',
    type: 'anomaly',
    severity: 'critical',
    title: 'Data exfiltration risk detected',
    description: 'Unusual outbound data transfer pattern detected from database server',
    confidence: 87,
    timestamp: new Date(Date.now() - 45 * 60 * 1000),
    recommendation: 'Investigate immediately and review database access logs'
  },
  {
    id: 'ai-004',
    type: 'optimization',
    severity: 'info',
    title: 'Security policy optimization',
    description: 'Current firewall rules can be consolidated to improve performance by 15%',
    confidence: 92,
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    recommendation: 'Review and merge redundant firewall rules'
  }
]

// Mock data for audit logs
const auditLogs = [
  {
    id: 'AUD-001',
    action: 'USER_LOGIN',
    user: 'admin@synapsix.io',
    resource: 'Dashboard',
    status: 'success',
    ip: '10.0.1.45',
    timestamp: new Date(Date.now() - 5 * 60 * 1000)
  },
  {
    id: 'AUD-002',
    action: 'CONFIG_CHANGE',
    user: 'ops@synapsix.io',
    resource: 'Firewall Rules',
    status: 'success',
    ip: '10.0.1.23',
    timestamp: new Date(Date.now() - 15 * 60 * 1000)
  },
  {
    id: 'AUD-003',
    action: 'ACCESS_DENIED',
    user: 'unknown',
    resource: 'Admin Panel',
    status: 'failed',
    ip: '203.0.113.42',
    timestamp: new Date(Date.now() - 25 * 60 * 1000)
  },
  {
    id: 'AUD-004',
    action: 'DATA_EXPORT',
    user: 'analyst@synapsix.io',
    resource: 'Reports API',
    status: 'success',
    ip: '10.0.1.67',
    timestamp: new Date(Date.now() - 45 * 60 * 1000)
  },
  {
    id: 'AUD-005',
    action: 'PERMISSION_CHANGE',
    user: 'admin@synapsix.io',
    resource: 'User: dev@synapsix.io',
    status: 'success',
    ip: '10.0.1.45',
    timestamp: new Date(Date.now() - 60 * 60 * 1000)
  }
]

// Mock data for security policies
const securityPolicies = [
  {
    id: 'pol-001',
    name: 'Password Policy',
    status: 'enforced',
    lastUpdated: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    compliance: 98,
    violations: 12
  },
  {
    id: 'pol-002',
    name: 'Data Encryption',
    status: 'enforced',
    lastUpdated: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
    compliance: 100,
    violations: 0
  },
  {
    id: 'pol-003',
    name: 'Access Control',
    status: 'enforced',
    lastUpdated: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    compliance: 95,
    violations: 23
  },
  {
    id: 'pol-004',
    name: 'Network Segmentation',
    status: 'partial',
    lastUpdated: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000),
    compliance: 78,
    violations: 45
  },
  {
    id: 'pol-005',
    name: 'Incident Response',
    status: 'enforced',
    lastUpdated: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
    compliance: 92,
    violations: 5
  }
]

// Mock data for security video feeds
const securityVideoFeeds = [
  {
    id: 'cam-001',
    name: 'Main Entrance',
    location: 'Building A - Ground Floor',
    status: 'online',
    recording: true,
    lastMotion: new Date(Date.now() - 5 * 60 * 1000),
    resolution: '4K',
    fps: 30,
    alerts: 0
  },
  {
    id: 'cam-002',
    name: 'Server Room',
    location: 'Building A - Basement',
    status: 'online',
    recording: true,
    lastMotion: new Date(Date.now() - 15 * 60 * 1000),
    resolution: '1080p',
    fps: 30,
    alerts: 2
  },
  {
    id: 'cam-003',
    name: 'Production Floor 1',
    location: 'Building B - Main Hall',
    status: 'online',
    recording: true,
    lastMotion: new Date(Date.now() - 2 * 60 * 1000),
    resolution: '4K',
    fps: 60,
    alerts: 0
  },
  {
    id: 'cam-004',
    name: 'Parking Area',
    location: 'Exterior - North',
    status: 'offline',
    recording: false,
    lastMotion: new Date(Date.now() - 2 * 60 * 60 * 1000),
    resolution: '1080p',
    fps: 30,
    alerts: 1
  },
  {
    id: 'cam-005',
    name: 'Control Room',
    location: 'Building A - Floor 2',
    status: 'online',
    recording: true,
    lastMotion: new Date(Date.now() - 1 * 60 * 1000),
    resolution: '4K',
    fps: 30,
    alerts: 0
  },
  {
    id: 'cam-006',
    name: 'Warehouse',
    location: 'Building C',
    status: 'online',
    recording: true,
    lastMotion: new Date(Date.now() - 30 * 60 * 1000),
    resolution: '1080p',
    fps: 30,
    alerts: 0
  }
]

// Mock data for video events/recordings
const videoEvents = [
  {
    id: 'evt-001',
    cameraId: 'cam-002',
    cameraName: 'Server Room',
    type: 'motion',
    severity: 'warning',
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    description: 'Unauthorized access attempt detected',
    thumbnail: null,
    duration: '00:02:34'
  },
  {
    id: 'evt-002',
    cameraId: 'cam-004',
    cameraName: 'Parking Area',
    type: 'offline',
    severity: 'critical',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    description: 'Camera went offline unexpectedly',
    thumbnail: null,
    duration: null
  },
  {
    id: 'evt-003',
    cameraId: 'cam-001',
    cameraName: 'Main Entrance',
    type: 'motion',
    severity: 'info',
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    description: 'Regular visitor entry detected',
    thumbnail: null,
    duration: '00:00:45'
  },
  {
    id: 'evt-004',
    cameraId: 'cam-002',
    cameraName: 'Server Room',
    type: 'intrusion',
    severity: 'critical',
    timestamp: new Date(Date.now() - 45 * 60 * 1000),
    description: 'After-hours access detected - Security alerted',
    thumbnail: null,
    duration: '00:05:12'
  }
]

// Generate chart data
const generateSecurityTrendData = () => {
  const data = []
  for (let i = 30; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    data.push({
      time: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      score: Math.min(100, 85 + Math.random() * 10 + i * 0.2),
      threats: Math.floor(Math.random() * 15) + 5,
      blocked: Math.floor(Math.random() * 12) + 3
    })
  }
  return data
}

const generateVulnerabilityDistribution = () => [
  { name: 'Critical', value: 2, color: '#ef4444' },
  { name: 'High', value: 5, color: '#f97316' },
  { name: 'Medium', value: 12, color: '#eab308' },
  { name: 'Low', value: 23, color: '#22c55e' }
]

// Compliance Framework Card
function ComplianceCard({ framework, t }) {
  const statusColors = {
    compliant: 'bg-green-500/20 border-green-500/30 text-green-400',
    partial: 'bg-yellow-500/20 border-yellow-500/30 text-yellow-400',
    'non-compliant': 'bg-red-500/20 border-red-500/30 text-red-400'
  }

  const gaugeColor = framework.score >= 90 ? '#22c55e' : framework.score >= 75 ? '#eab308' : '#ef4444'

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="p-4 rounded-xl border border-industrial-border bg-industrial-card/50"
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h4 className="font-semibold text-white text-lg">{framework.name}</h4>
          <span className={`inline-block px-2 py-0.5 rounded text-xs mt-1 border ${statusColors[framework.status]}`}>
            {framework.status === 'compliant' ? t('security.compliant') : t('security.partial')}
          </span>
        </div>
        <div className="w-16 h-16">
          <RadialGauge value={framework.score} max={100} color={gaugeColor} size={64} showLabel />
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">{t('security.controls')}</span>
          <div className="flex gap-2">
            <span className="text-green-400">{framework.controls.passed} {t('security.passed')}</span>
            <span className="text-red-400">{framework.controls.failed} {t('security.failed')}</span>
          </div>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">{t('security.nextAudit')}</span>
          <span className="text-white">{framework.nextAudit.toLocaleDateString()}</span>
        </div>
      </div>
    </motion.div>
  )
}

// Vulnerability Card
function VulnerabilityCard({ vuln, t }) {
  const severityColors = {
    critical: 'border-red-500/50 bg-red-500/10',
    high: 'border-orange-500/50 bg-orange-500/10',
    medium: 'border-yellow-500/50 bg-yellow-500/10',
    low: 'border-green-500/50 bg-green-500/10'
  }

  const severityTextColors = {
    critical: 'text-red-400',
    high: 'text-orange-400',
    medium: 'text-yellow-400',
    low: 'text-green-400'
  }

  const statusBadge = {
    open: { color: 'bg-red-500/20 text-red-400', label: t('security.statusOpen') },
    in_progress: { color: 'bg-yellow-500/20 text-yellow-400', label: t('security.statusInProgress') },
    patched: { color: 'bg-green-500/20 text-green-400', label: t('security.statusPatched') }
  }

  return (
    <motion.div
      whileHover={{ x: 4 }}
      className={`p-4 rounded-xl border ${severityColors[vuln.severity]} flex items-center gap-4`}
    >
      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${severityColors[vuln.severity]}`}>
        <Bug className={`w-6 h-6 ${severityTextColors[vuln.severity]}`} />
      </div>

      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm text-gray-400">{vuln.id}</span>
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusBadge[vuln.status].color}`}>
            {statusBadge[vuln.status].label}
          </span>
        </div>
        <h4 className="font-medium text-white mt-1">{vuln.title}</h4>
        <div className="flex items-center gap-4 mt-1 text-sm text-gray-400">
          <span>{vuln.service}</span>
          <span className={`font-bold ${severityTextColors[vuln.severity]}`}>
            CVSS {vuln.cvss}
          </span>
        </div>
      </div>

      <button className="px-3 py-1.5 rounded-lg bg-industrial-accent/20 text-industrial-accent hover:bg-industrial-accent/30 transition-colors text-sm">
        {t('security.viewDetails')}
      </button>
    </motion.div>
  )
}

// AI Insight Card
function AIInsightCard({ insight, t }) {
  const typeIcons = {
    anomaly: AlertTriangle,
    prediction: Lightbulb,
    optimization: Sparkles
  }

  const severityColors = {
    critical: 'border-red-500/50 bg-red-500/10',
    warning: 'border-yellow-500/50 bg-yellow-500/10',
    info: 'border-blue-500/50 bg-blue-500/10'
  }

  const Icon = typeIcons[insight.type] || Brain

  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      className={`p-4 rounded-xl border ${severityColors[insight.severity]}`}
    >
      <div className="flex items-start gap-4">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center bg-purple-500/20`}>
          <Brain className="w-5 h-5 text-purple-400" />
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 uppercase">
              {t(`security.aiType.${insight.type}`)}
            </span>
            <span className="text-xs text-gray-500">
              {t('security.confidence')}: {insight.confidence}%
            </span>
          </div>
          <h4 className="font-medium text-white">{insight.title}</h4>
          <p className="text-sm text-gray-400 mt-1">{insight.description}</p>

          <div className="mt-3 p-3 rounded-lg bg-white/5">
            <div className="flex items-center gap-2 text-sm">
              <Lightbulb className="w-4 h-4 text-yellow-400" />
              <span className="text-gray-300">{insight.recommendation}</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// Policy Status Card
function PolicyCard({ policy, t }) {
  const statusColors = {
    enforced: 'text-green-400',
    partial: 'text-yellow-400',
    disabled: 'text-red-400'
  }

  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
      <div className="flex items-center gap-3">
        {policy.status === 'enforced' ? (
          <ShieldCheck className="w-5 h-5 text-green-400" />
        ) : (
          <ShieldAlert className="w-5 h-5 text-yellow-400" />
        )}
        <div>
          <h4 className="font-medium text-white">{policy.name}</h4>
          <span className={`text-xs ${statusColors[policy.status]}`}>
            {t(`security.policyStatus.${policy.status}`)}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-right">
          <p className="text-sm text-gray-400">{t('security.compliance')}</p>
          <p className={`font-bold ${policy.compliance >= 90 ? 'text-green-400' : 'text-yellow-400'}`}>
            {policy.compliance}%
          </p>
        </div>
        {policy.violations > 0 && (
          <span className="px-2 py-1 rounded bg-red-500/20 text-red-400 text-xs">
            {policy.violations} {t('security.violations')}
          </span>
        )}
      </div>
    </div>
  )
}

// Video Feed Card
function VideoFeedCard({ feed, t, formatTime }) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className="rounded-xl border border-industrial-border bg-industrial-card/50 overflow-hidden"
    >
      {/* Video Preview Area */}
      <div className="relative aspect-video bg-black/50">
        {/* Simulated video feed - gradient placeholder */}
        <div className="absolute inset-0 bg-gradient-to-br from-gray-800 via-gray-900 to-black flex items-center justify-center">
          {feed.status === 'online' ? (
            <div className="relative w-full h-full">
              {/* Simulated camera view with grid */}
              <div className="absolute inset-0 opacity-20">
                <div className="w-full h-full" style={{
                  backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
                  backgroundSize: '20px 20px'
                }} />
              </div>
              {/* Camera icon */}
              <div className="absolute inset-0 flex items-center justify-center">
                <Camera className="w-12 h-12 text-gray-600" />
              </div>
              {/* Recording indicator */}
              {feed.recording && (
                <div className="absolute top-2 left-2 flex items-center gap-1.5 px-2 py-1 rounded bg-red-500/90 text-white text-xs">
                  <Circle className="w-2 h-2 fill-current animate-pulse" />
                  REC
                </div>
              )}
              {/* Live badge */}
              <div className="absolute top-2 right-2 px-2 py-1 rounded bg-green-500/90 text-white text-xs font-medium">
                LIVE
              </div>
              {/* Resolution badge */}
              <div className="absolute bottom-2 left-2 px-2 py-1 rounded bg-black/60 text-white text-xs">
                {feed.resolution} @ {feed.fps}fps
              </div>
              {/* Timestamp */}
              <div className="absolute bottom-2 right-2 px-2 py-1 rounded bg-black/60 text-white text-xs font-mono">
                {new Date().toLocaleTimeString()}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2 text-gray-500">
              <Video className="w-12 h-12" />
              <span className="text-sm">{t('security.video.offline')}</span>
            </div>
          )}
        </div>

        {/* Hover overlay with controls */}
        <AnimatePresence>
          {isHovered && feed.status === 'online' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/40 flex items-center justify-center gap-4"
            >
              <button className="p-3 rounded-full bg-white/20 hover:bg-white/30 transition-colors">
                <Play className="w-6 h-6 text-white" />
              </button>
              <button className="p-3 rounded-full bg-white/20 hover:bg-white/30 transition-colors">
                <Maximize2 className="w-6 h-6 text-white" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Camera Info */}
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h4 className="font-semibold text-white">{feed.name}</h4>
            <div className="flex items-center gap-1 text-sm text-gray-400">
              <MapPin className="w-3 h-3" />
              {feed.location}
            </div>
          </div>
          <div className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs ${
            feed.status === 'online'
              ? 'bg-green-500/20 text-green-400'
              : 'bg-red-500/20 text-red-400'
          }`}>
            <Circle className={`w-2 h-2 fill-current ${feed.status === 'online' ? 'animate-pulse' : ''}`} />
            {feed.status === 'online' ? t('security.video.online') : t('security.video.offline')}
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{t('security.video.lastMotion')}: {formatTime(feed.lastMotion)}</span>
          {feed.alerts > 0 && (
            <span className="px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400">
              {feed.alerts} {t('security.video.alerts')}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  )
}

// Video Event Card
function VideoEventCard({ event, t, formatTime }) {
  const severityColors = {
    critical: 'border-red-500/50 bg-red-500/10',
    warning: 'border-yellow-500/50 bg-yellow-500/10',
    info: 'border-blue-500/50 bg-blue-500/10'
  }

  const severityTextColors = {
    critical: 'text-red-400',
    warning: 'text-yellow-400',
    info: 'text-blue-400'
  }

  const typeIcons = {
    motion: Activity,
    offline: XCircle,
    intrusion: AlertTriangle
  }

  const Icon = typeIcons[event.type] || Video

  return (
    <motion.div
      whileHover={{ x: 4 }}
      className={`p-4 rounded-xl border ${severityColors[event.severity]} flex items-center gap-4`}
    >
      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${severityColors[event.severity]}`}>
        <Icon className={`w-6 h-6 ${severityTextColors[event.severity]}`} />
      </div>

      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-mono text-sm text-gray-400">{event.cameraName}</span>
          <span className={`px-2 py-0.5 rounded text-xs ${severityColors[event.severity]} ${severityTextColors[event.severity]}`}>
            {event.type}
          </span>
        </div>
        <h4 className="font-medium text-white">{event.description}</h4>
        <div className="flex items-center gap-4 mt-1 text-sm text-gray-400">
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {formatTime(event.timestamp)}
          </span>
          {event.duration && (
            <span className="flex items-center gap-1">
              <Video className="w-3 h-3" />
              {event.duration}
            </span>
          )}
        </div>
      </div>

      <button className="px-3 py-1.5 rounded-lg bg-industrial-accent/20 text-industrial-accent hover:bg-industrial-accent/30 transition-colors text-sm">
        {t('security.video.viewRecording')}
      </button>
    </motion.div>
  )
}

function SecurityComplianceView() {
  const { metrics, userMode } = useDashboard()
  const { t, formatTime, formatDate } = useI18n()
  const [activeTab, setActiveTab] = useState('overview')
  const [expandedInsight, setExpandedInsight] = useState(null)

  const securityTrendData = useMemo(() => generateSecurityTrendData(), [])
  const vulnDistribution = useMemo(() => generateVulnerabilityDistribution(), [])

  // Calculate summary metrics
  const summaryMetrics = useMemo(() => {
    const avgCompliance = Math.round(
      complianceFrameworks.reduce((acc, f) => acc + f.score, 0) / complianceFrameworks.length
    )
    const criticalVulns = vulnerabilities.filter(v => v.severity === 'critical').length
    const openVulns = vulnerabilities.filter(v => v.status === 'open').length
    const aiAlerts = aiInsights.filter(i => i.severity === 'critical' || i.severity === 'warning').length
    const onlineCameras = securityVideoFeeds.filter(f => f.status === 'online').length
    const totalCameras = securityVideoFeeds.length

    return { avgCompliance, criticalVulns, openVulns, aiAlerts, onlineCameras, totalCameras }
  }, [])

  const tabs = [
    { id: 'overview', label: t('security.tabs.overview'), icon: Eye },
    { id: 'compliance', label: t('security.tabs.compliance'), icon: ShieldCheck },
    { id: 'euRegulations', label: t('security.tabs.euRegulations'), icon: Globe },
    { id: 'vulnerabilities', label: t('security.tabs.vulnerabilities'), icon: Bug },
    { id: 'aiInsights', label: t('security.tabs.aiInsights'), icon: Brain },
    { id: 'audit', label: t('security.tabs.audit'), icon: History },
    { id: 'policies', label: t('security.tabs.policies'), icon: FileText },
    { id: 'video', label: t('security.tabs.video'), icon: Video }
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">{t('security.title')}</h1>
          <p className="text-gray-400 mt-1">{t('security.description')}</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 text-gray-300 hover:bg-white/20 transition-colors">
            <Download className="w-4 h-4" />
            {t('security.exportReport')}
          </button>
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-industrial-accent text-white hover:bg-industrial-accent/80 transition-colors">
            <Scan className="w-4 h-4" />
            {t('security.runScan')}
          </button>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-6 gap-4">
        <MetricCard
          label={t('security.overallScore')}
          value={`${summaryMetrics.avgCompliance}%`}
          icon={Shield}
          color="cyan"
          trend={{ value: 3, direction: 'up' }}
        />
        <MetricCard
          label={t('security.criticalVulns')}
          value={summaryMetrics.criticalVulns}
          icon={Bug}
          color={summaryMetrics.criticalVulns > 0 ? 'red' : 'green'}
        />
        <MetricCard
          label={t('security.openVulns')}
          value={summaryMetrics.openVulns}
          icon={AlertTriangle}
          color={summaryMetrics.openVulns > 2 ? 'yellow' : 'green'}
        />
        <MetricCard
          label={t('security.aiAlerts')}
          value={summaryMetrics.aiAlerts}
          icon={Brain}
          color="purple"
        />
        <MetricCard
          label={t('security.activePolicies')}
          value={securityPolicies.filter(p => p.status === 'enforced').length}
          icon={ShieldCheck}
          color="green"
        />
        <MetricCard
          label={t('security.video.cameras')}
          value={`${summaryMetrics.onlineCameras}/${summaryMetrics.totalCameras}`}
          icon={Camera}
          color={summaryMetrics.onlineCameras === summaryMetrics.totalCameras ? 'green' : 'yellow'}
        />
      </div>

      {/* Tabs Navigation */}
      <div className="flex gap-2 border-b border-industrial-border pb-2 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? 'bg-industrial-accent/20 text-industrial-accent border-b-2 border-industrial-accent'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Security Score Trend & Vulnerability Distribution */}
            <div className="grid grid-cols-3 gap-6">
              <Card className="col-span-2">
                <CardHeader title={t('security.securityTrend')} icon={TrendingUp} />
                <CardBody>
                  <TimeSeriesChart
                    data={securityTrendData}
                    lines={[
                      { dataKey: 'score', name: t('security.securityScore'), color: '#06b6d4' },
                      { dataKey: 'threats', name: t('security.threatsDetected'), color: '#ef4444' },
                      { dataKey: 'blocked', name: t('security.threatsBlocked'), color: '#22c55e' }
                    ]}
                    height={250}
                  />
                </CardBody>
              </Card>

              <Card>
                <CardHeader title={t('security.vulnDistribution')} icon={PieChart} />
                <CardBody>
                  <DonutChart data={vulnDistribution} height={200} />
                  <div className="mt-4 space-y-2">
                    {vulnDistribution.map((item) => (
                      <div key={item.name} className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                          <span className="text-gray-400">{item.name}</span>
                        </div>
                        <span className="text-white font-medium">{item.value}</span>
                      </div>
                    ))}
                  </div>
                </CardBody>
              </Card>
            </div>

            {/* Compliance Overview & AI Insights Preview */}
            <div className="grid grid-cols-2 gap-6">
              <Card>
                <CardHeader
                  title={t('security.complianceOverview')}
                  icon={ShieldCheck}
                  action={
                    <button
                      onClick={() => setActiveTab('compliance')}
                      className="text-sm text-industrial-accent hover:underline flex items-center gap-1"
                    >
                      {t('common.viewAll')}
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  }
                />
                <CardBody>
                  <div className="grid grid-cols-2 gap-4">
                    {complianceFrameworks.slice(0, 4).map((framework) => (
                      <ComplianceCard key={framework.id} framework={framework} t={t} />
                    ))}
                  </div>
                </CardBody>
              </Card>

              <Card>
                <CardHeader
                  title={t('security.latestAIInsights')}
                  icon={Brain}
                  action={
                    <button
                      onClick={() => setActiveTab('aiInsights')}
                      className="text-sm text-industrial-accent hover:underline flex items-center gap-1"
                    >
                      {t('common.viewAll')}
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  }
                />
                <CardBody>
                  <div className="space-y-3">
                    {aiInsights.slice(0, 2).map((insight) => (
                      <AIInsightCard key={insight.id} insight={insight} t={t} />
                    ))}
                  </div>
                </CardBody>
              </Card>
            </div>

            {/* Recent Vulnerabilities */}
            <Card>
              <CardHeader
                title={t('security.recentVulnerabilities')}
                icon={Bug}
                action={
                  <button
                    onClick={() => setActiveTab('vulnerabilities')}
                    className="text-sm text-industrial-accent hover:underline flex items-center gap-1"
                  >
                    {t('common.viewAll')}
                    <ArrowRight className="w-4 h-4" />
                  </button>
                }
              />
              <CardBody>
                <div className="space-y-3">
                  {vulnerabilities.slice(0, 3).map((vuln) => (
                    <VulnerabilityCard key={vuln.id} vuln={vuln} t={t} />
                  ))}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {activeTab === 'compliance' && (
          <motion.div
            key="compliance"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader
                title={t('security.complianceFrameworks')}
                icon={ShieldCheck}
                action={
                  <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-industrial-accent text-white hover:bg-industrial-accent/80 transition-colors text-sm">
                    <FileText className="w-4 h-4" />
                    {t('security.generateReport')}
                  </button>
                }
              />
              <CardBody>
                <div className="grid grid-cols-2 gap-6">
                  {complianceFrameworks.map((framework) => (
                    <ComplianceCard key={framework.id} framework={framework} t={t} />
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Compliance Timeline */}
            <Card>
              <CardHeader title={t('security.auditTimeline')} icon={Clock} />
              <CardBody>
                <div className="relative">
                  <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-industrial-border" />
                  <div className="space-y-6">
                    {complianceFrameworks.map((framework, idx) => (
                      <div key={framework.id} className="flex items-start gap-4 ml-8 relative">
                        <div className="absolute -left-8 w-3 h-3 rounded-full bg-industrial-accent border-2 border-industrial-dark" />
                        <div className="flex-1 p-4 rounded-lg bg-white/5">
                          <div className="flex items-center justify-between">
                            <h4 className="font-medium text-white">{framework.name}</h4>
                            <span className="text-sm text-gray-400">
                              {t('security.nextAudit')}: {framework.nextAudit.toLocaleDateString()}
                            </span>
                          </div>
                          <p className="text-sm text-gray-400 mt-1">
                            {t('security.lastAudit')}: {framework.lastAudit.toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {activeTab === 'euRegulations' && (
          <motion.div
            key="euRegulations"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* EU Regulations Overview Cards */}
            <div className="grid grid-cols-2 gap-6">
              {/* AI Act Summary Card */}
              <Card>
                <CardBody>
                  <div className="flex items-start gap-4">
                    <div className="w-16 h-16 rounded-xl bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                      <Brain className="w-8 h-8 text-purple-400" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="text-xl font-bold text-white">AI Act</h3>
                        <span className="px-3 py-1 rounded-full text-sm bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
                          {t('security.euReg.inProgress')}
                        </span>
                      </div>
                      <p className="text-sm text-gray-400 mt-1">{t('security.euReg.aiActDesc')}</p>
                      <div className="mt-4 flex items-center gap-6">
                        <div>
                          <p className="text-2xl font-bold text-purple-400">78%</p>
                          <p className="text-xs text-gray-500">{t('security.compliance')}</p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-white">{aiSystemsInventory.length}</p>
                          <p className="text-xs text-gray-500">{t('security.euReg.aiSystems')}</p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-cyan-400">{aiSystemsInventory.filter(s => s.riskLevel === 'high').length}</p>
                          <p className="text-xs text-gray-500">{t('security.euReg.highRisk')}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardBody>
              </Card>

              {/* NIS 2 Summary Card */}
              <Card>
                <CardBody>
                  <div className="flex items-start gap-4">
                    <div className="w-16 h-16 rounded-xl bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                      <Network className="w-8 h-8 text-cyan-400" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="text-xl font-bold text-white">NIS 2</h3>
                        <span className="px-3 py-1 rounded-full text-sm bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
                          {t('security.euReg.inProgress')}
                        </span>
                      </div>
                      <p className="text-sm text-gray-400 mt-1">{t('security.euReg.nis2Desc')}</p>
                      <div className="mt-4 flex items-center gap-6">
                        <div>
                          <p className="text-2xl font-bold text-cyan-400">87%</p>
                          <p className="text-xs text-gray-500">{t('security.compliance')}</p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-white">{nis2Requirements.length}</p>
                          <p className="text-xs text-gray-500">{t('security.euReg.requirements')}</p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-green-400">{nis2Requirements.filter(r => r.status === 'compliant').length}</p>
                          <p className="text-xs text-gray-500">{t('security.euReg.compliantReq')}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </div>

            {/* AI Act Section */}
            <Card>
              <CardHeader
                title={t('security.euReg.aiActTitle')}
                icon={Brain}
                action={
                  <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 transition-colors text-sm">
                    <FileCheck className="w-4 h-4" />
                    {t('security.euReg.assessRisk')}
                  </button>
                }
              />
              <CardBody>
                {/* Risk Categories */}
                <div className="grid grid-cols-4 gap-4 mb-6">
                  <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertOctagon className="w-5 h-5 text-red-400" />
                      <span className="font-semibold text-red-400">{t('security.euReg.unacceptable')}</span>
                    </div>
                    <p className="text-2xl font-bold text-white">0</p>
                    <p className="text-xs text-gray-500">{t('security.euReg.systems')}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-orange-500/10 border border-orange-500/30">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle className="w-5 h-5 text-orange-400" />
                      <span className="font-semibold text-orange-400">{t('security.euReg.highRiskCat')}</span>
                    </div>
                    <p className="text-2xl font-bold text-white">{aiSystemsInventory.filter(s => s.riskLevel === 'high').length}</p>
                    <p className="text-xs text-gray-500">{t('security.euReg.systems')}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/30">
                    <div className="flex items-center gap-2 mb-2">
                      <Info className="w-5 h-5 text-yellow-400" />
                      <span className="font-semibold text-yellow-400">{t('security.euReg.limited')}</span>
                    </div>
                    <p className="text-2xl font-bold text-white">{aiSystemsInventory.filter(s => s.riskLevel === 'limited').length}</p>
                    <p className="text-xs text-gray-500">{t('security.euReg.systems')}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/30">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-400" />
                      <span className="font-semibold text-green-400">{t('security.euReg.minimal')}</span>
                    </div>
                    <p className="text-2xl font-bold text-white">{aiSystemsInventory.filter(s => s.riskLevel === 'minimal').length}</p>
                    <p className="text-xs text-gray-500">{t('security.euReg.systems')}</p>
                  </div>
                </div>

                {/* AI Systems Inventory */}
                <h4 className="font-semibold text-white mb-3">{t('security.euReg.aiInventory')}</h4>
                <div className="space-y-3">
                  {aiSystemsInventory.map((system) => {
                    const riskColors = {
                      minimal: 'border-green-500/30 bg-green-500/10',
                      limited: 'border-yellow-500/30 bg-yellow-500/10',
                      high: 'border-orange-500/30 bg-orange-500/10',
                      unacceptable: 'border-red-500/30 bg-red-500/10'
                    }
                    const riskTextColors = {
                      minimal: 'text-green-400',
                      limited: 'text-yellow-400',
                      high: 'text-orange-400',
                      unacceptable: 'text-red-400'
                    }
                    return (
                      <motion.div
                        key={system.id}
                        whileHover={{ x: 4 }}
                        className={`p-4 rounded-xl border ${riskColors[system.riskLevel]} flex items-center gap-4`}
                      >
                        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${riskColors[system.riskLevel]}`}>
                          <Cpu className={`w-6 h-6 ${riskTextColors[system.riskLevel]}`} />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h5 className="font-medium text-white">{system.name}</h5>
                            <span className={`px-2 py-0.5 rounded text-xs ${riskColors[system.riskLevel]} ${riskTextColors[system.riskLevel]}`}>
                              {t(`security.euReg.risk.${system.riskLevel}`)}
                            </span>
                            <span className={`px-2 py-0.5 rounded text-xs ${system.status === 'compliant' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                              {system.status === 'compliant' ? t('security.compliant') : t('security.partial')}
                            </span>
                          </div>
                          <p className="text-sm text-gray-400 mt-1">{system.description}</p>
                          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                            <span>{t('security.euReg.provider')}: {system.provider}</span>
                            <span>{t('security.euReg.useCases')}: {system.useCases.join(', ')}</span>
                          </div>
                        </div>
                        <button className="px-3 py-1.5 rounded-lg bg-white/10 text-gray-300 hover:bg-white/20 transition-colors text-sm">
                          {t('security.viewDetails')}
                        </button>
                      </motion.div>
                    )
                  })}
                </div>
              </CardBody>
            </Card>

            {/* AI Act Requirements */}
            <Card>
              <CardHeader
                title={t('security.euReg.aiActRequirements')}
                icon={FileCheck}
              />
              <CardBody>
                <div className="space-y-3">
                  {aiActRequirements.map((req) => {
                    const statusColors = {
                      compliant: 'text-green-400',
                      partial: 'text-yellow-400',
                      pending: 'text-gray-400'
                    }
                    const priorityColors = {
                      critical: 'bg-red-500/20 text-red-400',
                      high: 'bg-orange-500/20 text-orange-400',
                      medium: 'bg-yellow-500/20 text-yellow-400'
                    }
                    return (
                      <div key={req.id} className="p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            {req.status === 'compliant' ? (
                              <CheckCircle className="w-5 h-5 text-green-400" />
                            ) : req.status === 'partial' ? (
                              <Clock className="w-5 h-5 text-yellow-400" />
                            ) : (
                              <Circle className="w-5 h-5 text-gray-400" />
                            )}
                            <h5 className="font-medium text-white">{req.name}</h5>
                            <span className={`px-2 py-0.5 rounded text-xs ${priorityColors[req.priority]}`}>
                              {t(`security.euReg.priority.${req.priority}`)}
                            </span>
                          </div>
                          <span className="text-sm text-gray-400">
                            {t('security.euReg.deadline')}: {req.deadline.toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400 ml-8 mb-3">{req.description}</p>
                        <div className="ml-8">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                              <div
                                className={`h-full ${req.status === 'compliant' ? 'bg-green-500' : req.status === 'partial' ? 'bg-yellow-500' : 'bg-gray-500'}`}
                                style={{ width: `${req.progress}%` }}
                              />
                            </div>
                            <span className={`text-sm font-medium ${statusColors[req.status]}`}>{req.progress}%</span>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardBody>
            </Card>

            {/* NIS 2 Section */}
            <Card>
              <CardHeader
                title={t('security.euReg.nis2Title')}
                icon={Network}
                action={
                  <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 transition-colors text-sm">
                    <FileText className="w-4 h-4" />
                    {t('security.generateReport')}
                  </button>
                }
              />
              <CardBody>
                {/* NIS 2 Key Metrics */}
                <div className="grid grid-cols-4 gap-4 mb-6">
                  <div className="p-4 rounded-xl bg-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <Building2 className="w-5 h-5 text-cyan-400" />
                      <span className="text-sm text-gray-400">{t('security.euReg.entityType')}</span>
                    </div>
                    <p className="text-lg font-bold text-white">{t('security.euReg.essential')}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <Layers className="w-5 h-5 text-cyan-400" />
                      <span className="text-sm text-gray-400">{t('security.euReg.sector')}</span>
                    </div>
                    <p className="text-lg font-bold text-white">{t('security.euReg.manufacturing')}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className="w-5 h-5 text-cyan-400" />
                      <span className="text-sm text-gray-400">{t('security.euReg.notifyDelay')}</span>
                    </div>
                    <p className="text-lg font-bold text-white">24h / 72h</p>
                  </div>
                  <div className="p-4 rounded-xl bg-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <Users className="w-5 h-5 text-cyan-400" />
                      <span className="text-sm text-gray-400">{t('security.euReg.authority')}</span>
                    </div>
                    <p className="text-lg font-bold text-white">ANSSI</p>
                  </div>
                </div>

                {/* NIS 2 Requirements */}
                <h4 className="font-semibold text-white mb-3">{t('security.euReg.nis2Requirements')}</h4>
                <div className="space-y-3">
                  {nis2Requirements.map((req) => {
                    const statusColors = {
                      compliant: 'text-green-400',
                      partial: 'text-yellow-400',
                      pending: 'text-gray-400'
                    }
                    const priorityColors = {
                      critical: 'bg-red-500/20 text-red-400',
                      high: 'bg-orange-500/20 text-orange-400',
                      medium: 'bg-yellow-500/20 text-yellow-400'
                    }
                    return (
                      <div key={req.id} className="p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            {req.status === 'compliant' ? (
                              <CheckCircle className="w-5 h-5 text-green-400" />
                            ) : req.status === 'partial' ? (
                              <Clock className="w-5 h-5 text-yellow-400" />
                            ) : (
                              <Circle className="w-5 h-5 text-gray-400" />
                            )}
                            <h5 className="font-medium text-white">{req.name}</h5>
                            <span className={`px-2 py-0.5 rounded text-xs ${priorityColors[req.priority]}`}>
                              {t(`security.euReg.priority.${req.priority}`)}
                            </span>
                          </div>
                          <span className="text-sm text-gray-400">
                            {t('security.euReg.deadline')}: {req.deadline.toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400 ml-8 mb-3">{req.description}</p>
                        <div className="ml-8">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                              <div
                                className={`h-full ${req.status === 'compliant' ? 'bg-green-500' : req.status === 'partial' ? 'bg-yellow-500' : 'bg-gray-500'}`}
                                style={{ width: `${req.progress}%` }}
                              />
                            </div>
                            <span className={`text-sm font-medium ${statusColors[req.status]}`}>{req.progress}%</span>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardBody>
            </Card>

            {/* NIS 2 Incidents */}
            <Card>
              <CardHeader
                title={t('security.euReg.nis2Incidents')}
                icon={AlertTriangle}
              />
              <CardBody>
                <div className="space-y-3">
                  {nis2Incidents.map((incident) => {
                    const severityColors = {
                      significant: 'border-orange-500/30 bg-orange-500/10',
                      minor: 'border-yellow-500/30 bg-yellow-500/10'
                    }
                    const impactColors = {
                      low: 'text-green-400',
                      medium: 'text-yellow-400',
                      high: 'text-red-400'
                    }
                    return (
                      <motion.div
                        key={incident.id}
                        whileHover={{ x: 4 }}
                        className={`p-4 rounded-xl border ${severityColors[incident.type]} flex items-center gap-4`}
                      >
                        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${severityColors[incident.type]}`}>
                          <AlertTriangle className={`w-6 h-6 ${incident.type === 'significant' ? 'text-orange-400' : 'text-yellow-400'}`} />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h5 className="font-medium text-white">{incident.title}</h5>
                            <span className={`px-2 py-0.5 rounded text-xs ${incident.status === 'resolved' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                              {incident.status === 'resolved' ? t('security.euReg.resolved') : t('security.euReg.active')}
                            </span>
                            {incident.reportedToAuthority && (
                              <span className="px-2 py-0.5 rounded text-xs bg-blue-500/20 text-blue-400">
                                {t('security.euReg.reportedToANSSI')}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-400 mt-1">{incident.description}</p>
                          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                            <span>{t('security.euReg.detection')}: {formatTime(incident.detectionTime)}</span>
                            <span>{t('security.euReg.resolution')}: {formatTime(incident.resolutionTime)}</span>
                            <span className={impactColors[incident.impact]}>{t('security.euReg.impact')}: {t(`security.euReg.impactLevel.${incident.impact}`)}</span>
                          </div>
                        </div>
                      </motion.div>
                    )
                  })}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {activeTab === 'vulnerabilities' && (
          <motion.div
            key="vulnerabilities"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader
                title={t('security.allVulnerabilities')}
                icon={Bug}
                action={
                  <div className="flex gap-2">
                    <select className="px-3 py-1.5 rounded-lg bg-industrial-card border border-industrial-border text-sm text-white">
                      <option>{t('security.allSeverities')}</option>
                      <option>{t('security.critical')}</option>
                      <option>{t('security.high')}</option>
                      <option>{t('security.medium')}</option>
                      <option>{t('security.low')}</option>
                    </select>
                    <select className="px-3 py-1.5 rounded-lg bg-industrial-card border border-industrial-border text-sm text-white">
                      <option>{t('security.allStatuses')}</option>
                      <option>{t('security.statusOpen')}</option>
                      <option>{t('security.statusInProgress')}</option>
                      <option>{t('security.statusPatched')}</option>
                    </select>
                  </div>
                }
              />
              <CardBody>
                <div className="space-y-3">
                  {vulnerabilities.map((vuln) => (
                    <VulnerabilityCard key={vuln.id} vuln={vuln} t={t} />
                  ))}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {activeTab === 'aiInsights' && (
          <motion.div
            key="aiInsights"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader
                title={t('security.aiSecurityInsights')}
                icon={Brain}
                action={
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-400">{t('security.poweredByAI')}</span>
                    <Sparkles className="w-4 h-4 text-purple-400" />
                  </div>
                }
              />
              <CardBody>
                <div className="space-y-4">
                  {aiInsights.map((insight) => (
                    <AIInsightCard key={insight.id} insight={insight} t={t} />
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* AI Capabilities */}
            <div className="grid grid-cols-3 gap-4">
              <Card>
                <CardBody>
                  <div className="text-center p-4">
                    <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center mx-auto mb-3">
                      <AlertTriangle className="w-6 h-6 text-purple-400" />
                    </div>
                    <h4 className="font-semibold text-white mb-1">{t('security.aiCapabilities.anomalyDetection')}</h4>
                    <p className="text-sm text-gray-400">{t('security.aiCapabilities.anomalyDesc')}</p>
                  </div>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <div className="text-center p-4">
                    <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center mx-auto mb-3">
                      <Lightbulb className="w-6 h-6 text-blue-400" />
                    </div>
                    <h4 className="font-semibold text-white mb-1">{t('security.aiCapabilities.predictive')}</h4>
                    <p className="text-sm text-gray-400">{t('security.aiCapabilities.predictiveDesc')}</p>
                  </div>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <div className="text-center p-4">
                    <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center mx-auto mb-3">
                      <Sparkles className="w-6 h-6 text-green-400" />
                    </div>
                    <h4 className="font-semibold text-white mb-1">{t('security.aiCapabilities.optimization')}</h4>
                    <p className="text-sm text-gray-400">{t('security.aiCapabilities.optimizationDesc')}</p>
                  </div>
                </CardBody>
              </Card>
            </div>
          </motion.div>
        )}

        {activeTab === 'audit' && (
          <motion.div
            key="audit"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader
                title={t('security.auditTrail')}
                icon={History}
                action={
                  <div className="flex gap-2">
                    <select className="px-3 py-1.5 rounded-lg bg-industrial-card border border-industrial-border text-sm text-white">
                      <option>{t('observability.last24h')}</option>
                      <option>{t('observability.last7d')}</option>
                      <option>{t('observability.last30d')}</option>
                    </select>
                    <button className="px-3 py-1.5 rounded-lg bg-white/10 text-gray-300 hover:bg-white/20 transition-colors text-sm">
                      {t('common.export')}
                    </button>
                  </div>
                }
              />
              <CardBody>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-industrial-border">
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">{t('security.auditId')}</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">{t('security.action')}</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">{t('security.user')}</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">{t('security.resource')}</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">{t('security.ipAddress')}</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">{t('observability.status')}</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">{t('security.timestamp')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {auditLogs.map((log) => (
                        <tr key={log.id} className="border-b border-industrial-border/50 hover:bg-white/5">
                          <td className="py-3 px-4 text-sm font-mono text-gray-300">{log.id}</td>
                          <td className="py-3 px-4">
                            <span className="px-2 py-1 rounded bg-white/10 text-xs font-mono text-white">
                              {log.action}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-sm text-white">{log.user}</td>
                          <td className="py-3 px-4 text-sm text-gray-400">{log.resource}</td>
                          <td className="py-3 px-4 text-sm font-mono text-gray-400">{log.ip}</td>
                          <td className="py-3 px-4">
                            <StatusBadge
                              status={log.status === 'success' ? 'healthy' : 'down'}
                              label={log.status}
                              size="sm"
                            />
                          </td>
                          <td className="py-3 px-4 text-sm text-gray-400">{formatTime(log.timestamp)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {activeTab === 'policies' && (
          <motion.div
            key="policies"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader
                title={t('security.securityPolicies')}
                icon={FileText}
                action={
                  <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-industrial-accent text-white hover:bg-industrial-accent/80 transition-colors text-sm">
                    <Settings className="w-4 h-4" />
                    {t('security.managePolicies')}
                  </button>
                }
              />
              <CardBody>
                <div className="space-y-3">
                  {securityPolicies.map((policy) => (
                    <PolicyCard key={policy.id} policy={policy} t={t} />
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Policy Compliance Overview */}
            <div className="grid grid-cols-3 gap-4">
              <Card>
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16">
                      <SemiCircleGauge
                        value={securityPolicies.reduce((acc, p) => acc + p.compliance, 0) / securityPolicies.length}
                        max={100}
                        color="#22c55e"
                      />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">{t('security.avgCompliance')}</p>
                      <p className="text-2xl font-bold text-white">
                        {Math.round(securityPolicies.reduce((acc, p) => acc + p.compliance, 0) / securityPolicies.length)}%
                      </p>
                    </div>
                  </div>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center">
                      <ShieldCheck className="w-6 h-6 text-green-400" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">{t('security.enforced')}</p>
                      <p className="text-2xl font-bold text-white">
                        {securityPolicies.filter(p => p.status === 'enforced').length}
                      </p>
                    </div>
                  </div>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-red-500/20 flex items-center justify-center">
                      <AlertTriangle className="w-6 h-6 text-red-400" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">{t('security.totalViolations')}</p>
                      <p className="text-2xl font-bold text-white">
                        {securityPolicies.reduce((acc, p) => acc + p.violations, 0)}
                      </p>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </div>
          </motion.div>
        )}

        {activeTab === 'video' && (
          <motion.div
            key="video"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Video Stats */}
            <div className="grid grid-cols-4 gap-4">
              <Card>
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center">
                      <Camera className="w-6 h-6 text-green-400" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">{t('security.video.online')}</p>
                      <p className="text-2xl font-bold text-white">
                        {securityVideoFeeds.filter(f => f.status === 'online').length}
                      </p>
                    </div>
                  </div>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-red-500/20 flex items-center justify-center">
                      <XCircle className="w-6 h-6 text-red-400" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">{t('security.video.offline')}</p>
                      <p className="text-2xl font-bold text-white">
                        {securityVideoFeeds.filter(f => f.status === 'offline').length}
                      </p>
                    </div>
                  </div>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-red-500/20 flex items-center justify-center">
                      <Circle className="w-6 h-6 text-red-400 fill-current animate-pulse" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">{t('security.video.recording')}</p>
                      <p className="text-2xl font-bold text-white">
                        {securityVideoFeeds.filter(f => f.recording).length}
                      </p>
                    </div>
                  </div>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-yellow-500/20 flex items-center justify-center">
                      <AlertTriangle className="w-6 h-6 text-yellow-400" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">{t('security.video.totalAlerts')}</p>
                      <p className="text-2xl font-bold text-white">
                        {securityVideoFeeds.reduce((acc, f) => acc + f.alerts, 0)}
                      </p>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </div>

            {/* Live Camera Feeds */}
            <Card>
              <CardHeader
                title={t('security.video.liveFeeds')}
                icon={Video}
                action={
                  <div className="flex gap-2">
                    <select className="px-3 py-1.5 rounded-lg bg-industrial-card border border-industrial-border text-sm text-white">
                      <option>{t('security.video.allCameras')}</option>
                      <option>{t('security.video.onlineOnly')}</option>
                      <option>{t('security.video.withAlerts')}</option>
                    </select>
                    <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-industrial-accent text-white hover:bg-industrial-accent/80 transition-colors text-sm">
                      <Maximize2 className="w-4 h-4" />
                      {t('security.video.fullscreen')}
                    </button>
                  </div>
                }
              />
              <CardBody>
                <div className="grid grid-cols-3 gap-4">
                  {securityVideoFeeds.map((feed) => (
                    <VideoFeedCard key={feed.id} feed={feed} t={t} formatTime={formatTime} />
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Recent Events */}
            <Card>
              <CardHeader
                title={t('security.video.recentEvents')}
                icon={Activity}
                action={
                  <div className="flex gap-2">
                    <select className="px-3 py-1.5 rounded-lg bg-industrial-card border border-industrial-border text-sm text-white">
                      <option>{t('observability.last24h')}</option>
                      <option>{t('observability.last7d')}</option>
                      <option>{t('observability.last30d')}</option>
                    </select>
                    <button className="px-3 py-1.5 rounded-lg bg-white/10 text-gray-300 hover:bg-white/20 transition-colors text-sm">
                      {t('common.export')}
                    </button>
                  </div>
                }
              />
              <CardBody>
                <div className="space-y-3">
                  {videoEvents.map((event) => (
                    <VideoEventCard key={event.id} event={event} t={t} formatTime={formatTime} />
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Video Storage Info */}
            <div className="grid grid-cols-3 gap-4">
              <Card>
                <CardBody>
                  <div className="text-center p-4">
                    <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center mx-auto mb-3">
                      <Database className="w-6 h-6 text-blue-400" />
                    </div>
                    <h4 className="font-semibold text-white mb-1">{t('security.video.storage')}</h4>
                    <p className="text-2xl font-bold text-industrial-accent">2.4 TB</p>
                    <p className="text-sm text-gray-400">{t('security.video.of')} 5 TB</p>
                  </div>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <div className="text-center p-4">
                    <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center mx-auto mb-3">
                      <Calendar className="w-6 h-6 text-purple-400" />
                    </div>
                    <h4 className="font-semibold text-white mb-1">{t('security.video.retention')}</h4>
                    <p className="text-2xl font-bold text-industrial-accent">30</p>
                    <p className="text-sm text-gray-400">{t('security.video.days')}</p>
                  </div>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <div className="text-center p-4">
                    <div className="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center mx-auto mb-3">
                      <Activity className="w-6 h-6 text-cyan-400" />
                    </div>
                    <h4 className="font-semibold text-white mb-1">{t('security.video.bandwidth')}</h4>
                    <p className="text-2xl font-bold text-industrial-accent">156</p>
                    <p className="text-sm text-gray-400">Mbps</p>
                  </div>
                </CardBody>
              </Card>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default SecurityComplianceView
