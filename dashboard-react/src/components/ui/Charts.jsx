import React, { useState, useCallback, useMemo } from 'react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
  ReferenceArea,
  Brush,
  Label
} from 'recharts'

// ============================================================================
// CONSTANTS & COLORS
// ============================================================================

const COLORS = {
  cyan: '#06b6d4',
  purple: '#a855f7',
  green: '#22c55e',
  yellow: '#f59e0b',
  red: '#ef4444',
  blue: '#3b82f6',
  pink: '#ec4899',
  orange: '#f97316',
  teal: '#14b8a6',
  indigo: '#6366f1',
}

const AXIS_COLORS = {
  stroke: '#64748b',
  tick: '#94a3b8',
  axisLine: '#334155',
  grid: 'rgba(51, 65, 85, 0.5)',
  label: '#cbd5e1',
}

// ============================================================================
// SMART FORMATTERS - GAME CHANGER #1
// ============================================================================

/**
 * Smart number formatter with auto-detection of best format
 * Supports: K, M, B abbreviations, decimal precision, percentages
 */
export const formatNumber = (value, options = {}) => {
  if (value === null || value === undefined || isNaN(value)) return '-'

  const {
    decimals = 'auto',
    abbreviate = true,
    unit = '',
    prefix = '',
    forceSign = false,
  } = options

  const num = Number(value)
  const sign = forceSign && num > 0 ? '+' : ''

  if (abbreviate && Math.abs(num) >= 1e9) {
    const val = num / 1e9
    const dec = decimals === 'auto' ? (val % 1 === 0 ? 0 : 1) : decimals
    return `${sign}${prefix}${val.toFixed(dec)}B${unit}`
  }
  if (abbreviate && Math.abs(num) >= 1e6) {
    const val = num / 1e6
    const dec = decimals === 'auto' ? (val % 1 === 0 ? 0 : 1) : decimals
    return `${sign}${prefix}${val.toFixed(dec)}M${unit}`
  }
  if (abbreviate && Math.abs(num) >= 1e3) {
    const val = num / 1e3
    const dec = decimals === 'auto' ? (val % 1 === 0 ? 0 : 1) : decimals
    return `${sign}${prefix}${val.toFixed(dec)}K${unit}`
  }

  const dec = decimals === 'auto' ? (num % 1 === 0 ? 0 : 2) : decimals
  return `${sign}${prefix}${num.toFixed(dec)}${unit}`
}

/**
 * Time formatter for different granularities
 */
export const formatTime = (value, format = 'auto') => {
  if (!value) return ''

  // If it's already a string like "12:30", return it
  if (typeof value === 'string' && value.includes(':')) return value

  const date = new Date(value)
  if (isNaN(date.getTime())) return value

  switch (format) {
    case 'time':
      return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    case 'date':
      return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
    case 'datetime':
      return date.toLocaleString('fr-FR', {
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
      })
    case 'short':
      return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    default:
      return value
  }
}

/**
 * Duration formatter (ms, s, m, h)
 */
