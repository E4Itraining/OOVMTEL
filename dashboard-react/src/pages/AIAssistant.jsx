import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  Activity,
  AlertTriangle,
  ArrowUp,
  BarChart3,
  Bot,
  Brain,
  Building2,
  CheckCircle2,
  ChevronRight,
  Clock,
  Cpu,
  DollarSign,
  Eye,
  FileText,
  Gauge,
  HelpCircle,
  Lightbulb,
  Loader2,
  MessageSquare,
  Mic,
  Network,
  RefreshCw,
  Scale,
  Send,
  Server,
  Settings,
  Shield,
  Sparkles,
  Target,
  TrendingUp,
  User,
  Wrench,
  X,
  Zap
} from 'lucide-react'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody } from '../components/ui/Card'
import { PERSONAS, PERSONA_JOURNEYS } from './WelcomePage'

// Enhanced persona-specific suggestions
const PERSONA_SUGGESTIONS = {
  [PERSONAS.DIRIGEANT]: [
    { icon: TrendingUp, text: 'Quel est l\'impact financier des incidents du mois ?' },
    { icon: Target, text: 'Quels sont les risques stratégiques prioritaires ?' },
    { icon: BarChart3, text: 'Génère un rapport exécutif de la semaine' },
    { icon: DollarSign, text: 'Quelles économies sont réalisables ce trimestre ?' }
  ],
  [PERSONAS.DSI]: [
    { icon: Server, text: 'Analyse la dette technique actuelle' },
    { icon: Activity, text: 'État de santé de l\'infrastructure IT' },
    { icon: Zap, text: 'Quelles optimisations de performance recommandes-tu ?' },
    { icon: Cpu, text: 'Évalue la capacité de scalabilité du SI' }
  ],
  [PERSONAS.RSSI]: [
    { icon: Shield, text: 'Analyse les menaces détectées cette semaine' },
    { icon: AlertTriangle, text: 'Quelles vulnérabilités sont prioritaires ?' },
    { icon: Eye, text: 'Vérifie la conformité aux exigences NIS 2' },
    { icon: Target, text: 'Évalue notre posture de sécurité globale' }
  ],
  [PERSONAS.RSI]: [
    { icon: Server, text: 'État des services et disponibilité' },
    { icon: Wrench, text: 'Quels systèmes nécessitent une maintenance ?' },
    { icon: Activity, text: 'Analyse les incidents récurrents' },
    { icon: RefreshCw, text: 'Planification des mises à jour à prévoir' }
  ],
  [PERSONAS.DPO_JURISTE]: [
    { icon: Scale, text: 'État de conformité RGPD actuel' },
    { icon: FileText, text: 'Vérifie les exigences de l\'AI Act' },
    { icon: Shield, text: 'Analyse des risques data protection' },
    { icon: Clock, text: 'Échéances réglementaires à venir' }
  ],
  [PERSONAS.OPERATIONS_MANAGER]: [
    { icon: Gauge, text: 'Quel est l\'OEE actuel des lignes de production ?' },
    { icon: AlertTriangle, text: 'Alarmes critiques affectant la production' },
    { icon: Wrench, text: 'Équipements nécessitant attention' },
    { icon: Clock, text: 'Résumé performance production du jour' }
  ],
  [PERSONAS.DEVOPS_ENGINEER]: [
    { icon: Server, text: 'Santé de l\'infrastructure et des services' },
    { icon: Network, text: 'Analyse du lag Kafka et des pipelines' },
    { icon: Zap, text: 'Origine des pics de latence récents' },
    { icon: Activity, text: 'Status des pipelines OTEL' }
  ],
  [PERSONAS.DATA_ANALYST]: [
    { icon: Activity, text: 'Taux d\'ingestion des données' },
    { icon: BarChart3, text: 'Détecte les anomalies dans les métriques' },
    { icon: FileText, text: 'Exporte les données de production' },
    { icon: Lightbulb, text: 'Identifie les patterns de pannes équipement' }
  ]
}

// Default suggestions for unknown/no persona
const DEFAULT_SUGGESTIONS = [
  { icon: Activity, text: 'Vue d\'ensemble santé système' },
  { icon: Gauge, text: 'Quel est l\'OEE actuel ?' },
  { icon: AlertTriangle, text: 'Y a-t-il des alertes actives ?' },
  { icon: HelpCircle, text: 'Comment peux-tu m\'aider ?' }
]

