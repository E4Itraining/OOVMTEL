/**
 * Enhanced Visualizations Component
 * Sankey diagrams, Heatmaps, Network graphs, and more
 */

import React, { useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  Sankey,
  Tooltip,
  ResponsiveContainer,
  Treemap,
  Cell,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Legend,
  ComposedChart,
  Bar,
  Line,
  Area,
} from 'recharts'

// Color palettes
const COLORS = {
  primary: ['#06b6d4', '#0891b2', '#0e7490', '#155e75'],
  secondary: ['#a855f7', '#9333ea', '#7c3aed', '#6d28d9'],
  success: ['#22c55e', '#16a34a', '#15803d', '#166534'],
  warning: ['#f59e0b', '#d97706', '#b45309', '#92400e'],
  danger: ['#ef4444', '#dc2626', '#b91c1c', '#991b1b'],
  neutral: ['#6b7280', '#4b5563', '#374151', '#1f2937'],
}

// =============================================
// Sankey Diagram Component
// =============================================

const DEMO_SANKEY_DATA = {
  nodes: [
    { name: 'Raw Materials' },
    { name: 'Production Line A' },
    { name: 'Production Line B' },
    { name: 'Quality Control' },
    { name: 'Finished Goods' },
    { name: 'Defects' },
    { name: 'Rework' },
  ],
  links: [
    { source: 0, target: 1, value: 500 },
    { source: 0, target: 2, value: 300 },
    { source: 1, target: 3, value: 480 },
    { source: 2, target: 3, value: 285 },
    { source: 3, target: 4, value: 700 },
    { source: 3, target: 5, value: 45 },
    { source: 5, target: 6, value: 30 },
    { source: 6, target: 3, value: 25 },
  ],
}

export function SankeyDiagram({
  data = DEMO_SANKEY_DATA,
  width = '100%',
  height = 400,
  nodeWidth = 20,
  nodePadding = 30,
  title = 'Production Flow',
}) {
  const nodeColor = (node) => {
    const colors = [...COLORS.primary, ...COLORS.secondary]
    return colors[node.index % colors.length]
  }

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-sm font-medium text-gray-300 mb-4">{title}</h3>
      )}
      <ResponsiveContainer width={width} height={height}>
        <Sankey
          data={data}
          nodeWidth={nodeWidth}
          nodePadding={nodePadding}
          margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
          link={{ stroke: '#374151', strokeOpacity: 0.5 }}
          node={{ fill: nodeColor }}
        >
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#9ca3af' }}
          />
        </Sankey>
      </ResponsiveContainer>
    </div>
  )
}

// =============================================
// Heatmap Component
// =============================================

const DEMO_HEATMAP_DATA = [
  { hour: '00:00', Mon: 45, Tue: 52, Wed: 48, Thu: 55, Fri: 42, Sat: 30, Sun: 25 },
  { hour: '04:00', Mon: 35, Tue: 42, Wed: 38, Thu: 45, Fri: 32, Sat: 20, Sun: 15 },
  { hour: '08:00', Mon: 75, Tue: 82, Wed: 78, Thu: 85, Fri: 72, Sat: 50, Sun: 45 },
  { hour: '12:00', Mon: 85, Tue: 92, Wed: 88, Thu: 95, Fri: 82, Sat: 60, Sun: 55 },
  { hour: '16:00', Mon: 90, Tue: 95, Wed: 92, Thu: 98, Fri: 88, Sat: 65, Sun: 58 },
  { hour: '20:00', Mon: 65, Tue: 72, Wed: 68, Thu: 75, Fri: 62, Sat: 45, Sun: 40 },
]

