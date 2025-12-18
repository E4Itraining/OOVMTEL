import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Activity,
  AlertTriangle,
  ArrowUp,
  BarChart3,
  Bot,
  CheckCircle2,
  ChevronRight,
  Clock,
  Factory,
  FileText,
  Gauge,
  HelpCircle,
  Lightbulb,
  Loader2,
  MessageSquare,
  Mic,
  RefreshCw,
  Send,
  Server,
  Shield,
  Sparkles,
  User,
  Wrench,
  X,
  Zap
} from 'lucide-react'
import { useI18n } from '../i18n'
import { Card, CardHeader, CardBody } from '../components/ui/Card'

// Persona-specific suggestions
const PERSONA_SUGGESTIONS = {
  operations_manager: [
    { icon: Gauge, text: 'What is the current OEE across all production lines?' },
    { icon: AlertTriangle, text: 'Show me critical alarms affecting production' },
    { icon: Factory, text: 'Which equipment needs immediate attention?' },
    { icon: Clock, text: 'Summarize today\'s production performance' }
  ],
  plant_director: [
    { icon: BarChart3, text: 'Show me financial impact of current downtime' },
    { icon: Activity, text: 'Compare OEE trends across this week' },
    { icon: FileText, text: 'Generate executive summary for today' },
    { icon: Lightbulb, text: 'What optimizations do you recommend?' }
  ],
  devops_engineer: [
    { icon: Server, text: 'Show infrastructure health status' },
    { icon: Activity, text: 'What\'s causing Kafka consumer lag?' },
    { icon: Zap, text: 'Analyze latency spikes in the last hour' },
    { icon: RefreshCw, text: 'Check OTEL collector pipeline status' }
  ],
  security_analyst: [
    { icon: Shield, text: 'Show recent security alerts' },
    { icon: AlertTriangle, text: 'Any anomalies detected in system access?' },
    { icon: FileText, text: 'Generate compliance status report' },
    { icon: Wrench, text: 'List open vulnerabilities by severity' }
  ],
  compliance_officer: [
    { icon: FileText, text: 'Show current compliance status' },
    { icon: CheckCircle2, text: 'Which controls need attention?' },
    { icon: Clock, text: 'When is the next audit scheduled?' },
    { icon: AlertTriangle, text: 'List policy violations this month' }
  ],
  data_analyst: [
    { icon: Activity, text: 'Show data ingestion rates' },
    { icon: BarChart3, text: 'Analyze metric trends for anomalies' },
    { icon: FileText, text: 'Export production data for analysis' },
    { icon: Lightbulb, text: 'Identify patterns in equipment failures' }
  ]
}

// Default suggestions for unknown/no persona
const DEFAULT_SUGGESTIONS = [
  { icon: Activity, text: 'Show system health overview' },
  { icon: Gauge, text: 'What is the current OEE?' },
  { icon: AlertTriangle, text: 'Are there any active alerts?' },
  { icon: HelpCircle, text: 'How can you help me?' }
]

// Sample conversation responses
const SAMPLE_RESPONSES = {
  oee: `Based on real-time data, here's the current OEE analysis:

**Overall OEE: 83.4%**

| Component | Current | Target | Status |
|-----------|---------|--------|--------|
| Availability | 95.2% | 95% | On Target |
| Performance | 88.5% | 90% | Below Target |
| Quality | 99.1% | 98% | Above Target |

**Key Insights:**
- Performance is 1.5% below target due to micro-stoppages on Line 2
- Quality has improved by 0.3% since yesterday
- Availability recovered after morning maintenance

**Recommended Actions:**
1. Investigate Line 2 micro-stoppages
2. Continue current quality protocols
3. Schedule preventive maintenance for Line 4`,

  health: `## System Health Status

All core services are operational with the following status:

| Service | Status | Latency | Notes |
|---------|--------|---------|-------|
| VictoriaMetrics | Healthy | 12ms | - |
| OpenSearch | Healthy | 45ms | - |
| Kafka | Degraded | 89ms | Consumer lag detected |
| OTEL Collector | Healthy | 5ms | - |

**Active Alerts (2):**
- Kafka consumer lag increasing (Warning)
- Scheduled maintenance in 2 hours (Info)

**Pipeline Status:** All 4 pipelines operational`,

  alerts: `## Active Alerts Summary

| Severity | Count | Top Issue |
|----------|-------|-----------|
| Critical | 0 | - |
| Warning | 2 | Kafka lag |
| Info | 1 | Scheduled maintenance |

**Details:**
1. **Kafka Consumer Lag** (Warning)
   - Lag increased to 1,250 messages
   - Affected topics: production-metrics, equipment-events
   - Started: 15 minutes ago

2. **Scheduled Maintenance** (Info)
   - System maintenance window starting in 2 hours
   - Expected duration: 30 minutes`
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

function MessageBubble({ message, isUser }) {
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

function AIAssistant() {
  const { t } = useI18n()
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Get stored persona
  const storedPersona = localStorage.getItem('selectedPersona')
  const suggestions = PERSONA_SUGGESTIONS[storedPersona] || DEFAULT_SUGGESTIONS

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const getAIResponse = (query) => {
    const lowerQuery = query.toLowerCase()

    if (lowerQuery.includes('oee') || lowerQuery.includes('production') || lowerQuery.includes('performance')) {
      return SAMPLE_RESPONSES.oee
    }
    if (lowerQuery.includes('health') || lowerQuery.includes('infrastructure') || lowerQuery.includes('status')) {
      return SAMPLE_RESPONSES.health
    }
    if (lowerQuery.includes('alert') || lowerQuery.includes('alarm') || lowerQuery.includes('warning')) {
      return SAMPLE_RESPONSES.alerts
    }

    return `I understand you're asking about "${query}".

Based on the current system data, I can help you with:

1. **Production Metrics** - OEE, availability, performance, quality
2. **Infrastructure Health** - Service status, latency, throughput
3. **Alerts & Issues** - Active alarms, incidents, recommendations
4. **Business KPIs** - Financial impact, trends, forecasts

Would you like me to provide more specific information about any of these areas?`
  }

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
      const aiResponse = {
        id: Date.now() + 1,
        type: 'assistant',
        content: getAIResponse(userMessage.content),
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

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">
              {t('aiAssistant.title')}
            </h1>
            <p className="text-sm text-gray-400">
              {t('aiAssistant.subtitle')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-500/10 border border-green-500/30">
          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <span className="text-xs text-green-400">{t('aiAssistant.online')}</span>
        </div>
      </div>

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
              <p className="text-gray-400 max-w-md mb-8">
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
                title="Voice input (coming soon)"
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
