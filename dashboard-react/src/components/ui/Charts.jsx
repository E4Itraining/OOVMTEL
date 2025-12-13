import React from 'react'
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
  Legend
} from 'recharts'

const COLORS = {
  cyan: '#06b6d4',
  purple: '#a855f7',
  green: '#22c55e',
  yellow: '#f59e0b',
  red: '#ef4444',
  blue: '#3b82f6',
  pink: '#ec4899',
}

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

export function TimeSeriesChart({
  data,
  lines = [{ dataKey: 'value', color: 'cyan', name: 'Value' }],
  height = 300,
  showGrid = true,
  showLegend = false
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        {showGrid && (
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(51, 65, 85, 0.5)" />
        )}
        <XAxis
          dataKey="time"
          stroke="#64748b"
          tick={{ fill: '#64748b', fontSize: 11 }}
          axisLine={{ stroke: '#334155' }}
        />
        <YAxis
          stroke="#64748b"
          tick={{ fill: '#64748b', fontSize: 11 }}
          axisLine={{ stroke: '#334155' }}
        />
        <Tooltip content={<CustomTooltip />} />
        {showLegend && <Legend />}
        {lines.map((line, i) => (
          <Line
            key={i}
            type="monotone"
            dataKey={line.dataKey}
            name={line.name}
            stroke={COLORS[line.color] || line.color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: COLORS[line.color] || line.color }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}

export function AreaChartComponent({
  data,
  areas = [{ dataKey: 'value', color: 'cyan', name: 'Value' }],
  height = 300,
  stacked = false
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <defs>
          {areas.map((area, i) => (
            <linearGradient key={i} id={`area-gradient-${i}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={COLORS[area.color] || area.color} stopOpacity={0.4} />
              <stop offset="95%" stopColor={COLORS[area.color] || area.color} stopOpacity={0} />
            </linearGradient>
          ))}
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(51, 65, 85, 0.5)" />
        <XAxis
          dataKey="time"
          stroke="#64748b"
          tick={{ fill: '#64748b', fontSize: 11 }}
        />
        <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
        <Tooltip content={<CustomTooltip />} />
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
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  )
}

export function BarChartComponent({
  data,
  bars = [{ dataKey: 'value', color: 'cyan', name: 'Value' }],
  height = 300,
  horizontal = false,
  stacked = false
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={data}
        layout={horizontal ? 'vertical' : 'horizontal'}
        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(51, 65, 85, 0.5)" />
        {horizontal ? (
          <>
            <XAxis type="number" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
            <YAxis dataKey="name" type="category" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} width={80} />
          </>
        ) : (
          <>
            <XAxis dataKey="name" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
            <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
          </>
        )}
        <Tooltip content={<CustomTooltip />} />
        {bars.map((bar, i) => (
          <Bar
            key={i}
            dataKey={bar.dataKey}
            name={bar.name}
            fill={COLORS[bar.color] || bar.color}
            radius={[4, 4, 0, 0]}
            stackId={stacked ? 'stack' : undefined}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}

export function DonutChart({ data, height = 200, innerRadius = 60, outerRadius = 80 }) {
  const colorArray = Object.values(COLORS)

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
        >
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={entry.color || colorArray[index % colorArray.length]}
            />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
      </PieChart>
    </ResponsiveContainer>
  )
}

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