export const formatDuration = (ms) => {
  if (ms === null || ms === undefined) return '-'
  if (ms < 1) return `${(ms * 1000).toFixed(0)}μs`
  if (ms < 1000) return `${ms.toFixed(ms < 10 ? 1 : 0)}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  if (ms < 3600000) return `${(ms / 60000).toFixed(1)}m`
  return `${(ms / 3600000).toFixed(1)}h`
}

/**
 * Bytes formatter (B, KB, MB, GB, TB)
 */
export const formatBytes = (bytes, decimals = 1) => {
  if (bytes === 0) return '0 B'
  if (!bytes) return '-'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(Math.abs(bytes)) / Math.log(k))

  return `${(bytes / Math.pow(k, i)).toFixed(decimals)} ${sizes[i]}`
}

// Unit-specific formatters
const UNIT_FORMATTERS = {
  '%': (v) => `${v?.toFixed(1) ?? '-'}%`,
  'ms': (v) => formatDuration(v),
  's': (v) => `${v?.toFixed(1) ?? '-'}s`,
  'bytes': (v) => formatBytes(v),
  'KB': (v) => formatBytes(v * 1024),
  'MB': (v) => formatBytes(v * 1024 * 1024),
  'GB': (v) => formatBytes(v * 1024 * 1024 * 1024),
  'ops/s': (v) => formatNumber(v, { unit: ' ops/s' }),
  'req/s': (v) => formatNumber(v, { unit: ' req/s' }),
  'pts/s': (v) => formatNumber(v, { unit: ' pts/s' }),
  'msg/s': (v) => formatNumber(v, { unit: ' msg/s' }),
  'rec/s': (v) => formatNumber(v, { unit: ' rec/s' }),
  'default': (v) => formatNumber(v),
}

const getFormatter = (unit) => UNIT_FORMATTERS[unit] || UNIT_FORMATTERS.default

// ============================================================================
// ENHANCED TOOLTIP - GAME CHANGER #2
// ============================================================================

const EnhancedTooltip = ({
  active,
  payload,
  label,
  unit,
  formatter,
  showTotal = false,
  showChange = false,
}) => {
  if (!active || !payload?.length) return null

  const total = showTotal ? payload.reduce((sum, entry) => sum + (entry.value || 0), 0) : null
  const formatValue = formatter || getFormatter(unit)

  return (
    <div className="bg-industrial-dark/95 border border-industrial-border rounded-lg p-3 shadow-2xl backdrop-blur-sm min-w-[180px]">
      {/* Header with time/label */}
      <div className="flex items-center justify-between mb-2 pb-2 border-b border-industrial-border/50">
        <p className="text-gray-300 text-xs font-medium">{label}</p>
        {showTotal && total !== null && (
          <span className="text-xs text-cyan-400 font-semibold">
            Total: {formatValue(total)}
          </span>
        )}
      </div>

      {/* Data entries */}
      <div className="space-y-1.5">
        {payload.map((entry, i) => (
          <div key={i} className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 rounded-full ring-2 ring-white/10"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-gray-400 text-sm">{entry.name}</span>
            </div>
            <span className="font-semibold text-white text-sm tabular-nums">
              {entry.unit ? getFormatter(entry.unit)(entry.value) : formatValue(entry.value)}
            </span>
          </div>
        ))}
      </div>

      {/* Change indicator */}
      {showChange && payload[0]?.payload?.change !== undefined && (
        <div className="mt-2 pt-2 border-t border-industrial-border/50">
          <span className={`text-xs ${
            payload[0].payload.change >= 0 ? 'text-green-400' : 'text-red-400'
          }`}>
            {payload[0].payload.change >= 0 ? '↑' : '↓'} {Math.abs(payload[0].payload.change).toFixed(1)}%
          </span>
        </div>
      )}
    </div>
  )
}

// Legacy tooltip for backward compatibility
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null

  return (
    <div className="bg-industrial-dark/95 border border-industrial-border rounded-lg p-3 shadow-xl backdrop-blur-sm">
      <p className="text-gray-400 text-xs mb-2">{label}</p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center gap-2 text-sm">
          <span
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-gray-300">{entry.name}:</span>
          <span className="font-medium text-white">{entry.value}</span>
        </div>
      ))}
    </div>
  )
}

// ============================================================================
// AXIS LABEL COMPONENT - GAME CHANGER #3
// ============================================================================

const AxisLabel = ({
  x,
  y,
  width,
  height,
  value,
  position = 'insideLeft',
  angle = -90,
  offset = 0,
}) => {
  let textX = x
  let textY = y
  let anchor = 'middle'
  let baseline = 'middle'

  switch (position) {
    case 'insideLeft':
      textX = x + 15 + offset
      textY = y + height / 2
      break
    case 'insideRight':
      textX = x + width - 15 - offset
      textY = y + height / 2
      break
    case 'insideTop':
      textX = x + width / 2
      textY = y + 20 + offset
      break
    case 'insideBottom':
      textX = x + width / 2
      textY = y + height - 10 - offset
      anchor = 'middle'
      baseline = 'auto'
      break
    case 'left':
      textX = 12 + offset
      textY = y + height / 2
      break
    default:
      break
  }

  return (
    <text
      x={textX}
      y={textY}
      fill={AXIS_COLORS.label}
      fontSize={11}
      fontWeight={500}
      textAnchor={anchor}
      dominantBaseline={baseline}
      transform={angle !== 0 ? `rotate(${angle}, ${textX}, ${textY})` : undefined}
    >
      {value}
    </text>
  )
}

// ============================================================================
// SPARKLINE CHART (Unchanged for backward compatibility)
// ============================================================================

export function SparklineChart({ data, dataKey = 'value', color = 'cyan', height = 60 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
        <defs>
          <linearGradient id={`gradient-${color}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={COLORS[color]} stopOpacity={0.3} />
            <stop offset="95%" stopColor={COLORS[color]} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area
          type="monotone"
          dataKey={dataKey}
          stroke={COLORS[color]}
          strokeWidth={2}
          fill={`url(#gradient-${color})`}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}

// ============================================================================
// ENHANCED TIME SERIES CHART - GAME CHANGER #4
// ============================================================================

