import React, { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import {
  MessageSquare,
  Layers,
  Activity,
  Users,
  Clock,
  ExternalLink,
  ArrowRightLeft,
  TrendingUp,
  Database,
  Zap,
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  ChevronRight
} from 'lucide-react'
import { useDashboard, USER_MODES } from '../context/DashboardContext'
import { Card, CardHeader, CardBody, MetricCard } from '../components/ui/Card'
import { TimeSeriesChart, BarChartComponent, AreaChartComponent } from '../components/ui/Charts'
import { StatusBadge } from '../components/ui/Status'

const KAFKA_UI_URL = 'http://localhost:8090'

const topics = [
  { name: 'scada-metrics', partitions: 12, replicas: 1, messages: 2500000, throughput: '520 msg/s', retention: '24h', size: '450MB' },
  { name: 'mes-events', partitions: 8, replicas: 1, messages: 890000, throughput: '180 msg/s', retention: '24h', size: '180MB' },
  { name: 'plm-data', partitions: 4, replicas: 1, messages: 125000, throughput: '45 msg/s', retention: '24h', size: '85MB' },
  { name: 'opcua-nodes', partitions: 8, replicas: 1, messages: 1200000, throughput: '320 msg/s', retention: '24h', size: '220MB' },
  { name: 'industrial-telemetry', partitions: 12, replicas: 1, messages: 3500000, throughput: '850 msg/s', retention: '24h', size: '680MB' },
  { name: 'processed-telemetry', partitions: 6, replicas: 1, messages: 1800000, throughput: '420 msg/s', retention: '24h', size: '320MB' },
]

const consumerGroups = [
  { name: 'otel-collector', topics: ['industrial-telemetry'], members: 3, lag: 0, state: 'Stable' },
  { name: 'opensearch-sink', topics: ['processed-telemetry'], members: 2, lag: 125, state: 'Stable' },
  { name: 'victoria-metrics-sink', topics: ['scada-metrics', 'opcua-nodes'], members: 2, lag: 0, state: 'Stable' },
  { name: 'analytics-processor', topics: ['mes-events', 'plm-data'], members: 1, lag: 45, state: 'Rebalancing' },
]

function KafkaView() {
  const { userMode, metrics } = useDashboard()
  const [expandedTopic, setExpandedTopic] = useState(null)

  const throughputData = useMemo(() =>
    Array.from({ length: 30 }, (_, i) => ({
      time: `${String(i).padStart(2, '0')}:00`,
      incoming: Math.floor(800 + Math.random() * 400),
      outgoing: Math.floor(750 + Math.random() * 350)
    }))
  , [])

  const topicThroughputData = useMemo(() =>
    topics.slice(0, 5).map(t => ({
      name: t.name.replace('-', '\n'),
      value: parseInt(t.throughput)
    }))
  , [])

  const brokerStats = {
    brokers: 1,
    topics: topics.length,
    partitions: topics.reduce((acc, t) => acc + t.partitions, 0),
    replicas: topics.reduce((acc, t) => acc + t.replicas * t.partitions, 0),
    messages: topics.reduce((acc, t) => acc + t.messages, 0),
    storage: '1.9GB'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-teal-600 flex items-center justify-center">
              <MessageSquare className="w-6 h-6 text-white" />
            </div>
            Kafka
          </h1>
          <p className="text-gray-400 mt-1">Streaming de données en temps réel</p>
        </div>
        <a
          href={KAFKA_UI_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
        >
          <ExternalLink className="w-4 h-4" />
          Ouvrir Kafka UI
        </a>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Topics"
          value={brokerStats.topics.toString()}
          icon={Layers}
          color="cyan"
        />
        <MetricCard
          label="Partitions"
          value={brokerStats.partitions.toString()}
          icon={Database}
          color="purple"
        />
        <MetricCard
          label="Messages"
          value={`${(brokerStats.messages / 1000000).toFixed(1)}M`}
          icon={MessageSquare}
          color="green"
        />
        <MetricCard
          label="Throughput"
          value={metrics.tech?.kafkaThroughput?.toLocaleString() || "2,335"}
          unit="msg/s"
          icon={Zap}
          color="yellow"
        />
      </div>

      {/* Throughput Chart & Topic Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Throughput Over Time */}
        <Card className="lg:col-span-2">
          <CardHeader title="Débit Temps Réel" icon={Activity} />
          <CardBody>
            <AreaChartComponent
              data={throughputData}
              areas={[
                { dataKey: 'incoming', color: 'cyan', name: 'Entrant' },
                { dataKey: 'outgoing', color: 'purple', name: 'Sortant' }
              ]}
              height={250}
            />
          </CardBody>
        </Card>

        {/* Topic Distribution */}
        <Card>
          <CardHeader title="Throughput par Topic" icon={TrendingUp} />
          <CardBody>
            <BarChartComponent
              data={topicThroughputData}
              bars={[{ dataKey: 'value', color: 'cyan', name: 'msg/s' }]}
              height={250}
              horizontal
            />
          </CardBody>
        </Card>
      </div>

      {/* Topics Table */}
      <Card>
        <CardHeader title="Topics" icon={Layers} />
        <CardBody className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-industrial-border">
                  <th className="text-left p-4 text-sm font-medium text-gray-400">Topic</th>
                  <th className="text-left p-4 text-sm font-medium text-gray-400">Partitions</th>
                  <th className="text-left p-4 text-sm font-medium text-gray-400">Messages</th>
                  <th className="text-left p-4 text-sm font-medium text-gray-400">Throughput</th>
                  <th className="text-left p-4 text-sm font-medium text-gray-400">Retention</th>
                  <th className="text-left p-4 text-sm font-medium text-gray-400">Taille</th>
                </tr>
              </thead>
              <tbody>
                {topics.map((topic, index) => (
                  <motion.tr
                    key={topic.name}
                    className="border-b border-industrial-border/50 hover:bg-industrial-dark/50 cursor-pointer"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    onClick={() => setExpandedTopic(expandedTopic === topic.name ? null : topic.name)}
                  >
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {expandedTopic === topic.name ? (
                          <ChevronDown className="w-4 h-4 text-gray-500" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-gray-500" />
                        )}
                        <span className="font-medium text-white font-mono">{topic.name}</span>
                      </div>
                    </td>
                    <td className="p-4 text-gray-300">{topic.partitions}</td>
                    <td className="p-4 text-gray-300">{topic.messages.toLocaleString()}</td>
                    <td className="p-4">
                      <span className="text-green-400">{topic.throughput}</span>
                    </td>
                    <td className="p-4 text-gray-300">{topic.retention}</td>
                    <td className="p-4 text-gray-300">{topic.size}</td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>

      {/* Consumer Groups */}
      <Card>
        <CardHeader title="Consumer Groups" icon={Users} />
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {consumerGroups.map((group, index) => (
              <motion.div
                key={group.name}
                className="p-4 rounded-lg bg-industrial-dark/50 border border-industrial-border/50"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-white">{group.name}</h4>
                  <StatusBadge
                    status={group.state === 'Stable' ? 'healthy' : 'warning'}
                    label={group.state}
                    size="sm"
                  />
                </div>
                <div className="grid grid-cols-3 gap-3 text-sm">
                  <div>
                    <p className="text-gray-500">Topics</p>
                    <p className="text-white font-medium">{group.topics.length}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Members</p>
                    <p className="text-white font-medium">{group.members}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Lag</p>
                    <p className={`font-medium ${group.lag > 100 ? 'text-yellow-400' : 'text-green-400'}`}>
                      {group.lag}
                    </p>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-industrial-border/50">
                  <p className="text-xs text-gray-500">Subscribed topics:</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {group.topics.map(t => (
                      <span key={t} className="px-2 py-0.5 bg-industrial-border/50 rounded text-xs text-gray-400">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* Data Flow Visualization */}
      <Card>
        <CardHeader title="Data Flow Pipeline" icon={ArrowRightLeft} />
        <CardBody>
          <div className="flex items-center justify-between overflow-x-auto py-4">
            {/* Simulators */}
            <div className="flex flex-col items-center gap-2 min-w-[120px]">
              <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center">
                <Database className="w-8 h-8 text-white" />
              </div>
              <span className="text-sm text-gray-400">Simulators</span>
              <span className="text-xs text-gray-500">SCADA, MES, PLM</span>
            </div>

            {/* Arrow */}
            <div className="flex-1 flex items-center justify-center px-4">
              <div className="h-0.5 flex-1 bg-gradient-to-r from-blue-500 to-green-500" />
              <Zap className="w-6 h-6 text-green-400 mx-2 animate-pulse" />
              <div className="h-0.5 flex-1 bg-gradient-to-r from-green-500 to-green-500" />
            </div>

            {/* Kafka */}
            <div className="flex flex-col items-center gap-2 min-w-[120px]">
              <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-green-500 to-teal-600 flex items-center justify-center">
                <MessageSquare className="w-8 h-8 text-white" />
              </div>
              <span className="text-sm text-gray-400">Kafka</span>
              <span className="text-xs text-green-400">{metrics.tech?.kafkaThroughput || 2335} msg/s</span>
            </div>

            {/* Arrow */}
            <div className="flex-1 flex items-center justify-center px-4">
              <div className="h-0.5 flex-1 bg-gradient-to-r from-green-500 to-purple-500" />
              <Zap className="w-6 h-6 text-purple-400 mx-2 animate-pulse" />
              <div className="h-0.5 flex-1 bg-gradient-to-r from-purple-500 to-purple-500" />
            </div>

            {/* OTEL */}
            <div className="flex flex-col items-center gap-2 min-w-[120px]">
              <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                <Activity className="w-8 h-8 text-white" />
              </div>
              <span className="text-sm text-gray-400">OTEL Collector</span>
              <span className="text-xs text-purple-400">Processing</span>
            </div>

            {/* Arrow */}
            <div className="flex-1 flex items-center justify-center px-4">
              <div className="h-0.5 flex-1 bg-gradient-to-r from-purple-500 to-orange-500" />
              <Zap className="w-6 h-6 text-orange-400 mx-2 animate-pulse" />
              <div className="h-0.5 flex-1 bg-gradient-to-r from-orange-500 to-orange-500" />
            </div>

            {/* Storage */}
            <div className="flex flex-col items-center gap-2 min-w-[120px]">
              <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
                <Database className="w-8 h-8 text-white" />
              </div>
              <span className="text-sm text-gray-400">Storage</span>
              <span className="text-xs text-gray-500">VM, OS, OO</span>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

export default KafkaView