// Persona-specific greeting messages
const PERSONA_GREETINGS = {
  [PERSONAS.DIRIGEANT]: 'Je suis votre assistant stratégique. Je peux analyser les impacts financiers, évaluer les risques et générer des rapports exécutifs.',
  [PERSONAS.DSI]: 'Je suis votre conseiller IT. Je peux analyser l\'infrastructure, évaluer la dette technique et recommander des optimisations.',
  [PERSONAS.RSSI]: 'Je suis votre analyste sécurité. Je surveille les menaces, évalue les vulnérabilités et vérifie la conformité.',
  [PERSONAS.RSI]: 'Je suis votre assistant opérationnel. Je surveille les systèmes, planifie les maintenances et analyse les incidents.',
  [PERSONAS.DPO_JURISTE]: 'Je suis votre conseiller conformité. Je vérifie le RGPD, l\'AI Act, NIS 2 et les exigences réglementaires.',
  [PERSONAS.OPERATIONS_MANAGER]: 'Je suis votre assistant production. Je surveille l\'OEE, les équipements et optimise les performances.',
  [PERSONAS.DEVOPS_ENGINEER]: 'Je suis votre copilote DevOps. Je surveille l\'infrastructure, les pipelines et diagnostique les problèmes.',
  [PERSONAS.DATA_ANALYST]: 'Je suis votre assistant analytics. Je détecte les patterns, analyse les métriques et identifie les anomalies.'
}

