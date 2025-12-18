import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MessageSquare,
  Send,
  ArrowLeft,
  Bot,
  User,
  Sparkles,
  Lightbulb,
  TrendingUp,
  AlertTriangle,
  Database,
  Activity,
  ChevronRight,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Mic,
  MicOff,
  Clock,
  Search,
  Factory,
  Shield,
  Server,
  BarChart3,
  Loader2,
  X,
  ExternalLink,
  Eye
} from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import { useI18n } from '../i18n'
import { TimeSeriesChart } from '../components/ui/Charts'
import { LoadingSpinner } from '../components/ui/Status'

// Suggested queries based on persona
const SUGGESTED_QUERIES = {
  OPERATIONS_MANAGER: [
    { icon: Factory, text: "What's the current OEE and how can I improve it?" },
    { icon: AlertTriangle, text: "Which equipment needs attention right now?" },
    { icon: TrendingUp, text: "Show me the production trend for today" },
    { icon: Clock, text: "Why did we have downtime yesterday?" }
  ],
  DEVOPS_ENGINEER: [
    { icon: Server, text: "What's the current system health status?" },
    { icon: Database, text: "Show me the error rate over the last 24 hours" },
    { icon: Activity, text: "Which services are experiencing high latency?" },
    { icon: AlertTriangle, text: "Are there any anomalies in the data pipeline?" }
  ],
  SECURITY_ANALYST: [
    { icon: Shield, text: "What's our current security posture?" },
    { icon: AlertTriangle, text: "Show me recent security threats" },
    { icon: Search, text: "Any suspicious activities detected?" },
    { icon: Database, text: "Compliance status overview" }
  ],
  default: [
    { icon: Activity, text: "Give me an overview of the system" },
    { icon: AlertTriangle, text: "What needs my attention right now?" },
    { icon: TrendingUp, text: "Show me the key metrics" },
    { icon: Lightbulb, text: "Any recommendations for improvement?" }
  ]
}

// Mock AI responses
const generateResponse = (query, metrics) => {
  const lowerQuery = query.toLowerCase()

  if (lowerQuery.includes('oee') || lowerQuery.includes('efficiency')) {
    return {
      text: `Based on the current data, your Overall Equipment Effectiveness (OEE) is at **${metrics.business?.oee || 87.5}%**, which is above the industry average of 85%.

Here's the breakdown:
- **Availability**: ${metrics.business?.availability || 92}%
- **Performance**: ${metrics.business?.performance || 95}%
- **Quality**: ${metrics.business?.quality || 99}%

To improve OEE, I recommend:
1. Address the warning on Conveyor-03 (currently at 72% efficiency)
2. Schedule preventive maintenance for CNC-02 before the temperature issue escalates
3. Optimize the idle time on Welder-05`,
      hasChart: true,
      chartData: Array.from({ length: 24 }, (_, i) => ({
        time: `${String(i).padStart(2, '0')}:00`,
        value: 80 + Math.random() * 15
      })),
      chartTitle: 'OEE Trend (24h)',
      actions: [
        { label: 'View Equipment Status', path: '/business-kpi' },
        { label: 'Schedule Maintenance', path: '/observability' }
      ]
    }
  }

  if (lowerQuery.includes('error') || lowerQuery.includes('latency') || lowerQuery.includes('health')) {
    return {
      text: `System health is currently **good** with some areas to monitor:

**Current Status:**
- Error Rate: ${metrics.tech?.errorRate || 0.02}% (within SLO)
- P95 Latency: ${metrics.tech?.latencyP95 || 23}ms
- Throughput: ${metrics.tech?.metricsRate || 1250} pts/s

**Attention Required:**
- Kafka consumer lag is increasing (142 messages behind)
- SCADA connector showing intermittent reconnects

I've identified these as related to a network issue between the edge nodes and the Kafka cluster.`,
      hasChart: true,
      chartData: Array.from({ length: 24 }, (_, i) => ({
        time: `${String(i).padStart(2, '0')}:00`,
        value: 15 + Math.random() * 20
      })),
      chartTitle: 'Latency P95 (24h)',
      actions: [
        { label: 'View Technical Dashboard', path: '/technical' },
        { label: 'Check Kafka Status', path: '/kafka' }
      ]
    }
  }

  if (lowerQuery.includes('security') || lowerQuery.includes('threat') || lowerQuery.includes('compliance')) {
    return {
      text: `**Security Posture Summary:**

Your overall security score is **88/100**, which is good but has room for improvement.

**Key Findings:**
- 2 Critical vulnerabilities need patching
- 5 Medium-risk issues identified
- Compliance: ISO 27001 (95%), SOC2 (92%), GDPR (98%)

**Recent Activity:**
- 3 failed login attempts from unknown IP (blocked)
- 1 unusual data access pattern detected (investigating)
- All security patches up to date

**Recommended Actions:**
1. Patch CVE-2024-1234 on api-gateway (critical)
2. Review access logs for user anomaly detection
3. Schedule quarterly security audit`,
      hasChart: false,
      actions: [
        { label: 'Security Dashboard', path: '/security' },
        { label: 'View Vulnerabilities', path: '/security' }
      ]
    }
  }

  // Default response
  return {
    text: `Here's a quick overview of your system:

**Business Metrics:**
- OEE: ${metrics.business?.oee || 87.5}% (Target: 90%)
- Production Today: ${metrics.business?.productionToday?.toLocaleString() || 3247} units
- Quality Rate: ${metrics.business?.quality || 99.2}%

**Technical Health:**
- System Uptime: 99.9%
- Error Rate: ${metrics.tech?.errorRate || 0.02}%
- Data Pipeline: Healthy

**Attention Items:**
- 2 critical alerts need review
- 1 equipment showing warning status
- Upcoming maintenance in 2 hours

How can I help you dive deeper into any of these areas?`,
    hasChart: false,
    actions: [
      { label: 'Command Center', path: '/command-center' },
      { label: 'View Alerts', path: '/observability' }
    ]
  }
}