export function TimeSeriesChart({
  data,
  lines = [{ dataKey: 'value', color: 'cyan', name: 'Value' }],
  height = 300,
  showGrid = true,
  showLegend = false,
  // NEW: Axis enhancements
  yAxisLabel,
  yAxisUnit,
  xAxisLabel,
  xAxisFormat = 'auto',
  // NEW: Domain customization
  yDomain,
  yMin,
  yMax,
  yPadding = { top: 10, bottom: 10 },
  // NEW: Reference lines
  referenceLines = [],
  referenceAreas = [],
  // NEW: Thresholds with zones
  warningThreshold,
  criticalThreshold,
  showThresholdZones = false,
  // NEW: Interactive features
  enableBrush = false,
  brushHeight = 40,
  onBrushChange,
  // NEW: Dual Y-axis
  dualYAxis = false,
  rightAxisLabel,
  rightAxisUnit,
  rightAxisLines = [],
  // NEW: Enhanced tooltip
  tooltipUnit,
  showTooltipTotal = false,
  // NEW: Styling
  animationDuration = 300,
  strokeWidth = 2,
}) {
  const [brushDomain, setBrushDomain] = useState(null)

  // Calculate Y-axis domain with smart padding
  const calculatedDomain = useMemo(() => {
    if (yDomain) return yDomain
    if (yMin !== undefined && yMax !== undefined) return [yMin, yMax]

    const allValues = data.flatMap(d =>
      lines.map(line => d[line.dataKey]).filter(v => v !== null && v !== undefined)
    )

    if (allValues.length === 0) return [0, 100]

    const min = Math.min(...allValues)
    const max = Math.max(...allValues)
    const range = max - min || max || 100

    return [
      yMin ?? Math.floor(min - range * 0.1),
      yMax ?? Math.ceil(max + range * 0.1)
    ]
  }, [data, lines, yDomain, yMin, yMax])

  // Smart tick formatter
  const yTickFormatter = useCallback((value) => {
    if (yAxisUnit) return getFormatter(yAxisUnit)(value)
    return formatNumber(value, { abbreviate: true })
  }, [yAxisUnit])

  const xTickFormatter = useCallback((value) => {
    return formatTime(value, xAxisFormat)
  }, [xAxisFormat])

  // Reference line renderer
  const renderReferenceLines = () => {
    const refs = [...referenceLines]

    if (warningThreshold !== undefined) {
      refs.push({
        y: warningThreshold,
        color: '#f59e0b',
        label: 'Warning',
        dashed: true
      })
    }

    if (criticalThreshold !== undefined) {
      refs.push({
        y: criticalThreshold,
        color: '#ef4444',
        label: 'Critical',
        dashed: true
      })
    }

    return refs.map((ref, i) => (
      <ReferenceLine
        key={`ref-${i}`}
        y={ref.y}
        x={ref.x}
        stroke={ref.color || '#64748b'}
        strokeDasharray={ref.dashed ? '5 5' : undefined}
        strokeWidth={ref.strokeWidth || 1.5}
      >
        {ref.label && (
          <Label
            value={ref.label}
            position={ref.position || 'right'}
            fill={ref.color || '#64748b'}
            fontSize={10}
          />
        )}
      </ReferenceLine>
    ))
  }

  // Threshold zones renderer
  const renderThresholdZones = () => {
    if (!showThresholdZones) return null

    const zones = []

    if (warningThreshold !== undefined && criticalThreshold !== undefined) {
      // Warning zone (between warning and critical)
      zones.push(
        <ReferenceArea
          key="warning-zone"
          y1={warningThreshold}
          y2={criticalThreshold}
          fill="#f59e0b"
          fillOpacity={0.1}
        />
      )
      // Critical zone (above critical)
      zones.push(
        <ReferenceArea
          key="critical-zone"
          y1={criticalThreshold}
          y2={calculatedDomain[1]}
          fill="#ef4444"
          fillOpacity={0.1}
        />
      )
    }

    return zones
  }

  // Reference areas renderer
  const renderReferenceAreas = () => {
    return referenceAreas.map((area, i) => (
      <ReferenceArea
        key={`area-${i}`}
        x1={area.x1}
        x2={area.x2}
        y1={area.y1}
        y2={area.y2}
        fill={area.color || '#64748b'}
        fillOpacity={area.opacity || 0.1}
        stroke={area.strokeColor}
        strokeOpacity={0.5}
      />
    ))
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart
        data={data}
        margin={{
          top: 10,
          right: dualYAxis ? 60 : 30,
          left: yAxisLabel ? 60 : 20,
          bottom: enableBrush ? brushHeight + 30 : (xAxisLabel ? 30 : 10)
        }}
      >
        {/* Definitions for gradients */}
        <defs>
          {lines.map((line, i) => (
            <linearGradient key={`line-gradient-${i}`} id={`line-gradient-${i}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={COLORS[line.color] || line.color} stopOpacity={0.3} />
              <stop offset="95%" stopColor={COLORS[line.color] || line.color} stopOpacity={0} />
            </linearGradient>
          ))}
        </defs>

        {/* Grid */}
        {showGrid && (
          <CartesianGrid
            strokeDasharray="3 3"
            stroke={AXIS_COLORS.grid}
            vertical={false}
          />
        )}

        {/* Threshold zones */}
        {renderThresholdZones()}

        {/* Reference areas */}
        {renderReferenceAreas()}

        {/* X-Axis with label */}
        <XAxis
          dataKey="time"
          stroke={AXIS_COLORS.stroke}
          tick={{ fill: AXIS_COLORS.tick, fontSize: 11 }}
          axisLine={{ stroke: AXIS_COLORS.axisLine }}
          tickFormatter={xTickFormatter}
          tickLine={{ stroke: AXIS_COLORS.axisLine }}
          interval="preserveStartEnd"
        >
          {xAxisLabel && (
            <Label
              value={xAxisLabel}
              position="bottom"
              offset={-5}
              fill={AXIS_COLORS.label}
              fontSize={12}
            />
          )}
        </XAxis>

        {/* Primary Y-Axis with label and unit */}
        <YAxis
          yAxisId="left"
          stroke={AXIS_COLORS.stroke}
          tick={{ fill: AXIS_COLORS.tick, fontSize: 11 }}
          axisLine={{ stroke: AXIS_COLORS.axisLine }}
          tickLine={{ stroke: AXIS_COLORS.axisLine }}
          tickFormatter={yTickFormatter}
          domain={calculatedDomain}
          padding={yPadding}
          width={yAxisLabel ? 50 : 40}
        >
          {yAxisLabel && (
            <Label
              value={yAxisLabel}
              angle={-90}
              position="insideLeft"
              offset={-5}
              fill={AXIS_COLORS.label}
              fontSize={12}
              style={{ textAnchor: 'middle' }}
            />
          )}
        </YAxis>

        {/* Secondary Y-Axis for dual axis mode */}
        {dualYAxis && (
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke={AXIS_COLORS.stroke}
            tick={{ fill: AXIS_COLORS.tick, fontSize: 11 }}
            axisLine={{ stroke: AXIS_COLORS.axisLine }}
            tickLine={{ stroke: AXIS_COLORS.axisLine }}
            tickFormatter={rightAxisUnit ? getFormatter(rightAxisUnit) : yTickFormatter}
            width={50}
          >
            {rightAxisLabel && (
              <Label
                value={rightAxisLabel}
                angle={90}
                position="insideRight"
                offset={10}
                fill={AXIS_COLORS.label}
                fontSize={12}
                style={{ textAnchor: 'middle' }}
              />
            )}
          </YAxis>
        )}

        {/* Reference lines */}
        {renderReferenceLines()}

        {/* Enhanced Tooltip */}
        <Tooltip
          content={
            <EnhancedTooltip
              unit={tooltipUnit || yAxisUnit}
              showTotal={showTooltipTotal}
            />
          }
        />

        {/* Legend */}
        {showLegend && (
          <Legend
            wrapperStyle={{ paddingTop: 10 }}
            iconType="circle"
            iconSize={8}
            formatter={(value) => <span className="text-gray-300 text-sm">{value}</span>}
          />
        )}

        {/* Primary Lines */}
        {lines.map((line, i) => (
          <Line
            key={i}
            yAxisId="left"
            type="monotone"
            dataKey={line.dataKey}
            name={line.name}
            stroke={COLORS[line.color] || line.color}
            strokeWidth={line.strokeWidth || strokeWidth}
            dot={false}
            activeDot={{
              r: 5,
              fill: COLORS[line.color] || line.color,
              stroke: '#fff',
              strokeWidth: 2
            }}
            animationDuration={animationDuration}
            unit={line.unit}
          />
        ))}

        {/* Secondary Y-Axis Lines */}
        {dualYAxis && rightAxisLines.map((line, i) => (
          <Line
            key={`right-${i}`}
            yAxisId="right"
            type="monotone"
            dataKey={line.dataKey}
            name={line.name}
            stroke={COLORS[line.color] || line.color}
            strokeWidth={line.strokeWidth || strokeWidth}
            strokeDasharray={line.dashed ? '5 5' : undefined}
            dot={false}
            activeDot={{
              r: 5,
              fill: COLORS[line.color] || line.color,
              stroke: '#fff',
              strokeWidth: 2
            }}
            animationDuration={animationDuration}
            unit={line.unit}
          />
        ))}

        {/* Brush for zooming */}
        {enableBrush && (
          <Brush
            dataKey="time"
            height={brushHeight}
            stroke={COLORS.cyan}
            fill="rgba(6, 182, 212, 0.1)"
            tickFormatter={xTickFormatter}
            onChange={(domain) => {
              setBrushDomain(domain)
              onBrushChange?.(domain)
            }}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  )
}

// ============================================================================
// ENHANCED AREA CHART - GAME CHANGER #5
// ============================================================================

export function AreaChartComponent({
  data,
  areas = [{ dataKey: 'value', color: 'cyan', name: 'Value' }],
  height = 300,
  stacked = false,
  // NEW: Axis enhancements
  yAxisLabel,
  yAxisUnit,
  xAxisLabel,
  // NEW: Domain customization
  yDomain,
  yMin,
  yMax,
  // NEW: Reference lines
  referenceLines = [],
  warningThreshold,
  criticalThreshold,
  showThresholdZones = false,
  // NEW: Interactive features
  enableBrush = false,
  brushHeight = 40,
  // NEW: Tooltip
  tooltipUnit,
  showTooltipTotal = false,
  // NEW: Gradient intensity
  gradientOpacity = { start: 0.4, end: 0 },
}) {
  // Calculate Y-axis domain
  const calculatedDomain = useMemo(() => {
    if (yDomain) return yDomain
    if (yMin !== undefined && yMax !== undefined) return [yMin, yMax]
    return ['auto', 'auto']
  }, [yDomain, yMin, yMax])

  // Smart tick formatter
  const yTickFormatter = useCallback((value) => {
    if (yAxisUnit) return getFormatter(yAxisUnit)(value)
    return formatNumber(value, { abbreviate: true })
  }, [yAxisUnit])

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart
        data={data}
        margin={{
          top: 10,
          right: 30,
          left: yAxisLabel ? 60 : 20,
          bottom: enableBrush ? brushHeight + 30 : 10
        }}
      >
        <defs>
          {areas.map((area, i) => (
            <linearGradient key={i} id={`area-gradient-${i}`} x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor={COLORS[area.color] || area.color}
                stopOpacity={gradientOpacity.start}
              />
              <stop
                offset="95%"
                stopColor={COLORS[area.color] || area.color}
                stopOpacity={gradientOpacity.end}
              />
            </linearGradient>
          ))}
        </defs>

        <CartesianGrid
          strokeDasharray="3 3"
          stroke={AXIS_COLORS.grid}
          vertical={false}
        />

        {/* Threshold zones */}
        {showThresholdZones && warningThreshold !== undefined && criticalThreshold !== undefined && (
          <>
            <ReferenceArea
              y1={warningThreshold}
              y2={criticalThreshold}
              fill="#f59e0b"
              fillOpacity={0.1}
            />
            <ReferenceArea
              y1={criticalThreshold}
              y2={calculatedDomain[1]}
              fill="#ef4444"
              fillOpacity={0.1}
            />
          </>
        )}

        <XAxis
          dataKey="time"
          stroke={AXIS_COLORS.stroke}
          tick={{ fill: AXIS_COLORS.tick, fontSize: 11 }}
          axisLine={{ stroke: AXIS_COLORS.axisLine }}
          tickLine={{ stroke: AXIS_COLORS.axisLine }}
        >
          {xAxisLabel && (
            <Label
              value={xAxisLabel}
              position="bottom"
              offset={-5}
              fill={AXIS_COLORS.label}
              fontSize={12}
            />
          )}
        </XAxis>

        <YAxis
          stroke={AXIS_COLORS.stroke}
          tick={{ fill: AXIS_COLORS.tick, fontSize: 11 }}
          axisLine={{ stroke: AXIS_COLORS.axisLine }}
          tickLine={{ stroke: AXIS_COLORS.axisLine }}
          tickFormatter={yTickFormatter}
          domain={calculatedDomain}
          width={yAxisLabel ? 50 : 40}
        >
          {yAxisLabel && (
            <Label
              value={yAxisLabel}
              angle={-90}
              position="insideLeft"
              offset={-5}
              fill={AXIS_COLORS.label}
              fontSize={12}
              style={{ textAnchor: 'middle' }}
            />
          )}
        </YAxis>

        {/* Reference lines */}
        {referenceLines.map((ref, i) => (
          <ReferenceLine
            key={`ref-${i}`}
            y={ref.y}
            x={ref.x}
            stroke={ref.color || '#64748b'}
            strokeDasharray={ref.dashed ? '5 5' : undefined}
            strokeWidth={ref.strokeWidth || 1.5}
          >
            {ref.label && (
              <Label
                value={ref.label}
                position={ref.position || 'right'}
                fill={ref.color || '#64748b'}
                fontSize={10}
              />
            )}
          </ReferenceLine>
        ))}

        {warningThreshold !== undefined && (
          <ReferenceLine
            y={warningThreshold}
            stroke="#f59e0b"
            strokeDasharray="5 5"
            strokeWidth={1.5}
          >
            <Label value="Warning" position="right" fill="#f59e0b" fontSize={10} />
          </ReferenceLine>
        )}

        {criticalThreshold !== undefined && (
          <ReferenceLine
            y={criticalThreshold}
            stroke="#ef4444"
            strokeDasharray="5 5"
            strokeWidth={1.5}
          >
            <Label value="Critical" position="right" fill="#ef4444" fontSize={10} />
          </ReferenceLine>
        )}

        <Tooltip
          content={
            <EnhancedTooltip
              unit={tooltipUnit || yAxisUnit}
              showTotal={showTooltipTotal || stacked}
            />
          }
        />

        {areas.map((area, i) => (
          <Area
            key={i}
            type="monotone"
            dataKey={area.dataKey}
            name={area.name}
            stroke={COLORS[area.color] || area.color}
            fill={`url(#area-gradient-${i})`}
            strokeWidth={2}
            stackId={stacked ? 'stack' : undefined}
            unit={area.unit}
          />
        ))}

        {enableBrush && (
          <Brush
            dataKey="time"
            height={brushHeight}
            stroke={COLORS.cyan}
            fill="rgba(6, 182, 212, 0.1)"
          />
        )}
      </AreaChart>
    </ResponsiveContainer>
  )
}

// ============================================================================
// ENHANCED BAR CHART - GAME CHANGER #6
// ============================================================================

export function BarChartComponent({
  data,
  bars = [{ dataKey: 'value', color: 'cyan', name: 'Value' }],
  height = 300,
  horizontal = false,
  stacked = false,
  // NEW: Axis enhancements
  yAxisLabel,
  yAxisUnit,
  xAxisLabel,
  // NEW: Domain customization
  yDomain,
  yMin,
  yMax,
  // NEW: Reference lines
  referenceLines = [],
  targetLine,
  // NEW: Bar customization
  barSize,
  barGap = 4,
  categoryWidth = 80,
  // NEW: Tooltip
  tooltipUnit,
  showTooltipTotal = false,
  // NEW: Animation
  animationDuration = 300,
}) {
  const yTickFormatter = useCallback((value) => {
    if (yAxisUnit) return getFormatter(yAxisUnit)(value)
    return formatNumber(value, { abbreviate: true })
  }, [yAxisUnit])

  // Calculate domain
  const calculatedDomain = useMemo(() => {
    if (yDomain) return yDomain
    if (yMin !== undefined && yMax !== undefined) return [yMin, yMax]
    return [0, 'auto']
  }, [yDomain, yMin, yMax])

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={data}
        layout={horizontal ? 'vertical' : 'horizontal'}
        margin={{
          top: 10,
          right: 30,
          left: horizontal ? categoryWidth : (yAxisLabel ? 60 : 20),
          bottom: xAxisLabel ? 30 : 10
        }}
        barGap={barGap}
      >
        <CartesianGrid
          strokeDasharray="3 3"
          stroke={AXIS_COLORS.grid}
          horizontal={!horizontal}
          vertical={horizontal}
        />

        {horizontal ? (
          <>
            <XAxis
              type="number"
              stroke={AXIS_COLORS.stroke}
              tick={{ fill: AXIS_COLORS.tick, fontSize: 11 }}
              axisLine={{ stroke: AXIS_COLORS.axisLine }}
              tickLine={{ stroke: AXIS_COLORS.axisLine }}
              tickFormatter={yTickFormatter}
              domain={calculatedDomain}
            >
              {xAxisLabel && (
                <Label
                  value={xAxisLabel}
                  position="bottom"
                  offset={-5}
                  fill={AXIS_COLORS.label}
                  fontSize={12}
                />
              )}
            </XAxis>
            <YAxis
              dataKey="name"
              type="category"
              stroke={AXIS_COLORS.stroke}
              tick={{ fill: AXIS_COLORS.tick, fontSize: 11 }}
              axisLine={{ stroke: AXIS_COLORS.axisLine }}
              tickLine={{ stroke: AXIS_COLORS.axisLine }}
              width={categoryWidth}
            >
              {yAxisLabel && (
                <Label
                  value={yAxisLabel}
                  angle={-90}
                  position="insideLeft"
                  offset={-categoryWidth + 20}
                  fill={AXIS_COLORS.label}
                  fontSize={12}
                  style={{ textAnchor: 'middle' }}
                />
              )}
            </YAxis>
          </>
        ) : (
          <>
            <XAxis
              dataKey="name"
              stroke={AXIS_COLORS.stroke}
              tick={{ fill: AXIS_COLORS.tick, fontSize: 11 }}
              axisLine={{ stroke: AXIS_COLORS.axisLine }}
              tickLine={{ stroke: AXIS_COLORS.axisLine }}
              interval={0}
              angle={data.length > 6 ? -45 : 0}
              textAnchor={data.length > 6 ? 'end' : 'middle'}
              height={data.length > 6 ? 60 : 30}
            >
              {xAxisLabel && (
                <Label
                  value={xAxisLabel}
                  position="bottom"
                  offset={data.length > 6 ? 40 : -5}
                  fill={AXIS_COLORS.label}
                  fontSize={12}
                />
              )}
            </XAxis>
            <YAxis
              stroke={AXIS_COLORS.stroke}
              tick={{ fill: AXIS_COLORS.tick, fontSize: 11 }}
              axisLine={{ stroke: AXIS_COLORS.axisLine }}
              tickLine={{ stroke: AXIS_COLORS.axisLine }}
              tickFormatter={yTickFormatter}
              domain={calculatedDomain}
              width={yAxisLabel ? 50 : 40}
            >
              {yAxisLabel && (
                <Label
                  value={yAxisLabel}
                  angle={-90}
                  position="insideLeft"
                  offset={-5}
                  fill={AXIS_COLORS.label}
                  fontSize={12}
                  style={{ textAnchor: 'middle' }}
                />
              )}
            </YAxis>
          </>
        )}

        {/* Reference lines */}
        {referenceLines.map((ref, i) => (
          <ReferenceLine
            key={`ref-${i}`}
            y={horizontal ? undefined : ref.y}
            x={horizontal ? ref.y : undefined}
            stroke={ref.color || '#64748b'}
            strokeDasharray={ref.dashed ? '5 5' : undefined}
            strokeWidth={ref.strokeWidth || 1.5}
          >
            {ref.label && (
              <Label
                value={ref.label}
                position={ref.position || 'right'}
                fill={ref.color || '#64748b'}
                fontSize={10}
              />
            )}
          </ReferenceLine>
        ))}

        {/* Target line */}
        {targetLine !== undefined && (
          <ReferenceLine
            y={horizontal ? undefined : targetLine}
            x={horizontal ? targetLine : undefined}
            stroke="#22c55e"
            strokeDasharray="8 4"
            strokeWidth={2}
          >
            <Label value="Target" position="right" fill="#22c55e" fontSize={10} />
          </ReferenceLine>
        )}

        <Tooltip
          content={
            <EnhancedTooltip
              unit={tooltipUnit || yAxisUnit}
              showTotal={showTooltipTotal || stacked}
            />
          }
          cursor={{ fill: 'rgba(255,255,255,0.05)' }}
        />

        {bars.map((bar, i) => (
          <Bar
            key={i}
            dataKey={bar.dataKey}
            name={bar.name}
            fill={COLORS[bar.color] || bar.color}
            radius={[4, 4, 0, 0]}
            stackId={stacked ? 'stack' : undefined}
            barSize={barSize}
            animationDuration={animationDuration}
            unit={bar.unit}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}

// ============================================================================
// DONUT CHART (Enhanced)
// ============================================================================

export function DonutChart({
  data,
  height = 200,
  innerRadius = 60,
  outerRadius = 80,
  // NEW: Center label
  centerLabel,
  centerValue,
  // NEW: Label customization
  showLabels = false,
  labelType = 'percent', // 'percent', 'value', 'name'
}) {
  const colorArray = Object.values(COLORS)

  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, name, value }) => {
    if (!showLabels) return null

    const RADIAN = Math.PI / 180
    const radius = innerRadius + (outerRadius - innerRadius) * 1.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    let label = ''
    switch (labelType) {
      case 'percent':
        label = `${(percent * 100).toFixed(0)}%`
        break
      case 'value':
        label = formatNumber(value)
        break
      case 'name':
        label = name
        break
      default:
        label = `${(percent * 100).toFixed(0)}%`
    }

    return (
      <text
        x={x}
        y={y}
        fill={AXIS_COLORS.tick}
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        fontSize={11}
      >
        {label}
      </text>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={innerRadius}
          outerRadius={outerRadius}
          paddingAngle={2}
          dataKey="value"
          label={showLabels ? renderCustomLabel : undefined}
          labelLine={showLabels}
        >
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={entry.color || colorArray[index % colorArray.length]}
            />
          ))}
        </Pie>
        <Tooltip content={<EnhancedTooltip />} />

        {/* Center label */}
        {(centerLabel || centerValue) && (
          <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle">
            {centerValue && (
              <tspan x="50%" dy="-0.5em" fill="#fff" fontSize={20} fontWeight="bold">
                {centerValue}
              </tspan>
            )}
            {centerLabel && (
              <tspan x="50%" dy={centerValue ? '1.5em' : '0'} fill={AXIS_COLORS.tick} fontSize={11}>
                {centerLabel}
              </tspan>
            )}
          </text>
        )}
      </PieChart>
    </ResponsiveContainer>
  )
}

// ============================================================================
// MINI METRIC CHART (Unchanged)
// ============================================================================

export function MiniMetricChart({ current, previous, label, trend }) {
  const data = previous ? [
    { name: 'Previous', value: previous },
    { name: 'Current', value: current }
  ] : [{ name: 'Current', value: current }]

  return (
    <div className="flex items-center gap-3">
      <div className="w-16 h-8">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
            <Bar dataKey="value" fill="#06b6d4" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div>
        <p className="text-lg font-semibold text-white">{current}</p>
        <p className="text-xs text-gray-500">{label}</p>
      </div>
    </div>
  )
}

// ============================================================================
// COMPARISON CHART - GAME CHANGER #7 (NEW)
// ============================================================================

export function ComparisonChart({
  data,
  bars,
  height = 300,
  // Comparison specific
  compareKey = 'previous',
  currentLabel = 'Current',
  compareLabel = 'Previous',
  // Axis
  yAxisLabel,
  yAxisUnit,
  // Tooltip
  showPercentChange = true,
}) {
  const enhancedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      change: item[compareKey] ?
        ((item.value - item[compareKey]) / item[compareKey] * 100) : 0
    }))
  }, [data, compareKey])

  const yTickFormatter = useCallback((value) => {
    if (yAxisUnit) return getFormatter(yAxisUnit)(value)
    return formatNumber(value, { abbreviate: true })
  }, [yAxisUnit])

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={enhancedData}
        margin={{ top: 10, right: 30, left: yAxisLabel ? 60 : 20, bottom: 10 }}
        barGap={0}
        barCategoryGap="20%"
      >
        <CartesianGrid strokeDasharray="3 3" stroke={AXIS_COLORS.grid} vertical={false} />

        <XAxis
          dataKey="name"
          stroke={AXIS_COLORS.stroke}
          tick={{ fill: AXIS_COLORS.tick, fontSize: 11 }}
          axisLine={{ stroke: AXIS_COLORS.axisLine }}
        />

        <YAxis
          stroke={AXIS_COLORS.stroke}
          tick={{ fill: AXIS_COLORS.tick, fontSize: 11 }}
          axisLine={{ stroke: AXIS_COLORS.axisLine }}
          tickFormatter={yTickFormatter}
        >
          {yAxisLabel && (
            <Label
              value={yAxisLabel}
              angle={-90}
              position="insideLeft"
              offset={-5}
              fill={AXIS_COLORS.label}
              fontSize={12}
              style={{ textAnchor: 'middle' }}
            />
          )}
        </YAxis>

        <Tooltip
          content={
            <EnhancedTooltip
              unit={yAxisUnit}
              showChange={showPercentChange}
            />
          }
        />

        <Legend
          wrapperStyle={{ paddingTop: 10 }}
          iconType="circle"
          iconSize={8}
        />

        <Bar
          dataKey={compareKey}
          name={compareLabel}
          fill={COLORS.purple}
          radius={[4, 4, 0, 0]}
          opacity={0.5}
        />
        <Bar
          dataKey="value"
          name={currentLabel}
          fill={COLORS.cyan}
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}

// ============================================================================
// EXPORTS - Utilities (already exported inline via export const/function)
// ============================================================================

export {
  COLORS,
  AXIS_COLORS,
  EnhancedTooltip,
  CustomTooltip,
  getFormatter,
}