// Enhanced AI responses based on context
const generateAIResponse = (query, persona) => {
  const lowerQuery = query.toLowerCase()

  // Context-aware responses
  if (lowerQuery.includes('oee') || lowerQuery.includes('production') || lowerQuery.includes('performance')) {
    return {
      text: `## Analyse OEE en temps réel

**OEE Global: 83.4%**

| Composante | Actuel | Objectif | Statut |
|------------|--------|----------|--------|
| Disponibilité | 95.2% | 95% | Conforme |
| Performance | 88.5% | 90% | Sous objectif |
| Qualité | 99.1% | 98% | Excellent |

### Insights IA
- Performance 1.5% sous objectif due aux micro-arrêts Ligne 2
- Qualité améliorée de 0.3% depuis hier
- Disponibilité récupérée après maintenance matinale

### Préconisations
1. Investiguer les micro-arrêts Ligne 2 (pattern détecté toutes les 4h)
2. Maintenir les protocoles qualité actuels
3. Planifier maintenance préventive Ligne 4`,
      actions: [
        { label: 'Voir détails OEE', route: '/business-kpi' },
        { label: 'Analyser Ligne 2', route: '/details/ligne-2' }
      ]
    }
  }

  if (lowerQuery.includes('sécurité') || lowerQuery.includes('security') || lowerQuery.includes('menace') || lowerQuery.includes('vulnérabilité')) {
    return {
      text: `## Analyse Sécurité

### Posture de Sécurité Globale
**Score: 78/100** (Amélioration +5 pts ce mois)

### Alertes Actives
| Sévérité | Count | Top Issue |
|----------|-------|-----------|
| Critique | 3 | CVE-2024-0001 Log4j |
| Haute | 7 | Tentatives bruteforce SSH |
| Moyenne | 12 | Certificats à renouveler |

### Insights IA
- 3 CVE critiques détectées nécessitant action immédiate
- 847 tentatives d'intrusion bloquées (24h)
- Conformité NIS 2: 68% (échéance dans 45 jours)

### Préconisations Prioritaires
1. **URGENT**: Patcher Log4j vers 2.17.1+
2. Activer 2FA sur tous les accès privilégiés
3. Renouveler les certificats expirant sous 30j`,
      actions: [
        { label: 'Voir vulnérabilités', route: '/security#vulnerabilities' },
        { label: 'Conformité NIS 2', route: '/security#euRegulations' }
      ]
    }
  }

  if (lowerQuery.includes('conformité') || lowerQuery.includes('compliance') || lowerQuery.includes('rgpd') || lowerQuery.includes('nis')) {
    return {
      text: `## État de Conformité

### Cadres Réglementaires
| Framework | Score | Statut |
|-----------|-------|--------|
| ISO 27001 | 92% | Conforme |
| RGPD | 88% | Conforme |
| NIS 2 | 68% | En cours |
| AI Act | 45% | À améliorer |
| SOC 2 | 85% | Conforme |

### Points d'Attention NIS 2
- Plan de réponse incident: Non formalisé
- Notification ANSSI 24h: Non implémenté
- Gestion accès privilégiés: Partiel

### Prochains Audits
- ISO 27001: 15 février 2025
- SOC 2 Type II: 1er mars 2025

### Préconisations
1. Formaliser le plan de réponse aux incidents
2. Implémenter la notification automatique ANSSI
3. Renforcer la gestion PAM`,
      actions: [
        { label: 'Détail conformité', route: '/security#compliance' },
        { label: 'Régulations EU', route: '/security#euRegulations' }
      ]
    }
  }

  if (lowerQuery.includes('infrastructure') || lowerQuery.includes('service') || lowerQuery.includes('santé')) {
    return {
      text: `## Santé Infrastructure

### Services Backend
| Service | Status | Latence | Notes |
|---------|--------|---------|-------|
| VictoriaMetrics | Healthy | 12ms | - |
| OpenSearch | Healthy | 45ms | - |
| Kafka | Dégradé | 89ms | Consumer lag détecté |
| OTEL Collector | Healthy | 5ms | - |

### Métriques Clés
- CPU moyen: 45% | Memory: 62% | Disk: 71%
- Ingestion: 125K métriques/s
- Logs: 8.5K/s | Traces: 2.1K/s

### Insights IA
- Kafka consumer lag en augmentation (+1,250 messages)
- Prédiction: saturation disque dans 12 jours
- Pattern: pics de charge entre 9h-11h

### Préconisations
1. Augmenter les consommateurs Kafka
2. Planifier extension stockage
3. Implémenter cache Redis`,
      actions: [
        { label: 'Vue technique', route: '/technical' },
        { label: 'Observabilité', route: '/observability' }
      ]
    }
  }

  if (lowerQuery.includes('impact') || lowerQuery.includes('préconisation') || lowerQuery.includes('recommandation')) {
    return {
      text: `## Analyse d'Impact & Préconisations

### Résumé Exécutif
- **12 impacts** identifiés dont **3 critiques**
- **45K€** d'économies potentielles annuelles
- **32%** de réduction de risque réalisable

### Top 3 Actions Prioritaires

#### 1. Sécurité - Critique
Patcher 3 CVE critiques (Log4j, OpenSSL)
- Impact: Réduction risque cyber 85%
- Délai: Immédiat - 24h

#### 2. Infrastructure - Haute
Rightsizing instances cloud
- Impact: -25% coûts infrastructure
- Délai: 2-4 semaines

#### 3. Performance - Haute
Optimisation latence API
- Impact: P95 de 340ms → 120ms
- Délai: 1-2 semaines

### ROI Estimé
Économies annuelles: **180K€** + évitement incidents`,
      actions: [
        { label: 'Voir tous les impacts', route: '/impact-analysis' },
        { label: 'Créer plan d\'action', route: '/observability#runbooks' }
      ]
    }
  }

  // Default contextual response
  return {
    text: `Je comprends votre question sur "${query}".

Basé sur les données système actuelles, je peux vous aider avec:

1. **Métriques Production** - OEE, disponibilité, performance, qualité
2. **Santé Infrastructure** - Services, latence, throughput
3. **Alertes & Incidents** - Alarmes actives, recommandations
4. **KPIs Business** - Impact financier, tendances, prévisions
5. **Sécurité & Conformité** - Vulnérabilités, audits, réglementations

Que souhaitez-vous approfondir ?`,
    actions: [
      { label: 'Impact & Préconisations', route: '/impact-analysis' },
      { label: 'Vue d\'ensemble', route: '/command-center' }
    ]
  }
}

function SuggestionChip({ suggestion, onClick }) {
  const Icon = suggestion.icon

  return (
    <motion.button
      onClick={() => onClick(suggestion.text)}
      className="flex items-center gap-2 px-4 py-2 rounded-full bg-industrial-card/50 border border-industrial-border hover:border-cyan-500/50 hover:bg-industrial-card transition-all text-sm text-gray-300 hover:text-white"
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Icon className="w-4 h-4 text-cyan-400" />
      <span className="truncate max-w-[200px]">{suggestion.text}</span>
    </motion.button>
  )
}