export function Heatmap({
  data = DEMO_HEATMAP_DATA,
  xKey = 'hour',
  dataKeys = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  title = 'Production Intensity by Time',
  height = 300,
}) {
  const getColor = (value) => {
    if (value >= 90) return '#22c55e'
    if (value >= 70) return '#84cc16'
    if (value >= 50) return '#facc15'
    if (value >= 30) return '#f97316'
    return '#ef4444'
  }

  const cellSize = 40

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-sm font-medium text-gray-300 mb-4">{title}</h3>
      )}
      <div className="overflow-x-auto">
        <div className="min-w-fit">
          {/* Header */}
          <div className="flex gap-1 mb-1 ml-16">
            {dataKeys.map((key) => (
              <div
                key={key}
                className="text-xs text-gray-400 text-center"
                style={{ width: cellSize }}
              >
                {key}
              </div>
            ))}
          </div>

          {/* Rows */}
          {data.map((row, rowIndex) => (
            <div key={rowIndex} className="flex items-center gap-1 mb-1">
              <div className="w-14 text-xs text-gray-400 text-right pr-2">
                {row[xKey]}
              </div>
              {dataKeys.map((key) => (
                <motion.div
                  key={`${rowIndex}-${key}`}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: rowIndex * 0.05 + dataKeys.indexOf(key) * 0.02 }}
                  className="rounded cursor-pointer hover:scale-110 transition-transform"
                  style={{
                    width: cellSize,
                    height: cellSize,
                    backgroundColor: getColor(row[key]),
                    opacity: 0.8 + (row[key] / 500),
                  }}
                  title={`${key} ${row[xKey]}: ${row[key]}%`}
                />
              ))}
            </div>
          ))}

          {/* Legend */}
          <div className="flex items-center gap-4 mt-4 ml-16">
            <span className="text-xs text-gray-400">Low</span>
            <div className="flex gap-1">
              {['#ef4444', '#f97316', '#facc15', '#84cc16', '#22c55e'].map((color, i) => (
                <div
                  key={i}
                  className="w-6 h-4 rounded"
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
            <span className="text-xs text-gray-400">High</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// =============================================
// Treemap Component
// =============================================

const DEMO_TREEMAP_DATA = [
  { name: 'Product A', value: 4500, category: 'Main' },
  { name: 'Product B', value: 3200, category: 'Main' },
  { name: 'Product C', value: 2800, category: 'Secondary' },
  { name: 'Product D', value: 1900, category: 'Secondary' },
  { name: 'Product E', value: 1500, category: 'Other' },
  { name: 'Product F', value: 1100, category: 'Other' },
  { name: 'Product G', value: 800, category: 'Other' },
]

const TreemapContent = ({ x, y, width, height, name, value, index }) => {
  const colors = [...COLORS.primary, ...COLORS.secondary, ...COLORS.success]

  if (width < 50 || height < 30) return null

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        fill={colors[index % colors.length]}
        stroke="#1f2937"
        strokeWidth={2}
        rx={4}
      />
      {width > 80 && height > 40 && (
        <>
          <text
            x={x + width / 2}
            y={y + height / 2 - 8}
            textAnchor="middle"
            fill="#fff"
            fontSize={12}
            fontWeight="500"
          >
            {name}
          </text>
          <text
            x={x + width / 2}
            y={y + height / 2 + 10}
            textAnchor="middle"
            fill="#d1d5db"
            fontSize={10}
          >
            {value?.toLocaleString()}
          </text>
        </>
      )}
    </g>
  )
}

export function TreemapChart({
  data = DEMO_TREEMAP_DATA,
  title = 'Production by Product',
  height = 300,
}) {
  return (
    <div className="w-full">
      {title && (
        <h3 className="text-sm font-medium text-gray-300 mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <Treemap
          data={data}
          dataKey="value"
          nameKey="name"
          stroke="#1f2937"
          content={<TreemapContent />}
        >
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#9ca3af' }}
          />
        </Treemap>
      </ResponsiveContainer>
    </div>
  )
}

// =============================================
// Bubble Chart Component
// =============================================

const DEMO_BUBBLE_DATA = [
  { name: 'Reactor-001', x: 85, y: 92, z: 150, status: 'healthy' },
  { name: 'Mixer-002', x: 72, y: 88, z: 80, status: 'healthy' },
  { name: 'Pump-003', x: 45, y: 65, z: 40, status: 'warning' },
  { name: 'Furnace-004', x: 90, y: 95, z: 200, status: 'healthy' },
  { name: 'Conveyor-005', x: 78, y: 82, z: 60, status: 'healthy' },
  { name: 'Tank-006', x: 30, y: 45, z: 30, status: 'critical' },
]

export function BubbleChart({
  data = DEMO_BUBBLE_DATA,
  title = 'Equipment Health vs Performance',
  xLabel = 'Health Score',
  yLabel = 'Performance',
  height = 400,
}) {
  const getColor = (status) => {
    switch (status) {
      case 'healthy':
        return '#22c55e'
      case 'warning':
        return '#f59e0b'
      case 'critical':
        return '#ef4444'
      default:
        return '#6b7280'
    }
  }

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-sm font-medium text-gray-300 mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 40, left: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            type="number"
            dataKey="x"
            name={xLabel}
            domain={[0, 100]}
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            axisLine={{ stroke: '#4b5563' }}
            label={{
              value: xLabel,
              position: 'bottom',
              offset: 0,
              fill: '#9ca3af',
            }}
          />
          <YAxis
            type="number"
            dataKey="y"
            name={yLabel}
            domain={[0, 100]}
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            axisLine={{ stroke: '#4b5563' }}
            label={{
              value: yLabel,
              angle: -90,
              position: 'insideLeft',
              fill: '#9ca3af',
            }}
          />
          <ZAxis type="number" dataKey="z" range={[100, 1000]} name="Power" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#9ca3af' }}
            formatter={(value, name) => [value, name]}
          />
          <Scatter name="Equipment" data={data}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.status)} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}

// =============================================
// Multi-Series Composed Chart
// =============================================

const DEMO_COMPOSED_DATA = [
  { name: '00:00', metrics: 75000, logs: 42000, errors: 120, latency: 35 },
  { name: '04:00', metrics: 65000, logs: 38000, errors: 80, latency: 28 },
  { name: '08:00', metrics: 85000, logs: 48000, errors: 150, latency: 45 },
  { name: '12:00', metrics: 92000, logs: 52000, errors: 180, latency: 52 },
  { name: '16:00', metrics: 95000, logs: 55000, errors: 200, latency: 58 },
  { name: '20:00', metrics: 82000, logs: 46000, errors: 140, latency: 42 },
]

export function ComposedMetricsChart({
  data = DEMO_COMPOSED_DATA,
  title = 'System Metrics Overview',
  height = 400,
}) {
  return (
    <div className="w-full">
      {title && (
        <h3 className="text-sm font-medium text-gray-300 mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={data} margin={{ top: 20, right: 60, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} axisLine={{ stroke: '#4b5563' }} />
          <YAxis yAxisId="left" tick={{ fill: '#9ca3af', fontSize: 12 }} axisLine={{ stroke: '#4b5563' }} />
          <YAxis yAxisId="right" orientation="right" tick={{ fill: '#9ca3af', fontSize: 12 }} axisLine={{ stroke: '#4b5563' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#9ca3af' }}
          />
          <Legend wrapperStyle={{ paddingTop: 20 }} />
          <Area
            yAxisId="left"
            type="monotone"
            dataKey="metrics"
            fill="#06b6d4"
            fillOpacity={0.3}
            stroke="#06b6d4"
            name="Metrics/s"
          />
          <Bar yAxisId="left" dataKey="logs" fill="#a855f7" name="Logs/s" opacity={0.8} />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="latency"
            stroke="#22c55e"
            strokeWidth={2}
            dot={{ fill: '#22c55e' }}
            name="Latency (ms)"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="errors"
            stroke="#ef4444"
            strokeWidth={2}
            dot={{ fill: '#ef4444' }}
            name="Errors"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

// =============================================
// Network Graph Component (Simple SVG-based)
// =============================================

const DEMO_NETWORK_DATA = {
  nodes: [
    { id: 'otel', label: 'OTEL Collector', x: 250, y: 100, type: 'collector' },
    { id: 'vm', label: 'VictoriaMetrics', x: 100, y: 250, type: 'storage' },
    { id: 'os', label: 'OpenSearch', x: 400, y: 250, type: 'storage' },
    { id: 'grafana', label: 'Grafana', x: 150, y: 400, type: 'visualization' },
    { id: 'unified', label: 'Unified View', x: 350, y: 400, type: 'visualization' },
    { id: 'scada', label: 'SCADA', x: 100, y: 100, type: 'source' },
    { id: 'mes', label: 'MES', x: 400, y: 100, type: 'source' },
  ],
  links: [
    { source: 'scada', target: 'otel' },
    { source: 'mes', target: 'otel' },
    { source: 'otel', target: 'vm' },
    { source: 'otel', target: 'os' },
    { source: 'vm', target: 'grafana' },
    { source: 'vm', target: 'unified' },
    { source: 'os', target: 'unified' },
  ],
}

export function NetworkGraph({
  data = DEMO_NETWORK_DATA,
  title = 'Service Topology',
  width = 500,
  height = 500,
}) {
  const typeColors = {
    source: '#f59e0b',
    collector: '#06b6d4',
    storage: '#a855f7',
    visualization: '#22c55e',
  }

  const nodeMap = useMemo(() => {
    const map = {}
    data.nodes.forEach(node => { map[node.id] = node })
    return map
  }, [data.nodes])

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-sm font-medium text-gray-300 mb-4">{title}</h3>
      )}
      <svg width={width} height={height} className="mx-auto">
        {/* Links */}
        {data.links.map((link, i) => {
          const source = nodeMap[link.source]
          const target = nodeMap[link.target]
          return (
            <motion.line
              key={i}
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke="#4b5563"
              strokeWidth={2}
              markerEnd="url(#arrowhead)"
            />
          )
        })}

        {/* Arrow marker */}
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="10"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" fill="#4b5563" />
          </marker>
        </defs>

        {/* Nodes */}
        {data.nodes.map((node, i) => (
          <motion.g
            key={node.id}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: i * 0.1 }}
          >
            <circle
              cx={node.x}
              cy={node.y}
              r={30}
              fill={typeColors[node.type] || '#6b7280'}
              opacity={0.8}
              className="cursor-pointer hover:opacity-100 transition-opacity"
            />
            <text
              x={node.x}
              y={node.y + 50}
              textAnchor="middle"
              fill="#d1d5db"
              fontSize={12}
            >
              {node.label}
            </text>
          </motion.g>
        ))}
      </svg>

      {/* Legend */}
      <div className="flex justify-center gap-6 mt-4">
        {Object.entries(typeColors).map(([type, color]) => (
          <div key={type} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="text-xs text-gray-400 capitalize">{type}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// =============================================
// Export all components
// =============================================

export default {
  SankeyDiagram,
  Heatmap,
  TreemapChart,
  BubbleChart,
  ComposedMetricsChart,
  NetworkGraph,
}