// Message Component
function ChatMessage({ message, onActionClick }) {
  const isUser = message.role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      {/* Avatar */}
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0
        ${isUser
          ? 'bg-purple-500/20'
          : 'bg-gradient-to-br from-cyan-500 to-blue-500'
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5 text-purple-400" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Content */}
      <div className={`flex-1 max-w-3xl ${isUser ? 'text-right' : ''}`}>
        <div className={`inline-block p-4 rounded-2xl ${isUser
          ? 'bg-purple-500/20 border border-purple-500/30 text-white'
          : 'bg-industrial-card border border-industrial-border text-gray-200'
        }`}>
          {/* Text with markdown-like rendering */}
          <div className="prose prose-invert prose-sm max-w-none">
            {message.content.text.split('\n').map((line, i) => {
              // Bold text
              const boldRegex = /\*\*(.*?)\*\*/g
              const formattedLine = line.replace(boldRegex, '<strong class="text-white">$1</strong>')

              return (
                <p
                  key={i}
                  className="mb-2 last:mb-0"
                  dangerouslySetInnerHTML={{ __html: formattedLine }}
                />
              )
            })}
          </div>

          {/* Chart if present */}
          {message.content.hasChart && (
            <div className="mt-4 p-4 rounded-xl bg-industrial-darker border border-industrial-border">
              <h4 className="text-sm font-medium text-white mb-3">{message.content.chartTitle}</h4>
              <TimeSeriesChart
                data={message.content.chartData}
                lines={[{ dataKey: 'value', color: 'cyan', name: 'Value' }]}
                height={150}
              />
            </div>
          )}

          {/* Action buttons */}
          {!isUser && message.content.actions && (
            <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-industrial-border">
              {message.content.actions.map((action, i) => (
                <button
                  key={i}
                  onClick={() => onActionClick(action.path)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-industrial-accent/10 text-industrial-accent text-sm hover:bg-industrial-accent/20 transition-colors"
                >
                  <Eye className="w-4 h-4" />
                  {action.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Timestamp and actions */}
        {!isUser && (
          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            <span>{message.timestamp}</span>
            <div className="flex items-center gap-2">
              <button className="hover:text-white transition-colors" title="Copy">
                <Copy className="w-3 h-3" />
              </button>
              <button className="hover:text-green-400 transition-colors" title="Good response">
                <ThumbsUp className="w-3 h-3" />
              </button>
              <button className="hover:text-red-400 transition-colors" title="Bad response">
                <ThumbsDown className="w-3 h-3" />
              </button>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}

// Suggested Query Button
function SuggestedQuery({ icon: Icon, text, onClick }) {
  return (
    <motion.button
      onClick={onClick}
      className="flex items-center gap-3 p-3 rounded-xl bg-industrial-card/50 border border-industrial-border hover:border-industrial-accent/50 transition-all text-left group"
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="w-10 h-10 rounded-lg bg-industrial-accent/10 flex items-center justify-center group-hover:bg-industrial-accent/20 transition-colors">
        <Icon className="w-5 h-5 text-industrial-accent" />
      </div>
      <span className="text-sm text-gray-300 group-hover:text-white transition-colors">{text}</span>
      <ChevronRight className="w-4 h-4 text-gray-500 ml-auto group-hover:text-industrial-accent transition-colors" />
    </motion.button>
  )
}

function AIAssistant() {
  const navigate = useNavigate()
  const { metrics, selectedPersona } = useDashboard()
  const { t } = useI18n()

  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const suggestedQueries = SUGGESTED_QUERIES[selectedPersona] || SUGGESTED_QUERIES.default

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (query = inputValue) => {
    if (!query.trim()) return

    // Add user message
    const userMessage = {
      role: 'user',
      content: { text: query },
      timestamp: new Date().toLocaleTimeString()
    }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // Simulate AI response
    setTimeout(() => {
      const response = generateResponse(query, metrics)
      const aiMessage = {
        role: 'assistant',
        content: response,
        timestamp: new Date().toLocaleTimeString()
      }
      setMessages(prev => [...prev, aiMessage])
      setIsLoading(false)
    }, 1500)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleActionClick = (path) => {
    navigate(path)
  }

  return (
    <div className="h-[calc(100vh-120px)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 rounded-lg hover:bg-white/5 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-400" />
          </button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">{t('assistant.title')}</h1>
              <p className="text-sm text-gray-400">{t('assistant.subtitle')}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setMessages([])}
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="text-sm">New Chat</span>
          </button>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-6">
        {messages.length === 0 ? (
          // Empty state with suggested queries
          <div className="flex flex-col items-center justify-center h-full">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-6">
              <MessageSquare className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">{t('assistant.welcome')}</h2>
            <p className="text-gray-400 text-center max-w-md mb-8">
              {t('assistant.welcomeDescription')}
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
              {suggestedQueries.map((query, i) => (
                <SuggestedQuery
                  key={i}
                  icon={query.icon}
                  text={query.text}
                  onClick={() => handleSend(query.text)}
                />
              ))}
            </div>
          </div>
        ) : (
          // Messages
          <>
            {messages.map((message, i) => (
              <ChatMessage
                key={i}
                message={message}
                onActionClick={handleActionClick}
              />
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-4"
              >
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div className="flex items-center gap-2 p-4 rounded-2xl bg-industrial-card border border-industrial-border">
                  <Loader2 className="w-4 h-4 text-industrial-accent animate-spin" />
                  <span className="text-gray-400 text-sm">Analyzing...</span>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="mt-4 p-4 rounded-2xl bg-industrial-card border border-industrial-border">
        <div className="flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={t('assistant.placeholder')}
              rows={1}
              className="w-full bg-transparent text-white placeholder-gray-500 resize-none focus:outline-none"
              style={{ minHeight: '24px', maxHeight: '120px' }}
            />
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsListening(!isListening)}
              className={`p-2 rounded-lg transition-colors ${isListening
                ? 'bg-red-500/20 text-red-400'
                : 'hover:bg-white/5 text-gray-400 hover:text-white'
              }`}
            >
              {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>

            <button
              onClick={() => handleSend()}
              disabled={!inputValue.trim() || isLoading}
              className={`p-3 rounded-xl transition-all ${inputValue.trim() && !isLoading
                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40'
                : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              }`}
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Quick actions */}
        <div className="flex items-center gap-2 mt-3 pt-3 border-t border-industrial-border">
          <span className="text-xs text-gray-500">Quick:</span>
          {['System status', 'Recent alerts', 'Performance'].map((quick) => (
            <button
              key={quick}
              onClick={() => handleSend(quick)}
              className="px-2 py-1 rounded-md text-xs text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
            >
              {quick}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default AIAssistant