function MessageBubble({ message, isUser, onActionClick }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ${
        isUser
          ? 'bg-purple-500/20'
          : 'bg-gradient-to-br from-cyan-500 via-blue-500 to-purple-600'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-purple-400" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>
      <div className={`flex-1 max-w-[80%] ${isUser ? 'text-right' : ''}`}>
        <div className={`inline-block p-4 rounded-2xl ${
          isUser
            ? 'bg-purple-500/20 border border-purple-500/30 text-white'
            : 'bg-industrial-card border border-industrial-border text-gray-200'
        }`}>
          {isUser ? (
            <p className="text-sm">{message.content}</p>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none">
              <div className="text-sm whitespace-pre-wrap">{message.content}</div>
              {message.actions && message.actions.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-industrial-border">
                  {message.actions.map((action, idx) => (
                    <button
                      key={idx}
                      onClick={() => onActionClick(action.route)}
                      className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 transition-colors text-xs"
                    >
                      {action.label}
                      <ChevronRight className="w-3 h-3" />
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
        <p className="text-xs text-gray-500 mt-1 px-2">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </motion.div>
  )
}

function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex gap-3"
    >
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-500 to-purple-600 flex items-center justify-center">
        <Bot className="w-5 h-5 text-white" />
      </div>
      <div className="flex items-center gap-1 px-4 py-3 rounded-2xl bg-industrial-card border border-industrial-border">
        <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </motion.div>
  )
}

function PersonaBadge({ persona }) {
  const personaConfig = {
    [PERSONAS.DIRIGEANT]: { icon: Building2, label: 'Dirigeant', color: 'indigo' },
    [PERSONAS.DSI]: { icon: Cpu, label: 'DSI', color: 'blue' },
    [PERSONAS.RSSI]: { icon: Shield, label: 'RSSI', color: 'red' },
    [PERSONAS.RSI]: { icon: Server, label: 'RSI', color: 'cyan' },
    [PERSONAS.DPO_JURISTE]: { icon: Scale, label: 'DPO/Juriste', color: 'emerald' },
    [PERSONAS.OPERATIONS_MANAGER]: { icon: Activity, label: 'Opérations', color: 'purple' },
    [PERSONAS.DEVOPS_ENGINEER]: { icon: Network, label: 'DevOps', color: 'amber' },
    [PERSONAS.DATA_ANALYST]: { icon: BarChart3, label: 'Data Analyst', color: 'rose' }
  }

  const config = personaConfig[persona] || { icon: User, label: 'Utilisateur', color: 'gray' }
  const Icon = config.icon

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg bg-${config.color}-500/10 border border-${config.color}-500/30`}>
      <Icon className={`w-4 h-4 text-${config.color}-400`} />
      <span className={`text-xs font-medium text-${config.color}-400`}>{config.label}</span>
    </div>
  )
}

function JourneyProgress() {
  const navigate = useNavigate()
  const storedJourney = localStorage.getItem('personaJourney')
  const currentStageIdx = parseInt(localStorage.getItem('currentJourneyStage') || '0')

  if (!storedJourney) return null

  const journey = JSON.parse(storedJourney)

  return (
    <Card className="bg-industrial-card/50 border-industrial-border mb-4">
      <CardBody className="p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-medium text-white">Votre parcours</span>
          </div>
          <div className="flex items-center gap-1">
            {journey.stages.map((stage, idx) => (
              <button
                key={stage.id}
                onClick={() => navigate(stage.route)}
                className={`w-2 h-2 rounded-full transition-colors ${
                  idx <= currentStageIdx
                    ? 'bg-cyan-400'
                    : 'bg-industrial-border'
                }`}
                title={stage.label}
              />
            ))}
          </div>
        </div>
      </CardBody>
    </Card>
  )
}

function AIAssistant() {
  const { t } = useI18n()
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Get stored persona
  const storedPersona = localStorage.getItem('selectedPersona')
  const suggestions = PERSONA_SUGGESTIONS[storedPersona] || DEFAULT_SUGGESTIONS
  const greeting = PERSONA_GREETINGS[storedPersona] || 'Je suis votre assistant IA. Je peux analyser vos données et répondre à vos questions.'

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!inputValue.trim()) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    // Simulate AI response delay
    setTimeout(() => {
      const response = generateAIResponse(userMessage.content, storedPersona)
      const aiResponse = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.text,
        actions: response.actions,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiResponse])
      setIsTyping(false)
    }, 1500)
  }

  const handleSuggestionClick = (text) => {
    setInputValue(text)
    inputRef.current?.focus()
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleActionClick = (route) => {
    navigate(route)
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              {t('aiAssistant.title')}
              <Brain className="w-5 h-5 text-cyan-400" />
            </h1>
            <p className="text-sm text-gray-400">
              {t('aiAssistant.subtitle')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {storedPersona && <PersonaBadge persona={storedPersona} />}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-500/10 border border-green-500/30">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-xs text-green-400">{t('aiAssistant.online')}</span>
          </div>
        </div>
      </div>

      {/* Journey Progress */}
      <JourneyProgress />

      {/* Chat Area */}
      <div className="flex-1 rounded-xl bg-industrial-dark/50 border border-industrial-border overflow-hidden flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-cyan-500/20 via-blue-500/20 to-purple-500/20 flex items-center justify-center mb-6">
                <MessageSquare className="w-10 h-10 text-cyan-400" />
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">
                {t('aiAssistant.welcome')}
              </h2>
              <p className="text-gray-400 max-w-md mb-2">
                {greeting}
              </p>
              <p className="text-gray-500 max-w-md mb-8 text-sm">
                {t('aiAssistant.welcomeDescription')}
              </p>

              {/* Suggestions */}
              <div className="w-full max-w-2xl">
                <p className="text-sm text-gray-500 mb-3">{t('aiAssistant.suggestions')}</p>
                <div className="flex flex-wrap justify-center gap-2">
                  {suggestions.map((suggestion, idx) => (
                    <SuggestionChip
                      key={idx}
                      suggestion={suggestion}
                      onClick={handleSuggestionClick}
                    />
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  isUser={message.type === 'user'}
                  onActionClick={handleActionClick}
                />
              ))}
              {isTyping && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Quick Suggestions (when in conversation) */}
        {messages.length > 0 && (
          <div className="px-4 py-2 border-t border-industrial-border/50">
            <div className="flex items-center gap-2 overflow-x-auto pb-2">
              <span className="text-xs text-gray-500 flex-shrink-0">{t('aiAssistant.quickActions')}:</span>
              {suggestions.slice(0, 3).map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSuggestionClick(suggestion.text)}
                  className="flex-shrink-0 px-3 py-1 rounded-full bg-industrial-border/50 text-xs text-gray-400 hover:text-white hover:bg-industrial-border transition-colors"
                >
                  {suggestion.text.substring(0, 30)}...
                </button>
              ))}
              <button
                onClick={() => navigate('/impact-analysis')}
                className="flex-shrink-0 flex items-center gap-1 px-3 py-1 rounded-full bg-cyan-500/20 text-xs text-cyan-400 hover:bg-cyan-500/30 transition-colors"
              >
                <Target className="w-3 h-3" />
                Impact & Préconisations
              </button>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="p-4 border-t border-industrial-border">
          <div className="flex items-end gap-3">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={t('aiAssistant.placeholder')}
                className="w-full px-4 py-3 pr-12 rounded-xl bg-industrial-darker border border-industrial-border focus:border-cyan-500/50 focus:outline-none resize-none text-white placeholder-gray-500 min-h-[48px] max-h-[120px]"
                rows={1}
              />
              <button
                className="absolute right-2 bottom-2 p-2 text-gray-400 hover:text-cyan-400 transition-colors"
                title="Saisie vocale (bientôt disponible)"
              >
                <Mic className="w-5 h-5" />
              </button>
            </div>
            <motion.button
              onClick={handleSend}
              disabled={!inputValue.trim() || isTyping}
              className={`p-3 rounded-xl transition-all ${
                inputValue.trim() && !isTyping
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:from-cyan-400 hover:to-blue-400'
                  : 'bg-industrial-border text-gray-500 cursor-not-allowed'
              }`}
              whileHover={inputValue.trim() && !isTyping ? { scale: 1.05 } : undefined}
              whileTap={inputValue.trim() && !isTyping ? { scale: 0.95 } : undefined}
            >
              {isTyping ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </motion.button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AIAssistant
